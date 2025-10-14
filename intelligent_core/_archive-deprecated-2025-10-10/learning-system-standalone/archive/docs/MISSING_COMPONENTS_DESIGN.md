# 🧩 Недостающие Компоненты Системы Обучения

## Критический Анализ: Что НЕ сделано

---

## 1. ❌ Процесс Сбора Потребностей в Обучении

### Проблема
**Сейчас:** Система пассивно анализирует результаты упражнений, но **НЕ собирает активно потребности в обучении**.

### Решение: Learning Needs Collector

```python
# НОВЫЙ КОМПОНЕНТ: engines/learning_needs_collector.py

class LearningNeedsCollector:
    """
    Автоматический сбор потребностей в обучении

    Источники потребностей:
    1. Результаты упражнений (gaps → needs)
    2. Анализ компетенций (low scores → needs)
    3. User requests (explicit needs)
    4. Regulatory requirements (ISO 22301 → needs)
    5. Emerging threats (новые сценарии → needs)
    6. Industry trends (бенчмарки → needs)
    """

    def collect_needs_from_exercises(self, exercise_results):
        """
        Из пробелов в упражнениях → потребности в обучении

        Пример:
        Gap: "Slow escalation process"
        → Need: "Training on escalation procedures"
        """
        needs = []

        for result in exercise_results:
            for issue in result.key_issues:
                needs.append({
                    'source': 'exercise_gap',
                    'gap': issue,
                    'need_type': 'skill_improvement',
                    'urgency': self._assess_urgency(issue),
                    'affected_users': result.participants,
                    'recommended_training': self._map_gap_to_training(issue)
                })

        return needs

    def collect_needs_from_competencies(self, user_competencies):
        """
        Из низких компетенций → потребности

        Пример:
        Competency: "BIA Execution: 45%"
        → Need: "BIA methodology training"
        """
        needs = []

        for user_comp in user_competencies:
            for competency, score in user_comp.competencies.items():
                if score < 70:  # Threshold
                    needs.append({
                        'source': 'low_competency',
                        'competency': competency,
                        'current_score': score,
                        'target_score': 80,
                        'gap': 80 - score,
                        'user_id': user_comp.user_id,
                        'urgency': 'high' if score < 50 else 'medium',
                        'recommended_training': self._map_competency_to_training(competency)
                    })

        return needs

    def collect_needs_from_regulations(self, iso_requirements):
        """
        Из требований ISO 22301 → потребности

        Пример:
        ISO Clause 8.5: "Exercising and testing"
        → Need: "Training on exercise facilitation"
        """
        needs = []

        for clause, requirement in iso_requirements.items():
            if not self._is_requirement_met(clause):
                needs.append({
                    'source': 'regulatory_requirement',
                    'iso_clause': clause,
                    'requirement': requirement,
                    'urgency': 'critical',
                    'recommended_training': self._map_iso_to_training(clause)
                })

        return needs

    def collect_needs_from_user_requests(self, user_requests):
        """
        Явные запросы пользователей

        Пример:
        User: "Хочу научиться проводить BIA"
        → Need: "BIA execution training"
        """
        needs = []

        for request in user_requests:
            needs.append({
                'source': 'user_request',
                'user_id': request.user_id,
                'request': request.description,
                'urgency': request.priority,
                'recommended_training': self._analyze_request(request)
            })

        return needs

    def prioritize_needs(self, all_needs):
        """
        Приоритизация потребностей

        Критерии:
        - Urgency (critical > high > medium > low)
        - Impact (сколько пользователей затронуто)
        - Compliance risk (ISO требования)
        - Business impact (критичность процесса)
        """
        prioritized = sorted(all_needs, key=lambda n: (
            self._urgency_score(n['urgency']),
            self._impact_score(n),
            self._compliance_score(n),
            self._business_score(n)
        ), reverse=True)

        return prioritized

    def generate_training_plan(self, prioritized_needs):
        """
        Генерация учебного плана

        Выход:
        - Список тренингов в приоритетном порядке
        - Распределение по времени
        - Назначение на пользователей/группы
        """
        plan = {
            'immediate': [],  # Выполнить в течение недели
            'short_term': [],  # 1-4 недели
            'medium_term': [],  # 1-3 месяца
            'long_term': []  # > 3 месяцев
        }

        for need in prioritized_needs:
            timeframe = self._determine_timeframe(need['urgency'])

            plan[timeframe].append({
                'training_id': self._find_training(need),
                'need': need,
                'assigned_to': need.get('user_id') or need.get('affected_users'),
                'estimated_duration': self._estimate_duration(need),
                'deadline': self._calculate_deadline(timeframe)
            })

        return plan
```

---

## 2. ❌ Процесс Самообучения (Self-Learning Loop)

### Проблема
**Сейчас:** ML модели статичны, **НЕ обучаются на новых данных**.

### Решение: Self-Learning Engine

```python
# НОВЫЙ КОМПОНЕНТ: engines/self_learning_engine.py

class SelfLearningEngine:
    """
    Система самообучения

    Цикл:
    1. Предсказание (prediction)
    2. Реальный результат (actual outcome)
    3. Сравнение (prediction vs actual)
    4. Обновление модели (model update)
    5. Валидация (validation)
    """

    def record_prediction(self, prediction_id, prediction_data):
        """
        Шаг 1: Записать предсказание

        Пример:
        prediction_id: "pred_123"
        prediction_data: {
            'predicted_score': 75,
            'confidence': 0.85,
            'model_version': 'v1.0',
            'features_used': {...}
        }
        """
        self.predictions_store[prediction_id] = {
            **prediction_data,
            'timestamp': datetime.now(),
            'status': 'pending'
        }

    def record_actual_outcome(self, prediction_id, actual_data):
        """
        Шаг 2: Записать реальный результат

        Пример:
        actual_data: {
            'actual_score': 68,  # Факт оказался ниже
            'exercise_completed': True
        }
        """
        if prediction_id in self.predictions_store:
            self.predictions_store[prediction_id].update({
                'actual_outcome': actual_data,
                'outcome_timestamp': datetime.now(),
                'status': 'completed'
            })

            # Триггер: Обучение модели
            self._trigger_model_update(prediction_id)

    def _trigger_model_update(self, prediction_id):
        """
        Шаг 3-4: Сравнение и обновление модели
        """
        pred = self.predictions_store[prediction_id]

        # Расчет ошибки
        error = abs(pred['predicted_score'] - pred['actual_outcome']['actual_score'])

        # Анализ ошибки
        error_analysis = {
            'prediction_id': prediction_id,
            'error': error,
            'error_type': 'overestimate' if pred['predicted_score'] > pred['actual_outcome']['actual_score'] else 'underestimate',
            'features_responsible': self._analyze_feature_impact(pred)
        }

        # Накопление данных для переобучения
        self.training_buffer.append({
            'features': pred['features_used'],
            'target': pred['actual_outcome']['actual_score']
        })

        # Если накоплено достаточно данных → переобучить модель
        if len(self.training_buffer) >= self.retrain_threshold:
            self._retrain_model()

    def _retrain_model(self):
        """
        Шаг 5: Переобучение модели

        Процесс:
        1. Взять новые данные из training_buffer
        2. Объединить со старыми данными (если нужно)
        3. Переобучить модель
        4. Валидация на hold-out set
        5. Если качество улучшилось → deploy новую версию
        """
        logger.info("🔄 Начало переобучения модели...")

        # Подготовка данных
        X_new = [item['features'] for item in self.training_buffer]
        y_new = [item['target'] for item in self.training_buffer]

        # Переобучение (simplified - в реале использовать MLflow)
        new_model = self.model.fit(X_new, y_new)

        # Валидация
        validation_score = self._validate_model(new_model)

        if validation_score > self.current_model_score:
            # Деплой новой модели
            self.model = new_model
            self.current_model_score = validation_score
            self.model_version += 1

            logger.info(f"✅ Модель обновлена до v{self.model_version}, score: {validation_score}")

            # Очистить буфер
            self.training_buffer = []
        else:
            logger.warning(f"⚠️ Новая модель хуже (score: {validation_score}), откат")

    def analyze_learning_effectiveness(self):
        """
        Анализ эффективности самообучения

        Метрики:
        - Снижение ошибки предсказания со временем
        - Скорость адаптации к новым сценариям
        - Стабильность модели
        """
        predictions = list(self.predictions_store.values())

        # Ошибка по времени
        errors_over_time = []
        for pred in sorted(predictions, key=lambda p: p['timestamp']):
            if 'actual_outcome' in pred:
                error = abs(pred['predicted_score'] - pred['actual_outcome']['actual_score'])
                errors_over_time.append({
                    'timestamp': pred['timestamp'],
                    'error': error,
                    'model_version': pred['model_version']
                })

        # Расчет улучшения
        if len(errors_over_time) > 10:
            early_errors = [e['error'] for e in errors_over_time[:10]]
            recent_errors = [e['error'] for e in errors_over_time[-10:]]

            improvement = (statistics.mean(early_errors) - statistics.mean(recent_errors)) / statistics.mean(early_errors) * 100

            return {
                'improvement_percentage': round(improvement, 2),
                'early_avg_error': round(statistics.mean(early_errors), 2),
                'recent_avg_error': round(statistics.mean(recent_errors), 2),
                'learning_status': 'improving' if improvement > 0 else 'degrading'
            }

        return {'status': 'insufficient_data'}
```

---

## 3. ❌ Обучение Системы Обучать (Meta-Learning)

### Проблема
**Сейчас:** Система использует фиксированные методы обучения, **НЕ адаптируется к эффективности**.

### Решение: Meta-Learning Engine

```python
# НОВЫЙ КОМПОНЕНТ: engines/meta_learning_engine.py

class MetaLearningEngine:
    """
    Мета-обучение: система учится обучать

    Концепция:
    - Система анализирует эффективность своих рекомендаций
    - Адаптирует методы под разных пользователей
    - Обучает AI коллег (экспертов, специалистов)
    """

    def analyze_teaching_effectiveness(self, user_id, learning_path_id):
        """
        Анализ: насколько эффективно система учит конкретного пользователя

        Метрики:
        - Improvement rate (как быстро улучшается)
        - Retention rate (как долго помнит)
        - Engagement rate (как активно учится)
        - Success rate (достигает ли целей)
        """
        path_progress = self._get_learning_path_progress(user_id, learning_path_id)

        effectiveness = {
            'user_id': user_id,
            'learning_path_id': learning_path_id,

            # Скорость улучшения
            'improvement_rate': self._calculate_improvement_rate(path_progress),

            # Retention (тест через 30 дней)
            'retention_score': self._test_retention(user_id, learning_path_id),

            # Engagement
            'engagement_score': path_progress['completion_percentage'],

            # Успех
            'goal_achieved': path_progress['score_after'] >= path_progress['target_score']
        }

        # Общая эффективность
        effectiveness['overall_effectiveness'] = (
            effectiveness['improvement_rate'] * 0.3 +
            effectiveness['retention_score'] * 0.3 +
            effectiveness['engagement_score'] * 0.2 +
            (100 if effectiveness['goal_achieved'] else 0) * 0.2
        )

        return effectiveness

    def adapt_teaching_method(self, user_id, learning_style):
        """
        Адаптация метода обучения под пользователя

        Стили обучения:
        - Visual (предпочитает видео, диаграммы)
        - Reading (предпочитает статьи, документы)
        - Kinesthetic (предпочитает практику, упражнения)
        - Auditory (предпочитает аудио, лекции)
        """
        # Анализ истории обучения пользователя
        user_history = self._get_user_learning_history(user_id)

        # Определение эффективных форматов
        effective_formats = self._analyze_effective_formats(user_history)

        # Адаптация будущих путей
        adapted_strategy = {
            'user_id': user_id,
            'detected_learning_style': learning_style,
            'preferred_formats': effective_formats,
            'resource_allocation': {
                'visual': 0.4 if learning_style == 'visual' else 0.2,
                'reading': 0.4 if learning_style == 'reading' else 0.2,
                'practice': 0.4 if learning_style == 'kinesthetic' else 0.3,
                'audio': 0.4 if learning_style == 'auditory' else 0.1
            },
            'pace': self._determine_optimal_pace(user_history),
            'difficulty_progression': self._determine_progression(user_history)
        }

        return adapted_strategy

    def train_ai_colleagues(self, ai_expert_id, learning_domain):
        """
        Обучение AI коллег (AI Experts, Specialists)

        Процесс:
        1. Learning System обучает AI Experts эффективным методам
        2. Передает знания о паттернах обучения
        3. Синхронизирует лучшие практики
        """
        # Извлечение знаний из Learning System
        teaching_knowledge = {
            'effective_learning_paths': self._get_best_learning_paths(learning_domain),
            'successful_teaching_patterns': self._extract_teaching_patterns(),
            'common_learning_obstacles': self._identify_common_obstacles(),
            'proven_interventions': self._get_proven_interventions()
        }

        # Передача знаний AI коллеге
        self.ai_expert_connector.teach(
            expert_id=ai_expert_id,
            domain=learning_domain,
            knowledge=teaching_knowledge
        )

        # Feedback loop: AI Expert передает обратно инсайты
        expert_insights = self.ai_expert_connector.get_insights(ai_expert_id)

        # Интеграция инсайтов от AI Expert
        self._integrate_expert_insights(expert_insights)

        return {
            'ai_expert_id': ai_expert_id,
            'knowledge_transferred': len(teaching_knowledge),
            'insights_received': len(expert_insights),
            'status': 'knowledge_exchange_complete'
        }
```

---

## 4. ❌ Интеграция с Библиотекой Знаний

### Проблема
**Сейчас:** Только маппинг gap→knowledge, **НЕТ реальной интеграции с Knowledge Base**.

### Решение: Knowledge Base Integrator

```python
# НОВЫЙ КОМПОНЕНТ: engines/knowledge_base_integrator.py

class KnowledgeBaseIntegrator:
    """
    Полная интеграция с Библиотекой Знаний

    Функции:
    1. Реальное подключение к Knowledge Base
    2. Автоматическое пополнение знаний
    3. Синхронизация с актуальной информацией
    4. Создание новых статей на основе паттернов
    """

    def __init__(self, knowledge_base_client):
        self.kb_client = knowledge_base_client  # Подключение к Knowledge Base Service
        self.auto_update_enabled = True

    def fetch_resources_for_gap(self, gap_keyword):
        """
        Реальный поиск ресурсов в Knowledge Base

        Вместо hardcoded ресурсов → реальный поиск
        """
        # Поиск в Knowledge Base
        search_results = self.kb_client.search(
            query=gap_keyword,
            filters={
                'type': ['article', 'video', 'template', 'guide'],
                'domain': 'BCM',
                'language': 'ru'
            },
            limit=10
        )

        # Ранжирование по релевантности
        ranked_resources = self._rank_by_relevance(search_results, gap_keyword)

        return ranked_resources

    def auto_create_knowledge_from_patterns(self, pattern):
        """
        Автоматическое создание статей на основе паттернов

        Пример:
        Pattern: "Recurring failure: Slow escalation"
        → Создать статью: "How to Improve Escalation Process"
        """
        if pattern.type == 'failure' and pattern.occurrences >= 5:
            # Проверить, существует ли уже статья
            existing = self.kb_client.search(
                query=f"improve {pattern.issue}",
                limit=1
            )

            if not existing:
                # Создать новую статью
                article = {
                    'title': f"Улучшение: {pattern.issue}",
                    'content': self._generate_article_content(pattern),
                    'type': 'article',
                    'domain': 'BCM',
                    'tags': ['auto-generated', 'pattern-based', pattern.scenario_type],
                    'based_on_pattern_id': pattern.id,
                    'sources': self._collect_pattern_sources(pattern)
                }

                article_id = self.kb_client.create_article(article)

                logger.info(f"✅ Auto-created article: {article['title']} (ID: {article_id})")

                return article_id

    def _generate_article_content(self, pattern):
        """
        Генерация контента статьи на основе паттерна

        Использует:
        - AI Expert (для генерации рекомендаций)
        - Historical data (для примеров)
        - Best practices (из успешных случаев)
        """
        content = f"""
# {pattern.issue}

## Проблема
Данная проблема была выявлена в {pattern.occurrences} упражнениях за последние {pattern.timespan}.

## Анализ
{self._analyze_pattern_root_cause(pattern)}

## Рекомендации
{self._generate_recommendations(pattern)}

## Примеры успешных решений
{self._find_successful_examples(pattern)}

## Связанные ресурсы
{self._find_related_resources(pattern)}

---
*Статья автоматически создана Learning System на основе выявленного паттерна*
*Pattern ID: {pattern.id}*
*Дата создания: {datetime.now()}*
        """

        return content

    def sync_with_external_sources(self):
        """
        Синхронизация с внешними источниками знаний

        Источники:
        - ISO standards updates
        - Industry news (BCM trends)
        - Threat intelligence feeds
        - Best practices databases
        """
        updates = []

        # 1. ISO стандарты
        iso_updates = self._fetch_iso_updates()
        for update in iso_updates:
            self.kb_client.update_or_create_article({
                'title': f"ISO Update: {update['clause']}",
                'content': update['content'],
                'type': 'standard_update',
                'source': 'ISO',
                'last_updated': update['date']
            })
            updates.append(update)

        # 2. Новые угрозы
        threat_updates = self._fetch_threat_intelligence()
        for threat in threat_updates:
            self.kb_client.update_or_create_article({
                'title': f"New Threat: {threat['name']}",
                'content': threat['description'],
                'type': 'threat_intelligence',
                'source': threat['source'],
                'severity': threat['severity']
            })
            updates.append(threat)

        # 3. Industry best practices
        best_practices = self._fetch_industry_best_practices()
        for practice in best_practices:
            self.kb_client.update_or_create_article({
                'title': practice['title'],
                'content': practice['content'],
                'type': 'best_practice',
                'source': practice['source'],
                'industry': practice['industry']
            })
            updates.append(practice)

        logger.info(f"✅ Synced {len(updates)} knowledge updates")

        return updates

    def create_learning_path_from_knowledge(self, user_competency_gap):
        """
        Создание learning path на основе актуальной Knowledge Base

        Процесс:
        1. Определить пробел компетенции
        2. Найти релевантные ресурсы в KB
        3. Упорядочить по сложности (beginner → advanced)
        4. Добавить практические упражнения
        5. Вернуть готовый путь
        """
        # Поиск ресурсов
        resources = self.kb_client.search(
            query=user_competency_gap['competency'],
            filters={
                'difficulty_level': self._map_score_to_level(user_competency_gap['current_score'])
            }
        )

        # Упорядочивание
        ordered_resources = self._order_by_progression(resources)

        # Создание пути
        learning_path = {
            'name': f"Improve {user_competency_gap['competency']}",
            'target_competency': user_competency_gap['competency'],
            'current_score': user_competency_gap['current_score'],
            'target_score': user_competency_gap['target_score'],
            'steps': []
        }

        for idx, resource in enumerate(ordered_resources, 1):
            learning_path['steps'].append({
                'order': idx,
                'type': resource['type'],
                'resource_id': resource['id'],
                'title': resource['title'],
                'duration_minutes': resource.get('duration', 30),
                'url': resource['url']
            })

        # Добавить практику в конце
        learning_path['steps'].append({
            'order': len(ordered_resources) + 1,
            'type': 'practice',
            'title': f"Практическое упражнение: {user_competency_gap['competency']}",
            'duration_minutes': 60
        })

        return learning_path
```

---

## 🔄 Полный Цикл Обучения (Интеграция всех компонентов)

```
┌─────────────────────────────────────────────────────────────────┐
│                    ПОЛНЫЙ ЦИКЛ ОБУЧЕНИЯ                         │
└─────────────────────────────────────────────────────────────────┘

1️⃣ СБОР ПОТРЕБНОСТЕЙ
   ↓
   [LearningNeedsCollector]
   - Упражнения → пробелы → потребности
   - Компетенции → низкие скоры → потребности
   - ISO требования → compliance needs
   - User requests → явные потребности
   ↓
   [Приоритизация потребностей]
   ↓

2️⃣ СОЗДАНИЕ УЧЕБНОГО ПЛАНА
   ↓
   [KnowledgeBaseIntegrator]
   - Поиск ресурсов в Knowledge Base (РЕАЛЬНЫЙ)
   - Создание learning paths из актуальных данных
   - Автоматическое пополнение знаний
   ↓
   [MetaLearningEngine]
   - Адаптация под стиль обучения пользователя
   - Оптимизация темпа и сложности
   ↓

3️⃣ ВЫПОЛНЕНИЕ ОБУЧЕНИЯ
   ↓
   [User проходит learning path]
   - Читает статьи
   - Смотрит видео
   - Выполняет практики
   ↓

4️⃣ ОЦЕНКА РЕЗУЛЬТАТОВ
   ↓
   [Упражнение/тест после обучения]
   - Новый competency score
   - Сравнение с predicted score
   ↓

5️⃣ САМООБУЧЕНИЕ СИСТЕМЫ
   ↓
   [SelfLearningEngine]
   - Prediction vs Actual
   - Анализ ошибки
   - Переобучение ML модели
   ↓
   [MetaLearningEngine]
   - Анализ эффективности обучения
   - Адаптация методов
   - Обучение AI коллег
   ↓

6️⃣ ОБНОВЛЕНИЕ ЗНАНИЙ
   ↓
   [KnowledgeBaseIntegrator]
   - Создание новых статей из паттернов
   - Синхронизация с внешними источниками
   - Обновление существующих ресурсов
   ↓

7️⃣ CONTINUOUS IMPROVEMENT
   ↓
   Цикл повторяется с улучшенной системой
```

---

## 📋 Чек-лист: Что нужно реализовать

### Phase 2: Core Learning Processes

- [ ] **LearningNeedsCollector**
  - [ ] `collect_needs_from_exercises()`
  - [ ] `collect_needs_from_competencies()`
  - [ ] `collect_needs_from_regulations()`
  - [ ] `collect_needs_from_user_requests()`
  - [ ] `prioritize_needs()`
  - [ ] `generate_training_plan()`

- [ ] **SelfLearningEngine**
  - [ ] `record_prediction()`
  - [ ] `record_actual_outcome()`
  - [ ] `_trigger_model_update()`
  - [ ] `_retrain_model()`
  - [ ] `analyze_learning_effectiveness()`
  - [ ] Интеграция с MLflow для версионирования моделей

- [ ] **MetaLearningEngine**
  - [ ] `analyze_teaching_effectiveness()`
  - [ ] `adapt_teaching_method()`
  - [ ] `train_ai_colleagues()`
  - [ ] Определение стилей обучения

- [ ] **KnowledgeBaseIntegrator**
  - [ ] Реальное подключение к Knowledge Base Service
  - [ ] `fetch_resources_for_gap()` - реальный поиск
  - [ ] `auto_create_knowledge_from_patterns()`
  - [ ] `sync_with_external_sources()`
  - [ ] `create_learning_path_from_knowledge()`

### Phase 3: Integration

- [ ] **API Endpoints**
  - [ ] `/api/learning/needs/collect` - Сбор потребностей
  - [ ] `/api/learning/needs/prioritize` - Приоритизация
  - [ ] `/api/learning/plans/generate` - Генерация планов
  - [ ] `/api/learning/self-learn/record-prediction` - Запись предсказания
  - [ ] `/api/learning/self-learn/record-outcome` - Запись результата
  - [ ] `/api/learning/self-learn/retrain` - Триггер переобучения
  - [ ] `/api/learning/meta/analyze-effectiveness` - Анализ эффективности
  - [ ] `/api/learning/meta/adapt-method` - Адаптация метода
  - [ ] `/api/learning/kb/sync` - Синхронизация с KB
  - [ ] `/api/learning/kb/auto-create` - Авто-создание статей

- [ ] **Database Tables**
  - [ ] `learning.learning_needs` - Потребности в обучении
  - [ ] `learning.training_plans` - Учебные планы
  - [ ] `learning.predictions_log` - Лог предсказаний
  - [ ] `learning.model_versions` - Версии ML моделей
  - [ ] `learning.teaching_effectiveness` - Эффективность обучения
  - [ ] `learning.user_learning_styles` - Стили обучения
  - [ ] `learning.knowledge_sync_log` - Лог синхронизации KB

- [ ] **Integrations**
  - [ ] Knowledge Base Service (поиск, создание, обновление)
  - [ ] AI Experts (передача знаний)
  - [ ] ISO Standards API (обновления стандартов)
  - [ ] Threat Intelligence Feeds
  - [ ] MLflow (версионирование моделей)

---

## 🎯 Приоритет Реализации

### 🔴 Критичные (MUST HAVE)
1. **KnowledgeBaseIntegrator** - реальная интеграция с KB
2. **LearningNeedsCollector** - сбор потребностей из существующих данных
3. **SelfLearningEngine** - базовый feedback loop

### 🟡 Важные (SHOULD HAVE)
4. **MetaLearningEngine** - адаптация методов обучения
5. Auto-creation статей из паттернов
6. Синхронизация с внешними источниками

### 🟢 Желательные (NICE TO HAVE)
7. Обучение AI коллег
8. Расширенная мета-аналитика
9. A/B тестирование методов обучения

---

## 💡 Ключевые Инсайты

### Что сейчас работает:
✅ Детекция паттернов
✅ Анализ компетенций
✅ Геймификация
✅ ML предсказания (статичные)
✅ Маппинг gap→knowledge (mock)

### Что критически НЕ хватает:
❌ Автоматический сбор потребностей
❌ Самообучение ML моделей
❌ Реальная интеграция с Knowledge Base
❌ Автоматическое пополнение знаний
❌ Мета-обучение (адаптация методов)

### Как это исправить:
1. Реализовать 4 новых компонента (выше)
2. Подключить реальную Knowledge Base
3. Настроить feedback loops
4. Интегрировать с внешними источниками

---

*Дизайн: 2025-10-05*
*Статус: Требует реализации (Phase 2)*
