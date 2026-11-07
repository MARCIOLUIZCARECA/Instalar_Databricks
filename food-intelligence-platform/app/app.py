"""Food Intelligence Explorer (Databricks App em Streamlit).

Consulta SOMENTE a tabela Gold (gold_sales_by_store) por um SQL warehouse.

Identidade:
- Se a autorização de usuário estiver ligada no App (escopo "sql"), as consultas
  rodam COM O TOKEN DE QUEM ESTÁ USANDO: o Unity Catalog aplica as permissões
  dessa pessoa. Quem não tem SELECT na Gold vê um erro de permissão, igual no SQL.
- Sem isso, usa o service principal do App (que tem SELECT só na Gold).
Nenhuma credencial fica no código: Config() lê o ambiente do Databricks Apps.
"""

import os
import re
from datetime import date

import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

st.set_page_config(page_title="Food Intelligence Explorer", page_icon="🍽️", layout="wide")

CATALOG = os.getenv("FOOD_CATALOG", "food_dev")
GOLD = f"{CATALOG}.orders.gold_sales_by_store"
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")

cfg = Config()


def user_token() -> str | None:
    return st.context.headers.get("x-forwarded-access-token")


@st.cache_resource(show_spinner=False)
def app_connection():
    """Conexão com o service principal do App (reaproveitada entre sessões)."""
    return sql.connect(
        server_hostname=cfg.host,
        http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
        credentials_provider=lambda: cfg.authenticate,
    )


def query(statement: str, params: dict | None = None) -> pd.DataFrame:
    token = user_token()
    if token:
        with sql.connect(server_hostname=cfg.host, http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
                         access_token=token) as conn, conn.cursor() as cur:
            cur.execute(statement, params or {})
            return cur.fetchall_arrow().to_pandas()
    with app_connection().cursor() as cur:
        cur.execute(statement, params or {})
        return cur.fetchall_arrow().to_pandas()


@st.cache_data(ttl=600, show_spinner=False)
def load_options(_token_key: str | None) -> tuple[pd.DataFrame, date, date]:
    stores = query(f"SELECT DISTINCT store_id, store_name, city, state FROM {GOLD} ORDER BY store_name")
    bounds = query(f"SELECT min(order_date) AS d0, max(order_date) AS d1 FROM {GOLD}")
    return stores, bounds.d0[0], bounds.d1[0]


def brl(value: float) -> str:
    return "R$ " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- Cabeçalho -----------------------------------------------------------------

st.title("Food Intelligence Explorer")
st.caption(f"Fonte: `{GOLD}` · pedidos entregues · "
           f"identidade: {'seu usuário' if user_token() else 'service principal do App'}")

if not WAREHOUSE_ID:
    st.error("DATABRICKS_WAREHOUSE_ID não definido: adicione o recurso sql-warehouse ao App.")
    st.stop()

try:
    with st.spinner("Conectando ao SQL warehouse... Se ele estava desligado, isso leva de 2 a 5 minutos."):
        stores, first_day, last_day = load_options(user_token())
except Exception as exc:  # noqa: BLE001
    st.error("Sem acesso à tabela Gold com a sua identidade. "
             "Peça ao time de plataforma o grupo de leitura de PROD.")
    with st.expander("Detalhe técnico"):
        st.code(str(exc))
    st.stop()

# --- Filtros -------------------------------------------------------------------

with st.sidebar:
    st.header("Filtros")
    period = st.date_input("Período", value=(first_day, last_day), min_value=first_day, max_value=last_day,
                           format="DD/MM/YYYY")
    start, end = (period if isinstance(period, tuple) and len(period) == 2 else (first_day, last_day))
    labels = dict(zip(stores.store_name, stores.store_id))
    selected = st.multiselect("Lojas (vazio = todas)", options=list(labels))
    compare_top = st.slider("Lojas no comparativo", 5, 30, 10)

store_ids = [labels[n] for n in selected] or list(stores.store_id)
# Os IDs vêm da própria tabela; ainda assim validamos o formato antes de montar o IN.
store_ids = [s for s in store_ids if re.fullmatch(r"[A-Za-z0-9_-]+", s)]
params = {"start": start, "end": end}
store_list = ", ".join(f"'{s}'" for s in store_ids) or "''"
where = f"order_date BETWEEN :start AND :end AND store_id IN ({store_list})"

# --- Indicadores ---------------------------------------------------------------

with st.spinner("Consultando a camada Gold..."):
    kpi = query(f"""
        SELECT coalesce(sum(total_revenue), 0) AS revenue,
               coalesce(sum(total_orders), 0)  AS orders
        FROM {GOLD} WHERE {where}
    """, params).iloc[0]

orders = int(kpi.orders)
revenue = float(kpi.revenue)
c1, c2, c3 = st.columns(3)
c1.metric("Faturamento", brl(revenue))
c2.metric("Pedidos", f"{orders:,}".replace(",", "."))
c3.metric("Ticket médio", brl(revenue / orders) if orders else "—")

# --- Histórico -----------------------------------------------------------------

st.subheader("Histórico de vendas")
history = query(f"""
    SELECT date_trunc('WEEK', order_date) AS semana,
           sum(total_revenue) AS faturamento,
           sum(total_orders)  AS pedidos
    FROM {GOLD} WHERE {where}
    GROUP BY 1 ORDER BY 1
""", params)
if history.empty:
    st.info("Sem vendas no período selecionado.")
else:
    history["faturamento"] = history["faturamento"].astype(float)
    st.line_chart(history, x="semana", y="faturamento", height=280)

# --- Comparativo entre lojas ---------------------------------------------------

st.subheader("Comparativo entre lojas")
ranking = query(f"""
    SELECT store_name AS loja, city AS cidade, state AS uf,
           sum(total_revenue) AS faturamento,
           sum(total_orders)  AS pedidos,
           sum(total_revenue) / sum(total_orders) AS ticket_medio
    FROM {GOLD} WHERE {where}
    GROUP BY ALL ORDER BY faturamento DESC LIMIT {int(compare_top)}
""", params)
for col in ("faturamento", "ticket_medio"):
    ranking[col] = ranking[col].astype(float)

left, right = st.columns([3, 2])
left.bar_chart(ranking, x="loja", y="faturamento", horizontal=True, height=420)
right.dataframe(
    ranking,
    hide_index=True,
    use_container_width=True,
    column_config={
        "faturamento": st.column_config.NumberColumn("Faturamento", format="R$ %.2f"),
        "ticket_medio": st.column_config.NumberColumn("Ticket médio", format="R$ %.2f"),
        "pedidos": st.column_config.NumberColumn("Pedidos", format="%d"),
    },
)
