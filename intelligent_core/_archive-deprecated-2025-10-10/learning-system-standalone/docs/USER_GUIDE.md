# Learning System Service - Руководство Пользователя

**Версия**: 2.0.0
**Дата**: 2025-10-05

## Содержание

1. [Введение](#введение)
2. [Быстрый Старт](#быстрый-старт)
3. [Основные Функции](#основные-функции)
4. [Практические Примеры](#практические-примеры)
5. [API Использование](#api-использование)
6. [Интеграция с Платформой](#интеграция-с-платформой)
7. [FAQ](#faq)
8. [Troubleshooting](#troubleshooting)

## Введение

### Что такое Learning System?

Learning System - это интеллектуальный сервис, который автоматически учится на результатах ваших BCM упражнений и помогает улучшать подготовку команды.

**Ключевые возможности**:
- 📊 Автоматический анализ результатов упражнений
- 🔍 Обнаружение паттернов успеха и провала
- 👤 Отслеживание компетенций (индивидуальных и командных)
- 🎮 Геймификация для мотивации
- 🤖 ML предсказания успеха упражнений
- 📚 Персонализированные рекомендации по обучению
- 🔄 Самообучающиеся модели

### Для кого этот сервис?

- **BCM Координаторы** - планирование обучения, анализ эффективности
- **Team Leads** - мониторинг компетенций команды, выявление пробелов
- **Участники Упражнений** - отслеживание личного прогресса, получение рекомендаций
- **Администраторы** - общая аналитика, отчётность

## Быстрый Старт

### Шаг 1: Проверка Доступа

```bash
# Проверить, что сервис работает
curl http://localhost:8033/

# Открыть API документацию
open http://localhost:8033/docs
```

### Шаг 2: Первый Запрос

```python
import httpx
import asyncio

async def main():
    # Получить информацию о сервисе
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8033/")
        print(response.json())

asyncio.run(main())
```

### Шаг 3: Анализ Результатов

После проведения упражнения, загрузите результаты для анализа:

```python
import httpx
import asyncio

async def analyze_exercise():
    exercise_result = {
        "exercise_id": "ex_001",
        "user_id": "user_123",
        "scenario_type": "cyber_incident",
        "overall_score": 75,
        "subscores": {
            "incident_detection": 80,
            "escalation": 70,
            "communication": 75,
            "technical_response": 78
        },
        "conducted_at": "2025-10-05T10:00:00Z",
        "duration_minutes": 120,
        "team_size": 12
    }

    async with httpx.AsyncClient() as client:
        # Анализ результатов
        response = await client.post(
            "http://localhost:8033/api/learning/analyze",
            json={"exercise_results": [exercise_result]}
        )

        analysis = response.json()
        print(f"Анализ завершён: {analysis}")

asyncio.run(analyze_exercise())
```

## Основные Функции

### 1. Обнаружение Паттернов

Learning System автоматически обнаруживает повторяющиеся паттерны в результатах упражнений.

**Типы паттернов**:
- **Success Patterns** - что работает хорошо
- **Failure Patterns** - где регулярно возникают проблемы
- **Improvement Patterns** - тренды улучшения
- **Decline Patterns** - тренды ухудшения

**Пример использования**:

```python
async def detect_patterns():
    # Загрузить результаты последних упражнений
    results = await get_recent_exercises(limit=20)

    # Обнаружить паттерны
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8033/api/learning/patterns/detect",
            json={
                "exercise_results": results,
                "min_confidence": 0.7  # минимальная уверенность 70%
            }
        )

        patterns = response.json()

        # Показать обнаруженные паттерны
        for pattern in patterns['patterns']:
            print(f"""
            Паттерн: {pattern['pattern_name']}
            Тип: {pattern['pattern_type']}
            Уверенность: {pattern['confidence']*100:.0f}%
            Рекомендации: {', '.join(pattern['recommendations'])}
            """)
```

**Что вы получите**:
```
Паттерн: Проблемы коммуникации в киберинцидентах
Тип: failure_pattern
Уверенность: 85%
Рекомендации:
  - Добавить обучение по протоколам эскалации
  - Внедрить автоматические уведомления
  - Провести дополнительные тренинги по коммуникации
```

### 2. Отслеживание Компетенций

Система отслеживает 9 ключевых компетенций BCM:

1. **incident_detection** - Обнаружение инцидентов
2. **escalation** - Эскалация
3. **communication** - Коммуникация
4. **technical_response** - Технический ответ
5. **decision_making** - Принятие решений
6. **coordination** - Координация
7. **documentation** - Документирование
8. **recovery** - Восстановление
9. **assessment** - Оценка

**Пример: Проверка своих компетенций**

```python
async def check_my_competencies(user_id: str):
    async with httpx.AsyncClient() as client:
        # Получить текущие компетенции
        response = await client.get(
            f"http://localhost:8033/api/learning/competency/user/{user_id}"
        )

        profile = response.json()

        print(f"Общий уровень: {profile['overall_avg']:.1f}/100")
        print(f"\nСильные стороны:")
        for comp in profile['strongest_competencies']:
            print(f"  ✓ {comp}")

        print(f"\nОбласти для развития:")
        for comp in profile['weakest_competencies']:
            print(f"  ⚠ {comp}")

        print(f"\nКомпетенции под риском деградации:")
        for comp in profile['competencies_at_risk']:
            print(f"  ⏰ {comp} - давно не практиковали")
```

**Вывод**:
```
Общий уровень: 78.5/100

Сильные стороны:
  ✓ technical_response (92/100)
  ✓ incident_detection (88/100)
  ✓ documentation (85/100)

Области для развития:
  ⚠ communication (65/100)
  ⚠ escalation (68/100)

Компетенции под риском деградации:
  ⏰ recovery - давно не практиковали (120 дней)
```

### 3. Анализ Команды

**Проверка готовности команды**:

```python
async def analyze_team(team_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8033/api/learning/competency/team/{team_name}"
        )

        team_analysis = response.json()

        print(f"Команда: {team_name}")
        print(f"Размер: {team_analysis['team_size']} человек")
        print(f"Средний уровень: {team_analysis['avg_competency']:.1f}/100")

        # Пробелы в покрытии
        print("\nПробелы в покрытии:")
        for gap in team_analysis['coverage_gaps']:
            print(f"  ⚠ {gap['competency']}")
            print(f"    Требуется: {gap['required_coverage']} человек")
            print(f"    Доступно: {gap['available_coverage']} человек")
            print(f"    Дефицит: {gap['gap']} человек")

        # Рекомендации
        print("\nРекомендации по обучению:")
        for rec in team_analysis['training_recommendations']:
            print(f"  • {rec}")
```

### 4. Геймификация

**Проверка своего профиля**:

```python
async def check_gamification_profile(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8033/api/learning/gamification/profile/{user_id}"
        )

        profile = response.json()

        print(f"""
        🎮 Игровой Профиль

        Уровень: {profile['level']}
        Очки: {profile['total_points']}

        Текущая серия: {profile['streak_days']} дней 🔥
        Лучшая серия: {profile['longest_streak']} дней

        Упражнений выполнено: {profile['exercises_completed']}
        Бейджей получено: {profile['badges_earned']}

        Место в лидерборде: #{profile['rank']}
        """)

        # Заработанные бейджи
        badges_response = await client.get(
            f"http://localhost:8033/api/learning/gamification/badges/{user_id}"
        )
        badges = badges_response.json()

        print("🏆 Заработанные бейджи:")
        for badge in badges['earned']:
            print(f"  {badge['badge_name']} - {badge['earned_at']}")
```

### 5. ML Предсказания

**Предсказать успех будущего упражнения**:

```python
async def predict_exercise_success():
    # Параметры планируемого упражнения
    exercise_plan = {
        "scenario_type": "cyber_incident",
        "team_size": 12,
        "avg_competency": 0.75,
        "days_since_last_exercise": 45,
        "historical_scores": [78, 82, 85]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8033/api/learning/platform/ml/predict-success",
            json=exercise_plan
        )

        prediction = response.json()

        print(f"""
        🎯 Предсказание Успеха Упражнения

        Ожидаемый результат: {prediction['predicted_score']:.1f}/100
        Уверенность: {prediction['confidence']*100:.0f}%
        Вероятность успеха: {prediction['success_probability']*100:.0f}%

        Уровень риска: {prediction['risk_level'].upper()}

        Рекомендации:
        """)

        for rec in prediction['recommendations']:
            print(f"  • {rec}")
```

**Вывод**:
```
🎯 Предсказание Успеха Упражнения

Ожидаемый результат: 83.5/100
Уверенность: 82%
Вероятность успеха: 85%

Уровень риска: LOW

Рекомендации:
  • Команда хорошо подготовлена для этого сценария
  • Рассмотрите увеличение сложности для дополнительного вызова
```

### 6. Персонализированные Рекомендации

**Получить рекомендации по обучению**:

```python
async def get_learning_recommendations(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8033/api/learning/recommendations/{user_id}"
        )

        recommendations = response.json()

        print("📚 Персонализированные Рекомендации\n")

        for i, rec in enumerate(recommendations['recommendations'], 1):
            print(f"{i}. {rec['title']}")
            print(f"   Приоритет: {rec['priority']}")
            print(f"   Причина: {rec['reason']}")
            print(f"   Ресурсы: {', '.join(rec['resources'])}")
            print()
```

**Вывод**:
```
📚 Персонализированные Рекомендации

1. Улучшение Навыков Коммуникации
   Приоритет: HIGH
   Причина: Обнаружен паттерн проблем в коммуникации (confidence: 85%)
   Ресурсы: Протоколы эскалации, Тренинг коммуникации, Чеклисты

2. Практика Эскалации
   Приоритет: MEDIUM
   Причина: Компетенция ниже среднего (68/100)
   Ресурсы: Процедуры эскалации, Сценарии упражнений

3. Обновление Навыков Восстановления
   Приоритет: MEDIUM
   Причина: Риск деградации (120 дней без практики)
   Ресурсы: Процедуры восстановления, DR планы
```

## Практические Примеры

### Сценарий 1: Планирование Упражнения

**Задача**: Планируем cyber incident упражнение, хотим предсказать результат и получить рекомендации.

```python
async def plan_exercise():
    # 1. Проверить компетенции команды
    team_response = await client.get(
        "http://localhost:8033/api/learning/competency/team/security-team"
    )
    team = team_response.json()

    # 2. Предсказать успех
    prediction_response = await client.post(
        "http://localhost:8033/api/learning/platform/ml/predict-success",
        json={
            "scenario_type": "cyber_incident",
            "team_size": team['team_size'],
            "avg_competency": team['avg_competency'] / 100
        }
    )
    prediction = prediction_response.json()

    # 3. Если риск высокий - получить рекомендации
    if prediction['risk_level'] in ['medium', 'high']:
        recommendations_response = await client.post(
            "http://localhost:8033/api/learning/platform/unified/predict-and-recommend",
            json={
                "scenario_type": "cyber_incident",
                "team_size": team['team_size'],
                "avg_competency": team['avg_competency'] / 100
            }
        )
        result = recommendations_response.json()

        print(f"⚠ Риск: {prediction['risk_level']}")
        print(f"Рекомендуемая подготовка:")
        for resource in result['learning_resources']:
            print(f"  • {resource['title']} ({resource['duration_hours']}ч)")
```

### Сценарий 2: Анализ После Упражнения

**Задача**: Упражнение завершено, нужно проанализировать результаты.

```python
async def post_exercise_analysis(exercise_results):
    # 1. Обнаружить паттерны
    patterns_response = await client.post(
        "http://localhost:8033/api/learning/patterns/detect",
        json={"exercise_results": exercise_results}
    )
    patterns = patterns_response.json()

    # 2. Обновить компетенции
    for result in exercise_results:
        await client.post(
            "http://localhost:8033/api/learning/competency/calculate",
            json={
                "user_id": result['user_id'],
                "exercise_results": [result]
            }
        )

    # 3. Обновить геймификацию
    for result in exercise_results:
        await client.post(
            "http://localhost:8033/api/learning/gamification/activity",
            json={
                "user_id": result['user_id'],
                "activity_type": "exercise_completion",
                "score": result['overall_score']
            }
        )

    # 4. Если было предсказание - отправить feedback
    if result.get('prediction_id'):
        await client.post(
            "http://localhost:8033/api/learning/platform/ml/submit-feedback",
            json={
                "prediction_id": result['prediction_id'],
                "actual_score": result['overall_score']
            }
        )

    # 5. Получить обновлённые рекомендации
    for result in exercise_results:
        recommendations = await client.get(
            f"http://localhost:8033/api/learning/recommendations/{result['user_id']}"
        )
        # Отправить участникам
```

### Сценарий 3: Мониторинг Команды

**Задача**: Ежемесячный review команды.

```python
async def monthly_team_review(team_name: str):
    # 1. Анализ команды
    team = await client.get(
        f"http://localhost:8033/api/learning/competency/team/{team_name}"
    )

    # 2. Лидерборд
    leaderboard = await client.get(
        "http://localhost:8033/api/learning/gamification/leaderboard",
        params={"team": team_name}
    )

    # 3. Паттерны за месяц
    last_month_results = await get_results_for_period(days=30)
    patterns = await client.post(
        "http://localhost:8033/api/learning/patterns/detect",
        json={"exercise_results": last_month_results}
    )

    # 4. Генерация отчёта
    report = {
        "period": "last_30_days",
        "team_competency_avg": team['avg_competency'],
        "exercises_completed": len(last_month_results),
        "top_performers": leaderboard['top_3'],
        "patterns_detected": patterns['patterns'],
        "training_recommendations": team['training_recommendations']
    }

    return report
```

## API Использование

### Аутентификация

Все запросы требуют JWT токен:

```python
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

response = await client.get(
    "http://localhost:8033/api/learning/progress/user_123",
    headers=headers
)
```

### Rate Limits

| Endpoint | Лимит |
|----------|-------|
| Pattern detection | 10 req/min |
| Competency calculation | 20 req/min |
| ML predictions | 30 req/min |
| General API | 100 req/min |

### Error Handling

```python
try:
    response = await client.post(url, json=data)
    response.raise_for_status()
    result = response.json()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 429:
        print("Rate limit exceeded, retry later")
    elif e.response.status_code == 400:
        error = e.response.json()
        print(f"Validation error: {error['message']}")
    else:
        print(f"Error: {e}")
```

## Интеграция с Платформой

### RAG Semantic Search

Поиск знаний по всей платформе:

```python
# Найти ресурсы по теме
response = await client.post(
    "http://localhost:8033/api/learning/platform/rag/search",
    json={
        "query": "как улучшить коммуникацию при киберинцидентах",
        "context": {"domain": "BCM", "user_id": "user_123"},
        "filters": {"type": ["procedure", "guideline"]},
        "limit": 10
    }
)
```

### ML Platform Integration

Общие ML модели для всех сервисов:

```python
# Предсказание
prediction = await client.post(
    "http://localhost:8033/api/learning/platform/ml/predict-success",
    json={...}
)

# Feedback после упражнения
await client.post(
    "http://localhost:8033/api/learning/platform/ml/submit-feedback",
    json={
        "prediction_id": prediction['prediction_id'],
        "actual_score": 82.0
    }
)
```

## FAQ

**Q: Как часто обновляются компетенции?**
A: Компетенции обновляются сразу после каждого упражнения. Также учитывается деградация навыков (skills decay) - чем дольше не практикуете, тем ниже score.

**Q: Что такое confidence в паттернах?**
A: Confidence - это уверенность системы, что паттерн реален (не случайность). Мы рекомендуем обращать внимание на паттерны с confidence >= 70%.

**Q: Как работает геймификация?**
A: За каждое упражнение вы получаете очки. Больше очков за высокие результаты, улучшения, серии. Очки дают уровни и бейджи.

**Q: Можно ли сбросить/пересчитать компетенции?**
A: Да, через админ API. Но обычно не нужно - система учитывает все упражнения с весами (свежие важнее старых).

**Q: Что делать, если предсказание было неточным?**
A: Обязательно отправьте feedback через `/ml/submit-feedback`. Модель учится на реальных результатах и становится точнее.

## Troubleshooting

### Проблема: "Service unavailable"

```bash
# Проверить статус
curl http://localhost:8033/

# Проверить логи
docker logs learning-system

# Проверить health
curl http://localhost:8033/health/ready
```

### Проблема: "Platform services unavailable"

Learning System работает в fallback режиме, если RAG/ML Platform/KB недоступны:

```bash
# Проверить статус интеграции
curl http://localhost:8033/api/learning/platform/status
```

### Проблема: "No patterns detected"

- Нужно минимум 3 упражнения одного типа
- Проверьте `min_confidence` (попробуйте 0.5)
- Убедитесь, что результаты разнообразные (не все одинаковые)

### Проблема: "Competencies not updating"

```python
# Проверить, что результаты корректные
result = {
    "user_id": "...",  # обязательно
    "scenario_type": "...",  # обязательно
    "subscores": {...}  # обязательно - отдельные компетенции
}
```

---

**Нужна помощь?**
- Документация: [README.md](README.md)
- Техническая спецификация: [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md)
- API Docs: http://localhost:8033/docs
