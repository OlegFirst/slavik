# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import json

class BcmKpiCategory(models.Model):
    """KPI Categories for organization"""
    _name = 'bcm.kpi.category'
    _description = 'BCM KPI Category'
    _order = 'sequence, name'

    name = fields.Char(
        string='Category Name',
        required=True, index=True,
        help='Name of the KPI category'
    )
    sequence = fields.Integer(string='Sequence', default=10)
    
    description = fields.Text(
        string='Description',
        help='Description of the KPI category'
    )
    
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color for visualization'
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company
    )
    
    active = fields.Boolean(default=True)

class BcmKpi(models.Model):
    """BCM Key Performance Indicators"""
    _name = 'bcm.kpi'
    _description = 'BCM KPI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'category_id, sequence, name'

    name = fields.Char(
        string='KPI Name',
        required=True, index=True,
        tracking=True,
        help='Name of the KPI'
    )
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    category_id = fields.Many2one(
        'bcm.kpi.category',
        string='Category',
        required=True, index=True,
        help='KPI category'
    )
    
    # KPI Definition
    description = fields.Html(
        string='Description',
        help='Detailed description of the KPI'
    )
    
    objective = fields.Text(
        string='Objective',
        help='What this KPI measures and why'
    )
    
    # Measurement Details
    measurement_unit = fields.Char(
        string='Unit of Measurement',
        required=True, index=True,
        help='Unit (%, hours, count, etc.)'
    )
    
    calculation_method = fields.Html(
        string='Calculation Method',
        help='How this KPI is calculated'
    )
    
    data_source = fields.Char(
        string='Data Source',
        help='Where the data comes from'
    )
    
    # Targets and Thresholds
    target_value = fields.Float(
        string='Target Value',
        help='Target value for this KPI'
    )
    
    critical_threshold = fields.Float(
        string='Critical Threshold',
        help='Value below which performance is critical'
    )
    
    warning_threshold = fields.Float(
        string='Warning Threshold',
        help='Value below which performance needs attention'
    )
    
    # Performance Direction
    performance_direction = fields.Selection([
        ('higher_better', 'Higher is Better'),
        ('lower_better', 'Lower is Better'),
        ('target_value', 'Closest to Target is Better')
    ], string='Performance Direction', required=True, default='higher_better')
    
    # Frequency and Timing
    measurement_frequency = fields.Selection([
        ('real_time', 'Real-time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually')
    ], string='Measurement Frequency', required=True, default='monthly')
    
    # Responsible Parties
    owner_id = fields.Many2one(
        'res.users',
        string='KPI Owner',
        required=True, index=True,
        tracking=True,
        help='Person responsible for this KPI'
    )
    
    department_id = fields.Many2one(
        'hr.department',
        string='Responsible Department'
    )
    
    # Status
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('under_review', 'Under Review')
    ], string='Status', default='active', required=True, tracking=True)
    
    # Current Performance
    current_value = fields.Float(
        string='Current Value',
        compute='_compute_current_performance',
        store=True,
        help='Latest measured value'
    )
    
    current_status = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('no_data', 'No Data')
    ], string='Current Status', compute='_compute_current_performance', store=True)
    
    trend = fields.Selection([
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
        ('no_data', 'No Data')
    ], string='Trend', compute='_compute_trend', store=True)
    
    # Related Records
    measurement_ids = fields.One2many(
        'bcm.kpi.measurement',
        'kpi_id',
        string='Measurements'
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company
    )
    
    active = fields.Boolean(default=True, tracking=True)
    
    @api.depends('measurement_ids.value')
    def _compute_current_performance(self):
        """Compute current value and status based on latest measurement"""
        for record in self:
            latest_measurement = record.measurement_ids.sorted('measurement_date', reverse=True)[:1]
            
            if latest_measurement:
                record.current_value = latest_measurement.value
                
                # Determine status based on thresholds
                if record.performance_direction == 'higher_better':
                    if latest_measurement.value >= record.target_value:
                        record.current_status = 'excellent'
                    elif latest_measurement.value >= record.warning_threshold:
                        record.current_status = 'good'
                    elif latest_measurement.value >= record.critical_threshold:
                        record.current_status = 'warning'
                    else:
                        record.current_status = 'critical'
                        
                elif record.performance_direction == 'lower_better':
                    if latest_measurement.value <= record.target_value:
                        record.current_status = 'excellent'
                    elif latest_measurement.value <= record.warning_threshold:
                        record.current_status = 'good'
                    elif latest_measurement.value <= record.critical_threshold:
                        record.current_status = 'warning'
                    else:
                        record.current_status = 'critical'
                        
                else:  # target_value
                    deviation = abs(latest_measurement.value - record.target_value)
                    if deviation <= (record.target_value * 0.05):  # Within 5%
                        record.current_status = 'excellent'
                    elif deviation <= (record.target_value * 0.10):  # Within 10%
                        record.current_status = 'good'
                    elif deviation <= (record.target_value * 0.20):  # Within 20%
                        record.current_status = 'warning'
                    else:
                        record.current_status = 'critical'
            else:
                record.current_value = 0
                record.current_status = 'no_data'
    
    @api.depends('measurement_ids.value')
    def _compute_trend(self):
        """Compute trend based on last few measurements"""
        for record in self:
            measurements = record.measurement_ids.sorted('measurement_date', reverse=True)[:3]
            
            if len(measurements) >= 2:
                recent_avg = sum(measurements[:2].mapped('value')) / 2
                older_avg = sum(measurements[1:].mapped('value')) / len(measurements[1:])
                
                diff_pct = (recent_avg - older_avg) / older_avg * 100 if older_avg else 0
                
                if record.performance_direction == 'lower_better':
                    diff_pct = -diff_pct  # Invert for lower_better KPIs
                
                if diff_pct > 5:
                    record.trend = 'improving'
                elif diff_pct < -5:
                    record.trend = 'declining'
                else:
                    record.trend = 'stable'
            else:
                record.trend = 'no_data'

class BcmKpiMeasurement(models.Model):
    """KPI Measurements/Data Points"""
    _name = 'bcm.kpi.measurement'
    _description = 'BCM KPI Measurement'
    _order = 'measurement_date desc'

    kpi_id = fields.Many2one(
        'bcm.kpi',
        string='KPI',
        required=True, index=True,
        ondelete='cascade'
    )
    
    measurement_date = fields.Date(
        string='Measurement Date',
        required=True, index=True,
        default=fields.Date.today
    )
    
    value = fields.Float(
        string='Value',
        required=True, index=True,
        help='Measured value'
    )
    
    # Additional Context
    notes = fields.Text(
        string='Notes',
        help='Additional context or notes about this measurement'
    )
    
    data_quality = fields.Selection([
        ('high', 'High Quality'),
        ('medium', 'Medium Quality'), 
        ('low', 'Low Quality'),
        ('estimated', 'Estimated')
    ], string='Data Quality', default='high')
    
    # Data Collection
    collected_by = fields.Many2one(
        'res.users',
        string='Collected By',
        default=lambda self: self.env.user
    )
    
    collection_method = fields.Selection([
        ('manual', 'Manual Entry'),
        ('automated', 'Automated System'),
        ('import', 'Data Import'),
        ('calculation', 'Calculated')
    ], string='Collection Method', default='manual')
    
    # Verification
    verified = fields.Boolean(
        string='Verified',
        default=False,
        help='Has this measurement been verified?'
    )
    
    verified_by = fields.Many2one(
        'res.users',
        string='Verified By'
    )
    
    verification_date = fields.Date(string='Verification Date')
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        related='kpi_id.company_id',
        store=True
    )
    
    def action_verify(self):
        """Mark measurement as verified"""
        self.write({
            'verified': True,
            'verified_by': self.env.user.id,
            'verification_date': fields.Date.today()
        })

class BcmKpiDashboard(models.Model):
    """KPI Dashboards for different audiences"""
    _name = 'bcm.kpi.dashboard'
    _description = 'BCM KPI Dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(
        string='Dashboard Name',
        required=True, index=True,
        tracking=True
    )
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    description = fields.Text(
        string='Description',
        help='Purpose and audience of this dashboard'
    )
    
    # Dashboard Configuration
    dashboard_type = fields.Selection([
        ('executive', 'Executive Dashboard'),
        ('operational', 'Operational Dashboard'),
        ('tactical', 'Tactical Dashboard'),
        ('compliance', 'Compliance Dashboard'),
        ('custom', 'Custom Dashboard')
    ], string='Dashboard Type', required=True)
    
    # Audience
    target_audience = fields.Selection([
        ('executives', 'Executive Management'),
        ('bcm_team', 'BCM Team'),
        ('department_heads', 'Department Heads'),
        ('all_staff', 'All Staff'),
        ('external', 'External Stakeholders')
    ], string='Target Audience', required=True)
    
    # KPIs in Dashboard
    kpi_ids = fields.Many2many(
        'bcm.kpi',
        string='KPIs'
    )
    
    # Layout and Display
    layout_config = fields.Text(
        string='Layout Configuration',
        help='JSON configuration for dashboard layout'
    )
    
    refresh_frequency = fields.Selection([
        ('real_time', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly')
    ], string='Refresh Frequency', default='daily')
    
    # Access Control
    user_ids = fields.Many2many(
        'res.users',
        string='Authorized Users'
    )
    
    group_ids = fields.Many2many(
        'res.groups',
        string='Authorized Groups'
    )
    
    public_access = fields.Boolean(
        string='Public Access',
        default=False,
        help='Allow access without authentication'
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company
    )
    
    active = fields.Boolean(default=True, tracking=True)

class BcmKpiReport(models.Model):
    """KPI Reports and Analysis"""
    _name = 'bcm.kpi.report'
    _description = 'BCM KPI Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'report_date desc'

    name = fields.Char(
        string='Report Name',
        required=True, index=True,
        tracking=True
    )
    
    report_type = fields.Selection([
        ('performance_summary', 'Performance Summary'),
        ('trend_analysis', 'Trend Analysis'),
        ('benchmark_comparison', 'Benchmark Comparison'),
        ('exception_report', 'Exception Report'),
        ('compliance_report', 'Compliance Report')
    ], string='Report Type', required=True)
    
    report_date = fields.Date(
        string='Report Date',
        required=True, index=True,
        default=fields.Date.today
    )
    
    # Report Scope
    period_from = fields.Date(string='Period From', required=True)
    period_to = fields.Date(string='Period To', required=True)
    
    kpi_ids = fields.Many2many(
        'bcm.kpi',
        string='KPIs Included'
    )
    
    category_ids = fields.Many2many(
        'bcm.kpi.category',
        string='Categories Included'
    )
    
    # Report Content
    executive_summary = fields.Html(
        string='Executive Summary',
        help='High-level summary of key findings'
    )
    
    key_findings = fields.Html(
        string='Key Findings',
        help='Detailed findings and insights'
    )
    
    recommendations = fields.Html(
        string='Recommendations',
        help='Recommended actions based on analysis'
    )
    
    # Report Generation
    generated_by = fields.Many2one(
        'res.users',
        string='Generated By',
        default=lambda self: self.env.user
    )
    
    generation_method = fields.Selection([
        ('manual', 'Manual'),
        ('scheduled', 'Scheduled'),
        ('automated', 'Automated')
    ], string='Generation Method', default='manual')
    
    # Distribution
    distribution_list = fields.Many2many(
        'res.users',
        string='Distribution List'
    )
    
    sent_date = fields.Datetime(string='Sent Date')
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company
    )
    
    active = fields.Boolean(default=True, tracking=True)
    
    def action_generate_report(self):
        """Generate the report content"""
        # This would contain logic to analyze KPI data and generate insights
        self.message_post(
            body=_('Report generated on %s') % fields.Datetime.now()
        )
    
    def action_send_report(self):
        """Send report to distribution list"""
        self.write({'sent_date': fields.Datetime.now()})
        self.message_post(
            body=_('Report sent to distribution list on %s') % fields.Datetime.now()
        )
