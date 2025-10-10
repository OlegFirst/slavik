# Setup Guide

## Quick Setup

### 1. Install Dependencies

```bash
cd /Users/MD/AI-Platform-ISO/docs-website
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Visit [http://localhost:4000](http://localhost:4000)

### 3. Build for Production

```bash
npm run build
```

Static files will be in `/out` directory.

---

## GitHub Pages Setup

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings**
3. Scroll to **Pages** section
4. Under **Source**, select **GitHub Actions**

### Step 2: Push Code

```bash
git add .
git commit -m "Add documentation website"
git push origin main
```

### Step 3: Wait for Deployment

- Go to **Actions** tab
- Wait for workflow to complete
- Visit `https://[your-username].github.io/docs-website/`

---

## Customization

### Change Repository Name

If your repository name is different from `docs-website`, update `next.config.js`:

```javascript
basePath: process.env.NODE_ENV === 'production' ? '/YOUR-REPO-NAME' : '',
assetPrefix: process.env.NODE_ENV === 'production' ? '/YOUR-REPO-NAME/' : '',
```

### Change Docs Location

If your docs are in a different location, update `src/lib/docs.ts`:

```typescript
const DOCS_PATH = path.join(process.cwd(), '..', 'YOUR-DOCS-FOLDER')
```

---

## Troubleshooting

### Dependencies Not Installing

```bash
rm -rf node_modules package-lock.json
npm install
```

### Build Fails

Check Node.js version:
```bash
node --version  # Should be 18+
```

### GitHub Pages 404

1. Ensure `.nojekyll` file exists in `/public`
2. Check `basePath` matches repository name
3. Verify GitHub Pages is enabled in settings

---

## Development Tips

1. **Hot Reload**: Save files to see changes instantly
2. **Type Safety**: TypeScript will catch errors
3. **Linting**: Run `npm run lint` before committing
4. **Testing**: Test both light and dark modes

---

## Production Checklist

- [ ] All dependencies installed
- [ ] No build errors
- [ ] All links working
- [ ] Images loading correctly
- [ ] Dark/light mode working
- [ ] Mobile responsive
- [ ] Search functioning
- [ ] GitHub Actions configured
- [ ] Custom domain (if applicable)

---

**Ready to Go!** 🚀
