"""
Scenario Auto-Generator

Автогенератор сценариев на всех уровнях (L1-L4) с использованием:
- AI (LLM) для генерации
- Predictive Intelligence для оптимизации
- Community Intelligence для валидации
- BCM Service для domain expertise
- Workflow Intelligence для process mining
- Event Intelligence для pattern detection
- Orchestration для AI task delegation
- Simulation Service для testing
"""

import logging
import sys
from typing import Dict, List, Optional, Any
import yaml

# Add platform root to path for ACE integration
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')

# Import all adapters
from integration import (
    get_predictive_adapter,
    get_community_adapter,
    get_workflow_adapter,
    get_orchestration_adapter,
    get_event_intelligence_adapter,
    get_bcm_adapter,
    get_workflow_intel_adapter,
    get_simulation_adapter
)

# ACE Integration
from shared.ace_integration import ACEIntegration

logger = logging.getLogger(__name__)


class ScenarioAutoGenerator:
    """
    Автогенератор сценариев на всех уровнях (L1-L4)

    Uses all 8 integration adapters:
    1. predictive - предсказание оптимальных параметров
    2. community - валидация через consensus
    3. workflow - Temporal для long-running generation
    4. orchestration - делегирование AI задач
    5. event_intelligence - pattern detection
    6. bcm - domain expertise (ISO 22301, NIST, WHO)
    7. workflow_intel - process optimization
    8. simulation - testing generated scenarios
    """

    def __init__(self):
        """Initialize Auto-Generator with all adapters"""
        # ACE Integration for continuous learning
        self.ace = ACEIntegration(module_name="scenario_intelligence")

        # Adapters
        self.predictive = get_predictive_adapter()
        self.community = get_community_adapter()
        self.workflow = get_workflow_adapter()
        self.orchestration = get_orchestration_adapter()
        self.event_intel = get_event_intelligence_adapter()
        self.bcm = get_bcm_adapter()
        self.workflow_intel = get_workflow_intel_adapter()
        self.simulation = get_simulation_adapter()

        # State
        self.generation_stats = {
            "total_generated": 0,
            "by_level": {"l1": 0, "l2": 0, "l3": 0, "l4": 0},
            "success_rate": 0.0
        }

        logger.info(" Initialized ScenarioAutoGenerator with 8 adapters + ACE learning")

    # ==========================================================================
    # LEVEL 1: Module Scenarios (Service-level testing)
    # ==========================================================================

    async def generate_module_scenario(
        self,
        module_name: str,
        operation: str,
        framework: str = "ISO_22301"
    ) -> Dict[str, Any]:
        """
        Автогенерация Level 1 сценария для модуля (with ACE learning!)

        Args:
            module_name: Имя модуля (e.g., "notification-service")
            operation: Операция (e.g., "send_notification")
            framework: BCM framework (ISO_22301, NIST, WHO_Healthcare)

        Returns:
            Dict with generated scenario

        Example:
            scenario = await auto_gen.generate_module_scenario(
                module_name="notification-service",
                operation="send_notification",
                framework="ISO_22301"
            )
        """
        logger.info(f"Generating L1 scenario: {module_name}.{operation}")

        # Use ACE for continuous learning!
        result = await self.ace.execute_with_learning(
            task_type=f"scenario_L1_{module_name}_{operation}",
            base_context={
                "module_name": module_name,
                "operation": operation,
                "framework": framework
            },
            execute_fn=self._generate_module_scenario_impl
        )

        return result

    async def _generate_module_scenario_impl(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Internal implementation (called by ACE)"""
        module_name = context["module_name"]
        operation = context["operation"]
        framework = context["framework"]

        # ACE provides enhanced context with playbook strategies!
        strategies = context.get('playbook_strategies', [])
        patterns = context.get('known_patterns', [])

        logger.info(f"ACE enhanced context: {len(strategies)} strategies, {len(patterns)} patterns")

        # 1. Get BCM domain expertise
        domain_info = await self.bcm.get_framework_info(framework)
        logger.info(f"Got domain info for {framework}")

        # 2. Delegate AI task for scenario generation
        ai_task = await self.orchestration.delegate_to_ai(
            task_type="scenario_generation",
            scenario_context={
                "level": 1,
                "module_name": module_name,
                "operation": operation,
                "framework": framework,
                "domain_info": domain_info,
                "template_type": "functional"
            },
            priority="normal"
        )

        logger.info(f"Delegated to AI: task_id={ai_task['task_id']}")

        # 3. Wait for AI result
        ai_result = await self.orchestration.wait_for_result(
            task_id=ai_task["task_id"],
            timeout=120  # 2 minutes
        )

        if not ai_result["completed"]:
            logger.error("AI generation failed or timed out")
            return {"success": False, "error": "AI generation failed"}

        scenario_data = ai_result["result"]["scenario"]

        # 4. Predict optimal parameters
        prediction = await self.predictive.forecast_execution_time(
            scenario_id=f"{module_name}_{operation}",
            context={
                "module": module_name,
                "operation": operation,
                "steps_count": len(scenario_data.get("steps", []))
            }
        )

        # Add predicted timeout
        scenario_data["timeout_ms"] = int(prediction["predicted_duration_ms"] * 1.5)
        logger.info(f"Predicted timeout: {scenario_data['timeout_ms']}ms")

        # 5. Community validation
        validation = await self.community.validate_scenario(
            scenario_yaml=yaml.dump(scenario_data),
            validators=["all"]
        )

        if not validation["approved"]:
            logger.warning(f"Community rejected scenario: {validation['feedback']}")

            # Retry with feedback (simplified - just log for now)
            for feedback_item in validation["feedback"]:
                logger.info(f"Feedback: {feedback_item}")

            # In production: retry generation with feedback
            # For now: return with feedback
            scenario_data["validation_warnings"] = validation["feedback"]

        # 6. Safety check
        safety = await self.orchestration.check_safety(
            scenario_id=f"{module_name}_{operation}",
            planned_actions=[{"type": "http_request", "target": module_name}]
        )

        if not safety["safe"]:
            logger.error(f"Safety check failed: {safety['risks']}")
            scenario_data["safety_warnings"] = safety["risks"]

        # 7. Update stats
        self.generation_stats["total_generated"] += 1
        self.generation_stats["by_level"]["l1"] += 1

        logger.info(f" L1 scenario generated: {module_name}.{operation}")

        return {
            "success": True,
            "scenario": scenario_data,
            "level": 1,
            "validation": validation,
            "safety": safety,
            "predicted_duration_ms": prediction["predicted_duration_ms"]
        }

    # ==========================================================================
    # LEVEL 2: Subsystem Scenarios (Integration testing)
    # ==========================================================================

    async def generate_subsystem_scenario(
        self,
        subsystem_name: str,
        modules: List[str],
        interaction_type: str = "health_check"
    ) -> Dict[str, Any]:
        """
        Автогенерация Level 2 сценария для подсистемы

        Args:
            subsystem_name: Имя подсистемы
            modules: Список модулей в подсистеме
            interaction_type: Тип интеграции

        Returns:
            Dict with generated scenario

        Example:
            scenario = await auto_gen.generate_subsystem_scenario(
                subsystem_name="notification-subsystem",
                modules=["email-service", "sms-service", "push-service"],
                interaction_type="cross_module_communication"
            )
        """
        logger.info(f"Generating L2 scenario: {subsystem_name}")

        # 1. Analyze events for patterns
        analysis = await self.event_intel.analyze_scenario_events(
            scenario_id=subsystem_name,
            time_window="7d"
        )

        patterns = analysis.get("patterns", [])
        logger.info(f"Found {len(patterns)} patterns in subsystem events")

        # 2. Get workflow optimization recommendations
        optimizations = await self.workflow_intel.optimize_scenario(subsystem_name)
        logger.info(f"Got {len(optimizations['optimizations'])} optimization recommendations")

        # 3. Delegate AI task for L2 scenario generation
        ai_task = await self.orchestration.delegate_to_ai(
            task_type="scenario_generation",
            scenario_context={
                "level": 2,
                "subsystem_name": subsystem_name,
                "modules": modules,
                "interaction_type": interaction_type,
                "patterns": patterns,
                "optimizations": optimizations,
                "template_type": "integration"
            },
            priority="normal"
        )

        # 4. Wait for AI result
        ai_result = await self.orchestration.wait_for_result(
            task_id=ai_task["task_id"],
            timeout=180  # 3 minutes
        )

        if not ai_result["completed"]:
            return {"success": False, "error": "AI generation failed"}

        scenario_data = ai_result["result"]["scenario"]

        # 5. Community validation
        validation = await self.community.validate_scenario(
            scenario_yaml=yaml.dump(scenario_data),
            validators=["all"]
        )

        # 6. Predict failure probability
        prediction = await self.predictive.predict_scenario_failure(
            scenario_id=subsystem_name,
            historical_data={
                "modules": modules,
                "patterns": patterns
            }
        )

        logger.info(
            f"Failure prediction: {prediction['probability']:.2%} "
            f"(confidence: {prediction['confidence']:.2%})"
        )

        # 7. Update stats
        self.generation_stats["total_generated"] += 1
        self.generation_stats["by_level"]["l2"] += 1

        logger.info(f" L2 scenario generated: {subsystem_name}")

        return {
            "success": True,
            "scenario": scenario_data,
            "level": 2,
            "validation": validation,
            "failure_prediction": prediction,
            "patterns": patterns,
            "optimizations": optimizations
        }

    # ==========================================================================
    # LEVEL 3: Inter-system Scenarios (Functional testing)
    # ==========================================================================

    async def generate_intersystem_scenario(
        self,
        system_a: str,
        system_b: str,
        interaction_type: str,
        use_temporal: bool = False
    ) -> Dict[str, Any]:
        """
        Автогенерация Level 3 межсистемного сценария

        Args:
            system_a: Первая система
            system_b: Вторая система
            interaction_type: Тип взаимодействия
            use_temporal: Использовать Temporal workflow

        Returns:
            Dict with generated scenario

        Example:
            scenario = await auto_gen.generate_intersystem_scenario(
                system_a="ai-office",
                system_b="platform-services",
                interaction_type="ai_assisted_workflow",
                use_temporal=True
            )
        """
        logger.info(f"Generating L3 scenario: {system_a} ↔ {system_b}")

        # 1. Analyze execution flow for both systems
        flow_a = await self.workflow_intel.analyze_execution_flow(
            scenario_id=system_a,
            time_window="7d"
        )

        flow_b = await self.workflow_intel.analyze_execution_flow(
            scenario_id=system_b,
            time_window="7d"
        )

        logger.info(
            f"Flow analysis: {system_a}={flow_a['average_duration_ms']}ms, "
            f"{system_b}={flow_b['average_duration_ms']}ms"
        )

        # 2. Get BCM compliance requirements
        compliance_a = await self.bcm.validate_bcm_compliance(system_a)
        compliance_b = await self.bcm.validate_bcm_compliance(system_b)

        # 3. Community recommendation for best integration approach
        recommendation = await self.community.get_community_recommendation(
            scenario_id=f"{system_a}_{system_b}",
            context={
                "system_a": system_a,
                "system_b": system_b,
                "interaction_type": interaction_type
            },
            agents=["all"]
        )

        logger.info(f"Community consensus: {recommendation['consensus']}")

        # 4. Delegate AI task for L3 scenario generation
        ai_task = await self.orchestration.delegate_to_ai(
            task_type="scenario_generation",
            scenario_context={
                "level": 3,
                "system_a": system_a,
                "system_b": system_b,
                "interaction_type": interaction_type,
                "flow_analysis": {"system_a": flow_a, "system_b": flow_b},
                "compliance": {"system_a": compliance_a, "system_b": compliance_b},
                "community_recommendation": recommendation,
                "template_type": "functional"
            },
            priority="high"  # L3 is critical
        )

        # 5. Wait for AI result
        ai_result = await self.orchestration.wait_for_result(
            task_id=ai_task["task_id"],
            timeout=300  # 5 minutes
        )

        if not ai_result["completed"]:
            return {"success": False, "error": "AI generation failed"}

        scenario_data = ai_result["result"]["scenario"]

        # 6. If use_temporal, register as workflow
        if use_temporal:
            workflow_result = await self.workflow.execute_scenario_as_workflow(
                scenario_id=f"{system_a}_{system_b}_{interaction_type}",
                context=scenario_data
            )

            logger.info(f"Registered as Temporal workflow: {workflow_result['workflow_id']}")

            scenario_data["temporal_workflow_id"] = workflow_result["workflow_id"]

        # 7. Convert to simulation exercise for testing
        exercise = await self.simulation.convert_scenario_to_exercise(
            scenario_id=f"{system_a}_{system_b}_{interaction_type}",
            exercise_type="bcm_drill",
            duration_minutes=120
        )

        logger.info(f"Converted to exercise: {exercise['exercise_id']}")

        # 8. Update stats
        self.generation_stats["total_generated"] += 1
        self.generation_stats["by_level"]["l3"] += 1

        logger.info(f" L3 scenario generated: {system_a} ↔ {system_b}")

        return {
            "success": True,
            "scenario": scenario_data,
            "level": 3,
            "community_recommendation": recommendation,
            "compliance": {"system_a": compliance_a, "system_b": compliance_b},
            "exercise": exercise,
            "temporal_workflow_id": scenario_data.get("temporal_workflow_id")
        }

    # ==========================================================================
    # LEVEL 4: User/System Scenarios (E2E workflows)
    # ==========================================================================

    async def generate_user_workflow(
        self,
        user_persona: str,
        workflow_name: str,
        business_goal: str,
        framework: str = "ISO_22301"
    ) -> Dict[str, Any]:
        """
        Автогенерация Level 4 E2E workflow

        Args:
            user_persona: Персона пользователя
            workflow_name: Название workflow
            business_goal: Бизнес-цель
            framework: BCM framework

        Returns:
            Dict with generated scenario

        Example:
            scenario = await auto_gen.generate_user_workflow(
                user_persona="Risk Manager",
                workflow_name="Complete Risk Assessment",
                business_goal="Identify and mitigate organizational risks",
                framework="ISO_22301"
            )
        """
        logger.info(f"Generating L4 workflow: {workflow_name} for {user_persona}")

        # 1. Get BCM framework scenarios
        framework_scenarios = await self.bcm.load_framework_scenarios(framework)
        logger.info(f"Loaded {len(framework_scenarios)} {framework} scenarios")

        # 2. Get community best practices for this persona
        best_practices = await self.community.get_best_practices(
            scenario_type="workflow",
            level=4
        )

        logger.info(f"Got {len(best_practices)} best practices")

        # 3. Analyze patterns across all L3 scenarios
        anomalies = await self.event_intel.detect_anomalies(
            scenario_ids=[],  # All L3 scenarios
            time_window="30d"
        )

        logger.info(f"Detected {len(anomalies)} anomalies in L3 scenarios")

        # 4. Get process metrics from workflow intelligence
        # (In production: aggregate metrics from multiple L3 scenarios)

        # 5. Delegate AI task for L4 workflow generation
        ai_task = await self.orchestration.delegate_to_ai(
            task_type="scenario_generation",
            scenario_context={
                "level": 4,
                "user_persona": user_persona,
                "workflow_name": workflow_name,
                "business_goal": business_goal,
                "framework": framework,
                "framework_scenarios": [s.get("id") for s in framework_scenarios[:10]],
                "best_practices": best_practices,
                "anomalies": anomalies,
                "template_type": "e2e_workflow"
            },
            priority="high"
        )

        # 6. Wait for AI result
        ai_result = await self.orchestration.wait_for_result(
            task_id=ai_task["task_id"],
            timeout=600  # 10 minutes for complex E2E
        )

        if not ai_result["completed"]:
            return {"success": False, "error": "AI generation failed"}

        scenario_data = ai_result["result"]["scenario"]

        # 7. Community validation with all agents
        validation = await self.community.validate_scenario(
            scenario_yaml=yaml.dump(scenario_data),
            validators=["all"]
        )

        logger.info(
            f"Community validation: approved={validation['approved']}, "
            f"score={validation['score']:.2f}"
        )

        # 8. BCM compliance check
        compliance = await self.bcm.validate_bcm_compliance(
            scenario_id=workflow_name,
            iso_clause=None  # Check all clauses
        )

        # 9. Register as Temporal workflow (L4 workflows are long-running)
        workflow_result = await self.workflow.execute_scenario_as_workflow(
            scenario_id=workflow_name,
            context=scenario_data
        )

        logger.info(f"Registered as Temporal workflow: {workflow_result['workflow_id']}")

        # 10. Apply PDCA cycle for continuous improvement
        pdca = await self.workflow_intel.apply_pdca_cycle(workflow_name)

        logger.info(f"PDCA cycle applied: {list(pdca.keys())}")

        # 11. Convert to simulation exercise
        exercise = await self.simulation.convert_scenario_to_exercise(
            scenario_id=workflow_name,
            exercise_type="bcm_drill",
            duration_minutes=480  # 8 hours for E2E
        )

        # 12. Update stats
        self.generation_stats["total_generated"] += 1
        self.generation_stats["by_level"]["l4"] += 1
        self.generation_stats["success_rate"] = (
            self.generation_stats["total_generated"] /
            max(self.generation_stats["total_generated"], 1)
        )

        logger.info(f" L4 workflow generated: {workflow_name}")

        return {
            "success": True,
            "scenario": scenario_data,
            "level": 4,
            "validation": validation,
            "compliance": compliance,
            "best_practices": best_practices,
            "temporal_workflow_id": workflow_result["workflow_id"],
            "exercise": exercise,
            "pdca": pdca,
            "stats": self.generation_stats
        }

    # ==========================================================================
    # UTILITY METHODS
    # ==========================================================================

    async def generate_batch(
        self,
        level: int,
        specifications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Генерация batch сценариев

        Args:
            level: Уровень (1-4)
            specifications: Список спецификаций

        Returns:
            List of generated scenarios
        """
        logger.info(f"Generating batch of {len(specifications)} L{level} scenarios")

        results = []

        for spec in specifications:
            if level == 1:
                result = await self.generate_module_scenario(**spec)
            elif level == 2:
                result = await self.generate_subsystem_scenario(**spec)
            elif level == 3:
                result = await self.generate_intersystem_scenario(**spec)
            elif level == 4:
                result = await self.generate_user_workflow(**spec)
            else:
                logger.error(f"Invalid level: {level}")
                continue

            results.append(result)

        logger.info(f" Batch generation complete: {len(results)} scenarios")

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return self.generation_stats


# Global instance
_auto_generator: Optional[ScenarioAutoGenerator] = None


def get_auto_generator() -> ScenarioAutoGenerator:
    """Get global Auto-Generator instance"""
    global _auto_generator
    if _auto_generator is None:
        _auto_generator = ScenarioAutoGenerator()
    return _auto_generator
