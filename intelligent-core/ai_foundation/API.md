# ai-foundation - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 109
**Ресурсов:** 51
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [...](#...)
- [achievements](#achievements)
- [analytics](#analytics)
- [api](#api)
- [badges](#badges)
- [cases](#cases)
- [competencies](#competencies)
- [coverage](#coverage)
- [dashboard](#dashboard)
- [decay](#decay)
- [detect](#detect)
- [difficulty](#difficulty)
- [effectiveness](#effectiveness)
- [gap-mappings](#gap-mappings)
- [gaps](#gaps)
- [health](#health)
- [iso-mapping](#iso-mapping)
- [kb](#kb)
- [leaderboard](#leaderboard)
- [learning-paths](#learning-paths)
- [levels](#levels)
- [matrix](#matrix)
- [ml](#ml)
- [needs](#needs)
- [next-exercise](#next-exercise)
- [optimal-challenge](#optimal-challenge)
- [points](#points)
- [predict](#predict)
- [priorities](#priorities)
- [processes](#processes)
- [profile](#profile)
- [rag](#rag)
- [recommend](#recommend)
- [resources](#resources)
- [results](#results)
- [roles](#roles)
- [scenario-complexity](#scenario-complexity)
- [scenarios](#scenarios)
- [self-learn](#self-learn)
- [simulate](#simulate)
- [standards](#standards)
- [stats](#stats)
- [status](#status)
- [streaks](#streaks)
- [teams](#teams)
- [training](#training)
- [unified](#unified)
- [users](#users)
- [workflow](#workflow)
- [{pattern_id}](#{pattern_id})

---

## 

### `GET` /

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /

**Файл:** `recommendation_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /

**Файл:** `pattern_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/" \
  -H "Authorization: Bearer <token>"
```

---

## ...

### `GET` /...

**Файл:** `database.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/..." \
  -H "Authorization: Bearer <token>"
```

---

## achievements

### `POST` /achievements/check

**Файл:** `gamification_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/achievements/check" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## analytics

### `GET` /analytics/benchmarks

**Файл:** `analytics_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics/benchmarks" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /analytics/comparative

**Файл:** `analytics_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics/comparative" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /analytics/drill-down

**Файл:** `analytics_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/analytics/drill-down" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /analytics/export

**Файл:** `analytics_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics/export" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /analytics/performance-matrix

**Файл:** `analytics_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics/performance-matrix" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /analytics/predictions

**Файл:** `analytics_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics/predictions" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /analytics/real-time

**Файл:** `analytics_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics/real-time" \
  -H "Authorization: Bearer <token>"
```

---

## api

### `GET` /api/cross-learning/virtuous-cycle/metrics

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/cross-learning/virtuous-cycle/metrics" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/cross-learning/virtuous-cycle/pattern

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/cross-learning/virtuous-cycle/pattern" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/cross-learning/virtuous-cycle/workflow

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/cross-learning/virtuous-cycle/workflow" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/search

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/search" \
  -H "Authorization: Bearer <token>"
```

---

## badges

### `POST` /badges/check

**Файл:** `gamification_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/badges/check" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /badges/definitions

**Файл:** `gamification_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/badges/definitions" \
  -H "Authorization: Bearer <token>"
```

---

## cases

### `GET` /cases

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/cases" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /cases/search

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/cases/search" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /cases/{case_id}

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/cases/{case_id}" \
  -H "Authorization: Bearer <token>"
```

---

## competencies

### `GET` /competencies/summary

**Файл:** `competency_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/competencies/summary" \
  -H "Authorization: Bearer <token>"
```

---

## coverage

### `POST` /coverage/analyze

**Файл:** `process_gap_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/coverage/analyze" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /coverage/save

**Файл:** `process_gap_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/coverage/save" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /coverage/summary

**Файл:** `process_gap_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/coverage/summary" \
  -H "Authorization: Bearer <token>"
```

---

## dashboard

### `GET` /dashboard/executive

**Файл:** `analytics_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/dashboard/executive" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /dashboard/learning-trends

**Файл:** `analytics_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/dashboard/learning-trends" \
  -H "Authorization: Bearer <token>"
```

---

## decay

### `POST` /decay/calculate

**Файл:** `competency_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/decay/calculate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## detect

### `POST` /detect

**Файл:** `pattern_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/detect" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /detect/anomalies

**Файл:** `ml_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/detect/anomalies" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## difficulty

### `POST` /difficulty/adjust

**Файл:** `ml_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/difficulty/adjust" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## effectiveness

### `POST` /effectiveness/record

**Файл:** `knowledge_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/effectiveness/record" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /effectiveness/report

**Файл:** `knowledge_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/effectiveness/report" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /effectiveness/{gap_keyword}/best-resources

**Файл:** `knowledge_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/effectiveness/{gap_keyword}/best-resources" \
  -H "Authorization: Bearer <token>"
```

---

## gap-mappings

### `GET` /gap-mappings

**Файл:** `knowledge_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/gap-mappings" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /gap-mappings/create

**Файл:** `knowledge_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/gap-mappings/create" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## gaps

### `GET` /gaps/critical

**Файл:** `process_gap_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/gaps/critical" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /gaps/map-to-knowledge

**Файл:** `knowledge_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/gaps/map-to-knowledge" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## health

### `GET` /health

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health" \
  -H "Authorization: Bearer <token>"
```

---

## iso-mapping

### `GET` /iso-mapping

**Файл:** `process_gap_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/iso-mapping" \
  -H "Authorization: Bearer <token>"
```

---

## kb

### `POST` /kb/auto-create-from-pattern

**Файл:** `platform_integration_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/kb/auto-create-from-pattern" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /kb/auto-create-from-patterns

**Файл:** `self_learning_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/kb/auto-create-from-patterns" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /kb/create-learning-path

**Файл:** `platform_integration_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/kb/create-learning-path" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /kb/create-learning-path

**Файл:** `self_learning_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/kb/create-learning-path" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /kb/search

**Файл:** `self_learning_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/kb/search" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /kb/sync-external

**Файл:** `platform_integration_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/kb/sync-external" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /kb/sync-external

**Файл:** `self_learning_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/kb/sync-external" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## leaderboard

### `GET` /leaderboard/global

**Файл:** `gamification_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/leaderboard/global" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /leaderboard/monthly

**Файл:** `gamification_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/leaderboard/monthly" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /leaderboard/scenario/{scenario_type}

**Файл:** `gamification_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/leaderboard/scenario/{scenario_type}" \
  -H "Authorization: Bearer <token>"
```

---

## learning-paths

### `POST` /learning-paths/generate

**Файл:** `knowledge_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/learning-paths/generate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /learning-paths/save

**Файл:** `knowledge_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/learning-paths/save" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /learning-paths/{path_id}/progress

**Файл:** `knowledge_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/learning-paths/{path_id}/progress" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /learning-paths/{user_id}

**Файл:** `knowledge_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/learning-paths/{user_id}" \
  -H "Authorization: Bearer <token>"
```

---

## levels

### `GET` /levels

**Файл:** `gamification_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/levels" \
  -H "Authorization: Bearer <token>"
```

---

## matrix

### `POST` /matrix/generate

**Файл:** `process_gap_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/matrix/generate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## ml

### `GET` /ml/feature-importance

**Файл:** `platform_integration_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/ml/feature-importance" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /ml/model-info

**Файл:** `ml_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/ml/model-info" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /ml/performance

**Файл:** `platform_integration_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/ml/performance" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /ml/predict-success

**Файл:** `platform_integration_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/ml/predict-success" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /ml/submit-feedback

**Файл:** `platform_integration_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/ml/submit-feedback" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## needs

### `POST` /needs/collect

**Файл:** `self_learning_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/needs/collect" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /needs/training-plan

**Файл:** `self_learning_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/needs/training-plan" \
  -H "Authorization: Bearer <token>"
```

---

## next-exercise

### `GET` /next-exercise

**Файл:** `recommendation_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/next-exercise" \
  -H "Authorization: Bearer <token>"
```

---

## optimal-challenge

### `GET` /optimal-challenge

**Файл:** `ml_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/optimal-challenge" \
  -H "Authorization: Bearer <token>"
```

---

## points

### `POST` /points/award

**Файл:** `gamification_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/points/award" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## predict

### `POST` /predict/success

**Файл:** `ml_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/predict/success" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## priorities

### `POST` /priorities/generate

**Файл:** `process_gap_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/priorities/generate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## processes

### `GET` /processes

**Файл:** `process_gap_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/processes" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /processes/{process_id}

**Файл:** `process_gap_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/processes/{process_id}" \
  -H "Authorization: Bearer <token>"
```

---

## profile

### `POST` /profile/calculate

**Файл:** `gamification_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/profile/calculate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /profile/{user_id}

**Файл:** `gamification_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/profile/{user_id}" \
  -H "Authorization: Bearer <token>"
```

---

## rag

### `POST` /rag/add-knowledge

**Файл:** `platform_integration_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/rag/add-knowledge" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /rag/search

**Файл:** `platform_integration_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/rag/search" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## recommend

### `POST` /recommend/learning-path

**Файл:** `ml_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/recommend/learning-path" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## resources

### `GET` /resources/recommend

**Файл:** `knowledge_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/resources/recommend" \
  -H "Authorization: Bearer <token>"
```

---

## results

### `GET` /results

**Файл:** `learning_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/results" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /results

**Файл:** `learning_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/results" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## roles

### `GET` /roles

**Файл:** `competency_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/roles" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /roles/gaps

**Файл:** `competency_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/roles/gaps" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /roles/{role_name}/requirements

**Файл:** `competency_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/roles/{role_name}/requirements" \
  -H "Authorization: Bearer <token>"
```

---

## scenario-complexity

### `GET` /scenario-complexity

**Файл:** `ml_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/scenario-complexity" \
  -H "Authorization: Bearer <token>"
```

---

## scenarios

### `GET` /scenarios

**Файл:** `learning_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/scenarios" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /scenarios/{scenario_type}

**Файл:** `learning_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/scenarios/{scenario_type}" \
  -H "Authorization: Bearer <token>"
```

---

## self-learn

### `GET` /self-learn/accuracy-report

**Файл:** `self_learning_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/self-learn/accuracy-report" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /self-learn/effectiveness

**Файл:** `self_learning_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/self-learn/effectiveness" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /self-learn/export-training-data

**Файл:** `self_learning_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/self-learn/export-training-data" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /self-learn/feature-importance

**Файл:** `self_learning_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/self-learn/feature-importance" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /self-learn/predictions

**Файл:** `self_learning_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/self-learn/predictions" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /self-learn/record-outcome

**Файл:** `self_learning_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/self-learn/record-outcome" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /self-learn/record-prediction

**Файл:** `self_learning_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/self-learn/record-prediction" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /self-learn/trigger-retrain

**Файл:** `self_learning_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/self-learn/trigger-retrain" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## simulate

### `POST` /simulate/performance

**Файл:** `ml_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/simulate/performance" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## standards

### `GET` /standards

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/standards" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /standards/{standard_id:path}

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/standards/{standard_id:path}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /standards/{standard_id:path}/metadata

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/standards/{standard_id:path}/metadata" \
  -H "Authorization: Bearer <token>"
```

---

## stats

### `GET` /stats

**Файл:** `learning_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/stats" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /stats/summary

**Файл:** `gamification_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/stats/summary" \
  -H "Authorization: Bearer <token>"
```

---

## status

### `GET` /status

**Файл:** `platform_integration_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/status" \
  -H "Authorization: Bearer <token>"
```

---

## streaks

### `GET` /streaks/{user_id}

**Файл:** `gamification_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/streaks/{user_id}" \
  -H "Authorization: Bearer <token>"
```

---

## teams

### `POST` /teams/analyze

**Файл:** `competency_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/teams/analyze" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## training

### `GET` /training

**Файл:** `recommendation_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/training" \
  -H "Authorization: Bearer <token>"
```

---

## unified

### `POST` /unified/predict-and-recommend

**Файл:** `platform_integration_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/unified/predict-and-recommend" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## users

### `GET` /users/{user_id}/competency

**Файл:** `competency_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/users/{user_id}/competency" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /users/{user_id}/competency

**Файл:** `competency_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/users/{user_id}/competency" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## workflow

### `POST` /workflow/full-cycle

**Файл:** `self_learning_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/workflow/full-cycle" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## {pattern_id}

### `DELETE` /{pattern_id}

**Файл:** `pattern_router.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/{pattern_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{pattern_id}

**Файл:** `pattern_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{pattern_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{pattern_id}/acknowledge

**Файл:** `pattern_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{pattern_id}/acknowledge" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---


## 🔗 Интеграция

### Authentication
```python
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}
```

### Base URL
```
http://localhost:8000  # Development
https://api.example.com  # Production
```

---

**Сгенерировано:** 2025-10-07 05:07
**Инструмент:** `tools/generators/documentation_generator.py`
