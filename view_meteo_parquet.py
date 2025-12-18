from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ViewMeteoParquetData") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:8020") \
    .master("local[*]") \
    .getOrCreate()

df = spark.read.parquet("hdfs://namenode:8020/user/hadoop/datalake/meteo_stream")
print("DONNÉES MÉTÉO DAKAR:")
print(f"Nombre d'enregistrements: {df.count()}")
df.show(truncate=False)
df.describe().show()
spark.stop()