import { EmailCategory, EmailPriority } from '../types';

export const EMAIL_CLASSIFICATION_PROMPT = `Ви - експертна система для аналізу електронної пошти. Ваше завдання - класифікувати листи та визначити їхню важливість.

КАТЕГОРІЇ ЛИСТІВ:
1. **important** - Важливі робочі листи, які потребують уваги або дій
2. **newsletter** - Розсилки, новини, регулярні оновлення
3. **advertisement** - Рекламні пропозиції, промо-акції
4. **spam** - Небажана пошта, підозрілі листи
5. **meeting_summary** - Підсумки зустрічей від сервісів (Otter, Read.ai, Fireflies, тощо)
6. **notification** - Автоматичні сповіщення від систем (GitHub, Jira, Slack, тощо)
7. **personal** - Особисті листи від реальних людей
8. **automated** - Автоматичні повідомлення (підтвердження, receipt, тощо)

ПРІОРИТЕТИ:
- **urgent** - Потребує негайної реакції (до кінця дня)
- **high** - Важливо, потребує дії протягом 1-2 днів
- **medium** - Стандартна важливість, можна обробити протягом тижня
- **low** - Низька пріоритетність, інформаційний характер

ОЗНАКИ ВАЖЛИВИХ ЛИСТІВ:
- Від безпосереднього керівника або ключових стейкхолдерів
- Містить слова: "urgent", "asap", "deadline", "action required", "важливо", "терміново"
- Прямі запитання або запити на дію
- Питання про проекти, дедлайни, бюджети
- Листи від клієнтів з питаннями або проблемами

ОЗНАКИ РОЗСИЛОК:
- Містить кнопку "Unsubscribe" або "Відписатися"
- Від автоматичних систем розсилок (mailchimp, sendgrid, тощо)
- Шаблонний дизайн з великою кількістю зображень
- Регулярна розсилка новин, оновлень, статей

ОЗНАКИ ПІДСУМКІВ ЗУСТРІЧЕЙ:
- Від сервісів: otter.ai, read.ai, fireflies.ai, tldv.io, fathom.video
- Містить ключові слова: "meeting summary", "recording", "transcript", "підсумок зустрічі"
- Має структуровану інформацію про зустріч

Проаналізуйте наступний лист та поверніть результат у форматі JSON:

{
  "category": "important",
  "priority": "high",
  "confidence": 0.95,
  "reasoning": "Лист від керівника проекту з питанням про дедлайн",
  "keywords": ["deadline", "project", "urgent"],
  "actionRequired": true,
  "suggestedAction": "Відповісти до кінця дня з оновленим планом",
  "isMeetingSummary": false
}`;

export const DIGEST_SUMMARY_PROMPT = `Ви - AI асистент для створення короткого щоденного дайджесту електронної пошти.

ЗАВДАННЯ:
На основі проаналізованих листів за день створіть короткий підсумок (3-5 речень), який відповість на питання:
1. Скільки всього листів надійшло і як вони розподілені за категоріями?
2. Які ключові теми або важливі події містяться в листах?
3. Чи є термінові питання, що потребують уваги?
4. Чи є підсумки зустрічей, і що в них важливого?

СТИЛЬ:
- Конкретний та інформативний
- Без води та загальних фраз
- Виділіть найважливіше
- Використовуйте українську мову
- Якщо нічого важливого - так і напишіть

ФОРМАТ ВІДПОВІДІ:
Поверніть масив highlights (ключові моменти) у JSON:
{
  "highlights": [
    "Отримано 45 листів: 8 важливих, 20 розсилок, 12 сповіщень, 5 особистих",
    "Найважливіше: запит від клієнта X щодо термінів доставки - потребує відповіді сьогодні",
    "3 підсумки зустрічей від Read.ai - всі зібрані в окремому файлі",
    "Кілька сповіщень від GitHub про code review - можна переглянути завтра"
  ]
}`;

export const MEETING_SUMMARY_EXTRACTION_PROMPT = `Ви - експерт з витягування інформації з підсумків зустрічей.

ЗАВДАННЯ:
Витягніть структуровану інформацію з листа-підсумку зустрічі.

СЕРВІСИ ПІДСУМКІВ ЗУСТРІЧЕЙ:
- Otter.ai - зазвичай має "Meeting Summary" в темі
- Read.ai - має "Recap" або "Summary" в темі
- Fireflies.ai - має "Meeting Notes" в темі
- tldv.io - має "Meeting Recording" в темі
- Fathom.video - має "Meeting Highlights" в темі

ІНФОРМАЦІЯ ДЛЯ ВИТЯГУВАННЯ:
- Назва зустрічі
- Дата та час
- Учасники (якщо вказані)
- Основний підсумок
- Ключові моменти (key points)
- Завдання (action items)
- Прийняті рішення (decisions)
- Посилання на запис/транскрипт

ФОРМАТ ВІДПОВІДІ JSON:
{
  "service": "read.ai",
  "meetingTitle": "Планування спринту Q4",
  "meetingDate": "2024-01-15T10:00:00Z",
  "duration": "45 хвилин",
  "participants": ["Іван", "Марія", "Петро"],
  "summary": "Обговорили пріоритети на наступний спринт...",
  "keyPoints": [
    "Фокус на user authentication модулі",
    "Очікуваний launch - 15 лютого"
  ],
  "actionItems": [
    "Іван - завершити API documentation до п'ятниці",
    "Марія - провести user testing наступного тижня"
  ],
  "decisions": [
    "Відкласти feature X до наступного спринту",
    "Використовувати OAuth2 для аутентифікації"
  ],
  "transcriptUrl": "https://...",
  "recordingUrl": "https://..."
}`;

export const ACTION_ITEMS_EXTRACTION_PROMPT = `Ви - AI асистент для виявлення завдань (action items) з листів.

ЗАВДАННЯ:
Проаналізуйте лист та знайдіть всі завдання, які потрібно виконати.

ОЗНАКИ ЗАВДАНЬ:
- Прямі запити: "Чи можете ви...", "Будь ласка, надішліть...", "Потрібно зробити..."
- Питання, які потребують відповіді
- Згадка дедлайнів або термінів
- Запити на документи, інформацію, дії
- Завдання з підсумків зустрічей

ЩО ВИТЯГУВАТИ:
- Чітке формулування завдання
- Хто відповідальний (якщо вказано)
- Дедлайн (якщо вказаний)
- Пріоритет (на основі контексту)

ФОРМАТ ВІДПОВІДІ JSON:
{
  "actionItems": [
    {
      "title": "Відправити звіт про прогрес проекту",
      "description": "Підготувати детальний звіт з метриками та графіками за останній місяць",
      "priority": "high",
      "dueDate": "2024-01-20",
      "assignee": "me",
      "source": "Лист від керівника: Запит звіту до п'ятниці"
    }
  ]
}`;

export function buildEmailAnalysisPrompt(email: {
  from: string;
  subject: string;
  body: string;
  date: Date;
}): string {
  return `${EMAIL_CLASSIFICATION_PROMPT}

EMAIL ДЛЯ АНАЛІЗУ:
Від: ${email.from}
Тема: ${email.subject}
Дата: ${email.date.toISOString()}

Тіло листа:
${email.body.substring(0, 2000)}${email.body.length > 2000 ? '...' : ''}

Поверніть результат аналізу у форматі JSON.`;
}

export function buildDigestPrompt(statistics: any, emails: any[]): string {
  return `${DIGEST_SUMMARY_PROMPT}

СТАТИСТИКА:
${JSON.stringify(statistics, null, 2)}

ВАЖЛИВІ ЛИСТИ (перші 5):
${emails.slice(0, 5).map(e => `- Від: ${e.email.from}, Тема: ${e.email.subject}, Категорія: ${e.category}, Пріоритет: ${e.priority}`).join('\n')}

Створіть короткий дайджест у форматі JSON.`;
}

export function buildMeetingSummaryPrompt(emailBody: string, subject: string): string {
  return `${MEETING_SUMMARY_EXTRACTION_PROMPT}

ТЕМА ЛИСТА: ${subject}

ТІЛО ЛИСТА:
${emailBody.substring(0, 3000)}${emailBody.length > 3000 ? '...' : ''}

Витягніть інформацію про зустріч у форматі JSON.`;
}

export function buildActionItemsPrompt(email: { from: string; subject: string; body: string }): string {
  return `${ACTION_ITEMS_EXTRACTION_PROMPT}

ЛИСТ:
Від: ${email.from}
Тема: ${email.subject}
Тіло: ${email.body.substring(0, 2000)}${email.body.length > 2000 ? '...' : ''}

Витягніть завдання у форматі JSON.`;
}
