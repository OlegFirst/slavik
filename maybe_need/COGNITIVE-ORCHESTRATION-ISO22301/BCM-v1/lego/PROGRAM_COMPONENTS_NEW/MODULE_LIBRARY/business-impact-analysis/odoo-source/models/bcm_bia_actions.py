# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class BCMBusinessImpactAnalysis(models.Model):
    _name = 'bcm.bia'
    _description = 'Business Impact Analysis with Actions'
    
    # Computed RTO/RPO/MTPD fields
    computed_rto = fields.Float('Computed RTO (hours)', readonly=True)
    computed_rpo = fields.Float('Computed RPO (hours)', readonly=True)
    computed_mtpd = fields.Float('Computed MTPD (hours)', readonly=True)
    
    def action_compute_bia(self):
        """Compute BIA using BIA Engine service"""
        self.ensure_one()
        
        try:
            config = self.env['bcm.config'].get_config()
            bia_engine_url = config.bia_engine_url
            
            if not bia_engine_url:
                raise UserError(_("BIA Engine URL not configured"))
            
            # Prepare data for BIA Engine
            processes = []
            for process in self.process_ids:
                processes.append({
                    'id': process.id,
                    'name': process.name,
                    'criticality': process.criticality or 'medium',
                    'dependencies': [dep.name for dep in process.dependency_ids],
                    'resources': process.resource_count or 0,
                })
            
            payload = {
                'tenant_id': self.company_id.id,
                'bia_id': self.id,
                'processes': processes,
                'analysis_type': 'full'
            }
            
            # Call BIA Engine
            response = requests.post(
                f'{bia_engine_url}/api/bia/compute',
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Update BIA with computed values
                self.write({
                    'computed_rto': result.get('rto', 0),
                    'computed_rpo': result.get('rpo', 0),
                    'computed_mtpd': result.get('mtpd', 0),
                    'state': 'completed'
                })
                
                # Send event to EventBus
                self.send_event_to_eventbus('bcm.bia.completed', {
                    'bia_id': self.id,
                    'rto': result.get('rto', 0),
                    'rpo': result.get('rpo', 0),
                    'mtpd': result.get('mtpd', 0),
                    'critical_processes': result.get('critical_processes', [])
                })
                
                # Show notification
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('BIA Computed Successfully'),
                        'message': _(f'RTO: {self.computed_rto}h, RPO: {self.computed_rpo}h, MTPD: {self.computed_mtpd}h'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_(f"BIA Engine error: {response.text}"))
                
        except requests.exceptions.RequestException as e:
            raise UserError(_(f"Failed to connect to BIA Engine: {str(e)}"))
        except Exception as e:
            raise UserError(_(f"Error computing BIA: {str(e)}"))
