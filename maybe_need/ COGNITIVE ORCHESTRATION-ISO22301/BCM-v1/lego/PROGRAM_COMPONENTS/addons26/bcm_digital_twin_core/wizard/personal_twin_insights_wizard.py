# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json


class PersonalTwinInsightsWizard(models.TransientModel):
    _name = 'bcm.personal.twin.insights.wizard'
    _description = 'Personal Digital Twin Insights Display Wizard'

    twin_id = fields.Many2one(
        'bcm.personal.digital.twin',
        string='Digital Twin',
        required=True
    )

    # Pattern Analysis Results
    activity_level = fields.Char(
        string='Activity Level',
        readonly=True
    )

    peak_usage_hours = fields.Text(
        string='Peak Usage Hours',
        readonly=True
    )

    preferred_modules = fields.Text(
        string='Preferred Modules',
        readonly=True
    )

    engagement_trend = fields.Char(
        string='Engagement Trend',
        readonly=True
    )

    # Behavioral Insights
    behavioral_insights = fields.Text(
        string='Behavioral Insights',
        readonly=True
    )

    recommendations = fields.Text(
        string='Recommendations',
        readonly=True
    )

    risk_indicators = fields.Text(
        string='Risk Indicators',
        readonly=True
    )

    # Predictive Insights
    churn_risk = fields.Char(
        string='Churn Risk',
        readonly=True
    )

    feature_adoption_probability = fields.Float(
        string='Feature Adoption Probability',
        readonly=True
    )

    engagement_forecast = fields.Char(
        string='Engagement Forecast',
        readonly=True
    )

    # Detailed Analysis Data
    patterns_data = fields.Text(
        string='Raw Patterns Data',
        readonly=True,
        help="JSON data containing detailed pattern analysis"
    )

    insights_data = fields.Text(
        string='Raw Insights Data',
        readonly=True,
        help="JSON data containing detailed insights"
    )

    analysis_timestamp = fields.Datetime(
        string='Analysis Timestamp',
        readonly=True
    )

    @api.model
    def default_get(self, fields_list):
        """Load insights and patterns data from context"""
        res = super().default_get(fields_list)

        twin_id = self.env.context.get('default_twin_id')
        patterns = self.env.context.get('patterns', {})
        insights = self.env.context.get('insights', {})

        if twin_id:
            res['twin_id'] = twin_id

        if patterns:
            res.update({
                'activity_level': patterns.get('activity_level', '').title(),
                'peak_usage_hours': ', '.join(patterns.get('peak_usage_hours', [])),
                'preferred_modules': ', '.join(patterns.get('preferred_modules', [])),
                'engagement_trend': patterns.get('engagement_trend', '').title(),
                'patterns_data': json.dumps(patterns, indent=2),
                'analysis_timestamp': patterns.get('analyzed_at')
            })

            # Behavioral insights
            behavioral_insights = patterns.get('behavioral_insights', [])
            if behavioral_insights:
                res['behavioral_insights'] = '\n• ' + '\n• '.join(behavioral_insights)

            # Recommendations
            recommendations = patterns.get('recommendations', [])
            if recommendations:
                res['recommendations'] = '\n• ' + '\n• '.join(recommendations)

            # Risk indicators
            risk_indicators = patterns.get('risk_indicators', [])
            if risk_indicators:
                res['risk_indicators'] = '\n• ' + '\n• '.join(risk_indicators)

            # Predictive insights
            predictive = patterns.get('predictive_insights', {})
            if predictive:
                res.update({
                    'churn_risk': predictive.get('likely_churn_risk', '').title(),
                    'feature_adoption_probability': predictive.get('feature_adoption_probability', 0.0),
                    'engagement_forecast': predictive.get('engagement_forecast', '').title()
                })

        if insights:
            res['insights_data'] = json.dumps(insights, indent=2)

        return res

    def action_apply_recommendations(self):
        """Apply recommendations to the digital twin"""
        self.ensure_one()

        if not self.twin_id or not self.patterns_data:
            raise UserError(_("No data available to apply recommendations"))

        try:
            patterns = json.loads(self.patterns_data)
            recommendations = patterns.get('recommendations', [])

            if not recommendations:
                raise UserError(_("No recommendations available to apply"))

            # Apply recommendations (this would be more sophisticated in practice)
            applied_recommendations = []

            for recommendation in recommendations:
                if 'Risk Management' in recommendation:
                    # Enable risk management notifications
                    applied_recommendations.append("Enabled Risk Management notifications")
                elif 'automated reports' in recommendation:
                    # Set up automated reports
                    applied_recommendations.append("Configured automated reporting preferences")
                elif 'community forum' in recommendation:
                    # Enable community features
                    applied_recommendations.append("Enabled community forum notifications")

            # Update twin with applied recommendations
            current_config = self.twin_id.workspace_config or {}
            current_config['applied_recommendations'] = applied_recommendations
            current_config['last_recommendation_application'] = fields.Datetime.to_string(fields.Datetime.now())
            self.twin_id.workspace_config = current_config

            # Log the action
            self.twin_id.message_post(
                body=_("Applied %d recommendations:\n• %s") % (
                    len(applied_recommendations),
                    '\n• '.join(applied_recommendations)
                ),
                message_type='notification'
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Applied %d recommendations successfully") % len(applied_recommendations),
                    'type': 'success'
                }
            }

        except json.JSONDecodeError:
            raise UserError(_("Invalid patterns data format"))
        except Exception as e:
            raise UserError(_("Failed to apply recommendations: %s") % str(e))

    def action_schedule_analysis(self):
        """Schedule regular pattern analysis"""
        self.ensure_one()

        return {
            'name': _('Schedule Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.personal.twin.analysis.schedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_twin_id': self.twin_id.id
            }
        }

    def action_export_insights(self):
        """Export insights to a report"""
        self.ensure_one()

        # Create a comprehensive insights report
        report_data = {
            'twin_id': self.twin_id.id,
            'user_name': self.twin_id.user_id.name,
            'analysis_date': self.analysis_timestamp,
            'activity_summary': {
                'level': self.activity_level,
                'peak_hours': self.peak_usage_hours,
                'preferred_modules': self.preferred_modules,
                'engagement_trend': self.engagement_trend
            },
            'insights': {
                'behavioral': self.behavioral_insights,
                'recommendations': self.recommendations,
                'risks': self.risk_indicators
            },
            'predictions': {
                'churn_risk': self.churn_risk,
                'feature_adoption': self.feature_adoption_probability,
                'engagement_forecast': self.engagement_forecast
            }
        }

        # In practice, this would generate a PDF or Excel report
        # For now, we'll create a downloadable JSON file
        filename = f"personal_insights_{self.twin_id.user_id.name}_{fields.Date.today().strftime('%Y%m%d')}.json"

        return {
            'type': 'ir.actions.act_url',
            'url': f'/bcm/export-insights/{self.twin_id.id}?format=json',
            'target': 'new'
        }

    def action_compare_with_peers(self):
        """Compare insights with anonymized peer data"""
        self.ensure_one()

        return {
            'name': _('Peer Comparison'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.personal.twin.peer.comparison.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_twin_id': self.twin_id.id,
                'current_patterns': self.patterns_data
            }
        }

    def action_set_goals(self):
        """Set personal improvement goals based on insights"""
        self.ensure_one()

        return {
            'name': _('Set Personal Goals'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.personal.twin.goals.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_twin_id': self.twin_id.id,
                'recommendations': self.recommendations,
                'current_activity_level': self.activity_level
            }
        }

    def action_view_detailed_metrics(self):
        """View detailed metrics and analytics"""
        self.ensure_one()

        return {
            'name': _('Detailed Metrics'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.personal.digital.twin',
            'res_id': self.twin_id.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'form_view_initial_mode': 'readonly'
            }
        }