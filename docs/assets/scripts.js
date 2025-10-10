// AI-Platform-ISO - Shared JavaScript

// Initialize Mermaid
document.addEventListener('DOMContentLoaded', function() {
  // Initialize Mermaid diagrams
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      themeVariables: {
        primaryColor: '#2563eb',
        primaryTextColor: '#fff',
        primaryBorderColor: '#1d4ed8',
        lineColor: '#6b7280',
        secondaryColor: '#059669',
        tertiaryColor: '#f3f4f6'
      }
    });
  }

  // Mobile menu toggle
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (mobileMenuToggle && navLinks) {
    mobileMenuToggle.addEventListener('click', function() {
      navLinks.classList.toggle('active');
    });
  }

  // Set active nav link based on current page
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  const navItems = document.querySelectorAll('.nav-links a');

  navItems.forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage) {
      link.classList.add('active');
    }
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
});

// Add copy button to code blocks
function addCopyButtons() {
  const codeBlocks = document.querySelectorAll('pre code');

  codeBlocks.forEach(block => {
    const button = document.createElement('button');
    button.className = 'copy-button';
    button.textContent = 'Copy';
    button.style.cssText = `
      position: absolute;
      top: 0.5rem;
      right: 0.5rem;
      padding: 0.25rem 0.75rem;
      background: #2563eb;
      color: white;
      border: none;
      border-radius: 0.25rem;
      cursor: pointer;
      font-size: 0.875rem;
    `;

    const pre = block.parentElement;
    pre.style.position = 'relative';
    pre.appendChild(button);

    button.addEventListener('click', async () => {
      const text = block.textContent;
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = 'Copied!';
        setTimeout(() => {
          button.textContent = 'Copy';
        }, 2000);
      } catch (err) {
        console.error('Failed to copy:', err);
      }
    });
  });
}

// Call after DOM is loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', addCopyButtons);
} else {
  addCopyButtons();
}

// Simple search functionality for documentation page
function initSearch() {
  const searchInput = document.getElementById('doc-search');
  const searchResults = document.getElementById('search-results');

  if (!searchInput || !searchResults) return;

  searchInput.addEventListener('input', function(e) {
    const query = e.target.value.toLowerCase();
    const items = document.querySelectorAll('.doc-item');

    let matchCount = 0;

    items.forEach(item => {
      const title = item.querySelector('h3')?.textContent.toLowerCase() || '';
      const description = item.querySelector('p')?.textContent.toLowerCase() || '';

      if (title.includes(query) || description.includes(query)) {
        item.style.display = 'block';
        matchCount++;
      } else {
        item.style.display = 'none';
      }
    });

    if (query && matchCount === 0) {
      searchResults.textContent = `No results found for "${e.target.value}"`;
      searchResults.style.display = 'block';
    } else {
      searchResults.style.display = 'none';
    }
  });
}

// Initialize search on documentation page
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSearch);
} else {
  initSearch();
}

// Back to top button
const backToTop = document.createElement('button');
backToTop.innerHTML = '↑';
backToTop.style.cssText = `
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 3rem;
  height: 3rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.5rem;
  display: none;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
  transition: all 0.3s;
`;

document.body.appendChild(backToTop);

window.addEventListener('scroll', () => {
  if (window.pageYOffset > 300) {
    backToTop.style.display = 'block';
  } else {
    backToTop.style.display = 'none';
  }
});

backToTop.addEventListener('click', () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
});

backToTop.addEventListener('mouseenter', () => {
  backToTop.style.transform = 'scale(1.1)';
});

backToTop.addEventListener('mouseleave', () => {
  backToTop.style.transform = 'scale(1)';
});
