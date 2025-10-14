# community-service - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 100
**Ресурсов:** 29
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [ai-generate](#ai-generate)
- [articles](#articles)
- [badges](#badges)
- [bookmarks](#bookmarks)
- [categories](#categories)
- [endpoint](#endpoint)
- [engines](#engines)
- [featured](#featured)
- [health](#health)
- [leaderboard](#leaderboard)
- [library](#library)
- [me](#me)
- [moderation](#moderation)
- [my](#my)
- [posts](#posts)
- [reputation](#reputation)
- [search](#search)
- [simulations](#simulations)
- [specialists](#specialists)
- [stats](#stats)
- [topics](#topics)
- [users](#users)
- [{org_id}](#{org_id})
- [{project_id}](#{project_id})
- [{proposal_id}](#{proposal_id})
- [{review_id}](#{review_id})
- [{scenario_id}](#{scenario_id})
- [{specialist_id}](#{specialist_id})

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

## ai-generate

### `POST` /ai-generate

**Файл:** `knowledge.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/ai-generate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## articles

### `GET` /articles

**Файл:** `knowledge.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/articles" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /articles

**Файл:** `knowledge.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/articles" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /articles/{article_id}

**Файл:** `knowledge.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/articles/{article_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /articles/{article_id}

**Файл:** `knowledge.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/articles/{article_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /articles/{article_id}/bookmark

**Файл:** `knowledge.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/articles/{article_id}/bookmark" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /articles/{article_id}/bookmark

**Файл:** `knowledge.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/articles/{article_id}/bookmark" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /articles/{article_id}/discuss

**Файл:** `knowledge.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/articles/{article_id}/discuss" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /articles/{article_id}/discussion

**Файл:** `knowledge.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/articles/{article_id}/discussion" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /articles/{article_id}/verify

**Файл:** `knowledge.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/articles/{article_id}/verify" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /articles/{article_id}/vote

**Файл:** `knowledge.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/articles/{article_id}/vote" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /articles/{article_id}/vote

**Файл:** `knowledge.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/articles/{article_id}/vote" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## badges

### `GET` /badges

**Файл:** `forum.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/badges" \
  -H "Authorization: Bearer <token>"
```

---

## bookmarks

### `GET` /bookmarks

**Файл:** `knowledge.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/bookmarks" \
  -H "Authorization: Bearer <token>"
```

---

## categories

### `GET` /categories

**Файл:** `forum.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/categories" \
  -H "Authorization: Bearer <token>"
```

---

## endpoint

### `GET` /endpoint

**Файл:** `connection.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/endpoint" \
  -H "Authorization: Bearer <token>"
```

---

## engines

### `GET` /engines

**Файл:** `simulation_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/engines" \
  -H "Authorization: Bearer <token>"
```

---

## featured

### `GET` /featured/popular

**Файл:** `scenarios.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/featured/popular" \
  -H "Authorization: Bearer <token>"
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

## leaderboard

### `GET` /leaderboard

**Файл:** `forum.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/leaderboard" \
  -H "Authorization: Bearer <token>"
```

---

## library

### `GET` /library

**Файл:** `scenario_library_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/library" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /library/complexity-levels

**Файл:** `scenario_library_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/library/complexity-levels" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /library/stats

**Файл:** `scenario_library_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/library/stats" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /library/threat-types

**Файл:** `scenario_library_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/library/threat-types" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /library/{scenario_id}

**Файл:** `scenario_library_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/library/{scenario_id}" \
  -H "Authorization: Bearer <token>"
```

---

## me

### `GET` /me

**Файл:** `organizations.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/me" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /me

**Файл:** `specialists.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/me" \
  -H "Authorization: Bearer <token>"
```

---

## moderation

### `POST` /moderation/flags/{flag_id}/resolve

**Файл:** `forum.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/moderation/flags/{flag_id}/resolve" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /moderation/queue

**Файл:** `forum.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/moderation/queue" \
  -H "Authorization: Bearer <token>"
```

---

## my

### `GET` /my

**Файл:** `projects.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/my" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /my/written

**Файл:** `reviews.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/my/written" \
  -H "Authorization: Bearer <token>"
```

---

## posts

### `PATCH` /posts/{post_id}

**Файл:** `forum.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/posts/{post_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /posts/{post_id}/flag

**Файл:** `forum.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/posts/{post_id}/flag" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /posts/{post_id}/mark-solution

**Файл:** `forum.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/posts/{post_id}/mark-solution" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /posts/{post_id}/vote

**Файл:** `forum.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/posts/{post_id}/vote" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## reputation

### `GET` /reputation/{user_id}

**Файл:** `forum.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/reputation/{user_id}" \
  -H "Authorization: Bearer <token>"
```

---

## search

### `GET` /search

**Файл:** `knowledge.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/search" \
  -H "Authorization: Bearer <token>"
```

---

## simulations

### `GET` /simulations

**Файл:** `simulation_router.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/simulations" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /simulations

**Файл:** `simulation_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/simulations" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /simulations/{sim_id}

**Файл:** `simulation_router.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/simulations/{sim_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /simulations/{sim_id}

**Файл:** `simulation_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/simulations/{sim_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /simulations/{sim_id}/results

**Файл:** `execution_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/simulations/{sim_id}/results" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /simulations/{sim_id}/run

**Файл:** `execution_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/simulations/{sim_id}/run" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /simulations/{sim_id}/status

**Файл:** `execution_router.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/simulations/{sim_id}/status" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /simulations/{sim_id}/stop

**Файл:** `execution_router.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/simulations/{sim_id}/stop" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## specialists

### `GET` /specialists/{specialist_id}/reviews

**Файл:** `reviews.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/specialists/{specialist_id}/reviews" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /specialists/{specialist_id}/stats

**Файл:** `reviews.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/specialists/{specialist_id}/stats" \
  -H "Authorization: Bearer <token>"
```

---

## stats

### `GET` /stats

**Файл:** `forum.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/stats" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /stats/my

**Файл:** `proposals.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/stats/my" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /stats/overview

**Файл:** `projects.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/stats/overview" \
  -H "Authorization: Bearer <token>"
```

---

## topics

### `GET` /topics

**Файл:** `forum.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/topics" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /topics

**Файл:** `forum.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/topics" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /topics/{topic_id}

**Файл:** `forum.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/topics/{topic_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /topics/{topic_id}

**Файл:** `forum.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/topics/{topic_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /topics/{topic_id}/flag

**Файл:** `forum.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/topics/{topic_id}/flag" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /topics/{topic_id}/posts

**Файл:** `forum.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/topics/{topic_id}/posts" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /topics/{topic_id}/posts

**Файл:** `forum.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/topics/{topic_id}/posts" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /topics/{topic_id}/vote

**Файл:** `forum.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/topics/{topic_id}/vote" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## users

### `GET` /users/{user_id}/badges

**Файл:** `forum.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/users/{user_id}/badges" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /users/{user_id}/profile

**Файл:** `forum.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/users/{user_id}/profile" \
  -H "Authorization: Bearer <token>"
```

---

## {org_id}

### `GET` /{org_id}

**Файл:** `organizations.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{org_id}" \
  -H "Authorization: Bearer <token>"
```

---

## {project_id}

### `DELETE` /{project_id}

**Файл:** `projects.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/{project_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{project_id}

**Файл:** `projects.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{project_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PUT` /{project_id}

**Файл:** `projects.py`

**Описание:**  
Обновить ресурс

**Пример запроса:**

```bash
curl -X PUT \
  "http://localhost:8000/{project_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{project_id}/cancel

**Файл:** `projects.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{project_id}/cancel" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{project_id}/complete

**Файл:** `projects.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{project_id}/complete" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /{project_id}/matching-specialists

**Файл:** `projects.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{project_id}/matching-specialists" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{project_id}/proposals

**Файл:** `projects.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{project_id}/proposals" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{project_id}/publish

**Файл:** `projects.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{project_id}/publish" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /{project_id}/scenarios

**Файл:** `projects.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{project_id}/scenarios" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{project_id}/set-competency-requirements

**Файл:** `projects.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{project_id}/set-competency-requirements" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## {proposal_id}

### `DELETE` /{proposal_id}

**Файл:** `proposals.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/{proposal_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{proposal_id}

**Файл:** `proposals.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{proposal_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PUT` /{proposal_id}

**Файл:** `proposals.py`

**Описание:**  
Обновить ресурс

**Пример запроса:**

```bash
curl -X PUT \
  "http://localhost:8000/{proposal_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{proposal_id}/accept

**Файл:** `proposals.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{proposal_id}/accept" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{proposal_id}/reject

**Файл:** `proposals.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{proposal_id}/reject" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{proposal_id}/withdraw

**Файл:** `proposals.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{proposal_id}/withdraw" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## {review_id}

### `GET` /{review_id}

**Файл:** `reviews.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{review_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{review_id}/hide

**Файл:** `reviews.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{review_id}/hide" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{review_id}/respond

**Файл:** `reviews.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{review_id}/respond" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{review_id}/verify

**Файл:** `reviews.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{review_id}/verify" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## {scenario_id}

### `GET` /{scenario_id}

**Файл:** `scenarios.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{scenario_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{scenario_id}/deploy

**Файл:** `scenarios.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{scenario_id}/deploy" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /{scenario_id}/reviews

**Файл:** `scenarios.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{scenario_id}/reviews" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{scenario_id}/reviews

**Файл:** `scenarios.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{scenario_id}/reviews" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## {specialist_id}

### `DELETE` /{specialist_id}

**Файл:** `specialists.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/{specialist_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{specialist_id}

**Файл:** `specialists.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{specialist_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PUT` /{specialist_id}

**Файл:** `specialists.py`

**Описание:**  
Обновить ресурс

**Пример запроса:**

```bash
curl -X PUT \
  "http://localhost:8000/{specialist_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{specialist_id}/certifications

**Файл:** `specialists.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{specialist_id}/certifications" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /{specialist_id}/certifications/{cert_id}

**Файл:** `specialists.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/{specialist_id}/certifications/{cert_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{specialist_id}/community-reputation

**Файл:** `specialists.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{specialist_id}/community-reputation" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{specialist_id}/knowledge-articles

**Файл:** `specialists.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{specialist_id}/knowledge-articles" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{specialist_id}/portfolio

**Файл:** `specialists.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{specialist_id}/portfolio" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /{specialist_id}/portfolio/{portfolio_id}

**Файл:** `specialists.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/{specialist_id}/portfolio/{portfolio_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{specialist_id}/sync-competencies

**Файл:** `specialists.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{specialist_id}/sync-competencies" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{specialist_id}/verify

**Файл:** `specialists.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{specialist_id}/verify" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{specialist_id}/verify-via-governance

**Файл:** `specialists.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{specialist_id}/verify-via-governance" \
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
