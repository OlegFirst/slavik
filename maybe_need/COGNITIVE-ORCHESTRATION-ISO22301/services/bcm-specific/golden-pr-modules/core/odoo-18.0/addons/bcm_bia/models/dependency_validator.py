# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class BCMBusinessProcessImproved(models.Model):
    """Улучшенная модель бизнес-процессов с проверкой циклических зависимостей"""
    _inherit = 'bcm.business.process'
    
    @api.constrains('dependency_ids')
    def _check_circular_dependencies(self):
        """Проверка на циклические зависимости в процессах"""
        for process in self:
            if process.id in process._get_all_dependencies():
                raise ValidationError(
                    _('Circular dependency detected! Process "%s" cannot depend on itself directly or indirectly.') 
                    % process.name
                )
    
    def _get_all_dependencies(self, visited=None):
        """Рекурсивно получить все зависимости процесса"""
        if visited is None:
            visited = set()
        
        if self.id in visited:
            return visited
        
        visited.add(self.id)
        
        for dep in self.dependency_ids:
            if dep.id not in visited:
                dep._get_all_dependencies(visited)
        
        return visited
    
    @api.model
    def get_dependency_graph(self):
        """Построить граф зависимостей для визуализации"""
        processes = self.search([])
        graph = {
            'nodes': [],
            'edges': []
        }
        
        for process in processes:
            graph['nodes'].append({
                'id': process.id,
                'name': process.name,
                'criticality': process.criticality,
                'rto': process.optimized_rto_hours or 0
            })
            
            for dep in process.dependency_ids:
                graph['edges'].append({
                    'from': process.id,
                    'to': dep.id,
                    'label': 'depends on'
                })
        
        return graph
    
    def calculate_cascade_impact(self):
        """Рассчитать каскадное влияние отказа процесса"""
        self.ensure_one()
        
        # Найти все процессы, зависящие от текущего
        dependent_processes = self.search([
            ('dependency_ids', 'in', self.id)
        ])
        
        total_impact = self.annual_revenue_impact
        affected_users = self.peak_concurrent_users
        affected_staff = self.staff_count
        
        for proc in dependent_processes:
            total_impact += proc.annual_revenue_impact * 0.7  # 70% влияния
            affected_users += proc.peak_concurrent_users
            affected_staff += proc.staff_count
        
        return {
            'direct_impact': self.annual_revenue_impact,
            'cascade_impact': total_impact - self.annual_revenue_impact,
            'total_impact': total_impact,
            'affected_processes': len(dependent_processes),
            'affected_users': affected_users,
            'affected_staff': affected_staff
        }
    
    @api.model
    def validate_all_dependencies(self):
        """Валидация всех зависимостей в системе"""
        processes = self.search([])
        issues = []
        
        for process in processes:
            try:
                process._check_circular_dependencies()
            except ValidationError as e:
                issues.append({
                    'process': process.name,
                    'issue': str(e)
                })
            
            # Проверка на слишком глубокие зависимости
            deps = process._get_all_dependencies()
            if len(deps) > 10:
                issues.append({
                    'process': process.name,
                    'issue': f'Too many dependencies ({len(deps)}). Consider simplifying.'
                })
        
        return issues
