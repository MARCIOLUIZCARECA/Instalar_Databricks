"""Gera dashboards/executive_overview.lvdash.json (AI/BI Dashboard).

Uso:  python dashboards/build_dashboard.py

O JSON é gerado por código para manter os nomes de campos consistentes.
Fonte única: a tabela gold_sales_by_store (sem catálogo no FROM: o bundle
injeta o catálogo do ambiente via dataset_catalog / dataset_schema).
"""

import json
from pathlib import Path

DS = "ds_sales"
BRL = {"type": "number-currency", "currencyCode": "BRL", "abbreviation": "compact",
       "decimalPlaces": {"type": "max", "places": 2}}
BRL_EXACT = {"type": "number-currency", "currencyCode": "BRL", "decimalPlaces": {"type": "exact", "places": 2}}

MEASURES = {
    "Faturamento": ("SUM(`total_revenue`)", "Faturamento (R$) dos pedidos entregues"),
    "Pedidos": ("SUM(`total_orders`)", "Pedidos entregues"),
    "Ticket médio": ("SUM(`total_revenue`) / SUM(`total_orders`)", "Faturamento / pedidos"),
    "Lojas": ("COUNT(DISTINCT `store_id`)", "Lojas com venda no período"),
}


def m(name):
    return {"name": f"measure({name})", "expression": f"MEASURE(`{name}`)"}


def text(name, line, x, y, w, h=1):
    return {"widget": {"name": name, "multilineTextboxSpec": {"lines": [line]}},
            "position": {"x": x, "y": y, "width": w, "height": h}}


def counter(name, measure, title, x, fmt=None):
    value = {"fieldName": f"measure({measure})", "displayName": title}
    if fmt:
        value["format"] = fmt
    return {
        "widget": {
            "name": name,
            "queries": [{"name": "main_query", "query": {
                "datasetName": DS, "fields": [m(measure)], "disaggregated": False}}],
            "spec": {"version": 2, "widgetType": "counter", "encodings": {"value": value},
                     "frame": {"title": title, "showTitle": True}},
        },
        "position": {"x": x, "y": 2, "width": 3, "height": 3},
    }


def chart(name, kind, title, dim, dim_expr, dim_type, measure, pos, horizontal=False, fmt=None):
    dim_enc = {"fieldName": dim, "scale": {"type": dim_type}, "displayName": title.split(" por ")[-1].capitalize()}
    if dim_type == "categorical":
        dim_enc["scale"]["sort"] = {"by": "value"} if horizontal or kind == "bar" else {"by": "alphabetical"}
    y_field = {"fieldName": f"measure({measure})", "displayName": measure}
    if fmt:
        y_field["format"] = fmt
    val_enc = {"scale": {"type": "quantitative"}, **y_field}
    encodings = {"x": val_enc, "y": dim_enc} if horizontal else {"x": dim_enc, "y": val_enc}
    return {
        "widget": {
            "name": name,
            "queries": [{"name": "main_query", "query": {
                "datasetName": DS,
                "fields": [{"name": dim, "expression": dim_expr}, m(measure)],
                "disaggregated": False}}],
            "spec": {"version": 3, "widgetType": kind, "encodings": encodings,
                     "frame": {"title": title, "showTitle": True}},
        },
        "position": pos,
    }


def filt(name, field, title, kind, x):
    return {
        "widget": {
            "name": name,
            "queries": [{"name": f"q_{field}", "query": {
                "datasetName": DS, "fields": [{"name": field, "expression": f"`{field}`"}],
                "disaggregated": False}}],
            "spec": {"version": 2, "widgetType": kind,
                     "encodings": {"fields": [{"fieldName": field, "displayName": title, "queryName": f"q_{field}"}]},
                     "frame": {"showTitle": True, "title": title}},
        },
        "position": {"x": x, "y": 0, "width": 3, "height": 2},
    }


dashboard = {
    "datasets": [{
        "name": DS,
        "displayName": "Vendas por loja e dia (Gold)",
        "queryLines": [
            "SELECT store_id, store_name, city, state, region, order_date, total_orders, total_revenue\n",
            "FROM gold_sales_by_store\n",
        ],
        "columns": [{"displayName": k, "expression": e, "description": d} for k, (e, d) in MEASURES.items()],
    }],
    "pages": [
        {
            "name": "overview",
            "displayName": "Visão executiva",
            "pageType": "PAGE_TYPE_CANVAS",
            "layoutVersion": "GRID_V1",
            "layout": [
                text("title", "# Food Intelligence — Executive Overview", 0, 0, 12),
                text("subtitle", "Pedidos **entregues**, fonte única `gold_sales_by_store`. "
                     "Filtros de período, estado, cidade e loja na aba **Filtros**.", 0, 1, 12),
                counter("kpi_revenue", "Faturamento", "Faturamento total", 0, BRL),
                counter("kpi_orders", "Pedidos", "Pedidos", 3),
                counter("kpi_ticket", "Ticket médio", "Ticket médio", 6, BRL_EXACT),
                counter("kpi_stores", "Lojas", "Lojas", 9),
                chart("revenue_by_day", "line", "Faturamento por dia", "daily(order_date)",
                      'DATE_TRUNC("DAY", `order_date`)', "temporal", "Faturamento",
                      {"x": 0, "y": 5, "width": 12, "height": 5}, fmt=BRL),
                chart("revenue_by_region", "bar", "Faturamento por região", "region", "`region`",
                      "categorical", "Faturamento", {"x": 0, "y": 10, "width": 6, "height": 5}, fmt=BRL),
                chart("orders_by_month", "bar", "Pedidos por mês", "monthly(order_date)",
                      'DATE_TRUNC("MONTH", `order_date`)', "temporal", "Pedidos",
                      {"x": 6, "y": 10, "width": 6, "height": 5}),
                chart("store_ranking", "bar", "Ranking das lojas por faturamento", "store_name", "`store_name`",
                      "categorical", "Faturamento", {"x": 0, "y": 15, "width": 6, "height": 9},
                      horizontal=True, fmt=BRL),
                chart("ticket_by_store", "bar", "Ticket médio por loja", "store_name", "`store_name`",
                      "categorical", "Ticket médio", {"x": 6, "y": 15, "width": 6, "height": 9},
                      horizontal=True, fmt=BRL_EXACT),
            ],
        },
        {
            "name": "filters",
            "displayName": "Filtros",
            "pageType": "PAGE_TYPE_GLOBAL_FILTERS",
            "layoutVersion": "GRID_V1",
            "layout": [
                filt("f_period", "order_date", "Período", "filter-date-range-picker", 0),
                filt("f_state", "state", "Estado", "filter-multi-select", 3),
                filt("f_city", "city", "Cidade", "filter-multi-select", 6),
                filt("f_store", "store_name", "Loja", "filter-multi-select", 9),
            ],
        },
    ],
    "uiSettings": {
        "theme": {
            "canvasBackgroundColor": {"light": "#FCFCFC", "dark": "#1F272D"},
            "widgetBackgroundColor": {"light": "#FFFFFF", "dark": "#11171C"},
            "widgetBorderColor": {"light": "#FFFFFF", "dark": "#11171C"},
            "fontColor": {"light": "#11171C", "dark": "#E8ECF0"},
            "selectionColor": {"light": "#2272B4", "dark": "#8ACAFF"},
            "visualizationColors": ["#EA1D2C", "#FE9000", "#3C6997", "#21918C", "#594E90", "#FFDD4A", "#6DD980"],
            "widgetHeaderAlignment": "LEFT",
        }
    },
}

out = Path(__file__).with_name("executive_overview.lvdash.json")
out.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Gerado: {out}")
