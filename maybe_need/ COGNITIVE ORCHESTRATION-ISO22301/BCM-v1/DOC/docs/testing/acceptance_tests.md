# BCM Platform - Acceptance Test Scenarios

## Test Environment Setup

### Prerequisites
- Docker Compose services running (EventBus, Orchestrator, Odoo)
- Test tenant: `demo_hospital`
- Test users: Admin (`bcm_manager`), Portal user (`bcm_portal`)
- Sample data: Processes, incidents, BIA records

### Service Health Check
```bash
# Test all services are responding
curl http://localhost:8001/health  # EventBus
curl http://localhost:8002/health  # Orchestrator  
curl http://localhost:8069/web/health  # Odoo
curl http://localhost:8081/  # Frontend
```

## Test Scenarios

### Scenario 1: Multi-Tenancy Isolation

**Objective**: Verify tenant data isolation across all BCM models

**Test Steps**:
1. Login as Company A user
2. Create business process "HR System"
3. Create incident "Data Breach"  
4. Switch to Company B user
5. Verify Company A data is not visible
6. Create business process "Finance System"
7. Verify only Company B data visible

**Expected Results**:
- ✅ Users see only their company's data
- ✅ Cross-tenant data access blocked
- ✅ API endpoints respect company_id filtering

**SQL Verification**:
```sql
-- All BCM records should have company_id
SELECT table_name FROM information_schema.tables 
WHERE table_name LIKE 'bcm_%';

-- Check company_id presence
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'bcm_business_process' AND column_name = 'company_id';
```

### Scenario 2: Event-Driven Workflow (BIA → BCP Generation)

**Objective**: Test complete PDCA workflow from BIA completion to BCP generation

**Test Steps**:
1. Login to Odoo BCM module
2. Navigate to Business Process "EHR System"
3. Click "Compute BIA" button
4. Verify BIA calculation completes (RTO: 2 hours, RPO: 30 min)
5. Check EventBus receives `bcm.bia.completed` event
6. Verify Orchestrator creates AI decision for BCP generation
7. Login to web portal `/orchestrator`
8. Approve BCP generation decision
9. Verify plan draft created in Odoo
10. Check `bcm.plan.draft_generated` event published

**Expected Results**:
- ✅ BIA calculation triggers external engine call
- ✅ Event published with correct tenant_id and payload
- ✅ Orchestrator receives event and creates decision
- ✅ Web portal shows pending decision with 92% confidence
- ✅ Plan draft generated with AI-recommended steps
- ✅ Audit trail maintained for all decisions

**Event Verification**:
```bash
# Check event history
curl "http://localhost:8001/api/events/history?tenant_id=demo_hospital&event_type=bcm.bia.completed"

# Check pending decisions
curl "http://localhost:8002/api/ai/decisions/pending?tenant_id=demo_hospital"
```

### Scenario 3: Real-time Event Monitoring

**Objective**: Verify SSE/WebSocket event streaming in web portal

**Test Steps**:
1. Open web portal `/events`
2. Verify SSE connection established
3. Create new incident in Odoo
4. Verify `bcm.incident.opened` appears in real-time
5. Filter events by type "incident"
6. Expand event details to inspect payload
7. Export event history as JSON

**Expected Results**:
- ✅ SSE connection established within 2 seconds
- ✅ Events appear in real-time (<1 second delay)
- ✅ Event filtering works correctly
- ✅ Payload inspection shows complete data structure
- ✅ Export functionality generates valid JSON
- ✅ Connection auto-reconnects on failure

**Browser Console Check**:
```javascript
// EventSource connection active
console.log(window.eventSource?.readyState); // Should be 1 (OPEN)

// Check event listeners
console.log(window.eventListeners?.length); // Should be > 0
```

### Scenario 4: KPI Dashboard Integration

**Objective**: Test KPI calculation and real-time dashboard updates

**Test Steps**:
1. Login to web portal `/overview`
2. Verify KPI widgets show current metrics
3. Navigate to Odoo KPI Calculator
4. Click "Calculate KPIs" action
5. Verify web portal updates in real-time
6. Check KPI values: BIA Coverage, Plans Up-to-date, CAPA On-time
7. Verify KPI thresholds trigger notifications

**Expected Results**:
- ✅ KPI endpoint returns valid JSON data
- ✅ Dashboard widgets display metrics correctly
- ✅ Real-time updates via `bcm.kpi.calculated` event
- ✅ Threshold breaches trigger visual alerts
- ✅ KPI calculations mathematically correct
- ✅ Historical trending data available

**API Test**:
```bash
# Test KPI endpoint
curl -X POST "http://localhost:8069/bcm/kpi/calculate" \
  -H "Content-Type: application/json" \
  -d '{"period": "Q3 2024"}'

# Verify response format
curl "http://localhost:8069/bcm/kpi" | jq '.data'
```

### Scenario 5: AI Orchestrator Decision Flow

**Objective**: Test complete AI decision workflow

**Test Steps**:
1. Create critical incident (severity: critical)
2. Verify Orchestrator creates response decision
3. Login to web portal `/orchestrator`
4. Review decision details and confidence score
5. Click "Approve" with custom parameters
6. Verify incident updated with response checklist
7. Check decision audit trail
8. Test decision rejection workflow

**Expected Results**:
- ✅ Critical incidents auto-trigger response decisions
- ✅ Decision confidence scores displayed (85-95%)
- ✅ Approval executes recommended actions
- ✅ Rejection requires reason and logs appropriately
- ✅ Decision history maintained with timestamps
- ✅ Failed decisions retry with backoff

### Scenario 6: Portal Evidence Upload

**Objective**: Test document management and audit evidence workflow

**Test Steps**:
1. Login to Odoo Portal as external user
2. Navigate to BCM Portal section
3. Click "Upload Evidence" for Q3 Audit
4. Upload PDF document (ISO certificate)
5. Add metadata: type, description, tags
6. Verify document stored in bcm.client.vault
7. Check event `bcm.evidence.uploaded` published
8. Verify document analysis triggers

**Expected Results**:
- ✅ File upload completes successfully
- ✅ Metadata correctly stored and indexed
- ✅ Tenant isolation maintained for documents
- ✅ Event published with document metadata
- ✅ Document analysis queued for processing
- ✅ Audit trail records upload activity

### Scenario 7: Service Configuration Management

**Objective**: Test BCM configuration and service connectivity

**Test Steps**:
1. Login to Odoo as BCM Manager
2. Navigate to BCM Settings configuration
3. Update EventBus URL to invalid endpoint
4. Click "Test Connection" button
5. Verify error status displayed
6. Restore correct URL and test again
7. Enable/disable webhooks and test event publishing
8. Configure webhook authentication

**Expected Results**:
- ✅ Connection tests accurately reflect service status
- ✅ Invalid configurations properly handled
- ✅ Webhook enable/disable affects event publishing
- ✅ Authentication headers included in requests
- ✅ Configuration changes apply immediately
- ✅ Service status cached and updated periodically

## Performance Tests

### Load Test: Event Publishing
- Simulate 100 concurrent BIA calculations
- Verify all events processed within SLA (5 seconds)
- Check EventBus handles burst traffic
- Monitor Redis pub/sub performance

### Stress Test: Dashboard Widgets  
- Load 50 concurrent users on overview dashboard
- Verify SSE connections remain stable
- Check KPI calculations under load
- Monitor memory usage and response times

### Integration Test: End-to-End Workflow
- Execute complete PDCA cycle for 10 processes
- Measure total workflow completion time
- Verify no events lost or duplicated
- Check data consistency across services

## Security Tests

### Authentication Tests
- Verify JWT token validation
- Test session timeout handling
- Check user role enforcement
- Validate portal access controls

### Authorization Tests  
- Verify tenant isolation under load
- Test admin route protection
- Check API endpoint authorization
- Validate webhook authentication

### Data Protection Tests
- Verify sensitive data encryption
- Test API key security
- Check audit log integrity
- Validate backup/restore procedures

## Browser Compatibility

### Desktop Testing
- Chrome 120+ (primary)
- Firefox 119+ (secondary)
- Safari 17+ (secondary)
- Edge 119+ (secondary)

### Mobile Testing
- iOS Safari (responsive)
- Chrome Mobile (responsive)
- Samsung Internet (basic)

### Feature Support
- Server-Sent Events (SSE)
- WebSocket connections
- JavaScript ES6+ modules
- CSS Grid and Flexbox
- Local Storage API

## Acceptance Criteria Summary

### Functional Requirements ✅
- [ ] Multi-tenancy enforced across all models
- [ ] Real-time event streaming operational
- [ ] AI decision workflow complete
- [ ] KPI dashboard functional
- [ ] Document upload/analysis working
- [ ] Configuration management operational

### Performance Requirements ✅
- [ ] Event publishing < 500ms average
- [ ] Dashboard loads < 2 seconds
- [ ] SSE connection established < 1 second
- [ ] KPI calculations < 5 seconds
- [ ] 100 concurrent users supported

### Security Requirements ✅
- [ ] Tenant data isolation verified
- [ ] Authentication/authorization enforced
- [ ] API endpoints secured
- [ ] Audit trails maintained
- [ ] Data encryption validated

### Integration Requirements ✅
- [ ] Odoo integration functional
- [ ] EventBus communication stable
- [ ] Orchestrator decisions working
- [ ] Portal uploads operational
- [ ] Configuration sync active

## Test Data Sets

### Sample Companies
1. **demo_hospital** - Healthcare, 500+ employees, High criticality
2. **test_bank** - Financial, 1000+ employees, Critical systems
3. **sample_factory** - Manufacturing, 200+ employees, Supply chain focus

### Sample Processes
1. **Electronic Health Records** - RTO: 2 hours, RPO: 30 minutes
2. **Core Banking System** - RTO: 1 hour, RPO: 15 minutes  
3. **Production Line Control** - RTO: 4 hours, RPO: 2 hours

### Sample Incidents
1. **Data Center Outage** - Critical severity, Infrastructure
2. **Cyber Security Breach** - High severity, Information
3. **Supply Chain Disruption** - Medium severity, External

## Reporting

### Test Execution Report
- Test case pass/fail status
- Performance metrics summary
- Security validation results
- Browser compatibility matrix
- Known issues and limitations

### Sign-off Requirements
- [ ] BCM Manager approval
- [ ] IT Operations approval  
- [ ] Security Team approval
- [ ] End User Representative approval
- [ ] Compliance Officer approval
