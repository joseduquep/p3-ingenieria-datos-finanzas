from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
import sys

if __name__ == "__main__":
    inp, out = sys.argv[1], sys.argv[2]
    spark = SparkSession.builder.appName("REFINED-Proyecto3").getOrCreate()

    df = spark.read.parquet(inp)
    summary = df.groupBy("indicator", "country").agg(avg("value").alias("avg_value"))

    # Guarda CSV
    summary.write.mode("overwrite").option("header", True).csv(out)

    # Guarda JSON (un solo archivo en carpeta json/)
    summary.coalesce(1).write.mode("overwrite").json(out + "json/")

    spark.stop()
