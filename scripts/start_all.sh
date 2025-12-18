#!/bin/bash
# scripts/stop_all.sh

echo "Demarrage de tous les services..."

docker network create my_network 2>/dev/null || echo "Réseau existe déjà"
docker compose -f docker-compose.core.yml up -d
docker compose -f docker-compose.utils.yml up -d
docker compose -f docker-compose.monitoring.yml up -d
docker compose -f docker-compose.airflow.yml up -d

echo "Tous les services demarrés"