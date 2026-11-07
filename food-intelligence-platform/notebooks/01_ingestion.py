# Databricks notebook source
# MAGIC %md
# MAGIC # 01 · Ingestão: conhecer o que chegou no RAW
# MAGIC
# MAGIC Os arquivos chegam no bucket **raw** (`s3://food-intelligence-raw-<conta>/<env>/orders/`).
# MAGIC O Unity Catalog expõe essa pasta como o volume `/Volumes/<catalog>/orders/raw`:
# MAGIC ninguém precisa de chave da AWS, o acesso é governado pelo catálogo.
# MAGIC
# MAGIC Aqui só **lemos e inspecionamos**. Nada é gravado.

# COMMAND ----------

dbutils.widgets.text("catalog", "food_dev", "Catálogo")
catalog = dbutils.widgets.get("catalog")
raw_path = f"/Volumes/{catalog}/orders/raw"
print(f"Lendo de {raw_path}")

# COMMAND ----------

# MAGIC %md ## Arquivos no bucket raw

# COMMAND ----------

files = dbutils.fs.ls(raw_path)
display(files)

names = {f.name for f in files}
missing = {"orders.csv", "stores.csv"} - names
assert not missing, f"Arquivos faltando em {raw_path}: {missing}. Rode data/upload_to_s3.sh."

# COMMAND ----------

# MAGIC %md ## Schema identificado
# MAGIC Com `inferSchema`, o Spark tenta adivinhar os tipos. Repare: `order_date` e
# MAGIC `total_amount` vêm como **texto**, porque há formatos misturados. É trabalho da Silver.

# COMMAND ----------

orders = (
    spark.read.option("header", True).option("inferSchema", True)
    .csv(f"{raw_path}/orders.csv")
)
orders.printSchema()

# COMMAND ----------

# MAGIC %md ## Registros

# COMMAND ----------

display(orders.limit(20))
print(f"Linhas no arquivo: {orders.count():,}")

# COMMAND ----------

# MAGIC %md ## A mesma leitura em SQL, direto do volume

# COMMAND ----------

display(spark.sql(f"""
    SELECT order_status, count(*) AS linhas
    FROM read_files('{raw_path}/orders.csv', format => 'csv', header => true)
    GROUP BY order_status
    ORDER BY linhas DESC
"""))
