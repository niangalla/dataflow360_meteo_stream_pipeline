from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# ==== CONFIGURATION DE BASE ====
default_args = {
    'owner': 'alla',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

# CRÉATION DU DAG
with DAG(
    dag_id='send_weather_to_kafka',
    default_args=default_args,
    description='Récupère les données météo et les envoie vers Kafka toutes les n-heures',
    schedule_interval=timedelta(hours=2),  # toutes les 2 heures à partir de start_date
    start_date=datetime.now() - timedelta(minutes=1),# déclenchement prequ'immediat
    catchup=False,
    tags=['weather', 'kafka'],
) as dag:

    # Tache 1 : Lancer le producer météo
    fetch_and_send_weather_to_kafka = BashOperator(
        task_id='fetch_and_send_weather_to_kafka',
        bash_command='cd /opt/airflow/scripts && python3 kafka/producer.py'
    )

    # Tache 2 : Lancer le consumer vers Redis
    verify_pipeline_elk_to_redis = BashOperator(
        task_id='verify_pipeline_elk_to_redis',
        bash_command='''
            echo " Attente traitement Logstash..." && sleep 5 &&
            curl -s "http://elasticsearch:9200/_cat/indices/weather*" || echo "Pas encore d'index weather"
        ''',
        trigger_rule='all_done'  # S'exécute même si producer échoue
    )

    # Tache 3 : Lancer le job Spark
    run_py_spark_job_to_hdfs = BashOperator(
        task_id='run_py_spark_job_to_hdfs',
        # Lance un job Spark en mode local pour traiter les données Kafka avec le package spark-sql-kafka
        bash_command=(
            '$SPARK_HOME/bin/spark-submit '
            '--master local[*] '  # Utilise tous les cores CPU disponibles localement
            '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 '  # Package pour lire depuis Kafka
            '/opt/airflow/py_spark/pyspark_streaming_meteo.py'  # Script Python Spark à exécuter
        ),
        env={
            'JAVA_HOME': '/usr/lib/jvm/java-11-openjdk-amd64',  # JVM requise pour Spark
            'SPARK_HOME': '/opt/spark',  # Répertoire d'installation Spark
            'PYSPARK_PYTHON': 'python3',  # Version Python pour PySpark
            'HADOOP_CONF_DIR': '/opt/spark/conf',  # Configuration Hadoop/HDFS
            'HADOOP_USER_NAME': 'hadoop'  # Utilisateur Hadoop pour éviter les erreurs de permissions
        }
    )

    # DÉPENDANCES
    fetch_and_send_weather_to_kafka >> verify_pipeline_elk_to_redis >> run_py_spark_job_to_hdfs