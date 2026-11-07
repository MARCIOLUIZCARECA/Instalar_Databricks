# Databricks notebook source
# MAGIC %md
# MAGIC # 05 · Validação (o "TEST" do fluxo DEV → TEST → HML → PROD)
# MAGIC
# MAGIC Checagens automáticas de qualidade. Se alguma falhar, o job falha
# MAGIC e a promoção para o próximo ambiente não deve acontecer.

# COMMAND ----------

dbutils.widgets.text("catalog", "food_dev", "Catálogo")
catalog = dbutils.widgets.get("catalog")
t = lambda name: f"{catalog}.orders.{name}"  # noqa: E731

# COMMAND ----------

checks = {
    "bronze_orders tem linhas":
        f"SELECT count(*) > 0 FROM {t('bronze_orders')}",
    "silver_orders sem order_id duplicado":
        f"SELECT count(*) = count(DISTINCT order_id) FROM {t('silver_orders')}",
    "silver_orders sem data ou valor nulo":
        f"SELECT count_if(order_date IS NULL OR total_amount IS NULL) = 0 FROM {t('silver_orders')}",
    "silver_orders só com status padronizados":
        f"SELECT count_if(order_status NOT IN ('DELIVERED','CANCELLED','IN_PROGRESS')) = 0 FROM {t('silver_orders')}",
    "todo pedido tem loja cadastrada":
        f"""SELECT count(*) = 0 FROM {t('silver_orders')} o
            LEFT ANTI JOIN {t('silver_stores')} s ON o.store_id = s.store_id""",
    "gold bate com silver (faturamento entregue)":
        f"""SELECT abs((SELECT sum(total_revenue) FROM {t('gold_sales_by_store')})
                 - (SELECT sum(total_amount) FROM {t('silver_orders')} WHERE order_status = 'DELIVERED')) < 0.01""",
    "gold sem ticket médio negativo":
        f"SELECT count_if(average_ticket <= 0) = 0 FROM {t('gold_sales_by_store')}",
}

failures = []
for name, sql in checks.items():
    ok = spark.sql(sql).first()[0]
    print(f"{'OK  ' if ok else 'FALHOU'}  {name}")
    if not ok:
        failures.append(name)

assert not failures, f"Validação falhou: {failures}"
print(f"\nTodas as {len(checks)} checagens passaram em {catalog}.")
