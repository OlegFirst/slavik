# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ContentGamificationBridge(models.Model):
    """Bridge between BCM content and Odoo gamification"""
    _name = 'bcm.content.gamification.bridge'
    _description = 'BCM Content Gamification Bridge'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Achievement Name', required=True)
    active = fields.Boolean(default=True)

    # Content links
    template_id = fields.Many2one('bcm.template', 'Template')
    scenario_id = fields.Many2one('bcm.scenario', 'Scenario')

    # Gamification integration
    challenge_id = fields.Many2one('gamification.challenge', 'Challenge')
    badge_id = fields.Many2one('gamification.badge', 'Badge')

    # Points system
    points_for_creation = fields.Integer('Points for Creating Content', default=50)
    points_for_review = fields.Integer('Points for Reviewing', default=10)
    points_for_usage = fields.Integer('Points for Using', default=5)
    points_for_rating = fields.Integer('Points for Rating', default=3)

    # Achievements
    achievement_type = fields.Selection([
        ('content_creator', 'Content Creator'),
        ('template_master', 'Template Master'),
        ('scenario_expert', 'Scenario Expert'),
        ('quality_reviewer', 'Quality Reviewer'),
        ('power_user', 'Power User'),
        ('mentor', 'Mentor'),
    ], string='Achievement Type')

    # Tracking
    user_achievements = fields.One2many('bcm.user.achievement', 'bridge_id', 'User Achievements')

    @api.model
    def award_points(self, user_id, action_type, content_type, content_id):
        """Award points for content actions"""
        points = 0
        if action_type == 'create':
            points = self.points_for_creation
        elif action_type == 'review':
            points = self.points_for_review
        elif action_type == 'use':
            points = self.points_for_usage
        elif action_type == 'rate':
            points = self.points_for_rating

        # Create achievement record
        self.env['bcm.user.achievement'].create({
            'user_id': user_id,
            'bridge_id': self.id,
            'points': points,
            'action_type': action_type,
            'content_type': content_type,
            'content_ref': f'{content_type},{content_id}'
        })

        return points


class UserAchievement(models.Model):
    """Track user achievements in content creation"""
    _name = 'bcm.user.achievement'
    _description = 'User Content Achievement'
    _order = 'create_date desc'

    user_id = fields.Many2one('res.users', 'User', required=True)
    bridge_id = fields.Many2one('bcm.content.gamification.bridge', 'Bridge')
    points = fields.Integer('Points Earned')
    action_type = fields.Selection([
        ('create', 'Created'),
        ('review', 'Reviewed'),
        ('use', 'Used'),
        ('rate', 'Rated'),
        ('complete', 'Completed'),
    ], string='Action')
    content_type = fields.Char('Content Type')
    content_ref = fields.Reference(
        selection=[
            ('bcm.template', 'Template'),
            ('bcm.scenario', 'Scenario'),
            ('slide.channel', 'Course'),
            ('calendar.event', 'Event'),
        ],
        string='Content'
    )
    badge_ids = fields.Many2many('gamification.badge', string='Badges Earned')

    # Leaderboard position
    weekly_rank = fields.Integer('Weekly Rank', compute='_compute_ranks')
    monthly_rank = fields.Integer('Monthly Rank', compute='_compute_ranks')
    total_points = fields.Integer('Total Points', compute='_compute_total_points')

    @api.depends('user_id', 'points')
    def _compute_total_points(self):
        for record in self:
            record.total_points = self.search_count([
                ('user_id', '=', record.user_id.id)
            ])

    @api.depends('user_id', 'points')
    def _compute_ranks(self):
        # Calculate weekly and monthly rankings
        for record in self:
            # Simplified ranking logic
            record.weekly_rank = 1
            record.monthly_rank = 1


class ContentLearningBridge(models.Model):
    """Bridge between BCM content and e-learning slides"""
    _name = 'bcm.content.learning.bridge'
    _description = 'BCM Content E-Learning Bridge'

    name = fields.Char('Course Name', required=True)
    active = fields.Boolean(default=True)

    # Content sources
    template_ids = fields.Many2many('bcm.template', string='Templates')
    scenario_ids = fields.Many2many('bcm.scenario', string='Scenarios')

    # E-learning integration
    slide_channel_id = fields.Many2one('slide.channel', 'Course Channel')

    # Learning path
    learning_path_type = fields.Selection([
        ('beginner', 'BCM Fundamentals'),
        ('intermediate', 'BCM Practitioner'),
        ('advanced', 'BCM Expert'),
        ('specialized', 'Industry Specific'),
    ], string='Learning Path')

    # Auto-generation settings
    auto_generate_slides = fields.Boolean('Auto Generate Slides', default=True)
    auto_generate_quiz = fields.Boolean('Auto Generate Quiz', default=True)
    quiz_pass_score = fields.Float('Quiz Pass Score %', default=70.0)

    @api.model
    def convert_template_to_slide(self, template_id):
        """Convert a template to e-learning slide"""
        template = self.env['bcm.template'].browse(template_id)
        if not template:
            return False

        slide_vals = {
            'name': template.name,
            'channel_id': self.slide_channel_id.id,
            'slide_type': 'document',
            'is_published': True,
            'completion_time': 5.0,  # minutes
            'description': template.description,
        }

        return self.env['slide.slide'].create(slide_vals)

    @api.model
    def create_scenario_exercise(self, scenario_id):
        """Create interactive exercise from scenario"""
        scenario = self.env['bcm.scenario'].browse(scenario_id)
        if not scenario:
            return False

        # Create practical exercise slide
        slide_vals = {
            'name': f'Exercise: {scenario.name}',
            'channel_id': self.slide_channel_id.id,
            'slide_type': 'quiz',
            'is_published': True,
            'question_ids': [(0, 0, {
                'question': f'How would you respond to: {scenario.description}',
                'sequence': 1,
            })]
        }

        return self.env['slide.slide'].create(slide_vals)


class ContentCalendarBridge(models.Model):
    """Bridge between BCM content and calendar events"""
    _name = 'bcm.content.calendar.bridge'
    _description = 'BCM Content Calendar Bridge'

    name = fields.Char('Event Series Name', required=True)
    active = fields.Boolean(default=True)

    # Content scheduling
    template_review_schedule = fields.Selection([
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ], string='Template Review Schedule', default='monthly')

    scenario_exercise_schedule = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('biannual', 'Twice a Year'),
        ('annual', 'Annual'),
    ], string='Scenario Exercise Schedule', default='quarterly')

    # Calendar integration
    calendar_event_ids = fields.One2many('calendar.event', 'bcm_bridge_id', 'Events')

    # Auto-scheduling
    auto_schedule_reviews = fields.Boolean('Auto Schedule Reviews', default=True)
    auto_schedule_training = fields.Boolean('Auto Schedule Training', default=True)
    auto_schedule_exercises = fields.Boolean('Auto Schedule Exercises', default=True)

    @api.model
    def schedule_template_review(self, template_id, reviewer_ids):
        """Schedule template review event"""
        template = self.env['bcm.template'].browse(template_id)
        if not template:
            return False

        event_vals = {
            'name': f'Review: {template.name}',
            'start': fields.Datetime.now(),
            'stop': fields.Datetime.now(),
            'duration': 1.0,
            'partner_ids': [(6, 0, reviewer_ids)],
            'bcm_bridge_id': self.id,
            'bcm_content_type': 'template_review',
            'bcm_content_id': template_id,
        }

        return self.env['calendar.event'].create(event_vals)

    @api.model
    def schedule_scenario_exercise(self, scenario_id, participant_ids):
        """Schedule scenario exercise event"""
        scenario = self.env['bcm.scenario'].browse(scenario_id)
        if not scenario:
            return False

        event_vals = {
            'name': f'Exercise: {scenario.name}',
            'start': fields.Datetime.now(),
            'stop': fields.Datetime.now(),
            'duration': 2.0,
            'partner_ids': [(6, 0, participant_ids)],
            'bcm_bridge_id': self.id,
            'bcm_content_type': 'scenario_exercise',
            'bcm_content_id': scenario_id,
        }

        return self.env['calendar.event'].create(event_vals)


class CalendarEvent(models.Model):
    """Extend calendar event for BCM content"""
    _inherit = 'calendar.event'

    bcm_bridge_id = fields.Many2one('bcm.content.calendar.bridge', 'BCM Bridge')
    bcm_content_type = fields.Selection([
        ('template_review', 'Template Review'),
        ('scenario_exercise', 'Scenario Exercise'),
        ('training_session', 'Training Session'),
        ('assessment', 'Assessment'),
    ], string='BCM Content Type')
    bcm_content_id = fields.Integer('Content ID')

    # Completion tracking
    completion_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending')

    completion_score = fields.Float('Completion Score')