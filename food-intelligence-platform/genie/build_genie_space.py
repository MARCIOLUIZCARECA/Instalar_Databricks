"""Gera a definição do Genie "Food Business Analyst" para cada ambiente.

Uso:  python genie/build_genie_space.py

Saída: genie/food_business_analyst.<catalog>.geniespace.json (food_dev e food_prod).
O Genie exige o nome COMPLETO da tabela, por isso há um arquivo por catálogo.
IDs são derivados do texto (md5), então o arquivo não muda entre execuções.
"""

import hashlib
import json
from pathlib import Path

CATALOGS = ["food_dev", "food_prod"]

SAMPLE_QUESTIONS = [
    "Qual foi o faturamento total no período?",
    "Quais são as cinco lojas com maior faturamento?",
    "Qual estado possui maior volume de vendas?",
    "Qual é o ticket médio por loja?",
    "Como evoluíram as vendas nos últimos meses?",
    "Quais lojas tiveram queda de faturamento?",
    "Qual foi o volume de pedidos por região?",
]

INSTRUCTIONS = [
    "Você responde perguntas de negócio sobre as vendas da rede Food Intelligence (delivery de comida).\n",
    "Fonte única: a tabela gold_sales_by_store, com uma linha por loja por dia, só com pedidos ENTREGUES.\n",
    "Faturamento = SUM(total_revenue), em reais (R$). Pedidos = SUM(total_orders).\n",
    "Ticket médio = SUM(total_revenue) / SUM(total_orders). Nunca calcule a média da coluna average_ticket.\n",
    "Volume de vendas significa quantidade de pedidos, salvo se o usuário falar em valor ou faturamento.\n",
    "Região é a coluna region (Sudeste, Sul, Centro-Oeste, Nordeste, Norte); estado é a coluna state (UF).\n",
    "Sem período informado, use todo o histórico disponível e diga qual foi o intervalo de datas.\n",
    "'Últimos meses' = agrupar por mês com DATE_TRUNC('MONTH', order_date).\n",
    "Queda de faturamento: compare o último mês completo com o primeiro mês do histórico por loja.\n",
    "Responda em português do Brasil e formate valores como R$ com duas casas decimais.",
]

COLUMNS = {
    "store_id": (["Código da loja."], ["código da loja", "id da loja"]),
    "store_name": (["Nome da loja (marca + cidade)."], ["loja", "restaurante", "unidade"]),
    "city": (["Cidade da loja."], ["cidade", "município"]),
    "state": (["UF da loja."], ["estado", "UF"]),
    "region": (["Região do Brasil."], ["região"]),
    "order_date": (["Dia dos pedidos."], ["data", "dia", "período"]),
    "total_orders": (["Pedidos entregues no dia."], ["pedidos", "volume", "quantidade de pedidos"]),
    "total_revenue": (["Faturamento em R$ no dia."], ["faturamento", "receita", "vendas em R$"]),
    "average_ticket": (["Ticket médio do dia. Para períodos, recalcule com SUM/SUM."], ["ticket médio"]),
}
CATEGORICAL = {"store_name", "city", "state", "region"}


def hid(*parts: str) -> str:
    return hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()


def example_sqls(table: str) -> list[tuple[str, str]]:
    return [
        ("Quais são as cinco lojas com maior faturamento?",
         f"SELECT store_name, SUM(total_revenue) AS faturamento FROM {table} "
         "GROUP BY store_name ORDER BY faturamento DESC LIMIT 5"),
        ("Qual é o ticket médio por loja?",
         f"SELECT store_name, ROUND(SUM(total_revenue) / SUM(total_orders), 2) AS ticket_medio FROM {table} "
         "GROUP BY store_name ORDER BY ticket_medio DESC"),
        ("Quais lojas tiveram queda de faturamento?",
         f"WITH m AS (SELECT store_name, DATE_TRUNC('MONTH', order_date) AS mes, SUM(total_revenue) AS fat "
         f"FROM {table} GROUP BY ALL), lim AS (SELECT MIN(mes) AS primeiro, MAX(mes) AS ultimo FROM m) "
         "SELECT m1.store_name, m1.fat AS faturamento_inicial, m2.fat AS faturamento_final, "
         "ROUND((m2.fat - m1.fat) / m1.fat * 100, 1) AS variacao_pct "
         "FROM m m1 JOIN m m2 ON m1.store_name = m2.store_name CROSS JOIN lim "
         "WHERE m1.mes = lim.primeiro AND m2.mes = lim.ultimo AND m2.fat < m1.fat ORDER BY variacao_pct"),
    ]


def build(catalog: str) -> dict:
    table = f"{catalog}.orders.gold_sales_by_store"
    column_configs = []
    for name, (desc, synonyms) in sorted(COLUMNS.items()):
        cfg = {"column_name": name, "description": desc, "synonyms": synonyms}
        if name in CATEGORICAL:
            cfg["enable_format_assistance"] = True
            cfg["enable_entity_matching"] = True
        column_configs.append(cfg)

    sales_alias = "gold_sales_by_store"
    return {
        "version": 2,
        "config": {
            "sample_questions": sorted(
                [{"id": hid("q", q), "question": [q]} for q in SAMPLE_QUESTIONS], key=lambda x: x["id"]),
        },
        "data_sources": {"tables": [{"identifier": table, "column_configs": column_configs}]},
        "instructions": {
            "text_instructions": [{"id": hid("instr"), "content": INSTRUCTIONS}],
            "example_question_sqls": sorted(
                [{"id": hid("sql", q), "question": [q], "sql": [s]} for q, s in example_sqls(table)],
                key=lambda x: x["id"]),
            "sql_snippets": {
                "measures": sorted([
                    {"id": hid("m", "fat"), "alias": "faturamento", "display_name": "Faturamento",
                     "sql": [f"SUM({sales_alias}.total_revenue)"], "synonyms": ["receita", "vendas em R$"]},
                    {"id": hid("m", "ped"), "alias": "pedidos", "display_name": "Pedidos",
                     "sql": [f"SUM({sales_alias}.total_orders)"], "synonyms": ["volume", "quantidade de pedidos"]},
                    {"id": hid("m", "tkt"), "alias": "ticket_medio", "display_name": "Ticket médio",
                     "sql": [f"SUM({sales_alias}.total_revenue) / SUM({sales_alias}.total_orders)"],
                     "synonyms": ["ticket"]},
                ], key=lambda x: x["id"]),
            },
        },
    }


def main() -> None:
    here = Path(__file__).parent
    for catalog in CATALOGS:
        out = here / f"food_business_analyst.{catalog}.geniespace.json"
        out.write_text(json.dumps(build(catalog), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Gerado: {out}")


if __name__ == "__main__":
    main()
