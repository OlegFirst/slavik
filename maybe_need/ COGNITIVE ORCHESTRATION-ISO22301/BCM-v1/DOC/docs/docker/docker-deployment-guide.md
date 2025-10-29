# BCM Odoo Docker Deployment Guide

## Способы развертывания образа

### 1. Локальное использование (уже готово)
```bash
# Использовать локальный образ
docker run -d --name bcm-odoo -p 8069:8069 bcm-odoo:pr-99
```

### 2. Docker Hub развертывание

#### Шаг 1: Авторизация в Docker Hub
```bash
docker login
# Введите ваши credentials от Docker Hub
```

#### Шаг 2: Загрузка образа
```bash
# Пересоздать тег с вашим Docker Hub username
docker tag bcm-odoo:pr-99 YOUR_DOCKERHUB_USERNAME/bcm-odoo:pr-99
docker tag bcm-odoo:pr-99 YOUR_DOCKERHUB_USERNAME/bcm-odoo:latest

# Загрузить на Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/bcm-odoo:pr-99
docker push YOUR_DOCKERHUB_USERNAME/bcm-odoo:latest
```

#### Шаг 3: Обновить docker-compose.yml
```yaml
services:
  odoo:
    image: YOUR_DOCKERHUB_USERNAME/bcm-odoo:pr-99
    # остальная конфигурация...
```

#### Шаг 4: Использование на удаленных серверах
```bash
# На любом сервере с Docker
docker pull YOUR_DOCKERHUB_USERNAME/bcm-odoo:pr-99
docker run -d --name bcm-odoo -p 8069:8069 YOUR_DOCKERHUB_USERNAME/bcm-odoo:pr-99
```

### 3. GitHub Container Registry (рекомендуется)

#### Шаг 1: Авторизация в GHCR
```bash
# Создайте GitHub Personal Access Token с правами packages
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

#### Шаг 2: Загрузка в GHCR
```bash
# Пересоздать тег для GHCR
docker tag bcm-odoo:pr-99 ghcr.io/seh-foundation/bcm-odoo:pr-99
docker tag bcm-odoo:pr-99 ghcr.io/seh-foundation/bcm-odoo:latest

# Загрузить в GHCR
docker push ghcr.io/seh-foundation/bcm-odoo:pr-99
docker push ghcr.io/seh-foundation/bcm-odoo:latest
```

#### Шаг 3: Обновить docker-compose.yml для GHCR
```yaml
services:
  odoo:
    image: ghcr.io/seh-foundation/bcm-odoo:pr-99
    # остальная конфигурация...
```

### 4. Быстрый деплой на популярных платформах

#### Railway
```bash
# В корне проекта создать railway.toml
railway login
railway deploy
```

#### Render
- Подключить GitHub репозиторий
- Указать образ: `ghcr.io/seh-foundation/bcm-odoo:pr-99`
- Настроить переменные окружения

#### DigitalOcean App Platform
- Создать приложение из Docker образа
- Указать: `ghcr.io/seh-foundation/bcm-odoo:pr-99`

#### Google Cloud Run
```bash
gcloud run deploy bcm-odoo \
  --image=ghcr.io/seh-foundation/bcm-odoo:pr-99 \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated
```

## Преимущества разных подходов

### Docker Hub
✅ Простота использования
✅ Публичные репозитории бесплатны
❌ Лимиты на pull'ы для бесплатных аккаунтов

### GitHub Container Registry (GHCR)
✅ Интеграция с GitHub
✅ Неограниченные приватные образы
✅ Хорошие лимиты
❌ Нужен GitHub Personal Access Token

### Локальный файл
✅ Нет зависимости от интернета
✅ Полный контроль
❌ Нужно передавать файл вручную

## Рекомендации

1. **Для разработки**: используйте локальный образ
2. **Для продакшна**: GHCR или Docker Hub
3. **Для CI/CD**: GHCR с автоматическими workflow

## Текущее состояние

- ✅ Образ собран: `bcm-odoo:pr-99`
- ✅ docker-compose.yml обновлен
- ✅ Локальный tar файл создан: `bcm-odoo-pr99.tar`
- ⚠️  Нужна авторизация для загрузки в registry

## Содержимое образа

- **Базовый образ**: odoo:18.0
- **BCM модули**: 39 модулей из `./core/odoo-18.0/addons/bcm_*`
- **Python пакеты**: numpy, pandas, scikit-learn, matplotlib, scipy, PyJWT, python-jose, cryptography, jwt, redis, python-dotenv, httpx, pydantic, fastapi
- **Размер**: ~3.88GB
- **Порт**: 8069