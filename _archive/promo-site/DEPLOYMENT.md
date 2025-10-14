# AI-Platform-ISO Promotional Website - Deployment Guide

**Quick deployment guide for GitHub Pages**

---

## 🚀 Quick Deploy (5 Minutes)

### Step 1: Verify Files
```bash
cd /Users/MD/AI-Platform-ISO/promo-site
ls -la
# Should see: index.html, business-flow.html, user-flow.html, interfaces.html, contact.html, docs/, assets/, etc.
```

### Step 2: Git Commands
```bash
# From project root
cd /Users/MD/AI-Platform-ISO

# Add all promo-site files
git add promo-site/

# Commit
git commit -m "feat: Add professional promotional website for GitHub Pages

- Main landing page with features, architecture, and specs
- Business flow page with implementation timeline
- User flow page with UX journey
- Interfaces page with mockups and descriptions
- Contact page with partnership info
- Documentation library with 1745+ docs
- Dark/Light theme with Russian/English language support
- Fully responsive design
- Mermaid.js diagrams
- Production ready for GitHub Pages"

# Push to GitHub
git push origin recovery-7-8-oct  # or your main branch
```

### Step 3: Enable GitHub Pages
1. Go to: `https://github.com/YOUR_USERNAME/AI-Platform-ISO/settings/pages`
2. Under "Source":
   - Branch: `recovery-7-8-oct` (or `main`)
   - Folder: `/promo-site`
3. Click "Save"
4. Wait 1-2 minutes for deployment

### Step 4: Access Your Site
- URL: `https://YOUR_USERNAME.github.io/AI-Platform-ISO/`
- GitHub will show the URL in the Pages settings

---

## 🔧 Configuration (Optional)

### Update _config.yml
```yaml
# Edit: promo-site/_config.yml
title: AI-Platform-ISO
description: Интеллектуальная платформа управления непрерывностью бизнеса
baseurl: "/AI-Platform-ISO"  # Your repo name
url: "https://YOUR_USERNAME.github.io"
```

### Custom Domain (Optional)
1. Create file: `promo-site/CNAME`
2. Add your domain: `www.example.com`
3. Configure DNS:
   - Type: CNAME
   - Name: www
   - Value: YOUR_USERNAME.github.io
4. Push changes
5. Enable in GitHub Pages settings

---

## 🧪 Local Testing

### Option 1: Python HTTP Server
```bash
cd /Users/MD/AI-Platform-ISO/promo-site
python3 -m http.server 8000
open http://localhost:8000
```

### Option 2: Node.js HTTP Server
```bash
cd /Users/MD/AI-Platform-ISO/promo-site
npx http-server -p 8000
open http://localhost:8000
```

### Option 3: Direct File
```bash
open /Users/MD/AI-Platform-ISO/promo-site/index.html
```

---

## ✅ Verification Checklist

After deployment, verify:

### Pages Load
- [ ] https://YOUR_SITE/ (index.html)
- [ ] https://YOUR_SITE/business-flow.html
- [ ] https://YOUR_SITE/user-flow.html
- [ ] https://YOUR_SITE/interfaces.html
- [ ] https://YOUR_SITE/contact.html
- [ ] https://YOUR_SITE/docs/index.html

### Features Work
- [ ] Navigation menu
- [ ] Mobile menu (resize browser)
- [ ] Theme toggle (dark/light)
- [ ] Language switcher
- [ ] All internal links
- [ ] Contact form validation
- [ ] Search in docs
- [ ] Mermaid diagrams render
- [ ] Animations trigger on scroll
- [ ] Statistics count up

### Design
- [ ] Responsive on mobile (375px)
- [ ] Responsive on tablet (768px)
- [ ] Responsive on desktop (1280px+)
- [ ] Dark theme displays correctly
- [ ] Light theme displays correctly
- [ ] No broken styles

---

## 📱 Test on Devices

### Desktop Browsers
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Mobile
- [ ] iOS Safari
- [ ] Chrome Mobile (Android)
- [ ] Samsung Internet

### Screen Sizes
- [ ] 375px (iPhone SE)
- [ ] 768px (iPad)
- [ ] 1024px (iPad Pro)
- [ ] 1280px (Desktop)
- [ ] 1920px (Full HD)

---

## 🎨 Customization

### Add Your Branding

**1. Update Colors (assets/css/main.css)**
```css
:root {
  --accent-primary: #YOUR_COLOR;
  --accent-secondary: #YOUR_COLOR;
}
```

**2. Add Logo (all HTML files)**
```html
<!-- Replace in navigation -->
<a href="index.html" class="logo">
    <img src="assets/images/logo.png" alt="Logo" style="height: 2rem;">
    <span>AI-Platform-ISO</span>
</a>
```

**3. Update Contact Info (contact.html)**
```html
<!-- Update email addresses -->
<p>info@YOUR_DOMAIN.com</p>
```

### Add Images

**1. Create images directory** (already exists)
```bash
mkdir -p promo-site/assets/images
```

**2. Add images**
```bash
# Add your images to:
promo-site/assets/images/
├── logo.png
├── dashboard-screenshot.png
├── bia-screenshot.png
└── ...
```

**3. Update HTML**
```html
<!-- In interfaces.html, replace mockup divs -->
<img src="assets/images/dashboard-screenshot.png" alt="Dashboard">
```

---

## 🔗 Update Links

### GitHub Repository Link
Replace in all HTML files:
```html
<!-- Old -->
<a href="https://github.com">

<!-- New -->
<a href="https://github.com/YOUR_USERNAME/AI-Platform-ISO">
```

### Documentation Links
All documentation links point to actual project files:
```html
<!-- These work if promo-site is deployed from project root -->
<a href="../../docs/README.md">
<a href="../../platform-services/bia-service/">
```

---

## 📊 Analytics (Optional)

### Add Google Analytics

**1. Get tracking ID** from Google Analytics

**2. Add to all HTML files** (before `</head>`):
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

---

## 🐛 Troubleshooting

### Issue: Pages not loading
**Solution:** Check GitHub Pages settings, ensure correct branch and folder

### Issue: Styles not applying
**Solution:** Check browser console for 404s, verify CSS path in HTML

### Issue: Mermaid diagrams not showing
**Solution:** Check browser console, ensure mermaid.js CDN is accessible

### Issue: Links broken
**Solution:** Check if baseurl is set correctly in _config.yml

### Issue: Images not loading
**Solution:** Verify image paths are relative and files exist

---

## 🔄 Updates

### Update Content
```bash
# 1. Edit HTML files
nano promo-site/index.html

# 2. Test locally
cd promo-site && python3 -m http.server 8000

# 3. Commit and push
git add promo-site/
git commit -m "Update: ..."
git push
```

### Add New Page
```bash
# 1. Create new HTML file
cp promo-site/index.html promo-site/new-page.html

# 2. Update content and navigation
nano promo-site/new-page.html

# 3. Add link to navigation in all pages
# Update nav-links in all HTML files

# 4. Commit and push
git add promo-site/new-page.html
git commit -m "Add: new-page.html"
git push
```

---

## 📞 Support

### Deployment Issues
- GitHub Pages Docs: https://docs.github.com/en/pages
- GitHub Community: https://github.community/

### Website Issues
- Check SITE_MAP.md for site structure
- Check README.md for setup instructions
- Contact: support@ai-platform-iso.org

---

## 🎉 Success Criteria

Your site is successfully deployed when:
- ✅ All 6 pages load without errors
- ✅ Navigation works between all pages
- ✅ Theme toggle persists across page loads
- ✅ Mobile menu works on small screens
- ✅ All diagrams render correctly
- ✅ Forms validate properly
- ✅ Responsive on all device sizes
- ✅ No console errors in browser

---

## 📝 Next Steps

After successful deployment:
1. Share URL with stakeholders
2. Add to project README.md
3. Submit to search engines (optional)
4. Monitor analytics (if configured)
5. Gather feedback
6. Iterate and improve

---

**Happy Deploying! 🚀**

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-10
**Status:** Production Ready
