// AI-Platform-ISO Promotional Website - Main JavaScript

// Theme Management
const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;

// Load saved theme or default to light
const savedTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
  });
}

function updateThemeIcon(theme) {
  if (themeToggle) {
    themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
  }
}

// Language Management
const langToggle = document.getElementById('lang-toggle');
let currentLang = localStorage.getItem('language') || 'ru';

if (langToggle) {
  langToggle.textContent = currentLang === 'ru' ? 'EN' : 'RU';

  langToggle.addEventListener('click', () => {
    currentLang = currentLang === 'ru' ? 'en' : 'ru';
    localStorage.setItem('language', currentLang);
    langToggle.textContent = currentLang === 'ru' ? 'EN' : 'RU';
    switchLanguage(currentLang);
  });
}

function switchLanguage(lang) {
  document.querySelectorAll('[data-lang-ru]').forEach(el => {
    el.textContent = lang === 'ru' ? el.dataset.langRu : el.dataset.langEn;
  });
}

// Mobile Menu
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const navLinks = document.getElementById('nav-links');

if (mobileMenuBtn && navLinks) {
  mobileMenuBtn.addEventListener('click', () => {
    navLinks.classList.toggle('active');
    const isOpen = navLinks.classList.contains('active');
    mobileMenuBtn.innerHTML = isOpen ? '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
  });

  // Close menu when clicking on a link
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('active');
      mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
    });
  });
}

// Smooth Scroll with Offset
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const href = this.getAttribute('href');
    if (href === '#') return;

    e.preventDefault();
    const target = document.querySelector(href);
    if (target) {
      const offset = 80; // Nav height
      const targetPosition = target.offsetTop - offset;
      window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
      });
    }
  });
});

// Navigation Scroll Effect
let lastScroll = 0;
const nav = document.querySelector('nav');

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;

  if (currentScroll > 100) {
    nav.classList.add('scrolled');
  } else {
    nav.classList.remove('scrolled');
  }

  lastScroll = currentScroll;
});

// Active Navigation Link
function updateActiveLink() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-links a');

  let current = '';

  sections.forEach(section => {
    const sectionTop = section.offsetTop;
    const sectionHeight = section.clientHeight;
    if (window.pageYOffset >= (sectionTop - 100)) {
      current = section.getAttribute('id');
    }
  });

  navLinks.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === `#${current}`) {
      link.classList.add('active');
    }
  });
}

window.addEventListener('scroll', updateActiveLink);

// Intersection Observer for Animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('fade-in');
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// Observe elements for animation
document.querySelectorAll('.feature-card, .stat-card, .flow-step, .interface-demo').forEach(el => {
  observer.observe(el);
});

// Initialize Mermaid
if (typeof mermaid !== 'undefined') {
  mermaid.initialize({
    startOnLoad: true,
    theme: savedTheme === 'dark' ? 'dark' : 'default',
    securityLevel: 'loose',
    flowchart: {
      useMaxWidth: true,
      htmlLabels: true,
      curve: 'basis'
    }
  });

  // Update mermaid theme when theme changes
  const originalToggleClick = themeToggle?.onclick;
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      setTimeout(() => {
        const currentTheme = html.getAttribute('data-theme');
        mermaid.initialize({
          theme: currentTheme === 'dark' ? 'dark' : 'default'
        });
        location.reload(); // Reload to apply mermaid theme
      }, 100);
    });
  }
}

// Contact Form Handler
const contactForm = document.getElementById('contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(contactForm);
    const data = Object.fromEntries(formData);

    const submitBtn = contactForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;

    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="loading"></span> Отправка...';

      // Here you would send the data to your backend
      console.log('Form data:', data);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Show success message
      showNotification('Спасибо! Мы свяжемся с вами в ближайшее время.', 'success');
      contactForm.reset();

    } catch (error) {
      showNotification('Произошла ошибка. Пожалуйста, попробуйте позже.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
}

// Notification System
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;

  notification.style.cssText = `
    position: fixed;
    top: 100px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 0.5rem;
    background: ${type === 'success' ? 'var(--accent-success)' : 'var(--accent-danger)'};
    color: white;
    font-weight: 600;
    box-shadow: var(--shadow-lg);
    z-index: 10000;
    animation: slideIn 0.3s ease-out;
  `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Add animation keyframes
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(400px);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

// Copy to Clipboard
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showNotification('Скопировано в буфер обмена!', 'success');
  }).catch(() => {
    showNotification('Не удалось скопировать', 'error');
  });
}

// Search Functionality for Documentation
const searchInput = document.getElementById('docs-search');
if (searchInput) {
  searchInput.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const docItems = document.querySelectorAll('.docs-list li');

    docItems.forEach(item => {
      const text = item.textContent.toLowerCase();
      if (text.includes(searchTerm)) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
      }
    });
  });
}

// Statistics Counter Animation
function animateCounter(element, target, duration = 2000) {
  const start = 0;
  const increment = target / (duration / 16);
  let current = start;

  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      element.textContent = target.toLocaleString('ru-RU');
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current).toLocaleString('ru-RU');
    }
  }, 16);
}

// Animate stats when they come into view
const statsObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const statNumber = entry.target.querySelector('.stat-number');
      if (statNumber && !statNumber.dataset.animated) {
        const target = parseInt(statNumber.dataset.value);
        animateCounter(statNumber, target);
        statNumber.dataset.animated = 'true';
      }
      statsObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-card').forEach(card => {
  statsObserver.observe(card);
});

// Back to Top Button
const backToTopBtn = document.createElement('button');
backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
backToTopBtn.className = 'back-to-top';
backToTopBtn.style.cssText = `
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  border: none;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: var(--shadow-lg);
  z-index: 999;
  transition: all 0.3s ease;
`;

document.body.appendChild(backToTopBtn);

window.addEventListener('scroll', () => {
  if (window.pageYOffset > 300) {
    backToTopBtn.style.display = 'flex';
  } else {
    backToTopBtn.style.display = 'none';
  }
});

backToTopBtn.addEventListener('click', () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
});

backToTopBtn.addEventListener('mouseenter', () => {
  backToTopBtn.style.transform = 'translateY(-4px)';
});

backToTopBtn.addEventListener('mouseleave', () => {
  backToTopBtn.style.transform = 'translateY(0)';
});

// Print current page info on load
console.log('%c AI-Platform-ISO ', 'background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; font-size: 20px; font-weight: bold; padding: 10px;');
console.log('Version: 1.0.0');
console.log('Theme:', savedTheme);
console.log('Language:', currentLang);

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  // Apply saved language
  switchLanguage(currentLang);

  // Update active nav link
  updateActiveLink();

  // Add loaded class to body for animations
  document.body.classList.add('loaded');
});
