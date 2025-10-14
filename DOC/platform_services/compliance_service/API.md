# compliance-service - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 97
**Ресурсов:** 36
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [analytics](#analytics)
- [api](#api)
- [audits](#audits)
- [batch-ai-scan](#batch-ai-scan)
- [bci](#bci)
- [benchmarks](#benchmarks)
- [best-practices](#best-practices)
- [case-studies](#case-studies)
- [corrective-actions](#corrective-actions)
- [evidence](#evidence)
- [guides](#guides)
- [health](#health)
- [improvements](#improvements)
- [iso22301](#iso22301)
- [items](#items)
- [mapping](#mapping)
- [nonconformities](#nonconformities)
- [overview](#overview)
- [programs](#programs)
- [rca](#rca)
- [registry](#registry)
- [requirements-matrix](#requirements-matrix)
- [research](#research)
- [roadmap](#roadmap)
- [search](#search)
- [severity](#severity)
- [standards](#standards)
- [templates](#templates)
- [who](#who)
- [{assessment_id}](#{assessment_id})
- [{audit_id}](#{audit_id})
- [{evidence_id}](#{evidence_id})
- [{gap_id}](#{gap_id})
- [{item_id}](#{item_id})
- [{review_id}](#{review_id})

---

## 

### `GET` /

**Файл:** `gaps.py`

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

**Файл:** `assessments.py`

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

**Файл:** `evidence.py`

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

**Файл:** `management_review.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/" \
  -H "Authorization: Bearer <token>"
```

---

## analytics

### `GET` /analytics

**Файл:** `dashboard.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics" \
  -H "Authorization: Bearer <token>"
```

---

## api

### `GET` /api/compliance/check

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/compliance/check" \
  -H "Authorization: Bearer <token>"
```

---

## audits

### `GET` /audits

**Файл:** `audit.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/audits" \
  -H "Authorization: Bearer <token>"
```

---

## batch-ai-scan

### `POST` /batch-ai-scan

**Файл:** `assessments.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/batch-ai-scan" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## bci

### `GET` /bci/practices

**Файл:** `knowledge_base.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/bci/practices" \
  -H "Authorization: Bearer <token>"
```

---

## benchmarks

### `GET` /benchmarks

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/benchmarks" \
  -H "Authorization: Bearer <token>"
```

---

## best-practices

### `GET` /best-practices

**Файл:** `library.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/best-practices" \
  -H "Authorization: Bearer <token>"
```

---

## case-studies

### `GET` /case-studies

**Файл:** `library.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/case-studies" \
  -H "Authorization: Bearer <token>"
```

---

## corrective-actions

### `POST` /corrective-actions/bulk

**Файл:** `bulk_operations.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/corrective-actions/bulk" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## evidence

### `POST` /evidence/bulk

**Файл:** `bulk_operations.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/evidence/bulk" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## guides

### `GET` /guides

**Файл:** `library.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/guides" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /guides/{guide_id}

**Файл:** `library.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/guides/{guide_id}" \
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

**Файл:** `health.py`

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

**Файл:** `modules.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /health/info

**Файл:** `health.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health/info" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /health/ready

**Файл:** `health.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health/ready" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /health/{service_name}

**Файл:** `modules.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health/{service_name}" \
  -H "Authorization: Bearer <token>"
```

---

## improvements

### `GET` /improvements

**Файл:** `improvements.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/improvements" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /improvements

**Файл:** `improvements.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/improvements" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /improvements/dashboard

**Файл:** `improvements.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/improvements/dashboard" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /improvements/roi-analysis

**Файл:** `improvements.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/improvements/roi-analysis" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /improvements/{initiative_id}

**Файл:** `improvements.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/improvements/{initiative_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /improvements/{initiative_id}

**Файл:** `improvements.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/improvements/{initiative_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `PATCH` /improvements/{initiative_id}/progress

**Файл:** `improvements.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/improvements/{initiative_id}/progress" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /improvements/{initiative_id}/verify

**Файл:** `improvements.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/improvements/{initiative_id}/verify" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## iso22301

### `GET` /iso22301/clauses

**Файл:** `knowledge_base.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/iso22301/clauses" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /iso22301/{clause}

**Файл:** `knowledge_base.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/iso22301/{clause}" \
  -H "Authorization: Bearer <token>"
```

---

## items

### `GET` /items

**Файл:** `connection.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/items" \
  -H "Authorization: Bearer <token>"
```

---

## mapping

### `GET` /mapping

**Файл:** `knowledge_base.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/mapping" \
  -H "Authorization: Bearer <token>"
```

---

## nonconformities

### `POST` /nonconformities/bulk

**Файл:** `bulk_operations.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/nonconformities/bulk" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /nonconformities/{nc_id}/rca/complete

**Файл:** `nonconformities.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/nonconformities/{nc_id}/rca/complete" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /nonconformities/{nc_id}/rca/start

**Файл:** `nonconformities.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/nonconformities/{nc_id}/rca/start" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## overview

### `GET` /overview

**Файл:** `dashboard.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/overview" \
  -H "Authorization: Bearer <token>"
```

---

## programs

### `GET` /programs

**Файл:** `audit.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/programs" \
  -H "Authorization: Bearer <token>"
```

---

## rca

### `POST` /rca/bulk-validate

**Файл:** `bulk_operations.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/rca/bulk-validate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /rca/methods

**Файл:** `nonconformities.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/rca/methods" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /rca/templates/{method}

**Файл:** `nonconformities.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/rca/templates/{method}" \
  -H "Authorization: Bearer <token>"
```

---

## registry

### `GET` /registry

**Файл:** `modules.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/registry" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /registry

**Файл:** `modules.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/registry" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## requirements-matrix

### `GET` /requirements-matrix

**Файл:** `dashboard.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/requirements-matrix" \
  -H "Authorization: Bearer <token>"
```

---

## research

### `GET` /research

**Файл:** `library.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/research" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /research/{source}

**Файл:** `library.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/research/{source}" \
  -H "Authorization: Bearer <token>"
```

---

## roadmap

### `GET` /roadmap

**Файл:** `dashboard.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/roadmap" \
  -H "Authorization: Bearer <token>"
```

---

## search

### `GET` /search

**Файл:** `knowledge_base.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/search" \
  -H "Authorization: Bearer <token>"
```

---

## severity

### `GET` /severity/{severity}

**Файл:** `gaps.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/severity/{severity}" \
  -H "Authorization: Bearer <token>"
```

---

## standards

### `GET` /standards

**Файл:** `knowledge_base.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/standards" \
  -H "Authorization: Bearer <token>"
```

---

## templates

### `GET` /templates

**Файл:** `templates.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/templates" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /templates

**Файл:** `templates.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/templates" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /templates/bpmn/{workflow_type}

**Файл:** `templates.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/templates/bpmn/{workflow_type}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /templates/category/{category}

**Файл:** `templates.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/templates/category/{category}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /templates/generate

**Файл:** `templates.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/templates/generate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /templates/iso-clause/{clause}

**Файл:** `templates.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/templates/iso-clause/{clause}" \
  -H "Authorization: Bearer <token>"
```

---

### `DELETE` /templates/{template_id}

**Файл:** `templates.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/templates/{template_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /templates/{template_id}

**Файл:** `templates.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/templates/{template_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PUT` /templates/{template_id}

**Файл:** `templates.py`

**Описание:**  
Обновить ресурс

**Пример запроса:**

```bash
curl -X PUT \
  "http://localhost:8000/templates/{template_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /templates/{template_id}/render

**Файл:** `templates.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/templates/{template_id}/render" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /templates/{template_id}/usage-stats

**Файл:** `templates.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/templates/{template_id}/usage-stats" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /templates/{template_id}/verify

**Файл:** `templates.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/templates/{template_id}/verify" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## who

### `GET` /who/framework

**Файл:** `knowledge_base.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/who/framework" \
  -H "Authorization: Bearer <token>"
```

---

## {assessment_id}

### `DELETE` /{assessment_id}

**Файл:** `assessments.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/{assessment_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{assessment_id}

**Файл:** `assessments.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{assessment_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{assessment_id}/results

**Файл:** `assessments.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{assessment_id}/results" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{assessment_id}/run

**Файл:** `assessments.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{assessment_id}/run" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## {audit_id}

### `GET` /{audit_id}/checklist

**Файл:** `audit.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{audit_id}/checklist" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{audit_id}/complete

**Файл:** `audit.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{audit_id}/complete" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /{audit_id}/findings

**Файл:** `audit.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{audit_id}/findings" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{audit_id}/findings

**Файл:** `audit.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{audit_id}/findings" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /{audit_id}/report

**Файл:** `audit.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{audit_id}/report" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{audit_id}/start

**Файл:** `audit.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{audit_id}/start" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## {evidence_id}

### `DELETE` /{evidence_id}

**Файл:** `evidence.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/{evidence_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{evidence_id}

**Файл:** `evidence.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{evidence_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /{evidence_id}

**Файл:** `evidence.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/{evidence_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /{evidence_id}/history

**Файл:** `evidence.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{evidence_id}/history" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{evidence_id}/transition

**Файл:** `evidence.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{evidence_id}/transition" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## {gap_id}

### `GET` /{gap_id}

**Файл:** `gaps.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{gap_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /{gap_id}

**Файл:** `gaps.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/{gap_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{gap_id}/effectiveness-review

**Файл:** `gaps.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{gap_id}/effectiveness-review" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /{gap_id}/effectiveness-reviews

**Файл:** `gaps.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{gap_id}/effectiveness-reviews" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{gap_id}/rca

**Файл:** `gaps.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{gap_id}/rca" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{gap_id}/rca

**Файл:** `gaps.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{gap_id}/rca" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{gap_id}/reopen

**Файл:** `gaps.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{gap_id}/reopen" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{gap_id}/resolve

**Файл:** `gaps.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{gap_id}/resolve" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{gap_id}/start-remediation

**Файл:** `gaps.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{gap_id}/start-remediation" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{gap_id}/update-progress

**Файл:** `gaps.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{gap_id}/update-progress" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{gap_id}/verify

**Файл:** `gaps.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{gap_id}/verify" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## {item_id}

### `GET` /{item_id}/ai-advice

**Файл:** `workflow_ai.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{item_id}/ai-advice" \
  -H "Authorization: Bearer <token>"
```

---

## {review_id}

### `GET` /{review_id}

**Файл:** `management_review.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{review_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{review_id}/complete

**Файл:** `management_review.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{review_id}/complete" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /{review_id}/decisions

**Файл:** `management_review.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{review_id}/decisions" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /{review_id}/inputs

**Файл:** `management_review.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{review_id}/inputs" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{review_id}/report

**Файл:** `management_review.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{review_id}/report" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{review_id}/start

**Файл:** `management_review.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{review_id}/start" \
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
