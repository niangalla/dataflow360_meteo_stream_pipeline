#!/bin/bash
# scripts/restart_pipeline.sh

echo "Redémarrage du pipeline..."

# Arrêter tous les services
docker compose -f docker-compose.core.yml restart 
docker compose -f docker-compose.utils.yml restart
docker compose -f docker-compose.monitoring.yml restart
docker compose -f docker-compose.airflow.yml restart


echo "Pipeline redémarré"