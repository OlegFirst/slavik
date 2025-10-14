# BCM Digital Twin Platform - Complete Integration Guide

## 🏗️ Architecture Overview

The BCM Digital Twin Platform is a comprehensive hybrid system that combines the power of Odoo 18 ERP with advanced Node.js simulation services to provide cutting-edge Business Continuity Management (BCM) capabilities.

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Odoo 18      │◄──►│  Bridge API     │◄──►│   Node.js       │
│   BCM Core      │    │  Integration    │    │  Digital Twin   │
│                 │    │                 │    │   Simulation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   23+ BCM       │    │  AI Organs      │    │  Web Dashboard  │
│   Modules       │    │ Orchestration   │    │   Monitoring    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start Guide

### Prerequisites

- Docker & Docker Compose
- Odoo 18 installation
- Node.js 18+ environment
- PostgreSQL database

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/SEH-foundation/ISO-22301.git
cd ISO-22301/core/odoo-18.0/addons
```

2. **Install Odoo modules**
```bash
# Start Odoo container
docker-compose up -d

# Install BCM Digital Twin modules
docker exec odoo_container odoo -d your_db -i bcm_digital_twin_core,bcm_ai_twin_orchestrator --stop-after-init
```

3. **Setup Node.js Digital Twin service**
```bash
cd /path/to/digital-twin-main
npm install
npm run simple
```

4. **Verify installation**
```bash
# Check Odoo modules
curl http://localhost:8069/web/database/manager

# Check Node.js service
curl http://localhost:3000/api/health
```

## 📋 Features Overview

### Core Modules

#### 1. BCM Digital Twin Core (`bcm_digital_twin_core`)
- **Purpose**: Main integration layer between Odoo and Digital Twin services
- **Models**: `bcm.digital.twin.organization`, `bcm.digital.twin.simulation`
- **Features**: Multi-domain support, simulation management, BCM data synchronization

#### 2. AI Twin Orchestrator (`bcm_ai_twin_orchestrator`)
- **Purpose**: Coordinates 10 specialized AI organs for comprehensive analysis
- **AI Organs**: Governance Brain, Risk Advisor, Impact Oracle, Compliance Guardian, etc.
- **Features**: Parallel processing, real AI API integration, confidence scoring

### Digital Twin Organizations

#### Supported Domain Types
- **Corporate**: Financial services, manufacturing, technology companies
- **Government**: Public sector, municipalities, regulatory bodies
- **NPO**: Non-profit organizations, foundations, charities
- **Infrastructure**: Critical infrastructure, utilities, transportation

#### Key Capabilities
- Comprehensive organizational modeling
- Real-time health scoring (0-100%)
- BCM context integration
- Simulation-driven insights

## 🧠 AI Organs System

### The 10 AI Organs

| Organ | Icon | Purpose | API Integration |
|-------|------|---------|-----------------|
| Governance Brain | 🧠 | Strategic intelligence and policy guidance | OpenAI GPT-4 |
| Emergency Response | 🚨 | Crisis management and incident response | Real-time analysis |
| Impact Oracle | 🔮 | Predictive business impact analysis | ML forecasting |
| Scenario Creator | 📝 | Creative scenario generation and modeling | AI-powered |
| Risk Advisor | ⚡ | FAIR methodology + Monte Carlo analysis | Statistical models |
| Compliance Guardian | 🛡️ | Continuous regulatory compliance monitoring | Rule-based + AI |
| Performance Analyst | 📊 | KPI intelligence and performance optimization | Data analytics |
| Learning Coach | 🎓 | Training programs and competency optimization | Adaptive learning |
| Plan Generator | 📋 | Intelligent business continuity planning | AI planning |
| Lifecycle Monitor | 💓 | System health and lifecycle monitoring | Real-time monitoring |

### AI Configuration

Set up AI services with environment variables:

```bash
# .env configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
AI_MODEL=gpt-4
AI_USE_MOCK_DATA=false
```

## 🎯 Business Scenarios

### Supported Scenario Types

#### 1. Business Continuity Scenarios
- **Supply Chain Disruption**: Multi-tier supply chain impact analysis
- **Cyber Security Incidents**: Ransomware, data breaches, system failures
- **Pandemic Response**: Remote work adaptation, health protocols
- **Natural Disasters**: Physical infrastructure damage assessment
- **Key Personnel Loss**: Critical skill gap impact analysis
- **Technology Failures**: System downtime and recovery planning
- **Regulatory Changes**: Compliance impact assessment

#### 2. Risk Analysis Tools
- **Monte Carlo Simulations**: 10,000+ iteration risk modeling
- **FAIR Methodology**: Quantitative risk analysis
- **Crisis Response Planning**: Multi-phase response strategies
- **Compliance Gap Analysis**: ISO 22301, GDPR, SOX frameworks

### Example API Usage

```javascript
// Run supply chain disruption scenario
const response = await fetch('/api/bcm/scenarios/business-continuity', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    scenarioType: 'supply_chain_disruption',
    organizationData: { annualBudget: 5000000 },
    parameters: {
      severity: 0.8,
      recoveryTimeWeeks: 12,
      alternativeSuppliers: 1
    }
  })
});

const results = await response.json();
console.log('Financial Impact:', results.results.impact.financial);
```

## 🖥️ Web Dashboard

### AI Organs Monitor

Access the comprehensive monitoring dashboard at `http://localhost:3000/ai-organs`:

#### Features
- **Real-time Status**: Live status of all 10 AI organs
- **Performance Metrics**: Response times, confidence scores, success rates
- **System Health**: CPU, memory, API call monitoring
- **Analysis Timeline**: Historical analysis tracking
- **Interactive Controls**: Trigger AI analysis, risk assessments, compliance checks

#### Dashboard Sections
1. **AI Organs Status Overview**: Real-time organ health monitoring
2. **Performance Metrics**: Charts showing response times and confidence
3. **Recent AI Analysis**: Timeline of completed analyses
4. **Active AI Insights**: Current recommendations and findings
5. **AI Organs Control Panel**: Interactive analysis triggers
6. **System Health**: Infrastructure monitoring metrics

## 🔧 Configuration

### Odoo Configuration

#### System Parameters
```xml
<!-- Digital Twin service configuration -->
<record id="digital_twin_service_url" model="ir.config_parameter">
    <field name="key">digital_twin.service_url</field>
    <field name="value">http://localhost:3000</field>
</record>

<record id="digital_twin_timeout" model="ir.config_parameter">
    <field name="key">digital_twin.timeout</field>
    <field name="value">30</field>
</record>
```

#### Security Configuration
```xml
<!-- BCM Digital Twin security groups -->
<record id="group_digital_twin_user" model="res.groups">
    <field name="name">Digital Twin User</field>
    <field name="category_id" ref="base.module_category_business_continuity"/>
</record>

<record id="group_digital_twin_manager" model="res.groups">
    <field name="name">Digital Twin Manager</field>
    <field name="category_id" ref="base.module_category_business_continuity"/>
    <field name="implied_ids" eval="[(4, ref('group_digital_twin_user'))]"/>
</record>
```

### Node.js Configuration

#### Service Configuration
```javascript
// Server configuration
const config = {
    port: process.env.PORT || 3000,
    cors: {
        origin: process.env.CORS_ORIGINS?.split(',') || ['*'],
        methods: ['GET', 'POST', 'PUT', 'DELETE'],
        credentials: true
    },
    rateLimit: {
        enabled: process.env.RATE_LIMIT_ENABLED === 'true',
        requests: parseInt(process.env.RATE_LIMIT_REQUESTS) || 100,
        windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000
    }
};
```

## 📊 API Reference

### Core Endpoints

#### Digital Twin Management
```http
GET /api/digital-twins           # List all digital twins
POST /api/digital-twins          # Create new digital twin
GET /api/digital-twins/:id       # Get specific digital twin
PUT /api/digital-twins/:id/sync  # Sync with BCM data
```

#### AI Analysis
```http
GET /api/health                         # System health check
GET /api/digital-twins/:id/metrics      # Get organization metrics
GET /api/digital-twins/:id/predictions  # Get AI predictions
POST /api/digital-twins/:id/ai-analysis # Trigger AI analysis
```

#### Advanced Scenarios
```http
POST /api/bcm/scenarios/business-continuity    # Business continuity scenarios
POST /api/bcm/scenarios/crisis-response        # Crisis response planning
POST /api/bcm/scenarios/monte-carlo-risk       # Monte Carlo simulations
POST /api/bcm/scenarios/compliance-gap-analysis # Compliance gap analysis
```

### Response Formats

#### Standard Success Response
```json
{
  "success": true,
  "data": { /* response data */ },
  "timestamp": "2025-09-16T13:30:00.000Z",
  "confidence": 87
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-09-16T13:30:00.000Z"
}
```

## 🔍 Monitoring & Troubleshooting

### Health Checks

#### Odoo Health Check
```bash
# Check module installation
docker exec odoo_container odoo shell -d your_db -c "
env['ir.module.module'].search([('name', 'in', ['bcm_digital_twin_core', 'bcm_ai_twin_orchestrator'])])
"

# Test Bridge connection
docker exec odoo_container python3 -c "
import requests
response = requests.get('http://host.docker.internal:3000/api/health')
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
"
```

#### Node.js Health Check
```bash
# Service status
curl http://localhost:3000/api/health

# AI Organs status
curl http://localhost:3000/api/digital-twins/test/metrics
```

### Common Issues

#### Connection Issues
- Verify Docker network configuration
- Check firewall settings for port 3000
- Ensure `host.docker.internal` resolves correctly

#### AI Integration Issues
- Verify OpenAI API key is set correctly
- Check API rate limits and quotas
- Monitor AI response times in dashboard

#### Performance Issues
- Monitor system resources (CPU, memory)
- Check database query performance
- Review API response times in dashboard

## 📈 Performance Optimization

### Odoo Optimization
```python
# Enable parallel processing for AI organs
@api.model
def _run_ai_organs_parallel(self, twin_data):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for organ_name in self.AI_ORGANS:
            future = executor.submit(self._simulate_ai_organ, organ_name, {}, twin_data)
            futures.append((organ_name, future))

        results = {}
        for organ_name, future in futures:
            try:
                results[organ_name] = future.result(timeout=30)
            except Exception as e:
                results[organ_name] = {'error': str(e)}

        return results
```

### Node.js Optimization
```javascript
// Implement caching for expensive operations
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 600 }); // 10 minutes

app.get('/api/digital-twins/:id/metrics', async (req, res) => {
    const cacheKey = `metrics_${req.params.id}`;
    let metrics = cache.get(cacheKey);

    if (!metrics) {
        metrics = await calculateMetrics(req.params.id);
        cache.set(cacheKey, metrics);
    }

    res.json({ metrics });
});
```

## 🔐 Security Considerations

### Access Control
- Implement role-based access control (RBAC)
- Use JWT tokens for API authentication
- Enable HTTPS in production environments
- Regular security audits and penetration testing

### Data Protection
- Encrypt sensitive data at rest and in transit
- Implement data retention policies
- Regular backup and disaster recovery testing
- GDPR/privacy compliance measures

## 🚀 Deployment

### Production Deployment

#### Docker Compose Setup
```yaml
version: '3.8'
services:
  odoo:
    image: odoo:18
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - ./addons:/mnt/extra-addons
    ports:
      - "8069:8069"

  digital-twin:
    build: ./digital-twin-main
    environment:
      - NODE_ENV=production
      - PORT=3000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "3000:3000"

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
```

### Scaling Considerations
- Horizontal scaling with load balancers
- Database read replicas for analytics
- Redis caching layer for performance
- CDN for static assets delivery

## 📚 Additional Resources

### Documentation
- [Odoo 18 Development Guide](https://www.odoo.com/documentation/18.0/)
- [Node.js Best Practices](https://nodejs.org/en/docs/guides/)
- [ISO 22301 Standard](https://www.iso.org/standard/75106.html)
- [FAIR Risk Analysis](https://www.fairinstitute.org/)

### Community
- GitHub Issues: [Report bugs and feature requests](https://github.com/SEH-foundation/ISO-22301/issues)
- BCM Community: [Join discussions and share experiences](https://bcm-community.org)
- Training Materials: [Online courses and certifications](https://training.bcm-platform.org)

### Support
- Technical Support: support@bcm-platform.org
- Documentation: docs@bcm-platform.org
- Sales & Partnerships: sales@bcm-platform.org

---

*This documentation is part of the BCM Digital Twin Platform. For the latest updates and detailed API documentation, visit our [official documentation site](https://docs.bcm-platform.org).*