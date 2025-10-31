# Docker Hub Push Instructions

## Проблема с токеном
Текущий токен не имеет прав на push (`authentication required - access token has insufficient scopes`)

## Решение: Создать новый Personal Access Token

### Шаг 1: Создать новый PAT в Docker Hub
1. Идите на https://hub.docker.com/settings/security
2. Нажмите **New Access Token**
3. Название: `BCM-ISO-Push-Token`
4. **Permissions**: выберите **Read, Write, Delete** (или минимум **Read, Write**)
5. Скопируйте новый токен

### Шаг 2: Используйте новый токен
```bash
# Logout и login с новым токеном
docker logout

# Login с новым токеном (замените YOUR_NEW_TOKEN)
echo "YOUR_NEW_TOKEN" | docker login -u maxde4 --password-stdin

# Push образа
docker push maxde4/seh-foundation-iso-22301:pr-99
docker push maxde4/seh-foundation-iso-22301:latest
```

## После успешного push

### Образ будет доступен по адресу:
- **Docker Hub**: https://hub.docker.com/r/maxde4/seh-foundation-iso-22301
- **Pull команда**: `docker pull maxde4/seh-foundation-iso-22301:pr-99`

### Обновить docker-compose.yml:
```yaml
services:
  odoo:
    image: maxde4/seh-foundation-iso-22301:pr-99
    # остальная конфигурация без изменений
```

## Альтернативы, если не хотите создавать новый токен:

### 1. Использовать локальный tar файл
```bash
# На другом сервере
scp bcm-odoo-pr99.tar user@server:/path/to/
ssh user@server "docker load -i /path/to/bcm-odoo-pr99.tar"
```

### 2. Использовать GitHub Actions для автопуша
Создать workflow который будет автоматически пушить при изменениях в main ветке.

## Текущее состояние:
- ✅ Образ собран локально: `bcm-odoo:pr-99`
- ✅ Тег создан: `maxde4/seh-foundation-iso-22301:pr-99`
- ✅ Login в Docker Hub успешен
- ❌ Push заблокирован (нужны права записи в токене)
- ✅ docker-compose.yml обновлен для использования локального образа