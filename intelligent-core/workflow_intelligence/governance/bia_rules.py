# workflow_intelligence/governance/bia_rules.py

from .rules_engine import Rule, RuleCategory, RuleSeverity
from typing import Dict, Any

class BIARules:
    """
    Governance rules специфичные для BIA
    
    Три уровня:
    1. Constitution - неизменяемые принципы
    2. Mandatory - обязательные требования
    3. Best Practice - рекомендации
    """
    
    @staticmethod
    def get_all_rules() -> list[Rule]:
        """Получить все BIA rules"""
        return [
            # ========== CONSTITUTION (Неизменяемые принципы) ==========
            
            Rule(
                rule_id="bia_const_001",
                name="No RTO < 1 hour without justification",
                description="Tier 1 processes cannot have RTO < 1 hour unless explicitly justified",
                category=RuleCategory.CONSTITUTION,
                severity=RuleSeverity.CRITICAL,
                validation_fn=BIARules._validate_minimum_rto,
                applies_to_stages=["determine_rto", "review_results"]
            ),
            
            Rule(
                rule_id="bia_const_002",
                name="Financial impact required",
                description="All processes must have quantified financial impact",
                category=RuleCategory.CONSTITUTION,
                severity=RuleSeverity.CRITICAL,
                validation_fn=BIARules._validate_financial_impact_exists,
                applies_to_stages=["assess_impact", "review_results"]
            ),
            
            Rule(
                rule_id="bia_const_003",
                name="Tier 1 dependency mapping mandatory",
                description="Tier 1 processes must have complete dependency mapping",
                category=RuleCategory.CONSTITUTION,
                severity=RuleSeverity.CRITICAL,
                validation_fn=BIARules._validate_tier1_dependencies,
                applies_to_stages=["analyze_dependencies", "review_results"]
            ),
            
            # ========== MANDATORY (Обязательные требования) ==========
            
            Rule(
                rule_id="bia_mand_001",
                name="Minimum 3 processes",
                description="BIA must analyze at least 3 business processes",
                category=RuleCategory.MANDATORY,
                severity=RuleSeverity.HIGH,
                validation_fn=BIARules._validate_minimum_processes,
                applies_to_stages=["identify_processes", "analyze_dependencies"]
            ),
            
            Rule(
                rule_id="bia_mand_002",
                name="At least one Tier 1 process",
                description="BIA must identify at least one critical (Tier 1) process",
                category=RuleCategory.MANDATORY,
                severity=RuleSeverity.HIGH,
                validation_fn=BIARules._validate_has_tier1,
                applies_to_stages=["identify_processes", "analyze_dependencies"]
            ),
            
            Rule(
                rule_id="bia_mand_003",
                name="All impact types assessed",
                description="Each process must have financial, operational, reputational, and regulatory impact assessed",
                category=RuleCategory.MANDATORY,
                severity=RuleSeverity.HIGH,
                validation_fn=BIARules._validate_all_impact_types,
                applies_to_stages=["assess_impact", "review_results"]
            ),
            
            Rule(
                rule_id="bia_mand_004",
                name="RTO rationale required",
                description="All RTO determinations must include rationale",
                category=RuleCategory.MANDATORY,
                severity=RuleSeverity.HIGH,
                validation_fn=BIARules._validate_rto_rationale,
                applies_to_stages=["determine_rto", "review_results"]
            ),
            
            # ========== BEST PRACTICE (Рекомендации) ==========
            
            Rule(
                rule_id="bia_bp_001",
                name="Process owner documented",
                description="Each process should have a clearly identified owner",
                category=RuleCategory.BEST_PRACTICE,
                severity=RuleSeverity.MEDIUM,
                validation_fn=BIARules._validate_process_owners,
                applies_to_stages=None  # All stages
            ),
            
            Rule(
                rule_id="bia_bp_002",
                name="Dependency details",
                description="Dependencies should include type and criticality",
                category=RuleCategory.BEST_PRACTICE,
                severity=RuleSeverity.LOW,
                validation_fn=BIARules._validate_dependency_details,
                applies_to_stages=["analyze_dependencies"]
            ),
            
            Rule(
                rule_id="bia_bp_003",
                name="RPO alignment with RTO",
                description="RPO should be aligned with RTO (typically RPO ≤ RTO)",
                category=RuleCategory.BEST_PRACTICE,
                severity=RuleSeverity.LOW,
                validation_fn=BIARules._validate_rpo_rto_alignment,
                applies_to_stages=["determine_rto"]
            )
        ]
    
    # ========== VALIDATION FUNCTIONS ==========
    
    @staticmethod
    def _validate_minimum_rto(context: Dict[str, Any]) -> tuple[bool, str]:
        """No RTO < 1 hour without justification"""
        objectives = context.get('recovery_objectives', {})
        processes = context.get('processes', [])
        
        for proc in processes:
            if proc.get('tier') != 'tier_1':
                continue
                
            obj = objectives.get(proc['id'], {})
            rto = obj.get('rto_hours')
            
            if rto is not None and rto < 1:
                rationale = obj.get('rationale', '')
                if 'immediate' not in rationale.lower() and 'zero' not in rationale.lower():
                    return False, f"Tier 1 process '{proc['name']}' has RTO < 1h without justification"
                    
        return True, ""
    
    @staticmethod
    def _validate_financial_impact_exists(context: Dict[str, Any]) -> tuple[bool, str]:
        """All processes must have financial impact"""
        processes = context.get('processes', [])
        impacts = context.get('impacts', {})
        
        for proc in processes:
            impact = impacts.get(proc['id'], {})
            financial = impact.get('financial', {})
            
            if not financial.get('hourly_loss') and not financial.get('daily_loss'):
                return False, f"Process '{proc['name']}' missing financial impact"
                
        return True, ""
    
    @staticmethod
    def _validate_tier1_dependencies(context: Dict[str, Any]) -> tuple[bool, str]:
        """Tier 1 processes need complete dependencies"""
        processes = context.get('processes', [])
        dependencies = context.get('dependencies', [])
        
        tier1_procs = [p for p in processes if p.get('tier') == 'tier_1']
        
        for proc in tier1_procs:
            proc_deps = [d for d in dependencies if d.get('process_id') == proc['id']]
            
            if len(proc_deps) < 2:
                return False, f"Tier 1 process '{proc['name']}' needs at least 2 dependencies"
                
            # Check dependency types
            dep_types = set(d.get('type') for d in proc_deps)
            required_types = {'people', 'technology'}
            
            if not required_types.issubset(dep_types):
                return False, f"Tier 1 process '{proc['name']}' missing key dependency types (people/technology)"
                
        return True, ""
    
    @staticmethod
    def _validate_minimum_processes(context: Dict[str, Any]) -> tuple[bool, str]:
        """Minimum 3 processes"""
        processes = context.get('processes', [])
        
        if len(processes) < 3:
            return False, f"Need at least 3 processes, have {len(processes)}"
            
        return True, ""
    
    @staticmethod
    def _validate_has_tier1(context: Dict[str, Any]) -> tuple[bool, str]:
        """At least one Tier 1"""
        processes = context.get('processes', [])
        tier1_count = len([p for p in processes if p.get('tier') == 'tier_1'])
        
        if tier1_count == 0:
            return False, "No Tier 1 (critical) processes identified"
            
        return True, ""
    
    @staticmethod
    def _validate_all_impact_types(context: Dict[str, Any]) -> tuple[bool, str]:
        """All impact types assessed"""
        processes = context.get('processes', [])
        impacts = context.get('impacts', {})
        
        required_types = ['financial', 'operational', 'reputational', 'regulatory']
        
        for proc in processes:
            impact = impacts.get(proc['id'], {})
            
            missing = [t for t in required_types if t not in impact]
            if missing:
                return False, f"Process '{proc['name']}' missing impact types: {', '.join(missing)}"
                
        return True, ""
    
    @staticmethod
    def _validate_rto_rationale(context: Dict[str, Any]) -> tuple[bool, str]:
        """RTO rationale required"""
        objectives = context.get('recovery_objectives', {})
        
        for proc_id, obj in objectives.items():
            if not obj.get('rationale'):
                return False, f"Process {proc_id} RTO missing rationale"
                
            if len(obj['rationale']) < 30:
                return False, f"Process {proc_id} RTO rationale too brief (min 30 chars)"
                
        return True, ""
    
    @staticmethod
    def _validate_process_owners(context: Dict[str, Any]) -> tuple[bool, str]:
        """Process owners documented"""
        processes = context.get('processes', [])
        
        for proc in processes:
            if not proc.get('owner'):
                return False, f"Process '{proc['name']}' missing owner"
                
        return True, ""
    
    @staticmethod
    def _validate_dependency_details(context: Dict[str, Any]) -> tuple[bool, str]:
        """Dependencies have type and criticality"""
        dependencies = context.get('dependencies', [])
        
        for dep in dependencies:
            if not dep.get('type'):
                return False, f"Dependency missing type: {dep}"
                
            if not dep.get('criticality'):
                return False, f"Dependency missing criticality: {dep}"
                
        return True, ""
    
    @staticmethod
    def _validate_rpo_rto_alignment(context: Dict[str, Any]) -> tuple[bool, str]:
        """RPO ≤ RTO"""
        objectives = context.get('recovery_objectives', {})
        
        for proc_id, obj in objectives.items():
            rto = obj.get('rto_hours')
            rpo = obj.get('rpo_hours')
            
            if rto is not None and rpo is not None:
                if rpo > rto:
                    return False, f"Process {proc_id}: RPO ({rpo}h) > RTO ({rto}h)"
                    
        return True, ""