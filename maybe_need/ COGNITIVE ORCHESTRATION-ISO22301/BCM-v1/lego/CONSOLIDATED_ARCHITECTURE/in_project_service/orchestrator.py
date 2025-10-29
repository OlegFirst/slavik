#!/usr/bin/env python3
"""
In-Project Orchestrator Service
Embeddable service for direct integration into user projects
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from analyzer.project_analyzer import ProjectAnalyzer
from analyzer.architecture_classifier import ArchitectureClassifier
from generator.code_generator import CodeGenerator
from visualizer.diagram_generator import DiagramGenerator
from ai_integration.claude_generator import ClaudeCodeGenerator
from ai_integration.workflow_optimizer_client import WorkflowOptimizerClient

class InProjectOrchestrator:
    """
    Embeddable orchestrator service for in-project use

    Usage:
        from orchestrator import InProjectOrchestrator

        orchestrator = InProjectOrchestrator()
        result = await orchestrator.analyze_and_generate()
    """

    def __init__(self,
                 project_root: Optional[Path] = None,
                 output_dir: Optional[Path] = None,
                 ai_enabled: bool = True,
                 workflow_optimizer_url: Optional[str] = None):
        """
        Initialize in-project orchestrator

        Args:
            project_root: Root directory of project (defaults to current dir)
            output_dir: Output directory for generated files (defaults to ./orchestrator_output)
            ai_enabled: Whether to use AI generation (Claude)
            workflow_optimizer_url: URL for workflow optimizer service
        """
        self.project_root = project_root or Path.cwd()
        self.output_dir = output_dir or self.project_root / "orchestrator_output"
        self.ai_enabled = ai_enabled

        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)

        # Initialize components
        self.analyzer = ProjectAnalyzer()
        self.classifier = ArchitectureClassifier()
        self.generator = CodeGenerator()
        self.visualizer = DiagramGenerator()

        # Initialize AI components if enabled
        if self.ai_enabled:
            self.claude_generator = ClaudeCodeGenerator()
            if workflow_optimizer_url:
                self.workflow_optimizer = WorkflowOptimizerClient(workflow_optimizer_url)
            else:
                self.workflow_optimizer = None

    async def analyze_current_project(self) -> Dict[str, Any]:
        """Analyze current project structure and architecture"""

        print(f"🔍 Analyzing project at: {self.project_root}")

        # Analyze project structure
        analysis = await self.analyzer.analyze(self.project_root)

        # Classify architecture
        classification = await self.classifier.classify(analysis)

        # Enhance with workflow optimization if available
        if self.ai_enabled and self.workflow_optimizer:
            try:
                classification = await self.workflow_optimizer.optimize_architecture_workflow(classification)
                print("✅ Enhanced with ML workflow optimization")
            except Exception as e:
                print(f"⚠️ Workflow optimization unavailable: {e}")

        return {
            "analysis": analysis,
            "classification": classification,
            "project_root": str(self.project_root),
            "analyzed_files": len(analysis.get("files", [])),
            "detected_languages": analysis.get("languages", []),
            "architecture_pattern": classification.get("pattern", "unknown")
        }

    async def generate_architecture_code(self,
                                       analysis_result: Dict[str, Any],
                                       generation_type: str = "enhancement") -> Dict[str, Any]:
        """
        Generate architecture code based on analysis

        Args:
            analysis_result: Result from analyze_current_project()
            generation_type: 'enhancement', 'migration', 'modernization'
        """

        print(f"🎨 Generating {generation_type} code...")

        classification = analysis_result["classification"]

        # Choose generation method
        if self.ai_enabled:
            try:
                # Use AI generation
                generated_files = await self.claude_generator.generate_intelligent_code(
                    classification
                )
                generation_method = "AI-powered"
                print("✅ Used AI-powered code generation")
            except Exception as e:
                print(f"⚠️ AI generation failed, using template fallback: {e}")
                # Fallback to template generation
                generated_files = await self.generator.generate(classification)
                generation_method = "Template-based"
        else:
            # Use template generation
            generated_files = await self.generator.generate(classification)
            generation_method = "Template-based"
            print("✅ Used template-based code generation")

        # Save generated files to output directory
        saved_files = []
        for filename, content in generated_files.items():
            output_path = self.output_dir / filename

            # Create subdirectories if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            output_path.write_text(content, encoding='utf-8')
            saved_files.append(str(output_path))
            print(f"📝 Saved: {output_path}")

        return {
            "generated_files": generated_files,
            "saved_files": saved_files,
            "generation_method": generation_method,
            "generation_type": generation_type,
            "output_directory": str(self.output_dir)
        }

    async def create_architecture_diagram(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create architecture visualization diagram"""

        print("📊 Creating architecture diagram...")

        classification = analysis_result["classification"]

        # Generate diagram
        mermaid_diagram = await self.visualizer.generate(classification)

        # Save Mermaid diagram
        mermaid_path = self.output_dir / "architecture_diagram.mmd"
        mermaid_path.write_text(mermaid_diagram, encoding='utf-8')
        print(f"🎨 Saved diagram: {mermaid_path}")

        return {
            "diagram_files": [str(mermaid_path)],
            "mermaid_source": mermaid_diagram,
            "output_directory": str(self.output_dir)
        }

    async def full_orchestration(self, generation_type: str = "enhancement") -> Dict[str, Any]:
        """
        Complete orchestration: analyze + generate + visualize

        Args:
            generation_type: 'enhancement', 'migration', 'modernization'
        """

        print("🚀 Starting full orchestration process...")
        print("=" * 60)

        try:
            # Step 1: Analyze current project
            analysis_result = await self.analyze_current_project()

            print("\n" + "=" * 60)

            # Step 2: Generate architecture code
            generation_result = await self.generate_architecture_code(
                analysis_result, generation_type
            )

            print("\n" + "=" * 60)

            # Step 3: Create visualization
            diagram_result = await self.create_architecture_diagram(analysis_result)

            print("\n" + "=" * 60)

            # Create summary report
            summary = await self._create_summary_report(
                analysis_result, generation_result, diagram_result
            )

            print("✅ Orchestration completed successfully!")
            print(f"📁 All outputs saved to: {self.output_dir}")

            return {
                "status": "success",
                "analysis": analysis_result,
                "generation": generation_result,
                "visualization": diagram_result,
                "summary": summary,
                "output_directory": str(self.output_dir)
            }

        except Exception as e:
            print(f"❌ Orchestration failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "output_directory": str(self.output_dir)
            }

    async def _create_summary_report(self,
                                   analysis_result: Dict[str, Any],
                                   generation_result: Dict[str, Any],
                                   diagram_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive summary report"""

        classification = analysis_result["classification"]

        # Get workflow insights if available
        workflow_insights = {}
        if self.ai_enabled and self.workflow_optimizer:
            try:
                workflow_insights = await self.workflow_optimizer.get_workflow_insights(classification)
            except Exception:
                pass

        # Create report content
        report_content = f"""# 🏗️ Architecture Orchestration Report

## Project Analysis Summary
- **Project Root**: {analysis_result['project_root']}
- **Files Analyzed**: {analysis_result['analyzed_files']}
- **Languages Detected**: {', '.join(analysis_result['detected_languages'])}
- **Architecture Pattern**: {analysis_result['architecture_pattern']}

## Generated Artifacts
- **Generation Method**: {generation_result['generation_method']}
- **Generation Type**: {generation_result['generation_type']}
- **Files Generated**: {len(generation_result['generated_files'])}

### Generated Files:
{chr(10).join(f"- {f}" for f in generation_result['saved_files'])}

## Architecture Visualization
- **Diagrams Created**: {len(diagram_result['diagram_files'])}

### Diagram Files:
{chr(10).join(f"- {f}" for f in diagram_result['diagram_files'])}

## Workflow Optimization Insights
"""

        if workflow_insights:
            report_content += f"""
- **Deployment Complexity**: {workflow_insights.get('deployment_complexity', 'N/A')} out of 3
- **Estimated Deployment Time**: {workflow_insights.get('estimated_deployment_time', 'N/A')} minutes
- **Resource Requirements**: {workflow_insights.get('resource_requirements', {})}

### ML-Generated Recommendations:
{chr(10).join(f"- {rec}" for rec in workflow_insights.get('workflow_recommendations', []))}
"""
        else:
            report_content += "\n- Workflow optimization not available\n"

        report_content += f"""
## Output Location
All generated files are available in: `{self.output_dir}`

## Next Steps
1. Review generated architecture code
2. Examine visualization diagrams
3. Consider implementing workflow recommendations
4. Test generated code in your environment

---
*Report generated by Universal Orchestration Platform*
*Timestamp: {asyncio.get_event_loop().time()}*
"""

        # Save report
        report_path = self.output_dir / "ORCHESTRATION_REPORT.md"
        report_path.write_text(report_content, encoding='utf-8')

        print(f"📋 Summary report saved: {report_path}")

        return {
            "report_path": str(report_path),
            "report_content": report_content,
            "workflow_insights": workflow_insights
        }

    async def quick_analysis(self) -> Dict[str, Any]:
        """Quick project analysis without code generation"""

        print("⚡ Quick analysis mode...")

        analysis_result = await self.analyze_current_project()

        # Create quick summary
        classification = analysis_result["classification"]
        summary = {
            "project_overview": {
                "files_count": analysis_result["analyzed_files"],
                "languages": analysis_result["detected_languages"],
                "pattern": analysis_result["architecture_pattern"],
                "complexity": classification.get("complexity", "unknown")
            },
            "recommendations": classification.get("recommendations", []),
            "suggested_improvements": classification.get("suggested_improvements", [])
        }

        # Save quick summary
        summary_path = self.output_dir / "quick_analysis.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')

        print(f"💾 Quick analysis saved: {summary_path}")

        return {
            "status": "success",
            "summary": summary,
            "analysis": analysis_result,
            "output_file": str(summary_path)
        }

    async def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'workflow_optimizer') and self.workflow_optimizer:
            await self.workflow_optimizer.close()


# Convenience functions for direct usage
async def analyze_project(project_path: str = None) -> Dict[str, Any]:
    """Convenience function for quick project analysis"""
    orchestrator = InProjectOrchestrator(
        project_root=Path(project_path) if project_path else None
    )
    try:
        return await orchestrator.quick_analysis()
    finally:
        await orchestrator.cleanup()

async def generate_architecture(project_path: str = None,
                              generation_type: str = "enhancement") -> Dict[str, Any]:
    """Convenience function for full architecture generation"""
    orchestrator = InProjectOrchestrator(
        project_root=Path(project_path) if project_path else None
    )
    try:
        return await orchestrator.full_orchestration(generation_type)
    finally:
        await orchestrator.cleanup()

# CLI interface for direct execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="In-Project Orchestration Service")
    parser.add_argument("--mode", choices=["analyze", "generate", "full"],
                       default="full", help="Operation mode")
    parser.add_argument("--project", type=str, help="Project root path")
    parser.add_argument("--output", type=str, help="Output directory")
    parser.add_argument("--type", choices=["enhancement", "migration", "modernization"],
                       default="enhancement", help="Generation type")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI generation")
    parser.add_argument("--optimizer-url", type=str, help="Workflow optimizer URL")

    args = parser.parse_args()

    async def main():
        orchestrator = InProjectOrchestrator(
            project_root=Path(args.project) if args.project else None,
            output_dir=Path(args.output) if args.output else None,
            ai_enabled=not args.no_ai,
            workflow_optimizer_url=args.optimizer_url
        )

        try:
            if args.mode == "analyze":
                result = await orchestrator.quick_analysis()
            elif args.mode == "generate":
                analysis = await orchestrator.analyze_current_project()
                result = await orchestrator.generate_architecture_code(analysis, args.type)
            else:  # full
                result = await orchestrator.full_orchestration(args.type)

            print("\n" + "=" * 60)
            print("🎉 Operation completed!")
            print(f"Status: {result.get('status', 'success')}")
            if 'output_directory' in result:
                print(f"Output: {result['output_directory']}")

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await orchestrator.cleanup()

    asyncio.run(main())