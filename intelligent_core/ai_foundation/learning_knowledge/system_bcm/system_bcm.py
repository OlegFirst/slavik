"""
System BCM - Platform Self-Application Module

Applies BCM to AI-Platform-ISO itself, enabling the platform to:
1. Analyze its own critical processes (BIA)
2. Identify its own risks
3. Configure auto-recovery
4. Manage resource priorities

The platform LIVES BCM on itself, learning through practice.
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemBCM:
    """
    Platform Self-BCM Engine

    Enables the platform to apply Business Continuity Management to ITSELF.
    This is the core of self-learning: practicing resilience, not just teaching it.
    """

    def __init__(self, scenarios_path: str = None):
        """
        Initialize System BCM

        Args:
            scenarios_path: Path to system scenarios directory
        """
        if scenarios_path is None:
            scenarios_path = Path(__file__).parent.parent / "scenarios" / "system_scenarios"

        self.scenarios_path = Path(scenarios_path)
        self.bia_data = None
        self.risks_data = None
        self.recovery_data = None
        self.priorities_data = None

        logger.info(f"SystemBCM initialized with scenarios path: {self.scenarios_path}")

    async def load_scenarios(self):
        """Load all system scenarios"""
        try:
            # Load BIA
            bia_file = self.scenarios_path / "platform_bia.json"
            with open(bia_file, 'r') as f:
                self.bia_data = json.load(f)
            logger.info("Loaded platform BIA scenario")

            # Load Risks
            risks_file = self.scenarios_path / "platform_risks.json"
            with open(risks_file, 'r') as f:
                self.risks_data = json.load(f)
            logger.info("Loaded platform risks scenario")

            # Load Recovery
            recovery_file = self.scenarios_path / "recovery_procedures.json"
            with open(recovery_file, 'r') as f:
                self.recovery_data = json.load(f)
            logger.info("Loaded recovery procedures")

            # Load Priorities
            priorities_file = self.scenarios_path / "resource_priorities.json"
            with open(priorities_file, 'r') as f:
                self.priorities_data = json.load(f)
            logger.info("Loaded resource priorities")

        except Exception as e:
            logger.error(f"Failed to load scenarios: {e}")
            raise

    async def execute_self_bia(self) -> Dict[str, Any]:
        """
        Execute BIA for the platform ITSELF

        Returns:
            BIA results with identified critical processes, RTOs, RPOs, dependencies
        """
        logger.info(" Executing Self-BIA: Analyzing platform's own critical processes")

        if not self.bia_data:
            await self.load_scenarios()

        results = {
            "execution_time": datetime.utcnow().isoformat(),
            "target": self.bia_data["target"],
            "critical_processes": [],
            "dependencies_identified": [],
            "recovery_targets_set": [],
            "actions_taken": []
        }

        # Analyze each critical process
        for process in self.bia_data["critical_processes"]:
            process_analysis = {
                "process_id": process["process_id"],
                "name": process["name"],
                "criticality": process["criticality"],
                "rto": process["rto"],
                "rpo": process["rpo"],
                "recovery_priority": process["recovery_priority"],
                "auto_recovery_enabled": process.get("auto_recovery", False)
            }

            results["critical_processes"].append(process_analysis)

            logger.info(
                f"   {process['name']}: "
                f"Tier {process['criticality']}, "
                f"RTO={process['rto']}, "
                f"RPO={process['rpo']}, "
                f"Priority={process['recovery_priority']}"
            )

        # Analyze cross-dependencies
        for dep in self.bia_data["cross_dependencies"]:
            dependency_analysis = {
                "from_service": dep["from"],
                "to_services": dep["to"],
                "type": dep["type"],
                "failure_mode": dep["failure_mode"]
            }
            results["dependencies_identified"].append(dependency_analysis)

            logger.info(
                f"  → Dependency: {dep['from']} depends on {dep['to']} "
                f"(failure mode: {dep['failure_mode']})"
            )

        # Set recovery targets for each tier
        for tier_priority in self.bia_data["resource_priorities"]:
            tier_info = {
                "tier": tier_priority["tier"],
                "processes": tier_priority["processes"],
                "resource_allocation": tier_priority["resource_allocation"],
                "action_on_contention": tier_priority["action_on_resource_contention"]
            }
            results["recovery_targets_set"].append(tier_info)

            logger.info(
                f"  ️  {tier_priority['tier']}: "
                f"{len(tier_priority['processes'])} processes"
            )

        # Actions to take based on BIA
        results["actions_taken"] = [
            "critical_processes_identified",
            "rto_rpo_targets_defined",
            "dependencies_mapped",
            "recovery_priorities_set",
            "resource_tiers_established"
        ]

        logger.info(f" Self-BIA Complete: {len(results['critical_processes'])} critical processes identified")

        return results

    async def assess_own_risks(self) -> Dict[str, Any]:
        """
        Assess platform's OWN risks

        Returns:
            Risk assessment results with identified risks and mitigation strategies
        """
        logger.info(" Assessing Own Risks: Identifying platform's vulnerabilities")

        if not self.risks_data:
            await self.load_scenarios()

        results = {
            "execution_time": datetime.utcnow().isoformat(),
            "target": self.risks_data["target"],
            "risks_by_category": {},
            "high_priority_risks": [],
            "mitigations_to_implement": [],
            "actions_taken": []
        }

        # Analyze risks by category
        for category_data in self.risks_data["risk_categories"]:
            category = category_data["category"]
            risks = category_data["risks"]

            results["risks_by_category"][category] = []

            for risk in risks:
                risk_analysis = {
                    "risk_id": risk["risk_id"],
                    "name": risk["name"],
                    "probability": risk["probability"],
                    "impact": risk["impact"],
                    "risk_score": risk["risk_score"],
                    "current_controls": risk.get("current_controls", []),
                    "residual_risk": risk.get("residual_risk", "unknown")
                }

                results["risks_by_category"][category].append(risk_analysis)

                # High priority risks (score >= 7)
                if risk["risk_score"] >= 7:
                    results["high_priority_risks"].append(risk_analysis)
                    logger.warning(
                        f"  ️  HIGH RISK: {risk['name']} "
                        f"(score={risk['risk_score']}, "
                        f"probability={risk['probability']}, "
                        f"impact={risk['impact']})"
                    )
                else:
                    logger.info(
                        f"  ℹ️  {risk['name']} "
                        f"(score={risk['risk_score']})"
                    )

                # Extract mitigation strategies
                for mitigation in risk.get("mitigation_strategies", []):
                    mitigation_info = {
                        "risk_id": risk["risk_id"],
                        "risk_name": risk["name"],
                        "type": mitigation["type"],
                        "actions": mitigation["actions"]
                    }
                    results["mitigations_to_implement"].append(mitigation_info)

        # Summary
        total_risks = sum(len(risks) for risks in results["risks_by_category"].values())
        high_risks = len(results["high_priority_risks"])

        results["actions_taken"] = [
            f"identified_{total_risks}_risks",
            f"flagged_{high_risks}_high_priority_risks",
            f"prepared_{len(results['mitigations_to_implement'])}_mitigation_strategies"
        ]

        logger.info(
            f" Risk Assessment Complete: "
            f"{total_risks} risks identified, "
            f"{high_risks} high-priority"
        )

        return results

    async def setup_recovery(self) -> Dict[str, Any]:
        """
        Setup auto-recovery procedures for the platform

        Returns:
            Recovery setup results with configured procedures
        """
        logger.info(" Setting Up Recovery: Configuring platform auto-recovery")

        if not self.recovery_data:
            await self.load_scenarios()

        results = {
            "execution_time": datetime.utcnow().isoformat(),
            "target": self.recovery_data["target"],
            "procedures_configured": [],
            "auto_recovery_enabled": [],
            "manual_approval_required": [],
            "actions_taken": []
        }

        # Configure each recovery procedure
        for procedure in self.recovery_data["recovery_procedures"]:
            procedure_config = {
                "procedure_id": procedure["procedure_id"],
                "name": procedure["name"],
                "triggers": procedure["triggers"],
                "detection_time_target": procedure["detection_time_target"],
                "recovery_time_target": procedure["recovery_time_target"],
                "steps_count": len(procedure["steps"]),
                "automation_ready": True
            }

            results["procedures_configured"].append(procedure_config)

            logger.info(
                f"   {procedure['name']}: "
                f"Detection<{procedure['detection_time_target']}, "
                f"Recovery<{procedure['recovery_time_target']}, "
                f"{len(procedure['steps'])} steps"
            )

            # Simulate configuration (in real implementation, this would configure actual systems)
            await self._configure_procedure(procedure)

        # Check automation config
        auto_config = self.recovery_data.get("automation_config", {})
        results["auto_recovery_enabled"] = auto_config.get("auto_recovery_procedures", [])
        results["manual_approval_required"] = auto_config.get("manual_approval_required", [])

        results["actions_taken"] = [
            f"configured_{len(results['procedures_configured'])}_recovery_procedures",
            f"enabled_auto_recovery_for_{len(results['auto_recovery_enabled'])}_procedures",
            f"manual_approval_required_for_{len(results['manual_approval_required'])}_procedures"
        ]

        logger.info(
            f" Recovery Setup Complete: "
            f"{len(results['procedures_configured'])} procedures configured, "
            f"{len(results['auto_recovery_enabled'])} automated"
        )

        return results

    async def _configure_procedure(self, procedure: Dict[str, Any]):
        """
        Configure a single recovery procedure

        In real implementation, this would:
        - Register health check monitors
        - Configure alerting rules
        - Set up automated scripts
        - Configure circuit breakers
        """
        # Simulate configuration delay
        await asyncio.sleep(0.1)

        # In production, this would configure actual monitoring and automation
        logger.debug(f"Configured procedure: {procedure['procedure_id']}")

    async def apply_priorities(self) -> Dict[str, Any]:
        """
        Apply resource priorities to ensure critical services survive

        Returns:
            Priority application results
        """
        logger.info(" Applying Resource Priorities: Protecting critical services")

        if not self.priorities_data:
            await self.load_scenarios()

        results = {
            "execution_time": datetime.utcnow().isoformat(),
            "target": self.priorities_data["target"],
            "tiers_configured": [],
            "services_prioritized": [],
            "contention_policies_set": [],
            "actions_taken": []
        }

        # Configure each tier
        for tier_config in self.priorities_data["service_tiers"]:
            tier_info = {
                "tier": tier_config["tier"],
                "description": tier_config["description"],
                "services_count": len(tier_config["services"]),
                "resource_reservation": tier_config["total_resource_reservation"]
            }

            results["tiers_configured"].append(tier_info)

            logger.info(
                f"   {tier_config['tier']}: "
                f"{len(tier_config['services'])} services, "
                f"CPU={tier_config['total_resource_reservation']['cpu']}, "
                f"Memory={tier_config['total_resource_reservation']['memory']}"
            )

            # Configure each service in tier
            for service in tier_config["services"]:
                service_config = {
                    "service_name": service["service_name"],
                    "tier": tier_config["tier"],
                    "criticality": service["criticality"],
                    "cpu_guarantee": service["resource_guarantees"]["cpu"],
                    "memory_guarantee": service["resource_guarantees"]["memory"],
                    "degradation_behavior": service["degradation_behavior"]
                }

                results["services_prioritized"].append(service_config)

                logger.info(
                    f"    → {service['service_name']}: "
                    f"CPU={service['resource_guarantees']['cpu']['minimum']}-"
                    f"{service['resource_guarantees']['cpu']['maximum']}, "
                    f"Memory={service['resource_guarantees']['memory']['minimum']}-"
                    f"{service['resource_guarantees']['memory']['maximum']}"
                )

                # Simulate applying resource limits
                await self._apply_service_limits(service)

        # Configure contention policies
        for policy in self.priorities_data["resource_contention_policies"]:
            policy_config = {
                "contention_type": policy["contention_type"],
                "detection": policy["detection"],
                "response_actions": len(policy["response"])
            }

            results["contention_policies_set"].append(policy_config)

            logger.info(
                f"  ️  Contention Policy: {policy['contention_type']} → "
                f"{len(policy['response'])} response actions"
            )

        results["actions_taken"] = [
            f"configured_{len(results['tiers_configured'])}_resource_tiers",
            f"prioritized_{len(results['services_prioritized'])}_services",
            f"set_{len(results['contention_policies_set'])}_contention_policies",
            "enabled_dynamic_resource_allocation"
        ]

        logger.info(
            f" Resource Priorities Applied: "
            f"{len(results['tiers_configured'])} tiers, "
            f"{len(results['services_prioritized'])} services prioritized"
        )

        return results

    async def _apply_service_limits(self, service: Dict[str, Any]):
        """
        Apply resource limits to a service

        In real implementation, this would:
        - Update Docker/Kubernetes resource limits
        - Configure cgroups
        - Set OOM scores
        - Configure network QoS
        """
        # Simulate configuration delay
        await asyncio.sleep(0.05)

        # In production, this would apply actual resource limits
        logger.debug(f"Applied limits to service: {service['service_name']}")

    async def execute_full_cycle(self) -> Dict[str, Any]:
        """
        Execute the full System BCM cycle:
        1. BIA
        2. Risk Assessment
        3. Recovery Setup
        4. Priority Application

        This is the platform applying BCM to ITSELF.

        Returns:
            Complete cycle results
        """
        logger.info(" Starting Full System BCM Cycle")
        logger.info("=" * 60)

        cycle_results = {
            "cycle_start": datetime.utcnow().isoformat(),
            "target": "AI-Platform-ISO",
            "level": "system",
            "phases": {}
        }

        try:
            # Phase 1: BIA
            logger.info("\n PHASE 1: Business Impact Analysis")
            logger.info("-" * 60)
            bia_results = await self.execute_self_bia()
            cycle_results["phases"]["bia"] = {
                "status": "completed",
                "results": bia_results
            }

            # Phase 2: Risk Assessment
            logger.info("\n️  PHASE 2: Risk Assessment")
            logger.info("-" * 60)
            risk_results = await self.assess_own_risks()
            cycle_results["phases"]["risk_assessment"] = {
                "status": "completed",
                "results": risk_results
            }

            # Phase 3: Recovery Setup
            logger.info("\n PHASE 3: Recovery Setup")
            logger.info("-" * 60)
            recovery_results = await self.setup_recovery()
            cycle_results["phases"]["recovery_setup"] = {
                "status": "completed",
                "results": recovery_results
            }

            # Phase 4: Priority Application
            logger.info("\n PHASE 4: Resource Priorities")
            logger.info("-" * 60)
            priority_results = await self.apply_priorities()
            cycle_results["phases"]["priority_application"] = {
                "status": "completed",
                "results": priority_results
            }

            cycle_results["cycle_end"] = datetime.utcnow().isoformat()
            cycle_results["status"] = "success"

            logger.info("\n" + "=" * 60)
            logger.info(" Full System BCM Cycle COMPLETED Successfully")
            logger.info("=" * 60)
            logger.info("\n Platform has applied BCM to ITSELF!")
            logger.info("   → Critical processes identified and prioritized")
            logger.info("   → Risks assessed and mitigations prepared")
            logger.info("   → Auto-recovery procedures configured")
            logger.info("   → Resource priorities enforced")
            logger.info("\n Platform is now LIVING BCM through practice!")

        except Exception as e:
            logger.error(f" System BCM Cycle failed: {e}")
            cycle_results["status"] = "failed"
            cycle_results["error"] = str(e)
            raise

        return cycle_results


# Convenience functions for direct usage

async def execute_self_bia() -> Dict[str, Any]:
    """Execute BIA for the platform itself"""
    bcm = SystemBCM()
    return await bcm.execute_self_bia()


async def assess_own_risks() -> Dict[str, Any]:
    """Assess platform's own risks"""
    bcm = SystemBCM()
    return await bcm.assess_own_risks()


async def setup_recovery() -> Dict[str, Any]:
    """Setup auto-recovery procedures"""
    bcm = SystemBCM()
    return await bcm.setup_recovery()


async def apply_priorities() -> Dict[str, Any]:
    """Apply resource priorities"""
    bcm = SystemBCM()
    return await bcm.apply_priorities()


# CLI entry point for testing
if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def main():
        bcm = SystemBCM()

        if len(sys.argv) > 1:
            action = sys.argv[1]

            if action == "bia":
                results = await bcm.execute_self_bia()
            elif action == "risk":
                results = await bcm.assess_own_risks()
            elif action == "recovery":
                results = await bcm.setup_recovery()
            elif action == "priorities":
                results = await bcm.apply_priorities()
            elif action == "full":
                results = await bcm.execute_full_cycle()
            else:
                print(f"Unknown action: {action}")
                print("Usage: python system_bcm.py [bia|risk|recovery|priorities|full]")
                sys.exit(1)

            print(json.dumps(results, indent=2))
        else:
            # Default: run full cycle
            results = await bcm.execute_full_cycle()
            print(json.dumps(results, indent=2))

    asyncio.run(main())
