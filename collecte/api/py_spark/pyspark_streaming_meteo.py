from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, FloatType, TimestampType
import time

# 1. Initialiser Spark Session avec mode local
spark = (
    SparkSession.builder
    .appName("MeteoKafkaToHDFS")
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:8020")
    .config("spark.hadoop.fs.hdfs.impl", "org.apache.hadoop.hdfs.DistributedFileSystem")
    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true")
    .config("spark.hadoop.dfs.permissions.enabled", "false")  # Désactive les permissions strictes
    # .config("spark.sql.adaptive.enabled", "false")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .config("spark.sql.adaptive.enabled", "true")  # Pour de meilleures performances
    .config("spark.sql.shuffle.partitions", "3")   # adapte au nombre de partitions Kafka
    .master("local[*]")
    .getOrCreate()
)

print(" Spark Session créée avec succès!")

spark.sparkContext.setLogLevel("WARN")

# 2. Schéma des données JSON 
schema = (
    StructType()
    .add("temperature", FloatType())
    .add("humidity", FloatType())
    .add("windSpeed", FloatType())
    .add("cloudCover", FloatType())
    .add("rainIntensity", FloatType())
    .add("timestamp", TimestampType())
)

print(" Schéma défini")

try:
    # 3. Lire depuis Kafka (streaming)
    df_kafka = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "kafka:9092")
        .option("subscribe", "weather_dakar")
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
    )
    
    print(" Connexion Kafka établie")

    # 4. Transformer le message Kafka (clé/valeurs binaires => JSON structuré)
    df_parsed = (
        df_kafka.selectExpr("CAST(value AS STRING) as json_value")
        .select(from_json(col("json_value"), schema).alias("data"))
        .select("data.*")
    )
    
    print(" Parsing des données configuré")

    # 5. Écrire dans HDFS (en format Parquet par défaut, ou JSON)
    output_path = "hdfs://namenode:8020/user/hadoop/datalake/meteo_stream"
    checkpoint_path = "hdfs://namenode:8020/user/hadoop/datalake/weather_checkpoint"

    
    print(f" Tentative d'écriture vers: {output_path}")

    query = (
        df_parsed.writeStream
        .format("parquet")
        .option("path", output_path)
        .option("checkpointLocation", checkpoint_path)
        .outputMode("append")
        .trigger(processingTime='5 seconds')  # Ajouté un trigger
        .option("maxFilesPerTrigger", 1)      # limiter la charge par batch
        .start()
    )
    # print(" Streaming démarré, en continu...")
    # query.awaitTermination()  # Bloque ici et laisse Spark traiter les données en continu

    print(" Streaming démarré, en attente de données...")
    
    # On attend quelques secondes puis arrêter pour test
   
    time.sleep(60)  # Attendre 1 minute pour tester
    
    query.stop()
    print(" Streaming arrêté")

    # 7. Vérification des données écrites
    try:
        result_df = spark.read.parquet(output_path)
        count = result_df.count()
        print(f"Données écrites avec succès: {count} lignes")
        if count > 0:
            print("Aperçu des données:")
            result_df.show(10, truncate=False)
    except Exception as read_error:
        print(f"Impossible de lire les données écrites: {read_error}")
    
except Exception as e:
    print(f" Erreur: {str(e)}")
    
finally:
    spark.stop()
    print(" Spark Session fermée")