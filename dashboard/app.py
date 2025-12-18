import streamlit as st
import pandas as pd
from pyspark.sql import SparkSession

# ==== Initialisation Spark ====
spark = (
    SparkSession.builder
    .appName("MeteoDashboard")
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:8020")
    .master("local[*]")
    .getOrCreate()
)

st.title("Dashboard Météo Dakar")

# Lire les données depuis HDFS
try:
    df = spark.read.parquet("hdfs://namenode:8020/user/hadoop/datalake/meteo_stream")
    pd_df = df.toPandas()
    
    st.subheader("Aperçu des données")
    st.dataframe(pd_df.tail(20))

    st.subheader("Graphique Température et Humidité")
    st.line_chart(pd_df[['timestamp', 'temperature', 'humidity']].set_index('timestamp'))
    
except Exception as e:
    st.error(f"Impossible de lire les données: {e}")
