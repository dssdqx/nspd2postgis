CREATE DATABASE gis_home;

\c gis

CREATE EXTENSION postgis;

CREATE SCHEMA IF NOT exists boundaries;


CREATE TABLE boundaries.gran_mo_fo_rf (
    id serial PRIMARY KEY,
    MO text,
    FO text,
    created_at timestamp
    geom geometry(MultiPolygon, 4326)
);


CREATE INDEX gran_mo_fo_rf_geom_idx
ON boundaries.gran_mo_fo_rf
USING GIST (geom);


CREATE INDEX gran_mo_fo_rf_mo_idx
ON boundaries.gran_mo_fo_rf (mo);



SELECT *
FROM boundaries.gran_mo_fo_rf
LIMIT 10


CREATE TABLE boundaries.nas_poly_nspd (
    id serial PRIMARY KEY,
    name text,
    name_locality text,
    category int,
    category_name text,
    system_info jsonb,
    cadastral_districts_code int,
    description text,
    external_key text,
    interaction_id int,
    LABEL text,
    subcategory int,
    registration_date timestamp,
    reg_code int,
    
    document_name text,
    document_date timestamp,
    document_issuer text,
    code text,
    date_cr timestamp,
    guid uuid,
    geom geometry(MultiPolygon, 4326)
);


CREATE INDEX nas_poly_geom_idx
ON boundaries.nas_poly_nspd
USING GIST (geom);


ALTER TABLE boundaries.nas_poly_nspd
ADD CONSTRAINT uq_nspd_guid UNIQUE (guid);