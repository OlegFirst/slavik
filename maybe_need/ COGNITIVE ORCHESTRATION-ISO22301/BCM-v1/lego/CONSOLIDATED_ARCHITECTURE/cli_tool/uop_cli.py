#!/usr/bin/env python3
"""
Universal Orchestration Platform CLI Tool
Command-line interface for the AI-Enhanced Universal Orchestration Platform
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
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

class UniversalOrchestratorCLI:
    """Command-line interface for Universal Orchestration Platform"""

    def __init__(self):
        self.analyzer = ProjectAnalyzer()
        self.classifier = ArchitectureClassifier()
        self.generator = CodeGenerator()
        self.visualizer = DiagramGenerator()
        self.claude_generator = None
        self.workflow_optimizer = None

    async def analyze_command(self, args) -> Dict[str, Any]:
        """Handle analyze command"""

        print(f"🔍 Analyzing project: {args.input}")

        # Determine input type
        input_path = Path(args.input)

        if input_path.is_dir():
            # Direct directory analysis
            analysis = await self.analyzer.analyze(input_path)
        elif input_path.is_file() and input_path.suffix == '.zip':
            # ZIP file analysis
            with tempfile.TemporaryDirectory() as temp_dir:
                shutil.unpack_archive(str(input_path), temp_dir)
                analysis = await self.analyzer.analyze(Path(temp_dir))
        else:
            raise ValueError(f"Unsupported input type: {input_path}")

        # Classify architecture
        classification = await self.classifier.classify(analysis)

        # Enhance with workflow optimization if available
        if args.optimizer_url:
            try:
                self.workflow_optimizer = WorkflowOptimizerClient(args.optimizer_url)
                classification = await self.workflow_optimizer.optimize_architecture_workflow(classification)
                print("✅ Enhanced with ML workflow optimization")
            except Exception as e:
                print(f"⚠️ Workflow optimization failed: {e}")

        result = {
            "analysis": analysis,
            "classification": classification,
            "summary": {
                "files_analyzed": len(analysis.get("files", [])),
                "languages_detected": analysis.get("languages", []),
                "architecture_pattern": classification.get("pattern", "unknown"),
                "complexity": classification.get("complexity", "unknown")
            }
        }

        # Save results if requested
        if args.output:
            output_path = Path(args.output)
            output_path.mkdir(parents=True, exist_ok=True)

            analysis_file = output_path / "analysis_result.json"
            analysis_file.write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(f"📄 Analysis saved to: {analysis_file}")

        return result

    async def generate_command(self, args) -> Dict[str, Any]:
        """Handle generate command"""

        print(f"🎨 Generating architecture code for: {args.input}")

        # First analyze the project
        analysis_result = await self.analyze_command(args)
        classification = analysis_result["classification"]

        # Initialize AI generator if enabled
        if args.ai_enabled:
            try:
                self.claude_generator = ClaudeCodeGenerator()
                generated_files = await self.claude_generator.generate_intelligent_code(
                    classification
                )
                generation_method = "AI-powered"
                print("✅ Used AI-powered code generation")
            except Exception as e:
                print(f"⚠️ AI generation failed, using template fallback: {e}")
                generated_files = await self.generator.generate(classification)
                generation_method = "Template-based"
        else:
            generated_files = await self.generator.generate(classification)
            generation_method = "Template-based"
            print("✅ Used template-based code generation")

        # Save generated files
        output_path = Path(args.output) if args.output else Path.cwd() / "orchestrator_output"
        output_path.mkdir(parents=True, exist_ok=True)

        saved_files = []
        for filename, content in generated_files.items():
            file_path = output_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            saved_files.append(str(file_path))
            print(f"📝 Generated: {file_path}")

        result = {
            "generated_files": generated_files,
            "saved_files": saved_files,
            "generation_method": generation_method,
            "generation_type": args.generation_type,
            "output_directory": str(output_path),
            "analysis": analysis_result
        }

        # Save generation summary
        summary_file = output_path / "generation_summary.json"
        summary_file.write_text(json.dumps({
            "generation_method": generation_method,
            "generation_type": args.generation_type,
            "files_generated": len(generated_files),
            "saved_files": saved_files
        }, indent=2), encoding='utf-8')

        print(f"📋 Generation summary saved to: {summary_file}")

        return result

    async def visualize_command(self, args) -> Dict[str, Any]:
        """Handle visualize command"""

        print(f"📊 Creating architecture visualization for: {args.input}")

        # Analyze project first
        analysis_result = await self.analyze_command(args)
        classification = analysis_result["classification"]

        # Generate visualization
        mermaid_diagram = await self.visualizer.generate(classification)

        # Save diagrams
        output_path = Path(args.output) if args.output else Path.cwd() / "orchestrator_output"
        output_path.mkdir(parents=True, exist_ok=True)

        # Save Mermaid source
        mermaid_file = output_path / "architecture_diagram.mmd"
        mermaid_file.write_text(mermaid_diagram, encoding='utf-8')
        print(f"📝 Mermaid diagram saved to: {mermaid_file}")

        result = {
            "diagram_files": [str(mermaid_file)],
            "mermaid_source": mermaid_diagram,
            "output_directory": str(output_path),
            "analysis": analysis_result
        }

        return result

    async def full_command(self, args) -> Dict[str, Any]:
        """Handle full orchestration command"""

        print("🚀 Starting full orchestration process...")
        print("=" * 60)

        try:
            # Step 1: Analyze
            print("\n📍 Step 1: Project Analysis")
            analysis_result = await self.analyze_command(args)

            print("\n📍 Step 2: Code Generation")
            generation_result = await self.generate_command(args)

            print("\n📍 Step 3: Visualization")
            visualization_result = await self.visualize_command(args)

            print("\n📍 Step 4: Creating Summary Report")
            report_result = await self._create_full_report(
                analysis_result, generation_result, visualization_result, args
            )

            print("\n" + "=" * 60)
            print("✅ Full orchestration completed successfully!")

            return {
                "status": "success",
                "analysis": analysis_result,
                "generation": generation_result,
                "visualization": visualization_result,
                "report": report_result,
                "output_directory": args.output or str(Path.cwd() / "orchestrator_output")
            }

        except Exception as e:
            print(f"\n❌ Orchestration failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "output_directory": args.output or str(Path.cwd() / "orchestrator_output")
            }

    async def _create_full_report(self, analysis_result, generation_result, visualization_result, args):
        """Create comprehensive orchestration report"""

        output_path = Path(args.output) if args.output else Path.cwd() / "orchestrator_output"
        classification = analysis_result["classification"]

        # Get workflow insights if available
        workflow_insights = {}
        if args.optimizer_url and self.workflow_optimizer:
            try:
                workflow_insights = await self.workflow_optimizer.get_workflow_insights(classification)
            except Exception:
                pass

        report_content = f"""# 🏗️ Universal Orchestration Platform - CLI Report

## Command Executed
```bash
{' '.join(sys.argv)}
```

## Project Analysis Summary
- **Input**: {args.input}
- **Files Analyzed**: {analysis_result['summary']['files_analyzed']}
- **Languages Detected**: {', '.join(analysis_result['summary']['languages_detected'])}
- **Architecture Pattern**: {analysis_result['summary']['architecture_pattern']}
- **Complexity**: {analysis_result['summary']['complexity']}

## Code Generation Results
- **Generation Method**: {generation_result['generation_method']}
- **Generation Type**: {generation_result['generation_type']}
- **Files Generated**: {len(generation_result['generated_files'])}

### Generated Files:
{chr(10).join(f"- {Path(f).name}" for f in generation_result['saved_files'])}

## Architecture Visualization
- **Diagrams Created**: {len(visualization_result['diagram_files'])}

### Diagram Files:
{chr(10).join(f"- {Path(f).name}" for f in visualization_result['diagram_files'])}

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
All generated files are available in: `{output_path}`

## CLI Usage Summary
- **Command**: {' '.join(sys.argv)}
- **AI Enabled**: {args.ai_enabled if hasattr(args, 'ai_enabled') else 'N/A'}
- **Workflow Optimizer**: {args.optimizer_url if args.optimizer_url else 'Not used'}

## Next Steps
1. Review generated architecture code in the output directory
2. Examine visualization diagrams for architecture overview
3. Consider implementing workflow recommendations
4. Test generated code in your development environment
5. Customize generated files as needed for your specific requirements

---
*Report generated by Universal Orchestration Platform CLI*
*Version: 1.0.0*
"""

        # Save report
        report_path = output_path / "CLI_ORCHESTRATION_REPORT.md"
        report_path.write_text(report_content, encoding='utf-8')
        print(f"📋 Full report saved to: {report_path}")

        return {
            "report_path": str(report_path),
            "report_content": report_content,
            "workflow_insights": workflow_insights
        }

    async def cleanup(self):
        """Cleanup resources"""
        if self.workflow_optimizer:
            await self.workflow_optimizer.close()

def create_parser():
    """Create argument parser for CLI"""

    parser = argparse.ArgumentParser(
        description="Universal Orchestration Platform CLI - AI-Enhanced Architecture Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze ./my-project
  %(prog)s generate ./my-project --output ./output --ai
  %(prog)s visualize ./my-project.zip
  %(prog)s full ./my-project --type modernization --ai --optimizer-url http://localhost:8080
  %(prog)s analyze ./project --output ./results --optimizer-url http://localhost:8080
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze project structure and architecture')
    analyze_parser.add_argument('input', help='Project directory or ZIP file path')
    analyze_parser.add_argument('--output', '-o', help='Output directory for results')
    analyze_parser.add_argument('--optimizer-url', help='AI Workflow Optimizer service URL')

    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate architecture code')
    generate_parser.add_argument('input', help='Project directory or ZIP file path')
    generate_parser.add_argument('--output', '-o', help='Output directory for generated files')
    generate_parser.add_argument('--type', dest='generation_type',
                                choices=['enhancement', 'migration', 'modernization'],
                                default='enhancement', help='Type of generation to perform')
    generate_parser.add_argument('--ai', dest='ai_enabled', action='store_true',
                                help='Enable AI-powered code generation')
    generate_parser.add_argument('--optimizer-url', help='AI Workflow Optimizer service URL')

    # Visualize command
    visualize_parser = subparsers.add_parser('visualize', help='Create architecture visualization')
    visualize_parser.add_argument('input', help='Project directory or ZIP file path')
    visualize_parser.add_argument('--output', '-o', help='Output directory for diagrams')
    visualize_parser.add_argument('--optimizer-url', help='AI Workflow Optimizer service URL')

    # Full command
    full_parser = subparsers.add_parser('full', help='Full orchestration: analyze + generate + visualize')
    full_parser.add_argument('input', help='Project directory or ZIP file path')
    full_parser.add_argument('--output', '-o', help='Output directory for all results')
    full_parser.add_argument('--type', dest='generation_type',
                            choices=['enhancement', 'migration', 'modernization'],
                            default='enhancement', help='Type of generation to perform')
    full_parser.add_argument('--ai', dest='ai_enabled', action='store_true',
                            help='Enable AI-powered code generation')
    full_parser.add_argument('--optimizer-url', help='AI Workflow Optimizer service URL')

    return parser

async def main():
    """Main CLI entry point"""

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = UniversalOrchestratorCLI()

    try:
        if args.command == 'analyze':
            result = await cli.analyze_command(args)
            print(f"\n✅ Analysis completed!")
            print(f"Files analyzed: {result['summary']['files_analyzed']}")
            print(f"Languages: {', '.join(result['summary']['languages_detected'])}")
            print(f"Pattern: {result['summary']['architecture_pattern']}")

        elif args.command == 'generate':
            result = await cli.generate_command(args)
            print(f"\n✅ Generation completed!")
            print(f"Method: {result['generation_method']}")
            print(f"Files generated: {len(result['generated_files'])}")
            print(f"Output: {result['output_directory']}")

        elif args.command == 'visualize':
            result = await cli.visualize_command(args)
            print(f"\n✅ Visualization completed!")
            print(f"Diagrams created: {len(result['diagram_files'])}")
            print(f"Output: {result['output_directory']}")

        elif args.command == 'full':
            result = await cli.full_command(args)
            if result['status'] == 'success':
                print(f"\n🎉 Full orchestration completed successfully!")
                print(f"Output directory: {result['output_directory']}")
            else:
                print(f"\n❌ Orchestration failed: {result['error']}")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        await cli.cleanup()

if __name__ == "__main__":
    asyncio.run(main())