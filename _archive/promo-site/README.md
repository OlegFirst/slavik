# AI-Platform-ISO Promotional Website

Professional promotional website for AI-Platform-ISO, designed for business partners and stakeholders.

## Quick Setup

### Local Development

1. **Clone and navigate:**
```bash
cd /Users/MD/AI-Platform-ISO/promo-site
```

2. **Open in browser:**
```bash
open index.html
# or
python3 -m http.server 8000
# Then visit http://localhost:8000
```

### GitHub Pages Deployment

1. **Push to GitHub:**
```bash
git add promo-site/
git commit -m "Add promotional website"
git push origin main
```

2. **Enable GitHub Pages:**
- Go to repository Settings
- Navigate to Pages section
- Source: Deploy from branch
- Branch: main
- Folder: /promo-site
- Save

3. **Access site:**
- URL: `https://yourusername.github.io/AI-Platform-ISO/`

## Site Structure

```
promo-site/
├── index.html              # Main landing page
├── business-flow.html      # Business process flow
├── user-flow.html          # User experience flow
├── interfaces.html         # Interface demonstrations
├── contact.html            # Contact and partnership info
├── docs/
│   └── index.html         # Documentation library
├── assets/
│   ├── css/
│   │   └── main.css       # Custom styles
│   ├── js/
│   │   └── main.js        # Interactive features
│   └── images/            # Images and assets
├── _config.yml            # GitHub Pages config
├── .nojekyll              # Disable Jekyll processing
└── README.md              # This file
```

## Features

- **Pure HTML/CSS/JS** - No build process required
- **Tailwind CSS** - Modern, responsive design
- **Mermaid.js** - Beautiful diagrams and flowcharts
- **Bilingual** - Russian (default) + English
- **Dark/Light Theme** - User preference toggle
- **Mobile Responsive** - Works on all devices
- **Fast Loading** - Static files only

## Content Highlights

- **1,745** total documentation files
- **5** core platform modules
- **12** BCM microservices
- **23** total services
- **ISO 22301:2019** compliant
- **AI-Powered** with Claude API integration

## Technology Stack

- HTML5
- CSS3 (Tailwind CSS via CDN)
- JavaScript (ES6+)
- Mermaid.js for diagrams
- Font Awesome for icons

## Customization

### Update Content
Edit the HTML files directly. All content is in Russian with English translations available.

### Update Styles
Modify `assets/css/main.css` for custom styling beyond Tailwind.

### Update Interactivity
Edit `assets/js/main.js` for additional JavaScript features.

### Update Configuration
Edit `_config.yml` for GitHub Pages settings.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

Non-Commercial Use Only - See main project LICENSE

## Contact

For partnership inquiries, use the contact form on the website or reach out through the documentation links.

---

**Version:** 1.0.0
**Last Updated:** 2025-10-10
**Status:** Production Ready
