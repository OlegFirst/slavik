# 📘 Planning Module - User Guide

**Version:** 1.0.0
**Date:** 2025-10-22
**For:** AI Platform ISO - Business Continuity Planning Module

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [BC Plans Management](#bc-plans-management)
4. [Recovery Strategies](#recovery-strategies)
5. [Action Plans](#action-plans)
6. [Plan Approval Workflow](#plan-approval-workflow)
7. [Analytics Dashboard](#analytics-dashboard)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## 1. Introduction

### What is the Planning Module?

The Planning Module helps organizations create, manage, and maintain Business Continuity Plans (BC Plans) in compliance with **ISO 22301:2019 Clause 8.3**.

### Key Features

✅ **BC Plans Management** - Create and manage multiple types of business continuity plans
✅ **Recovery Strategies** - Define strategies for different disruption scenarios
✅ **Action Plans** - Track preventive, detective, corrective, and recovery actions
✅ **Approval Workflow** - Draft → Review → Approved → Active lifecycle
✅ **Analytics Dashboard** - Monitor coverage, maturity, gaps, and implementation
✅ **Integration** - Links with BIA and Risk modules for comprehensive planning

### Who Should Use This Module?

- **Business Continuity Managers** - Create and maintain BC plans
- **Department Heads** - Contribute to departmental plans
- **Risk Managers** - Align plans with risk assessments
- **Executives** - Review analytics and approve plans
- **Auditors** - Verify compliance and coverage

---

## 2. Getting Started

### Accessing the Planning Module

1. Log in to AI Platform ISO
2. Navigate to **Planning** from the main menu
3. You'll see the BC Plans dashboard

### Your First BC Plan

**Quick Start (5 minutes):**

1. Click **"Create Plan"** button
2. Enter plan name and description
3. Select plan type (Comprehensive, Departmental, IT DR, Emergency Response, or Crisis Management)
4. Set Recovery Objectives:
   - **RTO** (Recovery Time Objective) - Maximum acceptable downtime
   - **RPO** (Recovery Point Objective) - Maximum acceptable data loss
   - **MTPD** (Maximum Tolerable Period of Disruption) - Absolute deadline
5. Choose criticality level (Critical, High, Medium, Low)
6. Click **"Create Plan"**

🎉 **Congratulations!** You've created your first BC Plan.

---

## 3. BC Plans Management

### Plan Types

#### 1. Comprehensive BC Plan
**Purpose:** Organization-wide business continuity planning
**Scope:** All critical processes and departments
**When to use:** Primary BC plan covering entire organization
**Example:** "Company-Wide Business Continuity Plan 2025"

#### 2. Departmental Plan
**Purpose:** Specific department or business unit planning
**Scope:** Single department (IT, Finance, Operations, etc.)
**When to use:** Detailed planning for critical departments
**Example:** "IT Department Continuity Plan"

#### 3. IT Disaster Recovery Plan
**Purpose:** Technology systems and infrastructure recovery
**Scope:** Servers, networks, applications, data
**When to use:** IT-specific recovery procedures
**Example:** "Datacenter Disaster Recovery Plan"

#### 4. Emergency Response Plan
**Purpose:** Immediate response to emergencies
**Scope:** Life safety, emergency procedures
**When to use:** First response during incidents
**Example:** "Building Evacuation and Emergency Response Plan"

#### 5. Crisis Management Plan
**Purpose:** Executive-level crisis management
**Scope:** Decision-making, communications, stakeholders
**When to use:** Major incidents requiring executive involvement
**Example:** "Executive Crisis Management Plan"

---

### Viewing BC Plans

#### List View

**Default View:**
- Grid layout showing all plans as cards
- Each card displays: Name, Type, Status, Criticality, Last Updated

**Filters:**
- **Plan Type** - Filter by Comprehensive, Departmental, IT DR, Emergency Response, Crisis Management
- **Status** - Draft, Review, Approved, Active, Archived
- **Criticality** - Critical, High, Medium, Low

**Search:**
- Type in search box to find plans by name or description
- Search is case-insensitive and searches both fields

**Layouts:**
- **Grid View** (default) - Cards in responsive grid
- **List View** - Compact table format

#### Statistics Cards

Top of the page shows:
- **Total Plans** - Number of BC plans
- **Active Plans** - Plans currently active
- **Coverage** - % of business processes covered
- **Avg Maturity** - Average maturity score (0-5)

---

### Creating a BC Plan

#### Step 1: Plan Information

**Required Fields:**
- **Name*** - Plan title (e.g., "Main BC Plan 2025")
- **Description*** - Brief overview of plan scope and purpose
- **Plan Type*** - Select from 5 types
- **Status*** - Initial status (usually "Draft")

**Optional Fields:**
- **Version** - Plan version number
- **Owner** - Responsible person/department
- **Last Review Date** - When plan was last reviewed
- **Next Review Date** - When plan should be reviewed next
- **Review Frequency** - Daily, Weekly, Monthly, Quarterly, Annually

#### Step 2: Recovery Objectives

**RTO (Recovery Time Objective):**
- Maximum acceptable time to restore a process/system
- Measured in hours
- Example: RTO of 4 hours means system must be restored within 4 hours
- **Validation:** RTO must be ≤ MTPD

**RPO (Recovery Point Objective):**
- Maximum acceptable amount of data loss
- Measured in hours (how far back to restore)
- Example: RPO of 2 hours means max 2 hours of data loss acceptable
- **Validation:** RPO should be ≤ RTO

**MTPD (Maximum Tolerable Period of Disruption):**
- Absolute deadline before unacceptable consequences
- Measured in hours
- Example: MTPD of 24 hours means process must resume within 24 hours max
- **Validation:** MTPD must be > RTO

**Real Example:**
```
E-commerce Website:
- RTO: 2 hours (site must be back online within 2 hours)
- RPO: 15 minutes (max 15 min of orders can be lost)
- MTPD: 8 hours (absolute deadline before major revenue loss)
```

#### Step 3: Strategy

Select primary recovery strategy type:
- **Prevention** - Prevent disruptions (backups, redundancy)
- **Mitigation** - Reduce impact of disruptions
- **Recovery** - Restore after disruption
- **Transfer** - Transfer risk (insurance, outsourcing)

#### Step 4: Resources

**Personnel:**
- List key personnel required
- Roles: BC Manager, IT Lead, Operations Manager, etc.

**Technology:**
- Systems, servers, applications needed
- Backup systems, alternative sites

**Documentation:**
- Attach relevant documents
- Procedures, contact lists, recovery steps

---

### Editing a BC Plan

1. Open plan detail page
2. Click **"Edit"** button (top right)
3. Modify fields as needed
4. Click **"Save Changes"**

**Note:** Editing an approved/active plan may require re-approval.

---

### Deleting a BC Plan

⚠️ **Warning:** Deletion is permanent and removes all associated strategies and actions.

1. Open plan detail page
2. Click **"Delete"** button
3. Confirm deletion in modal
4. Plan is permanently deleted

**Recommendation:** Use **Archive** instead of Delete to preserve history.

---

### Archiving a BC Plan

**When to Archive:**
- Plan is outdated or superseded
- Plan no longer relevant
- Keep for historical records

**How to Archive:**
1. Open plan detail page
2. Click **"Archive"** button
3. Confirm archiving
4. Plan moved to "Archived" status

**View Archived Plans:**
- Use Status filter → "Archived"
- Archived plans can be viewed but not edited
- Can be restored if needed

---

### Cloning a BC Plan

**Use Case:** Create a new plan based on existing template

**How to Clone:**
1. Open plan detail page
2. Click **"Clone"** button
3. New plan created with "(Copy)" suffix
4. Edit cloned plan as needed

**What's Cloned:**
- All plan details
- Recovery strategies
- Action plans
- Resources

**What's NOT Cloned:**
- Status (resets to "Draft")
- Approval history
- Version history

---

## 4. Recovery Strategies

### What are Recovery Strategies?

Recovery strategies define **HOW** you will respond to and recover from different disruption scenarios.

### Strategy Types

#### 1. Alternative Site
**Description:** Backup location for operations
**Examples:** Secondary office, remote datacenter, cloud infrastructure
**When to use:** Primary site unavailable
**Resources needed:** Physical space, equipment, connectivity

#### 2. Manual Workarounds
**Description:** Manual processes when systems unavailable
**Examples:** Paper forms, manual calculations, phone calls
**When to use:** Short-term system outages
**Resources needed:** Printed procedures, staff training

#### 3. Reciprocal Arrangement
**Description:** Agreement with similar organization to share resources
**Examples:** Partner company provides temporary space/systems
**When to use:** Cost-effective backup for rare disasters
**Resources needed:** Formal agreements, compatible systems

#### 4. Mobile Site
**Description:** Portable recovery facilities (trailers, tents)
**Examples:** Mobile command centers, temporary offices
**When to use:** Disasters affecting large areas
**Resources needed:** Mobile units, generators, satellite communications

#### 5. Third-Party Services
**Description:** Commercial recovery services (hot site, warm site, cold site)
**Examples:** Disaster recovery vendors, cloud providers
**When to use:** Critical systems requiring guaranteed recovery
**Resources needed:** Contracts, SLAs, periodic testing

#### 6. Data Backup
**Description:** Regular backup and restore procedures
**Examples:** Daily backups, replication, snapshots
**When to use:** Data loss scenarios
**Resources needed:** Backup systems, offsite storage, restore procedures

---

### Adding a Recovery Strategy

1. Open plan detail page
2. Go to **"Strategies"** tab
3. Click **"Add Strategy"** button
4. Fill in strategy form:
   - **Strategy Name** - Descriptive name
   - **Strategy Type** - Select from 6 types
   - **Description** - Detailed explanation
   - **Resources Required** - Personnel, technology, facilities
   - **Estimated Cost** - Implementation and maintenance costs
   - **Implementation Time** - Hours needed to implement
   - **Dependencies** - Other strategies or systems required
5. Click **"Create Strategy"**

### Editing/Deleting Strategies

- Click **"Edit"** icon on strategy card
- Click **"Delete"** icon to remove (with confirmation)

### Testing Strategies

**Record Test Results:**
1. Open strategy detail
2. Click **"Record Test"**
3. Enter test details:
   - Test date
   - Test results (success/failure)
   - Issues found
   - Improvements needed
4. Save test results

**Test History:**
- View all previous tests
- Track effectiveness over time
- Identify recurring issues

---

## 5. Action Plans

### What are Action Plans?

Action Plans are **specific tasks** required to implement, test, and maintain your BC strategies.

### Action Types

#### 1. Preventive Actions
**Purpose:** Prevent disruptions from occurring
**Examples:**
- Install redundant power supplies
- Implement regular backups
- Train staff on procedures
- Maintain equipment

#### 2. Detective Actions
**Purpose:** Detect disruptions quickly
**Examples:**
- Set up monitoring alerts
- Regular system checks
- Audit logs review
- Incident detection procedures

#### 3. Corrective Actions
**Purpose:** Correct issues before they become major
**Examples:**
- Fix vulnerabilities
- Update outdated systems
- Address audit findings
- Resolve policy gaps

#### 4. Recovery Actions
**Purpose:** Recover after a disruption
**Examples:**
- Restore from backups
- Failover to alternate site
- Activate recovery team
- Execute recovery procedures

---

### Adding an Action Plan

1. Open plan detail page
2. Go to **"Actions"** tab
3. Click **"Add Action"** button
4. Fill in action form:

   **Basic Information:**
   - **Action Title*** - Short, descriptive title
   - **Action Type*** - Preventive, Detective, Corrective, Recovery
   - **Priority*** - Critical, High, Medium, Low
   - **Description*** - Detailed explanation

   **Responsibility:**
   - **Responsible Party*** - Person/team responsible
   - **Backup Responsible** - Backup person

   **Timeline:**
   - **Start Date** - When action begins
   - **Target Date** - Deadline for completion
   - **Completion Date** - Actual completion (filled after done)

   **Progress:**
   - **Status*** - Not Started, In Progress, Completed, Delayed, Cancelled
   - **Progress Percentage** - 0-100%

   **Dependencies:**
   - **Depends On** - Actions that must complete first
   - **Blocks** - Actions blocked by this one

5. Click **"Create Action"**

---

### Managing Actions

#### Mark Action Complete

1. Open action detail
2. Click **"Mark Complete"** button
3. Enter completion date
4. Add completion notes
5. Save

#### Update Progress

1. Open action detail
2. Update **Progress Percentage** slider
3. Add progress notes
4. Save

#### View Overdue Actions

- Use **"Overdue"** filter on Actions tab
- Shows actions past target date
- Sorted by priority

#### View My Actions

- Filter by **Responsible Party** = Your name
- See all actions assigned to you
- Across all plans

---

## 6. Plan Approval Workflow

### Plan Lifecycle

```
Draft → Review → Approved → Active → (Archived)
```

### Status Descriptions

#### 1. Draft
**Description:** Plan is being created/edited
**Who can edit:** Plan owner and editors
**Next step:** Submit for review

#### 2. Review
**Description:** Plan is under review by stakeholders
**Who can edit:** Plan owner (limited changes)
**Next step:** Approve or send back to draft

#### 3. Approved
**Description:** Plan has been approved by management
**Who can edit:** Requires re-approval after edits
**Next step:** Activate plan

#### 4. Active
**Description:** Plan is currently in effect
**Who can edit:** Requires change management process
**Next step:** Update or archive

#### 5. Archived
**Description:** Plan is no longer active (historical)
**Who can edit:** Read-only
**Next step:** Can be cloned for new plan

---

### Approval Process

#### Submitting for Approval

**Prerequisites:**
- Plan has required information filled
- At least one recovery strategy defined
- Critical action plans created

**Steps:**
1. Open plan (must be in Draft status)
2. Click **"Submit for Review"** button
3. Enter submission notes
4. Select reviewers/approvers
5. Click **"Submit"**
6. Status changes to "Review"
7. Reviewers receive notification

#### Approving a Plan

**Who can approve:** Designated approvers (usually management)

**Steps:**
1. Open plan (must be in Review status)
2. Review plan details, strategies, actions
3. Click **"Approve"** button
4. Enter approval comments
5. Click **"Confirm Approval"**
6. Status changes to "Approved"
7. Plan owner receives notification

#### Rejecting a Plan

**Steps:**
1. Open plan (in Review status)
2. Click **"Reject"** button
3. Enter rejection reason (required)
4. Click **"Confirm Rejection"**
5. Status reverts to "Draft"
6. Plan owner receives notification with feedback

#### Activating a Plan

**Prerequisites:** Plan must be "Approved"

**Steps:**
1. Open plan
2. Click **"Activate"** button
3. Confirm activation
4. Status changes to "Active"
5. Plan is now the official BC plan

**Note:** Only one plan of each type should be "Active" at a time.

---

## 7. Analytics Dashboard

### Accessing Analytics

Navigate to: **Planning → Analytics**

### Dashboard Sections

#### 1. Executive Summary

**4 Key Metrics:**

**Total Plans**
- Count of all BC plans
- Breakdown by type
- Trend indicator

**Maturity Score (0-5)**
- Overall planning maturity
- Based on 5 categories
- Target vs Current score

**Coverage (%)**
- % of business processes with BC plans
- Critical processes covered
- Gap identification

**Critical Gaps**
- Number of high-priority gaps
- Areas needing attention
- Impact assessment

---

#### 2. Maturity Assessment

**Radar Chart Visualization:**

**5 Categories Evaluated:**

1. **Management Support (0-5)**
   - Executive sponsorship
   - Budget allocation
   - Resource commitment

2. **Documentation (0-5)**
   - Plan completeness
   - Document quality
   - Version control

3. **Training (0-5)**
   - Staff awareness
   - Training programs
   - Competency levels

4. **Testing (0-5)**
   - Test frequency
   - Test coverage
   - Test effectiveness

5. **Integration (0-5)**
   - BIA alignment
   - Risk alignment
   - Process integration

**Scoring:**
- **Level 1** - Initial (ad hoc)
- **Level 2** - Managed (documented)
- **Level 3** - Defined (standardized)
- **Level 4** - Quantitatively Managed (measured)
- **Level 5** - Optimizing (continuous improvement)

**How to Improve:**
- Click on each category for recommendations
- View specific improvement actions
- Track progress over time

---

#### 3. Coverage Matrix

**Shows:** Which business processes are covered by BC plans

**Table Columns:**
- **Business Process** - Name of process
- **Criticality** - Critical, High, Medium, Low
- **BC Plan** - Associated plan (or "Not Covered")
- **Coverage %** - How well covered (0-100%)
- **RTO** - Recovery time objective
- **Status** - Plan status

**Color Coding:**
- 🟢 Green - Well covered (80-100%)
- 🟡 Yellow - Partially covered (50-79%)
- 🔴 Red - Poorly covered (0-49%)

**Actions:**
- Click process to see details
- Click "Create Plan" to cover gaps
- Export matrix to Excel

---

#### 4. Gap Analysis

**Purpose:** Identify areas needing improvement

**Gap Categories:**
- **Missing Plans** - Critical processes without plans
- **Incomplete Plans** - Plans missing key elements
- **Outdated Plans** - Plans not reviewed recently
- **Untested Strategies** - Strategies never tested
- **Unassigned Actions** - Actions without responsible party
- **Overdue Actions** - Actions past deadline

**Each Gap Shows:**
- **Description** - What's missing/wrong
- **Impact** - Potential consequences
- **Priority** - Critical, High, Medium, Low
- **Category** - Type of gap
- **Recommendation** - How to fix
- **Estimated Effort** - Time to resolve

**Sorting:**
- By priority (default)
- By impact
- By category
- By estimated effort

**Actions:**
- Click gap to see full details
- Click "Resolve" to create action plan
- Mark as "Acknowledged" if accepting risk

---

#### 5. Implementation Timeline

**Purpose:** Visualize plan implementation over time

**Bar Chart Showing:**
- **Planned Actions** - Actions scheduled
- **Completed Actions** - Actions finished
- **Overdue Actions** - Actions delayed

**Time Periods:**
- By month (default)
- By quarter
- By week (for short-term view)

**Filters:**
- Date range selector
- Filter by plan
- Filter by action type
- Filter by priority

**Export:**
- Download as PNG image
- Export data to Excel
- Generate PDF report

---

### Exporting Analytics

**Export Options:**

**PDF Report:**
- Executive summary
- All charts and tables
- Formatted for presentations
- Company branding (if configured)

**Excel Spreadsheet:**
- All data tables
- Raw data for analysis
- Pivot tables ready

**How to Export:**
1. Click **"Export"** button
2. Select format (PDF or Excel)
3. Choose sections to include
4. Click **"Generate Export"**
5. Download file

---

### Refreshing Data

**Auto-Refresh:**
- Dashboard data refreshes every 5 minutes automatically

**Manual Refresh:**
- Click **"Refresh"** button anytime
- Useful after making changes
- Shows loading indicator during refresh

---

## 8. Best Practices

### Plan Creation Best Practices

#### 1. Start with BIA
- ✅ Complete Business Impact Analysis first
- ✅ Identify critical processes and their RTOs
- ✅ Use BIA data to prioritize planning

#### 2. Involve Stakeholders
- ✅ Include process owners in planning
- ✅ Get input from IT, operations, finance
- ✅ Executive sponsorship essential

#### 3. Be Realistic
- ✅ Set achievable RTOs and RPOs
- ✅ Consider actual resources available
- ✅ Test assumptions regularly

#### 4. Document Thoroughly
- ✅ Include step-by-step procedures
- ✅ Document contact information
- ✅ Attach relevant diagrams and layouts

#### 5. Keep it Simple
- ✅ Clear, concise language
- ✅ Avoid jargon where possible
- ✅ Use checklists and templates

---

### Strategy Development Best Practices

#### 1. Multiple Strategies
- ✅ Develop strategies for different scenarios
- ✅ Have primary and backup strategies
- ✅ Consider various disruption types

#### 2. Cost-Effective Solutions
- ✅ Balance cost vs recovery speed
- ✅ Consider existing resources first
- ✅ Evaluate ROI of strategies

#### 3. Leverage Technology
- ✅ Use cloud services for flexibility
- ✅ Automate where possible
- ✅ Implement monitoring and alerts

#### 4. Consider Dependencies
- ✅ Map strategy dependencies
- ✅ Ensure strategies work together
- ✅ Address single points of failure

---

### Action Plan Best Practices

#### 1. SMART Actions
- **Specific** - Clear, specific tasks
- **Measurable** - Trackable progress
- **Achievable** - Realistic given resources
- **Relevant** - Aligned with plan goals
- **Time-bound** - Clear deadlines

#### 2. Assign Responsibility
- ✅ Every action has an owner
- ✅ Include backup responsible party
- ✅ Ensure accountability

#### 3. Set Priorities
- ✅ Focus on critical actions first
- ✅ Use priority levels consistently
- ✅ Review priorities regularly

#### 4. Track Progress
- ✅ Update progress percentage regularly
- ✅ Add status notes
- ✅ Communicate delays immediately

---

### Testing Best Practices

#### 1. Regular Testing
- ✅ Test plans at least annually
- ✅ Test strategies after any major change
- ✅ Test critical plans more frequently

#### 2. Vary Test Types
- **Tabletop Exercises** - Discussion-based
- **Walkthroughs** - Step through procedures
- **Simulations** - Practice without disruption
- **Full Tests** - Actual failover/recovery

#### 3. Document Results
- ✅ Record all test findings
- ✅ Document issues discovered
- ✅ Create action plans for improvements

#### 4. Learn and Improve
- ✅ Review test results with team
- ✅ Update plans based on findings
- ✅ Share lessons learned

---

### Review and Maintenance

#### 1. Regular Reviews
- ✅ Review plans on schedule (quarterly recommended)
- ✅ Update after organizational changes
- ✅ Review after any incident (even minor)

#### 2. Version Control
- ✅ Track version numbers
- ✅ Document changes made
- ✅ Maintain version history

#### 3. Keep Current
- ✅ Update contact information immediately
- ✅ Revise when processes change
- ✅ Ensure strategies still viable

#### 4. Training and Awareness
- ✅ Train staff on their roles
- ✅ Communicate plan updates
- ✅ Maintain awareness program

---

## 9. Troubleshooting

### Common Issues and Solutions

#### Issue: Plan won't save
**Symptoms:** Error message when clicking "Save"
**Possible Causes:**
- Required fields not filled
- RTO/RPO/MTPD validation errors
- Network connectivity issue

**Solutions:**
1. Check all required fields (marked with *)
2. Verify RTO ≤ MTPD and RPO ≤ RTO
3. Check internet connection
4. Try refreshing page and re-entering data

---

#### Issue: Can't approve plan
**Symptoms:** Approve button disabled or not visible
**Possible Causes:**
- Plan not in "Review" status
- Don't have approval permissions
- Plan missing required elements

**Solutions:**
1. Check plan status - must be "Review"
2. Verify you have "Approver" role
3. Ensure plan has at least one strategy and action
4. Contact administrator if permissions issue

---

#### Issue: Analytics not loading
**Symptoms:** Dashboard shows loading spinner indefinitely
**Possible Causes:**
- Backend service issue
- Large dataset taking time
- Browser cache issue

**Solutions:**
1. Click "Refresh" button
2. Clear browser cache and reload
3. Try different browser
4. Contact IT support if persists

---

#### Issue: Export fails
**Symptoms:** Export button doesn't generate file
**Possible Causes:**
- Popup blocker enabled
- Too much data to export
- Format not supported

**Solutions:**
1. Disable popup blocker for this site
2. Try exporting smaller date range
3. Try different export format (PDF vs Excel)
4. Check browser console for errors

---

#### Issue: Search not working
**Symptoms:** Search returns no results or wrong results
**Possible Causes:**
- Typo in search term
- Filters applied
- Search index needs update

**Solutions:**
1. Check spelling
2. Clear all filters
3. Refresh page
4. Try simpler search terms

---

## 10. FAQ

### General Questions

**Q: How many BC plans should we have?**
**A:** At minimum, one Comprehensive plan. Add Departmental plans for critical departments and IT Disaster Recovery plan for IT systems. Typical organization: 3-10 plans.

**Q: What's the difference between a plan and a strategy?**
**A:** A **plan** is the overall document covering a scope (department, process). A **strategy** is a specific approach within a plan (alternative site, backups). One plan contains multiple strategies.

**Q: Can multiple people edit the same plan?**
**A:** Yes, but not simultaneously. Changes are saved when you click "Save." Last save wins. Use version control and communicate with team.

**Q: How often should plans be reviewed?**
**A:** Minimum annually per ISO 22301. Critical plans quarterly. After any major organizational change, immediately.

---

### Technical Questions

**Q: Where is plan data stored?**
**A:** Securely in the platform database. Regular backups performed. Contact IT for specific backup/retention policies.

**Q: Can I import/export plans?**
**A:** Yes. Export to PDF/Excel from analytics. Import from Excel template (contact admin for template).

**Q: Does the system support version history?**
**A:** Yes. Every change creates a version. View version history on plan detail page → History tab.

**Q: Can I attach documents to plans?**
**A:** Yes. In plan form, Resources section → Documentation. Upload files up to 50MB each. Supports PDF, Word, Excel, images.

---

### Workflow Questions

**Q: Who can approve plans?**
**A:** Users with "BC Manager" or "Approver" role. Contact administrator to request approval permissions.

**Q: Can I skip the review step?**
**A:** No, per ISO 22301 requirements, all plans must be reviewed and approved before activation.

**Q: What happens to actions when a plan is archived?**
**A:** Actions remain for historical record but are read-only. Can't add new actions to archived plans.

**Q: Can I have multiple active plans of the same type?**
**A:** Technically yes, but not recommended. Only one plan of each type should be "Active" to avoid confusion.

---

### Integration Questions

**Q: How does Planning integrate with BIA?**
**A:** Plans can be linked to business processes from BIA. System shows alignment and suggests plans based on BIA critical processes.

**Q: How does Planning integrate with Risk?**
**A:** Plans can be linked to risk assessments. System shows which risks are covered by plans and identifies gaps.

**Q: Can I sync data from other modules?**
**A:** Yes. Use "Sync" button in plan detail page. Syncs related processes from BIA, risks from Risk module, and assets from Inventory.

---

### Reporting Questions

**Q: What reports are available?**
**A:** Analytics dashboard provides: Executive Summary, Maturity Assessment, Coverage Matrix, Gap Analysis, Implementation Timeline. All exportable to PDF/Excel.

**Q: Can I customize reports?**
**A:** Yes. Use filters to customize date ranges, plans included, action types. Export provides further customization options.

**Q: Can I schedule automatic reports?**
**A:** Not currently in UI. Contact administrator to set up scheduled email reports.

---

### Support Questions

**Q: I found a bug. Where do I report it?**
**A:** Contact IT Support with: Description, Steps to reproduce, Screenshots, Browser/OS info.

**Q: I have a feature request. How do I submit it?**
**A:** Use the Feedback button (top right) or email product team with detailed description of desired feature and use case.

**Q: Where can I get training?**
**A:** Training videos available in Help menu. Live training sessions scheduled quarterly. Contact Training team to register.

**Q: Is there a mobile app?**
**A:** Not currently. Web interface is mobile-responsive and works on tablets/phones. Native mobile app planned for future.

---

## 📞 Need Help?

### Support Channels

**Technical Support:**
📧 Email: support@aiplatform-iso.com
📞 Phone: 1-800-XXX-XXXX
🕒 Hours: Monday-Friday, 9 AM - 5 PM EST

**Documentation:**
📚 Online Help: https://docs.aiplatform-iso.com
🎥 Video Tutorials: https://training.aiplatform-iso.com

**Community:**
💬 User Forum: https://community.aiplatform-iso.com
📣 Release Notes: https://releases.aiplatform-iso.com

---

## 📄 Appendix

### Glossary

**BC (Business Continuity)** - Capability to continue operations during and after disruption

**BCP (Business Continuity Plan)** - Documented procedures to guide response and recovery

**RTO (Recovery Time Objective)** - Target time to restore a process after disruption

**RPO (Recovery Point Objective)** - Maximum acceptable data loss measured in time

**MTPD (Maximum Tolerable Period of Disruption)** - Maximum time before unacceptable consequences

**BIA (Business Impact Analysis)** - Process to identify critical functions and impacts of disruption

**ISO 22301** - International standard for Business Continuity Management Systems

---

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl/Cmd + K | Open search |
| Ctrl/Cmd + N | Create new plan |
| Ctrl/Cmd + S | Save current form |
| Esc | Close modal/dialog |
| Ctrl/Cmd + / | Show keyboard shortcuts |

---

### Related Standards

**ISO 22301:2019** - Security and resilience — Business continuity management systems
**ISO 27001:2013** - Information security management
**ISO 9001:2015** - Quality management systems
**NIST SP 800-34** - Contingency Planning Guide for IT Systems
**BS 25999** - Business Continuity Management (superseded by ISO 22301)

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-22
**Next Review:** 2026-01-22
**Document Owner:** Product Team

---

**End of User Guide**

For latest version, visit: https://docs.aiplatform-iso.com/planning/user-guide
