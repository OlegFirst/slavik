# Complete File Paths Reference

All absolute file paths for the AI-Platform-ISO Documentation Website.

---

## 📚 Documentation Files

```
/Users/MD/AI-Platform-ISO/docs-website/README.md
/Users/MD/AI-Platform-ISO/docs-website/QUICK_START.md
/Users/MD/AI-Platform-ISO/docs-website/SETUP.md
/Users/MD/AI-Platform-ISO/docs-website/PROJECT_SUMMARY.md
/Users/MD/AI-Platform-ISO/docs-website/DELIVERABLES.md
/Users/MD/AI-Platform-ISO/docs-website/INDEX.md
/Users/MD/AI-Platform-ISO/docs-website/FILE_PATHS.md
```

---

## 🎨 Application Files

### App Directory
```
/Users/MD/AI-Platform-ISO/docs-website/src/app/layout.tsx
/Users/MD/AI-Platform-ISO/docs-website/src/app/page.tsx
/Users/MD/AI-Platform-ISO/docs-website/src/app/globals.css
/Users/MD/AI-Platform-ISO/docs-website/src/app/not-found.tsx
/Users/MD/AI-Platform-ISO/docs-website/src/app/docs/[...slug]/page.tsx
/Users/MD/AI-Platform-ISO/docs-website/src/app/search/page.tsx
```

### Components
```
/Users/MD/AI-Platform-ISO/docs-website/src/components/Sidebar.tsx
/Users/MD/AI-Platform-ISO/docs-website/src/components/Header.tsx
/Users/MD/AI-Platform-ISO/docs-website/src/components/MarkdownRenderer.tsx
/Users/MD/AI-Platform-ISO/docs-website/src/components/TableOfContents.tsx
/Users/MD/AI-Platform-ISO/docs-website/src/components/Breadcrumbs.tsx
/Users/MD/AI-Platform-ISO/docs-website/src/components/DocSearch.tsx
/Users/MD/AI-Platform-ISO/docs-website/src/components/ThemeProvider.tsx
```

### Library
```
/Users/MD/AI-Platform-ISO/docs-website/src/lib/docs.ts
```

---

## ⚙️ Configuration Files

```
/Users/MD/AI-Platform-ISO/docs-website/next.config.js
/Users/MD/AI-Platform-ISO/docs-website/tailwind.config.js
/Users/MD/AI-Platform-ISO/docs-website/tsconfig.json
/Users/MD/AI-Platform-ISO/docs-website/postcss.config.js
/Users/MD/AI-Platform-ISO/docs-website/package.json
/Users/MD/AI-Platform-ISO/docs-website/.eslintrc.json
/Users/MD/AI-Platform-ISO/docs-website/.gitignore
```

---

## 🚀 Deployment Files

```
/Users/MD/AI-Platform-ISO/docs-website/.github/workflows/deploy.yml
/Users/MD/AI-Platform-ISO/docs-website/public/.nojekyll
```

---

## 📂 Directory Structure

```
/Users/MD/AI-Platform-ISO/docs-website/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── public/
│   └── .nojekyll
├── src/
│   ├── app/
│   │   ├── docs/
│   │   │   └── [...slug]/
│   │   │       └── page.tsx
│   │   ├── search/
│   │   │   └── page.tsx
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   └── not-found.tsx
│   ├── components/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── MarkdownRenderer.tsx
│   │   ├── TableOfContents.tsx
│   │   ├── Breadcrumbs.tsx
│   │   ├── DocSearch.tsx
│   │   └── ThemeProvider.tsx
│   └── lib/
│       └── docs.ts
├── README.md
├── QUICK_START.md
├── SETUP.md
├── PROJECT_SUMMARY.md
├── DELIVERABLES.md
├── INDEX.md
├── FILE_PATHS.md
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── postcss.config.js
├── package.json
├── .eslintrc.json
└── .gitignore
```

---

## 🗂️ External Dependencies

### Source Documents (Read by the app)
```
/Users/MD/AI-Platform-ISO/docs/
├── ARCHITECTURE.md
├── IMPLEMENTATION_GUIDE.md
├── README.md
├── BUSINESS_FEATURES.md
├── ... (40+ markdown files)
└── requirements/
    ├── USER_SEGMENT_BCM_PROFESSIONAL.md
    ├── USER_SEGMENT_CONSULTANT.md
    ├── USER_SEGMENT_AUDITOR.md
    ├── CORE_PLATFORM_SRS.md
    └── FRONTEND_ARCHITECTURE.md
```

---

## 📋 Quick Copy-Paste Commands

### View Main Files
```bash
# View homepage
cat /Users/MD/AI-Platform-ISO/docs-website/src/app/page.tsx

# View layout
cat /Users/MD/AI-Platform-ISO/docs-website/src/app/layout.tsx

# View sidebar
cat /Users/MD/AI-Platform-ISO/docs-website/src/components/Sidebar.tsx

# View docs loader
cat /Users/MD/AI-Platform-ISO/docs-website/src/lib/docs.ts
```

### Edit Configuration
```bash
# Edit Next.js config
nano /Users/MD/AI-Platform-ISO/docs-website/next.config.js

# Edit Tailwind config
nano /Users/MD/AI-Platform-ISO/docs-website/tailwind.config.js

# Edit TypeScript config
nano /Users/MD/AI-Platform-ISO/docs-website/tsconfig.json
```

### View Documentation
```bash
# Read README
cat /Users/MD/AI-Platform-ISO/docs-website/README.md

# Read Quick Start
cat /Users/MD/AI-Platform-ISO/docs-website/QUICK_START.md

# Read Setup Guide
cat /Users/MD/AI-Platform-ISO/docs-website/SETUP.md
```

---

## 🔧 Development Commands

```bash
# Navigate to project
cd /Users/MD/AI-Platform-ISO/docs-website

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

---

## 📦 Build Output

After running `npm run build`, output files are in:

```
/Users/MD/AI-Platform-ISO/docs-website/out/
├── index.html
├── docs/
│   └── [slug].html
├── search.html
├── 404.html
├── _next/
│   ├── static/
│   └── chunks/
└── .nojekyll
```

---

## 🌐 URLs (Local Development)

```
Homepage:           http://localhost:4000/
Search:             http://localhost:4000/search
Architecture Docs:  http://localhost:4000/docs/ARCHITECTURE
Requirements:       http://localhost:4000/docs/requirements/CORE_PLATFORM_SRS
```

---

## 🌐 URLs (Production - GitHub Pages)

```
Homepage:           https://[username].github.io/docs-website/
Search:             https://[username].github.io/docs-website/search
Architecture Docs:  https://[username].github.io/docs-website/docs/ARCHITECTURE
Requirements:       https://[username].github.io/docs-website/docs/requirements/CORE_PLATFORM_SRS
```

---

## 📊 File Statistics

| Category | Count | Total Lines |
|----------|-------|-------------|
| TypeScript/TSX | 13 | 1,047 |
| CSS | 1 | 170 |
| Configuration | 7 | ~300 |
| Documentation | 7 | 2,100+ |
| Deployment | 2 | 50 |
| **Total** | **30** | **3,667+** |

---

## 🎯 Key File Descriptions

| File | Lines | Purpose |
|------|-------|---------|
| `src/lib/docs.ts` | 270 | Documentation data management - reads from `/docs` directory |
| `src/app/page.tsx` | 155 | Homepage with overview, stats, and category cards |
| `src/app/globals.css` | 170 | Global styles including dark/light theme variables |
| `src/components/Sidebar.tsx` | 170 | Navigation sidebar with collapsible categories |
| `src/app/docs/[...slug]/page.tsx` | 100 | Dynamic route handler for all documentation pages |
| `src/components/DocSearch.tsx` | 90 | Full-text search functionality |
| `src/components/Header.tsx` | 80 | Top header with theme toggle and search |
| `src/components/TableOfContents.tsx` | 70 | Auto-generated table of contents |
| `src/components/MarkdownRenderer.tsx` | 55 | Markdown rendering with syntax highlighting |

---

**Total Files Created**: 30
**Ready for Use**: ✅ Yes
**Status**: Production Ready

---

Last Updated: October 10, 2025
