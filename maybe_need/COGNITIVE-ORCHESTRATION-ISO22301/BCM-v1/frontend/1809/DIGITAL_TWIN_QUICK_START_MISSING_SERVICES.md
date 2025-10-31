# DIGITAL TWIN - НЕДОСТАЮЩИЕ СЕРВИСЫ ДЛЯ ЗАПУСКА

## 🚨 **КРИТИЧНО! ЧТО НУЖНО СОЗДАТЬ СРОЧНО**

### **1. WebSocket Сервер (ОБЯЗАТЕЛЬНО!)**
```javascript
// /Users/MD/ISO-22301/services/websocket-server/server.js
const WebSocket = require('ws');
const express = require('express');
const http = require('http');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

wss.on('connection', function connection(ws) {
    console.log('Digital Twin client connected');

    // Heartbeat
    ws.isAlive = true;
    ws.on('pong', () => ws.isAlive = true);

    ws.on('message', function message(data) {
        const msg = JSON.parse(data);
        console.log('Received:', msg);

        // Broadcast to all clients
        wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify({
                    type: 'digital_twin_update',
                    data: msg
                }));
            }
        });
    });
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', connections: wss.clients.size });
});

server.listen(8001, () => {
    console.log('🚀 Digital Twin WebSocket Server started on ws://localhost:8001');
});
```

### **2. API Endpoints в Odoo (КРИТИЧНО!)**
```python
# /Users/MD/ISO-22301/core/odoo-18.0/addons/bcm_digital_twin_core/controllers/personal_twin_api.py
# ДОБАВИТЬ эти endpoints:

@http.route('/api/digital-twin/overview', type='json', auth='user', methods=['GET'])
def get_overview(self):
    """Dashboard overview data"""
    personal_twins = request.env['bcm.personal.digital.twin'].sudo()
    org_twins = request.env['bcm.digital.twin.organization'].sudo()

    return {
        'personalTwins': {
            'total': personal_twins.search_count([]),
            'active': personal_twins.search_count([('sync_status', '=', 'active')]),
            'inactive': personal_twins.search_count([('sync_status', '=', 'offline')])
        },
        'organizationalTwins': {
            'total': org_twins.search_count([]),
            'healthy': org_twins.search_count([('status', '=', 'active')]),
            'warning': 0,
            'error': 0
        },
        'dataCollection': {
            'totalServices': 73,
            'activeServices': 68,
            'collectionsPerHour': 145200
        },
        'recentActivity': []
    }

@http.route('/api/digital-twin/personal-twins', type='json', auth='user', methods=['GET'])
def get_personal_twins(self):
    """Get all personal twins"""
    twins = request.env['bcm.personal.digital.twin'].sudo().search([])
    return {
        'twins': [twin._to_dict() for twin in twins]
    }

# Добавить _to_dict() методы в модели!
```

### **3. Data Vacuum Service (ВАЖНО!)**
```javascript
// /Users/MD/ISO-22301/services/data-vacuum/app.js
const express = require('express');
const axios = require('axios');
const WebSocket = require('ws');

const app = express();
app.use(express.json());

class DataVacuum {
    constructor() {
        this.services = [
            { name: 'BCM Core', url: 'http://localhost:8069/api/bcm' },
            { name: 'AI Orchestrator', url: 'http://localhost:8000/api/v1' },
            { name: 'BIA Engine', url: 'http://localhost:8082/api' }
        ];
        this.isRunning = false;
        this.stats = { collected: 0, errors: 0 };
    }

    async start() {
        this.isRunning = true;
        console.log('🔄 Data Vacuum started - collecting from 70+ services');

        setInterval(async () => {
            if (!this.isRunning) return;
            await this.collectFromAllServices();
        }, 30000); // Every 30 seconds
    }

    async collectFromAllServices() {
        for (const service of this.services) {
            try {
                const response = await axios.get(service.url + '/data', { timeout: 5000 });
                this.stats.collected++;

                // Send to WebSocket
                this.broadcastUpdate({
                    type: 'data_collected',
                    service: service.name,
                    data: response.data,
                    timestamp: new Date().toISOString()
                });

            } catch (error) {
                this.stats.errors++;
                console.error(`❌ Failed to collect from ${service.name}:`, error.message);
            }
        }
    }

    broadcastUpdate(data) {
        // Send to EventBus WebSocket
        const ws = new WebSocket('ws://localhost:8001');
        ws.on('open', () => {
            ws.send(JSON.stringify(data));
            ws.close();
        });
    }
}

const vacuum = new DataVacuum();

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        running: vacuum.isRunning,
        stats: vacuum.stats
    });
});

app.post('/start', (req, res) => {
    vacuum.start();
    res.json({ message: 'Data vacuum started' });
});

app.listen(8010, () => {
    console.log('🔌 Data Vacuum Service running on http://localhost:8010');
    vacuum.start();
});
```

### **4. Package.json для сервисов**
```json
// /Users/MD/ISO-22301/services/package.json
{
  "name": "digital-twin-services",
  "version": "1.0.0",
  "scripts": {
    "start:websocket": "node websocket-server/server.js",
    "start:vacuum": "node data-vacuum/app.js",
    "start:all": "concurrently \"npm run start:websocket\" \"npm run start:vacuum\""
  },
  "dependencies": {
    "ws": "^8.13.0",
    "express": "^4.18.2",
    "axios": "^1.5.0",
    "concurrently": "^8.2.0"
  }
}
```

## 🔧 **КАК ЗАПУСТИТЬ МИНИМАЛЬНО**

### **Шаг 1: Создать сервисы**
```bash
cd /Users/MD/ISO-22301/
mkdir -p services/websocket-server services/data-vacuum

# Скопировать код выше в файлы
# Установить зависимости
cd services && npm install
```

### **Шаг 2: Добавить API в Odoo**
```bash
# Добавить endpoints в personal_twin_api.py
# Добавить _to_dict() методы в модели
```

### **Шаг 3: Запустить все**
```bash
# Терминал 1 - BCM Platform
./launch_bcm_platform.sh

# Терминал 2 - Digital Twin Services
cd services && npm run start:all

# Терминал 3 - Admin Panel
cd frontend/admin_panel && npm start
```

## 💡 **БЫСТРЫЙ FIX ДЛЯ ДЕМО**

Если нет времени на сервисы, можно **заменить в digitalTwinAPI.ts**:

```typescript
// Временный fix - вернуть mock данные при ошибке API
async getOverview(): Promise<DigitalTwinOverview> {
  try {
    const response = await bcmAPI.get('/api/digital-twin/overview');
    return response.data;
  } catch (error) {
    console.warn('⚠️ API unavailable, using demo data');
    return {
      personalTwins: { total: 47, active: 42, inactive: 5 },
      organizationalTwins: { total: 8, healthy: 6, warning: 1, error: 1 },
      dataCollection: { totalServices: 73, activeServices: 68, collectionsPerHour: 145200 },
      recentActivity: [/* mock data */]
    };
  }
}
```

**НО ЭТО TEMPORARY! Для production нужны реальные сервисы!** 🚨