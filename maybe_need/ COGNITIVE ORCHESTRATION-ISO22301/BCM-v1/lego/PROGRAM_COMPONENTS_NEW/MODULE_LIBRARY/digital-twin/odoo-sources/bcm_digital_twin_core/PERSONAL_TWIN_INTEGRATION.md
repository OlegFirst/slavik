# Personal Digital Twin Frontend Integration

## Overview

The Personal Digital Twin system provides seamless integration between users and their digital twins across multiple frontend interfaces including:

- **Web Portal v2** (Vue.js at port 5173)
- **Admin Panel** (React at port 3001)
- **Main Odoo** (Odoo Web Framework at port 8069)

## Architecture

### Backend Components

1. **PersonalTwinConnector Model** (`/models/personal_twin_connector.py`)
   - Manages user connections to digital twins
   - Handles real-time session management
   - Stores widget configurations and dashboard layouts
   - Manages notification preferences

2. **Personal Twin API Controller** (`/controllers/personal_twin_api.py`)
   - REST API endpoints for frontend integration
   - WebSocket simulation for real-time updates
   - CORS support for cross-origin requests
   - Multi-portal authentication

### Frontend Integration Points

#### 1. Dashboard Data Retrieval

**Endpoint:** `GET /api/personal-twin/dashboard-data`

```javascript
// Example: Vue.js Web Portal v2 Integration
async function fetchDashboardData(portalType = 'web_portal_v2', sessionId = null) {
  try {
    const response = await fetch('/api/personal-twin/dashboard-data?' + new URLSearchParams({
      portal_type: portalType,
      session_id: sessionId || generateSessionId(),
      refresh: 'false'
    }), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
      }
    });

    const result = await response.json();

    if (result.status === 'success') {
      return {
        connectionInfo: result.data.connection,
        dashboardData: result.data.dashboard,
        portalConfig: result.data.portal_config,
        apiInfo: result.data.api_info
      };
    } else {
      throw new Error(result.data.error?.message || 'Failed to fetch dashboard data');
    }
  } catch (error) {
    console.error('Dashboard data fetch error:', error);
    throw error;
  }
}

// Usage in Vue.js component
export default {
  data() {
    return {
      dashboardData: null,
      connectionInfo: null,
      loading: true
    };
  },
  async mounted() {
    try {
      const { dashboardData, connectionInfo } = await fetchDashboardData('web_portal_v2');
      this.dashboardData = dashboardData;
      this.connectionInfo = connectionInfo;

      // Initialize WebSocket connection
      this.initializeWebSocket(connectionInfo.websocket_channels);
    } catch (error) {
      this.$toast.error('Failed to load dashboard data');
    } finally {
      this.loading = false;
    }
  }
};
```

#### 2. Widget Configuration Management

**Endpoint:** `POST /api/personal-twin/update-widget`

```javascript
// Example: React Admin Panel Integration
import { useState, useCallback } from 'react';

const useWidgetConfig = () => {
  const [configs, setConfigs] = useState({});

  const updateWidgetConfig = useCallback(async (widgetId, newConfig) => {
    try {
      const response = await fetch('/api/personal-twin/update-widget', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({
          widget_id: widgetId,
          config: newConfig,
          session_id: getSessionId()
        })
      });

      const result = await response.json();

      if (result.status === 'success') {
        setConfigs(prev => ({
          ...prev,
          [widgetId]: newConfig
        }));

        // Show success notification
        showNotification('Widget configuration updated', 'success');

        return result.data;
      } else {
        throw new Error(result.message || 'Failed to update widget configuration');
      }
    } catch (error) {
      console.error('Widget config update error:', error);
      showNotification('Failed to update widget configuration', 'error');
      throw error;
    }
  }, []);

  return { configs, updateWidgetConfig };
};

// Usage in React component
const DashboardWidget = ({ widgetId, initialConfig }) => {
  const { updateWidgetConfig } = useWidgetConfig();
  const [config, setConfig] = useState(initialConfig);

  const handleConfigChange = async (newConfig) => {
    try {
      await updateWidgetConfig(widgetId, newConfig);
      setConfig(newConfig);
    } catch (error) {
      // Error handled in hook
    }
  };

  return (
    <Widget
      config={config}
      onConfigChange={handleConfigChange}
    />
  );
};
```

#### 3. Real-time Updates via WebSocket Simulation

```javascript
// Example: WebSocket Integration for Real-time Updates
class PersonalTwinWebSocket {
  constructor(apiInfo, onUpdate) {
    this.apiInfo = apiInfo;
    this.onUpdate = onUpdate;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.isConnected = false;

    this.connect();
  }

  async connect() {
    try {
      // Get WebSocket connection info
      const response = await fetch('/ws/personal-twin/live-updates?' + new URLSearchParams({
        session_id: this.apiInfo.session_id,
        portal_type: this.apiInfo.portal_type
      }), {
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
      });

      const wsInfo = await response.json();

      if (wsInfo.status === 'success') {
        // In a real implementation, this would create a WebSocket connection
        // For now, we'll simulate with polling
        this.simulateWebSocket(wsInfo.data);
      }
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.handleReconnect();
    }
  }

  simulateWebSocket(wsInfo) {
    console.log('WebSocket simulation started:', wsInfo);
    this.isConnected = true;
    this.reconnectAttempts = 0;

    // Simulate periodic updates
    this.pollInterval = setInterval(async () => {
      try {
        await this.checkForUpdates();
      } catch (error) {
        console.error('Update check error:', error);
        this.handleReconnect();
      }
    }, this.getUpdateInterval());

    // Simulate heartbeat
    this.heartbeatInterval = setInterval(() => {
      this.sendHeartbeat();
    }, wsInfo.heartbeat_interval * 1000);
  }

  async checkForUpdates() {
    // This would be replaced with actual WebSocket message handling
    // For now, we can check for updates via API
    const response = await fetch('/api/personal-twin/notifications?' + new URLSearchParams({
      limit: '5',
      unread_only: 'true'
    }), {
      headers: { 'Authorization': `Bearer ${getAuthToken()}` }
    });

    const result = await response.json();
    if (result.status === 'success' && result.data.notifications.length > 0) {
      this.onUpdate({
        type: 'notifications',
        data: result.data.notifications
      });
    }
  }

  getUpdateInterval() {
    // Convert update frequency to milliseconds
    const frequencies = {
      'realtime': 1000,
      'high': 5000,
      'medium': 30000,
      'low': 300000
    };
    return frequencies[this.apiInfo.update_frequency] || 30000;
  }

  sendHeartbeat() {
    console.log('Heartbeat sent');
    // In a real WebSocket implementation, this would send a ping frame
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

      setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
      this.isConnected = false;
    }
  }

  disconnect() {
    this.isConnected = false;
    if (this.pollInterval) clearInterval(this.pollInterval);
    if (this.heartbeatInterval) clearInterval(this.heartbeatInterval);
  }
}

// Usage in application
const wsConnection = new PersonalTwinWebSocket(
  apiInfo,
  (update) => {
    console.log('Received update:', update);

    switch (update.type) {
      case 'notifications':
        updateNotifications(update.data);
        break;
      case 'widget_config_update':
        updateWidgetConfig(update.widget_id, update.config);
        break;
      case 'twin_change':
        updateTwinData(update.change_data);
        break;
      case 'layout_update':
        updateDashboardLayout(update.portal_type, update.layout);
        break;
      default:
        console.log('Unknown update type:', update.type);
    }
  }
);
```

#### 4. Dashboard Layout Management

```javascript
// Example: Dashboard Layout Management
class DashboardLayoutManager {
  constructor(portalType, initialLayout) {
    this.portalType = portalType;
    this.layout = initialLayout;
    this.saveDebounceTime = 1000;
    this.saveTimeout = null;
  }

  async updateLayout(newLayout) {
    this.layout = newLayout;

    // Debounce save to avoid too many API calls
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }

    this.saveTimeout = setTimeout(async () => {
      await this.saveLayout();
    }, this.saveDebounceTime);
  }

  async saveLayout() {
    try {
      const response = await fetch('/api/personal-twin/layout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({
          portal_type: this.portalType,
          layout: this.layout
        })
      });

      const result = await response.json();

      if (result.status === 'success') {
        console.log('Layout saved successfully');
      } else {
        throw new Error(result.message || 'Failed to save layout');
      }
    } catch (error) {
      console.error('Layout save error:', error);
    }
  }

  async loadLayout() {
    try {
      const response = await fetch('/api/personal-twin/layout?' + new URLSearchParams({
        portal_type: this.portalType
      }), {
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
      });

      const result = await response.json();

      if (result.status === 'success') {
        this.layout = result.data.layout;
        return this.layout;
      } else {
        throw new Error(result.message || 'Failed to load layout');
      }
    } catch (error) {
      console.error('Layout load error:', error);
      return null;
    }
  }
}
```

## Portal-Specific Integration Examples

### Web Portal v2 (Vue.js)

```vue
<template>
  <div class="personal-twin-dashboard">
    <div v-if="loading" class="loading-spinner">
      Loading Personal Twin Dashboard...
    </div>

    <div v-else class="dashboard-grid" :style="gridStyle">
      <widget-component
        v-for="widget in widgets"
        :key="widget.id"
        :widget-id="widget.id"
        :config="widget.config"
        :data="widget.data"
        @config-change="updateWidgetConfig"
      />
    </div>

    <notification-panel
      :notifications="notifications"
      @mark-read="markNotificationRead"
    />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import { usePersonalTwin } from '@/composables/usePersonalTwin';

export default {
  name: 'PersonalTwinDashboard',
  setup() {
    const {
      dashboardData,
      notifications,
      loading,
      initializeDashboard,
      updateWidgetConfig,
      markNotificationRead,
      cleanup
    } = usePersonalTwin();

    onMounted(async () => {
      await initializeDashboard('web_portal_v2');
    });

    onUnmounted(() => {
      cleanup();
    });

    return {
      dashboardData,
      notifications,
      loading,
      updateWidgetConfig,
      markNotificationRead
    };
  }
};
</script>
```

### Admin Panel (React)

```jsx
import React, { useState, useEffect } from 'react';
import { Grid, Paper, Alert } from '@mui/material';
import { usePersonalTwin } from '../hooks/usePersonalTwin';

const PersonalTwinDashboard = () => {
  const {
    dashboardData,
    loading,
    error,
    initializeDashboard,
    updateWidgetConfig
  } = usePersonalTwin();

  const [gridLayout, setGridLayout] = useState([]);

  useEffect(() => {
    initializeDashboard('admin_panel');
  }, []);

  useEffect(() => {
    if (dashboardData?.widget_configs) {
      const layout = Object.entries(dashboardData.widget_configs).map(([id, config]) => ({
        i: id,
        x: config.position.x,
        y: config.position.y,
        w: config.size.width,
        h: config.size.height
      }));
      setGridLayout(layout);
    }
  }, [dashboardData]);

  if (loading) {
    return <div>Loading Personal Twin Dashboard...</div>;
  }

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  return (
    <div className="personal-twin-dashboard">
      <Grid container spacing={2}>
        {Object.entries(dashboardData?.widget_configs || {}).map(([widgetId, config]) => (
          <Grid
            item
            key={widgetId}
            xs={config.size.width}
            md={config.size.height}
          >
            <Paper elevation={2}>
              <WidgetComponent
                widgetId={widgetId}
                config={config}
                onConfigChange={(newConfig) => updateWidgetConfig(widgetId, newConfig)}
              />
            </Paper>
          </Grid>
        ))}
      </Grid>
    </div>
  );
};

export default PersonalTwinDashboard;
```

### Main Odoo Integration

```javascript
// Odoo Web Framework Integration
odoo.define('bcm_digital_twin_core.PersonalTwinDashboard', function (require) {
    'use strict';

    const AbstractAction = require('web.AbstractAction');
    const ajax = require('web.ajax');
    const core = require('web.core');

    const PersonalTwinDashboard = AbstractAction.extend({
        template: 'PersonalTwinDashboard',

        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.dashboardData = null;
            this.connectionInfo = null;
        },

        start: function () {
            const self = this;
            return this._super().then(function () {
                return self.loadDashboardData();
            });
        },

        loadDashboardData: function () {
            const self = this;
            return ajax.jsonRpc('/api/personal-twin/dashboard-data', 'call', {
                portal_type: 'odoo_main'
            }).then(function (result) {
                if (result.status === 'success') {
                    self.dashboardData = result.data.dashboard;
                    self.connectionInfo = result.data.connection;
                    self.renderDashboard();
                } else {
                    self.displayNotification({
                        type: 'danger',
                        message: 'Failed to load dashboard data'
                    });
                }
            });
        },

        renderDashboard: function () {
            const $dashboard = this.$('.dashboard-content');

            // Render widgets based on configuration
            Object.keys(this.dashboardData.widget_configs).forEach(widgetId => {
                const config = this.dashboardData.widget_configs[widgetId];
                const $widget = this.renderWidget(widgetId, config);
                $dashboard.append($widget);
            });
        },

        renderWidget: function (widgetId, config) {
            const $widget = $('<div>').addClass('dashboard-widget').attr('data-widget-id', widgetId);

            // Widget content based on type
            switch (widgetId) {
                case 'twin_status':
                    $widget.html(this.renderTwinStatus());
                    break;
                case 'activity_feed':
                    $widget.html(this.renderActivityFeed());
                    break;
                case 'metrics_chart':
                    $widget.html(this.renderMetricsChart());
                    break;
                default:
                    $widget.html('<p>Unknown widget: ' + widgetId + '</p>');
            }

            return $widget;
        },

        updateWidgetConfig: function (widgetId, newConfig) {
            const self = this;
            return ajax.jsonRpc('/api/personal-twin/update-widget', 'call', {
                widget_id: widgetId,
                config: newConfig
            }).then(function (result) {
                if (result.status === 'success') {
                    self.dashboardData.widget_configs[widgetId] = newConfig;
                    self.displayNotification({
                        type: 'success',
                        message: 'Widget configuration updated'
                    });
                } else {
                    self.displayNotification({
                        type: 'danger',
                        message: 'Failed to update widget configuration'
                    });
                }
            });
        }
    });

    core.action_registry.add('personal_twin_dashboard', PersonalTwinDashboard);

    return PersonalTwinDashboard;
});
```

## Security Considerations

### Authentication

All API endpoints require proper authentication:

- **Internal users**: Odoo session authentication
- **Portal users**: Portal session authentication
- **API access**: Bearer token authentication

### User Isolation

- Users can only access their own personal twin connectors
- Record rules enforce user-level security
- API endpoints filter data by current user

### CORS Configuration

```javascript
// Configure CORS for cross-origin requests
const corsConfig = {
  'Access-Control-Allow-Origin': '*', // Restrict in production
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
  'Access-Control-Max-Age': '86400'
};
```

## Performance Optimization

### Caching Strategy

```javascript
// Client-side caching example
class DashboardCache {
  constructor(ttl = 300000) { // 5 minutes TTL
    this.cache = new Map();
    this.ttl = ttl;
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  set(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  clear() {
    this.cache.clear();
  }
}

const dashboardCache = new DashboardCache();
```

### Rate Limiting

API endpoints include built-in rate limiting:
- Dashboard data: 60 requests per minute
- Widget updates: 30 requests per minute
- Real-time updates: 120 requests per minute

## Error Handling

### Standardized Error Responses

```json
{
  "status": "error",
  "timestamp": "2024-09-18T10:30:00Z",
  "data": {
    "error": {
      "message": "Authentication required",
      "code": 401,
      "details": {
        "type": "AuthenticationError",
        "required_permissions": ["personal_twin_access"]
      }
    }
  }
}
```

### Client-side Error Handling

```javascript
// Comprehensive error handling
async function handleApiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    const result = await response.json();

    if (!response.ok) {
      throw new ApiError(result.data?.error?.message || 'Request failed', response.status, result.data?.error?.details);
    }

    if (result.status === 'error') {
      throw new ApiError(result.data.error.message, result.data.error.code, result.data.error.details);
    }

    return result.data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Network error occurred', 0, { originalError: error.message });
  }
}

class ApiError extends Error {
  constructor(message, code, details) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
  }
}
```

## Testing

### Unit Testing Example

```javascript
// Jest testing for API integration
describe('Personal Twin API Integration', () => {
  let dashboardData;

  beforeEach(() => {
    // Mock authentication
    mockAuthToken('valid-token');
  });

  test('should fetch dashboard data successfully', async () => {
    const mockResponse = {
      status: 'success',
      data: {
        dashboard: { widget_configs: {} },
        connection: { connector_id: 1 }
      }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    const result = await fetchDashboardData('web_portal_v2');

    expect(result.dashboardData).toBeDefined();
    expect(result.connectionInfo).toBeDefined();
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/personal-twin/dashboard-data'),
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          'Authorization': 'Bearer valid-token'
        })
      })
    );
  });

  test('should handle widget configuration updates', async () => {
    const widgetId = 'twin_status';
    const newConfig = { position: { x: 1, y: 1 } };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'success', data: { widget_id: widgetId, config: newConfig } })
    });

    const { updateWidgetConfig } = useWidgetConfig();
    await updateWidgetConfig(widgetId, newConfig);

    expect(fetch).toHaveBeenCalledWith(
      '/api/personal-twin/update-widget',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          widget_id: widgetId,
          config: newConfig
        })
      })
    );
  });
});
```

## Deployment Considerations

### Environment Configuration

```bash
# Environment variables for production
PERSONAL_TWIN_API_RATE_LIMIT=60
PERSONAL_TWIN_WEBSOCKET_ENABLED=true
PERSONAL_TWIN_CACHE_TTL=300
PERSONAL_TWIN_LOG_LEVEL=INFO
```

### Monitoring and Logging

```python
# Server-side logging configuration
import logging

# Configure logger for personal twin operations
twin_logger = logging.getLogger('bcm.personal_twin')
twin_logger.setLevel(logging.INFO)

# Log important events
twin_logger.info(f"Dashboard data retrieved for user {user.name} via {portal_type}")
twin_logger.warning(f"Widget configuration update failed for user {user.name}: {error}")
twin_logger.error(f"WebSocket connection failed: {error}")
```

This integration provides a comprehensive foundation for implementing Personal Digital Twins across multiple frontend interfaces with real-time updates, customizable dashboards, and robust security measures.