# UI/UX Documentation

**Section**: User Interface & User Experience
**Last Updated**: 2025-10-09

---

## 📋 Main Technical Specifications

### Current Technical Specification

**[TZ_USER_INTERFACE.md](../../doc-project/TZ_USER_INTERFACE.md)** (35 KB)
- **Location**: `/doc-project/TZ_USER_INTERFACE.md`
- **Status**: ✅ Current (2025-10-09)
- **Content**: Complete web-based user interface with administrator panel
- **Sections**:
  1. Executive Summary
  2. Technical Stack (Next.js 14, TypeScript, Tailwind)
  3. User Interface Structure (10 main sections)
  4. Core Features & Screens
  5. Administrator Panel (10 admin sections)
  6. AI Assistant Integration
  7. Real-Time Features
  8. Mobile Responsiveness
  9. Performance Requirements
  10. Security Requirements
  11. Accessibility (WCAG 2.1 AA)
  12. Internationalization (i18n)
  13. Testing Strategy
  14. Deployment Architecture
  15. Documentation Requirements
  16. Success Metrics
  17. Timeline & Phases (14-21 weeks)
  18. Team Requirements
  19. Risks & Mitigation
  20. Appendices

---

## 📚 Related UI Specifications

### Service-Specific Frontend Specifications

1. **[Learning Service Frontend](../../platform-services/learning-service/FRONTEND_SPECIFICATION.md)** (59 KB)
   - Training and knowledge management interface
   - Video courses, quizzes, certifications
   - Progress tracking

2. **[Digital Twin Frontend](../../platform-services/simulation/digital-twin/docs/FRONTEND_SPECIFICATION.md)** (44 KB)
   - Digital twin simulation interface
   - BIA engine integration
   - Exercise simulators

3. **[Community Service Frontend](../../platform-services/community-service/FRONTEND_SPECIFICATION_SUMMARY.md)** (20 KB)
   - Community portal interface
   - Forums, Q&A, best practices

4. **[Interface Brief](../../interface/FRONTEND_SPECIFICATION_BRIEF.md)** (11 KB)
   - Brief overview of frontend requirements

---

## 🎨 User Scenario Diagrams

Interactive diagrams showing user flows:

### [User Scenarios Diagrams](../../doc-project/diagrams/user-scenarios/)

1. **[BCM_USER_JOURNEY.mmd](../../doc-project/diagrams/user-scenarios/BCM_USER_JOURNEY.mmd)**
   - Complete user journey: BIA → Risk → Plan → Exercise
   - 4 main workflows with AI recommendations

2. **[BIA_DETAILED_WORKFLOW.mmd](../../doc-project/diagrams/user-scenarios/BIA_DETAILED_WORKFLOW.mmd)**
   - Detailed 6-step BIA workflow
   - Sequence diagram with AI analysis

3. **[ADMIN_SERVICE_MONITORING.mmd](../../doc-project/diagrams/user-scenarios/ADMIN_SERVICE_MONITORING.mmd)**
   - Administrator panel monitoring
   - 23 services + infrastructure management

4. **[RISK_ASSESSMENT_FLOW.mmd](../../doc-project/diagrams/user-scenarios/RISK_ASSESSMENT_FLOW.mmd)**
   - Risk assessment process
   - From identification to registration

---

## 🗂️ Historical UI Specifications (Archived)

**Location**: `/_archive/old-ui-specs/`

Old HTML/JSON blueprint files (archived on 2025-10-09):
- `documents_blueprint.html` (16 KB)
- `documents_spec.json` (9 KB)
- `governance_blueprint.html` (32 KB)
- `governance_spec.json` (21 KB)
- `other_blueprint.html` (156 KB)
- `other_spec.json` (95 KB)
- `validation_blueprint.html` (26 KB)
- `validation_spec.json` (17 KB)
- `index.html` (4 KB)

**Note**: These are old specifications and have been superseded by the current `TZ_USER_INTERFACE.md`.

---

## 🎯 Quick Navigation

### For UI/UX Designers

1. **Start here**: [TZ_USER_INTERFACE.md](../../doc-project/TZ_USER_INTERFACE.md)
2. **User flows**: [User Scenarios Diagrams](../../doc-project/diagrams/user-scenarios/)
3. **Service-specific UIs**: See "Related UI Specifications" above

### For Frontend Developers

1. **Technical stack**: [TZ_USER_INTERFACE.md - Section 2](../../doc-project/TZ_USER_INTERFACE.md#2-technical-stack)
2. **Component structure**: [TZ_USER_INTERFACE.md - Section 3](../../doc-project/TZ_USER_INTERFACE.md#3-user-interface-structure)
3. **API integration**: [API Reference](../API_REFERENCE.md)

### For Product Managers

1. **Timeline**: [TZ_USER_INTERFACE.md - Section 17](../../doc-project/TZ_USER_INTERFACE.md#17-timeline--phases)
2. **Success metrics**: [TZ_USER_INTERFACE.md - Section 16](../../doc-project/TZ_USER_INTERFACE.md#16-success-metrics)
3. **Team requirements**: [TZ_USER_INTERFACE.md - Section 18](../../doc-project/TZ_USER_INTERFACE.md#18-team-requirements)

---

## 📊 UI Specifications Summary

| Document | Size | Type | Status |
|----------|------|------|--------|
| TZ_USER_INTERFACE.md | 35 KB | Main Technical Specification | ✅ Current |
| Learning Service Frontend | 59 KB | Service-specific | ✅ Active |
| Digital Twin Frontend | 44 KB | Service-specific | ✅ Active |
| Community Service Frontend | 20 KB | Service-specific | ✅ Active |
| Interface Brief | 11 KB | Overview | ✅ Active |
| Old HTML/JSON specs | 400+ KB | Legacy | 📦 Archived |

**Total**: 169 KB of current UI specifications

---

## 🔗 Related Documentation

- [**Architecture**](../ARCHITECTURE.md) - Platform architecture
- [**API Reference**](../API_REFERENCE.md) - 150+ API endpoints
- [**Deployment Guide**](../DEPLOYMENT_GUIDE.md) - Deployment instructions
- [**Standards Compliance**](../STANDARDS_COMPLIANCE.md) - ISO 22301, WCAG 2.1 AA
- [**All Diagrams**](../../doc-project/diagrams/README.md) - 36 interactive diagrams

---

## 📝 Document History

| Date | Action | Details |
|------|--------|---------|
| 2025-10-09 | Reorganization | TZ_USER_INTERFACE.md moved to /doc-project/ for consistency |
| 2025-10-09 | Archival | Old HTML/JSON specs moved to /_archive/old-ui-specs/ |
| 2025-10-09 | Created | This README.md created to document UI section structure |
| 2025-10-09 | Current | TZ_USER_INTERFACE.md is the authoritative UI specification |

---

**Note**: All UI documentation is current and actively maintained. The main technical specification is located at `/doc-project/TZ_USER_INTERFACE.md` for consistency with other technical specifications.

**Last Updated**: 2025-10-09
