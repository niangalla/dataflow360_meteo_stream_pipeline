-- =========================================
-- Script Structure Data Warehouse Météorologique
-- Pour ETL Talend depuis HDFS
-- =========================================

-- Connexion à la base de données
\c meteo_dw;

-- Création du schéma principal
CREATE SCHEMA IF NOT EXISTS meteo_dw;
SET search_path TO meteo_dw;

-- =========================================
-- TABLES DE DIMENSIONS
-- =========================================

-- Dimension Temps
CREATE TABLE IF NOT EXISTS "dim_temps" (
    temps_id SERIAL PRIMARY KEY,
    date_complete DATE NOT NULL,
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    jour INTEGER NOT NULL,
    heure INTEGER NOT NULL,
    jour_semaine INTEGER NOT NULL, -- 1=Lundi, 7=Dimanche
    nom_jour VARCHAR(10) NOT NULL,
    nom_mois VARCHAR(10) NOT NULL,
    saison VARCHAR(10) NOT NULL,
    timestamp_complet TIMESTAMP NOT NULL,
    UNIQUE(date_complete, heure)
);

-- Dimension Localisation
CREATE TABLE IF NOT EXISTS "dim_localisation" (
    localisation_id SERIAL PRIMARY KEY,
    ville VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    pays VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    type_zone VARCHAR(20), -- urbain, rural, côtier
    UNIQUE(latitude, longitude)
);

-- =========================================
-- TABLE DE FAITS PRINCIPALE
-- =========================================

CREATE TABLE IF NOT EXISTS "fait_mesures_meteo" (
    mesure_id BIGSERIAL PRIMARY KEY,
    
    -- Clés étrangères vers les dimensions
    temps_id INTEGER NOT NULL REFERENCES "dim_temps"(temps_id),
    localisation_id INTEGER NOT NULL REFERENCES "dim_localisation"(localisation_id),
    
    -- Mesures météo depuis HDFS
    temperature DECIMAL(5,2), -- en Celsius
    humidity DECIMAL(5,2),    -- en %
    wind_speed DECIMAL(6,2),  -- en km/h
    cloud_cover DECIMAL(5,2), -- en %
    rain_intensity DECIMAL(8,3), -- en mm/h
    
    -- Métadonnées ETL
    timestamp_ingestion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_fichier VARCHAR(200), -- nom du fichier HDFS source
    api_source VARCHAR(50) DEFAULT 'weather_api' -- nom de l'API source

);

-- =========================================
-- INDEX POUR PERFORMANCE ETL
-- =========================================

-- Index sur les clés étrangères
CREATE INDEX IF NOT EXISTS idx_fait_temps ON "fait_mesures_meteo"(temps_id);
CREATE INDEX IF NOT EXISTS idx_fait_localisation ON "fait_mesures_meteo"(localisation_id);

-- Index composites pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_fait_date_lieu ON "fait_mesures_meteo"(temps_id, localisation_id);
CREATE INDEX IF NOT EXISTS idx_temps_date ON "dim_temps"(date_complete);
CREATE INDEX IF NOT EXISTS idx_localisation_coords ON "dim_localisation"(latitude, longitude);

-- Index pour monitoring ETL
CREATE INDEX IF NOT EXISTS idx_fait_ingestion ON "fait_mesures_meteo"(timestamp_ingestion);
CREATE INDEX IF NOT EXISTS idx_fait_source_fichier ON "fait_mesures_meteo"(source_fichier);

-- =========================================
-- COMMENTAIRES DOCUMENTATION
-- =========================================

COMMENT ON SCHEMA meteo_dw IS 'Data Warehouse météorologique - ETL Talend';
COMMENT ON TABLE dim_temps IS 'Dimension temporelle - granularité horaire';
COMMENT ON TABLE dim_localisation IS 'Dimension géographique - données API';
COMMENT ON TABLE fait_mesures_meteo IS 'Table de faits - mesures depuis HDFS via Talend';

-- =========================================
-- REQUÊTE DE VÉRIFICATION
-- =========================================

-- Vérifier que les tables sont créées
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'meteo_dw'
ORDER BY tablename;

\echo 'Structure Data Warehouse créée avec succès !'
\echo 'Prêt pour ETL Talend depuis HDFS';