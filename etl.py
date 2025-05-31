#!/usr/bin/env python3
# etl.py  – Spark (pyspark) en EMR
#
# Lee todos los CSV del bucket/raw/, normaliza columnas, añade
# columnas de partición (indicator, country) y escribe Parquet
# particionado en bucket/trusted/.

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim

if len(sys.argv) != 3:
    print("Uso: etl.py s3://bucket/raw/  s3://bucket/trusted/")
    sys.exit(1)

raw_path = sys.argv[1]
trusted_path = sys.argv[2]

spark = SparkSession.builder.appName("ETL_RAW_TO_TRUSTED").getOrCreate()

# ==== 1) Carga todos los CSV de raw/ ====
df = spark.read.option("header", True) \
               .option("inferSchema", True) \
               .csv(f"{raw_path}/*.csv")

# ==== 2) Normaliza encabezados (sin espacios) ====
for c in df.columns:
    df = df.withColumnRenamed(c, c.strip().lower())

# Asegura que existen las columnas necesarias
needed = ["indicator", "country", "date", "value"]
missing = [c for c in needed if c not in df.columns]
if missing:
    raise RuntimeError(f"Columnas faltantes en CSV raw: {missing}")

# Limpia white-space accidental
df = df.select([trim(col(c)).alias(c) for c in df.columns])

# ==== 3) Escribe Parquet particionado ====
df.write.mode("overwrite") \
      .partitionBy("indicator", "country") \
      .parquet(trusted_path)

spark.stop()

