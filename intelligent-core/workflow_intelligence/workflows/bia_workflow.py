"""
BIA Workflow Engine
===================

Extracted from: /Users/MD/AI-Platform-ISO/SESSION_SUMMARY.md
Source lines: 431-823
Date extracted: 2025-10-04

Description:
-----------
Complete BIA (Business Impact Analysis) workflow implementation.
Extends the core State Machine with BIA-specific:
- Workflow stages (identify processes, analyze dependencies, assess impact, determine RTO, review)
- Validators for each stage
- State transitions with conditions
- Public API for BIA operations
- Event publishing for case collection

Dependencies:
- state_machine_extracted.py (StateMachine, ValidationError)
"""

from typing import Dict, Any
from datetime import datetime

# Note: In production, import from state_machine_extracted
# from state_machine_extracted import StateMachine, ValidationError


class BIAStage:
    """BIA workflow stages"""
    NOT_STARTED = "not_started"
    IDENTIFY_PROCESSES = "identify_processes"
    ANALYZE_DEPENDENCIES = "analyze_dependencies"
    ASSESS_IMPACT = "assess_impact"
    DETERMINE_RTO = "determine_rto"
    REVIEW_RESULTS = "review_results"
    COMPLETED = "completed"


class BIAWorkflowEngine:  # StateMachine
    """
    Workflow Engine специально для BIA процесса

    Полная реализация с:
    - Всеми стадиями BIA
    - Валидаторами для каждой стадии
    - Переходами между стадиями
    - Контекстом для AI
    """

    def __init__(self, bia_id: str, org_context: Dict[str, Any]):
        # In production: super().__init__(workflow_id=bia_id, initial_state=BIAStage.NOT_STARTED)

        self.bia_id = bia_id
        self.org_context = org_context
        self._setup_transitions()
        self._setup_requirements()
        self._setup_hooks()

    def _setup_transitions(self):
        """Определить все возможные переходы"""

        # NOT_STARTED → IDENTIFY_PROCESSES
        self.define_transition(
            from_state=BIAStage.NOT_STARTED,
            to_state=BIAStage.IDENTIFY_PROCESSES,
            on_enter=self._on_start_identify_processes
        )

        # IDENTIFY_PROCESSES → ANALYZE_DEPENDENCIES
        self.define_transition(
            from_state=BIAStage.IDENTIFY_PROCESSES,
            to_state=BIAStage.ANALYZE_DEPENDENCIES,
            condition=lambda data: len(data.get('processes', [])) >= 3,
            validators=[self._validate_processes],
            required_data=['processes'],
            on_exit=self._on_exit_identify_processes
        )

        # ANALYZE_DEPENDENCIES → ASSESS_IMPACT
        self.define_transition(
            from_state=BIAStage.ANALYZE_DEPENDENCIES,
            to_state=BIAStage.ASSESS_IMPACT,
            validators=[self._validate_dependencies],
            required_data=['processes', 'dependencies']
        )

        # ASSESS_IMPACT → DETERMINE_RTO
        self.define_transition(
            from_state=BIAStage.ASSESS_IMPACT,
            to_state=BIAStage.DETERMINE_RTO,
            validators=[self._validate_impacts],
            required_data=['processes', 'dependencies', 'impacts']
        )

        # DETERMINE_RTO → REVIEW_RESULTS
        self.define_transition(
            from_state=BIAStage.DETERMINE_RTO,
            to_state=BIAStage.REVIEW_RESULTS,
            validators=[self._validate_rto],
            required_data=['processes', 'dependencies', 'impacts', 'recovery_objectives']
        )

        # REVIEW_RESULTS → COMPLETED (или назад)
        self.define_transition(
            from_state=BIAStage.REVIEW_RESULTS,
            to_state=BIAStage.COMPLETED,
            validators=[self._validate_complete_bia]
        )

        # Можно вернуться назад для корректировок
        self.define_transition(
            from_state=BIAStage.REVIEW_RESULTS,
            to_state=BIAStage.IDENTIFY_PROCESSES
        )

    def _setup_requirements(self):
        """Определить требования для каждой стадии"""

        self.define_state_requirements(
            BIAStage.IDENTIFY_PROCESSES,
            {
                'min_requirements': {'processes': 3},
                'required_fields': ['processes'],
                'validators': [self._validate_process_quality]
            }
        )

        self.define_state_requirements(
            BIAStage.ANALYZE_DEPENDENCIES,
            {
                'min_requirements': {
                    'dependencies': 2  # минимум 2 dependency per process
                },
                'required_fields': ['processes', 'dependencies']
            }
        )

        self.define_state_requirements(
            BIAStage.ASSESS_IMPACT,
            {
                'required_fields': ['processes', 'dependencies', 'impacts'],
                'validators': [self._validate_impact_completeness]
            }
        )

        self.define_state_requirements(
            BIAStage.DETERMINE_RTO,
            {
                'required_fields': ['processes', 'recovery_objectives'],
                'validators': [self._validate_rto_rationale]
            }
        )

    def _setup_hooks(self):
        """Настроить hooks для событий"""

        # Событие при добавлении процесса
        self.on('process_added', self._handle_process_added)

        # Событие при завершении стадии
        self.on('stage_completed', self._handle_stage_completed)

    # ========== VALIDATORS ==========

    def _validate_processes(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Валидировать что процессы правильно описаны"""
        processes = data.get('processes', [])

        if len(processes) < 3:
            return False, "Minimum 3 processes required"

        # Проверить что каждый процесс имеет необходимые поля
        required_fields = ['name', 'description', 'owner', 'tier']
        for proc in processes:
            missing = [f for f in required_fields if f not in proc]
            if missing:
                return False, f"Process '{proc.get('name')}' missing fields: {missing}"

        # Проверить что есть хотя бы один Tier 1 процесс
        tier1_count = len([p for p in processes if p.get('tier') == 'tier_1'])
        if tier1_count == 0:
            return False, "At least one Tier 1 (critical) process required"

        return True, ""

    def _validate_process_quality(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Проверить качество описания процессов"""
        processes = data.get('processes', [])

        for proc in processes:
            # Проверить длину описания
            desc = proc.get('description', '')
            if len(desc) < 20:
                return False, f"Process '{proc['name']}' description too short (min 20 chars)"

            # Проверить что владелец указан
            if not proc.get('owner'):
                return False, f"Process '{proc['name']}' must have an owner"

        return True, ""

    def _validate_dependencies(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Валидировать dependencies"""
        processes = data.get('processes', [])
        dependencies = data.get('dependencies', [])

        # Проверить что критичные процессы имеют dependencies
        tier1_processes = [p for p in processes if p.get('tier') == 'tier_1']

        for proc in tier1_processes:
            proc_deps = [d for d in dependencies if d['process_id'] == proc['id']]
            if len(proc_deps) < 2:
                return False, f"Tier 1 process '{proc['name']}' needs at least 2 dependencies"

        return True, ""

    def _validate_impacts(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Валидировать impact assessments"""
        processes = data.get('processes', [])
        impacts = data.get('impacts', {})

        required_impact_types = ['financial', 'operational', 'reputational', 'regulatory']

        for proc in processes:
            proc_impact = impacts.get(proc['id'], {})

            # Проверить что все типы impact оценены
            missing_types = [t for t in required_impact_types if t not in proc_impact]
            if missing_types:
                return False, f"Process '{proc['name']}' missing impact types: {missing_types}"

            # Проверить что financial impact имеет числовые значения
            financial = proc_impact.get('financial', {})
            if not financial.get('hourly_loss') or not financial.get('daily_loss'):
                return False, f"Process '{proc['name']}' needs financial loss estimates"

        return True, ""

    def _validate_impact_completeness(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Проверить полноту impact analysis"""
        impacts = data.get('impacts', {})
        processes = data.get('processes', [])

        if len(impacts) < len(processes):
            return False, f"Only {len(impacts)}/{len(processes)} processes have impact assessment"

        return True, ""

    def _validate_rto(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Валидировать RTO/RPO/MTPD"""
        processes = data.get('processes', [])
        objectives = data.get('recovery_objectives', {})

        for proc in processes:
            obj = objectives.get(proc['id'], {})

            # Проверить что RTO определён
            if 'rto_hours' not in obj:
                return False, f"Process '{proc['name']}' missing RTO"

            # Проверить разумность RTO для tier
            rto = obj['rto_hours']
            tier = proc['tier']

            if tier == 'tier_1' and rto > 4:
                return False, f"Tier 1 process '{proc['name']}' RTO too high ({rto}h > 4h)"

            if tier == 'tier_2' and rto > 24:
                return False, f"Tier 2 process '{proc['name']}' RTO too high ({rto}h > 24h)"

        return True, ""

    def _validate_rto_rationale(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Проверить что RTO имеет обоснование"""
        objectives = data.get('recovery_objectives', {})

        for proc_id, obj in objectives.items():
            if not obj.get('rationale'):
                return False, f"Process {proc_id} RTO needs rationale"

            # Проверить длину обоснования
            if len(obj['rationale']) < 30:
                return False, f"Process {proc_id} RTO rationale too short"

        return True, ""

    def _validate_complete_bia(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Финальная валидация всего BIA"""

        # Проверить все предыдущие валидаторы
        validators = [
            self._validate_processes,
            self._validate_dependencies,
            self._validate_impacts,
            self._validate_rto
        ]

        for validator in validators:
            is_valid, error = validator(data)
            if not is_valid:
                return False, f"Validation failed: {error}"

        return True, ""

    # ========== HOOKS ==========

    async def _on_start_identify_processes(self, data: Dict[str, Any]):
        """Hook при начале идентификации процессов"""
        # Инициализировать пустые списки
        data['processes'] = []
        data['dependencies'] = []
        data['impacts'] = {}
        data['recovery_objectives'] = {}

        await self.emit('stage_started', {
            'stage': BIAStage.IDENTIFY_PROCESSES,
            'bia_id': self.workflow_id,
            'org_context': self.org_context
        })

    async def _on_exit_identify_processes(self, data: Dict[str, Any]):
        """Hook при завершении идентификации процессов"""
        await self.emit('stage_completed', {
            'stage': BIAStage.IDENTIFY_PROCESSES,
            'bia_id': self.workflow_id,
            'process_count': len(data.get('processes', []))
        })

    async def _handle_process_added(self, event_data: Dict[str, Any]):
        """Обработать добавление процесса"""
        # Проверить можно ли переходить к следующей стадии
        if len(self.current_state.data.get('processes', [])) >= 3:
            # Можно переходить!
            await self.emit('milestone_reached', {
                'milestone': 'minimum_processes',
                'bia_id': self.workflow_id
            })

    async def _handle_stage_completed(self, event_data: Dict[str, Any]):
        """Обработать завершение стадии"""
        # Сохранить в Case Library (будет реализовано дальше)
        pass

    # ========== PUBLIC API ==========

    async def add_process(self, process: Dict[str, Any]):
        """Добавить бизнес-процесс"""
        if self.current_state.name != BIAStage.IDENTIFY_PROCESSES:
            raise ValidationError(
                f"Cannot add processes in stage: {self.current_state.name}"
            )

        processes = self.current_state.data.get('processes', [])

        # Добавить ID если нет
        if 'id' not in process:
            process['id'] = f"proc_{len(processes) + 1}"

        processes.append(process)
        self.update_data({'processes': processes})
        self.add_completed_action(f"added_process_{process['id']}")

        await self.emit('process_added', {
            'bia_id': self.workflow_id,
            'process': process
        })

    async def add_dependency(self, process_id: str, dependency: Dict[str, Any]):
        """Добавить dependency для процесса"""
        if self.current_state.name != BIAStage.ANALYZE_DEPENDENCIES:
            raise ValidationError(
                f"Cannot add dependencies in stage: {self.current_state.name}"
            )

        dependencies = self.current_state.data.get('dependencies', [])
        dependency['process_id'] = process_id
        dependencies.append(dependency)
        self.update_data({'dependencies': dependencies})

        await self.emit('dependency_added', {
            'bia_id': self.workflow_id,
            'process_id': process_id,
            'dependency': dependency
        })

    async def assess_impact(self, process_id: str, impact: Dict[str, Any]):
        """Оценить impact для процесса"""
        if self.current_state.name != BIAStage.ASSESS_IMPACT:
            raise ValidationError(
                f"Cannot assess impact in stage: {self.current_state.name}"
            )

        impacts = self.current_state.data.get('impacts', {})
        impacts[process_id] = impact
        self.update_data({'impacts': impacts})

        await self.emit('impact_assessed', {
            'bia_id': self.workflow_id,
            'process_id': process_id,
            'impact': impact
        })

    async def set_recovery_objective(self, process_id: str, objective: Dict[str, Any]):
        """Установить RTO/RPO/MTPD для процесса"""
        if self.current_state.name != BIAStage.DETERMINE_RTO:
            raise ValidationError(
                f"Cannot set RTO in stage: {self.current_state.name}"
            )

        objectives = self.current_state.data.get('recovery_objectives', {})
        objectives[process_id] = objective
        self.update_data({'recovery_objectives': objectives})

        await self.emit('rto_set', {
            'bia_id': self.workflow_id,
            'process_id': process_id,
            'objective': objective
        })
