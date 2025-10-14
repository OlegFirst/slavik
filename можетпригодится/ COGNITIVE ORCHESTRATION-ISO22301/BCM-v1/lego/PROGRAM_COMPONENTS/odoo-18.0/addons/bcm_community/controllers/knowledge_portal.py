# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website.controllers.main import Website
import json
import logging

_logger = logging.getLogger(__name__)


class BCMKnowledgePortal(http.Controller):
    """Knowledge Base Portal Controller"""

    @http.route(['/bcm/community/knowledge', '/bcm/knowledge'], type='http', auth="public", website=True)
    def knowledge_portal(self, **kwargs):
        """Main Knowledge Base Portal Page"""

        # Get search parameters
        search_query = kwargs.get('q', '')
        category_filter = kwargs.get('category', '')
        tag_filter = kwargs.get('tag', '')
        iso_clause_filter = kwargs.get('iso_clause', '')
        page = int(kwargs.get('page', 1))
        items_per_page = 20

        # Build domain for filtering
        domain = [('is_published', '=', True)]

        if category_filter:
            domain.append(('category', '=', category_filter))

        if tag_filter:
            domain.append(('tags.name', 'ilike', tag_filter))

        if iso_clause_filter:
            domain.append(('iso_clauses.name', '=', iso_clause_filter))

        # Full-text search
        if search_query:
            search_domain = [
                '|', '|', '|',
                ('name', 'ilike', search_query),
                ('summary', 'ilike', search_query),
                ('content', 'ilike', search_query),
                ('tags.name', 'ilike', search_query)
            ]
            domain.extend(search_domain)

        # Get articles
        Article = request.env['bcm.knowledge.article'].sudo()
        total_articles = Article.search_count(domain)

        offset = (page - 1) * items_per_page
        articles = Article.search(domain, limit=items_per_page, offset=offset, order='sequence, create_date desc')

        # Get featured articles (top usefulness score)
        featured_articles = Article.search([
            ('is_published', '=', True),
            ('usefulness_score', '>', 5)
        ], limit=6, order='usefulness_score desc')

        # Get recent articles
        recent_articles = Article.search([
            ('is_published', '=', True)
        ], limit=10, order='create_date desc')

        # Get categories with article counts
        categories = self._get_categories_with_counts()

        # Get popular tags
        popular_tags = self._get_popular_tags()

        # Get ISO clauses with article counts
        iso_clauses = self._get_iso_clauses_with_counts()

        # Statistics
        stats = self._get_knowledge_stats()

        # Pagination
        total_pages = (total_articles + items_per_page - 1) // items_per_page

        pagination = {
            'current_page': page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None,
            'total_items': total_articles
        }

        values = {
            'articles': articles,
            'featured_articles': featured_articles,
            'recent_articles': recent_articles,
            'categories': categories,
            'popular_tags': popular_tags,
            'iso_clauses': iso_clauses,
            'search_query': search_query,
            'current_category': category_filter,
            'current_tag': tag_filter,
            'current_iso_clause': iso_clause_filter,
            'pagination': pagination,
            'total_articles': stats['total_articles'],
            'ai_generated_articles': stats['ai_generated_articles'],
            'exercise_derived_articles': stats['exercise_derived_articles'],
            'community_articles': stats['community_articles'],
        }

        return request.render('bcm_community.knowledge_base_portal', values)

    @http.route('/bcm/community/knowledge/article/<int:article_id>', type='http', auth="public", website=True)
    def knowledge_article_detail(self, article_id, **kwargs):
        """Individual Article Detail Page"""

        Article = request.env['bcm.knowledge.article'].sudo()
        article = Article.browse(article_id)

        if not article.exists() or not article.is_published:
            return request.not_found()

        # Increment view count
        article.sudo().write({'view_count': article.view_count + 1})

        # Get related articles
        related_articles = Article.search([
            ('is_published', '=', True),
            ('id', '!=', article_id),
            '|', '|',
            ('category', '=', article.category),
            ('tags', 'in', article.tags.ids),
            ('iso_clauses', 'in', article.iso_clauses.ids)
        ], limit=5, order='usefulness_score desc')

        # Get article navigation (prev/next)
        prev_article = Article.search([
            ('is_published', '=', True),
            ('sequence', '<', article.sequence)
        ], limit=1, order='sequence desc')

        next_article = Article.search([
            ('is_published', '=', True),
            ('sequence', '>', article.sequence)
        ], limit=1, order='sequence asc')

        values = {
            'article': article,
            'related_articles': related_articles,
            'prev_article': prev_article,
            'next_article': next_article,
            'page_title': article.name,
            'meta_description': article.summary,
        }

        return request.render('bcm_community.knowledge_article_detail', values)

    @http.route('/bcm/community/knowledge/search', type='http', auth="public", website=True)
    def knowledge_search(self, **kwargs):
        """Advanced Search Page"""

        search_query = kwargs.get('q', '')

        if not search_query:
            return request.redirect('/bcm/community/knowledge')

        # Perform search with highlighting
        Article = request.env['bcm.knowledge.article'].sudo()

        # Full-text search with ranking
        domain = [
            ('is_published', '=', True),
            '|', '|', '|',
            ('name', 'ilike', search_query),
            ('summary', 'ilike', search_query),
            ('content', 'ilike', search_query),
            ('tags.name', 'ilike', search_query)
        ]

        articles = Article.search(domain, order='usefulness_score desc')

        # Group results by category
        results_by_category = {}
        for article in articles:
            category = article.category
            if category not in results_by_category:
                results_by_category[category] = []
            results_by_category[category].append(article)

        values = {
            'search_query': search_query,
            'articles': articles,
            'results_by_category': results_by_category,
            'total_results': len(articles),
        }

        return request.render('bcm_community.knowledge_search_results', values)

    @http.route('/bcm/community/api/knowledge/article/<int:article_id>/bookmark',
                type='json', auth="user", methods=['POST'])
    def bookmark_article(self, article_id, **kwargs):
        """Bookmark an article (JSON API)"""

        try:
            Article = request.env['bcm.knowledge.article']
            article = Article.browse(article_id)

            if not article.exists():
                return {'success': False, 'error': 'Article not found'}

            # Check if already bookmarked
            Bookmark = request.env['bcm.knowledge.bookmark']
            existing_bookmark = Bookmark.search([
                ('article_id', '=', article_id),
                ('user_id', '=', request.env.user.id)
            ])

            if existing_bookmark:
                existing_bookmark.unlink()
                article.write({'bookmark_count': article.bookmark_count - 1})
                return {'success': True, 'action': 'removed', 'bookmark_count': article.bookmark_count}
            else:
                Bookmark.create({
                    'article_id': article_id,
                    'user_id': request.env.user.id
                })
                article.write({'bookmark_count': article.bookmark_count + 1})
                return {'success': True, 'action': 'added', 'bookmark_count': article.bookmark_count}

        except Exception as e:
            _logger.error(f'Error bookmarking article {article_id}: {e}')
            return {'success': False, 'error': str(e)}

    @http.route('/bcm/community/api/knowledge/search-suggestions',
                type='json', auth="public", methods=['GET'])
    def search_suggestions(self, query='', **kwargs):
        """Get search suggestions for auto-complete"""

        if len(query) < 2:
            return {'suggestions': []}

        Article = request.env['bcm.knowledge.article'].sudo()

        # Search in titles and tags
        articles = Article.search([
            ('is_published', '=', True),
            '|',
            ('name', 'ilike', query),
            ('tags.name', 'ilike', query)
        ], limit=10, order='usefulness_score desc')

        suggestions = []
        for article in articles:
            suggestions.append({
                'title': article.name,
                'category': article.category,
                'url': f'/bcm/community/knowledge/article/{article.id}',
                'summary': article.summary[:100] + '...' if len(article.summary) > 100 else article.summary
            })

        return {'suggestions': suggestions}

    @http.route('/bcm/community/api/knowledge/generate-from-exercise',
                type='json', auth="user", methods=['POST'])
    def generate_article_from_exercise(self, exercise_id, **kwargs):
        """Generate knowledge article from exercise results"""

        try:
            # Check user permissions
            if not request.env.user.has_group('bcm_core.group_bcm_user'):
                return {'success': False, 'error': 'Insufficient permissions'}

            Article = request.env['bcm.knowledge.article']
            article = Article.create_from_exercise_results(exercise_id)

            if article:
                return {
                    'success': True,
                    'article_id': article.id,
                    'article_url': f'/web#id={article.id}&model=bcm.knowledge.article'
                }
            else:
                return {'success': False, 'error': 'Failed to generate article'}

        except Exception as e:
            _logger.error(f'Error generating article from exercise {exercise_id}: {e}')
            return {'success': False, 'error': str(e)}

    def _get_categories_with_counts(self):
        """Get article categories with counts"""
        Article = request.env['bcm.knowledge.article'].sudo()

        categories = []
        category_options = Article._fields['category'].selection

        for code, name in category_options:
            count = Article.search_count([
                ('is_published', '=', True),
                ('category', '=', code)
            ])
            if count > 0:
                categories.append({
                    'code': code,
                    'name': name,
                    'article_count': count,
                    'icon': self._get_category_icon(code)
                })

        return sorted(categories, key=lambda x: x['article_count'], reverse=True)

    def _get_popular_tags(self):
        """Get popular tags with article counts"""
        Tag = request.env['bcm.knowledge.tag'].sudo()

        # Get tags with published articles
        tags = Tag.search([])
        popular_tags = []

        for tag in tags:
            article_count = request.env['bcm.knowledge.article'].sudo().search_count([
                ('is_published', '=', True),
                ('tags', 'in', [tag.id])
            ])

            if article_count > 0:
                popular_tags.append({
                    'name': tag.name,
                    'article_count': article_count,
                    'color': tag.color or 1
                })

        return sorted(popular_tags, key=lambda x: x['article_count'], reverse=True)[:20]

    def _get_iso_clauses_with_counts(self):
        """Get ISO clauses with article counts"""
        Clause = request.env['bcm.iso.clause'].sudo()

        clauses = Clause.search([])
        iso_clauses = []

        for clause in clauses:
            article_count = request.env['bcm.knowledge.article'].sudo().search_count([
                ('is_published', '=', True),
                ('iso_clauses', 'in', [clause.id])
            ])

            if article_count > 0:
                iso_clauses.append({
                    'name': clause.name,
                    'title': clause.title,
                    'article_count': article_count
                })

        return sorted(iso_clauses, key=lambda x: x['name'])

    def _get_knowledge_stats(self):
        """Get knowledge base statistics"""
        Article = request.env['bcm.knowledge.article'].sudo()

        total_articles = Article.search_count([('is_published', '=', True)])
        ai_generated_articles = Article.search_count([
            ('is_published', '=', True),
            ('article_type', '=', 'ai_generated')
        ])
        exercise_derived_articles = Article.search_count([
            ('is_published', '=', True),
            ('article_type', '=', 'exercise_derived')
        ])
        community_articles = Article.search_count([
            ('is_published', '=', True),
            ('article_type', '=', 'community_driven')
        ])

        return {
            'total_articles': total_articles,
            'ai_generated_articles': ai_generated_articles,
            'exercise_derived_articles': exercise_derived_articles,
            'community_articles': community_articles
        }

    def _get_category_icon(self, category_code):
        """Get icon for article category"""
        icons = {
            'best_practice': 'fas fa-star',
            'lesson_learned': 'fas fa-lightbulb',
            'procedure': 'fas fa-list-check',
            'case_study': 'fas fa-book',
            'template_guide': 'fas fa-file-alt',
            'troubleshooting': 'fas fa-tools',
            'compliance': 'fas fa-check-circle'
        }
        return icons.get(category_code, 'fas fa-file-text')


