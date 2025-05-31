#!/usr/bin/env python3
# refined.py  – Spark (pyspark) en EMR
#
# Lee Parquet de trusted/, calcula promedio por indicator–country,
# guarda resultados como CSV y JSON en bucket/refined/.

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg

if len(sys.argv) != 3:
    print("Uso: refined.py s3://bucket/trusted/  s3://bucket/refined/")
    sys.exit(1)

trusted_path = sys.argv[1]
refined_path = sys.argv[2]

spark = SparkSession.builder.appName("REFINED_JSON").getOrCreate()

df = spark.read.parquet(trusted_path)

summary = (df.groupBy("indicator", "country")
             .agg(avg("value").alias("avg_value"))
             .orderBy("indicator", "country"))

# CSV compacto
summary.coalesce(1).write.mode("overwrite") \
       .option("header", True) \
       .csv(refined_path)

# JSON (un registro por línea) en subcarpeta json/
summary.coalesce(1).write.mode("overwrite") \
       .json(f"{refined_path}/json")

spark.stop()

