# -*- coding: utf-8 -*-
"""
BCM Community Knowledge API Controllers
=====================================

API endpoints for knowledge base integration with compliance data
"""

import json
import logging
from datetime import datetime
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)

class BCMKnowledgeAPI(http.Controller):
    """Knowledge Base API for compliance integration"""

    @http.route('/api/bcm/knowledge/gaps', type='json', auth='user', methods=['POST'], cors='*')
    def get_gap_knowledge_articles(self, **kwargs):
        """Get knowledge articles for addressing compliance gaps"""
        try:
            # Получаем критические пробелы из compliance API
            compliance_api = request.env['bcm.compliance.dashboard']
            overview = compliance_api.get_compliance_overview()
            critical_gaps = overview.get('critical_gaps_list', [])
            
            # Ищем связанные knowledge articles
            gap_articles = []
            for gap in critical_gaps:
                # Поиск статей для этого пробела
                articles = request.env['bcm.knowledge.article'].search([
                    ('auto_generated_for_gap', '=', gap['clause']),
                    ('is_published', '=', True)
                ])
                
                # Поиск статей по связанным ISO clauses
                if not articles:
                    iso_clauses = request.env['bcm.iso.clause'].search([
                        ('name', '=', gap['clause'])
                    ])
                    if iso_clauses:
                        articles = request.env['bcm.knowledge.article'].search([
                            ('iso_clauses', 'in', iso_clauses.ids),
                            ('is_published', '=', True)
                        ], limit=3)
                
                article_data = []
                for article in articles:
                    article_data.append({
                        'id': article.id,
                        'title': article.name,
                        'summary': article.summary,
                        'knowledge_type': article.knowledge_type,
                        'compliance_contribution': article.compliance_contribution,
                        'usefulness_score': article.usefulness_score,
                        'view_count': article.view_count,
                        'url': f'/knowledge/article/{article.id}'
                    })
                
                gap_articles.append({
                    'gap': gap,
                    'articles': article_data,
                    'has_remedy': len(article_data) > 0
                })
            
            return {
                'success': True,
                'data': gap_articles,
                'message': f'Found knowledge articles for {len(critical_gaps)} gaps'
            }
            
        except Exception as e:
            _logger.error(f'Error fetching gap knowledge articles: {str(e)}')
            return {
                'success': False,
                'error': 'server_error',
                'message': f'Server error: {str(e)}'
            }

    @http.route('/api/bcm/knowledge/generate-gaps', type='json', auth='user', methods=['POST'], cors='*')
    def auto_generate_gap_articles(self, **kwargs):
        """Auto-generate knowledge articles for compliance gaps"""
        try:
            knowledge_model = request.env['bcm.knowledge.article']
            result = knowledge_model.auto_generate_gap_articles()
            
            return {
                'success': True,
                'data': result,
                'message': 'Gap remedy articles generated successfully'
            }
            
        except Exception as e:
            _logger.error(f'Error generating gap articles: {str(e)}')
            return {
                'success': False,
                'error': 'generation_failed',
                'message': f'Failed to generate articles: {str(e)}'
            }

    @http.route('/api/bcm/knowledge/search', type='json', auth='user', methods=['POST'], cors='*')
    def search_knowledge_articles(self, **kwargs):
        """Search knowledge articles with compliance filtering"""
        try:
            query = kwargs.get('query', '')
            compliance_level = kwargs.get('compliance_level')
            knowledge_type = kwargs.get('knowledge_type')
            limit = kwargs.get('limit', 20)
            
            domain = [('is_published', '=', True)]
            
            if query:
                domain.append('|')
                domain.append(('name', 'ilike', query))
                domain.append(('content', 'ilike', query))
            
            if compliance_level:
                domain.append(('iso_compliance_level', '=', compliance_level))
                
            if knowledge_type:
                domain.append(('knowledge_type', '=', knowledge_type))
            
            articles = request.env['bcm.knowledge.article'].search(domain, limit=limit)
            
            article_data = []
            for article in articles:
                article_data.append({
                    'id': article.id,
                    'title': article.name,
                    'summary': article.summary,
                    'knowledge_type': article.knowledge_type,
                    'compliance_level': article.iso_compliance_level,
                    'compliance_contribution': article.compliance_contribution,
                    'usefulness_score': article.usefulness_score,
                    'view_count': article.view_count,
                    'tags': [tag.name for tag in article.tags],
                    'iso_clauses': [clause.name for clause in article.iso_clauses],
                    'url': f'/knowledge/article/{article.id}',
                    'created_date': article.create_date.isoformat() if article.create_date else None
                })
            
            return {
                'success': True,
                'data': article_data,
                'total': len(article_data),
                'message': f'Found {len(article_data)} knowledge articles'
            }
            
        except Exception as e:
            _logger.error(f'Error searching knowledge articles: {str(e)}')
            return {
                'success': False,
                'error': 'search_failed',
                'message': f'Search failed: {str(e)}'
            }

    @http.route('/knowledge/article/<int:article_id>', type='http', auth='user', methods=['GET'])
    def view_knowledge_article(self, article_id, **kwargs):
        """View knowledge article and update view count"""
        try:
            article = request.env['bcm.knowledge.article'].browse(article_id)
            
            if not article.exists() or not article.is_published:
                return request.redirect('/web#action=&model=&view_type=&menu_id=')
            
            # Увеличиваем счетчик просмотров
            article.sudo().write({'view_count': article.view_count + 1})
            
            # Рендерим статью (можно создать отдельный template)
            return request.render('bcm_community.knowledge_article_view', {
                'article': article,
                'related_gaps': self._get_related_gaps(article),
                'related_modules': article.related_bcm_modules
            })
            
        except Exception as e:
            _logger.error(f'Error viewing knowledge article {article_id}: {str(e)}')
            return request.redirect('/web')

    def _get_related_gaps(self, article):
        """Get compliance gaps related to this article"""
        try:
            if not article.iso_clauses:
                return []
                
            compliance_api = request.env['bcm.compliance.dashboard']
            overview = compliance_api.get_compliance_overview()
            critical_gaps = overview.get('critical_gaps_list', [])
            
            # Найти пробелы, связанные с ISO clauses этой статьи
            article_clauses = article.iso_clauses.mapped('name')
            related_gaps = [gap for gap in critical_gaps if gap['clause'] in article_clauses]
            
            return related_gaps
            
        except Exception as e:
            _logger.warning(f'Could not get related gaps for article {article.id}: {e}')
            return []

    @http.route('/api/bcm/knowledge/dashboard', type='json', auth='user', methods=['POST'], cors='*')
    def get_knowledge_dashboard(self, **kwargs):
        """Get knowledge base dashboard data"""
        try:
            # Статистика knowledge base
            total_articles = request.env['bcm.knowledge.article'].search_count([
                ('is_published', '=', True)
            ])
            
            gap_articles = request.env['bcm.knowledge.article'].search_count([
                ('knowledge_type', '=', 'gap_remedy'),
                ('is_published', '=', True)
            ])
            
            # Топ статьи по usefulness
            top_articles = request.env['bcm.knowledge.article'].search([
                ('is_published', '=', True)
            ], order='usefulness_score desc', limit=5)
            
            top_articles_data = [{
                'id': art.id,
                'title': art.name,
                'usefulness_score': art.usefulness_score,
                'view_count': art.view_count,
                'knowledge_type': art.knowledge_type
            } for art in top_articles]
            
            # Статистика по типам знаний
            knowledge_types = request.env['bcm.knowledge.article'].read_group([
                ('is_published', '=', True)
            ], ['knowledge_type'], ['knowledge_type'])
            
            return {
                'success': True,
                'data': {
                    'total_articles': total_articles,
                    'gap_remedy_articles': gap_articles,
                    'top_articles': top_articles_data,
                    'knowledge_types_distribution': knowledge_types,
                    'coverage_percentage': round((gap_articles / 6) * 100, 1) if gap_articles else 0  # 6 critical gaps
                },
                'message': 'Knowledge dashboard data retrieved'
            }
            
        except Exception as e:
            _logger.error(f'Error getting knowledge dashboard: {str(e)}')
            return {
                'success': False,
                'error': 'dashboard_error',
                'message': f'Dashboard error: {str(e)}'
            }