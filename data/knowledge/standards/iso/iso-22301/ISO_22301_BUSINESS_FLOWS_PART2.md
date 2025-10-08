# ISO 22301:2019 - Complete Business Process Flows Analysis (Part 2)

**Continuation of:** ISO_22301_BUSINESS_FLOWS.md
**This document contains:** Clauses 7-10 and Cross-Cutting Flows

---

# CLAUSE 7: SUPPORT

**PDCA Phase:** PLAN (Supporting elements)
**Purpose:** Provide resources and support necessary for BCMS effectiveness

---

## FLOW 7.1: RESOURCE DETERMINATION AND ALLOCATION

**ISO Clause:** 7.1 - Resources
**Type:** MANDATORY
**Frequency:** Annual planning + ongoing as needed
**BCI Practice:** PP1 (Establishing BCMS) + PP2 (Embracing BC)

### Flow Description:
Determine and provide resources needed for establishment, implementation, maintenance, and continual improvement of BCMS.

### Trigger Conditions:
- Initial BCMS implementation
- Annual budget planning
- BCMS scope expansion
- New BC initiatives/projects
- Resource inadequacy identified
- Management review decisions

### Process Steps:

```
1. IDENTIFY RESOURCE REQUIREMENTS

   ├─ PEOPLE resources:
   │  ├─ BC Manager/Coordinator (dedicated or allocated time)
   │  ├─ BC team members (FTEs or % allocation)
   │  ├─ Process owners (time for BC activities)
   │  ├─ Recovery team members
   │  ├─ Exercise participants
   │  └─ Training time for all staff
   │
   ├─ FINANCIAL resources:
   │  ├─ BC programme budget (operational)
   │  ├─ BC strategy implementation (capital)
   │  ├─ Training budget
   │  ├─ Exercise budget
   │  ├─ Consultant/external support
   │  ├─ BC tools/software licenses
   │  ├─ Recovery resources (alternate sites, supplies)
   │  └─ Insurance premiums
   │
   ├─ INFRASTRUCTURE resources:
   │  ├─ Office space for BC team
   │  ├─ Emergency operations center (EOC)
   │  ├─ Backup/alternate facilities
   │  ├─ Communication systems (redundant)
   │  └─ Emergency supplies
   │
   ├─ TECHNOLOGY resources:
   │  ├─ BC management platform/software
   │  ├─ BIA/risk assessment tools
   │  ├─ Document management system
   │  ├─ Incident management tools
   │  ├─ Emergency notification system
   │  ├─ Backup and recovery systems (IT DR)
   │  └─ Monitoring and alerting tools
   │
   └─ INFORMATION resources:
      ├─ BC knowledge base
      ├─ Standards and guidelines
      ├─ Training materials
      ├─ External intelligence (threat data)
      └─ Benchmark data

2. ASSESS CURRENT RESOURCES
   ├─ What resources are currently available?
   ├─ Are they adequate and appropriate?
   ├─ Gaps between required and available?
   └─ Resource utilization efficiency

3. PRIORITIZE RESOURCE NEEDS
   ├─ Critical/mandatory resources (first priority)
   ├─ Important resources (second priority)
   ├─ Desirable resources (when budget allows)
   └─ Cost-benefit consideration

4. DEVELOP RESOURCE PLAN
   ├─ Phased acquisition (if needed)
   ├─ Budget request documentation
   ├─ Justification (business case)
   ├─ Timeline for resource allocation
   └─ Approval requirements

5. OBTAIN APPROVALS
   ├─ Budget approval (finance/senior management)
   ├─ Personnel allocation (HR/line managers)
   ├─ Infrastructure approval (facilities, IT)
   └─ Procurement approvals

6. ALLOCATE RESOURCES
   ├─ Assign budget to BC activities
   ├─ Assign personnel to BC roles
   ├─ Acquire technology/tools
   ├─ Establish infrastructure
   └─ Document allocations

7. MONITOR RESOURCE ADEQUACY
   ├─ Are resources sufficient?
   ├─ Are resources being used effectively?
   ├─ Any resource constraints impacting BCMS?
   └─ Report issues to management

8. ADJUST RESOURCES
   ├─ Respond to changing needs
   ├─ Reallocate as necessary
   └─ Request additional resources if needed
```

### Expected Outputs:
- Resource requirements document
- Budget proposals and approvals
- Personnel allocation records
- Resource inventory (tools, infrastructure)
- Resource adequacy assessment
- Resource utilization reports

### Success Criteria:
- Resource needs identified comprehensively
- Adequate resources allocated
- Resources available when needed
- Resource adequacy monitored
- Adjustments made as necessary

### Dependencies:
- **Input from:** All BCMS processes (resource needs)
- **Enables:** All BCMS activities

### Related Platform Services:
- `governance-service` (resource management)
- `planning_service` (budget tracking)

### Flow Pattern:
- **Type:** Annual planning → Continuous monitoring
- **Feedback Loop:** Adequacy monitoring → Adjustments

---

## FLOW 7.2: COMPETENCE MANAGEMENT

**ISO Clause:** 7.2 - Competence
**Type:** MANDATORY
**Frequency:** Continuous (assess → train → verify)
**BCI Practice:** PP2 (Embracing BC)

### Flow Description:
Determine necessary competence for BC roles, ensure persons are competent, and take actions to acquire and maintain competence.

### Trigger Conditions:
- New BC roles defined
- New personnel assigned to BC roles
- Competence gaps identified
- Annual training planning
- Regulatory/standard changes
- Technology changes
- Exercise/incident lessons learned

### Process Steps:

```
1. DETERMINE REQUIRED COMPETENCE

   For each BC role:
   ├─ BC Manager/Coordinator:
   │  ├─ ISO 22301 knowledge
   │  ├─ BIA/risk assessment skills
   │  ├─ BC planning expertise
   │  ├─ Exercise design and facilitation
   │  ├─ Project management
   │  ├─ Leadership and communication
   │  └─ Industry-specific BC knowledge
   │
   ├─ Incident Management Team:
   │  ├─ Incident command system (ICS)
   │  ├─ Decision-making under pressure
   │  ├─ Crisis communication
   │  ├─ Coordination skills
   │  └─ Specific incident response procedures
   │
   ├─ Recovery Team Leaders:
   │  ├─ Process-specific recovery procedures
   │  ├─ Team leadership
   │  ├─ Problem-solving
   │  └─ Status reporting
   │
   ├─ Process Owners:
   │  ├─ BIA participation
   │  ├─ Recovery strategy selection
   │  ├─ Plan development for their process
   │  └─ Exercise participation
   │
   └─ All Employees:
      ├─ BC awareness (what is BC?)
      ├─ Individual responsibilities
      ├─ How to report incidents
      ├─ Basic emergency response
      └─ Location-specific procedures

2. CREATE COMPETENCY MATRIX
   ├─ List all BC roles (rows)
   ├─ List required competencies (columns)
   ├─ Define proficiency levels:
   │  ├─ 1 = Awareness
   │  ├─ 2 = Working knowledge
   │  ├─ 3 = Proficient
   │  └─ 4 = Expert
   └─ Map requirements

3. ASSESS CURRENT COMPETENCE
   ├─ Review education and qualifications
   ├─ Review training records
   ├─ Review experience
   ├─ Assess performance (exercises, audits)
   ├─ Self-assessment
   ├─ Supervisor assessment
   └─ Identify gaps

4. DETERMINE ACTIONS TO ACQUIRE/MAINTAIN COMPETENCE

   ├─ TRAINING options:
   │  ├─ Internal training (develop in-house)
   │  ├─ External training (courses, workshops)
   │  ├─ E-learning (online courses)
   │  ├─ On-the-job training
   │  ├─ Mentoring/coaching
   │  └─ Professional certifications (CBCI, MBCI, ABCP)
   │
   ├─ HIRING options:
   │  ├─ Hire experienced BC professional
   │  ├─ Contract consultant/advisor
   │  └─ Temporary assignment from another org
   │
   └─ OTHER actions:
      ├─ Job shadowing
      ├─ Cross-training
      ├─ Participation in exercises (learning by doing)
      └─ Conference attendance

5. DEVELOP TRAINING PLAN
   ├─ Prioritize competence gaps
   ├─ Schedule training activities
   ├─ Assign participants
   ├─ Allocate budget
   └─ Define success criteria

6. IMPLEMENT TRAINING
   ├─ Deliver training per plan
   ├─ Track attendance
   ├─ Assess learning (tests, practical demos)
   ├─ Document completion
   └─ Provide certificates (if applicable)

7. VERIFY COMPETENCE
   ├─ Post-training assessment
   ├─ Performance in exercises
   ├─ Performance in actual incidents
   ├─ Audit observations
   └─ Supervisor feedback

8. MAINTAIN COMPETENCE RECORDS
   ├─ Training completion certificates
   ├─ Education credentials
   ├─ Professional certifications
   ├─ Experience records
   ├─ Assessment results
   └─ Competency matrix updates

9. REFRESH AND UPDATE
   ├─ Periodic refresher training
   ├─ Update for changes (procedures, technology)
   ├─ Continuous learning
   └─ Career development
```

### Expected Outputs:
- Competency requirements (per role)
- Competency matrix
- Competence gap analysis
- Training plan
- Training materials
- Training records (evidence of competence)
- Certificates/qualifications
- Competence assessment results

### Success Criteria:
- Competence requirements defined for all BC roles
- Current competence assessed
- Gaps identified and addressed
- Training delivered effectively
- Competence verified
- Records maintained and up-to-date
- Continual competence improvement

### Dependencies:
- **Input from:** Flow 5.3 (Roles and responsibilities)
- **Feeds into:** Flow 7.3 (Awareness), Flow 8.5 (Exercising), ALL operational flows

### Related Platform Services:
- `learning-service` (training management)
- `governance-service` (competency tracking)
- `community-service` (knowledge sharing)

### Flow Pattern:
- **Type:** Cyclical (assess → train → verify → maintain)
- **Continuous:** Ongoing competence development
- **Individual:** Different paths for different roles

---

## FLOW 7.3: BC AWARENESS PROGRAMME

**ISO Clause:** 7.3 - Awareness
**Type:** MANDATORY
**Frequency:** Continuous with periodic campaigns
**BCI Practice:** PP2 (Embracing BC)

### Flow Description:
Ensure all persons working under the organization's control are aware of BC policy, their contributions to BCMS effectiveness, and implications of not conforming.

### Trigger Conditions:
- Initial BCMS implementation
- Annual awareness week/month
- New employee onboarding
- BC policy update
- After incidents (real or exercise)
- Low awareness identified (surveys)
- Organizational changes

### Process Steps:

```
1. DEFINE AWARENESS OBJECTIVES

   All persons should be aware of:
   ├─ BC Policy:
   │  └─ What is our commitment to BC?
   │
   ├─ Their contribution to BCMS:
   │  ├─ What is BC and why it matters?
   │  ├─ What is my role in BC?
   │  ├─ How do I help ensure continuity?
   │  └─ What should I do in an incident?
   │
   └─ Implications of not conforming:
      ├─ What happens if we don't follow BC procedures?
      ├─ Impact on organization (financial, operational, reputational)
      ├─ Impact on customers/stakeholders
      └─ Personal accountability

2. IDENTIFY TARGET AUDIENCES

   ├─ All employees (general awareness)
   ├─ New hires (onboarding)
   ├─ Management (leadership role in BC)
   ├─ BC roles (detailed awareness)
   ├─ Contractors/temps (as applicable)
   └─ Specific groups (high-risk locations, critical processes)

3. DEVELOP AWARENESS MATERIALS

   ├─ CONTENT types:
   │  ├─ BC policy (accessible version)
   │  ├─ "BC 101" overview
   │  ├─ Individual responsibilities
   │  ├─ Incident reporting procedures
   │  ├─ Emergency contact information
   │  ├─ Success stories (exercises, real incidents)
   │  └─ BC tips and best practices
   │
   ├─ FORMATS:
   │  ├─ Posters/infographics
   │  ├─ Email bulletins
   │  ├─ Intranet articles
   │  ├─ Videos (short, engaging)
   │  ├─ Presentations (for meetings)
   │  ├─ Interactive e-learning
   │  ├─ Pocket cards (quick reference)
   │  └─ Screensavers/desktop backgrounds
   │
   └─ Ensure materials are:
      ├─ Clear and concise
      ├─ Relevant to audience
      ├─ Visually appealing
      └─ Accessible (language, format)

4. PLAN AWARENESS CAMPAIGNS

   ├─ Annual BC Awareness Week/Month:
   │  ├─ Theme and messaging
   │  ├─ Daily activities
   │  ├─ Contests/prizes
   │  └─ Culminating event
   │
   ├─ Ongoing awareness:
   │  ├─ Monthly BC tips
   │  ├─ Quarterly newsletters
   │  ├─ Seasonal reminders (winter storms, etc.)
   │  └─ Ad-hoc messages (after incidents)
   │
   └─ Special campaigns:
      ├─ New policy launch
      ├─ Exercise promotion
      └─ Lessons learned communication

5. DELIVER AWARENESS PROGRAMME

   ├─ COMMUNICATION CHANNELS:
   │  ├─ Email (mass and targeted)
   │  ├─ Intranet/portal
   │  ├─ Team meetings (BC agenda item)
   │  ├─ Town halls (leadership messages)
   │  ├─ Digital signage
   │  ├─ Social media (internal Yammer, Slack)
   │  └─ Physical posters (break rooms, elevators)
   │
   ├─ EVENTS:
   │  ├─ BC awareness sessions
   │  ├─ Lunch-and-learns
   │  ├─ Tabletop exercises (awareness through participation)
   │  ├─ Demonstrations (e.g., generator test)
   │  └─ Guest speakers (industry experts, emergency services)
   │
   └─ INTERACTIVE:
      ├─ Quizzes (with prizes)
      ├─ Surveys (gauge awareness)
      ├─ Feedback channels (questions, suggestions)
      └─ Gamification (BC challenges)

6. INTEGRATE INTO ONBOARDING
   ├─ BC module in new hire orientation
   ├─ BC policy acknowledgment
   ├─ Role-specific BC briefing
   └─ Emergency procedures orientation

7. ENGAGE LEADERSHIP
   ├─ Leadership messages supporting BC
   ├─ Management participation in events
   ├─ Recognition of BC contributions
   └─ "Tone from the top"

8. MEASURE AWARENESS

   ├─ METHODS:
   │  ├─ Awareness surveys (annual, pulse)
   │  ├─ Quiz scores
   │  ├─ Exercise performance (do people know what to do?)
   │  ├─ Incident response (did they follow procedures?)
   │  ├─ Event attendance
   │  └─ Content engagement (clicks, views)
   │
   ├─ METRICS:
   │  ├─ % awareness of BC policy
   │  ├─ % who know their BC role
   │  ├─ % who know how to report incidents
   │  ├─ Event participation rate
   │  └─ Awareness trend over time
   │
   └─ Report results to management

9. IMPROVE AWARENESS PROGRAMME
   ├─ Analyze effectiveness
   ├─ Gather feedback
   ├─ Identify low-awareness areas
   ├─ Adjust messaging/methods
   └─ Innovate (new approaches)
```

### Expected Outputs:
- Awareness programme plan
- Awareness materials (various formats)
- Campaign calendar
- Communication records (emails, posts, events)
- Event attendance records
- Awareness survey results
- Awareness metrics and trends
- Improvement actions

### Success Criteria:
- High awareness of BC policy (target: >90%)
- High awareness of individual BC roles (target: >85%)
- High awareness of incident reporting (target: >95%)
- Positive trend in awareness over time
- Engagement in awareness activities
- Awareness supports BCMS effectiveness

### Dependencies:
- **Input from:** Flow 5.2 (Policy), Flow 5.3 (Roles), Flow 7.2 (Competence)
- **Feeds into:** Flow 7.4 (Communication), Flow 8.5 (Exercising), ALL operational flows

### Related Platform Services:
- `learning-service` (awareness management)
- `community-service` (communication channels, engagement)
- `documents-service` (materials repository)

### Flow Pattern:
- **Type:** Continuous campaign with periodic intensification
- **Parallel:** Multiple awareness activities simultaneously
- **Feedback Loop:** Measurement → Improvement

---

## FLOW 7.4: COMMUNICATION PLANNING AND EXECUTION

**ISO Clause:** 7.4 - Communication
**Type:** MANDATORY
**Frequency:** Continuous with planned reviews
**BCI Practice:** PP2 (Embracing BC) + PP5 (Enabling Solutions)

### Flow Description:
Determine and execute internal and external communications relevant to BCMS, including what, when, with whom, how, and who communicates.

### Trigger Conditions:
- Initial BCMS implementation (plan communications)
- Ongoing operations (execute communications)
- Incidents (crisis communication)
- Exercises (exercise communication)
- Stakeholder feedback (adjust communication)
- Organizational changes (update communication)

### Process Steps:

```
1. IDENTIFY COMMUNICATION NEEDS

   ├─ INTERNAL communications:
   │  ├─ BCMS establishment and updates
   │  ├─ BC policy and objectives
   │  ├─ Roles and responsibilities
   │  ├─ Training and awareness
   │  ├─ Exercise announcements and results
   │  ├─ Audit findings
   │  ├─ Management review outcomes
   │  ├─ Incident alerts and updates
   │  ├─ Recovery status
   │  └─ Performance and improvements
   │
   └─ EXTERNAL communications:
      ├─ Stakeholder requirements (compliance reporting)
      ├─ Customer notifications (service disruptions)
      ├─ Supplier coordination (supply chain continuity)
      ├─ Regulatory reporting (mandatory notifications)
      ├─ Media relations (crisis communication)
      ├─ Public/community (as appropriate)
      ├─ Partners (mutual aid, collaboration)
      └─ Certification body (audit coordination)

2. FOR EACH COMMUNICATION, DETERMINE:

   ├─ WHAT to communicate:
   │  ├─ Content and message
   │  ├─ Level of detail
   │  ├─ Key points
   │  └─ Supporting information
   │
   ├─ WHEN to communicate:
   │  ├─ Timing (regular schedule or triggered)
   │  ├─ Frequency (daily, weekly, monthly, annual, ad-hoc)
   │  ├─ Urgency (immediate, within hours, within days)
   │  └─ Time-sensitivity
   │
   ├─ WITH WHOM to communicate:
   │  ├─ Target audience (specific or broad)
   │  ├─ Internal parties (employees, management, teams)
   │  ├─ External parties (customers, regulators, media)
   │  └─ Stakeholder segmentation
   │
   ├─ HOW to communicate:
   │  ├─ Communication channel:
   │  │  ├─ Email (mass, targeted)
   │  │  ├─ Intranet/portal
   │  │  ├─ Meetings (face-to-face, virtual)
   │  │  ├─ Phone/SMS (emergency notification)
   │  │  ├─ Social media (external, internal)
   │  │  ├─ Press release/media (crisis)
   │  │  ├─ Website (public)
   │  │  ├─ Written reports (formal)
   │  │  └─ Collaboration tools (Teams, Slack)
   │  │
   │  ├─ Communication method:
   │  │  ├─ One-way (broadcast) or two-way (dialogue)
   │  │  ├─ Formal or informal
   │  │  ├─ Written or verbal
   │  │  └─ Real-time or asynchronous
   │  │
   │  └─ Multiple channels (redundancy for critical communications)
   │
   └─ WHO communicates:
      ├─ Responsible person (primary communicator)
      ├─ Alternate (backup communicator)
      ├─ Approval authority (for sensitive communications)
      └─ Support (e.g., PR team for media)

3. DEVELOP COMMUNICATION PLAN

   ├─ Document all communications in matrix/table:
   │  [Communication | What | When | Whom | How | Who]
   │
   ├─ NORMAL-TIME communications:
   │  (Business as usual, preparedness phase)
   │
   ├─ INCIDENT-TIME communications:
   │  (During disruption, response/recovery phase)
   │
   └─ Approve plan (management, stakeholders)

4. ESTABLISH COMMUNICATION INFRASTRUCTURE

   ├─ Communication channels:
   │  ├─ Primary systems (email, phone, intranet)
   │  ├─ Backup systems (alternate email, mobile, radio)
   │  ├─ Emergency notification system (mass alert)
   │  └─ Redundant systems (if primary fails)
   │
   ├─ Contact information:
   │  ├─ Employee contact database (multiple numbers, emails)
   │  ├─ Stakeholder contact lists (customers, suppliers, regulators)
   │  ├─ Emergency contact lists (incident teams)
   │  ├─ Media contact list
   │  └─ Keep updated (quarterly verification)
   │
   ├─ Communication templates:
   │  ├─ Incident notification templates
   │  ├─ Status update templates
   │  ├─ Stakeholder messaging templates
   │  ├─ Media statement templates
   │  └─ Pre-approved messages (speed in crisis)
   │
   └─ Communication tools:
      ├─ Emergency notification system (e.g., Everbridge)
      ├─ Collaboration platforms
      ├─ Social media management tools
      └─ Monitoring tools (to track communications)

5. EXECUTE NORMAL-TIME COMMUNICATIONS
   ├─ Follow communication plan
   ├─ Regular BCMS updates (per schedule)
   ├─ Awareness communications (Flow 7.3)
   ├─ Training communications
   ├─ Exercise communications
   └─ Reporting (to stakeholders, management)

6. EXECUTE INCIDENT-TIME COMMUNICATIONS

   ├─ IMMEDIATE actions:
   │  ├─ Activate emergency notification
   │  ├─ Alert incident management team
   │  ├─ Notify key stakeholders
   │  └─ Establish communication cadence
   │
   ├─ ONGOING during incident:
   │  ├─ Regular status updates (internal)
   │  ├─ Stakeholder updates (customers, suppliers, regulators)
   │  ├─ Media statements (if public incident)
   │  ├─ Employee briefings
   │  ├─ Rumor control (correct misinformation)
   │  └─ "All clear" message (when resolved)
   │
   └─ Follow crisis communication plan (Flow 8.4.3)

7. GATHER FEEDBACK
   ├─ Was communication received?
   ├─ Was communication understood?
   ├─ Was communication timely?
   ├─ Was communication helpful?
   ├─ What could be improved?
   └─ Surveys, feedback channels

8. DOCUMENT COMMUNICATIONS
   ├─ Communication logs (what was sent, when, to whom)
   ├─ Acknowledgments/receipts
   ├─ Feedback received
   └─ Communication records (evidence for audits)

9. REVIEW AND IMPROVE COMMUNICATION
   ├─ After exercises (communication effectiveness)
   ├─ After incidents (what worked, what didn't)
   ├─ Stakeholder feedback
   ├─ Technology changes (new tools available)
   ├─ Update communication plan
   └─ Test communication systems (regularly)
```

### Expected Outputs:
- Communication plan (normal-time and incident-time)
- Contact databases (verified and current)
- Communication templates
- Communication infrastructure (systems, tools)
- Communication logs
- Feedback and effectiveness assessment
- Communication improvement actions

### Success Criteria:
- Communication plan covers all relevant communications
- Infrastructure reliable (primary and backup)
- Contact information current (<5% bounce rate)
- Communications timely and effective
- Stakeholders informed appropriately
- Feedback positive
- Continuous improvement of communication

### Dependencies:
- **Input from:** Flow 4.2 (Stakeholders), Flow 7.3 (Awareness)
- **Feeds into:** Flow 8.4.3 (Warning and communication), ALL operational flows

### Related Platform Services:
- `community-service` (communication platform)
- `response-service` (incident communication)
- `governance-service` (communication planning)

### Flow Pattern:
- **Type:** Planned → Continuous execution
- **Conditional:** Incident triggers crisis communication
- **Parallel:** Multiple communications simultaneously
- **Feedback Loop:** Feedback → Improvement

---

## FLOW 7.5.1: DOCUMENT CONTROL (Creation and Update)

**ISO Clause:** 7.5 - Documented information
**Type:** MANDATORY
**Frequency:** Continuous document lifecycle management
**BCI Practice:** All practices (documentation is cross-cutting)

### Flow Description:
Control documented information required by ISO 22301 and determined necessary for BCMS effectiveness, including creation, update, and control of BCMS documents.

### Trigger Conditions:
- Initial BCMS implementation (create documents)
- Process changes (update documents)
- Audit findings (correct documents)
- Regulatory changes (update documents)
- Scheduled reviews (maintain currency)
- New requirements (create new documents)

### Process Steps:

```
1. IDENTIFY DOCUMENTED INFORMATION REQUIREMENTS

   ├─ REQUIRED by ISO 22301:
   │  ├─ BCMS scope (4.3)
   │  ├─ BC policy (5.2)
   │  ├─ BC objectives (6.2)
   │  ├─ Risk assessment process and results (6.1, 8.2)
   │  ├─ BIA process and results (8.2.2)
   │  ├─ BC strategies (8.3)
   │  ├─ BC plans and procedures (8.4)
   │  ├─ Exercise plans and results (8.5)
   │  ├─ Monitoring and measurement results (9.1)
   │  ├─ Internal audit programme and results (9.2)
   │  ├─ Management review results (9.3)
   │  ├─ Nonconformities and corrective actions (10.1)
   │  └─ Competence records (7.2)
   │
   └─ DETERMINED NECESSARY by organization:
      ├─ Context analysis reports
      ├─ Stakeholder register
      ├─ RACI matrix
      ├─ Competency matrix
      ├─ Communication plan
      ├─ Training materials
      ├─ Recovery procedures (detailed)
      ├─ Contact lists
      ├─ Vendor contracts
      └─ Lessons learned

2. ESTABLISH DOCUMENT CONTROL PROCEDURE

   Define how documents are:
   ├─ Identified (naming convention, numbering)
   ├─ Created (templates, authoring tools)
   ├─ Reviewed (peer review, approval workflow)
   ├─ Approved (authorization levels)
   ├─ Distributed (access, availability)
   ├─ Stored (repository, location)
   ├─ Retrieved (search, access)
   ├─ Updated (revision process)
   ├─ Version controlled (version history)
   ├─ Archived (retention, disposal)
   └─ Protected (security, backup)

3. CREATE/UPDATE DOCUMENT

   ├─ CREATION:
   │  ├─ Use approved template (if available)
   │  ├─ Author drafts content
   │  ├─ Include required elements:
   │  │  ├─ Identification (title, doc ID, version)
   │  │  ├─ Date
   │  │  ├─ Author
   │  │  ├─ Approver
   │  │  ├─ Change history (for updates)
   │  │  └─ Controlled document notice
   │  └─ Follow organizational style/format
   │
   └─ UPDATE:
      ├─ Identify need for update (trigger)
      ├─ Retrieve current version
      ├─ Make changes (track changes if appropriate)
      ├─ Document reason for change
      └─ Increment version number

4. REVIEW DOCUMENT
   ├─ Technical review (content accuracy)
   ├─ Compliance review (meets requirements)
   ├─ Peer review (colleagues in BC)
   ├─ Stakeholder review (if appropriate)
   └─ Incorporate feedback

5. APPROVE DOCUMENT
   ├─ Submit for approval (per authority matrix)
   ├─ Obtain approval (signature, electronic approval)
   ├─ Document approval (date, approver)
   └─ Final version prepared

6. DISTRIBUTE/PUBLISH DOCUMENT
   ├─ Upload to document management system
   ├─ Notify relevant parties (document available)
   ├─ Ensure accessibility (permissions set)
   ├─ Remove/archive previous version
   └─ Update document register

7. ENSURE DOCUMENT AVAILABILITY
   ├─ Available where and when needed
   ├─ Accessible to authorized persons
   ├─ Protected from unauthorized access
   ├─ Latest version clearly identified
   └─ Obsolete versions removed from use

8. SCHEDULE DOCUMENT REVIEW
   ├─ Set review date (e.g., annual)
   ├─ Assign review responsibility
   ├─ Calendar reminder
   └─ Ensure documents remain current and relevant
```

### Expected Outputs:
- Document control procedure
- Document templates
- Document register (list of all controlled documents)
- Documents (all required and necessary documented information)
- Document metadata (ID, version, date, author, approver, status)
- Approval records
- Distribution records

### Success Criteria:
- All required documented information exists
- Documents approved before use
- Documents current and accurate
- Documents accessible to those who need them
- Obsolete documents removed
- Version control maintained
- Audit trail exists

### Dependencies:
- **Input from:** ALL BCMS processes (create documents)
- **Supports:** ALL BCMS processes (use documents)

### Related Platform Services:
- `documents-service` (document management)
- `governance-service` (approval workflows)

### Flow Pattern:
- **Type:** Lifecycle (create → review → approve → publish → use → review → update → archive)
- **Continuous:** Ongoing document management
- **Parallel:** Multiple documents in different lifecycle stages

---

## FLOW 7.5.2: RECORDS MANAGEMENT

**ISO Clause:** 7.5 - Documented information (records)
**Type:** MANDATORY
**Frequency:** Continuous capture and retention
**BCI Practice:** All practices (records are evidence)

### Flow Description:
Manage documented information kept as evidence of BCMS activities and results (records), including retention, protection, and retrieval.

### Trigger Conditions:
- BCMS activities generate records (continuous)
- Audit preparation (retrieve records)
- Retention period expires (dispose records)
- Regulatory requirements (retain records)

### Process Steps:

```
1. IDENTIFY RECORDS

   Records are documented information that provide evidence:
   ├─ Training records (7.2)
   ├─ Competence evidence (7.2)
   ├─ Communication logs (7.4)
   ├─ BIA results (8.2.2)
   ├─ Risk assessment results (8.2.3)
   ├─ Exercise records (8.5)
   ├─ Incident records (8.4.2)
   ├─ Monitoring and measurement results (9.1)
   ├─ Audit reports (9.2)
   ├─ Management review minutes (9.3)
   ├─ Nonconformity reports (10.1)
   ├─ Corrective action records (10.1)
   └─ Evidence of continuous improvement (10.2)

2. DETERMINE RETENTION REQUIREMENTS

   For each record type:
   ├─ Retention period:
   │  ├─ ISO 22301 requirements (as long as relevant)
   │  ├─ Legal/regulatory requirements (specific periods)
   │  ├─ Organizational policy (may exceed minimum)
   │  └─ Example retention periods:
   │     ├─ Training records: 3-5 years after employment ends
   │     ├─ Audit reports: 2 certification cycles (6 years)
   │     ├─ Incident records: 5-10 years
   │     ├─ Exercise records: Until superseded + 1 year
   │     └─ Risk assessments: Until superseded + 2 years
   │
   ├─ Disposition after retention:
   │  ├─ Secure destruction (shred, delete)
   │  ├─ Archive (long-term storage)
   │  └─ Transfer (to archives, regulatory body)
   │
   └─ Document retention schedule

3. CAPTURE RECORDS
   ├─ Generate record (automatic or manual)
   ├─ Complete required information
   ├─ Ensure legibility and accuracy
   ├─ Identify record type
   └─ Timestamp

4. PROTECT RECORDS

   ├─ PHYSICAL protection (paper records):
   │  ├─ Secure storage (locked cabinets, rooms)
   │  ├─ Fire protection
   │  ├─ Flood protection
   │  └─ Access control
   │
   ├─ ELECTRONIC protection (digital records):
   │  ├─ Backup regularly (daily, weekly)
   │  ├─ Offsite/cloud backup
   │  ├─ Access controls (permissions)
   │  ├─ Encryption (for sensitive records)
   │  ├─ Virus protection
   │  └─ Disaster recovery for record systems
   │
   └─ INTEGRITY protection:
      ├─ Prevent unauthorized alteration
      ├─ Audit trail of changes
      └─ Digital signatures (if appropriate)

5. STORE RECORDS
   ├─ Logical organization (by type, date, department)
   ├─ Naming convention (consistent, searchable)
   ├─ Indexing/cataloging (metadata)
   ├─ Centralized or distributed storage (as appropriate)
   └─ Easy retrieval (search functionality)

6. RETRIEVE RECORDS
   ├─ Authorized access only
   ├─ Search by various criteria (date, type, keyword)
   ├─ Fast retrieval (especially for audits)
   ├─ Log access (who accessed, when)
   └─ Provide copies (not originals, if possible)

7. RETAIN RECORDS
   ├─ Monitor retention schedule
   ├─ Ensure records not destroyed prematurely
   ├─ Migrate records if technology changes (readability)
   └─ Refresh backups (prevent media degradation)

8. DISPOSE RECORDS
   ├─ When retention period expires
   ├─ Verify no hold (legal hold, pending audit)
   ├─ Secure disposal (shred, secure delete)
   ├─ Document disposal (destruction certificate)
   └→ Update records register

9. AUDIT RECORDS MANAGEMENT
   ├─ Periodically verify records exist
   ├─ Check retention compliance
   ├─ Test retrieval (can we find records when needed?)
   └─ Verify protection (backups working?)
```

### Expected Outputs:
- Records retention schedule
- Records register/index
- Backup and recovery procedures
- Access logs
- Disposal certificates
- Records available when needed

### Success Criteria:
- All required records captured
- Records protected from loss/damage
- Records retained per schedule
- Records retrievable when needed
- Records legible and complete
- Unauthorized access prevented
- Compliance with legal/regulatory requirements

### Dependencies:
- **Input from:** ALL BCMS processes (generate records)
- **Used by:** Auditors, management, stakeholders

### Related Platform Services:
- `documents-service` (records management)
- `governance-service` (retention policy)

### Flow Pattern:
- **Type:** Continuous capture → Storage → Retrieval → Disposal
- **Lifecycle:** Record creation → Retention → Disposition
- **Critical:** Records are evidence of BCMS effectiveness

---

## FLOW 7.6: KNOWLEDGE MANAGEMENT (RECOMMENDED)

**ISO Clause:** Not explicit in ISO 22301, but implied in 7.5 and related to ISO 30401 (Knowledge Management)
**Type:** RECOMMENDED (best practice)
**Frequency:** Continuous
**BCI Practice:** PP2 (Embracing BC) + all practices

### Flow Description:
Capture, organize, share, and leverage BC knowledge to improve BCMS effectiveness and organizational resilience.

### Trigger Conditions:
- Initial BCMS implementation (establish knowledge base)
- Lessons learned from exercises/incidents (capture knowledge)
- Staff turnover (preserve knowledge)
- Continuous improvement (leverage knowledge)
- Training needs (share knowledge)

### Process Steps:

```
1. IDENTIFY BC KNOWLEDGE

   ├─ EXPLICIT knowledge (documented):
   │  ├─ BC plans and procedures
   │  ├─ Standards and regulations
   │  ├─ BIA and risk assessment results
   │  ├─ Exercise reports
   │  ├─ Incident after-action reports
   │  ├─ Training materials
   │  ├─ Best practices libraries
   │  └─ Vendor documentation
   │
   └─ TACIT knowledge (experience-based, not documented):
      ├─ "War stories" from incidents
      ├─ Expert judgment (BC veterans)
      ├─ Workarounds and tricks
      ├─ Relationships and networks
      └─ Organizational culture insights

2. CAPTURE KNOWLEDGE

   ├─ FROM EXERCISES:
   │  ├─ What worked well
   │  ├─ What didn't work
   │  ├─ Surprises/unexpected
   │  └─ Recommendations
   │
   ├─ FROM INCIDENTS:
   │  ├─ What happened (timeline)
   │  ├─ How we responded
   │  ├─ What helped recovery
   │  ├─ What hindered recovery
   │  └─ Lessons learned
   │
   ├─ FROM EXPERTS:
   │  ├─ Interviews (before they leave organization!)
   │  ├─ Job shadowing
   │  ├─ Mentoring/coaching
   │  └─ Expert tips and tricks
   │
   └─ FROM EXTERNAL SOURCES:
      ├─ Industry reports
      ├─ Case studies
      ├─ Conferences and networking
      └─ Vendor knowledge

3. ORGANIZE KNOWLEDGE

   ├─ Create BC knowledge base:
   │  ├─ Categorize by topic (BIA, risk, plans, exercises, incidents)
   │  ├─ Tag for easy search (keywords, metadata)
   │  ├─ Version control
   │  └─ Accessibility (permissions)
   │
   ├─ Knowledge repository structure:
   │  ├─ Standards and regulations
   │  ├─ Templates and tools
   │  ├─ Best practices
   │  ├─ Lessons learned library
   │  ├─ Case studies
   │  ├─ FAQs
   │  └─ Links to external resources
   │
   └─ Use technology:
      ├─ Document management system
      ├─ Knowledge management platform
      ├─ Intranet/wiki
      └─ Collaboration tools

4. SHARE KNOWLEDGE

   ├─ TRAINING:
   │  └─ Incorporate lessons learned into training
   │
   ├─ COMMUNITIES OF PRACTICE:
   │  ├─ BC community (internal)
   │  ├─ Regular knowledge sharing sessions
   │  ├─ Guest speakers
   │  └─ External BC networks
   │
   ├─ MENTORING:
   │  └─ Experienced BC staff mentor newer staff
   │
   ├─ KNOWLEDGE TRANSFER:
   │  └─ Before someone leaves, capture their knowledge
   │
   └─ TECHNOLOGY:
      ├─ Searchable knowledge base
      ├─ Push notifications (new content)
      ├─ Social features (comments, ratings)
      └─ Gamification (encourage contribution)

5. LEVERAGE KNOWLEDGE

   ├─ INFORM DECISIONS:
   │  └─ Use lessons learned to improve plans
   │
   ├─ ACCELERATE COMPETENCE:
   │  └─ New BC staff learn faster from knowledge base
   │
   ├─ AVOID REPEATING MISTAKES:
   │  └─ Lessons learned prevent repeat failures
   │
   ├─ INNOVATE:
   │  └─ Build on best practices
   │
   └─ BENCHMARK:
      └─ Compare to industry best practices

6. UPDATE KNOWLEDGE
   ├─ Keep knowledge base current
   ├─ Remove obsolete information
   ├─ Add new lessons learned
   └─ Continuous improvement

7. MEASURE KNOWLEDGE MANAGEMENT
   ├─ Knowledge base usage (views, searches)
   ├─ Contribution rate (new content added)
   ├─ Knowledge retention (staff turnover impact)
   ├─ Knowledge application (used in decisions)
   └─ User satisfaction (feedback)
```

### Expected Outputs:
- BC knowledge base (repository)
- Lessons learned library
- Best practices library
- Case studies
- Knowledge sharing events
- Knowledge management metrics

### Success Criteria:
- Knowledge captured systematically
- Knowledge accessible and searchable
- Knowledge shared widely
- Knowledge leveraged for improvement
- Reduced knowledge loss from turnover
- Faster competence development

### Dependencies:
- **Input from:** Flow 8.5 (Exercises), Flow 8.4.2 (Incidents), Flow 7.2 (Competence), Flow 10.2 (Improvement)
- **Supports:** All BCMS processes

### Related Platform Services:
- `learning-service` (knowledge base)
- `community-service` (knowledge sharing)
- `documents-service` (knowledge repository)

### Flow Pattern:
- **Type:** Continuous cycle (Capture → Organize → Share → Leverage → Update)
- **Feedback Loop:** Leveraged knowledge improves BCMS

---

## FLOW 7.7: INTEGRATION WITH OTHER MANAGEMENT SYSTEMS (RECOMMENDED)

**ISO Clause:** Implied in 4.4 (BCMS integration)
**Type:** RECOMMENDED (efficiency and effectiveness)
**Frequency:** During BCMS establishment and ongoing
**BCI Practice:** PP1 (Establishing BCMS)

### Flow Description:
Integrate BCMS with other management systems (Quality Management System QMS, Information Security Management System ISMS, Environmental Management System EMS, Occupational Health and Safety Management System OHSMS) to leverage synergies, avoid duplication, and improve overall management system effectiveness.

### Trigger Conditions:
- Organization has multiple management systems
- BCMS being implemented in organization with existing management systems
- Integrated management system (IMS) initiative
- Duplication and inefficiency identified
- Certification requirements (multiple standards)

### Process Steps:

```
1. IDENTIFY COMMON ELEMENTS

   ISO management system standards share common structure (Annex SL/High-Level Structure):

   ├─ Clause 4: Context of the organization
   ├─ Clause 5: Leadership
   ├─ Clause 6: Planning
   ├─ Clause 7: Support
   ├─ Clause 8: Operation (specific to each standard)
   ├─ Clause 9: Performance evaluation
   └─ Clause 10: Improvement

   Common elements that can be integrated:
   ├─ Context analysis (same for all systems)
   ├─ Stakeholder identification (same stakeholders)
   ├─ Scope (aligned scopes)
   ├─ Policy (integrated policy possible)
   ├─ Objectives (aligned objectives)
   ├─ Risk management (coordinated approach)
   ├─ Competence and training (shared training)
   ├─ Awareness (shared awareness programme)
   ├─ Communication (shared communication plan)
   ├─ Document control (single document management system)
   ├─ Internal audit (integrated audits)
   ├─ Management review (combined reviews)
   ├─ Corrective action (shared process)
   └─ Continual improvement (coordinated)

2. IDENTIFY SYNERGIES AND DEPENDENCIES

   ├─ BC and Information Security (ISMS ISO 27001):
   │  ├─ Shared: IT disaster recovery, cyber incident response
   │  ├─ ISMS focuses on confidentiality, integrity, availability
   │  ├─ BCMS focuses on continuity of critical operations
   │  └─ Integration: Align IT recovery with BC recovery objectives
   │
   ├─ BC and Quality (QMS ISO 9001):
   │  ├─ Shared: Process management, customer focus
   │  ├─ QMS focuses on consistent quality
   │  ├─ BCMS ensures quality maintained during disruptions
   │  └─ Integration: BC for critical quality processes
   │
   ├─ BC and Environment (EMS ISO 14001):
   │  ├─ Shared: Emergency preparedness for environmental incidents
   │  ├─ EMS focuses on environmental impact
   │  ├─ BCMS addresses environmental disruptions
   │  └─ Integration: Environmental incidents in BC scenarios
   │
   ├─ BC and Health & Safety (OHSMS ISO 45001):
   │  ├─ Shared: Emergency response, life safety
   │  ├─ OHSMS focuses on worker safety
   │  ├─ BCMS ensures operations continue safely
   │  └─ Integration: Safety in BC plans
   │
   └─ BC and Risk Management (ISO 31000):
      ├─ BCMS includes risk assessment (operational risks)
      ├─ Risk management broader (strategic, financial, operational)
      └─ Integration: Coordinated risk assessment

3. DEVELOP INTEGRATED APPROACH

   ├─ Single context analysis (for all systems)
   ├─ Single stakeholder register (all systems consider)
   ├─ Integrated policy (covering BC, quality, security, safety, environment)
   ├─ Aligned objectives (across all systems)
   ├─ Coordinated risk management (enterprise risk management)
   ├─ Single document management system (all system documents)
   ├─ Integrated training programme (cover all system requirements)
   ├─ Combined audits (audit all systems together)
   ├─ Single management review (review all systems)
   └─ Unified improvement process

4. ALIGN PROCESSES
   ├─ Map processes across systems
   ├─ Identify overlaps and gaps
   ├─ Eliminate duplication
   ├─ Ensure completeness (no requirements missed)
   └─ Document integrated processes

5. INTEGRATE DOCUMENTATION
   ├─ Integrated management system manual (optional)
   ├─ Cross-reference documents (avoid duplication)
   ├─ Shared procedures (where applicable)
   ├─ System-specific procedures (where needed)
   └─ Clear labeling (which system(s) each document supports)

6. COORDINATE ACTIVITIES
   ├─ Integrated audit schedule
   ├─ Combined management review meetings
   ├─ Coordinated training delivery
   ├─ Unified reporting (dashboards covering all systems)
   └─ Shared resources (where appropriate)

7. MAINTAIN SYSTEM INTEGRITY
   ├─ Ensure each standard's requirements fully met
   ├─ Don't compromise one system for another
   ├─ Respect different focuses (BC is continuity-focused)
   └─ Maintain separate certification (if required)

8. MONITOR INTEGRATION EFFECTIVENESS
   ├─ Is integration reducing duplication and effort?
   ├─ Are all system requirements still met?
   ├─ Is integration improving overall effectiveness?
   └─ Adjust integration approach as needed
```

### Expected Outputs:
- Integrated management system (IMS) framework
- Common elements documented once (context, stakeholders, policy, etc.)
- Integrated processes (where appropriate)
- Coordinated activities (audits, reviews, training)
- Integration mapping (how systems relate)
- Resource efficiency gains

### Success Criteria:
- Duplication eliminated or minimized
- All system requirements met
- Resource efficiency improved
- Processes streamlined
- Certifications maintained (if applicable)
- Overall management system effectiveness enhanced

### Dependencies:
- **Requires:** Multiple management systems in organization
- **Supports:** ALL management systems

### Related Platform Services:
- `governance-service` (integrated management system)
- ALL services (integration across all)

### Flow Pattern:
- **Type:** Initial integration → Continuous coordination
- **Synergistic:** Integrated systems more effective than siloed

---

*[Document continues with Clause 8: Operation - The CORE of BCMS]*

---

# CLAUSE 8: OPERATION

**PDCA Phase:** DO
**Purpose:** Implement BC strategies, plans, and procedures - THE CORE OF BCMS

This clause contains the most business process flows (18 flows) as it covers the actual implementation of business continuity activities.

---

## FLOW 8.1: OPERATIONAL PLANNING AND CONTROL

**ISO Clause:** 8.1 - Operational planning and control
**Type:** MANDATORY
**Frequency:** Continuous (plan → execute → control)
**BCI Practice:** PP3-PP6 (All technical practices)

### Flow Description:
Plan, implement, and control processes needed to meet BCMS requirements and implement actions determined in Clause 6.

### Trigger Conditions:
- BCMS implementation (initial planning)
- Annual BC planning cycle
- Actions from Clause 6 (risks, objectives) to be implemented
- Process changes needed
- Resource allocation decisions

### Process Steps:

```
1. PLAN OPERATIONAL PROCESSES

   Identify processes needed to meet BCMS requirements:
   ├─ BIA process (Flow 8.2.2)
   ├─ Risk assessment process (Flow 8.2.3)
   ├─ BC strategy development process (Flow 8.3)
   ├─ BC plan development process (Flow 8.4)
   ├─ Incident response process (Flow 8.4.2)
   ├─ Exercising and testing process (Flow 8.5)
   └─ Supporting processes (monitoring, audit, review, improvement)

2. FOR EACH PROCESS, DETERMINE:
   ├─ Process criteria (what defines success?)
   ├─ Process controls (how to ensure effectiveness?)
   ├─ Resources needed
   ├─ Responsibilities
   ├─ Documented information (procedures, records)
   └─ Performance indicators

3. IMPLEMENT ACTIONS FROM CLAUSE 6
   ├─ Actions to address risks and opportunities (Flow 6.1.2)
   ├─ Actions to achieve BC objectives (Flow 6.2.2)
   ├─ Integrate actions into operational processes
   └─ Track implementation

4. ESTABLISH CONTROLS
   ├─ Process controls (to ensure effectiveness)
   ├─ Output controls (to verify results meet requirements)
   ├─ Checkpoints and gates (approval points)
   └─ Monitoring mechanisms

5. PLAN FOR CHANGES
   ├─ Anticipate changes (organizational, technological, regulatory)
   ├─ Plan how changes will be managed
   └─ Follow Flow 6.3 (Change management)

6. CONTROL OUTSOURCED PROCESSES
   ├─ Identify externally provided processes affecting BCMS
   │  (e.g., IT services, emergency notification service, alternate site)
   ├─ Ensure control over outsourced processes:
   │  ├─ Define BC requirements in contracts/SLAs
   │  ├─ Monitor provider performance
   │  ├─ Review provider's own BC capabilities
   │  └─ Audit provider compliance
   │
   └─ Document how control is ensured

7. IMPLEMENT OPERATIONAL PROCESSES
   ├─ Execute per plan
   ├─ Follow documented procedures
   ├─ Apply controls
   ├─ Generate records
   └─ Monitor performance

8. KEEP DOCUMENTED INFORMATION
   ├─ Evidence that processes carried out as planned
   ├─ Evidence that outputs meet requirements
   ├─ Records for audit and review
   └─ Basis for improvement
```

### Expected Outputs:
- Operational plan (covering all Clause 8 processes)
- Process descriptions and procedures
- Process controls definition
- Implementation records
- Evidence of process execution
- Evidence of outsourced process control

### Success Criteria:
- All required operational processes planned
- Processes implemented effectively
- Process controls in place
- Actions from Clause 6 implemented
- Outsourced processes controlled
- Evidence maintained

### Dependencies:
- **Input from:** Flow 6.1 (Risks/opportunities), Flow 6.2 (Objectives), Flow 6.3 (Changes)
- **Governs:** ALL Clause 8 operational flows (8.2 through 8.5)

### Related Platform Services:
- `governance-service` (operational planning)
- `bcm-coordination-service` (process orchestration)
- ALL BCM services (operational processes)

### Flow Pattern:
- **Type:** Plan → Execute → Control (continuous)
- **Meta-process:** This flow governs all operational flows

---

## FLOW 8.2.1: BUSINESS IMPACT ANALYSIS (BIA) PROCESS ESTABLISHMENT

**ISO Clause:** 8.2.1 - General (BIA and risk assessment)
**Type:** MANDATORY
**Frequency:** Initial (establish process) + ongoing (execute process)
**BCI Practice:** PP3 (Analysis)

### Flow Description:
Establish, implement, and maintain a systematic process for conducting Business Impact Analysis and risk assessment.

### Trigger Conditions:
- Initial BCMS implementation (establish process)
- Process review (improve process)
- Methodology changes (update process)

### Process Steps:

```
1. DESIGN BIA METHODOLOGY

   ├─ PURPOSE:
   │  └─ Identify critical activities and understand disruption impacts
   │
   ├─ SCOPE:
   │  └─ Which processes/activities to analyze (per BCMS scope)
   │
   ├─ APPROACH:
   │  ├─ Top-down (start with products/services, identify supporting activities)
   │  ├─ Bottom-up (start with processes, determine criticality)
   │  └─ Hybrid (combination)
   │
   ├─ IMPACT CATEGORIES:
   │  ├─ Financial (revenue loss, cost increase)
   │  ├─ Operational (productivity, capacity, quality)
   │  ├─ Reputational (brand damage, customer confidence)
   │  ├─ Regulatory (compliance, fines, license loss)
   │  ├─ Safety (health and safety of people)
   │  ├─ Environmental (environmental damage)
   │  └─ [Healthcare specific: Patient safety, clinical outcomes]
   │
   ├─ TIME FRAMES:
   │  ├─ Analysis periods (e.g., 1 hour, 4 hours, 1 day, 3 days, 1 week, 1 month)
   │  ├─ RTO determination approach
   │  ├─ RPO determination approach
   │  └─ MTPD determination approach
   │
   ├─ IMPACT QUANTIFICATION:
   │  ├─ Qualitative (High/Medium/Low)
   │  ├─ Quantitative ($ amounts, customer numbers, etc.)
   │  └─ Semi-quantitative (numerical scale 1-5)
   │
   ├─ DEPENDENCIES:
   │  ├─ What dependencies to identify (people, technology, facilities, suppliers, utilities)
   │  └─ How to map dependencies
   │
   └─ DATA COLLECTION:
      ├─ Interviews (process owners, subject matter experts)
      ├─ Workshops (group sessions)
      ├─ Questionnaires (surveys)
      ├─ Document review (process documentation, financial data)
      └─ System analysis (technology dependencies)

2. DOCUMENT BIA METHODOLOGY
   ├─ BIA process description
   ├─ BIA templates and tools
   ├─ Impact criteria and scales
   ├─ Roles and responsibilities
   ├─ Data collection methods
   └─ Approval and review process

3. TRAIN BIA PRACTITIONERS
   ├─ BC team members conducting BIAs
   ├─ Interviewers
   ├─ BIA tool users
   └─ Process owners (participants)

4. ESTABLISH BIA SCHEDULE
   ├─ Initial BIA for all in-scope processes
   ├─ BIA review/refresh cycle (annual, biennial)
   ├─ Triggered BIA (when significant changes occur)
   └─ BIA calendar

5. EXECUTE BIA PROCESS
   └─ (See Flow 8.2.2 for detailed BIA execution)

6. REVIEW BIA METHODOLOGY
   ├─ After each BIA cycle (lessons learned)
   ├─ Is methodology effective?
   ├─ Are impact criteria appropriate?
   ├─ Are time frames realistic?
   └─ Improve methodology as needed

7. MAINTAIN BIA PROCESS
   ├─ Keep methodology current
   ├─ Update tools and templates
   ├─ Refresh training
   └─ Ensure consistent application
```

### Expected Outputs:
- BIA methodology document
- BIA templates and tools
- BIA process schedule
- BIA training materials
- BIA methodology review records

### Success Criteria:
- BIA methodology comprehensive and appropriate
- BIA process documented and understood
- Consistent application of methodology
- Effective in identifying critical activities and impacts
- Methodology improves over time

### Dependencies:
- **Input from:** Flow 4.3 (Scope)
- **Feeds into:** Flow 8.2.2 (BIA execution)

### Related Platform Services:
- `bia-service` (BIA methodology and execution)
- `governance-service` (process management)

### Flow Pattern:
- **Type:** Establish → Execute → Review → Improve

---

## FLOW 8.2.2: BUSINESS IMPACT ANALYSIS (BIA) EXECUTION

**ISO Clause:** 8.2.2 - Business impact analysis
**Type:** MANDATORY
**Frequency:** Initial + periodic review (annual/biennial) + triggered by changes
**BCI Practice:** PP3 (Analysis)

### Flow Description:
Execute BIA to identify critical activities, assess impact of disruption over time, determine recovery priorities and time frames, and identify dependencies and resources.

This is one of the MOST CRITICAL flows in the entire standard - BIA is the foundation for all BC planning.

### Trigger Conditions:
- Initial BCMS implementation (baseline BIA)
- Scheduled BIA review cycle (annual or biennial)
- Significant organizational change (new products, services, locations, technology, suppliers)
- Major incident lessons learned (impacts were different than expected)
- Stakeholder requirements change
- Audit finding or management review decision

### Process Steps:

```
1. PREPARE FOR BIA

   ├─ Define BIA scope:
   │  └─ Which processes/activities to analyze this cycle
   │
   ├─ Assemble BIA team:
   │  ├─ BC Manager/Coordinator (lead)
   │  ├─ BIA analysts
   │  └─ Support (admin, tools)
   │
   ├─ Identify participants:
   │  ├─ Process owners (primary interviewees)
   │  ├─ Subject matter experts (deep knowledge)
   │  ├─ Department heads (strategic perspective)
   │  └─ Support functions (IT, HR, Facilities - dependencies)
   │
   ├─ Schedule BIA activities:
   │  ├─ Interviews/workshops
   │  ├─ Analysis time
   │  └─ Review and validation
   │
   ├─ Prepare BIA tools:
   │  ├─ BIA questionnaires
   │  ├─ BIA software/spreadsheets
   │  └─ Templates
   │
   └─ Communicate to participants:
      ├─ Purpose of BIA
      ├─ What will be asked
      ├─ Time commitment
      └─ Pre-work (if any)

2. IDENTIFY ACTIVITIES SUPPORTING PRODUCTS/SERVICES

   ├─ List products and services delivered by organization:
   │  └─ (Within BCMS scope)
   │
   ├─ For each product/service, identify supporting activities:
   │  ├─ Core activities (directly deliver product/service)
   │  ├─ Supporting activities (enable core activities)
   │  └─ Suppliers/partners (external dependencies)
   │
   ├─ Create activity inventory:
   │  ├─ Activity name and description
   │  ├─ Owner (person/department responsible)
   │  ├─ Inputs required
   │  ├─ Outputs produced
   │  └─ Links to products/services
   │
   └─ Validate activity list with process owners

3. ASSESS IMPACTS OF DISRUPTION OVER TIME

   For each activity, assess impact if activity disrupted:

   ├─ TIME PERIODS (example):
   │  ├─ 1 hour
   │  ├─ 4 hours
   │  ├─ 8 hours (1 business day)
   │  ├─ 24 hours (1 calendar day)
   │  ├─ 3 days
   │  ├─ 1 week
   │  ├─ 2 weeks
   │  └─ 1 month
   │
   ├─ IMPACT CATEGORIES (assess for each time period):
   │
   │  ├─ FINANCIAL IMPACT:
   │  │  ├─ Revenue loss (sales not made, services not delivered)
   │  │  ├─ Cost increase (overtime, expedited shipping, penalties)
   │  │  ├─ Cash flow impact (can't process payments)
   │  │  ├─ Quantify in currency ($ per hour/day)
   │  │  └─ Consider cumulative (impacts add up over time)
   │  │
   │  ├─ OPERATIONAL IMPACT:
   │  │  ├─ Productivity loss (% of normal capacity)
   │  │  ├─ Backlog accumulation (how fast, how long to clear)
   │  │  ├─ Service level failures (miss SLAs)
   │  │  ├─ Quality issues (errors increase when stressed)
   │  │  └─ Cascade effects (disruption spreads to other areas)
   │  │
   │  ├─ REPUTATIONAL IMPACT:
   │  │  ├─ Customer dissatisfaction (complaints, churn)
   │  │  ├─ Brand damage (negative publicity)
   │  │  ├─ Market share loss (customers switch to competitors)
   │  │  ├─ Partner confidence (suppliers, investors lose faith)
   │  │  └─ Long-term reputation effects (hard to quantify but critical)
   │  │
   │  ├─ REGULATORY/COMPLIANCE IMPACT:
   │  │  ├─ Compliance violations (fail to meet regulatory requirements)
   │  │  ├─ Fines and penalties (specific $ amounts if known)
   │  │  ├─ License suspension or revocation (existential threat)
   │  │  ├─ Legal liability (lawsuits from affected parties)
   │  │  └─ Regulatory scrutiny (increased oversight, reputational)
   │  │
   │  ├─ SAFETY IMPACT:
   │  │  ├─ Risk to employee safety (injuries, health impacts)
   │  │  ├─ Risk to customer/public safety (product safety, facility safety)
   │  │  ├─ Environmental harm (pollution, contamination)
   │  │  └─ Ethical concerns (unable to fulfill duty of care)
   │  │
   │  └─ [HEALTHCARE-SPECIFIC]:
   │     ├─ PATIENT SAFETY IMPACT:
   │     │  ├─ Risk to life (mortality increase)
   │     │  ├─ Risk of permanent disability (morbidity)
   │     │  ├─ Delayed critical treatment (stroke, MI, trauma)
   │     │  ├─ Medication errors (if systems down)
   │     │  └─ Patient transfers required (capacity/capability loss)
   │     │
   │     └─ CLINICAL OUTCOMES IMPACT:
   │        ├─ Quality of care reduction
   │        ├─ Length of stay increase
   │        ├─ Readmission rate increase
   │        └─ Patient satisfaction decline
   │
   ├─ IMPACT QUANTIFICATION:
   │  ├─ Quantitative (specific numbers: $, customers, patients)
   │  ├─ Qualitative (High/Medium/Low based on criteria)
   │  └─ Combined (quantitative where possible, qualitative otherwise)
   │
   └─ IMPACT TRAJECTORY:
      ├─ How do impacts change over time?
      ├─ At what point does impact become unacceptable?
      ├─ Are there impact thresholds (points where impact jumps significantly)?
      └─ Graph impact over time (impact curves)

4. DETERMINE TIME FRAMES

   Based on impact assessment:

   ├─ RECOVERY TIME OBJECTIVE (RTO):
   │  ├─ Definition: Maximum acceptable downtime for activity
   │  ├─ Determined by: Point where impacts become unacceptable
   │  ├─ Examples:
   │  │  ├─ Critical: 0 hours (immediate/no downtime acceptable)
   │  │  ├─ Vital: 4 hours
   │  │  ├─ Important: 1 day
   │  │  └─ Normal: 3-5 days
   │  └─ Document for each activity
   │
   ├─ RECOVERY POINT OBJECTIVE (RPO):
   │  ├─ Definition: Maximum acceptable data loss for activity
   │  ├─ Applies to: Activities dependent on data/systems
   │  ├─ Examples:
   │  │  ├─ Critical data: 0 (zero data loss) - real-time replication
   │  │  ├─ Important data: 1 hour - hourly backups
   │  │  └─ Normal data: 24 hours - daily backups
   │  └─ Document for each data-dependent activity
   │
   └─ MAXIMUM TOLERABLE PERIOD OF DISRUPTION (MTPD):
      ├─ Definition: Time after which organizational viability threatened
      ├─ Absolute limit (beyond RTO - the "point of no return")
      ├─ Examples:
      │  ├─ Critical process: 24 hours MTPD (if not recovered, organization fails)
      │  ├─ Important process: 1 week MTPD
      │  └─ Normal process: 1 month MTPD
      └─ Document for critical activities

5. DETERMINE RECOVERY PRIORITIES

   ├─ Prioritize activities based on:
   │  ├─ Impact severity (higher impact = higher priority)
   │  ├─ RTO (shorter RTO = higher priority)
   │  ├─ Dependencies (must recover dependencies first)
   │  └─ Stakeholder requirements (regulatory, contractual)
   │
   ├─ Assign priority levels:
   │  ├─ Priority 1 (Critical): Recover immediately (RTO 0-4 hours)
   │  ├─ Priority 2 (Vital): Recover within 1 day
   │  ├─ Priority 3 (Important): Recover within 3 days
   │  └─ Priority 4 (Normal): Recover within 1-2 weeks
   │
   ├─ Create recovery sequence:
   │  └─ Order in which activities should be recovered
   │
   └─ Validate priorities:
      ├─ Do priorities make sense?
      ├─ Can we actually achieve these RTOs?
      └─ Adjust if necessary (RTO may need to be realistic, not just desired)

6. IDENTIFY DEPENDENCIES

   For each critical activity, identify dependencies:

   ├─ PEOPLE (Human Resources):
   │  ├─ Number of people required (minimum, optimal, peak)
   │  ├─ Skills required (specialized vs. general)
   │  ├─ Key personnel (cannot easily replace)
   │  ├─ Availability constraints (shift work, on-call)
   │  └─ Cross-training possibilities
   │
   ├─ TECHNOLOGY (Information Systems):
   │  ├─ Applications/software (what systems used)
   │  ├─ Data (what data accessed, where stored)
   │  ├─ Infrastructure (servers, network, workstations)
   │  ├─ Telecommunications (phone, internet, mobile)
   │  ├─ Specialized equipment (medical devices, manufacturing equipment)
   │  └─ IT support (who maintains/fixes)
   │
   ├─ FACILITIES (Physical Infrastructure):
   │  ├─ Buildings/workspace (office, factory, hospital)
   │  ├─ Location importance (does location matter?)
   │  ├─ Specialized facilities (clean room, operating room)
   │  ├─ Utilities:
   │  │  ├─ Electricity (power requirements, backup power)
   │  │  ├─ Water (potable, process, cooling)
   │  │  ├─ HVAC (temperature, humidity control)
   │  │  ├─ Telecommunications (phone, internet)
   │  │  └─ [Healthcare: Medical gases (oxygen, compressed air, vacuum)]
   │  └─ Access (physical security, parking)
   │
   ├─ SUPPLIERS AND VENDORS (External Dependencies):
   │  ├─ Critical suppliers (single source? alternatives?)
   │  ├─ Supply lead times (how long to get supplies?)
   │  ├─ Supplier BC capabilities (do they have BC plans?)
   │  ├─ Critical services (outsourced services)
   │  └─ Contracts/SLAs (commitments)
   │
   ├─ INFORMATION AND DOCUMENTATION:
   │  ├─ Documents required (forms, manuals, procedures)
   │  ├─ Records required (customer data, financial records)
   │  ├─ Reference materials (regulations, standards)
   │  └─ Accessibility (where stored? backup copies?)
   │
   └─ OTHER DEPENDENCIES:
      ├─ Interdependencies with other business activities
      ├─ External services (emergency services, government)
      ├─ Transportation (logistics, employee commute)
      └─ Environmental conditions (weather, infrastructure)

7. IDENTIFY RESOURCE REQUIREMENTS

   For each critical activity, minimum resources needed:

   ├─ PEOPLE resources:
   │  ├─ Minimum staffing (skeletal crew to maintain activity)
   │  ├─ Optimal staffing (ideal recovery team size)
   │  ├─ Peak staffing (if demand surge during recovery)
   │  └─ Roles and skills required
   │
   ├─ TECHNOLOGY resources:
   │  ├─ Minimum IT (what systems absolutely required)
   │  ├─ Workarounds (manual processes if systems unavailable)
   │  └─ Recovery time for systems (IT DR plans)
   │
   ├─ FACILITIES resources:
   │  ├─ Space requirements (square footage, configuration)
   │  ├─ Location flexibility (work from home? alternate site?)
   │  └─ Specialized facility needs
   │
   ├─ SUPPLIES AND MATERIALS:
   │  ├─ Consumables (office supplies, medical supplies)
   │  ├─ Inventory levels (how much on hand? how long lasts?)
   │  └─ Emergency stockpiles
   │
   └─ FINANCIAL resources:
   │  ├─ Operating funds (cash flow to sustain operations)
   │  └─ Emergency funds (for recovery expenses)

8. ANALYZE AND CONSOLIDATE BIA RESULTS

   ├─ Aggregate activity-level data to organizational view
   ├─ Identify critical activities (high impact, short RTO)
   ├─ Identify common dependencies (single points of failure)
   ├─ Identify concentration risks (many critical activities in one location, one supplier, etc.)
   ├─ Analyze interdependencies (activity recovery sequence)
   ├─ Calculate peak resource requirements (when recovering multiple activities)
   └─ Create summary dashboards/visualizations

9. VALIDATE BIA RESULTS

   ├─ Review with process owners (accuracy check)
   ├─ Review with management (strategic perspective)
   ├─ Cross-check with actual incidents (if any historical data)
   ├─ Sanity check (do results make sense?)
   └─ Obtain stakeholder agreement

10. DOCUMENT BIA RESULTS

    ├─ BIA REPORT (comprehensive):
    │  ├─ Executive summary (key findings, critical activities)
    │  ├─ Methodology used
    │  ├─ Activity-level BIA results (detailed)
    │  ├─ Impact analysis summary
    │  ├─ RTO/RPO/MTPD summary
    │  ├─ Recovery priorities
    │  ├─ Dependencies analysis
    │  ├─ Resource requirements summary
    │  ├─ Recommendations for BC strategies
    │  └─ Appendices (detailed data, interview notes)
    │
    ├─ BIA DATABASE/TOOL:
    │  └─ Store all BIA data for easy access and updates
    │
    ├─ VISUALIZATIONS:
    │  ├─ Impact curves (impact over time graphs)
    │  ├─ Criticality matrix (impact vs. RTO)
    │  ├─ Dependency maps (relationships between activities, resources)
    │  └─ Priority lists (ranked activities)
    │
    └─ APPROVAL AND COMMUNICATION:
       ├─ Obtain management approval of BIA results
       ├─ Communicate results to relevant stakeholders
       └─ Use BIA results to inform BC strategy (Flow 8.3)

11. MAINTAIN BIA

    ├─ Schedule next BIA review (annual, biennial)
    ├─ Trigger BIA updates when significant changes occur
    ├─ Keep BIA results accessible (for planning, exercises, incidents)
    └─ Monitor for changes that might invalidate BIA results
```

### Expected Outputs:
- Activity inventory
- Impact assessment (detailed, by activity and time period)
- RTO/RPO/MTPD for all activities
- Recovery priority list
- Dependency maps (people, technology, facilities, suppliers)
- Resource requirements (minimum, optimal, peak)
- BIA report (comprehensive documentation)
- BIA database (structured data)
- Visualizations (impact curves, criticality matrix, dependency maps)
- Validated and approved BIA results

### Success Criteria:
- All in-scope activities analyzed
- Impacts realistically assessed and quantified
- RTOs determined based on impacts (not arbitrary)
- Dependencies comprehensively identified
- Resource requirements determined
- Results validated by process owners and management
- BIA results inform BC strategy
- BIA documented and maintained

### Dependencies:
- **Input from:** Flow 4.3 (Scope), Flow 8.2.1 (BIA methodology)
- **Feeds into:** Flow 8.2.3 (Risk assessment), Flow 8.3 (BC strategy), Flow 8.4 (BC plans)
- **Critical dependency:** BIA is the foundation for all BC planning

### Related Platform Services:
- `bia-service` (BIA execution, data storage, reporting)
- `planning_service` (recovery priorities, resource planning)
- `documents-service` (BIA documentation)

### Flow Pattern:
- **Type:** Cyclical (initial → periodic review)
- **Sequential:** Steps must follow logical order
- **Iterative:** Validate and refine results
- **Critical:** One of most important flows in entire standard

### Healthcare Specific Considerations:

```
TIER-BASED CRITICALITY (WHO Framework):

TIER 1 (IMMEDIATE - RTO: 0):
├─ Emergency Department (triage, trauma, stabilization)
├─ ICU/CCU (life support, ventilators, monitoring)
├─ Operating Room (emergency surgery)
└─ Labor & Delivery (high-risk, emergency C-sections)

TIER 2 (URGENT - RTO: 2-4 hours):
├─ Laboratory (critical tests, blood bank)
├─ Pharmacy (medication dispensing, IV prep)
├─ Radiology (CT/X-ray for emergencies)
└─ Dialysis (for admitted patients)

TIER 3 (IMPORTANT - RTO: 24 hours):
├─ General inpatient care
├─ Scheduled surgery
├─ Outpatient clinics
└─ Non-urgent diagnostics

TIER 4 (NORMAL - RTO: 3-5 days):
├─ Administrative functions (billing, scheduling)
├─ Elective procedures
└─ Non-critical support services

IMPACT CATEGORIES (Healthcare-specific):
├─ Patient safety (most critical - mortality/morbidity)
├─ Clinical outcomes (quality of care)
├─ Regulatory compliance (HIPAA, CMS, Joint Commission)
├─ Financial (reimbursement loss, penalties)
└─ Reputation (community trust, referrals)

DEPENDENCIES (Healthcare-specific):
├─ Medical staff (physicians, nurses - specialized skills, licensing)
├─ EHR (electronic health records - patient data, orders)
├─ Medical devices (patient monitors, ventilators, infusion pumps)
├─ Medical gases (oxygen, compressed air, vacuum, anesthesia)
├─ Pharmaceuticals (critical medications, controlled substances)
└─ Medical supplies (PPE, surgical supplies, implants)
```

---

*[Document continues...]*

**Status:** Clause 8 in progress - 2 of 18 flows documented
**Next:** Flow 8.2.3 (Risk Assessment) and remaining operational flows

---

**Document Owner:** BCM Knowledge Base
**Version:** 1.0 (Part 2)
**Date:** 2025-10-08
