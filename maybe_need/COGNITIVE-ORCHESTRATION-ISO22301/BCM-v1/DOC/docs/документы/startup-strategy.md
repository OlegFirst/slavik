# 🚀 BCM Platform Startup Strategy

## ✅ ФИНАЛЬНАЯ СТРАТЕГИЯ ЗАПУСКА

### 1. МИНИМАЛЬНЫЙ ЗАПУСК (5 модулей)
```bash
# Только база для проверки работоспособности
docker-compose up -d postgres redis
sleep 10
docker-compose up -d odoo
# Odoo запустится только с: base, web, mail, bus, portal
```

### 2. УСТАНОВКА BCM МОДУЛЕЙ (после успешного старта)
```bash
# Устанавливаем BCM модули через UI или CLI
docker-compose exec odoo odoo -c /etc/odoo/odoo.conf \
  --init=bcm_core,bcm_base,bcm_config \
  --stop-after-init
```

### 3. ПОЛНАЯ КОНФИГУРАЦИЯ
```bash
# Добавляем остальные модули по необходимости
docker-compose exec odoo odoo -c /etc/odoo/odoo.conf \
  --init=hr,project,website \
  --stop-after-init
```

## 📋 ТЕКУЩАЯ СТРУКТУРА
- **125 модулей всего** в addons/
- **20 BCM модулей**
- **105 системных модулей**

## ⚠️ ПРОБЛЕМЫ С АВТОУСТАНОВКОЙ
- Odoo пытается загрузить ВСЕ модули сразу
- Зависимости тянут лишние модули
- Процесс инициализации зависает

## ✅ РЕШЕНИЕ
1. Запуск с минимумом
2. Поэтапная установка через CLI
3. Контроль зависимостей