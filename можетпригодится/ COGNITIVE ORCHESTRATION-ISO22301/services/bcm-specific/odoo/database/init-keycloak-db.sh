#!/bin/bash

# Скрипт для инициализации базы данных Keycloak

# Проверяем наличие переменной KEYCLOAK_DB_PASSWORD
if [ -z "$KEYCLOAK_DB_PASSWORD" ]; then
  echo "Ошибка: KEYCLOAK_DB_PASSWORD не установлена. Используем пароль по умолчанию."
  KEYCLOAK_DB_PASSWORD="keycloak_db_2024"
fi

# Создаем пользователя и базу данных для Keycloak
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER keycloak WITH PASSWORD '$KEYCLOAK_DB_PASSWORD';
    CREATE DATABASE keycloak;
    GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;
EOSQL

echo "База данных Keycloak успешно инициализирована"
