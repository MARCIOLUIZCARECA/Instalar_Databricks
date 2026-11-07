# Databricks notebook source
# MAGIC %md
# MAGIC # 03 · Silver: dado limpo e tipado
# MAGIC
# MAGIC | Problema na Bronze | Regra na Silver |
# MAGIC |---|---|
# MAGIC | Pedidos duplicados | Um registro por `order_id` |
# MAGIC | `quantity` nula | Vira 1 |
# MAGIC | `product_name` vazio | Vira "Não informado" |
# MAGIC | Datas em dois formatos | `order_ts` (timestamp) e `order_date` (date) |
# MAGIC | "R$ 1.234,56" e "45.90" | `total_amount` decimal |
# MAGIC | Status misturados | DELIVERED, CANCELLED, IN_PROGRESS |
# MAGIC
# MAGIC As regras estão em `src/food/transforms.py` e têm testes (`tests/test_orders.py`):
# MAGIC o mesmo código roda no seu computador e no Databricks.

# COMMAND ----------

dbutils.widgets.text("catalog", "food_dev", "Catálogo")
catalog = dbutils.widgets.get("catalog")

# COMMAND ----------

import os
import sys

sys.path.append(os.path.abspath("../src"))

from food import transforms  # noqa: E402
from pyspark.sql import functions as F  # noqa: E402
from pyspark.sql import types as T  # noqa: E402

parse_amount = F.udf(transforms.parse_amount, T.DoubleType())
parse_order_date = F.udf(transforms.parse_order_date, T.TimestampType())
normalize_status = F.udf(transforms.normalize_status, T.StringType())
parse_quantity = F.udf(transforms.parse_quantity, T.IntegerType())
clean_product_name = F.udf(transforms.clean_product_name, T.StringType())

# COMMAND ----------

bronze = spark.table(f"{catalog}.orders.bronze_orders")

silver_orders = (
    bronze
    .dropDuplicates(["order_id"])
    .select(
        F.col("order_id"),
        F.col("store_id"),
        parse_order_date("order_date").alias("order_ts"),
        clean_product_name("product_name").alias("product_name"),
        parse_quantity("quantity").alias("quantity"),
        parse_amount("total_amount").cast("decimal(12,2)").alias("total_amount"),
        normalize_status("order_status").alias("order_status"),
    )
    .withColumn("order_date", F.to_date("order_ts"))
    # Sem data ou sem valor, o pedido não serve para análise.
    .where(F.col("order_ts").isNotNull() & F.col("total_amount").isNotNull())
)

(silver_orders.write.mode("overwrite").option("overwriteSchema", True)
 .saveAsTable(f"{catalog}.orders.silver_orders"))

# COMMAND ----------

silver_stores = (
    spark.table(f"{catalog}.orders.bronze_stores")
    .select(
        F.trim("store_id").alias("store_id"),
        F.trim("store_name").alias("store_name"),
        F.trim("city").alias("city"),
        F.upper(F.trim("state")).alias("state"),
    )
    .dropDuplicates(["store_id"])
)
(silver_stores.write.mode("overwrite").option("overwriteSchema", True)
 .saveAsTable(f"{catalog}.orders.silver_stores"))

# COMMAND ----------

b = bronze.count()
s = spark.table(f"{catalog}.orders.silver_orders").count()
print(f"Bronze: {b:,}  ->  Silver: {s:,}  (removidos: {b - s:,})")
display(spark.table(f"{catalog}.orders.silver_orders").limit(10))
