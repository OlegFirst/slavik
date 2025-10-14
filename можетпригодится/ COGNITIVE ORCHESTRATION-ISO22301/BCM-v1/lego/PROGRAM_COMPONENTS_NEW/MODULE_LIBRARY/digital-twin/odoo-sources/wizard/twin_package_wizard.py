# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import json


class TwinPackageWizard(models.TransientModel):
    _name = 'bcm.twin.package.wizard'
    _description = 'Digital Twin Package Creation Wizard'

    # Source Configuration
    twin_id = fields.Many2one(
        'bcm.digital.twin.organization',
        string='Digital Twin',
        required=True,
        help="Select the digital twin to create a package from"
    )

    # Package Configuration
    content_type = fields.Selection([
        ('full_twin', 'Complete Digital Twin'),
        ('simulation_data', 'Simulation Results'),
        ('configuration', 'Configuration Data'),
        ('ai_insights', 'AI Analysis Results'),
        ('delta_update', 'Incremental Update'),
        ('backup', 'Backup Data'),
        ('custom', 'Custom Data')
    ], string='Content Type',
       default='full_twin',
       required=True,
       help="Type of data to include in the package")

    compression_type = fields.Selection([
        ('lz4', 'LZ4 (Fast)'),
        ('zstd', 'Zstandard (Balanced)'),
        ('brotli', 'Brotli (High Compression)'),
        ('gzip', 'Gzip (Compatible)'),
        ('zlib', 'Zlib (Standard)'),
        ('none', 'No Compression')
    ], string='Compression Algorithm',
       default='zstd',
       required=True,
       help="Algorithm to use for data compression")

    compression_level = fields.Integer(
        string='Compression Level',
        default=3,
        help="Compression level (1-22 for zstd, 1-9 for others)"
    )

    network_priority = fields.Selection([
        ('low', 'Low Priority'),
        ('normal', 'Normal'),
        ('high', 'High Priority'),
        ('critical', 'Critical')
    ], string='Network Priority',
       default='normal',
       help="Priority for network transport")

    # Advanced Options
    include_simulations = fields.Boolean(
        string='Include Simulation Data',
        default=True,
        help="Include all simulation records and results"
    )

    include_ai_insights = fields.Boolean(
        string='Include AI Insights',
        default=True,
        help="Include AI analysis and prediction data"
    )

    include_configuration = fields.Boolean(
        string='Include Configuration',
        default=True,
        help="Include twin configuration settings"
    )

    include_metadata = fields.Boolean(
        string='Include Metadata',
        default=True,
        help="Include creation dates, users, and other metadata"
    )

    # Custom Data Selection
    custom_data_json = fields.Text(
        string='Custom Data (JSON)',
        help="Custom JSON data to include (only for custom content type)"
    )

    # Validation Options
    auto_validate = fields.Boolean(
        string='Auto Validate Package',
        default=True,
        help="Automatically validate the package after creation"
    )

    auto_optimize = fields.Boolean(
        string='Auto Optimize for Transport',
        default=True,
        help="Automatically optimize the package for network transport"
    )

    # Preview Information
    estimated_size = fields.Text(
        string='Estimated Package Size',
        readonly=True,
        help="Estimated size of the package before compression"
    )

    twin_info = fields.Text(
        string='Twin Information',
        readonly=True,
        help="Information about the selected digital twin"
    )

    @api.onchange('twin_id')
    def _onchange_twin_id(self):
        """Update twin information when twin is selected"""
        if self.twin_id:
            twin = self.twin_id
            info = {
                'name': twin.name,
                'domain_type': twin.domain_type,
                'industry_sector': twin.industry_sector,
                'twin_status': twin.twin_status,
                'simulation_count': twin.simulation_count,
                'twin_health_score': twin.twin_health_score,
                'last_analysis_date': twin.last_analysis_date.strftime('%Y-%m-%d %H:%M:%S') if twin.last_analysis_date else None
            }
            self.twin_info = json.dumps(info, indent=2)

            # Estimate package size
            self._estimate_package_size()

    @api.onchange('content_type', 'include_simulations', 'include_ai_insights', 'include_configuration')
    def _onchange_content_options(self):
        """Update size estimation when content options change"""
        if self.twin_id:
            self._estimate_package_size()

    def _estimate_package_size(self):
        """Estimate the size of the package"""
        if not self.twin_id:
            return

        twin = self.twin_id
        size_estimates = []

        # Base twin data
        base_size = len(str(twin.name or '')) + len(str(twin.description or ''))
        size_estimates.append(f"Base twin data: ~{base_size} bytes")

        # Configuration data
        if self.include_configuration and twin.twin_config:
            config_size = len(twin.twin_config)
            size_estimates.append(f"Configuration: ~{config_size} bytes")

        # Simulation data
        if self.include_simulations:
            sim_size = len(twin.simulation_results or '') + (twin.simulation_count * 100)  # Estimate
            size_estimates.append(f"Simulations: ~{sim_size} bytes")

        # AI insights
        if self.include_ai_insights:
            ai_size = len(twin.ai_insights or '') + len(twin.prediction_models or '')
            size_estimates.append(f"AI insights: ~{ai_size} bytes")

        self.estimated_size = '\n'.join(size_estimates)

    @api.constrains('compression_level')
    def _check_compression_level(self):
        if self.compression_level < 1 or self.compression_level > 22:
            raise ValidationError(_("Compression level must be between 1 and 22"))

    @api.constrains('custom_data_json')
    def _check_custom_data_json(self):
        if self.custom_data_json:
            try:
                json.loads(self.custom_data_json)
            except ValueError:
                raise ValidationError(_("Custom Data must be valid JSON"))

    def action_create_package(self):
        """Create the data package"""
        self.ensure_one()

        if not self.twin_id:
            raise UserError(_("Please select a digital twin"))

        try:
            # Create package record
            package_vals = {
                'content_type': self.content_type,
                'compression_type': self.compression_type,
                'compression_level': self.compression_level,
                'network_priority': self.network_priority,
                'source_twin_id': self.twin_id.id,
            }

            package = self.env['bcm.twin.data.package'].create(package_vals)

            # Create package from twin
            result = package.create_package_from_twin(
                twin_id=self.twin_id.id,
                content_type=self.content_type,
                compression_type=self.compression_type
            )

            # Auto validate if requested
            if self.auto_validate:
                package.validate_integrity()

            # Auto optimize if requested
            if self.auto_optimize:
                package.optimize_for_transport()

            # Return to the created package
            return {
                'type': 'ir.actions.act_window',
                'name': _('Created Package'),
                'res_model': 'bcm.twin.data.package',
                'res_id': package.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'default_source_twin_id': self.twin_id.id,
                }
            }

        except Exception as e:
            raise UserError(_("Failed to create package: %s") % str(e))

    def action_preview_data(self):
        """Preview the data that will be packaged"""
        self.ensure_one()

        if not self.twin_id:
            raise UserError(_("Please select a digital twin"))

        # Get preview data based on content type
        twin = self.twin_id
        preview_data = {}

        if self.content_type == 'full_twin':
            preview_data = {
                'twin_info': {
                    'name': twin.name,
                    'description': twin.description[:200] + '...' if len(twin.description or '') > 200 else twin.description,
                    'domain_type': twin.domain_type,
                    'industry_sector': twin.industry_sector,
                    'twin_status': twin.twin_status
                },
                'include_configuration': self.include_configuration,
                'include_simulations': self.include_simulations,
                'include_ai_insights': self.include_ai_insights,
                'simulation_count': twin.simulation_count,
                'health_score': twin.twin_health_score
            }
        elif self.content_type == 'configuration':
            preview_data = {
                'configuration': json.loads(twin.twin_config)[:100] if twin.twin_config else {},
                'domain_type': twin.domain_type,
                'industry_sector': twin.industry_sector
            }
        elif self.content_type == 'ai_insights':
            preview_data = {
                'ai_insights_available': bool(twin.ai_insights),
                'prediction_models_available': bool(twin.prediction_models),
                'health_score': twin.twin_health_score,
                'last_analysis': twin.last_analysis_date.isoformat() if twin.last_analysis_date else None
            }
        elif self.content_type == 'simulation_data':
            preview_data = {
                'simulation_count': twin.simulation_count,
                'has_results': bool(twin.simulation_results),
                'last_analysis': twin.last_analysis_date.isoformat() if twin.last_analysis_date else None
            }

        # Show preview in a wizard
        preview_wizard = self.env['bcm.twin.package.preview.wizard'].create({
            'preview_data': json.dumps(preview_data, indent=2),
            'content_type': self.content_type,
            'twin_name': twin.name
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Package Preview'),
            'res_model': 'bcm.twin.package.preview.wizard',
            'res_id': preview_wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context
        }


class TwinPackagePreviewWizard(models.TransientModel):
    _name = 'bcm.twin.package.preview.wizard'
    _description = 'Package Preview Wizard'

    twin_name = fields.Char(
        string='Digital Twin',
        readonly=True
    )

    content_type = fields.Char(
        string='Content Type',
        readonly=True
    )

    preview_data = fields.Text(
        string='Preview Data',
        readonly=True,
        help="Preview of data that will be included in the package"
    )

    def action_close(self):
        """Close the preview"""
        return {'type': 'ir.actions.act_window_close'}


class TwinPackageExtractWizard(models.TransientModel):
    _name = 'bcm.twin.package.extract.wizard'
    _description = 'Twin Package Extraction Wizard'

    package_id = fields.Many2one(
        'bcm.twin.data.package',
        string='Package',
        required=True,
        help="Package to extract"
    )

    target_twin_id = fields.Many2one(
        'bcm.digital.twin.organization',
        string='Target Digital Twin',
        required=True,
        help="Digital twin to extract the package to"
    )

    merge_strategy = fields.Selection([
        ('replace', 'Replace Existing Data'),
        ('merge', 'Merge with Existing Data'),
        ('update', 'Update Only Modified Fields')
    ], string='Merge Strategy',
       default='merge',
       required=True,
       help="How to handle existing data in the target twin")

    validate_before_extract = fields.Boolean(
        string='Validate Before Extract',
        default=True,
        help="Validate package integrity before extraction"
    )

    backup_target = fields.Boolean(
        string='Backup Target Twin',
        default=True,
        help="Create a backup of the target twin before extraction"
    )

    package_info = fields.Text(
        string='Package Information',
        readonly=True,
        help="Information about the package"
    )

    target_info = fields.Text(
        string='Target Twin Information',
        readonly=True,
        help="Information about the target twin"
    )

    @api.onchange('package_id')
    def _onchange_package_id(self):
        """Update package information"""
        if self.package_id:
            package = self.package_id
            info = {
                'package_id': package.package_id,
                'content_type': package.content_type,
                'compression_type': package.compression_type,
                'size_compressed': package.size_compressed,
                'validation_status': package.validation_status,
                'created_date': package.created_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.package_info = json.dumps(info, indent=2)

    @api.onchange('target_twin_id')
    def _onchange_target_twin_id(self):
        """Update target twin information"""
        if self.target_twin_id:
            twin = self.target_twin_id
            info = {
                'name': twin.name,
                'domain_type': twin.domain_type,
                'twin_status': twin.twin_status,
                'simulation_count': twin.simulation_count,
                'has_config': bool(twin.twin_config),
                'has_ai_insights': bool(twin.ai_insights)
            }
            self.target_info = json.dumps(info, indent=2)

    def action_extract_package(self):
        """Extract the package to the target twin"""
        self.ensure_one()

        try:
            # Validate package if requested
            if self.validate_before_extract:
                if not self.package_id.validate_integrity():
                    raise UserError(_("Package validation failed. Cannot proceed with extraction."))

            # Create backup if requested
            if self.backup_target:
                backup_package = self.env['bcm.twin.data.package'].create({
                    'content_type': 'backup',
                    'compression_type': 'zstd',
                    'network_priority': 'low',
                    'source_twin_id': self.target_twin_id.id,
                })
                backup_package.create_package_from_twin(
                    twin_id=self.target_twin_id.id,
                    content_type='full_twin'
                )

            # Extract package
            result = self.package_id.extract_to_twin(
                twin_id=self.target_twin_id.id,
                merge_strategy=self.merge_strategy
            )

            if result.get('success'):
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Extraction Successful"),
                        'message': _("Package extracted to '%s' successfully") % self.target_twin_id.name,
                        'type': 'success'
                    }
                }
            else:
                raise UserError(_("Extraction failed"))

        except Exception as e:
            raise UserError(_("Failed to extract package: %s") % str(e))

    def action_cancel(self):
        """Cancel extraction"""
        return {'type': 'ir.actions.act_window_close'}