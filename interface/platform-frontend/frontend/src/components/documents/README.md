# Documents Module Components

Core UI components for the Documents Management Module (Week 4 Development).

## Components

### 1. DocumentCard

A comprehensive card component for displaying document summaries in list or grid views.

**Features:**
- Grid and list layout modes
- Document metadata display (title, description, owner, dates)
- Status and classification badges
- Version information with "Latest" indicator
- Approval status indicators
- Controlled document markers
- Hover quick actions (edit, share, archive)
- Full keyboard accessibility

**Usage:**

```tsx
import { DocumentCard } from '@/components/documents';

<DocumentCard
  document={document}
  layout="grid" // or "list"
  onClick={(doc) => navigate(`/documents/${doc.document_id}`)}
  onEdit={(doc) => setEditingDocument(doc)}
  onShare={(doc) => setShareDialog(doc)}
  onArchive={(doc) => handleArchive(doc)}
  showActions={true}
/>
```

### 2. DocumentStatusBadge

Status badge component with color coding for document lifecycle states.

**Supported Statuses:**
- DRAFT (gray)
- UNDER_REVIEW (amber)
- APPROVED (green)
- PUBLISHED (blue)
- ARCHIVED (slate)
- SUPERSEDED (purple)
- OBSOLETE (red)

**Usage:**

```tsx
import { DocumentStatusBadge } from '@/components/documents';

<DocumentStatusBadge
  status={DocumentStatus.PUBLISHED}
  showIcon={true}
  size="md" // "sm" | "md" | "lg"
/>
```

**Helper Functions:**

```tsx
import { getStatusConfig, getStatusProgress } from '@/components/documents';

// Get full configuration
const config = getStatusConfig(DocumentStatus.APPROVED);
// { label, description, bgClass, textClass, borderClass, Icon }

// Get workflow progress (0-100)
const progress = getStatusProgress(DocumentStatus.APPROVED); // 60
```

### 3. DocumentTypeIcon

Icon component for document types with color-coded categories.

**Supported Types (21 total):**
- Governance: POLICY, PROCEDURE, SOP
- Planning: PLAN, BIA, RISK_ASSESSMENT
- Reports: REPORT, AUDIT_REPORT, EXERCISE_REPORT, MANAGEMENT_REVIEW
- Templates: TEMPLATE, FORM, CHECKLIST
- Communication: COMMUNICATION, CONTACT_LIST, PRESENTATION
- Training: TRAINING_MATERIAL
- Evidence: EVIDENCE, CONTRACT
- Data: SPREADSHEET
- Other: OTHER

**Usage:**

```tsx
import { DocumentTypeIcon } from '@/components/documents';

// Icon only
<DocumentTypeIcon
  type={DocumentType.POLICY}
  size="md" // "sm" | "md" | "lg"
  showTooltip={true}
/>

// With label
<DocumentTypeIcon
  type={DocumentType.PROCEDURE}
  size="lg"
  showLabel={true}
/>
```

**Helper Functions:**

```tsx
import { getTypeConfig, getTypeCategory } from '@/components/documents';

// Get full configuration
const config = getTypeConfig(DocumentType.POLICY);
// { label, description, Icon, colorClass, bgClass }

// Get category grouping
const category = getTypeCategory(DocumentType.POLICY); // "Governance"
```

### 4. ClassificationBadge

Standalone badge for document classification levels (exported from DocumentCard).

**Classification Levels:**
- PUBLIC (gray)
- INTERNAL (blue)
- CONFIDENTIAL (orange)
- RESTRICTED (red)
- HIGHLY_RESTRICTED (dark red)

**Usage:**

```tsx
import { ClassificationBadge } from '@/components/documents';

<ClassificationBadge
  classification={DocumentClassification.CONFIDENTIAL}
  size="sm" // "sm" | "md"
/>
```

## Design System

### Colors

The components use Anthropic's warm color scheme with orange (#D97706) accents:
- Primary accent: Orange for hover states and important elements
- Status colors: Semantic colors (gray, amber, green, blue, slate, purple, red)
- Classification colors: Security-level appropriate (gray, blue, orange, red)

### Spacing

Consistent Tailwind spacing scale:
- Small: `px-2 py-0.5`, `gap-1`
- Medium: `px-3 py-1`, `gap-1.5`
- Large: `px-4 py-1.5`, `gap-2`

### Transitions

Smooth transitions throughout:
- Color transitions: `transition-colors duration-200`
- Shadow transitions: `transition-all duration-200`
- Opacity transitions: `transition-opacity duration-200`

### Accessibility

All components include:
- ARIA labels and roles
- Keyboard navigation support
- Focus indicators
- Tooltips with descriptions
- High contrast color ratios
- Semantic HTML structure

## Dependencies

### Required Packages
- `lucide-react`: Icon library
- `date-fns`: Date formatting utilities
- `tailwindcss`: Styling framework
- `clsx` + `tailwind-merge`: className utilities

### Internal Dependencies
- `@/types/documents`: Type definitions
- `@/lib/utils`: cn() utility function

## File Structure

```
src/components/documents/
├── DocumentCard.tsx              (352 lines)
├── DocumentStatusBadge.tsx       (165 lines)
├── DocumentTypeIcon.tsx          (317 lines)
├── index.ts                      (export barrel)
└── README.md                     (this file)
```

## Development Notes

1. All components use the `'use client'` directive for Next.js App Router
2. TypeScript interfaces are exported for all component props
3. JSDoc comments document all public APIs
4. Components follow established patterns from BIA module
5. Responsive design with mobile-first approach
6. Dark mode support can be added by extending Tailwind classes

## Testing Considerations

When testing these components:
1. Test all status/type enum values
2. Verify accessibility with screen readers
3. Test keyboard navigation
4. Check responsive behavior at different breakpoints
5. Verify hover states and transitions
6. Test with long text values (truncation)
7. Verify color contrast ratios meet WCAG standards

## Future Enhancements

Potential improvements for future iterations:
- Dark mode support
- Animation variants
- Custom icon support
- Drag and drop support for DocumentCard
- Bulk selection mode
- Virtualized list support for large datasets
- Export to PDF/Excel functionality
