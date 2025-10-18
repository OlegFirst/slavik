# 📋 WEEK 4 - Documents Module Execution Plan

**Created:** 2025-10-19
**Target:** Complete Documents & Living Docs module
**Strategy:** Parallel agent execution
**Backend Status:** ✅ Production-ready (8024 port, 25+ endpoints, AI-powered)

---

## 🎯 BACKEND RESEARCH COMPLETE

### Service Details:
- **Location:** `/platform_services/bcm_domain/services/documents_service/`
- **Port:** 8024
- **API Base:** `http://localhost:8024/api/documents`
- **Database:** PostgreSQL schema `documents`
- **ISO Compliance:** ISO 22301 Clause 7.5

### Key Features Available:
- ✅ 8 database models (Document, DocumentAccess, DocumentShare, DocumentApproval, etc.)
- ✅ 25+ REST endpoints (CRUD, workflow, versions, approvals, sharing, retention)
- ✅ AI/NLP processing (extraction, classification, analysis, comparison)
- ✅ DocumentsSpecialistAI integration
- ✅ Living Docs integration (port 8034)
- ✅ Event bus integration (RabbitMQ)
- ✅ Workflow Intelligence framework
- ✅ Complete audit trail

---

## 📊 ARCHITECTURE OVERVIEW

### Document Lifecycle:
```
DRAFT → UNDER_REVIEW → APPROVED → PUBLISHED → ARCHIVED/SUPERSEDED/OBSOLETE
```

### Document Types (22 types):
- Policy, Procedure, Plan, Risk Assessment, BIA
- Exercise Report, Audit Report, Management Review
- Form, Template, Checklist, Contact List
- Communication, Training Material, Evidence
- Contract, SOP, Report, Presentation, Spreadsheet, Other

### Classification Levels:
- Public → Internal → Confidential → Restricted → Highly Restricted

### Core Workflows:
1. **Lifecycle Workflow** - State transitions
2. **Approval Workflow** - Multi-stage approvals
3. **Retention Workflow** - Compliance policies

---

## 🎯 WEEK 4 PARALLEL EXECUTION PLAN

### Phase 1: Foundation (3 agents in parallel)

#### Agent 1: Types & Enums
**File:** `/src/types/documents.ts`
**Task:** Create all TypeScript types and enums
**Deliverables:**
- 6 enums (DocumentType, DocumentStatus, DocumentClassification, AccessAction, SharePermission, ApprovalStatus)
- 10+ interfaces (Document, DocumentCreate, DocumentUpdate, DocumentApproval, DocumentShare, RetentionPolicy, etc.)
- Complete type coverage for all backend models

#### Agent 2: Validation Schemas
**File:** `/src/lib/validations/document.ts`
**Task:** Create Zod validation schemas
**Deliverables:**
- documentCreateSchema
- documentUpdateSchema
- approvalRequestSchema
- shareRequestSchema
- retentionPolicySchema
- Business rules validation

#### Agent 3: API Client
**File:** `/src/lib/api/documents-client.ts`
**Task:** Create API client with all endpoints
**Deliverables:**
- 25+ methods covering all endpoints
- Error handling
- TypeScript typed
- Pattern consistent with bia-client.ts

---

### Phase 2: Data Layer (4 agents in parallel)

#### Agent 4: Core CRUD Hooks
**Files:**
- `/src/hooks/documents/useDocuments.ts` (list with filters)
- `/src/hooks/documents/useDocument.ts` (single document)
- `/src/hooks/documents/useCreateDocument.ts` (create + upload)
- `/src/hooks/documents/useUpdateDocument.ts` (update metadata)
- `/src/hooks/documents/useDeleteDocument.ts` (soft delete)

#### Agent 5: Workflow Hooks
**Files:**
- `/src/hooks/documents/useDocumentWorkflow.ts` (execute actions, get status)
- `/src/hooks/documents/useDocumentVersions.ts` (versions, comparison)

#### Agent 6: Collaboration Hooks
**Files:**
- `/src/hooks/documents/useDocumentApprovals.ts` (request, respond, list)
- `/src/hooks/documents/useDocumentSharing.ts` (share, list shares)

#### Agent 7: Retention & Audit Hooks
**Files:**
- `/src/hooks/documents/useRetentionPolicies.ts` (policies, status)
- `/src/hooks/documents/useDocumentAudit.ts` (access log)
- `/src/hooks/documents/index.ts` (barrel export)

---

### Phase 3: UI Components (6 agents in parallel)

#### Agent 8: Badge Components
**Files:**
- `/src/components/documents/DocumentTypeBadge.tsx`
- `/src/components/documents/DocumentStatusBadge.tsx`
- `/src/components/documents/ClassificationBadge.tsx`

#### Agent 9: Core Document Components
**Files:**
- `/src/components/documents/DocumentCard.tsx` (list item)
- `/src/components/documents/DocumentList.tsx` (list view with filters)
- `/src/components/documents/DocumentDetail.tsx` (detail view)

#### Agent 10: Form Components
**Files:**
- `/src/components/documents/DocumentForm.tsx` (create/edit metadata)
- `/src/components/documents/DocumentUpload.tsx` (file upload with drag-drop)
- `/src/components/documents/DocumentFilters.tsx` (filter panel)

#### Agent 11: Workflow Components
**Files:**
- `/src/components/documents/WorkflowStatus.tsx` (status display)
- `/src/components/documents/WorkflowActions.tsx` (action buttons)
- `/src/components/documents/WorkflowTimeline.tsx` (history timeline)

#### Agent 12: Version Components
**Files:**
- `/src/components/documents/VersionHistory.tsx` (version list)
- `/src/components/documents/VersionComparison.tsx` (side-by-side diff)

#### Agent 13: Approval & Sharing Components
**Files:**
- `/src/components/documents/ApprovalRequest.tsx` (request approval form)
- `/src/components/documents/ApprovalList.tsx` (approvals list)
- `/src/components/documents/ShareDialog.tsx` (share document dialog)
- `/src/components/documents/ShareList.tsx` (active shares)
- `/src/components/documents/index.ts` (barrel export)

---

### Phase 4: Pages (2 agents in parallel)

#### Agent 14: Main Pages
**Files:**
- `/src/app/(platform)/documents/page.tsx` (document list page)
- `/src/app/(platform)/documents/new/page.tsx` (create document)
- `/src/app/(platform)/documents/[id]/page.tsx` (document detail)
- `/src/app/(platform)/documents/[id]/edit/page.tsx` (edit document)

#### Agent 15: Advanced Pages
**Files:**
- `/src/app/(platform)/documents/[id]/versions/page.tsx` (version history)
- `/src/app/(platform)/documents/retention-policies/page.tsx` (retention management)

---

## 📈 PROGRESSIVE EXECUTION STRATEGY

### Round 1: Foundation (Agents 1-3) - Critical Path
**Why first:** Types needed for API client, validation needed for forms
**Estimated:** ~200 lines each = 600 lines total
**Wait for completion:** Yes (dependencies)

### Round 2: Data Layer (Agents 4-7) - Parallel
**Why second:** Hooks depend on API client and types
**Estimated:** ~150 lines each = 600 lines total
**Wait for completion:** Yes (components need hooks)

### Round 3: UI Components (Agents 8-13) - Parallel
**Why third:** Components depend on hooks and types
**Estimated:** ~300 lines each = 1800 lines total
**Wait for completion:** Yes (pages need components)

### Round 4: Pages (Agents 14-15) - Parallel
**Why last:** Pages integrate everything
**Estimated:** ~150 lines each = 300 lines total
**Wait for completion:** No (can test incrementally)

---

## 🎯 SUCCESS CRITERIA

### Functionality:
- ✅ Create document with metadata
- ✅ Upload file (PDF, DOCX, Excel, images)
- ✅ List documents with filters (type, status, classification, owner, search)
- ✅ View document details
- ✅ Update document metadata
- ✅ Download document file
- ✅ Execute workflow actions (submit, approve, publish, archive)
- ✅ Create new version
- ✅ Compare versions (side-by-side diff)
- ✅ Request approval (multi-stage)
- ✅ Respond to approval (approve/reject)
- ✅ Share document (user or email)
- ✅ Manage retention policies
- ✅ View audit log

### AI Features:
- ✅ Auto-classification on upload
- ✅ Auto-extraction (text, metadata)
- ✅ AI summarization
- ✅ Key phrase extraction
- ✅ Named entity recognition
- ✅ ISO clause mapping
- ✅ Document comparison with similarity score

### UI/UX:
- ✅ Professional design (consistent with BIA module)
- ✅ Responsive layout
- ✅ Loading states
- ✅ Error handling
- ✅ TypeScript strict mode
- ✅ Build successful

---

## 📊 ESTIMATED METRICS

**Code to Write:**
- Types: ~300 lines
- Validation: ~200 lines
- API Client: ~600 lines
- Hooks: ~1200 lines (8 files)
- Components: ~2500 lines (15+ files)
- Pages: ~500 lines (6 files)
- **Total: ~5300 lines**

**Timeline:**
- Round 1 (Foundation): 3 agents → ~30 min
- Round 2 (Data Layer): 4 agents → ~40 min
- Round 3 (UI Components): 6 agents → ~60 min
- Round 4 (Pages): 2 agents → ~20 min
- Testing & Fixes: ~30 min
- **Total: ~3 hours**

---

## 🔧 INTEGRATION POINTS

### With BIA Module:
- Link documents to BIA processes
- Attach BIA reports as documents
- Reference recovery procedures

### With Living Docs:
- AI-powered documentation search
- Personalized documentation pages
- Context-aware examples

### With Plans (Future):
- Link documents to BC plans
- Template-based plan documents
- Plan versioning

---

## 💡 KEY DECISIONS

1. **File Upload Strategy:**
   - Use Next.js API route for file proxy
   - Direct upload to backend /upload endpoint
   - Progress indication
   - File type validation client-side

2. **Document Preview:**
   - PDF preview in browser (PDF.js)
   - DOCX/Excel preview (convert to HTML)
   - Image preview (direct display)
   - Download for other types

3. **Version Comparison:**
   - Side-by-side view
   - Highlight additions (green)
   - Highlight deletions (red)
   - Show similarity score
   - Metadata diff

4. **Approval Workflow:**
   - Visual stage indicator
   - Email notifications (backend)
   - SLA tracking
   - Reminder system

5. **Access Control:**
   - Classification badges prominent
   - Permission-based UI (hide actions)
   - Audit log always visible
   - Share expiration warnings

---

## 🚀 EXECUTION COMMAND

### Round 1: Launch Foundation Agents
```typescript
// Agent 1: Types
// Agent 2: Validation
// Agent 3: API Client
```

### Round 2: Launch Data Layer Agents
```typescript
// Agent 4: Core CRUD Hooks
// Agent 5: Workflow Hooks
// Agent 6: Collaboration Hooks
// Agent 7: Retention & Audit Hooks
```

### Round 3: Launch UI Component Agents
```typescript
// Agent 8: Badge Components
// Agent 9: Core Document Components
// Agent 10: Form Components
// Agent 11: Workflow Components
// Agent 12: Version Components
// Agent 13: Approval & Sharing Components
```

### Round 4: Launch Page Agents
```typescript
// Agent 14: Main Pages
// Agent 15: Advanced Pages
```

---

## 📝 NOTES

**Backend Readiness:** 100% - No backend changes needed
**Pattern Consistency:** Follow BIA module patterns exactly
**No Mocks:** All API integration real
**TypeScript Strict:** Maintain strict mode throughout
**AI Integration:** Backend handles automatically on upload
**Event Bus:** Backend publishes events automatically

---

**ПАРТНЁР, ПЛАН ГОТОВ!** 🎯

Ready to launch Round 1 (Foundation agents)? 🚀
