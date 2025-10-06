# WHO Health Emergency and BCM Framework
## Business Continuity for Healthcare Organizations

**Source:** World Health Organization (WHO)
**Framework:** Health Emergency and Disaster Risk Management (Health EDRM)
**Publication:** WHO-WHE-CPI-2018.60

---

## OVERVIEW

Healthcare organizations face unique continuity challenges:
- **Patient safety is paramount** - lives at stake
- **24/7 operations** - no downtime acceptable for critical services
- **Regulatory complexity** - HIPAA, CMS, Joint Commission, local regulations
- **Essential services** - must continue during all hazards
- **Resource constraints** - especially for NPOs and public hospitals

---

## ESSENTIAL HEALTH SERVICES

### Definition
Services that must continue to protect life, prevent disability, and maintain public health.

### WHO Essential Services Framework

#### **TIER 1: IMMEDIATE (RTO: 0 minutes)**

Critical services where any interruption poses immediate risk to life:

1. **Emergency Department**
   - Trauma care
   - Critical stabilization
   - Triage
   - Ambulance services

2. **Intensive Care Unit (ICU/CCU)**
   - Ventilator support
   - Hemodynamic monitoring
   - Critical medication administration

3. **Operating Room (Emergency Surgery)**
   - Life-saving surgical procedures
   - Emergency C-sections

4. **Labor and Delivery (Critical Cases)**
   - High-risk deliveries
   - Emergency obstetric care

**BCM Requirements:**
- Redundant power (generators + UPS)
- Backup medical gas systems
- Alternate water supply
- Emergency medical supplies stockpile
- 24/7 staffing continuity plans
- Immediate failover for critical IT systems (patient monitoring)

---

#### **TIER 2: URGENT (RTO: 2-4 hours)**

Services where delay causes significant patient harm or deterioration:

1. **Laboratory Services**
   - Critical test processing (troponin, blood gases)
   - Blood bank
   - Microbiology (for sepsis diagnosis)

2. **Pharmacy**
   - Medication dispensing
   - IV preparation
   - Controlled substance access

3. **Radiology (Critical Imaging)**
   - CT for stroke/trauma
   - X-ray for acute conditions
   - Ultrasound for emergencies

4. **Dialysis (for admitted patients)**

5. **Blood Bank / Transfusion Services**

**BCM Requirements:**
- Alternative processing locations identified
- Mutual aid agreements with nearby hospitals
- Emergency supply reserves (3-7 days)
- Manual workaround procedures documented
- EHR access for critical patient data

---

#### **TIER 3: IMPORTANT (RTO: 24 hours)**

Services important for ongoing patient care but short delay manageable:

1. **General Inpatient Care**
   - Medical/surgical units
   - Step-down units

2. **Scheduled Surgery (Non-Emergency)**

3. **Outpatient Services**
   - Clinics
   - Specialty consultations

4. **Diagnostic Services**
   - Non-urgent lab tests
   - Non-urgent imaging

5. **Rehabilitation Services**

**BCM Requirements:**
- Patient transfer protocols (to other facilities if needed)
- Rescheduling procedures
- Communication plans for affected patients
- Telehealth alternatives

---

#### **TIER 4: NORMAL (RTO: 3-5 days)**

Services that can be delayed without significant patient impact:

1. **Administrative Functions**
   - Billing
   - Scheduling
   - Medical records (non-emergency)

2. **Elective Procedures**
   - Routine screenings
   - Preventive care

3. **Support Services**
   - Facilities maintenance (non-critical)
   - Laundry (if stockpiles available)

**BCM Requirements:**
- Work from home capabilities
- Backlog management plans
- Communication to patients about delays

---

## HEALTHCARE-SPECIFIC BIA METHODOLOGY

### Impact Assessment Categories

#### 1. **PATIENT SAFETY IMPACT** (Most Critical)

Questions to assess:
- Will loss of this service result in patient death?
- Will it cause permanent disability or serious harm?
- Will it prevent timely treatment of life-threatening conditions?
- Will it compromise infection control or patient safety?

**Rating Scale:**
- **Critical:** Immediate threat to life
- **High:** Serious harm probable within hours
- **Medium:** Harm possible but manageable with workarounds
- **Low:** Inconvenience but no direct patient harm

#### 2. **CLINICAL OUTCOMES IMPACT**

Questions:
- Will treatment delays compromise patient outcomes?
- Will quality of care be significantly reduced?
- Will patient deterioration occur?

**Metrics:**
- Mortality rate impact
- Morbidity increase
- Length of stay increase
- Readmission rate impact

#### 3. **REGULATORY COMPLIANCE IMPACT**

**U.S. Healthcare Regulations:**

- **HIPAA (Health Insurance Portability and Accountability Act)**
  - Patient data privacy and security
  - Breach notification requirements (60 days)
  - Business Associate Agreements (BAA) for continuity vendors

- **CMS (Centers for Medicare & Medicaid Services)**
  - Emergency Preparedness Rule (2016)
  - Requires annual emergency exercises
  - Required policies: risk assessment, continuity plan, communication plan, training

- **Joint Commission Standards**
  - Emergency Management (EM) standards
  - Life Safety Code compliance
  - Sentinel event reporting

- **State/Local Regulations**
  - Public health reporting
  - Disaster response requirements
  - Licensing standards

**Fines and Penalties:**
- HIPAA violations: $100 - $50,000 per violation (up to $1.5M/year)
- CMS: Loss of Medicare/Medicaid reimbursement
- Joint Commission: Accreditation loss

**BCM Evidence Requirements:**
- Emergency operations plan
- Hazard vulnerability assessment (HVA)
- Annual emergency preparedness exercises
- Staff training documentation
- Communication plan

#### 4. **FINANCIAL IMPACT**

**Revenue Loss:**
- Reimbursement loss (Medicare/Medicaid)
- Private payer revenue loss
- Procedure cancellations
- Patient diversion to competitors

**Cost Increase:**
- Overtime for staff
- Emergency supply purchases at premium
- Temporary facility costs
- Patient transfer costs
- Legal and regulatory fines

**NPO Specific:**
- Grant funding at risk
- Donor confidence impact
- Mission delivery failure

**Metrics:**
- Revenue per hour/day of downtime
- Fixed costs continuing during disruption
- Recovery costs
- Insurance deductibles

#### 5. **REPUTATIONAL IMPACT**

**Questions:**
- Will patients lose trust in the facility?
- Will referring physicians divert patients?
- Will media coverage be negative?
- Will community confidence be damaged?

**Especially Critical For:**
- NPOs (rely on donations and community support)
- Public hospitals (community trust essential)
- Teaching hospitals (reputation for quality)

**Long-Term Effects:**
- Patient volume decline
- Physician recruitment challenges
- Difficulty attracting donors/grants

---

## HEALTHCARE RTO/RPO GUIDELINES

### Data Recovery Point Objectives (RPO)

#### **RPO: 0 (Zero Data Loss)**

Systems where any data loss is unacceptable:

- Electronic Health Records (EHR) - patient charts
- Medication Administration Records (MAR)
- Lab results
- Radiology images (PACS)
- Patient monitoring data (ICU)

**Solution:** Real-time replication, synchronous backup

#### **RPO: 1 hour**

Systems where minor data loss acceptable:

- Scheduling systems
- Registration/ADT
- Billing (in-process claims)

**Solution:** Hourly backups, asynchronous replication

#### **RPO: 24 hours**

Systems where data can be recreated:

- Analytics and reporting
- Non-clinical administrative systems

**Solution:** Daily backups

### Recovery Time Objectives (RTO) by System

| System | RTO | Rationale |
|--------|-----|-----------|
| **Patient Monitoring (ICU)** | 0 min | Life support |
| **EHR (Emergency/ICU access)** | 15 min | Critical care decisions |
| **Pharmacy System** | 1 hour | Medication safety |
| **Lab System** | 2 hours | Critical test results |
| **PACS (Radiology)** | 2 hours | Diagnostic imaging |
| **EHR (General access)** | 4 hours | Inpatient care continuity |
| **Registration/ADT** | 8 hours | Can use manual process short-term |
| **Billing** | 24 hours | Can process later |
| **Scheduling** | 24 hours | Can reschedule |

---

## WHO HAZARD FRAMEWORK FOR HEALTHCARE

### All-Hazards Approach

Healthcare BCM must address:

#### **NATURAL HAZARDS**

1. **Pandemic/Epidemic**
   - COVID-19 lessons learned
   - Staff absenteeism (30-40% at peak)
   - Supply chain collapse (PPE, medications)
   - Surge capacity needs

2. **Earthquake**
   - Building structural damage
   - Utility disruption
   - Staff unable to reach facility
   - Patient evacuation needs

3. **Flood/Hurricane**
   - Facility flooding
   - Power loss
   - Evacuation challenges (moving ICU patients)
   - Supply delivery interruption

4. **Extreme Weather**
   - Heat wave (HVAC critical)
   - Winter storm (staff access, heat)

#### **TECHNOLOGICAL HAZARDS**

1. **Cyber Attack / Ransomware**
   - EHR encryption
   - Medical device malware
   - Data breach
   - Growing threat to healthcare

2. **IT System Failure**
   - Server crash
   - Network outage
   - Software bugs
   - Cloud provider outage

3. **Utility Failure**
   - Power (generators tested monthly?)
   - HVAC (infection control, OR requirements)
   - Water (sterilization, dialysis)
   - Medical gas (oxygen, compressed air)

#### **HUMAN HAZARDS**

1. **Workplace Violence**
   - Active shooter
   - Hostage situation
   - Assault on staff

2. **Mass Casualty Incident**
   - Terrorism
   - Transportation accident
   - Building collapse

3. **Staff Shortage**
   - Strike
   - Mass resignation
   - Burnout epidemic

4. **Supplier Failure**
   - Drug shortage (cancer drugs, anesthesia)
   - PPE shortage
   - Single-source dependency

---

## HEALTHCARE CONTINUITY STRATEGIES

### Pre-Incident (Mitigation)

1. **Facility Hardening**
   - Seismic retrofitting
   - Flood barriers
   - Backup generators (72-hour fuel minimum)
   - Multiple utility feeds

2. **Supply Stockpiling**
   - Strategic National Stockpile coordination
   - 3-7 day emergency supplies
   - Pharmaceuticals (expiration management)
   - PPE reserves

3. **Staff Preparedness**
   - Cross-training (staff can work multiple units)
   - "Just-in-time" training for surge
   - Family preparedness (so staff can report to work)
   - Credentialing volunteers (retired nurses, etc.)

4. **System Redundancy**
   - EHR hosted in multiple data centers
   - Backup communication systems
   - Multiple suppliers for critical items

### During-Incident (Response)

1. **Incident Command System (ICS)**
   - Standardized structure (FEMA/NIMS)
   - Hospital Incident Commander
   - Unified command with public health/EMS
   - Clear roles (operations, planning, logistics, finance)

2. **Staff Surge**
   - Cancel elective procedures (frees up staff)
   - Extended shifts (12→16 hours)
   - Recall off-duty staff
   - Activate volunteer pool
   - Request mutual aid

3. **Patient Surge**
   - Discharge stable patients early
   - Cancel elective admissions
   - Convert non-clinical space (cafeteria→treatment area)
   - Expand ICU capacity (2:1 nurse:patient ratio relaxed)
   - Transfer patients to other facilities

4. **Supply Conservation**
   - Crisis standards of care (CDC guidance)
   - PPE reuse protocols (N95 extended use)
   - Medication substitution
   - Rationing criteria (ethics committee)

### Post-Incident (Recovery)

1. **Restoration Prioritization**
   - Restore Tier 1 services first
   - Phased return to normal operations
   - Backlog management (rescheduling)

2. **Debriefing**
   - Hot wash (immediate after-action)
   - Formal after-action report
   - Identify lessons learned
   - Implement improvements

3. **Psychological Support**
   - Staff mental health services (PTSD from crisis)
   - Patient support
   - Family support

4. **Financial Recovery**
   - Insurance claims
   - FEMA reimbursement (if disaster declared)
   - Donor appeals (for NPOs)

---

## WHO EMERGENCY PREPAREDNESS REQUIREMENTS

### Required Plans for Healthcare Facilities

1. **Emergency Operations Plan (EOP)**
   - All-hazards approach
   - Activation criteria
   - Command structure
   - Response procedures
   - Recovery procedures

2. **Communication Plan**
   - Internal communication (staff notification)
   - External communication (public, media, regulators)
   - Patient/family communication
   - Redundant communication methods

3. **Training and Exercise Program**
   - Annual all-hazards exercise (CMS requirement)
   - Tabletop exercises quarterly
   - Staff training (new employees + annual refresher)
   - Drills (fire, evacuation, etc.)

4. **Continuity of Operations Plan (COOP)**
   - Essential services identified
   - RTO/RPO defined
   - Alternate site identified
   - Succession planning

---

## NPO (NON-PROFIT ORGANIZATION) SPECIFIC CONSIDERATIONS

### Unique Challenges for NPOs

1. **Resource Constraints**
   - Limited budget for BC investments
   - Difficulty affording redundant systems
   - Volunteer staff (less reliable during crisis)

2. **Mission Criticality**
   - Serving vulnerable populations
   - Cannot easily turn away patients
   - Community dependence

3. **Funding Vulnerability**
   - Grant funding may be disrupted
   - Donations decline during economic crisis
   - Reimbursement rates lower than for-profit

### NPO BCM Strategies

1. **Collaborative Arrangements**
   - Share resources with other NPOs
   - Mutual aid agreements
   - Consortium purchasing (supplies)
   - Shared backup facilities

2. **Leverage Free/Low-Cost Solutions**
   - Open-source software
   - Cloud services (scalable, lower upfront cost)
   - Volunteer expertise (retired IT professionals)

3. **Donor/Grant Continuity**
   - Diversify funding sources
   - Emergency fund reserve (3-6 months operating expenses)
   - Communication plan for donors during crisis

4. **Mission-Focused Prioritization**
   - Protect core mission services first
   - Scale back non-essential programs during crisis
   - Document impact (for future grant applications)

---

## HEALTHCARE BCM METRICS

### Key Performance Indicators (KPIs)

1. **Preparedness Metrics**
   - % staff completed emergency training
   - % essential services with BC plans
   - Generator test success rate
   - Exercise participation rate

2. **Response Metrics**
   - Time to activate incident command
   - Surge capacity achieved (% over normal)
   - Patient transfer time (during evacuation)

3. **Recovery Metrics**
   - Time to restore Tier 1 services (vs. RTO)
   - Backlog clearance time
   - Financial recovery (insurance reimbursement)

4. **Outcome Metrics**
   - Patient outcomes during crisis (mortality, complications)
   - Regulatory compliance maintained
   - Staff retention after crisis

---

## REFERENCES

- WHO Health Emergency and Disaster Risk Management Framework
- WHO Guidance for Business Continuity Planning (WHO-WHE-CPI-2018.60)
- CMS Emergency Preparedness Rule (2016)
- Joint Commission Emergency Management Standards
- FEMA/NIMS Incident Command System for Healthcare
- CDC Crisis Standards of Care

---

**Document Version:** 1.0
**Date:** 2025-01-20
**Purpose:** Healthcare-specific BCM guidance for platform design
