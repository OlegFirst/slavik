# Digital Twin WebSocket Integration

Complete WebSocket infrastructure for real-time Digital Twin updates in the BCM platform.

## 🎯 Overview

This implementation provides a comprehensive real-time WebSocket system specifically designed for Digital Twin data streaming, synchronization, and event handling. It integrates with the existing API Gateway and connects to Odoo backend systems.

## 🚀 Quick Start

### 1. Start the Service
```bash
cd /Users/MD/ISO-22301/api/
python start_digital_twin_websocket.py
```

### 2. Test the Integration
```bash
python test_digital_twin_websocket.py
```

### 3. Run Examples
```bash
python digital_twin_websocket_examples.py
```

## 📡 Available Endpoints

### HTTP API Endpoints
- `GET /health` - Service health check
- `GET /digital-twin/personal` - Get all Personal Digital Twins
- `GET /digital-twin/personal/{twin_id}` - Get specific Digital Twin
- `POST /digital-twin/personal/{twin_id}/sync` - Trigger Digital Twin sync
- `GET /digital-twin/organization/metrics` - Get organization health metrics
- `GET /digital-twin/organization/health` - Get organization health summary

### WebSocket Endpoints
- `ws://localhost:8999/ws/{client_id}` - General WebSocket for all updates
- `ws://localhost:8999/ws/digital-twin/{client_id}` - Specialized Digital Twin WebSocket

## 🔄 Real-time Data Streams

### Personal Digital Twins (10-second updates)
- Individual health scores
- Sync status updates
- Wellness metrics (mental, physical, professional)
- Risk indicators (burnout, health, performance)

### Organization Metrics (30-second updates)
- Overall organization health
- Department-level statistics
- Team wellness indicators
- Productivity indices
- Sync success rates

### Event Streams (5-second intervals)
- Health score changes
- Risk alerts
- Synchronization events
- Performance updates

### Advanced Analytics (45-second updates)
- Burnout forecasting
- Performance trend predictions
- Intervention recommendations
- Confidence scoring

### Performance Monitoring (20-second updates)
- WebSocket connection statistics
- System performance metrics
- API response times
- Error rates

## 📋 WebSocket Topics

Subscribe to these topics to receive specific data streams:

- `digital_twins` - Personal Digital Twin updates
- `metrics` - Organization health metrics
- `twin_events` - Digital Twin events (sync, create, update)
- `health` - Service health monitoring
- `performance` - System performance metrics
- `analytics` - Predictive analytics data
- `notifications` - System notifications
- `alerts` - Critical alerts

## 🎮 WebSocket Commands

### Subscribe to Topics
```json
{
    "type": "subscribe",
    "topics": ["digital_twins", "metrics", "twin_events"]
}
```

### Trigger Digital Twin Sync
```json
{
    "type": "sync",
    "twin_id": "1"
}
```

### Refresh Cached Data
```json
{
    "type": "refresh"
}
```

### Health Check
```json
{
    "type": "ping"
}
```

### Unsubscribe from Topics
```json
{
    "type": "unsubscribe",
    "topics": ["analytics"]
}
```

## 💾 Message Types

### Connection Messages
```json
{
    "type": "connection",
    "status": "connected",
    "client_id": "your_client_id",
    "timestamp": "2024-09-18T12:00:00Z"
}
```

### Digital Twins Update
```json
{
    "type": "digital_twins_update",
    "data": {
        "digital_twins": [
            {
                "id": 1,
                "user_id": 1,
                "name": "John Smith Digital Twin",
                "health_score": 0.85,
                "sync_status": "synced",
                "last_sync": "2024-09-18T12:00:00Z",
                "mental_wellness": 0.78,
                "physical_wellness": 0.92,
                "professional_performance": 0.88,
                "stress_level": 0.25,
                "energy_level": 0.73,
                "focus_score": 0.81,
                "collaboration_score": 0.89,
                "learning_progress": 0.67,
                "risk_indicators": {
                    "burnout_risk": 0.15,
                    "health_risk": 0.08,
                    "performance_risk": 0.12
                }
            }
        ],
        "count": 1,
        "last_updated": "2024-09-18T12:00:00Z"
    },
    "timestamp": "2024-09-18T12:00:00Z"
}
```

### Twin Events
```json
{
    "type": "twin_event",
    "event_type": "sync_triggered",
    "data": {
        "twin_id": "1",
        "event_data": {
            "status": "success",
            "message": "Synchronization started"
        },
        "timestamp": "2024-09-18T12:00:00Z"
    },
    "timestamp": "2024-09-18T12:00:00Z"
}
```

### Organization Metrics
```json
{
    "type": "organization_metrics_update",
    "data": {
        "overall_health": 0.84,
        "team_wellness": 0.79,
        "productivity_index": 0.91,
        "stress_index": 0.23,
        "collaboration_score": 0.87,
        "learning_velocity": 0.72,
        "total_employees": 45,
        "active_twins": 38,
        "sync_success_rate": 0.96,
        "risk_alerts": 2,
        "departments": [
            {
                "name": "Engineering",
                "health_score": 0.89,
                "employee_count": 15,
                "active_twins": 13
            }
        ]
    },
    "timestamp": "2024-09-18T12:00:00Z"
}
```

## 🔗 Odoo Integration

The system attempts to connect to real Odoo data through multiple endpoints:

### Digital Twin Data
- Primary: `/api/bcm/personal-digital-twin`
- Fallback: `/web/dataset/call_kw/bcm.personal.digital.twin/search_read`

### Organization Metrics
- Primary: `/api/bcm/organization/health-metrics`
- Fallback: `/web/dataset/call_kw/bcm.organization.health/search_read`

### Synchronization
- Primary: `/api/bcm/personal-digital-twin/{twin_id}/sync`
- Fallback: `/web/dataset/call_kw/bcm.personal.digital.twin/sync_twin`

### Authentication
Set environment variable for Odoo authentication:
```bash
export ODOO_URL="http://localhost:8069"
export ODOO_AUTH_TOKEN="your_auth_token"
```

## 🏗️ Architecture

### Components

1. **DigitalTwinDataManager** - Core data management and streaming
2. **ConnectionManager** - WebSocket connection handling
3. **LiveDataManager** - General system metrics streaming
4. **API Gateway Integration** - HTTP endpoints and WebSocket routing

### Data Flow

1. WebSocket clients connect and subscribe to topics
2. Background tasks fetch data from Odoo (with fallback to mock data)
3. Data is cached and broadcasted to subscribed clients
4. Real-time events are generated and streamed
5. Client commands trigger actions (sync, refresh, etc.)

### Performance Features

- Efficient caching system
- Connection pooling
- Graceful error handling
- Memory optimization
- Background task management

## 🔧 Configuration

### Environment Variables
```bash
ODOO_URL=http://localhost:8069
ODOO_AUTH_TOKEN=your_token_here
```

### Stream Intervals
- Personal Twins: 10 seconds
- Organization Metrics: 30 seconds
- System Health: 15 seconds
- Performance Metrics: 20 seconds
- Event Stream: 5 seconds
- Predictive Analytics: 45 seconds

## 🧪 Testing

### Unit Tests
```bash
python test_digital_twin_websocket.py
```

### Manual Testing
```bash
# Start service
python start_digital_twin_websocket.py

# In another terminal, run examples
python digital_twin_websocket_examples.py
```

### WebSocket Testing Tools
- [WebSocket King](https://websocketking.com/)
- [Postman WebSocket](https://www.postman.com/)
- Browser Developer Tools

## 🚨 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure service is running on port 8999
   - Check firewall settings

2. **No Data Updates**
   - Verify Odoo connection
   - Check authentication tokens
   - Review server logs

3. **High Memory Usage**
   - Monitor cache sizes
   - Check for connection leaks
   - Review background task performance

### Logging

Logs are written to:
- Console output
- `/Users/MD/ISO-22301/api/digital_twin_websocket.log`

### Health Monitoring

- HTTP endpoint: `GET /health`
- WebSocket ping/pong mechanism
- Built-in performance metrics

## 📚 Examples

See `digital_twin_websocket_examples.py` for comprehensive usage examples:

- Basic connection and subscription
- Full monitoring setup
- Interactive command interface
- Error handling patterns

## 🔒 Security Considerations

1. **Authentication**: Implement proper token-based authentication
2. **Rate Limiting**: Built-in rate limiting for HTTP endpoints
3. **Input Validation**: Validate all WebSocket messages
4. **Error Handling**: Graceful error responses without data leakage
5. **Connection Management**: Automatic cleanup of stale connections

## 🚀 Integration with Frontend

### React/Vue.js Example
```javascript
const ws = new WebSocket('ws://localhost:8999/ws/digital-twin/frontend_client');

ws.onopen = function() {
    // Subscribe to Digital Twin topics
    ws.send(JSON.stringify({
        type: 'subscribe',
        topics: ['digital_twins', 'metrics', 'twin_events']
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.type === 'digital_twins_update') {
        // Update Digital Twin visualizations
        updateDigitalTwinDisplay(data.data.digital_twins);
    } else if (data.type === 'organization_metrics_update') {
        // Update organization health dashboard
        updateOrganizationMetrics(data.data);
    }
};

// Trigger sync
function syncDigitalTwin(twinId) {
    ws.send(JSON.stringify({
        type: 'sync',
        twin_id: twinId
    }));
}
```

## 📈 Performance Metrics

The system provides built-in performance monitoring:

- WebSocket connection count
- Active subscription tracking
- Cache efficiency metrics
- API response times
- Error rates
- Memory usage patterns

## 🔄 Future Enhancements

1. **Enhanced Security**: OAuth2 integration, JWT tokens
2. **Scalability**: Redis pub/sub for multi-instance deployment
3. **Analytics**: Advanced machine learning predictions
4. **Customization**: Configurable stream intervals and topics
5. **Integration**: Additional data source connectors

## 📞 Support

For issues or questions about the Digital Twin WebSocket integration:

1. Check the logs for error details
2. Run the test script to verify functionality
3. Review the examples for proper usage patterns
4. Ensure all dependencies are installed
5. Verify Odoo backend connectivity

---

This Digital Twin WebSocket integration provides the real-time infrastructure needed for the DigitalTwin3D frontend component and enables comprehensive monitoring of personal and organizational digital twins in the BCM platform.