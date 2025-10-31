# Анализ модулей Odoo для BCM Platform

## 🟢 НЕОБХОДИМЫЕ МОДУЛИ (оставляем)

### Базовые и инфраструктурные:
- **web** - основной веб-интерфейс
- **web_editor** - редактор контента
- **web_tour** - туры/обучение
- **bus** - real-time messaging
- **mail** - почтовая система
- **mail_bot** - бот для чата
- **mail_group** - групповые рассылки
- **portal** - портальный доступ
- **portal_rating** - рейтинги в портале
- **calendar** - календарь событий
- **contacts** - управление контактами
- **http_routing** - маршрутизация HTTP

### Аутентификация и безопасность:
- **auth_signup** - регистрация пользователей
- **auth_totp** - двухфакторная аутентификация
- **auth_totp_portal** - 2FA для портала
- **auth_password_policy** - политика паролей
- **auth_ldap** - LDAP интеграция
- **privacy_lookup** - приватность

### Website (нужны для BCM портала):
- **website** - основной модуль сайта
- **website_mail** - почта на сайте
- **website_profile** - профили пользователей
- **website_forum** - форум (для сообщества BCM)
- **website_blog** - блог (для новостей BCM)
- **website_slides** - презентации/обучение
- **website_partner** - партнерские страницы

### Проектное управление (для BCM планов):
- **project** - управление проектами
- **project_todo** - задачи
- **project_mail_plugin** - интеграция с почтой
- **rating** - рейтинговая система
- **survey** - опросы (для BCM оценок)

### HR (для управления персоналом в BCM):
- **hr** - управление персоналом
- **hr_skills** - навыки сотрудников
- **hr_org_chart** - организационная структура
- **hr_calendar** - календарь HR

### Аналитика и отчетность:
- **analytic** - аналитические счета
- **digest** - дайджесты
- **gamification** - геймификация (для BCM тренировок)

### Утилиты:
- **base_automation** - автоматизация
- **base_import** - импорт данных
- **base_setup** - настройка системы
- **utm** - UTM метки
- **uom** - единицы измерения
- **resource** - управление ресурсами

### Интеграции:
- **sms** - SMS уведомления (для кризисных коммуникаций)
- **google_calendar** - интеграция с Google Calendar
- **google_recaptcha** - защита от ботов

## 🔴 НЕ НУЖНЫЕ МОДУЛИ (удаляем)

### Локализации (не нужны для BCM):
- l10n_ch - швейцарская локализация
- l10n_ua - украинская локализация

### E-commerce и платежи (не используем):
- website_payment
- website_payment_authorize
- website_membership
- website_customer

### Производство и склад (не используем):
- project_mrp
- project_mrp_account
- project_mrp_sale
- project_mrp_stock_landed_costs
- project_stock
- project_stock_account
- project_stock_landed_costs
- project_purchase
- project_purchase_stock

### Бухгалтерия (не используем):
- project_account
- project_sale_expense
- project_hr_expense

### Специфичные интеграции:
- website_jitsi
- website_twitter
- website_google_map
- website_hr_recruitment
- website_mass_mailing
- website_links
- website_cf_turnstile
- google_gmail
- google_account
- web_unsplash
- snailmail
- partner_autocomplete
- phone_validation

### Тестовые модули:
- test_simple
- web_fix
- web_hierarchy

### CRM модули (у нас свой CRM bridge):
- iap_crm
- iap
- iap_mail

### Прочее:
- project_timesheet_holidays
- mail_bot_hr
- website_slides_forum
- website_slides_survey
- mail_plugin
- base_address_extended
- base_geolocalize
- base_iban
- base_vat
- base_sparse_field
- base_import_module
- base_install_request
- resource_mail
- hr_gamification
- html_editor

## 📊 ИТОГО:
- **Оставляем: ~40 модулей**
- **Удаляем: ~66 модулей**