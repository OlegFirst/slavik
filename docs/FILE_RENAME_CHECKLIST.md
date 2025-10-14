# File Rename Checklist: Dashes to Underscores

**Why**: Python cannot read filenames with dashes (-), need to use underscores (_)

**Status**: READY TO EXECUTE

---

## Files to Rename

All HTML files in `/Users/MD/AI-Platform-ISO/docs/` directory:

### 1. Deep-Dive Documentation Pages (10 files)

| Current Name | New Name | Status |
|--------------|----------|--------|
| `service-catalog-visual.html` | `service_catalog_visual.html` | Pending |
| `platform-services-overview.html` | `platform_services_overview.html` | Pending |
| `ai-foundation.html` | `ai_foundation.html` | Pending |
| `workflow-intelligence.html` | `workflow_intelligence.html` | Pending |
| `ace-service.html` | `ace_service.html` | Pending |
| `eventbus-choreography.html` | `eventbus_choreography.html` | Pending |
| `governance-layer.html` | `governance_layer.html` | Pending |
| `predictive-intelligence.html` | `predictive_intelligence.html` | Pending |
| `expertise-center.html` | `expertise_center.html` | Pending |
| `collective-intelligence.html` | `collective_intelligence.html` | Pending |

### 2. Other Documentation Pages

| Current Name | New Name | Status |
|--------------|----------|--------|
| `bcm-philosophy.html` | `bcm_philosophy.html` | Pending |
| `platform-overview.html` | `platform_overview.html` | Pending |
| `decision-center.html` | `decision_center.html` | Pending |
| `mio-manager.html` | `mio_manager.html` | Pending |
| `business-flow.html` | `business_flow.html` | Pending |

**Total Files**: 15 files to rename

---

## Manual Rename Instructions (macOS Finder)

1. Open Finder
2. Navigate to: `/Users/MD/AI-Platform-ISO/docs/`
3. For each file:
   - Right-click on file
   - Select "Rename"
   - Replace ALL dashes (-) with underscores (_)
   - Press Enter

---

## Terminal Rename Script (Alternative)

```bash
cd /Users/MD/AI-Platform-ISO/docs

# Rename all HTML files with dashes to underscores
for file in *-*.html; do
  [ -f "$file" ] || continue
  new_name="${file//-/_}"
  mv "$file" "$new_name"
  echo "Renamed: $file → $new_name"
done
```

---

## Files Requiring Link Updates After Rename

### 1. index.html

**Lines to Update**:

```html
<!-- Navigation (lines 16-27) -->
<a href="bcm-philosophy.html">BCM Philosophy</a>
<a href="platform-overview.html">Platform Overview</a>
<a href="service-catalog-visual.html">Services</a>
<a href="ai-foundation.html">AI Foundation</a>
<a href="workflow-intelligence.html">Workflow Intelligence</a>
<a href="eventbus-choreography.html">EventBus</a>

<!-- Deep-Dive Documentation (lines 312-370) -->
<a href="service-catalog-visual.html" class="card">
<a href="platform-services-overview.html" class="card">
<a href="ai-foundation.html" class="card">
<a href="workflow-intelligence.html" class="card">
<a href="ace-service.html" class="card">
<a href="eventbus-choreography.html" class="card">
<a href="governance-layer.html" class="card">
<a href="predictive-intelligence.html" class="card">
<a href="expertise-center.html" class="card">
<a href="collective-intelligence.html" class="card">

<!-- Footer (lines 125-128) -->
<a href="business-flow.html">Business Flows</a>
```

**Replacement Pattern**: Replace `-` with `_` in all href attributes

---

### 2. All Deep-Dive Documentation Pages

**Each page contains**:
- Navigation links (top nav bar)
- Footer links
- Internal cross-references

**Example Navigation Block** (appears in ALL 10 deep-dive pages):
```html
<nav>
  <div class="nav-container">
    <a href="index.html" class="nav-logo">AI-Platform-ISO</a>
    <div class="nav-links">
      <a href="index.html">Home</a>
      <a href="bcm-philosophy.html">BCM Philosophy</a>
      <a href="platform-overview.html">Platform Overview</a>
      <a href="service-catalog-visual.html">Services</a>
      <a href="ai-foundation.html">AI Foundation</a>
      <a href="workflow-intelligence.html">Workflow Intelligence</a>
      <a href="eventbus-choreography.html">EventBus</a>
      <a href="architecture.html">Architecture</a>
      <a href="documentation.html">Documentation</a>
    </div>
  </div>
</nav>
```

**Files Requiring Update**:
1. `service_catalog_visual.html` (after rename)
2. `platform_services_overview.html` (after rename)
3. `ai_foundation.html` (after rename)
4. `workflow_intelligence.html` (after rename)
5. `ace_service.html` (after rename)
6. `eventbus_choreography.html` (after rename)
7. `governance_layer.html` (after rename)
8. `predictive_intelligence.html` (after rename)
9. `expertise_center.html` (after rename)
10. `collective_intelligence.html` (after rename)

**Update Required**: Navigation block + Footer links in each file

---

### 3. Cross-References Between Pages

**service_catalog_visual.html** → References other pages:
- Links to individual service deep-dives

**platform_services_overview.html** → References:
- Links to `workflow-intelligence.html`
- Links to `ai-foundation.html`

**Other Pages** → May contain:
- "See also" sections
- Related documentation links
- Integration examples

---

## Batch Find/Replace Strategy

After files are renamed, use batch find/replace across ALL HTML files:

### Pattern 1: Navigation Links
```
Find:    href="bcm-philosophy.html"
Replace: href="bcm_philosophy.html"

Find:    href="platform-overview.html"
Replace: href="platform_overview.html"

Find:    href="service-catalog-visual.html"
Replace: href="service_catalog_visual.html"

Find:    href="ai-foundation.html"
Replace: href="ai_foundation.html"

Find:    href="workflow-intelligence.html"
Replace: href="workflow_intelligence.html"

Find:    href="eventbus-choreography.html"
Replace: href="eventbus_choreography.html"

Find:    href="governance-layer.html"
Replace: href="governance_layer.html"

Find:    href="predictive-intelligence.html"
Replace: href="predictive_intelligence.html"

Find:    href="expertise-center.html"
Replace: href="expertise_center.html"

Find:    href="collective-intelligence.html"
Replace: href="collective_intelligence.html"

Find:    href="ace-service.html"
Replace: href="ace_service.html"

Find:    href="platform-services-overview.html"
Replace: href="platform_services_overview.html"

Find:    href="decision-center.html"
Replace: href="decision_center.html"

Find:    href="mio-manager.html"
Replace: href="mio_manager.html"

Find:    href="business-flow.html"
Replace: href="business_flow.html"
```

---

## Verification Checklist

After renaming and updating links:

- [ ] All 15 files renamed successfully
- [ ] index.html navigation links updated
- [ ] index.html deep-dive section links updated
- [ ] index.html footer links updated
- [ ] All 10 deep-dive pages navigation updated
- [ ] All 10 deep-dive pages footer updated
- [ ] Cross-references between pages updated
- [ ] Open index.html in browser and test all links
- [ ] No 404 errors when clicking any link
- [ ] All pages load correctly

---

## Quick Test Commands

```bash
# Check if any HTML files still have dashes
cd /Users/MD/AI-Platform-ISO/docs
ls -1 | grep -E '.*-.*\.html$'

# Should return: No results (all files renamed)

# Check for any remaining dash-based links in HTML files
grep -r 'href="[a-z-]*-[a-z-]*\.html"' *.html

# Should return: No results (all links updated)
```

---

## Completion Status

- [x] Deep-dive documentation pages created (10 pages)
- [x] index.html updated with new section
- [x] Service catalog updated (ACE Service added, count 62→63)
- [ ] **Files renamed (PENDING - USER ACTION REQUIRED)**
- [ ] **Links updated (PENDING - AFTER RENAME)**
- [ ] **Verification complete (PENDING)**

---

## Notes

- **Port 8050 conflict**: RESOLVED - Real-time WebSocket moved to 8053, ACE Service uses 8050
- **Service count**: Updated from 62 to 63 (ACE Service added)
- **Intelligent Core services**: Updated from 12 to 13
- **Documentation quality**: All pages include architecture diagrams, API examples, integration guides

**Last Updated**: 2025-10-15
**Created By**: Claude Code (AI Assistant)
