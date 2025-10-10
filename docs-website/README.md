# AI-Platform-ISO Documentation Website

Professional documentation website for **AI-Platform-ISO** - Business Continuity Management Platform with AI Intelligence and ISO 22301 Compliance.

Built with Next.js 14, TypeScript, and Tailwind CSS.

---

## Features

### Core Features

- **40+ Markdown Documents** - Automatically indexed from `/docs` directory
- **Dynamic Routing** - Clean URLs for all documentation pages
- **Full-Text Search** - Search across all documentation
- **Categorized Navigation** - Organized by Architecture, Requirements, Design, Implementation, Reports
- **Dark/Light Mode** - Built-in theme switcher with system preference support
- **Responsive Design** - Mobile-first, works on all devices
- **Syntax Highlighting** - Code blocks with highlight.js
- **Table of Contents** - Auto-generated TOC for each document
- **Breadcrumb Navigation** - Clear navigation path
- **SEO Optimized** - Meta tags, OpenGraph, structured data

### Technical Features

- **Static Site Generation** - Pre-rendered at build time for maximum performance
- **GitHub Pages Ready** - Automated deployment via GitHub Actions
- **TypeScript** - Full type safety
- **Tailwind CSS** - Modern, utility-first styling
- **React Markdown** - Rich markdown rendering with GFM support
- **Gray Matter** - Frontmatter parsing for metadata
- **Next Themes** - Theme management with no flash of unstyled content

---

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm start
```

Visit [http://localhost:4000](http://localhost:4000)

---

## Project Structure

```
docs-website/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout with sidebar
│   │   ├── page.tsx             # Homepage
│   │   ├── globals.css          # Global styles
│   │   ├── not-found.tsx        # 404 page
│   │   ├── docs/
│   │   │   └── [...slug]/
│   │   │       └── page.tsx     # Dynamic doc pages
│   │   └── search/
│   │       └── page.tsx         # Search page
│   │
│   ├── components/
│   │   ├── Sidebar.tsx          # Navigation sidebar
│   │   ├── Header.tsx           # Top header with theme toggle
│   │   ├── MarkdownRenderer.tsx # Markdown content renderer
│   │   ├── TableOfContents.tsx  # Auto-generated TOC
│   │   ├── Breadcrumbs.tsx      # Breadcrumb navigation
│   │   ├── DocSearch.tsx        # Search functionality
│   │   └── ThemeProvider.tsx    # Theme context provider
│   │
│   └── lib/
│       └── docs.ts              # Documentation data management
│
├── public/
│   └── .nojekyll                # GitHub Pages config
│
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Actions deployment
│
├── next.config.js               # Next.js configuration
├── tailwind.config.js           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
└── package.json                 # Dependencies
```

---

## Documentation Management

### Adding Documents

Simply add `.md` files to `/Users/MD/AI-Platform-ISO/docs/` directory. They will be automatically indexed and categorized.

### Frontmatter Support

Optionally add frontmatter to your markdown files:

```markdown
---
title: Custom Title
description: Custom description
category: architecture
tags: [AI, Microservices, Docker]
---

# Your Content Here
```

### Auto-Categorization

If no category is specified in frontmatter, documents are automatically categorized based on:

- **Directory name** (e.g., `requirements/`, `specs/`)
- **Filename patterns** (e.g., `ARCHITECTURE`, `REPORT`, `IMPLEMENTATION`)
- **Content analysis**

Categories:
- `architecture` - System architecture, platform design
- `requirements` - Requirements specifications, user segments
- `design` - Technical designs, specifications
- `implementation` - Guides, integrations, deployment
- `reports` - Progress reports, audits, summaries

---

## Deployment

### GitHub Pages (Automatic)

1. **Enable GitHub Pages** in repository settings:
   - Go to Settings → Pages
   - Source: GitHub Actions

2. **Push to main branch**:
   ```bash
   git add .
   git commit -m "Deploy documentation"
   git push origin main
   ```

3. **GitHub Actions** automatically builds and deploys

4. **Access** at: `https://[username].github.io/docs-website/`

### Manual Deployment

```bash
# Build static site
npm run build

# Output in /out directory
# Deploy /out to any static hosting service
```

---

## Configuration

### Update Base Path

Edit `next.config.js`:

```javascript
module.exports = {
  basePath: '/your-repo-name',
  assetPrefix: '/your-repo-name/',
}
```

### Update Docs Path

Edit `src/lib/docs.ts`:

```typescript
const DOCS_PATH = path.join(process.cwd(), '..', 'your-docs-folder')
```

### Customize Theme

Edit `src/app/globals.css` to change colors:

```css
:root {
  --primary: 221.2 83.2% 53.3%;  /* Blue */
  /* ... other colors */
}
```

---

## Development

### Available Scripts

- `npm run dev` - Start development server (port 4000)
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

### Hot Reload

Development server supports hot reload for:
- React components
- CSS changes
- Markdown content (after refresh)

---

## Features in Detail

### Search Functionality

- **Real-time search** - Results update as you type
- **Multi-field search** - Searches title, description, content, tags
- **Highlighted results** - Shows matched content
- **Category filters** - Filter by document category

### Theme System

- **Light/Dark modes** - Manual toggle or system preference
- **No flash** - Smooth transitions without FOUC
- **Persistent** - Remembers user preference
- **CSS Variables** - Easy customization

### Markdown Support

Supports all GitHub Flavored Markdown features:

- Tables
- Task lists
- Strikethrough
- Autolinks
- Syntax highlighting
- Blockquotes
- Images
- Code blocks

### SEO & Performance

- **Static generation** - All pages pre-rendered
- **Optimized images** - Automatic image optimization
- **Meta tags** - Dynamic titles and descriptions
- **Lighthouse score** - 90+ performance score
- **Mobile-first** - Responsive on all devices

---

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

---

## Troubleshooting

### Build Errors

**Problem**: `Error: Cannot find module 'gray-matter'`

**Solution**:
```bash
npm install
```

**Problem**: Documents not appearing

**Solution**: Check docs path in `src/lib/docs.ts` matches your directory structure

### Deployment Issues

**Problem**: 404 on GitHub Pages

**Solution**: Ensure `.nojekyll` file exists in `/out` after build

**Problem**: Styles not loading

**Solution**: Check `basePath` in `next.config.js` matches your repository name

---

## Performance

- **Build time**: ~30 seconds for 40+ documents
- **Page load**: < 1 second (static)
- **Search**: < 100ms for 40+ documents
- **Bundle size**: ~200KB gzipped

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

---

## Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Markdown**: react-markdown
- **Syntax Highlighting**: highlight.js
- **Theme**: next-themes
- **Icons**: lucide-react
- **Deployment**: GitHub Pages

---

## License

See [LICENSE](../LICENSE)

---

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review Next.js documentation

---

## Roadmap

- [ ] Advanced search with filters
- [ ] Document version history
- [ ] PDF export
- [ ] Multi-language support
- [ ] API documentation integration
- [ ] Interactive diagrams
- [ ] Comments system

---

**Built with ❤️ for AI-Platform-ISO**

Last Updated: October 2025
