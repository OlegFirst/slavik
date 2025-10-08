# Module Scan Report: observability

**Дата сканирования:** 2025-10-08 16:44
**Путь:** `infrastructure/observability`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 1899 |
| **Python файлов** | 6 |
| **Классов** | 7 |
| **Функций** | 16 |
| **API Endpoints** | 10 |
| **Зависимостей** | 32 |

---

## 🔗 Зависимости (32)


### ai_foundation
- `ai_foundation/intelligent_core`

### argparse
- `argparse`

### asyncio
- `asyncio`

### database
- `database/postgresql`
- `database/vector-db`

### datetime
- `datetime`

### dotenv
- `dotenv`

### email.mime.multipart
- `email.mime.multipart`

### email.mime.text
- `email.mime.text`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.responses
- `fastapi.responses`

### httpx
- `httpx`

### intelligent_core.ai_foundation.learning_knowledge.monitoring
- `intelligent_core.ai_foundation.learning_knowledge.monitoring`

### intelligent_core.ai_foundation.llm
- `intelligent_core.ai_foundation.llm`

### intelligent_core.ai_foundation.rag
- `intelligent_core.ai_foundation.rag`

### json
- `json`

### logging
- `logging`

### os
- `os`

### pathlib
- `pathlib`

### pika
- `pika`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### random
- `random`

### runtime
- `runtime/eventbus`

### smtplib
- `smtplib`

### sys
- `sys`

### time
- `time`

### typing
- `typing`

### uvicorn
- `uvicorn`

### werkzeug.middleware.dispatcher
- `werkzeug.middleware.dispatcher`

### werkzeug.serving
- `werkzeug.serving`

---

## 🌐 API Endpoints (10)

- **GET** `/metrics` (файл: `add_metrics_to_services.py`)
- **GET** `/metrics\` (файл: `add_metrics_to_services.py`)
- **GET** `/health` (файл: `main.py`)
- **POST** `/email/send` (файл: `main.py`)
- **POST** `/sms/send` (файл: `main.py`)
- **POST** `/push/send` (файл: `main.py`)
- **POST** `/webhook/send` (файл: `main.py`)
- **GET** `/notifications/history` (файл: `main.py`)
- **GET** `/notifications/stats` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)

---

## 💻 Классы (7)

- **QdrantExporter** (2 методов) - `qdrant_exporter.py`
- **ExternalNotificationService** (1 методов) - `external_integrations.py`
- **NotificationRequest** (0 методов) - `external_integrations.py`
- **EmailNotification** (0 методов) - `main.py`
- **SMSNotification** (0 методов) - `main.py`
- **PushNotification** (0 методов) - `main.py`
- **WebhookNotification** (0 методов) - `main.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 16787 символов (696 строк)

**Превью:**
```
# 📊 BCM Platform - Observability Stack

**Полная система мониторинга и наблюдаемости для BCM платформы**

> ✅ **Статус:** Production Ready
> 📅 **Обновлено:** 2025-10-08
> 🔧 **Инфраструктура:** Supabase + Upstash Redis + Qdrant Cloud

---

## 📋 Содержание

- [Компоненты](#компоненты)
- [Архитектура](#архитектура)
- [Быстрый старт](#быстрый-старт)
- [Конфигурация](#конфигурация)
- [Grafana Dashboards](#grafana-dashboards)
- [Prometheus Targets](#prometheus-targets)
- [Troubleshooting](#troubleshooting)
- [Production Checklist](#production-checklist)

---

## 🏗️ Компоненты

### Infrastructure Monitoring

| Компонент | Порт | Описание |
|-----------|------|----------|
| **Prometheus** | 9090 | Сбор метрик и мониторинг |
| **Grafana** | 3000 | Визуализация и дашборды |
| **Loki** | 3100 | Агрегация логов |
| **Promtail** | - | Сборщик логов |
| **AlertManager** | 9093 | Управление алертами |

### Observability Services

| Сервис | Порт | Назначение |
|--------|------|-----------|
| **compli
```

---

## ⚙️ Конфигурация

- `.env` → `infrastructure/observability/.env`
- `.env.example` → `infrastructure/observability/.env.example`

---

## 📂 Структура

**Всего файлов:** 65
**Директорий:** 20
