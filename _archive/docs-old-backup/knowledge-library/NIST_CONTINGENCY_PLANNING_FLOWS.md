# NIST SP 800-34 Contingency Planning Flows
**Source:** NIST Special Publication 800-34 Rev. 1 - Contingency Planning Guide for Federal Information Systems
**Date:** 2025-10-08
**Status:** Knowledge base - IT/Cyber continuity flows

---

## Overview

### What is NIST SP 800-34?

**NIST SP 800-34** is the US federal government's standard for **IT contingency planning** for information systems. While ISO 22301 is business-focused, NIST is IT/cybersecurity-focused.

**Key Differences from ISO 22301:**
- **Focus:** IT systems, data, and infrastructure (vs. business processes)
- **Scope:** Information system recovery (vs. organizational continuity)
- **Audience:** IT managers, CISOs, system owners (vs. BCM managers, executives)
- **Compliance:** US Federal agencies (FISMA) (vs. international certification)

---

## NIST 7-Step Contingency Planning Lifecycle

### Flow 1: NIST 7-Step CP Process

**Purpose:** Systematic approach to IT contingency planning

**7 Steps:**

1. **Develop contingency planning policy**
   - Define CP roles and responsibilities
   - Establish testing frequency
   - Set maintenance schedules
   - Assign coordination requirements

2. **Conduct Business Impact Analysis (BIA)**
   - Identify critical IT systems and components
   - Determine maximum tolerable downtimes (MTD)
   - Identify resource requirements
   - Establish recovery priorities

3. **Identify preventive controls**
   - Implement controls to reduce system disruption
   - Redundancy, fault tolerance, RAID arrays
   - Uninterruptible Power Supply (UPS)
   - Environmental controls

4. **Create contingency strategies**
   - Backup strategies (full, incremental, differential)
   - Alternative site strategies (hot, warm, cold)
   - Equipment replacement strategies
   - Roles and responsibilities

5. **Develop IT contingency plan**
   - Write formal contingency plan document
   - Include supporting information
   - Notification/activation procedures
   - Recovery procedures
   - Reconstitution procedures

6. **Test, train, and exercise**
   - Test plan procedures
   - Train personnel on roles
   - Conduct tabletop exercises
   - Conduct functional exercises
   - Conduct full-scale exercises

7. **Maintain plan**
   - Update plan regularly
   - Incorporate lessons learned
   - Reflect system changes
   - Review after tests/actual events

**NIST-Specific:** Emphasizes technical controls (backups, redundancy) more than ISO's business process focus.

---

## IT-Specific Contingency Flows

### Flow 2: Data Backup and Recovery Strategy

**Purpose:** Ensure data availability and recoverability

**Process:**

**Phase 1: Backup Strategy Selection**
- **Full backup** (complete data copy, time-consuming, high storage)
- **Incremental backup** (only changed data since last backup)
- **Differential backup** (changed data since last full backup)

**Phase 2: Backup Frequency Determination**
```
Based on:
- Data criticality
- Data change rate
- Recovery Point Objective (RPO)
- Storage capacity

Example:
- Critical databases: Full weekly + Incremental daily
- File servers: Full monthly + Differential weekly
- Workstations: Full quarterly
```

**Phase 3: Backup Verification**
- Test restore procedures monthly
- Verify backup integrity
- Document restoration times
- Update Recovery Time Objectives (RTOs)

**Phase 4: Offsite Storage**
- Store backups at alternate location
- Minimum 50-100 miles from primary
- Secure transport procedures
- Access controls at storage site

**NIST-Specific:** Technical backup methodologies vs. ISO's business data requirements.

---

### Flow 3: Alternative Site Selection and Setup

**Purpose:** Establish alternate processing facility for IT systems

**3 Alternative Site Types:**

**Type 1: Cold Site**
- **Setup:** Basic infrastructure (space, power, HVAC)
- **Activation time:** Days to weeks
- **Cost:** Low ($500-5,000/month)
- **Use case:** Non-critical systems, budget constraints

**Type 2: Warm Site**
- **Setup:** Infrastructure + hardware, no current data
- **Activation time:** Hours to days
- **Cost:** Medium ($10,000-50,000/month)
- **Use case:** Moderately critical systems

**Type 3: Hot Site**
- **Setup:** Fully operational, real-time data replication
- **Activation time:** Minutes to hours
- **Cost:** High ($50,000-200,000/month)
- **Use case:** Mission-critical systems, 24/7 operations

**Flow Process:**
1. Determine criticality of IT systems (from BIA)
2. Match criticality to site type (Critical → Hot, Medium → Warm, Low → Cold)
3. Establish contract with site provider
4. Test connectivity and access quarterly
5. Update runbooks for site-specific procedures

**NIST-Specific:** Technical infrastructure alternatives vs. ISO's business facility alternatives.

---

### Flow 4: IT System Recovery Procedures

**Purpose:** Step-by-step recovery of IT infrastructure

**Process (by layer):**

**Layer 1: Network Infrastructure Recovery (Hours 0-2)**
```
1. Assess network connectivity at alternate site
2. Establish VPN tunnels to primary datacenter (if accessible)
3. Configure routing and firewall rules
4. Verify DNS and DHCP services
5. Test connectivity to critical systems
```

**Layer 2: Server Infrastructure Recovery (Hours 2-8)**
```
1. Power on essential servers (Domain Controllers, DNS, DHCP)
2. Verify Active Directory replication
3. Restore application servers from backups
4. Verify database integrity
5. Start application services
```

**Layer 3: Application Recovery (Hours 8-24)**
```
1. Restore application configurations
2. Connect to recovered databases
3. Verify application functionality
4. Test critical business workflows
5. Enable user access
```

**Layer 4: Data Recovery (Hours 24-48)**
```
1. Restore latest full backup
2. Apply incremental/differential backups
3. Verify data consistency
4. Reconcile transactions since last backup
5. Validate data integrity
```

**NIST-Specific:** Technical recovery sequence vs. ISO's business process resumption.

---

### Flow 5: Incident Response Integration

**Purpose:** Integrate IT contingency with cybersecurity incident response

**Process:**

**Decision Point: Incident Type**
```
IF incident is:
  - Natural disaster → Activate IT Contingency Plan
  - Cyber attack → Activate Incident Response Plan
  - Both (e.g., ransomware) → Activate BOTH plans in coordination
```

**Coordinated Response Flow:**
1. **Incident Detection and Analysis** (IR + CP)
   - Security team: Determine attack vector, scope
   - IT team: Assess system availability and data integrity

2. **Containment** (IR focus)
   - Isolate affected systems
   - Prevent lateral movement
   - Preserve evidence for forensics

3. **Eradication** (IR focus)
   - Remove malware/attacker access
   - Patch vulnerabilities
   - Reset credentials

4. **Recovery** (CP focus)
   - Restore systems from clean backups
   - Verify system integrity
   - Resume business operations

5. **Post-Incident Activities** (Both)
   - Lessons learned
   - Update IR plan
   - Update CP plan
   - Implement preventive controls

**NIST-Specific:** IT incident response integration (NIST 800-61) with contingency planning (800-34).

---

## Federal Compliance Workflows

### Flow 6: FISMA Compliance Integration

**Purpose:** Ensure IT contingency planning meets Federal Information Security Management Act (FISMA) requirements

**Process:**

**Annual FISMA Reporting Cycle:**
1. **Q1: Plan Review and Update**
   - Review CP plan annually
   - Incorporate system changes
   - Update contact lists
   - Document changes

2. **Q2: BIA Update**
   - Re-assess IT system criticalities
   - Update MTDs and RTOs
   - Validate resource requirements

3. **Q3: Testing**
   - Conduct CP test or exercise
   - Document results
   - Identify corrective actions

4. **Q4: Reporting**
   - Submit FISMA metrics
   - Report CP test results
   - Document plan maintenance
   - Submit to management

**FISMA Requirements:**
- CP plan documented and approved
- Annual testing requirement
- Training requirements
- Plan maintenance procedures

**NIST-Specific:** Federal compliance workflow not present in ISO 22301.

---

### Flow 7: System Categorization and Recovery Priority

**Purpose:** Determine recovery priorities using FIPS 199 categorization

**Process:**

**Step 1: FIPS 199 Categorization**
```
For each IT system, assess impact of loss:
- Confidentiality impact (Low/Moderate/High)
- Integrity impact (Low/Moderate/High)
- Availability impact (Low/Moderate/High)

System Category = MAX(C, I, A)
```

**Step 2: Map to Recovery Priority**
```
High impact systems:
  - Priority 1 (0-24 hours recovery)
  - Hot site or real-time replication
  - Daily backups minimum

Moderate impact systems:
  - Priority 2 (24-72 hours recovery)
  - Warm site acceptable
  - Weekly backups

Low impact systems:
  - Priority 3 (72+ hours recovery)
  - Cold site or manual procedures
  - Monthly backups
```

**Step 3: Document in Contingency Plan**
- List systems by priority
- Assign recovery teams by priority
- Define recovery sequences

**NIST-Specific:** FIPS 199 security categorization methodology not in ISO 22301.

---

## Testing and Exercise Protocols

### Flow 8: NIST CP Testing Methodology

**Purpose:** Validate IT contingency plan effectiveness

**5 Testing Methods (in order of complexity):**

**Method 1: Checklist Review (Monthly)**
- Review plan procedures
- Verify contact lists current
- Check backup logs
- Time: 2-4 hours
- Disruption: None

**Method 2: Tabletop Exercise (Quarterly)**
- Discuss hypothetical scenario
- Walk through recovery procedures
- Identify gaps and issues
- Time: 4-8 hours
- Disruption: None

**Method 3: Functional Exercise (Semi-Annual)**
- Simulate recovery without actual system outage
- Test notification procedures
- Validate communication channels
- Time: 8-16 hours
- Disruption: Minimal

**Method 4: Parallel Test (Annual)**
- Recover systems at alternate site
- Run in parallel with production
- Validate full recovery capability
- Time: 24-48 hours
- Disruption: None to production

**Method 5: Full Interruption Test (Every 2-3 years)**
- Shut down production systems
- Fully activate contingency plan
- Operate from alternate site
- Time: 48-72 hours
- Disruption: High (planned)

**Testing Flow:**
```
Year 1: Tabletop (Q1, Q3) + Functional (Q2) + Parallel (Q4)
Year 2: Tabletop (Q1, Q3) + Functional (Q2) + Full Interruption (Q4)
Year 3: Repeat Year 1
```

**NIST-Specific:** Progressive testing approach from low to high risk.

---

## Plan Maintenance Flows

### Flow 9: Change Management Integration

**Purpose:** Keep IT contingency plan synchronized with system changes

**Triggers for Plan Update:**

**Trigger 1: System Changes**
- New system deployed → Add to BIA, update recovery procedures
- System decommissioned → Remove from plan
- Major upgrade → Re-test recovery procedures
- Architecture change → Update dependencies

**Trigger 2: Organizational Changes**
- Personnel changes → Update contact lists, roles
- Vendor changes → Update contracts, procedures
- Location changes → Update alternate sites

**Trigger 3: Test/Exercise Results**
- Failed recovery → Update procedures
- Longer than expected RTO → Revise strategy
- New issues identified → Add corrective actions

**Trigger 4: Actual Incidents**
- After-action review findings → Update plan
- New threats identified → Add preventive controls
- Lessons learned → Incorporate improvements

**Update Process:**
1. Document change in change log
2. Update relevant plan sections
3. Increment version number
4. Notify plan holders
5. Conduct training if significant changes
6. Re-test affected procedures

**NIST-Specific:** Integration with IT change management (ITIL) processes.

---

### Flow 10: Continuity of Operations (COOP) Integration

**Purpose:** Coordinate IT contingency with agency-wide COOP planning

**COOP vs. IT Contingency:**
- **COOP:** Organization-wide continuity (mission essential functions)
- **IT CP:** IT systems supporting those functions

**Integration Flow:**

**Step 1: Identify Mission Essential Functions (MEFs)**
- Agency leadership defines MEFs (e.g., "Process citizen benefits")
- Duration: Functions that must continue within 12 hours

**Step 2: Map IT Systems to MEFs**
```
Example:
- MEF: "Process citizen benefits"
  → IT Systems: Benefits database, payment system, citizen portal
  → Recovery Priority: High (all must be recovered within 12 hours)
```

**Step 3: Align Recovery Objectives**
```
If COOP requires MEF within 12 hours:
  → IT systems supporting MEF must have RTO ≤ 12 hours
  → Alternative site: Hot site
  → Backup frequency: Daily minimum
```

**Step 4: Coordinate Activation**
- COOP activation triggers IT contingency for MEF systems
- Unified incident command structure
- Coordinated communications

**Step 5: Test Integration**
- Conduct combined COOP + IT CP exercises
- Validate coordination procedures
- Test communication channels

**NIST-Specific:** Federal COOP framework integration not in ISO 22301.

---

## Additional NIST Flows (IT-Specific)

### Flow 11: Cryptographic Key Recovery

**Purpose:** Ensure cryptographic keys are recoverable after disaster

**Process:**
1. **Identify Critical Keys**
   - Encryption keys (data at rest)
   - SSL/TLS certificates
   - Code signing keys
   - Authentication keys

2. **Establish Key Escrow**
   - Secure key storage (Hardware Security Module)
   - Split-knowledge procedures (multiple custodians)
   - Offsite backup of key escrow

3. **Document Recovery Procedures**
   - Key retrieval authorization
   - Key restoration steps
   - Verification procedures

4. **Test Key Recovery**
   - Quarterly key recovery drills
   - Verify decryption/signing capability

**NIST-Specific:** Cryptographic considerations not addressed in ISO 22301.

---

### Flow 12: Cloud Service Contingency

**Purpose:** IT contingency for cloud-based systems (IaaS, PaaS, SaaS)

**Process:**

**For IaaS (Infrastructure as a Service):**
- VM snapshots and replication
- Region-to-region failover
- Disaster recovery automation (Azure Site Recovery, AWS DR)

**For PaaS (Platform as a Service):**
- Application-level backups
- Multi-region deployment
- Database geo-replication

**For SaaS (Software as a Service):**
- Data export procedures (weekly minimum)
- Vendor SLA review (verify RTO commitments)
- Alternate SaaS provider evaluation (contingency if primary fails)

**Cloud-Specific Considerations:**
- Verify cloud provider's DR capabilities
- Test data portability (avoid vendor lock-in)
- Understand shared responsibility model
- Document cloud provider contact procedures

**NIST-Specific:** Cloud contingency flows (NIST 800-146, 800-190) not in 2012-era ISO 22301.

---

## How NIST Complements ISO 22301

### What NIST Adds:

| Aspect | ISO 22301 | NIST SP 800-34 |
|--------|-----------|----------------|
| **Focus** | Business processes | IT systems and data |
| **BIA** | Business impact | IT system impact |
| **Recovery** | Resume business operations | Restore IT infrastructure |
| **Strategies** | Business workarounds | Technical redundancy (RAID, clustering) |
| **Testing** | Exercise scenarios | Technical recovery tests |
| **Personnel** | Business roles | IT technical roles |
| **Backups** | Business data | System images, databases, configurations |
| **Alternative** | Work locations | Datacenters (hot/warm/cold sites) |

### Integration Approach:

**Use ISO 22301 for:**
- Overall BCM strategy and governance
- Business impact analysis (process level)
- Business continuity strategies
- Organization-wide exercises
- Management review and improvement

**Use NIST SP 800-34 for:**
- IT system BIA (technical level)
- Data backup and recovery strategies
- IT infrastructure alternatives (sites)
- Technical recovery procedures
- IT-specific testing

**Combined Flow:**
```
1. ISO BIA identifies critical business process
2. NIST BIA identifies IT systems supporting that process
3. ISO defines business recovery time objective (e.g., 24 hours)
4. NIST defines IT recovery time objective (must be ≤ business RTO)
5. ISO develops business continuity strategy (e.g., work from home)
6. NIST develops IT contingency strategy (e.g., hot site, VPN)
7. Test both together in integrated exercise
```

---

## Key Takeaways: NIST for BCM Platform

### 1. IT-Specific Flows to Add to Platform:

The platform should support:
- **IT System BIA** (separate from business process BIA)
- **Data backup strategy selection** (full/incremental/differential)
- **Alternative site selection** (hot/warm/cold with cost/RTO tradeoffs)
- **Technical recovery procedures** (network → servers → apps → data)
- **Cloud service contingency planning**

### 2. Technical Recovery Templates:

Add to platform:
- Server recovery runbooks
- Network restoration checklists
- Database recovery procedures
- Application restoration steps

### 3. IT-Specific Testing:

Support NIST testing methods:
- Parallel testing (run at alternate site without disrupting production)
- Technical validation (can we actually restore from backups?)

### 4. Integration with Cybersecurity:

- Link IT CP with incident response plans
- Ransomware recovery workflows (combine IR + CP)
- Cryptographic key recovery procedures

### 5. Cloud-Native Considerations:

- Multi-region deployment strategies
- Vendor SLA validation
- Data portability and export procedures

---

## NIST Flows Summary

**Total NIST-Specific Flows: 12**

1. NIST 7-Step CP Lifecycle
2. Data Backup and Recovery Strategy
3. Alternative Site Selection
4. IT System Recovery Procedures (4 layers)
5. Incident Response Integration
6. FISMA Compliance Integration
7. System Categorization (FIPS 199)
8. NIST CP Testing Methodology (5 methods)
9. Change Management Integration
10. COOP Integration
11. Cryptographic Key Recovery
12. Cloud Service Contingency

**These flows ADD to ISO 22301 by providing:**
- Technical depth for IT contingency
- Federal compliance workflows
- Cloud and cybersecurity integration
- Detailed recovery procedures for IT infrastructure

---

**Next Steps:**
- Integrate NIST flows into platform's IT/technical continuity modules
- Add IT-specific BIA templates
- Create technical recovery runbooks
- Link with cybersecurity incident response workflows

**For organizations needing both:**
- Use ISO 22301 for business continuity governance
- Use NIST SP 800-34 for IT contingency technical details
- Integrate both in unified BCMS platform
