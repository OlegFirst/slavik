# DIGITAL TWIN + WebSocket INTEGRATION

## 🎯 **НАЙДЕНО! WebSocket инфраструктура УЖЕ ЕСТЬ!**

### 📍 **Существующие компоненты:**
- `/api/websocket_manager.py` - WebSocket Manager (готов!)
- `/api/simple_gateway.py` - FastAPI Gateway
- `/api/socketio_server.js` - Node.js SocketIO сервер

## 🔗 **ПЛАН ИНТЕГРАЦИИ:**

### **1. Добавить Digital Twin в WebSocket Manager**

```python
# Обновить /api/websocket_manager.py
class DigitalTwinDataManager:
    """Real-time Digital Twin data streams"""

    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.odoo_client = httpx.AsyncClient()

    async def start_personal_twins_stream(self, interval: int = 10):
        """Stream Personal Twins updates"""
        async def stream_twins():
            while True:
                try:
                    # Get from Odoo Digital Twin API
                    response = await self.odoo_client.get(
                        "http://localhost:8069/api/digital-twin/overview"
                    )

                    if response.status_code == 200:
                        data = response.json()
                        message = {
                            "type": "digital_twin_update",
                            "data": data,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        await self.manager.broadcast_to_topic("digital_twins", message)

                except Exception as e:
                    logger.error(f"Digital Twin stream error: {e}")

                await asyncio.sleep(interval)

        return asyncio.create_task(stream_twins())

    async def send_twin_event(self, event_type: str, twin_data: Dict):
        """Send Digital Twin lifecycle events"""
        message = {
            "type": "twin_event",
            "event": event_type,
            "data": twin_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_topic("twin_events", message)
```

### **2. Обновить simple_gateway.py для Digital Twin API**

```python
# Добавить в simple_gateway.py
from websocket_manager import connection_manager, live_data_manager, websocket_endpoint

# Digital Twin endpoints proxy
@app.get("/api/digital-twin/overview")
async def get_digital_twin_overview():
    """Proxy to Odoo Digital Twin API"""
    try:
        async with http_client as client:
            response = await client.get(f"{SERVICES['odoo']}/api/digital-twin/overview")
            return response.json()
    except Exception as e:
        logger.error(f"Digital Twin API error: {e}")
        raise HTTPException(status_code=500, detail="Digital Twin service unavailable")

@app.websocket("/ws/digital-twin/{client_id}")
async def digital_twin_websocket(websocket: WebSocket, client_id: str):
    """Digital Twin WebSocket endpoint"""
    # Add Digital Twin manager
    digital_twin_manager = DigitalTwinDataManager(connection_manager)
    await websocket_endpoint(websocket, client_id, connection_manager, digital_twin_manager)
```

### **3. Обновить Odoo EventBus integration**

```python
# В eventbus_integration.py изменить URL на API Gateway:
eventbus_url = fields.Char(
    default='ws://localhost:8999/ws/digital-twin',  # API Gateway WebSocket
    help="Connect to API Gateway WebSocket instead of direct EventBus"
)

def send_to_eventbus(self, message):
    """Send via API Gateway"""
    import requests
    requests.post('http://localhost:8999/api/eventbus/publish', json=message)
```

## 🚀 **КАК ЗАПУСТИТЬ:**

### **1. Запустить API Gateway с WebSocket**
```bash
cd /Users/MD/ISO-22301/api/
pip install -r requirements.txt
uvicorn simple_gateway:app --host 0.0.0.0 --port 8999 --reload
```

### **2. Обновить Frontend подключение**
```typescript
// В digitalTwinAPI.ts изменить WebSocket URL:
const wsUrl = 'ws://localhost:8999/ws/digital-twin/admin-panel';

// Подписаться на Digital Twin события
websocket.send(JSON.stringify({
    type: 'subscribe',
    topics: ['digital_twins', 'twin_events', 'metrics', 'health']
}));
```

### **3. Проверить подключения**
```bash
# Terminal 1 - BCM Platform
./launch_bcm_platform.sh

# Terminal 2 - API Gateway
cd api && uvicorn simple_gateway:app --port 8999

# Terminal 3 - Admin Panel
cd frontend/admin_panel && npm start

# Проверить WebSocket в браузере:
# ws://localhost:8999/ws/digital-twin/test
```

## 📊 **АРХИТЕКТУРА ИНТЕГРАЦИИ:**

```
┌─────────────────┐    ws://localhost:8999     ┌──────────────────┐
│   Frontend      │ ←─────────────────────────→ │   API Gateway    │
│  (Admin Panel)  │   /ws/digital-twin/{id}    │   simple_gateway │
└─────────────────┘                            │   + websocket    │
         ↑                                      │   manager        │
         │ HTTP REST                            └──────────────────┘
         ↓                                               ↑
┌─────────────────────────────────────────────────────────┐     │ HTTP
│                 ODOO BCM PLATFORM                       │     │
│  ┌─────────────┐    hooks     ┌─────────────────────┐   │     │
│  │  res.users  │ ────────────→│ Digital Twin Models │───┼─────┘
│  │  (CRM)      │              │ - PersonalTwin      │   │ /api/digital-twin/*
│  └─────────────┘              │ - LifecycleManager  │   │
│                                │ - EventBusInteg.    │   │
│                                └─────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## ✅ **РЕЗУЛЬТАТ:**
- **Реальный WebSocket сервер** на 8999 порту
- **Digital Twin события** в real-time
- **Frontend интеграция** без изменений
- **Odoo подключение** через HTTP API
- **Масштабируемая архитектура** для 70+ сервисов

**Осталось только обновить 3 файла и все заработает!** 🎉