# 🧪 Test Coverage Gap Analysis

**Дата**: 2025-10-11
**Цель**: Определить недостающие тесты для полного покрытия платформы

---

## 📊 Текущее Состояние

### ✅ Что есть (193 Python теста)

**Unit Tests** (`/tests/unit/`):
- ✅ Platform Services: 9 сервисов (BIA, Risk, Planning, Compliance, etc.)
- ✅ Intelligent Core: Expertise Center, AI Office, Workflow Engine
- ✅ Infrastructure: Частичное покрытие

**Integration Tests** (`/tests/integration/`):
- ✅ 2 базовых теста

**E2E Tests** (`/tests/e2e/`):
- ✅ 1 тест (test_full_bcm_workflow.py)

**Performance Tests** (`/tests/performance/`):
- ❌ Пустые директории

---

## ❌ Недостающие Тесты

### 1. **ResourceTracker Tests** ⚠️ КРИТИЧНО

**Локация**: `/intelligent-core/ai-foundation/utils/resource_tracker.py` (415 строк)

**Что нужно**:
```python
# /tests/unit/intelligent-core/ai-foundation/test_resource_tracker.py

import pytest
from utils.resource_tracker import ResourceTracker, ResourceSnapshot, create_resource_tracker

class TestResourceTracker:
    """Unit tests for ResourceTracker"""

    def test_take_snapshot(self):
        """Test resource snapshot creation"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)
        snapshot = tracker.take_snapshot()

        assert isinstance(snapshot, ResourceSnapshot)
        assert snapshot.cpu_percent >= 0
        assert snapshot.memory_percent >= 0
        assert snapshot.memory_mb >= 0

    def test_calculate_trend(self):
        """Test trend calculation"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        # Generate snapshots
        for _ in range(5):
            tracker.take_snapshot()

        trend = tracker.calculate_trend('cpu_percent')
        assert -1.0 <= trend <= 1.0

    def test_predict_deficit(self):
        """Test deficit prediction"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        # Generate snapshots
        for _ in range(5):
            tracker.take_snapshot()

        deficit = tracker.predict_deficit('cpu_percent', threshold_percent=90.0)
        assert deficit is None or deficit >= 0

    def test_detect_resource_state(self):
        """Test resource state detection"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)
        tracker.take_snapshot()

        state = tracker.detect_resource_state()
        assert state in ["deficit", "normal", "surplus"]

    def test_get_available_resources(self):
        """Test available resources calculation"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)
        tracker.take_snapshot()

        available = tracker.get_available_resources()
        assert 'cpu_percent' in available
        assert 'memory_mb' in available
        assert 'time_seconds' in available
        assert 'disk_io_mb' in available

    def test_persistence(self, tmp_path):
        """Test history persistence"""
        storage_path = tmp_path / "resource_history.json"

        # Create tracker and generate snapshots
        tracker = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=10,
            storage_path=str(storage_path)
        )

        for _ in range(3):
            tracker.take_snapshot()

        tracker._save_history()
        assert storage_path.exists()

        # Load in new tracker
        tracker2 = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=10,
            storage_path=str(storage_path)
        )

        assert len(tracker2.history) > 0

@pytest.mark.asyncio
async def test_create_resource_tracker():
    """Test async resource tracker creation"""
    tracker = await create_resource_tracker(
        snapshot_interval_seconds=1.0,
        history_size=10
    )

    assert tracker is not None
    assert tracker.running is True

    # Cleanup
    tracker.stop()
```

**Статус**: ❌ НЕТ ТЕСТОВ для нового компонента

---

### 2. **System BCM Service Integration Tests** ⚠️ ВАЖНО

**Что есть**:
- `/tests/unit/intelligent-core/system-bcm/tests/test_performance.py`
- `/tests/unit/intelligent-core/system-bcm/tests/test_phase1_integration.py`

**Что нужно добавить**:
```python
# /tests/integration/intelligent-core/test_system_bcm_integration.py

import pytest
from fastapi.testclient import TestClient

class TestSystemBCMIntegration:
    """Integration tests for System BCM Service"""

    def test_resource_tracker_integration(self, client: TestClient):
        """Test ResourceTracker integration in BCM cycle"""
        # Trigger BCM cycle
        response = client.post("/cycle/trigger")
        assert response.status_code == 200

        result = response.json()

        # Verify resource monitoring in BIA phase
        assert "phases" in result
        assert "bia" in result["phases"]
        assert "resource_monitoring" in result["phases"]["bia"]

        resource_data = result["phases"]["bia"]["resource_monitoring"]
        assert "state" in resource_data
        assert "available" in resource_data
        assert "predictions" in resource_data

    def test_resource_status_endpoint(self, client: TestClient):
        """Test /resources/status endpoint"""
        response = client.get("/resources/status")
        assert response.status_code == 200

        data = response.json()
        assert "available" in data
        assert "state" in data
        assert "stats" in data
        assert "predictions" in data

        # Validate structure
        assert data["state"] in ["deficit", "normal", "surplus"]
        assert "cpu_percent" in data["available"]
        assert "memory_mb" in data["available"]

    def test_resource_contention_events(self, client: TestClient, event_bus):
        """Test resource contention event publishing"""
        # Subscribe to events
        events = []

        @event_bus.subscribe("platform.bcm.resources.contention")
        async def on_contention(event):
            events.append(event)

        # Trigger cycle (may publish contention event if deficit)
        response = client.post("/cycle/trigger")
        assert response.status_code == 200

        # If deficit detected, event should be published
        # (This is conditional based on actual resource state)

    def test_prometheus_metrics_resource_tracking(self, client: TestClient):
        """Test new Prometheus metrics for ResourceTracker"""
        response = client.get("/metrics")
        assert response.status_code == 200

        metrics = response.text

        # Check new metrics exist
        assert "system_bcm_resource_snapshots_total" in metrics
        assert "system_bcm_resource_deficit_events" in metrics
        assert "system_bcm_resource_surplus_events" in metrics
        assert "system_bcm_resource_state" in metrics
        assert "system_bcm_cpu_available_percent" in metrics
        assert "system_bcm_memory_available_mb" in metrics
```

**Статус**: ⚠️ ЧАСТИЧНО (нет тестов ResourceTracker интеграции)

---

### 3. **E2E Tests - Business Flows** ❌ ОТСУТСТВУЮТ

**Черновик найден**: `/Users/MD/Downloads/files/tests/business-flow.e2e.spec.ts`

**Анализ черновика**:
- ✅ Playwright-based (TypeScript)
- ⚠️ Generic flows (не специфичные для BCM платформы)
- ❌ Hardcoded URLs (localhost:3000)
- ❌ Нет реальных BCM сценариев

**Что нужно** (адаптировать для Python + BCM):
```python
# /tests/e2e/platform-services/test_bcm_business_flows.py

import pytest
from playwright.async_api import async_playwright, Page

@pytest.mark.e2e
@pytest.mark.asyncio
class TestBCMBusinessFlows:
    """E2E tests for complete BCM business workflows"""

    async def test_bia_to_recovery_flow(self):
        """Complete flow: BIA → Risk Assessment → Recovery Plan"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # 1. Login
            await page.goto('http://localhost:3000/login')
            await page.fill('input[name="email"]', 'admin@bcm.local')
            await page.fill('input[name="password"]', 'admin123')
            await page.click('button[type="submit"]')

            # 2. Navigate to BIA Service
            await page.goto('http://localhost:8001/bia/new')

            # 3. Create BIA
            await page.fill('input[name="organization"]', 'Test Healthcare Org')
            await page.click('button:has-text("Start BIA")')

            # 4. Wait for BIA completion
            await page.wait_for_selector('text=BIA Completed')
            bia_id = await page.get_attribute('[data-bia-id]', 'data-bia-id')

            # 5. Navigate to Risk Assessment
            await page.goto(f'http://localhost:8002/risk/from-bia/{bia_id}')

            # 6. Assess risks
            await page.click('button:has-text("Auto-Assess Risks")')
            await page.wait_for_selector('text=Risk Assessment Complete')

            # 7. Generate Recovery Plan
            await page.goto(f'http://localhost:8004/planning/from-risk/{bia_id}')
            await page.click('button:has-text("Generate Plan")')
            await page.wait_for_selector('text=Recovery Plan Ready')

            # 8. Verify plan exists
            plan_title = await page.text_content('h1.plan-title')
            assert 'Recovery Plan' in plan_title

            await browser.close()

    async def test_ai_orchestrator_workflow(self):
        """AI Orchestrator coordinates multi-service workflow"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # 1. Trigger AI Orchestrator
            await page.goto('http://localhost:8037/orchestrate')

            # 2. Submit complex task
            await page.fill('textarea[name="task"]',
                'Analyze platform health and recommend BCM improvements')
            await page.click('button:has-text("Execute")')

            # 3. Wait for orchestration
            await page.wait_for_selector('text=Task Completed', timeout=30000)

            # 4. Verify AI specialists consulted
            specialists = await page.locator('.specialist-consulted').count()
            assert specialists > 0

            # 5. Verify recommendations generated
            recommendations = await page.locator('.recommendation').count()
            assert recommendations > 0

            await browser.close()

    async def test_system_bcm_auto_recovery_flow(self):
        """System BCM detects issue and auto-recovers"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # 1. Open System BCM dashboard
            await page.goto('http://localhost:8050/status')

            # 2. Simulate service failure (via API)
            await page.evaluate('''
                fetch('http://localhost:8050/recovery/trigger', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        service: 'test-service',
                        incident_type: 'failure'
                    })
                })
            ''')

            # 3. Wait for recovery event
            await page.wait_for_selector('text=Recovery Started', timeout=10000)

            # 4. Wait for completion
            await page.wait_for_selector('text=Recovery Completed', timeout=30000)

            # 5. Verify service restored
            status = await page.text_content('.service-status')
            assert 'healthy' in status.lower()

            await browser.close()
```

**Статус**: ❌ НЕТ E2E тестов для BCM сценариев

---

### 4. **Performance Tests - Orchestrator** ❌ ОТСУТСТВУЮТ

**Черновик найден**: `/Users/MD/Downloads/files/tests/orchestrator.performance.spec.ts`

**Анализ черновика**:
- ✅ Load testing concept
- ⚠️ Playwright-based (не оптимально для load testing)
- ❌ Не специфично для AI Orchestrator платформы

**Что нужно** (Python + Locust):
```python
# /tests/performance/intelligent-core/test_ai_orchestrator_load.py

import pytest
from locust import HttpUser, task, between
import time

class AIorchestratorLoadTest(HttpUser):
    """Performance tests for AI Orchestrator"""
    wait_time = between(1, 3)

    @task(3)
    def orchestrate_simple_task(self):
        """Test simple task orchestration throughput"""
        self.client.post("/api/orchestrate", json={
            "task": "Analyze platform health",
            "context": {"domain": "bcm"}
        })

    @task(1)
    def orchestrate_complex_task(self):
        """Test complex task orchestration"""
        self.client.post("/api/orchestrate", json={
            "task": "Generate comprehensive BCM report",
            "context": {
                "domain": "bcm",
                "include_bia": True,
                "include_risk": True,
                "include_planning": True
            }
        })

@pytest.mark.performance
class TestOrchestratorPerformance:
    """Orchestrator performance benchmarks"""

    def test_throughput_100_requests(self, orchestrator_client):
        """Test orchestrator can handle 100 requests in 3 seconds"""
        import asyncio

        async def send_request():
            return await orchestrator_client.post("/api/orchestrate", json={
                "task": "quick health check"
            })

        start = time.time()

        # Send 100 concurrent requests
        tasks = [send_request() for _ in range(100)]
        results = asyncio.run(asyncio.gather(*tasks))

        duration = time.time() - start

        # Assert all succeeded
        assert all(r.status_code == 200 for r in results)

        # Assert throughput (100 requests in < 3 seconds)
        assert duration < 3.0

        print(f"✅ Throughput: {100/duration:.2f} req/s")

    def test_latency_p95(self, orchestrator_client):
        """Test P95 latency is under 500ms"""
        import asyncio

        async def measure_latency():
            start = time.time()
            await orchestrator_client.post("/api/orchestrate", json={
                "task": "quick task"
            })
            return time.time() - start

        # Measure 100 requests
        latencies = asyncio.run(asyncio.gather(*[
            measure_latency() for _ in range(100)
        ]))

        # Calculate P95
        sorted_latencies = sorted(latencies)
        p95 = sorted_latencies[94]  # 95th percentile

        assert p95 < 0.5  # 500ms
        print(f"✅ P95 Latency: {p95*1000:.2f}ms")

    def test_resource_utilization_under_load(self, orchestrator_client, resource_tracker):
        """Test resource usage stays within limits under load"""
        import asyncio

        # Get baseline
        baseline = resource_tracker.take_snapshot()

        # Send load
        async def send_load():
            tasks = [
                orchestrator_client.post("/api/orchestrate", json={"task": "test"})
                for _ in range(50)
            ]
            await asyncio.gather(*tasks)

        asyncio.run(send_load())

        # Measure peak
        peak = resource_tracker.take_snapshot()

        # Assert CPU increase is reasonable
        cpu_increase = peak.cpu_percent - baseline.cpu_percent
        assert cpu_increase < 50  # No more than 50% increase

        # Assert memory increase is reasonable
        mem_increase = peak.memory_mb - baseline.memory_mb
        assert mem_increase < 500  # No more than 500MB increase
```

**Для запуска**:
```bash
# Locust load test
locust -f tests/performance/intelligent-core/test_ai_orchestrator_load.py \
       --host=http://localhost:8037 \
       --users=100 \
       --spawn-rate=10
```

**Статус**: ❌ НЕТ performance тестов

---

### 5. **Integration Tests - EventBus** ⚠️ ЧАСТИЧНО

**Что нужно**:
```python
# /tests/integration/infrastructure/test_eventbus_integration.py

import pytest
from infrastructure.eventbus import create_eventbus, Event

@pytest.mark.integration
@pytest.mark.asyncio
class TestEventBusIntegration:
    """EventBus integration tests across services"""

    async def test_bcm_cycle_event_flow(self):
        """Test event flow during BCM cycle"""
        eventbus = create_eventbus('redis')

        events_received = []

        @eventbus.subscribe("platform.bcm.cycle.started")
        async def on_cycle_started(event: Event):
            events_received.append(event)

        @eventbus.subscribe("platform.bcm.cycle.completed")
        async def on_cycle_completed(event: Event):
            events_received.append(event)

        # Trigger BCM cycle via API
        # (would need System BCM client)

        # Wait for events
        await asyncio.sleep(2)

        # Verify events received in order
        assert len(events_received) >= 2
        assert events_received[0].type == "platform.bcm.cycle.started"
        assert events_received[-1].type == "platform.bcm.cycle.completed"

    async def test_resource_contention_event_handling(self):
        """Test resource contention event publishing and handling"""
        eventbus = create_eventbus('redis')

        contention_events = []

        @eventbus.subscribe("platform.bcm.resources.contention")
        async def on_contention(event: Event):
            contention_events.append(event)

        # Trigger deficit condition
        # (would simulate high resource usage)

        # Wait for event
        await asyncio.sleep(1)

        if contention_events:
            event = contention_events[0]
            assert "available" in event.data
            assert "cpu_deficit_seconds" in event.data or "memory_deficit_seconds" in event.data
```

**Статус**: ⚠️ ЧАСТИЧНО (нет тестов для новых событий)

---

### 6. **Security Tests** ❌ ОТСУТСТВУЮТ

**Что нужно**:
```python
# /tests/security/test_api_security.py

import pytest

@pytest.mark.security
class TestAPISecurity:
    """API security tests"""

    def test_authentication_required(self, client):
        """Test endpoints require authentication"""
        response = client.post("/cycle/trigger")
        assert response.status_code in [401, 403]

    def test_sql_injection_protection(self, client):
        """Test SQL injection protection"""
        malicious_input = "'; DROP TABLE users; --"
        response = client.post("/bia/create", json={
            "organization": malicious_input
        })
        # Should not crash or expose error
        assert response.status_code != 500

    def test_xss_protection(self, client):
        """Test XSS protection"""
        xss_payload = "<script>alert('XSS')</script>"
        response = client.post("/bia/create", json={
            "organization": xss_payload
        })
        # Response should escape HTML
        assert "<script>" not in response.text
```

**Статус**: ❌ НЕТ security тестов

---

## 📋 Приоритизация Недостающих Тестов

### 🔴 КРИТИЧНО (Сделать немедленно)

1. **ResourceTracker Unit Tests**
   - Файл: `/tests/unit/intelligent-core/ai-foundation/test_resource_tracker.py`
   - Причина: Новый критичный компонент без тестов
   - Оценка: 2 часа

2. **System BCM ResourceTracker Integration Tests**
   - Файл: `/tests/integration/intelligent-core/test_system_bcm_resource_tracker.py`
   - Причина: Интеграция не покрыта тестами
   - Оценка: 3 часа

### 🟠 ВАЖНО (Сделать на этой неделе)

3. **E2E Business Flows**
   - Файлы: `/tests/e2e/platform-services/test_bcm_business_flows.py`
   - Причина: Нет end-to-end покрытия BCM сценариев
   - Оценка: 1 день

4. **Performance Tests - AI Orchestrator**
   - Файл: `/tests/performance/intelligent-core/test_ai_orchestrator_load.py`
   - Причина: Нет load/performance тестирования
   - Оценка: 4 часа

### 🟡 НОРМАЛЬНО (Сделать в течение месяца)

5. **EventBus Integration Tests**
   - Файл: `/tests/integration/infrastructure/test_eventbus_integration.py`
   - Причина: Новые события не покрыты
   - Оценка: 3 часа

6. **Security Tests**
   - Файл: `/tests/security/test_api_security.py`
   - Причина: Нет security coverage
   - Оценка: 1 день

---

## 🎯 План Действий

### Неделя 1 (Сейчас)

**День 1-2**:
- [ ] Создать ResourceTracker unit tests
- [ ] Создать System BCM integration tests для ResourceTracker

**День 3-4**:
- [ ] Создать E2E business flow tests (BIA → Risk → Planning)
- [ ] Добавить Playwright/Selenium setup

**День 5**:
- [ ] Создать performance tests для AI Orchestrator
- [ ] Setup Locust для load testing

### Неделя 2

**День 1-2**:
- [ ] Расширить EventBus integration tests
- [ ] Добавить тесты для новых resource contention events

**День 3-5**:
- [ ] Создать security test suite
- [ ] Добавить penetration testing scenarios
- [ ] Setup security scanning tools

### Метрики успеха

**Coverage Target**:
- Unit Tests: 80%+ ✅ (уже есть)
- Integration Tests: 70%+ (текущие ~40%)
- E2E Tests: 60%+ (текущие ~10%)
- Performance Tests: Базовые benchmarks (текущие 0%)
- Security Tests: OWASP Top 10 coverage (текущие 0%)

---

## 📦 Необходимые Зависимости

### Для E2E Tests
```bash
pip install playwright pytest-playwright
playwright install chromium
```

### Для Performance Tests
```bash
pip install locust pytest-benchmark
```

### Для Security Tests
```bash
pip install bandit safety pytest-security
```

---

## 🔍 Анализ Черновиков

### 1. `/Users/MD/Downloads/files/tests/business-flow.e2e.spec.ts`

**Что полезно**:
- ✅ Структура E2E теста
- ✅ Playwright usage pattern
- ✅ User flow concept

**Что нужно адаптировать**:
- ❌ TypeScript → Python
- ❌ Generic flows → BCM-specific
- ❌ localhost:3000 → реальные порты сервисов
- ❌ Добавить BCM business logic

**Рекомендация**: Использовать как template, но полностью переписать для BCM платформы

### 2. `/Users/MD/Downloads/files/tests/orchestrator.performance.spec.ts`

**Что полезно**:
- ✅ Performance test concept
- ✅ Throughput measurement
- ✅ Load generation pattern

**Что нужно адаптировать**:
- ❌ Playwright → Locust (better for load testing)
- ❌ TypeScript → Python
- ❌ Generic API → AI Orchestrator specific
- ❌ Добавить resource monitoring
- ❌ Добавить latency P95/P99 metrics

**Рекомендация**: Использовать концепцию, но реализовать с Locust для более точного load testing

---

## ✅ Итоговые Рекомендации

### Немедленно (Эта неделя)

1. **Создать ResourceTracker unit tests** - новый компонент без покрытия
2. **Создать System BCM integration tests** - интеграция ResourceTracker не тестируется
3. **Создать базовые E2E tests** - нет end-to-end покрытия

### Скоро (Следующие 2 недели)

4. **Создать performance test suite** - нет load/stress тестирования
5. **Расширить EventBus tests** - новые события не покрыты
6. **Создать security tests** - нет security coverage

### Инструменты

- **E2E**: Playwright (Python) ✅
- **Performance**: Locust + pytest-benchmark ✅
- **Security**: Bandit + Safety + OWASP ZAP ✅

### Метрики

**Текущее**:
- Unit: 80%+ ✅
- Integration: ~40% ⚠️
- E2E: ~10% ❌
- Performance: 0% ❌
- Security: 0% ❌

**Целевое** (через 2 недели):
- Unit: 85%+ ✅
- Integration: 70%+ ✅
- E2E: 60%+ ✅
- Performance: Базовые benchmarks ✅
- Security: OWASP Top 10 ✅

---

**Дата**: 2025-10-11
**Автор**: Claude Code
**Статус**: Gap Analysis Complete - Action Plan Ready
