#!/bin/bash
# scripts/stop_all.sh

echo "Arrêt de tous les services..."

docker compose -f docker-compose.core.yml down
docker compose -f docker-compose.utils.yml down 
docker compose -f docker-compose.monitoring.yml down 
docker compose -f docker-compose.airflow.yml down 

echo "Nettoyage des conteneurs arrêtés..."
docker container prune -f

echo "Tous les services arrêtés"