# AI-Platform-ISO GitHub Pages

This directory contains the static website for AI-Platform-ISO documentation, hosted on GitHub Pages.

## Website Structure

### Main Pages (10)
1. **index.html** - Homepage with BCM philosophy, stats, key benefits
2. **architecture.html** - 4-layer architecture, port map, EventBus diagrams
3. **modules.html** - 17 AI modules + 21 platform services detailed
4. **features.html** - 570+ usage scenarios, capabilities catalog
5. **business-flow.html** - 233 business flows with Mermaid diagrams
6. **technology.html** - Complete technology stack breakdown
7. **deployment.html** - 4-phase deployment guide with commands
8. **documentation.html** - Index of 320+ technical documents
9. **mvp.html** - MVP platform demo and API reference
10. **contact.html** - Community, contribution guidelines, support

### Assets
- **assets/styles.css** - Professional clean stylesheet (light theme)
- **assets/scripts.js** - Mermaid initialization, mobile menu, smooth scroll

## Features

- Clean professional design (NO dark theme - light background, dark text)
- Fully responsive mobile-first layout
- Mermaid.js diagrams for architecture and workflows
- Smooth scrolling navigation
- Search functionality on documentation page
- Copy buttons for code blocks
- Back-to-top button
- Consistent navigation across all pages

## Design Principles

- **Clean & Professional:** Light backgrounds, readable typography
- **No Clutter:** Focused content, clear hierarchy
- **Accessibility:** Semantic HTML, ARIA labels, keyboard navigation
- **Performance:** Minimal dependencies, optimized assets
- **SEO-Friendly:** Proper meta tags, semantic structure

## Local Development

```bash
# Serve locally with Python
cd docs-gh-pages
python -m http.server 8000

# Or with Node.js
npx http-server -p 8000

# Access at http://localhost:8000
```

## GitHub Pages Deployment

This site is configured for GitHub Pages. To deploy:

1. Push to `main` branch
2. Enable GitHub Pages in repository settings
3. Set source to `/docs-gh-pages` directory
4. Site will be available at: `https://yourusername.github.io/AI-Platform-ISO/`

## Dependencies

External CDN resources:
- **Mermaid.js v10** - Diagram rendering
- **No other dependencies** - Pure HTML/CSS/JS

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

MIT License - Same as main project

## Maintenance

- Update content when platform changes
- Keep diagrams synchronized with architecture
- Refresh stats and counts periodically
- Review links to ensure they work

---

Built with dedication for resilient organizations worldwide.
