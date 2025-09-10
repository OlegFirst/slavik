"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PRESS_RELEASE_PROMPT = void 0;
exports.PRESS_RELEASE_PROMPT = {
    id: 'press-release',
    name: 'Press Release Generator',
    description: 'Створення професійних прес-релізів для анонсування новин, продуктів або подій',
    category: 'PR & Marketing',
    outputFormat: 'markdown',
    systemPrompt: `Ви - професійний копірайтер та PR-спеціаліст з 10+ роками досвіду. Ваше завдання - створити високоякісний прес-реліз на основі наданої інформації.

ПРИНЦИПИ СТВОРЕННЯ ПРЕС-РЕЛІЗУ:

1. СТРУКТУРА (обов'язково дотримуватися):
   - Заголовок (привертає увагу, містить ключову інформацію)
   - Підзаголовок (розкриває деталі заголовку)
   - Дата і місце
   - Лід-абзац (відповідає на 5W+H: хто, що, де, коли, чому, як)
   - Основний текст (2-3 абзаци з деталями)
   - Цитати (1-2 цитати від керівництва/експертів)
   - Інформація про компанію (boilerplate)
   - Контактна інформація

2. СТИЛЬ НАПИСАННЯ:
   - Активний стан замість пасивного
   - Короткі, зрозумілі речення
   - Третя особа
   - Професійний, але доступний тон
   - Фактичність та об'єктивність
   - Використання цифр та конкретних даних

3. NEWSJACKING ТЕХНІКИ:
   - Зв'язок з актуальними трендами/новинами
   - Використання ключових слів для SEO
   - Емоційний крюк у заголовку
   - Соціальна значущість

4. КРИТЕРІЇ ЯКОСТІ:
   - Новинність (що нового?)
   - Актуальність (чому це важливо зараз?)
   - Цільова аудиторія (для кого це цікаво?)
   - Унікальність (що робить це особливим?)

ВИМОГИ ДО КОНТЕНТУ:
- Заголовок: 60-80 символів
- Лід-абзац: 25-35 слів, максимум 2 речення
- Загальний обсяг: 300-500 слів
- Читабельність: рівень 8-10 класу
- Обов'язкове включення всіх наданих фактів
- Природне включення ключових слів

Створюйте прес-реліз, який журналісти захочуть опублікувати!`,
    requiredFields: [
        {
            name: 'companyName',
            type: 'text',
            description: 'Назва компанії або організації',
            required: true,
            placeholder: 'ТОВ "Інноваційні технології"'
        },
        {
            name: 'announcementType',
            type: 'select',
            description: 'Тип анонсування',
            required: true,
            options: [
                'Запуск нового продукту',
                'Оновлення продукту/сервісу',
                'Партнерство/співпраця',
                'Інвестиції/фінансування',
                'Нагороди/досягнення',
                'Призначення керівництва',
                'Експансія/відкриття офісів',
                'Дослідження/статистика',
                'Подія/конференція',
                'CSR ініціатива'
            ]
        },
        {
            name: 'mainNews',
            type: 'textarea',
            description: 'Основна новина (що саме відбулося?)',
            required: true,
            placeholder: 'Опишіть головну новину в 2-3 реченнях...'
        },
        {
            name: 'keyBenefits',
            type: 'textarea',
            description: 'Ключові переваги/вигоди для цільової аудиторії',
            required: true,
            placeholder: 'Перелічіть 3-5 основних переваг...'
        },
        {
            name: 'targetAudience',
            type: 'text',
            description: 'Цільова аудиторія',
            required: true,
            placeholder: 'IT-спеціалісти, стартапи, великі корпорації'
        }
    ],
    optionalFields: [
        {
            name: 'executiveQuote',
            type: 'textarea',
            description: 'Цитата від керівництва',
            required: false,
            placeholder: '«Цей запуск знаменує новий етап...» - каже Іван Петренко, CEO'
        },
        {
            name: 'statistics',
            type: 'textarea',
            description: 'Важливі цифри/статистика',
            required: false,
            placeholder: '50% збільшення ефективності, $1M інвестицій...'
        },
        {
            name: 'location',
            type: 'text',
            description: 'Місце події',
            required: false,
            placeholder: 'Київ, Україна'
        },
        {
            name: 'partnerInfo',
            type: 'text',
            description: 'Інформація про партнерів (якщо є)',
            required: false,
            placeholder: 'За підтримки Google, Microsoft...'
        },
        {
            name: 'timeline',
            type: 'text',
            description: 'Терміни реалізації/доступності',
            required: false,
            placeholder: 'Доступно з лютого 2024, повний запуск до кінця року'
        },
        {
            name: 'companyBackground',
            type: 'textarea',
            description: 'Коротка інформація про компанію (для boilerplate)',
            required: false,
            placeholder: 'Компанія заснована в 2020 році, спеціалізується на...'
        },
        {
            name: 'contactInfo',
            type: 'textarea',
            description: 'Контактна інформація для ЗМІ',
            required: false,
            placeholder: 'Для довідок преси: PR@company.com, +380...'
        },
        {
            name: 'keywords',
            type: 'text',
            description: 'Ключові слова для SEO',
            required: false,
            placeholder: 'штучний інтелект, автоматизація, інновації'
        },
        {
            name: 'relatedTrends',
            type: 'text',
            description: 'Зв\'язок з актуальними трендами',
            required: false,
            placeholder: 'На хвилі зростання попиту на AI-рішення...'
        }
    ]
};
//# sourceMappingURL=PressReleasePrompts.js.map