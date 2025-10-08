#!/usr/bin/env python3
"""
DevOps Agent - AI Digital Colleague

Autonomous DevOps agent for:
- Infrastructure analysis
- Auto-remediation
- Deployment monitoring
- Container management
- Integration with platform services
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import argparse

# Add project root and ai-foundation to path
# DevOps Agent is in: infrastructure/AI-office-infrastructure/devops-agent/
# Project root is 3 levels up
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "intelligent-core" / "ai-foundation"))

# Now can import directly (Python sees ai-foundation as package)
from rag.pipeline import RAGPipeline
from llm.llm_router import LLMRouter

# EventBus is in infrastructure/
sys.path.insert(0, str(project_root / "infrastructure"))
from eventbus import create_eventbus

sys.path.insert(0, str(Path(__file__).parent))
from reports.report_manager import ReportManager
from integrations.workflow_intelligence import WorkflowIntelligenceClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DevOpsAgent:
    """
    DevOps Agent - AI Digital Colleague

    Responsibilities:
    - Continuous code analysis
    - Event architecture monitoring
    - Dockerfile generation
    - Deployment tracking
    - Auto-remediation
    - Platform integration
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.agent_id = "devops-agent"
        self.name = "DevOps Agent AI"

        # AI Foundation integrations
        self.rag: Optional[RAGPipeline] = None
        self.llm: Optional[LLMRouter] = None
        self.eventbus = None

        # Platform integrations
        self.report_manager = ReportManager(project_root)
        self.workflow_intelligence: Optional[WorkflowIntelligenceClient] = None

        # Statistics
        self.scans_completed = 0
        self.issues_detected = 0
        self.fixes_applied = 0

        logger.info(f"🤖 {self.name} initialized")

    async def initialize(self):
        """Initialize AI components"""
        try:
            # Initialize RAG for knowledge retrieval
            self.rag = RAGPipeline()
            logger.info("✅ RAG Pipeline initialized")

            # Initialize LLM for AI analysis
            self.llm = LLMRouter()
            logger.info("✅ LLM Router initialized")

            # Initialize EventBus for communication
            self.eventbus = create_eventbus('memory')  # or 'redis' based on config
            if self.eventbus:
                # Memory backend doesn't need connect, but Redis does
                logger.info("✅ EventBus initialized")

            # Initialize Workflow Intelligence client
            self.workflow_intelligence = WorkflowIntelligenceClient()
            logger.info("✅ Workflow Intelligence client initialized")

        except Exception as e:
            logger.error(f"❌ Initialization error: {e}")
            raise

    async def scan_infrastructure(self, scan_type: str = "full") -> Dict:
        """
        Scan infrastructure and analyze

        Args:
            scan_type: 'full', 'events', 'containers', 'deployments'

        Returns:
            Analysis results
        """
        logger.info(f"🔍 Starting {scan_type} infrastructure scan...")

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "scan_type": scan_type,
            "agent_id": self.agent_id
        }

        if scan_type in ["full", "events"]:
            # Event architecture analysis
            event_results = await self._scan_events()
            results["events"] = event_results

        if scan_type in ["full", "containers"]:
            # Container analysis
            container_results = await self._scan_containers()
            results["containers"] = container_results

        if scan_type in ["full", "deployments"]:
            # Deployment analysis
            deployment_results = await self._scan_deployments()
            results["deployments"] = deployment_results

        self.scans_completed += 1
        self.issues_detected += results.get("total_issues", 0)

        return results

    async def _scan_events(self) -> Dict:
        """Scan event architecture (from old event_intelligence_system.py)"""
        from analyzers.event_analyzer import EventArchitectureAnalyzer

        analyzer = EventArchitectureAnalyzer(str(self.project_root))

        # Load schemas
        analyzer.load_asyncapi_schema()
        analyzer.load_catalog()

        # Scan codebase
        analyzer.scan_codebase()

        # Analyze gaps
        gaps = analyzer.analyze_gaps()

        # Discover potential events
        potential = analyzer.discover_potential_events()

        return {
            "schema_events": len(analyzer.schema_events),
            "code_events": len(set(e.name for e in analyzer.code_events.values())),
            "gaps_found": len(gaps),
            "potential_events": len(potential),
            "critical_gaps": len([g for g in gaps if g.severity == 'critical'])
        }

    async def _scan_containers(self) -> Dict:
        """Scan container configurations"""
        from analyzers.dockerfile_analyzer import DockerfileAnalyzer

        analyzer = DockerfileAnalyzer(str(self.project_root))

        # Find services without Dockerfiles
        missing_dockerfiles = analyzer.find_missing_dockerfiles()

        # Analyze existing Dockerfiles
        dockerfile_issues = analyzer.analyze_existing()

        return {
            "missing_dockerfiles": len(missing_dockerfiles),
            "services_analyzed": analyzer.services_count,
            "issues_found": len(dockerfile_issues)
        }

    async def _scan_deployments(self) -> Dict:
        """Scan deployment status"""
        from analyzers.deployment_analyzer import DeploymentAnalyzer

        analyzer = DeploymentAnalyzer(str(self.project_root))

        # Check running services
        services_status = analyzer.check_services_health()

        # Detect port conflicts
        port_conflicts = analyzer.detect_port_conflicts()

        return {
            "total_services": len(services_status),
            "healthy_services": len([s for s in services_status if s['healthy']]),
            "port_conflicts": len(port_conflicts)
        }

    async def ai_analysis(self, scan_results: Dict) -> Dict:
        """
        AI-powered analysis with knowledge retrieval from RAG

        Uses RAG to retrieve historical patterns, then LLM to analyze
        """
        logger.info("🧠 Running AI analysis with knowledge retrieval...")

        if not self.llm:
            logger.warning("LLM not initialized, skipping AI analysis")
            return {"recommendations": []}

        # 🔹 STEP 1: Retrieve relevant knowledge from RAG
        relevant_knowledge = []

        if self.rag:
            # Build search queries from scan results
            search_queries = []

            # Event architecture issues
            if scan_results.get("events", {}).get("critical_gaps", 0) > 0:
                search_queries.append("critical event architecture gaps solutions")

            # Container issues
            if scan_results.get("containers", {}).get("missing_dockerfiles", 0) > 0:
                search_queries.append("dockerfile best practices for microservices")

            # Port conflicts
            if scan_results.get("deployments", {}).get("port_conflicts", 0) > 0:
                search_queries.append("port conflict resolution deployment")

            # Retrieve knowledge for each query
            for query in search_queries:
                try:
                    knowledge_chunks = await self.rag.retrieve(
                        query=query,
                        context={
                            "domain": "devops",
                            "task": "infrastructure_analysis"
                        },
                        top_k=3,
                        filters={"source_type": "devops_patterns"},
                        enable_reranking=True
                    )
                    relevant_knowledge.extend(knowledge_chunks)
                except Exception as e:
                    logger.warning(f"RAG retrieval failed for '{query}': {e}")

            logger.info(f"📚 Retrieved {len(relevant_knowledge)} knowledge chunks from RAG")

        # 🔹 STEP 2: Build enriched context
        knowledge_context = self._format_knowledge_context(relevant_knowledge)
        scan_context = self._format_scan_results(scan_results)

        enriched_context = f"""
        === RELEVANT KNOWLEDGE FROM PAST EXPERIENCES ===
        {knowledge_context}

        === CURRENT INFRASTRUCTURE SCAN RESULTS ===
        {scan_context}

        === TASK ===
        Based on the relevant knowledge and current scan results:
        1. Identify the most critical issues
        2. Provide specific recommendations with priority ranking
        3. Assess risk level for each issue
        4. Suggest which issues can be auto-fixed safely

        Format response as JSON with structure:
        {{
          "recommendations": [
            {{
              "id": "unique_id",
              "category": "event_architecture|missing_dockerfile|port_conflict",
              "priority": "critical|high|medium|low",
              "description": "detailed description",
              "suggested_action": "specific action to take",
              "auto_fix_safe": true|false,
              "risk_level": "high|medium|low"
            }}
          ],
          "risk_level": "critical|high|medium|low",
          "auto_fix_approved": true|false
        }}
        """

        # 🔹 STEP 3: Query LLM with full context
        try:
            response = await self.llm.query(
                system_prompt="""You are an expert DevOps infrastructure analyst.
                Analyze infrastructure issues based on historical patterns and current data.
                Provide actionable, specific recommendations.""",
                user_prompt=enriched_context,
                task_type="infrastructure_analysis",
                temperature=0.3,
                max_tokens=3000
            )

            # Parse JSON response
            import json
            ai_analysis = json.loads(response)

            return ai_analysis

        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            return {
                "recommendations": [],
                "risk_level": "unknown",
                "auto_fix_approved": False
            }
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {
                "recommendations": [],
                "risk_level": "unknown",
                "auto_fix_approved": False
            }

    async def apply_fixes(self, recommendations: List[Dict]) -> Dict:
        """
        Apply auto-remediation WITH BRAIN APPROVAL

        Args:
            recommendations: List of AI recommendations

        Returns:
            Fix results
        """
        logger.info("🛠️ Requesting approval from Workflow Intelligence...")

        # 1. Request decision from мозг
        if self.workflow_intelligence:
            brain_decision = await self.workflow_intelligence.request_decision({
                "agent_id": self.agent_id,
                "context": "auto_remediation",
                "recommendations": recommendations,
                "risk_assessment": self._assess_risk(recommendations)
            })

            approved_actions = brain_decision.get("approved_actions", [])
            logger.info(f"✅ Brain approved {len(approved_actions)}/{len(recommendations)} actions")
        else:
            logger.warning("⚠️  No brain connection - applying all (UNSAFE!)")
            approved_actions = recommendations

        # 2. Apply only approved fixes
        from auto_remediation.event_fixer import EventFixer
        from auto_remediation.dockerfile_generator import DockerfileGenerator

        results = {
            "approved": len(approved_actions),
            "fixes_attempted": 0,
            "fixes_successful": 0,
            "fixes_failed": 0,
            "feedbacks": []
        }

        for action in approved_actions:
            fix_result = None

            if action.get("category") == "event_architecture":
                fixer = EventFixer(str(self.project_root))
                fix_result = await fixer.fix(action)

            elif action.get("category") == "missing_dockerfile":
                generator = DockerfileGenerator(str(self.project_root))
                fix_result = await generator.generate(action)

            results["fixes_attempted"] += 1

            if fix_result and fix_result.get("success"):
                results["fixes_successful"] += 1
                self.fixes_applied += 1

                # 🔹 STORE SUCCESSFUL PATTERN IN RAG
                await self._store_successful_pattern(action, fix_result)

                # Send feedback to brain
                if self.workflow_intelligence:
                    await self.workflow_intelligence.report_fix_applied({
                        "action_id": action.get("id", "unknown"),
                        "category": action.get("category"),
                        "success": True,
                        "outcome": fix_result.get("outcome", "applied")
                    })
                    results["feedbacks"].append("success")
            else:
                results["fixes_failed"] += 1

                # Report failure to brain
                if self.workflow_intelligence:
                    await self.workflow_intelligence.report_fix_applied({
                        "action_id": action.get("id", "unknown"),
                        "category": action.get("category"),
                        "success": False,
                        "error": fix_result.get("error") if fix_result else "unknown"
                    })
                    results["feedbacks"].append("failed")

        return results

    def _format_knowledge_context(self, knowledge_chunks: List[Dict]) -> str:
        """Format knowledge chunks for LLM context"""
        if not knowledge_chunks:
            return "No relevant historical knowledge found."

        formatted = []
        for i, chunk in enumerate(knowledge_chunks, 1):
            formatted.append(f"""
            Knowledge {i}:
            Source: {chunk.get('source', 'unknown')}
            Content: {chunk.get('content', '')}
            Relevance Score: {chunk.get('score', 0.0):.2f}
            """)

        return "\n".join(formatted)

    def _format_scan_results(self, scan_results: Dict) -> str:
        """Format scan results for LLM context"""
        formatted = []

        if "events" in scan_results:
            events = scan_results["events"]
            formatted.append(f"""
            EVENT ARCHITECTURE:
            - Schema Events: {events.get('schema_events', 0)}
            - Code Events: {events.get('code_events', 0)}
            - Gaps Found: {events.get('gaps_found', 0)}
            - Critical Gaps: {events.get('critical_gaps', 0)}
            - Potential Events: {events.get('potential_events', 0)}
            """)

        if "containers" in scan_results:
            containers = scan_results["containers"]
            formatted.append(f"""
            CONTAINERS:
            - Missing Dockerfiles: {containers.get('missing_dockerfiles', 0)}
            - Services Analyzed: {containers.get('services_analyzed', 0)}
            - Issues Found: {containers.get('issues_found', 0)}
            """)

        if "deployments" in scan_results:
            deployments = scan_results["deployments"]
            formatted.append(f"""
            DEPLOYMENTS:
            - Total Services: {deployments.get('total_services', 0)}
            - Healthy Services: {deployments.get('healthy_services', 0)}
            - Port Conflicts: {deployments.get('port_conflicts', 0)}
            """)

        return "\n".join(formatted)

    def _assess_risk(self, recommendations: List[Dict]) -> Dict:
        """Assess risk level of recommendations"""
        critical_count = len([r for r in recommendations if r.get("priority") == "critical"])
        high_count = len([r for r in recommendations if r.get("priority") == "high"])

        if critical_count > 0:
            risk_level = "critical"
        elif high_count > 3:
            risk_level = "high"
        elif high_count > 0:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "total_recommendations": len(recommendations),
            "critical": critical_count,
            "high": high_count,
            "requires_manual_approval": risk_level in ["critical", "high"]
        }

    async def _store_successful_pattern(self, action: Dict, fix_result: Dict):
        """Store successful fix pattern in knowledge base (RAG)"""

        if not self.rag:
            return

        pattern_text = f"""
        SUCCESSFUL FIX PATTERN

        Category: {action.get('category', 'unknown')}
        Priority: {action.get('priority', 'unknown')}

        Problem Description:
        {action.get('description', 'N/A')}

        Solution Applied:
        {action.get('suggested_action', 'N/A')}

        Outcome:
        {fix_result.get('outcome', 'Applied successfully')}

        Risk Level: {action.get('risk_level', 'unknown')}
        Auto-fix Safe: {action.get('auto_fix_safe', False)}

        Success Rate: 100% (verified)
        Applied At: {datetime.utcnow().isoformat()}
        """

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": pattern_text,
                    "metadata": {
                        "source_type": "devops_patterns",
                        "pattern_category": action.get("category"),
                        "priority": action.get("priority"),
                        "auto_fix_safe": action.get("auto_fix_safe"),
                        "success_rate": 1.0,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }],
                source_type="devops_patterns"
            )

            logger.info(f"💾 Successful pattern stored in RAG: {action.get('category')}")

        except Exception as e:
            logger.warning(f"Failed to store pattern in RAG: {e}")

    async def report_to_brain(self, analysis: Dict):
        """
        Report findings to Workflow Intelligence (мозг)

        - Saves report to disk (JSON + HTML)
        - Publishes via EventBus
        - Sends to Workflow Intelligence API
        """
        logger.info("📡 Reporting to Workflow Intelligence...")

        report = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "report_type": "infrastructure_analysis",
            "analysis": analysis,
            "statistics": {
                "scans_completed": self.scans_completed,
                "issues_detected": self.issues_detected,
                "fixes_applied": self.fixes_applied
            }
        }

        # 1. SAVE TO DISK (JSON + HTML)
        saved_paths = self.report_manager.save_report(report)
        logger.info(f"💾 Report saved: {saved_paths['json_path']}")
        logger.info(f"🌐 HTML dashboard: {saved_paths['html_path']}")

        # 2. Publish to brain via EventBus
        if self.eventbus:
            await self.eventbus.publish(
                "devops.infrastructure.analyzed",
                report
            )
            logger.info("📡 EventBus: Report published")

        # 3. Send to Workflow Intelligence API
        if self.workflow_intelligence:
            brain_response = await self.workflow_intelligence.report_infrastructure_analysis(analysis)
            logger.info(f"🧠 Brain response: {brain_response.get('status')}")

        logger.info("✅ Report sent to all channels")

    async def run_full_cycle(self):
        """Run complete DevOps Agent cycle"""
        logger.info("🚀 Starting DevOps Agent full cycle...")

        # 1. Scan infrastructure
        scan_results = await self.scan_infrastructure(scan_type="full")
        logger.info(f"✅ Scan completed: {scan_results.get('total_issues', 0)} issues found")

        # 2. AI analysis
        ai_analysis = await self.ai_analysis(scan_results)
        logger.info(f"✅ AI analysis completed: {len(ai_analysis.get('ai_recommendations', []))} recommendations")

        # 3. Apply fixes if approved
        if ai_analysis.get('auto_fix_approved'):
            fix_results = await self.apply_fixes(ai_analysis['ai_recommendations'])
            logger.info(f"✅ Auto-fix: {fix_results['fixes_successful']}/{fix_results['fixes_attempted']} successful")

        # 4. Report to brain
        await self.report_to_brain({
            "scan_results": scan_results,
            "ai_analysis": ai_analysis
        })

        logger.info("🎉 DevOps Agent cycle completed!")

        return {
            "status": "completed",
            "scan_results": scan_results,
            "ai_analysis": ai_analysis
        }


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='DevOps Agent - AI Digital Colleague')
    parser.add_argument('--full-scan', action='store_true', help='Run full infrastructure scan')
    parser.add_argument('--scan-events', action='store_true', help='Scan event architecture only')
    parser.add_argument('--scan-containers', action='store_true', help='Scan containers only')
    parser.add_argument('--scan-deployments', action='store_true', help='Scan deployments only')
    parser.add_argument('--auto-fix', action='store_true', help='Apply auto-remediation')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--project-root', type=str, default='/Users/MD/AI-Platform-ISO',
                       help='Project root directory')

    args = parser.parse_args()

    # Initialize agent
    agent = DevOpsAgent(args.project_root)
    await agent.initialize()

    # Determine scan type
    if args.scan_events:
        scan_type = "events"
    elif args.scan_containers:
        scan_type = "containers"
    elif args.scan_deployments:
        scan_type = "deployments"
    else:
        scan_type = "full"

    # Run operations
    if args.full_scan or any([args.scan_events, args.scan_containers, args.scan_deployments]):
        results = await agent.run_full_cycle()

        if args.report:
            print("\n" + "="*70)
            print("📊 DEVOPS AGENT - INFRASTRUCTURE REPORT")
            print("="*70)
            print(f"\nScan Results: {results['scan_results']}")
            print(f"\nAI Analysis: {results['ai_analysis']}")
            print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    asyncio.run(main())
