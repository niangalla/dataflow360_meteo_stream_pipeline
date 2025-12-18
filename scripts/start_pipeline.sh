#!/bin/bash
# scripts/start_pipeline.sh

echo "Démarrage du pipeline météo par étapes"

# 1. Créer le réseau partagé
echo "Création du réseau partagé..."
docker network create my_network 2>/dev/null || echo "Réseau existe déjà"

# 2. Démarrer les services de base (Kafka + Hadoop + Spark)
echo "Démarrage des services de base (Kafka + Hadoop + Spark)..."
docker compose -f docker-compose.core.yml up -d

# Attendre que Kafka soit prêt
echo "Attente de Kafka..."
sleep 30

# 3. Initialiser HDFS
echo "Initialisation HDFS..."
docker compose -f docker-compose.utils.yml up hdfs-init

# 4. Démarrer le monitoring (optionnel)
echo "Démarrage du monitoring ELK..."
docker compose -f docker-compose.monitoring.yml up -d

# 5. Démarrer Airflow (optionnel)
echo "Démarrage d'Airflow..."
docker compose -f docker-compose.airflow.yml up -d

echo "Pipeline démarré avec succès!"
echo "Interfaces disponibles:"
echo "   - Kafka: localhost:9092"
echo "   - HDFS: http://localhost:9870"
echo "   - Spark: http://localhost:8090"
echo "   - Kibana: http://localhost:5601"
echo "   - Airflow: http://localhost:8080"