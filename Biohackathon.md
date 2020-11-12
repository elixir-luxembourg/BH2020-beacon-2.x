# The notes/comments from Biohackathon

## 1. Running the code
Fetch the code from the repository. Make sure Docker's daemon is running, and that you don't have old images cached.
Docker-compose.yml is not there anymore, use 'deploy/beacon.yml' like:

```
docker-compose -f deploy/beacon.yml up -d --build
```

During development you might want to uncomment the commented out lines in `beacon.yml`

## 2. Connection
In order to use our postgres server, modify `conf.py` files in `beacon/conf.py` and `deploy/conf.py` with the following values:

```
database_url = 'biohackathon2020.lcsb.uni.lu'
database_port = 5432
database_user = 'biohacker'
database_password = ''  # <====  PUT THE PASSWORD HERE -------------------------
database_name = 'synpuf1k_5_3'
database_schema = 's5_3_1' # comma-separated list of schemas
database_app_name = 'beacon' # Useful to track connections
```

## 3. What has been done to database with OMOP data
Created `addons` schema, installed `hstore` extension (make sure `postgres12-contrib` is installed on CentOS machine), added `dataset` table with `updated_at` field.

```
synpuf1k_5_3=# CREATE SCHEMA addons;
CREATE SCHEMA
synpuf1k_5_3=# ALTER SCHEMA addons OWNER TO biohacker;
ALTER SCHEMA
synpuf1k_5_3=# CREATE EXTENSION IF NOT EXISTS hstore WITH SCHEMA addons;
CREATE EXTENSION
synpuf1k_5_3=# COMMENT ON EXTENSION hstore IS 'data type for storing sets of (key, value) pairs';
COMMENT
synpuf1k_5_3=# SET search_path TO 's5_3_1';
SET
synpuf1k_5_3=# CREATE TABLE dataset (UPDATED_AT DATE);
CREATE TABLE
synpuf1k_5_3=# INSERT INTO dataset VALUES (current_timestamp);
INSERT 0 1
synpuf1k_5_3=# GRANT SELECT ON TABLE "dataset" TO biohacker;
GRANT
```

## 4. Example queries
Take a look into `deploy/omopdb/omop_query.sql`.

## 5. Modifications to the code to do the mapping:
 * `beacon/endpoints/rest/schema/default.py` ==> patched default schema's individuals to contain OMOP's data
 * `beacon/utils/db.py` ==> `fetch_individuals` function contains SQL code to get the individuals data
 
## 6. FHIR Queries

A prototype to perform FHIR queries against a FHIR REST server has been implemented. For the purpose of Biohackaton 
the HAPI test server has been used. The REST server configuration is in the ``conf.py`` file with the following values

```
fhir_schema = 'http'
fhir_host = 'hapi.fhir.org'
fhir_port = '80'
fhir_base_endpoint = 'baseR4'
``` 

This will make queries to ``http://hapi.fhir.org/baseR4``.

To make the REST service work the following has been implemented:

- a REST client ``beacon/utils/fhir_client.py``
- one new schema for generic FHIR Resources in ``beacon/endpoints/rest/schemas/alternative.py`` that just returns the 
  data as returned by the FHIR Server

The endpoint implemented are:

- /api/fhir-individuals: gets all individuls (i.e Patients) in FHIR Server. It also supports the filters parameter
- /api/fhir-individuals/{target_id_req}: gets the individual with id target_id_req 
- /api/fhir-individuals/{target_id_req}/biosamples: gets the biosamples (i.e., the Specimens) of individual with id target_id_req
- /api/fhir-biosamples/: gets all biosamples. It also supports the filters paramater to filter

In order to allow filtering, two types of filters has been implemented:

- gender for individuals: it queries for Patient FHIR Resource by gender. 
   In this case the FHIR internal terminology is used, so possible values for the filters are (male, female, other, unknown)
- sample type for biosamples: it queries for Specimen FHIR Resource by specimen type (e.g., venous blood).
    The terminology used is SNOMED-CT
    
In the index.html it hasa been added two sections:

- FHIR Listings to get all individuals, a specific individual and the biosamples of a specific individual
- FHIR Filter section that will perform the queries for venous blood biosamples and for male/female individuals