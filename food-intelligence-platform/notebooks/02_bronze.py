# Databricks notebook source
# MAGIC %md
# MAGIC # 02 · Bronze: do RAW para a primeira tabela Delta
# MAGIC
# MAGIC A Bronze guarda o dado **exatamente como chegou** (tudo como texto), mais
# MAGIC colunas de auditoria: de qual arquivo veio e quando foi ingerido.
# MAGIC
# MAGIC ```
# MAGIC bucket raw (CSV)  ──>  food_<env>.orders.bronze_orders  (Delta, bucket lakehouse)
# MAGIC                   ──>  food_<env>.orders.bronze_stores
# MAGIC ```
# MAGIC
# MAGIC O arquivo continua no raw: se a regra mudar, dá para reprocessar do zero.

# COMMAND ----------

dbutils.widgets.text("catalog", "food_dev", "Catálogo")
catalog = dbutils.widgets.get("catalog")
raw_path = f"/Volumes/{catalog}/orders/raw"

# COMMAND ----------

from pyspark.sql import functions as F


def read_raw(file_name: str):
    """Lê um CSV do raw sem inferir tipos e adiciona colunas de auditoria."""
    return (
        spark.read.option("header", True)
        .csv(f"{raw_path}/{file_name}")
        .select(
            "*",
            F.col("_metadata.file_path").alias("_source_file"),
            F.current_timestamp().alias("_ingested_at"),
        )
    )


# COMMAND ----------

bronze_orders = read_raw("orders.csv")
bronze_orders.write.mode("overwrite").option("overwriteSchema", True).saveAsTable(f"{catalog}.orders.bronze_orders")

bronze_stores = read_raw("stores.csv")
bronze_stores.write.mode("overwrite").option("overwriteSchema", True).saveAsTable(f"{catalog}.orders.bronze_stores")

# COMMAND ----------

spark.sql(f"COMMENT ON TABLE {catalog}.orders.bronze_orders IS 'Pedidos como chegaram no bucket raw (texto, sem limpeza).'")
spark.sql(f"COMMENT ON TABLE {catalog}.orders.bronze_stores IS 'Lojas como chegaram no bucket raw.'")

display(spark.table(f"{catalog}.orders.bronze_orders").limit(10))
print(f"bronze_orders: {spark.table(f'{catalog}.orders.bronze_orders').count():,} linhas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Metadado × dado físico
# MAGIC O nome `food_<env>.orders.bronze_orders` é **metadado** (Unity Catalog).
# MAGIC Os arquivos Parquet/Delta ficam no bucket **lakehouse**. Veja onde:

# COMMAND ----------

display(spark.sql(f"DESCRIBE DETAIL {catalog}.orders.bronze_orders").select("name", "location", "numFiles", "sizeInBytes"))
