# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class BCMMarketplaceAPI(http.Controller):

    def _get_cors_headers(self):
        """Get CORS headers for API responses"""
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
            'Access-Control-Max-Age': '3600'
        }

    def _json_response(self, data, status=200):
        """Helper method to return JSON response with CORS headers"""
        return request.make_response(
            json.dumps(data, default=str),
            headers=dict(self._get_cors_headers(), **{'Content-Type': 'application/json'}),
            status=status
        )

    def _error_response(self, message, status=400):
        """Helper method to return error response"""
        return self._json_response({
            'success': False,
            'error': message
        }, status=status)

    def _success_response(self, data, message=None):
        """Helper method to return success response"""
        response = {
            'success': True,
            'data': data
        }
        if message:
            response['message'] = message
        return self._json_response(response)

    # Authentication endpoints
    @http.route('/api/v1/auth/login', type='json', auth="none", methods=['POST'], csrf=False, cors='*')
    def auth_login(self, **kwargs):
        try:
            data = request.get_json_data()
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return self._error_response('Email and password are required')

            # Authenticate user
            uid = request.session.authenticate(request.session.db, email, password)
            if not uid:
                return self._error_response('Invalid credentials', 401)

            user = request.env['res.users'].browse(uid)

            # Check if user has specialist profile
            specialist = request.env['bcm.specialist'].search([('user_id', '=', uid)], limit=1)
            role = 'specialist' if specialist else 'client'

            return self._success_response({
                'token': request.session.sid,  # Using session ID as token
                'user': {
                    'id': str(user.id),
                    'name': user.name,
                    'email': user.email,
                    'avatar': f'/web/image/res.users/{user.id}/avatar_128' if user.avatar_128 else None,
                    'role': role
                }
            })

        except Exception as e:
            _logger.error(f"Login error: {str(e)}")
            return self._error_response('Authentication failed')

    @http.route('/api/v1/auth/me', type='json', auth="user", methods=['GET'], csrf=False, cors='*')
    def auth_me(self, **kwargs):
        try:
            user = request.env.user
            specialist = request.env['bcm.specialist'].search([('user_id', '=', user.id)], limit=1)
            role = 'specialist' if specialist else 'client'

            return self._success_response({
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'avatar': f'/web/image/res.users/{user.id}/avatar_128' if user.avatar_128 else None,
                'role': role
            })
        except Exception as e:
            _logger.error(f"Get user error: {str(e)}")
            return self._error_response('Failed to get user info', 500)

    # Specialists endpoints
    @http.route('/api/v1/specialists/search', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def search_specialists(self, **kwargs):
        try:
            data = request.get_json_data() or {}

            # Build domain for search
            domain = []

            # Text search
            query = data.get('query')
            if query:
                domain.extend([
                    '|', '|', '|',
                    ('name', 'ilike', query),
                    ('title', 'ilike', query),
                    ('bio', 'ilike', query),
                    ('specialization_ids.name', 'ilike', query)
                ])

            # Filters
            if data.get('specializations'):
                domain.append(('specialization_ids', 'in', data['specializations']))

            if data.get('industries'):
                domain.append(('industry_ids', 'in', data['industries']))

            if data.get('verifiedOnly'):
                domain.append(('is_verified', '=', True))

            if data.get('availability') and data['availability'] != 'all':
                domain.append(('availability_status', '=', data['availability']))

            # Location filters
            location = data.get('location', {})
            if location.get('country'):
                domain.append(('location_country', '=', location['country']))
            if location.get('city'):
                domain.append(('location_city', 'ilike', location['city']))
            if location.get('remote'):
                domain.append(('remote_available', '=', True))

            # Rating filter
            rating = data.get('rating', {})
            if rating.get('min'):
                domain.append(('rating', '>=', rating['min']))

            # Experience filter
            experience = data.get('experience', {})
            if experience.get('min'):
                domain.append(('years_experience', '>=', experience['min']))

            # Hourly rate filter
            hourly_rate = data.get('hourlyRate', {})
            if hourly_rate.get('min'):
                domain.append(('hourly_rate', '>=', hourly_rate['min']))
            if hourly_rate.get('max'):
                domain.append(('hourly_rate', '<=', hourly_rate['max']))

            # Pagination
            page = data.get('page', 1)
            page_size = data.get('pageSize', 12)
            offset = (page - 1) * page_size

            # Sorting
            order = 'rating desc'
            sort_by = data.get('sortBy')
            if sort_by == 'price_low':
                order = 'hourly_rate asc'
            elif sort_by == 'price_high':
                order = 'hourly_rate desc'
            elif sort_by == 'experience':
                order = 'years_experience desc'
            elif sort_by == 'rating':
                order = 'rating desc'

            # Execute search
            specialists = request.env['bcm.specialist'].search(domain, offset=offset, limit=page_size, order=order)
            total = request.env['bcm.specialist'].search_count(domain)

            # Format results
            items = []
            for specialist in specialists:
                items.append(self._format_specialist(specialist))

            return self._success_response({
                'items': items,
                'total': total,
                'page': page,
                'pageSize': page_size,
                'totalPages': (total + page_size - 1) // page_size
            })

        except Exception as e:
            _logger.error(f"Search specialists error: {str(e)}")
            return self._error_response('Search failed', 500)

    @http.route('/api/v1/specialists/<int:specialist_id>', type='json', auth="public", methods=['GET'], csrf=False, cors='*')
    def get_specialist(self, specialist_id, **kwargs):
        try:
            specialist = request.env['bcm.specialist'].browse(specialist_id)
            if not specialist.exists():
                return self._error_response('Specialist not found', 404)

            return self._success_response(self._format_specialist_detailed(specialist))

        except Exception as e:
            _logger.error(f"Get specialist error: {str(e)}")
            return self._error_response('Failed to get specialist', 500)

    # Service Requests endpoints
    @http.route('/api/v1/requests', type='json', auth="user", methods=['GET'], csrf=False, cors='*')
    def get_requests(self, **kwargs):
        try:
            data = request.get_json_data() or {}

            domain = []
            # Add filters based on user role
            user = request.env.user
            specialist = request.env['bcm.specialist'].search([('user_id', '=', user.id)], limit=1)

            if specialist:
                # Specialist can see public requests or invited requests
                domain = [
                    '|',
                    ('is_public', '=', True),
                    ('invited_specialist_ids', 'in', [specialist.id])
                ]
            else:
                # Client can see only their own requests
                domain = [('client_user_id', '=', user.id)]

            # Pagination
            page = data.get('page', 1)
            page_size = data.get('pageSize', 10)
            offset = (page - 1) * page_size

            requests = request.env['bcm.service.request'].search(
                domain, offset=offset, limit=page_size, order='create_date desc'
            )
            total = request.env['bcm.service.request'].search_count(domain)

            items = []
            for req in requests:
                items.append(self._format_service_request(req))

            return self._success_response({
                'items': items,
                'total': total,
                'page': page,
                'pageSize': page_size,
                'totalPages': (total + page_size - 1) // page_size
            })

        except Exception as e:
            _logger.error(f"Get requests error: {str(e)}")
            return self._error_response('Failed to get requests', 500)

    # Reference data endpoints
    @http.route('/api/v1/reference/specializations', type='json', auth="public", methods=['GET'], csrf=False, cors='*')
    def get_specializations(self, **kwargs):
        try:
            specializations = request.env['bcm.specialization'].search([])
            data = [{
                'id': spec.id,
                'name': spec.name,
                'code': spec.code if hasattr(spec, 'code') else str(spec.id)
            } for spec in specializations]

            return self._success_response(data)
        except Exception as e:
            _logger.error(f"Get specializations error: {str(e)}")
            return self._error_response('Failed to get specializations', 500)

    @http.route('/api/v1/reference/industries', type='json', auth="public", methods=['GET'], csrf=False, cors='*')
    def get_industries(self, **kwargs):
        try:
            industries = request.env['bcm.industry'].search([])
            data = [{
                'id': industry.id,
                'name': industry.name,
                'code': industry.code if hasattr(industry, 'code') else str(industry.id)
            } for industry in industries]

            return self._success_response(data)
        except Exception as e:
            _logger.error(f"Get industries error: {str(e)}")
            return self._error_response('Failed to get industries', 500)

    def _format_specialist(self, specialist):
        """Format specialist data for API response"""
        return {
            'id': specialist.id,
            'userId': specialist.user_id.id,
            'name': specialist.name,
            'title': specialist.title or '',
            'bio': specialist.bio or '',
            'yearsExperience': specialist.years_experience or 0,
            'hourlyRate': specialist.hourly_rate or 0,
            'currency': specialist.currency_id.name if specialist.currency_id else 'USD',
            'avatar': f'/web/image/bcm.specialist/{specialist.id}/avatar_128' if specialist.avatar_128 else None,
            'rating': specialist.rating or 0,
            'reviewCount': specialist.review_count or 0,
            'completedProjects': specialist.completed_projects or 0,
            'isVerified': specialist.is_verified or False,
            'availabilityStatus': specialist.availability_status or 'unavailable',
            'location': {
                'country': specialist.location_country or '',
                'city': specialist.location_city or '',
                'timezone': specialist.timezone or ''
            },
            'remoteAvailable': specialist.remote_available or False,
            'onsiteAvailable': specialist.onsite_available or False,
            'specializations': [{
                'id': spec.id,
                'name': spec.name,
                'code': getattr(spec, 'code', str(spec.id))
            } for spec in specialist.specialization_ids],
            'industries': [{
                'id': ind.id,
                'name': ind.name,
                'code': getattr(ind, 'code', str(ind.id))
            } for ind in specialist.industry_ids],
            'services': [{
                'id': service.id,
                'name': service.name,
                'description': service.description or '',
                'serviceType': service.service_type or 'other',
                'basePrice': service.base_price or 0,
                'currency': service.currency_id.name if service.currency_id else 'USD'
            } for service in specialist.service_ids[:3]],  # Limit to first 3 services
            'profileCompletion': specialist.profile_completion or 0,
            'createdAt': specialist.create_date,
            'updatedAt': specialist.write_date
        }

    def _format_specialist_detailed(self, specialist):
        """Format detailed specialist data"""
        basic_data = self._format_specialist(specialist)

        # Add detailed information
        basic_data.update({
            'certifications': [{
                'id': cert.id,
                'name': cert.name,
                'issuingOrganization': cert.issuing_organization or '',
                'issueDate': cert.issue_date,
                'expiryDate': cert.expiry_date,
                'isVerified': cert.is_verified or False
            } for cert in specialist.certification_ids],

            'services': [{
                'id': service.id,
                'name': service.name,
                'description': service.description or '',
                'serviceType': service.service_type or 'other',
                'pricingModel': service.pricing_model or 'hourly',
                'basePrice': service.base_price or 0,
                'currency': service.currency_id.name if service.currency_id else 'USD',
                'durationEstimate': service.duration_estimate or 0,
                'deliveryMode': service.delivery_mode or 'remote'
            } for service in specialist.service_ids],

            'portfolioItems': [{
                'id': item.id,
                'name': item.name,
                'description': item.description or '',
                'date': item.date,
                'duration': item.duration or '',
                'role': item.role or '',
                'keyAchievements': item.key_achievements or '',
                'isFeatured': item.is_featured or False
            } for item in specialist.portfolio_ids if hasattr(specialist, 'portfolio_ids')],

            'languages': [{
                'code': lang.code,
                'name': lang.name,
                'level': lang.level or 'basic'
            } for lang in specialist.language_ids if hasattr(specialist, 'language_ids')]
        })

        return basic_data

    def _format_service_request(self, request_obj):
        """Format service request data for API response"""
        return {
            'id': request_obj.id,
            'name': request_obj.name,
            'description': request_obj.description or '',
            'clientId': request_obj.client_id.id,
            'clientName': request_obj.client_id.name,
            'companyName': request_obj.company_name or '',
            'serviceType': request_obj.service_type or 'other',
            'urgency': request_obj.urgency or 'medium',
            'scopeOfWork': request_obj.scope_of_work or '',
            'deliverables': request_obj.deliverables or '',
            'startDate': request_obj.start_date,
            'endDate': request_obj.end_date,
            'budgetType': request_obj.budget_type or 'negotiable',
            'budgetMin': request_obj.budget_min or 0,
            'budgetMax': request_obj.budget_max or 0,
            'currency': request_obj.currency_id.name if request_obj.currency_id else 'USD',
            'workLocation': request_obj.work_location or 'remote',
            'locationCountry': request_obj.location_country or '',
            'locationCity': request_obj.location_city or '',
            'state': request_obj.state or 'draft',
            'proposalCount': request_obj.proposal_count or 0,
            'isPublic': request_obj.is_public or False,
            'postedDate': request_obj.posted_date,
            'deadline': request_obj.deadline,
            'createdAt': request_obj.create_date,
            'updatedAt': request_obj.write_date
        }

    # Solutions endpoints
    @http.route('/api/v1/solutions/search', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def search_solutions(self, **kwargs):
        try:
            data = request.get_json_data() or {}

            # Build domain for search
            domain = []

            # Text search
            query = data.get('query')
            if query:
                domain.extend([
                    '|', '|',
                    ('name', 'ilike', query),
                    ('description', 'ilike', query),
                    ('tags', 'ilike', query)
                ])

            # Filters
            if data.get('category') and data['category'] != 'All Categories':
                domain.append(('category', '=', data['category']))

            if data.get('type') and data['type'] != 'All Types':
                domain.append(('solution_type', '=', data['type']))

            if data.get('priceRange'):
                price_range = data['priceRange']
                if price_range.get('min'):
                    domain.append(('price', '>=', price_range['min']))
                if price_range.get('max'):
                    domain.append(('price', '<=', price_range['max']))

            # Pagination
            page = data.get('page', 1)
            page_size = data.get('pageSize', 12)
            offset = (page - 1) * page_size

            # Sorting
            order = 'featured desc, create_date desc'
            sort_by = data.get('sortBy')
            if sort_by == 'price_low':
                order = 'price asc'
            elif sort_by == 'price_high':
                order = 'price desc'
            elif sort_by == 'rating':
                order = 'rating desc'
            elif sort_by == 'downloads':
                order = 'download_count desc'

            # Execute search (assuming we have bcm.solution model)
            solutions = request.env['bcm.solution'].search(domain, offset=offset, limit=page_size, order=order)
            total = request.env['bcm.solution'].search_count(domain)

            items = []
            for solution in solutions:
                items.append(self._format_solution(solution))

            return self._success_response({
                'items': items,
                'total': total,
                'page': page,
                'pageSize': page_size,
                'totalPages': (total + page_size - 1) // page_size
            })

        except Exception as e:
            _logger.error(f"Search solutions error: {str(e)}")
            return self._error_response('Search failed', 500)

    # Knowledge Base endpoints
    @http.route('/api/v1/knowledge/search', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def search_knowledge(self, **kwargs):
        try:
            data = request.get_json_data() or {}

            domain = []

            # Text search
            query = data.get('query')
            if query:
                domain.extend([
                    '|', '|', '|',
                    ('name', 'ilike', query),
                    ('summary', 'ilike', query),
                    ('content', 'ilike', query),
                    ('tags.name', 'ilike', query)
                ])

            # Filters
            if data.get('category') and data['category'] != 'All Categories':
                domain.append(('category', '=', data['category']))

            if data.get('type') and data['type'] != 'all':
                domain.append(('article_type', '=', data['type']))

            if data.get('difficulty') and data['difficulty'] != 'all':
                domain.append(('difficulty', '=', data['difficulty']))

            # Only published articles
            domain.append(('is_published', '=', True))

            # Pagination
            page = data.get('page', 1)
            page_size = data.get('pageSize', 12)
            offset = (page - 1) * page_size

            # Sorting
            order = 'usefulness_score desc, view_count desc'
            sort_by = data.get('sortBy')
            if sort_by == 'newest':
                order = 'create_date desc'
            elif sort_by == 'views':
                order = 'view_count desc'
            elif sort_by == 'rating':
                order = 'usefulness_score desc'

            articles = request.env['bcm.knowledge.article'].search(domain, offset=offset, limit=page_size, order=order)
            total = request.env['bcm.knowledge.article'].search_count(domain)

            items = []
            for article in articles:
                items.append(self._format_knowledge_article(article))

            return self._success_response({
                'items': items,
                'total': total,
                'page': page,
                'pageSize': page_size,
                'totalPages': (total + page_size - 1) // page_size
            })

        except Exception as e:
            _logger.error(f"Search knowledge error: {str(e)}")
            return self._error_response('Search failed', 500)

    # Case Studies endpoints
    @http.route('/api/v1/cases/search', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def search_cases(self, **kwargs):
        try:
            data = request.get_json_data() or {}

            domain = []

            # Text search
            query = data.get('query')
            if query:
                domain.extend([
                    '|', '|', '|',
                    ('title', 'ilike', query),
                    ('summary', 'ilike', query),
                    ('challenge', 'ilike', query),
                    ('tags', 'ilike', query)
                ])

            # Filters
            if data.get('industry') and data['industry'] != 'All Industries':
                domain.append(('industry', '=', data['industry']))

            if data.get('companySize') and data['companySize'] != 'All Sizes':
                domain.append(('company_size', '=', data['companySize']))

            # Only published cases
            domain.append(('is_published', '=', True))

            # Pagination
            page = data.get('page', 1)
            page_size = data.get('pageSize', 12)
            offset = (page - 1) * page_size

            # Sorting
            order = 'featured desc, view_count desc'
            sort_by = data.get('sortBy')
            if sort_by == 'newest':
                order = 'publish_date desc'
            elif sort_by == 'budget_high':
                order = 'budget_max desc'
            elif sort_by == 'budget_low':
                order = 'budget_min asc'

            # Execute search (assuming we have bcm.case.study model)
            cases = request.env['bcm.case.study'].search(domain, offset=offset, limit=page_size, order=order)
            total = request.env['bcm.case.study'].search_count(domain)

            items = []
            for case in cases:
                items.append(self._format_case_study(case))

            return self._success_response({
                'items': items,
                'total': total,
                'page': page,
                'pageSize': page_size,
                'totalPages': (total + page_size - 1) // page_size
            })

        except Exception as e:
            _logger.error(f"Search cases error: {str(e)}")
            return self._error_response('Search failed', 500)

    def _format_solution(self, solution):
        """Format solution data for API response"""
        return {
            'id': solution.id,
            'title': solution.name,
            'description': solution.description or '',
            'category': solution.category or '',
            'type': solution.solution_type or 'template',
            'author': {
                'name': solution.author_id.name if solution.author_id else '',
                'verified': getattr(solution.author_id, 'is_verified', False),
                'company': getattr(solution.author_id, 'company_name', ''),
                'avatar': f'/web/image/res.users/{solution.author_id.id}/avatar_128' if solution.author_id and solution.author_id.avatar_128 else None
            },
            'price': solution.price or 0,
            'currency': solution.currency_id.name if solution.currency_id else 'USD',
            'rating': solution.rating or 0,
            'reviewCount': solution.review_count or 0,
            'downloadCount': solution.download_count or 0,
            'tags': solution.tags.split(',') if solution.tags else [],
            'format': solution.file_formats.split(',') if solution.file_formats else [],
            'compliance': solution.compliance_standards.split(',') if solution.compliance_standards else [],
            'industries': solution.target_industries.split(',') if solution.target_industries else [],
            'lastUpdated': solution.write_date,
            'featured': solution.featured or False,
            'preview': 'Available' if solution.preview_available else 'Limited'
        }

    def _format_knowledge_article(self, article):
        """Format knowledge article data for API response"""
        return {
            'id': article.id,
            'title': article.name,
            'summary': article.summary or '',
            'category': article.category or '',
            'type': article.article_type or 'best_practice',
            'author': {
                'name': article.create_uid.name,
                'verified': getattr(article.create_uid, 'is_verified', False),
                'title': getattr(article.create_uid, 'job_title', ''),
                'avatar': f'/web/image/res.users/{article.create_uid.id}/avatar_128' if article.create_uid.avatar_128 else None
            },
            'publishDate': article.create_date,
            'readTime': article.estimated_read_time or 5,
            'viewCount': article.view_count or 0,
            'bookmarkCount': article.bookmark_count or 0,
            'usefulness': article.usefulness_score or 0,
            'tags': [tag.name for tag in article.tags] if article.tags else [],
            'isoClause': article.iso_clauses[0].name if article.iso_clauses else None,
            'difficulty': getattr(article, 'difficulty', 'intermediate'),
            'featured': getattr(article, 'featured', False)
        }

    def _format_case_study(self, case):
        """Format case study data for API response"""
        return {
            'id': case.id,
            'title': case.title,
            'summary': case.summary or '',
            'challenge': case.challenge or '',
            'solution': case.solution or '',
            'results': case.results or '',
            'industry': case.industry or '',
            'company': {
                'name': case.company_name or '',
                'size': case.company_size or '',
                'location': case.company_location or ''
            },
            'consultant': {
                'name': case.consultant_id.name if case.consultant_id else '',
                'verified': getattr(case.consultant_id, 'is_verified', False),
                'company': getattr(case.consultant_id, 'company_name', ''),
                'avatar': f'/web/image/res.users/{case.consultant_id.id}/avatar_128' if case.consultant_id and case.consultant_id.avatar_128 else None
            },
            'duration': case.project_duration or '',
            'budget': {
                'range': f"${case.budget_min or 0} - ${case.budget_max or 0}",
                'currency': case.currency_id.name if case.currency_id else 'USD'
            },
            'tags': case.tags.split(',') if case.tags else [],
            'metrics': self._parse_metrics(case.key_metrics) if case.key_metrics else [],
            'publishDate': case.publish_date or case.create_date,
            'viewCount': case.view_count or 0,
            'likeCount': case.like_count or 0,
            'downloadCount': case.download_count or 0,
            'featured': case.featured or False,
            'compliance': case.compliance_standards.split(',') if case.compliance_standards else [],
            'attachments': self._format_attachments(case.attachment_ids) if case.attachment_ids else []
        }

    def _parse_metrics(self, metrics_json):
        """Parse metrics JSON string"""
        try:
            import json
            return json.loads(metrics_json) if metrics_json else []
        except:
            return []

    def _format_attachments(self, attachments):
        """Format attachment data"""
        return [{
            'name': att.name,
            'type': att.mimetype or 'PDF',
            'size': f"{round(att.file_size / 1024 / 1024, 1)} MB" if att.file_size else '0 MB',
            'url': f'/web/content/{att.id}'
        } for att in attachments]

    # OPTIONS handler for CORS preflight requests
    @http.route([
        '/api/v1/auth/login',
        '/api/v1/auth/me',
        '/api/v1/specialists/search',
        '/api/v1/specialists/<path:path>',
        '/api/v1/requests',
        '/api/v1/solutions/search',
        '/api/v1/knowledge/search',
        '/api/v1/cases/search',
        '/api/v1/reference/<path:path>'
    ], type='http', auth="none", methods=['OPTIONS'], csrf=False, cors='*')
    def preflight_handler(self, **kwargs):
        return request.make_response('', headers=self._get_cors_headers())