# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import pytz

class BcmSpecialist(models.Model):
    _name = 'bcm.specialist'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'BCM Specialist Profile'
    _order = 'rating desc, name'

    # Basic Information
    name = fields.Char('Full Name', required=True, tracking=True)
    user_id = fields.Many2one('res.users', 'User Account', required=True)
    partner_id = fields.Many2one('res.partner', 'Contact', related='user_id.partner_id')
    
    # Professional Information
    title = fields.Char('Professional Title', help='e.g., Senior BCM Consultant, Risk Manager')
    bio = fields.Text('Professional Bio')
    years_experience = fields.Integer('Years of Experience')
    hourly_rate = fields.Float('Hourly Rate', help='Rate in USD/hour')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    # Specializations
    specialization_ids = fields.Many2many(
        'bcm.specialization',
        'bcm_specialist_specialization_rel',
        'specialist_id',
        'specialization_id',
        string='Specializations'
    )
    
    industry_ids = fields.Many2many(
        'bcm.industry',
        'bcm_specialist_industry_rel',
        'specialist_id',
        'industry_id',
        string='Industry Experience'
    )
    
    # Certifications
    certification_ids = fields.One2many('bcm.specialist.certification', 'specialist_id', 'Certifications')
    
    # Service Offerings
    service_ids = fields.One2many('bcm.specialist.service', 'specialist_id', 'Services Offered')
    
    # Availability
    availability_status = fields.Selection([
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('unavailable', 'Unavailable')
    ], default='available', string='Availability Status', tracking=True)
    
    availability_hours = fields.Text('Availability Hours', help='JSON format for weekly availability')
    timezone = fields.Selection('_tz_get', string='Timezone', default=lambda self: self.env.user.tz)
    
    # Location
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one('res.country.state', 'State')
    city = fields.Char('City')
    location_country = fields.Char('Location Country', related='country_id.name', store=True)
    location_city = fields.Char('Location City', related='city', store=True)
    remote_available = fields.Boolean('Available for Remote Work', default=True)
    onsite_available = fields.Boolean('Available for Onsite Work', default=True)
    
    # Rating and Reviews
    rating = fields.Float('Average Rating', compute='_compute_rating', store=True)
    review_count = fields.Integer('Number of Reviews', compute='_compute_rating', store=True)
    completed_projects = fields.Integer('Completed Projects')
    
    # Verification
    is_verified = fields.Boolean('Verified Specialist', default=False)
    verification_date = fields.Date('Verification Date')
    verification_notes = fields.Text('Verification Notes')
    
    # Languages
    language_ids = fields.Many2many(
        'res.lang',
        'bcm_specialist_language_rel',
        'specialist_id',
        'lang_id',
        string='Languages Spoken'
    )
    
    # Portfolio
    portfolio_ids = fields.One2many('bcm.specialist.portfolio', 'specialist_id', 'Portfolio Items')
    
    # Engagement Metrics
    response_time = fields.Float('Average Response Time (hours)')
    acceptance_rate = fields.Float('Project Acceptance Rate (%)')
    
    # Status
    active = fields.Boolean('Active', default=True)
    profile_completion = fields.Float('Profile Completion', compute='_compute_profile_completion')
    
    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]
    
    @api.depends('portfolio_ids', 'certification_ids', 'service_ids')
    def _compute_profile_completion(self):
        for record in self:
            completion = 0
            if record.name: completion += 10
            if record.bio: completion += 10
            if record.title: completion += 10
            if record.years_experience: completion += 10
            if record.specialization_ids: completion += 10
            if record.industry_ids: completion += 10
            if record.certification_ids: completion += 10
            if record.service_ids: completion += 10
            if record.portfolio_ids: completion += 10
            if record.image_1920: completion += 10
            record.profile_completion = completion


class BcmSpecialization(models.Model):
    _name = 'bcm.specialization'
    _description = 'BCM Specialization Area'
    _order = 'sequence, name'
    
    name = fields.Char('Specialization', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)
    icon = fields.Char('Icon Class')
    active = fields.Boolean('Active', default=True)


class BcmIndustry(models.Model):
    _name = 'bcm.industry'
    _description = 'Industry Sector'
    
    name = fields.Char('Industry', required=True)
    code = fields.Char('Code', required=True)
    parent_id = fields.Many2one('bcm.industry', 'Parent Industry')
    child_ids = fields.One2many('bcm.industry', 'parent_id', 'Sub-Industries')
    active = fields.Boolean('Active', default=True)


class BcmSpecialistCertification(models.Model):
    _name = 'bcm.specialist.certification'
    _description = 'Specialist Certification'
    
    specialist_id = fields.Many2one('bcm.specialist', 'Specialist', required=True, ondelete='cascade')
    name = fields.Char('Certification Name', required=True)
    issuing_organization = fields.Char('Issuing Organization', required=True)
    issue_date = fields.Date('Issue Date')
    expiry_date = fields.Date('Expiry Date')
    credential_id = fields.Char('Credential ID')
    credential_url = fields.Char('Credential URL')
    is_verified = fields.Boolean('Verified')


class BcmSpecialistService(models.Model):
    _name = 'bcm.specialist.service'
    _description = 'Specialist Service Offering'
    _order = 'sequence, name'
    
    specialist_id = fields.Many2one('bcm.specialist', 'Specialist', required=True, ondelete='cascade')
    name = fields.Char('Service Name', required=True)
    description = fields.Text('Service Description')
    service_type = fields.Selection([
        ('consulting', 'Consulting'),
        ('assessment', 'Risk Assessment'),
        ('planning', 'BCM Planning'),
        ('training', 'Training & Workshop'),
        ('audit', 'Audit & Review'),
        ('implementation', 'Implementation Support'),
        ('crisis_support', 'Crisis Management Support'),
        ('other', 'Other')
    ], string='Service Type', required=True)
    
    pricing_model = fields.Selection([
        ('hourly', 'Hourly Rate'),
        ('fixed', 'Fixed Price'),
        ('retainer', 'Monthly Retainer'),
        ('project', 'Project-Based')
    ], string='Pricing Model', required=True)
    
    base_price = fields.Float('Base Price')
    currency_id = fields.Many2one('res.currency', related='specialist_id.currency_id')
    
    duration_estimate = fields.Float('Estimated Duration (hours)')
    min_engagement = fields.Float('Minimum Engagement (hours)')
    
    delivery_mode = fields.Selection([
        ('remote', 'Remote Only'),
        ('onsite', 'Onsite Only'),
        ('hybrid', 'Hybrid')
    ], string='Delivery Mode', default='hybrid')
    
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)


class BcmSpecialistPortfolio(models.Model):
    _name = 'bcm.specialist.portfolio'
    _description = 'Specialist Portfolio Item'
    _order = 'date desc'
    
    specialist_id = fields.Many2one('bcm.specialist', 'Specialist', required=True, ondelete='cascade')
    name = fields.Char('Project Name', required=True)
    description = fields.Text('Project Description')
    client_industry = fields.Many2one('bcm.industry', 'Client Industry')
    project_type = fields.Selection([
        ('bcm_implementation', 'BCM Program Implementation'),
        ('risk_assessment', 'Risk Assessment'),
        ('bia', 'Business Impact Analysis'),
        ('crisis_management', 'Crisis Management'),
        ('training', 'Training Program'),
        ('audit', 'BCM Audit'),
        ('other', 'Other')
    ], string='Project Type')
    
    date = fields.Date('Completion Date')
    duration = fields.Char('Project Duration')
    team_size = fields.Integer('Team Size')
    role = fields.Char('Your Role')
    
    key_achievements = fields.Text('Key Achievements')
    technologies_used = fields.Text('Technologies/Frameworks Used')
    
    # Attachments for case studies, reports etc.
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    is_featured = fields.Boolean('Featured Project')
    active = fields.Boolean('Active', default=True)