from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, lit
import sys

def load_csv(spark, path, indicator):
    return (spark.read.option("header", True).option("encoding", "UTF-8")
                 .csv(path).withColumn("indicator", lit(indicator)))

if __name__ == "__main__":
    raw_path, trusted_path = sys.argv[1], sys.argv[2]
    spark = SparkSession.builder.appName("ETL-Proyecto3").getOrCreate()

    df1 = load_csv(spark, f"{raw_path}inflacion_multi_country.csv",
                   "inflacion_anual")
    df2 = load_csv(spark, f"{raw_path}inversion_extranjera_multi_country.csv",
                   "inversion_extranjera_directa")
    df3 = load_csv(spark, f"{raw_path}Índice de Precios al Consumidor (IPC).csv",
                   "ipc_colombia")
    df4 = load_csv(spark, f"{raw_path}Tasas de interés de política monetaria.csv",
                   "tasa_politica_monetaria")

    df = df1.unionByName(df2, True)\
            .unionByName(df3, True)\
            .unionByName(df4, True)

    df_clean = (df.withColumn("date",
                              regexp_replace(col("date"), r"-.*", "").cast("int"))
                  .withColumn("value",
                              regexp_replace(col("value"), ",", "").cast("double"))
                  .na.drop(subset=["value"])
                  .filter(col("date") >= 2000))

    (df_clean.write.mode("overwrite")
            .partitionBy("indicator", "country")
            .parquet(trusted_path))
    spark.stop()
