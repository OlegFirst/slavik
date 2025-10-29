# Exercise Simulators for BCM Platform

Advanced simulation capabilities for Business Continuity Management exercises, integrating JaamSim discrete event simulation and NICS (Next Generation Incident Command System) for comprehensive BCM training and validation.

## 🏗️ Architecture

```
BCM Platform ←→ Simulators Bridge ←→ JaamSim Engine
                     ↕                   ↕
              NICS Integration ←→ NICS Platform
                     ↕
            Real-time WebSocket Updates
```

## 🚀 Features

### ✅ JaamSim Integration
- **Discrete event simulation** for BCM scenarios
- **Process modeling** for business continuity workflows
- **Resource allocation** and constraint modeling
- **Performance metrics** collection and analysis
- **Automated scenario execution** with real-time monitoring

### ✅ NICS Integration
- **Incident command structure** for complex exercises
- **Real-time collaboration** between exercise participants
- **Standard ICS forms** (ICS-201, ICS-202, etc.) for documentation
- **GIS mapping** and resource tracking
- **Multi-agency coordination** capabilities

### ✅ BCM Exercise Types
- **Tabletop exercises** - Discussion-based scenarios
- **Functional exercises** - Operations center activation
- **Full-scale exercises** - Real-time multi-site coordination
- **Simulation exercises** - Discrete event modeling
- **Hybrid exercises** - Combined JaamSim + NICS approach

### ✅ Exercise Management
- **Scenario templates** for common BCM situations
- **Automated inject delivery** during exercises
- **Real-time progress tracking** and performance metrics
- **Participant role management** with RBAC
- **Exercise evaluation** and reporting

## 📦 Components

### 1. JaamSim Client (`jaamsim_client.py`)
- Python interface to JaamSim simulation engine
- BCM-specific scenario creation and modeling
- Automated simulation execution and monitoring
- Results collection and analysis

### 2. NICS Client (`nics_client.py`)
- Integration with NICS incident command platform
- Real-time communication and collaboration
- ICS form management and submission
- WebSocket-based live updates

### 3. Bridge Service (`bridge_service.py`)
- Unified REST API for both simulation engines
- Exercise lifecycle management
- Real-time WebSocket connections for participants
- Background task processing

### 4. Docker Stack (`docker-compose.simulators.yml`)
- Complete simulation environment deployment
- JaamSim with virtual display support
- Optional NICS self-hosted deployment
- Exercise data persistence and management

## 🛠️ Setup & Deployment

### Prerequisites
- Docker & Docker Compose
- Java 11+ (for JaamSim)
- BCM Platform running
- Optional: NICS platform access

### 1. Environment Configuration
```bash
# Copy and configure environment
cp .env.example .env

# Required variables
BRIDGE_API_KEY=your_bridge_api_key
BCM_API_KEY=your_bcm_api_key
NICS_URL=https://your-nics-instance.com  # Optional
NICS_API_KEY=your_nics_api_key          # Optional
EXERCISE_DB_PASSWORD=secure_db_password
```

### 2. Deploy Simulators Stack
```bash
# Start core simulation services
docker-compose -f docker-compose.simulators.yml up -d

# Start with NICS self-hosted (optional)
docker-compose -f docker-compose.simulators.yml --profile nics-selfhosted up -d

# Start with GUI support (optional)
docker-compose -f docker-compose.simulators.yml --profile gui up -d
```

### 3. Verify Deployment
```bash
# Check service health
curl http://localhost:8094/health

# List available simulation engines
curl -H "Authorization: Bearer your_api_key" \
  http://localhost:8094/api/v1/exercises
```

## 🔧 API Usage

### Create BCM Exercise
```bash
POST /api/v1/exercises/create
Authorization: Bearer <bridge-api-key>

{
  "name": "IT System Failure Exercise",
  "description": "Simulated critical IT infrastructure failure",
  "scenario_type": "functional",
  "company_id": "hospital-001",
  "duration_minutes": 240,
  "simulation_engine": "jaamsim",
  "participants": ["bcm_coordinator", "it_manager", "operations_chief"],
  "objectives": [
    "Activate BCM procedures within 30 minutes",
    "Restore critical systems within 4 hours",
    "Communicate with stakeholders effectively"
  ],
  "location": {
    "lat": 40.7128,
    "lng": -74.0060,
    "address": "New York, NY"
  }
}
```

### Start Exercise
```bash
POST /api/v1/exercises/{exercise_id}/start
Authorization: Bearer <bridge-api-key>
```

### Inject Exercise Event
```bash
POST /api/v1/exercises/{exercise_id}/inject
Authorization: Bearer <bridge-api-key>

{
  "exercise_id": "bcm_ex_1640995200",
  "title": "Database Server Failure",
  "description": "Primary database server has experienced hardware failure",
  "event_type": "failure",
  "target_entity": "IT_Infrastructure",
  "requires_response": true,
  "parameters": {
    "severity": "critical",
    "estimated_repair_time": "6 hours",
    "backup_available": true
  }
}
```

### Monitor Exercise Progress
```bash
# Get exercise status
GET /api/v1/exercises/{exercise_id}/status
Authorization: Bearer <bridge-api-key>

# WebSocket connection for real-time updates
ws://localhost:8094/ws/{exercise_id}
```

## 📊 BCM Scenario Templates

### IT System Failure
- **Primary systems**: Database, network, applications
- **Recovery procedures**: Backup activation, failover testing
- **Success criteria**: RTO/RPO compliance, communication effectiveness
- **Metrics**: Response time, system availability, stakeholder satisfaction

### Pandemic Response
- **Remote work activation**: Communication, access management
- **Health protocols**: Safety measures, contact tracing
- **Business continuity**: Essential services, supply chain impact
- **Metrics**: Remote work efficiency, health compliance, service continuity

### Natural Disaster
- **Facility evacuation**: Emergency procedures, alternate sites
- **Communications**: Internal/external stakeholder updates
- **Recovery operations**: Damage assessment, restoration planning
- **Metrics**: Evacuation time, communication reach, recovery progress

### Cyber Security Incident
- **Incident response**: Detection, containment, eradication
- **Communications**: Internal teams, external authorities, customers
- **Recovery**: System restoration, data integrity verification
- **Metrics**: Detection time, containment effectiveness, recovery duration

## 📈 Exercise Analytics

### Performance Metrics
```json
{
  "exercise_id": "bcm_ex_1640995200",
  "duration_minutes": 180,
  "objectives_achieved": 8,
  "objectives_total": 10,
  "response_times": {
    "initial_response": "00:15:30",
    "escalation_decision": "00:32:15", 
    "recovery_initiation": "01:45:20"
  },
  "participant_engagement": 0.87,
  "communication_effectiveness": 0.92,
  "decision_quality_score": 0.85
}
```

### Compliance Tracking
- **ISO 22301** exercise frequency requirements
- **RTO/RPO** achievement during scenarios  
- **Stakeholder notification** timing and effectiveness
- **Documentation completeness** for audit trails

## 🔄 Exercise Workflows

### Tabletop Exercise Flow
1. **Scenario briefing** → Participants receive initial situation
2. **Discussion rounds** → Facilitated problem-solving sessions
3. **Decision points** → Key choices and their implications
4. **Lessons capture** → Documentation of learning outcomes

### Functional Exercise Flow
1. **Scenario initiation** → Automated or manual trigger
2. **Response activation** → BCM procedures implementation
3. **Event injection** → Progressive scenario complications
4. **Performance evaluation** → Real-time metrics collection

### Simulation Exercise Flow
1. **Model initialization** → JaamSim scenario setup
2. **Discrete event processing** → Automated scenario execution
3. **Resource optimization** → Dynamic allocation decisions
4. **Statistical analysis** → Performance distribution analysis

## 🔐 Security & Compliance

### Exercise Data Protection
- **Multi-tenant isolation** by company ID
- **Role-based access control** for participants
- **Audit logging** for all exercise activities
- **Data retention** policies per regulatory requirements

### BCM Standards Compliance
- **ISO 22301** exercise requirements fulfillment
- **NIST Cybersecurity Framework** exercise integration
- **CISA** tabletop exercise guidelines adherence
- **Industry-specific** compliance frameworks support

## 🧪 Testing & Validation

### Unit Tests
```bash
# Test simulation clients
pytest tests/unit/test_jaamsim_client.py
pytest tests/unit/test_nics_client.py

# Test bridge service
pytest tests/unit/test_bridge_service.py
```

### Integration Tests
```bash
# Test end-to-end exercise workflows
pytest tests/integration/test_exercise_workflows.py

# Test real-time communications
pytest tests/integration/test_websockets.py
```

### Performance Tests
```bash
# Test concurrent exercise capacity
pytest tests/performance/test_concurrent_exercises.py

# Test large-scale participant support
pytest tests/performance/test_participant_scaling.py
```

## 🔧 Troubleshooting

### JaamSim Issues
```bash
# Check JaamSim service
docker logs bcm-jaamsim

# Test Java environment
docker exec bcm-jaamsim java -version

# Verify simulation models
docker exec bcm-jaamsim ls -la /opt/jaamsim/templates/
```

### NICS Integration Issues
```bash
# Test NICS connectivity
curl -H "Authorization: Bearer $NICS_API_KEY" \
  $NICS_URL/api/v1/auth/verify

# Check WebSocket connections
docker logs bcm-simulators-bridge | grep -i websocket
```

### Exercise State Issues
```bash
# Check exercise database
docker exec bcm-exercise-postgres psql -U bcm_exercises -d bcm_exercises -c \
  "SELECT * FROM exercises WHERE status = 'active';"

# Verify Redis connections
docker exec bcm-exercise-redis redis-cli ping
```

## 🚀 Production Deployment

### High Availability Setup
- **Multiple bridge instances** with load balancing
- **JaamSim cluster** for parallel simulations
- **NICS redundancy** for critical exercises
- **Database clustering** for exercise data persistence

### Monitoring & Alerting
- **Exercise health monitoring** with custom dashboards
- **Performance metrics** integration with Grafana
- **Alert routing** for exercise failures or issues
- **Participant activity tracking** for engagement analytics

---

## 📚 Additional Resources

- [JaamSim Documentation](https://jaamsim.com/docs/)
- [NICS Platform Guide](https://www.fema.gov/emergency-managers/practitioners/nics)
- [ISO 22301 Exercise Requirements](https://www.iso.org/standard/75106.html)
- [BCM Exercise Best Practices](../../../docs/exercises/)
