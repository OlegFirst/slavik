# Quick Start Guide

Get your documentation website running in 3 minutes!

---

## Step 1: Install Dependencies (1 min)

```bash
cd /Users/MD/AI-Platform-ISO/docs-website
npm install
```

This installs all required packages (~200MB, takes ~1 minute).

---

## Step 2: Run Development Server (30 seconds)

```bash
npm run dev
```

Output:
```
  ▲ Next.js 14.2.5
  - Local:        http://localhost:4000
  - Network:      http://192.168.1.x:4000

 ✓ Ready in 3.2s
```

**Open**: [http://localhost:4000](http://localhost:4000)

---

## Step 3: Explore the Site (1 min)

### Homepage
- View statistics (total docs, categories)
- Browse category cards
- Check recent documents

### Navigation
- Click **Architecture** in sidebar
- Browse documents
- Try the search icon (top right)

### Theme
- Toggle dark/light mode (moon/sun icon)

### Document Page
- Click any document
- See breadcrumbs
- View table of contents (right sidebar on desktop)
- Check syntax highlighting in code blocks

---

## Step 4: Build for Production (1 min)

```bash
npm run build
```

Output:
```
Route (app)                              Size     First Load JS
┌ ○ /                                    5.2 kB         92.1 kB
├ ○ /docs/[...slug]                      1.8 kB         88.7 kB
├ ○ /search                              2.1 kB         89.0 kB
└ ○ /404                                 1.2 kB         88.1 kB

○  (Static)  prerendered as static content

✓ Compiled successfully
```

Static files are in `/out` directory.

---

## Step 5: Deploy to GitHub Pages (2 mins)

### A. Enable GitHub Pages

1. Go to your repo on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. Save

### B. Push Code

```bash
git add .
git commit -m "Add documentation website"
git push origin main
```

### C. Wait for Deployment

1. Go to **Actions** tab
2. Watch the workflow run (takes ~2 mins)
3. When complete, visit: `https://[username].github.io/docs-website/`

---

## Customization

### Update Repository Name

If your repo is NOT named `docs-website`, edit `next.config.js`:

```javascript
basePath: process.env.NODE_ENV === 'production' ? '/YOUR-REPO-NAME' : '',
assetPrefix: process.env.NODE_ENV === 'production' ? '/YOUR-REPO-NAME/' : '',
```

### Update Docs Location

If docs are NOT in `../docs`, edit `src/lib/docs.ts`:

```typescript
const DOCS_PATH = path.join(process.cwd(), '..', 'YOUR-FOLDER')
```

---

## Troubleshooting

### Dependencies Won't Install

```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Port 4000 Already in Use

```bash
npm run dev -- -p 3000
```

### Build Fails

Check Node.js version:
```bash
node --version  # Must be 18+
```

Update if needed:
```bash
nvm install 20
nvm use 20
```

### GitHub Pages Shows 404

1. Check `.nojekyll` exists in `/public`
2. Verify `basePath` matches repo name
3. Wait 2-3 minutes after deployment
4. Clear browser cache

---

## Commands Cheat Sheet

```bash
# Development
npm run dev          # Start dev server (port 4000)
npm run build        # Build for production
npm start            # Start production server
npm run lint         # Check for errors

# Cleanup
rm -rf .next out     # Remove build files
rm -rf node_modules  # Remove dependencies
```

---

## File Locations

| What | Where |
|------|-------|
| Homepage | `src/app/page.tsx` |
| Document pages | `src/app/docs/[...slug]/page.tsx` |
| Sidebar | `src/components/Sidebar.tsx` |
| Theme toggle | `src/components/Header.tsx` |
| Search | `src/components/DocSearch.tsx` |
| Styles | `src/app/globals.css` |
| Docs loader | `src/lib/docs.ts` |
| Config | `next.config.js` |

---

## What's Included

✅ **40+ Documents** - Auto-indexed from `/docs`
✅ **5 Categories** - Architecture, Requirements, Design, Implementation, Reports
✅ **Search** - Full-text search across all docs
✅ **Dark Mode** - Toggle theme
✅ **Mobile Responsive** - Works on all devices
✅ **GitHub Pages** - Automated deployment
✅ **SEO** - Meta tags, descriptions
✅ **Performance** - Static site, < 1s load

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Run dev server
3. ✅ Explore the site
4. ✅ Build for production
5. ✅ Deploy to GitHub Pages
6. 🎉 Share with partners!

---

**Need Help?**
- Check [README.md](README.md) for detailed docs
- See [SETUP.md](SETUP.md) for setup guide
- Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for overview

**Ready!** 🚀
