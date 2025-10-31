/**
 * BCM Knowledge Base Portal - Search and Interaction JavaScript
 * Provides advanced search functionality, auto-complete, and user interactions
 */

(function() {
    'use strict';

    // Knowledge Search Manager
    class KnowledgeSearchManager {
        constructor() {
            this.searchInput = null;
            this.suggestionsContainer = null;
            this.searchTimeout = null;
            this.currentRequest = null;
            this.isLoading = false;

            this.init();
        }

        init() {
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initializeElements());
            } else {
                this.initializeElements();
            }
        }

        initializeElements() {
            this.searchInput = document.getElementById('knowledge-search');
            this.suggestionsContainer = document.getElementById('search-suggestions');

            if (this.searchInput) {
                this.setupSearchHandlers();
                this.setupKeyboardNavigation();
            }

            this.setupBookmarkHandlers();
            this.setupCopyToClipboard();
            this.setupPrintHandlers();
        }

        setupSearchHandlers() {
            // Auto-complete on input
            this.searchInput.addEventListener('input', (e) => {
                this.handleSearchInput(e.target.value);
            });

            // Hide suggestions when clicking outside
            document.addEventListener('click', (e) => {
                if (!this.searchInput.contains(e.target) &&
                    !this.suggestionsContainer.contains(e.target)) {
                    this.hideSuggestions();
                }
            });

            // Submit search on Enter
            this.searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch(e.target.value);
                }
            });

            // Focus handling
            this.searchInput.addEventListener('focus', () => {
                if (this.searchInput.value.length > 2) {
                    this.showSuggestions();
                }
            });
        }

        setupKeyboardNavigation() {
            let selectedIndex = -1;

            this.searchInput.addEventListener('keydown', (e) => {
                const suggestions = this.suggestionsContainer.querySelectorAll('.suggestion-item');

                switch (e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        selectedIndex = Math.min(selectedIndex + 1, suggestions.length - 1);
                        this.highlightSuggestion(suggestions, selectedIndex);
                        break;

                    case 'ArrowUp':
                        e.preventDefault();
                        selectedIndex = Math.max(selectedIndex - 1, -1);
                        this.highlightSuggestion(suggestions, selectedIndex);
                        break;

                    case 'Enter':
                        e.preventDefault();
                        if (selectedIndex >= 0 && suggestions[selectedIndex]) {
                            this.selectSuggestion(suggestions[selectedIndex]);
                        } else {
                            this.performSearch(this.searchInput.value);
                        }
                        break;

                    case 'Escape':
                        this.hideSuggestions();
                        selectedIndex = -1;
                        break;
                }
            });
        }

        handleSearchInput(query) {
            // Clear existing timeout
            if (this.searchTimeout) {
                clearTimeout(this.searchTimeout);
            }

            // Cancel any pending request
            if (this.currentRequest) {
                this.currentRequest.abort();
            }

            if (query.length < 2) {
                this.hideSuggestions();
                return;
            }

            // Debounce search requests
            this.searchTimeout = setTimeout(() => {
                this.fetchSuggestions(query);
            }, 300);
        }

        async fetchSuggestions(query) {
            if (this.isLoading) return;

            this.isLoading = true;
            this.showLoadingIndicator();

            try {
                const controller = new AbortController();
                this.currentRequest = controller;

                const response = await fetch('/bcm/community/api/knowledge/search-suggestions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: { query: query }
                    }),
                    signal: controller.signal
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                this.displaySuggestions(data.result.suggestions || []);

            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.warn('Failed to fetch search suggestions:', error);
                    this.hideSuggestions();
                }
            } finally {
                this.isLoading = false;
                this.currentRequest = null;
            }
        }

        displaySuggestions(suggestions) {
            if (!this.suggestionsContainer) {
                this.createSuggestionsContainer();
            }

            if (suggestions.length === 0) {
                this.hideSuggestions();
                return;
            }

            let html = '<div class="suggestions-list">';

            suggestions.forEach((suggestion, index) => {
                html += `
                    <div class="suggestion-item" data-index="${index}" data-url="${suggestion.url}">
                        <div class="suggestion-title">${this.escapeHtml(suggestion.title)}</div>
                        <div class="suggestion-category badge badge-${suggestion.category}">${suggestion.category}</div>
                        <div class="suggestion-summary">${this.escapeHtml(suggestion.summary)}</div>
                    </div>
                `;
            });

            html += '</div>';

            this.suggestionsContainer.innerHTML = html;
            this.setupSuggestionClickHandlers();
            this.showSuggestions();
        }

        createSuggestionsContainer() {
            if (!this.suggestionsContainer) {
                this.suggestionsContainer = document.createElement('div');
                this.suggestionsContainer.id = 'search-suggestions';
                this.suggestionsContainer.className = 'search-suggestions';
                this.searchInput.parentNode.appendChild(this.suggestionsContainer);
            }
        }

        setupSuggestionClickHandlers() {
            const suggestionItems = this.suggestionsContainer.querySelectorAll('.suggestion-item');

            suggestionItems.forEach(item => {
                item.addEventListener('click', () => {
                    this.selectSuggestion(item);
                });

                item.addEventListener('mouseenter', () => {
                    this.highlightSuggestion(suggestionItems,
                        parseInt(item.getAttribute('data-index')));
                });
            });
        }

        selectSuggestion(suggestionElement) {
            const url = suggestionElement.getAttribute('data-url');
            if (url) {
                window.location.href = url;
            }
        }

        highlightSuggestion(suggestions, index) {
            suggestions.forEach((item, i) => {
                if (i === index) {
                    item.classList.add('highlighted');
                } else {
                    item.classList.remove('highlighted');
                }
            });
        }

        showSuggestions() {
            if (this.suggestionsContainer) {
                this.suggestionsContainer.classList.add('show');
            }
        }

        hideSuggestions() {
            if (this.suggestionsContainer) {
                this.suggestionsContainer.classList.remove('show');
            }
        }

        showLoadingIndicator() {
            if (this.suggestionsContainer) {
                this.suggestionsContainer.innerHTML = `
                    <div class="loading-indicator">
                        <i class="fas fa-spinner fa-spin"></i> Searching...
                    </div>
                `;
                this.showSuggestions();
            }
        }

        performSearch(query) {
            if (query.trim()) {
                window.location.href = `/bcm/community/knowledge/search?q=${encodeURIComponent(query)}`;
            }
        }

        setupBookmarkHandlers() {
            // Handle bookmark buttons
            document.addEventListener('click', (e) => {
                if (e.target.closest('[onclick*="bookmarkArticle"]')) {
                    e.preventDefault();
                    const button = e.target.closest('button');
                    const onclickAttr = button.getAttribute('onclick');
                    const match = onclickAttr.match(/bookmarkArticle\((\d+)\)/);

                    if (match) {
                        this.toggleBookmark(parseInt(match[1]), button);
                    }
                }
            });
        }

        async toggleBookmark(articleId, button) {
            const originalIcon = button.querySelector('i');
            const originalText = button.textContent;

            // Show loading state
            button.disabled = true;
            if (originalIcon) {
                originalIcon.className = 'fas fa-spinner fa-spin';
            }

            try {
                const response = await fetch(`/bcm/community/api/knowledge/article/${articleId}/bookmark`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: {}
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                const result = data.result;

                if (result.success) {
                    // Update button state
                    if (originalIcon) {
                        originalIcon.className = result.action === 'added' ?
                            'fas fa-bookmark' : 'far fa-bookmark';
                    }

                    // Show notification
                    this.showNotification(
                        result.action === 'added' ? 'Article bookmarked!' : 'Bookmark removed!',
                        'success'
                    );

                    // Update bookmark count in UI if displayed
                    this.updateBookmarkCount(articleId, result.bookmark_count);

                } else {
                    throw new Error(result.error || 'Failed to bookmark article');
                }

            } catch (error) {
                console.error('Bookmark error:', error);
                this.showNotification('Failed to bookmark article', 'error');

                // Restore original icon
                if (originalIcon) {
                    originalIcon.className = 'fas fa-bookmark';
                }
            } finally {
                button.disabled = false;
            }
        }

        updateBookmarkCount(articleId, newCount) {
            // Update bookmark count displays
            const countElements = document.querySelectorAll(`[data-article-id="${articleId}"] .bookmark-count`);
            countElements.forEach(element => {
                element.textContent = newCount;
            });
        }

        setupCopyToClipboard() {
            window.copyToClipboard = (text) => {
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(text).then(() => {
                        this.showNotification('Link copied to clipboard!', 'success');
                    }).catch(() => {
                        this.fallbackCopyToClipboard(text);
                    });
                } else {
                    this.fallbackCopyToClipboard(text);
                }
            };
        }

        fallbackCopyToClipboard(text) {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            try {
                document.execCommand('copy');
                this.showNotification('Link copied to clipboard!', 'success');
            } catch (err) {
                console.error('Failed to copy text: ', err);
                this.showNotification('Failed to copy link', 'error');
            }

            document.body.removeChild(textArea);
        }

        setupPrintHandlers() {
            // Enhance print functionality for articles
            const printButtons = document.querySelectorAll('[onclick="window.print()"]');
            printButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.printArticle();
                });
            });
        }

        printArticle() {
            // Add print-specific styles temporarily
            const printStyles = document.createElement('style');
            printStyles.textContent = `
                @media print {
                    .knowledge-sidebar, .article-actions, .breadcrumb,
                    .btn, button, .dropdown, .article-navigation { display: none !important; }
                    .col-md-8 { width: 100% !important; }
                    .article-content { margin: 0 !important; }
                }
            `;
            document.head.appendChild(printStyles);

            window.print();

            // Remove print styles after printing
            setTimeout(() => {
                document.head.removeChild(printStyles);
            }, 1000);
        }

        showNotification(message, type = 'info') {
            // Create or update notification
            let notification = document.getElementById('knowledge-notification');

            if (!notification) {
                notification = document.createElement('div');
                notification.id = 'knowledge-notification';
                notification.className = 'alert alert-dismissible fade';
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 1050;
                    min-width: 300px;
                `;
                document.body.appendChild(notification);
            }

            const typeClass = {
                'success': 'alert-success',
                'error': 'alert-danger',
                'warning': 'alert-warning',
                'info': 'alert-info'
            }[type] || 'alert-info';

            notification.className = `alert alert-dismissible fade show ${typeClass}`;
            notification.innerHTML = `
                ${message}
                <button type="button" class="close" onclick="this.parentElement.remove()">
                    <span>&times;</span>
                </button>
            `;

            // Auto-hide after 5 seconds
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.classList.remove('show');
                    setTimeout(() => {
                        if (notification.parentElement) {
                            notification.remove();
                        }
                    }, 150);
                }
            }, 5000);
        }

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }

    // Global functions for backward compatibility
    window.searchKnowledge = function() {
        const searchInput = document.getElementById('knowledge-search');
        if (searchInput && searchInput.value.trim()) {
            window.location.href = `/bcm/community/knowledge/search?q=${encodeURIComponent(searchInput.value)}`;
        }
    };

    window.filterByTag = function(tagName) {
        window.location.href = `/bcm/community/knowledge?tag=${encodeURIComponent(tagName)}`;
    };

    window.bookmarkArticle = function(articleId) {
        if (window.knowledgeSearchManager) {
            const button = event.target.closest('button');
            window.knowledgeSearchManager.toggleBookmark(articleId, button);
        }
    };

    // Initialize when DOM is ready
    window.knowledgeSearchManager = new KnowledgeSearchManager();

    // Enhanced search functionality for admin interface
    if (typeof odoo !== 'undefined' && odoo.define) {
        odoo.define('bcm_community.knowledge_search', function (require) {
            'use strict';

            var core = require('web.core');
            var Widget = require('web.Widget');

            var KnowledgeSearchWidget = Widget.extend({
                template: 'bcm_community.knowledge_search_widget',

                events: {
                    'input .knowledge-search-input': '_onSearchInput',
                    'click .knowledge-search-btn': '_onSearchClick',
                },

                init: function (parent, options) {
                    this._super(parent);
                    this.options = options || {};
                    this.searchDelay = 300;
                    this.searchTimeout = null;
                },

                _onSearchInput: function (event) {
                    clearTimeout(this.searchTimeout);
                    var query = event.target.value;

                    if (query.length >= 2) {
                        this.searchTimeout = setTimeout(() => {
                            this._performSearch(query);
                        }, this.searchDelay);
                    }
                },

                _onSearchClick: function () {
                    var query = this.$('.knowledge-search-input').val();
                    this._performSearch(query);
                },

                _performSearch: function (query) {
                    if (!query.trim()) return;

                    this._rpc({
                        route: '/bcm/community/api/knowledge/search-suggestions',
                        params: { query: query }
                    }).then((result) => {
                        this._displayResults(result.suggestions || []);
                    }).catch((error) => {
                        console.error('Search failed:', error);
                    });
                },

                _displayResults: function (suggestions) {
                    // Update UI with search results
                    this.trigger_up('knowledge_search_results', {
                        suggestions: suggestions
                    });
                }
            });

            return KnowledgeSearchWidget;
        });
    }

})();