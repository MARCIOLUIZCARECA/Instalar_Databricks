# Databricks notebook source
# MAGIC %md
# MAGIC # 04 · Gold: pronto para o negócio
# MAGIC
# MAGIC `gold_sales_by_store`: uma linha por **loja × dia**, só com pedidos entregues.
# MAGIC É a única fonte do Dashboard, do App e do Genie (as regras ficam aqui, não nos gráficos).
# MAGIC
# MAGIC | Coluna | Significado |
# MAGIC |---|---|
# MAGIC | region | Região do Brasil, derivada da UF |
# MAGIC | total_orders | Pedidos entregues no dia |
# MAGIC | total_revenue | Faturamento (R$) dos pedidos entregues |
# MAGIC | average_ticket | total_revenue / total_orders |

# COMMAND ----------

dbutils.widgets.text("catalog", "food_dev", "Catálogo")
# Grupos de negócio que podem LER a Gold (só em PROD; vazio em DEV e HML).
dbutils.widgets.text("reader_groups", "", "Grupos leitores (separados por vírgula)")

catalog = dbutils.widgets.get("catalog")
reader_groups = [g.strip() for g in dbutils.widgets.get("reader_groups").split(",") if g.strip()]
gold_table = f"{catalog}.orders.gold_sales_by_store"

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {gold_table}
COMMENT 'Vendas diárias por loja (somente pedidos entregues). Fonte oficial de Dashboard, App e Genie.'
AS
SELECT
  o.store_id,
  s.store_name,
  s.city,
  s.state,
  CASE
    WHEN s.state IN ('SP','RJ','MG','ES') THEN 'Sudeste'
    WHEN s.state IN ('PR','SC','RS')      THEN 'Sul'
    WHEN s.state IN ('DF','GO','MT','MS') THEN 'Centro-Oeste'
    WHEN s.state IN ('BA','PE','CE','MA','PB','RN','AL','SE','PI') THEN 'Nordeste'
    ELSE 'Norte'
  END                                                                AS region,
  o.order_date,
  COUNT(DISTINCT o.order_id)                                         AS total_orders,
  CAST(SUM(o.total_amount) AS DECIMAL(14,2))                         AS total_revenue,
  CAST(SUM(o.total_amount) / COUNT(DISTINCT o.order_id) AS DECIMAL(12,2)) AS average_ticket
FROM {catalog}.orders.silver_orders o
JOIN {catalog}.orders.silver_stores s ON o.store_id = s.store_id
WHERE o.order_status = 'DELIVERED'
GROUP BY ALL
""")

# COMMAND ----------

# MAGIC %md ## Descrições das colunas
# MAGIC Aparecem no Catalog Explorer e ajudam o Genie a entender as perguntas.

# COMMAND ----------

column_comments = {
    "store_id": "Código da loja (ex.: S001).",
    "store_name": "Nome da loja (marca + cidade).",
    "city": "Cidade da loja.",
    "state": "UF da loja (SP, RJ, MG...).",
    "region": "Região do Brasil da loja: Sudeste, Sul, Centro-Oeste, Nordeste ou Norte.",
    "order_date": "Dia dos pedidos.",
    "total_orders": "Quantidade de pedidos entregues no dia.",
    "total_revenue": "Faturamento em reais (R$) dos pedidos entregues no dia.",
    "average_ticket": "Ticket médio em reais: total_revenue / total_orders.",
}
for column, comment in column_comments.items():
    spark.sql(f"ALTER TABLE {gold_table} ALTER COLUMN {column} COMMENT '{comment}'")

# COMMAND ----------

# MAGIC %md ## Quem pode ler
# MAGIC O acesso faz parte do pipeline: em PROD, os grupos de negócio recebem SELECT
# MAGIC **só na Gold**. Bronze e Silver continuam fechadas para eles.

# COMMAND ----------

for group in reader_groups:
    spark.sql(f"GRANT SELECT ON TABLE {gold_table} TO `{group}`")
    print(f"SELECT em {gold_table} para {group}")

display(spark.sql(f"SHOW GRANTS ON TABLE {gold_table}"))

# COMMAND ----------

display(spark.sql(f"""
    SELECT store_name, SUM(total_orders) AS pedidos, SUM(total_revenue) AS faturamento
    FROM {gold_table}
    GROUP BY store_name
    ORDER BY faturamento DESC
    LIMIT 10
"""))
