#!/bin/bash

# !:@8?B 4;O 8=8F80;870F88 107K 40==KE Keycloak

# @>25@O5< =0;8G85 ?5@5<5==>9 KEYCLOAK_DB_PASSWORD
if [ -z "$KEYCLOAK_DB_PASSWORD" ]; then
  echo "H81:0: KEYCLOAK_DB_PASSWORD =5 CAB0=>2;5=0. A?>;L7C5< ?0@>;L ?> C<>;G0=8N."
  KEYCLOAK_DB_PASSWORD="keycloak_db_2024"
fi

# !>7405< ?>;L7>20B5;O 8 107C 40==KE 4;O Keycloak
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER keycloak WITH PASSWORD '$KEYCLOAK_DB_PASSWORD';
    CREATE DATABASE keycloak;
    GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;
EOSQL

echo "070 40==KE Keycloak CA?5H=> 8=8F80;878@>20=0"