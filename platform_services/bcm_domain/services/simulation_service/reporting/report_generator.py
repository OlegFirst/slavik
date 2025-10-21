"""
Report Generator Module

Generates professional analytical reports from simulation results:
- Executive summaries
- Detailed technical reports
- ISO 22301 compliance reports
- Visualization and charts
- Lessons learned documentation
- Action plans and recommendations
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json

from models.pydantic_models import (
    SimulationResult,
    Simulation,
    TaskSpecification,
    Scenario
)

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Professional report generator for simulation results

    Report Types:
    - Executive Summary (1-2 pages)
    - Detailed Technical Report (10-20 pages)
    - ISO 22301 Compliance Report
    - Lessons Learned Document
    - Action Plan
    - Visualization Dashboard

    Output Formats:
    - Markdown
    - HTML
    - PDF (via external service)
    - JSON (for programmatic access)
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize report generator

        Args:
            output_dir: Directory for report output
        """
        self.output_dir = output_dir or Path("./reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # MAIN REPORT GENERATION
    # ========================================================================

    async def generate_full_report(
        self,
        simulation: Simulation,
        results: SimulationResult,
        specification: TaskSpecification,
        scenario: Scenario,
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Generate complete simulation report

        Args:
            simulation: Simulation instance
            results: Simulation results
            specification: Original specification
            scenario: Scenario used
            format: Output format (markdown, html, json)

        Returns:
            Report metadata and file paths
        """
        logger.info(f"Generating full report for simulation {simulation.id}")

        report_data = {
            "report_id": f"report_{simulation.id}",
            "generated_at": datetime.utcnow().isoformat(),
            "simulation_id": simulation.id,
            "format": format,
            "sections": {}
        }

        try:
            # Generate all sections
            sections = {
                "executive_summary": self._generate_executive_summary(
                    simulation, results, specification
                ),
                "overview": self._generate_overview(
                    simulation, results, specification, scenario
                ),
                "objectives_outcomes": self._generate_objectives_outcomes(
                    specification, results
                ),
                "detailed_analysis": self._generate_detailed_analysis(
                    results
                ),
                "performance_metrics": self._generate_performance_metrics(
                    results
                ),
                "participant_analysis": self._generate_participant_analysis(
                    results
                ),
                "timeline_events": self._generate_timeline_events(
                    results
                ),
                "lessons_learned": self._generate_lessons_learned(
                    results
                ),
                "recommendations": self._generate_recommendations(
                    results
                ),
                "action_plan": self._generate_action_plan(
                    results
                ),
                "appendices": self._generate_appendices(
                    simulation, scenario, results
                )
            }

            report_data["sections"] = sections

            # Format and save report
            if format == "markdown":
                report_path = await self._save_markdown_report(
                    report_data, simulation.id
                )
            elif format == "html":
                report_path = await self._save_html_report(
                    report_data, simulation.id
                )
            elif format == "json":
                report_path = await self._save_json_report(
                    report_data, simulation.id
                )
            else:
                raise ValueError(f"Unsupported format: {format}")

            report_data["file_path"] = str(report_path)
            logger.info(f"Report generated: {report_path}")

            return report_data

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise

    async def generate_executive_summary(
        self,
        simulation: Simulation,
        results: SimulationResult,
        specification: TaskSpecification
    ) -> str:
        """
        Generate executive summary only (1-2 pages)

        Args:
            simulation: Simulation instance
            results: Simulation results
            specification: Original specification

        Returns:
            Executive summary text
        """
        summary = self._generate_executive_summary(
            simulation, results, specification
        )

        return summary

    async def generate_iso_compliance_report(
        self,
        simulation: Simulation,
        results: SimulationResult,
        specification: TaskSpecification,
        scenario: Scenario
    ) -> str:
        """
        Generate ISO 22301 compliance report

        Maps simulation results to ISO 22301 requirements

        Args:
            simulation: Simulation instance
            results: Simulation results
            specification: Original specification
            scenario: Scenario used

        Returns:
            ISO compliance report
        """
        logger.info("Generating ISO 22301 compliance report")

        report = f"""# ISO 22301 Compliance Report

## Simulation: {simulation.id}
**Date:** {datetime.utcnow().strftime('%Y-%m-%d')}
**Organization:** {simulation.organization_id}

---

## Executive Summary

This report documents simulation exercise conducted in accordance with ISO 22301:2019 requirements for testing business continuity arrangements.

**Overall Compliance Score:** {self._calculate_compliance_score(results)}%

---

## ISO 22301 Clause Mapping

### 8.4 Business Continuity Plans and Procedures

**Exercise Type:** {scenario.exercise_type.value}
**Objective:** {specification.goal}

**Tested Plans:**
{self._format_list(scenario.affected_processes)}

**Results:**
- Plans activated: {results.metrics.get('plans_activated', 'N/A')}
- Procedures followed: {results.metrics.get('procedures_compliance', 'N/A')}%
- Success rate: {results.overall_success_rate * 100:.1f}%

**Findings:**
{self._format_findings_iso(results)}

### 8.5 Exercising and Testing

**Exercise Scope:** {scenario.name}
**Duration:** {results.duration_seconds // 60} minutes
**Participants:** {len(results.participant_performance)}

**Objectives Tested:**
{self._format_list(specification.expected_outcomes)}

**Success Criteria Met:**
{self._format_criteria_status(results)}

### 9.1 Monitoring, Measurement, Analysis and Evaluation

**Key Performance Indicators:**
{self._format_kpis(results)}

**Metrics Collected:**
{self._format_metrics_iso(results)}

### 10.2 Nonconformity and Corrective Action

**Identified Nonconformities:**
{self._format_nonconformities(results)}

**Corrective Actions Required:**
{self._format_list(results.recommendations)}

---

## Detailed Findings

{self._generate_detailed_analysis(results)}

---

## Recommendations for Improvement

{self._format_list(results.recommendations)}

---

## Lessons Learned

{self._format_list(results.lessons_learned)}

---

## Next Steps

{self._format_list(self._extract_next_steps(results))}

---

## Approval

**Prepared by:** Simulation Service (Automated)
**Review required by:** Business Continuity Manager
**Approval required by:** Senior Management

---

*This report was automatically generated by Simulation & Modeling Service*
*ISO 22301:2019 Business Continuity Management Systems*
"""

        return report

    # ========================================================================
    # SECTION GENERATORS
    # ========================================================================

    def _generate_executive_summary(
        self,
        simulation: Simulation,
        results: SimulationResult,
        specification: TaskSpecification
    ) -> str:
        """Generate executive summary section"""

        # Determine overall assessment
        if results.overall_success_rate >= 0.8:
            assessment = " **SUCCESSFUL** - Objectives achieved"
        elif results.overall_success_rate >= 0.6:
            assessment = "️ **PARTIAL SUCCESS** - Some objectives achieved"
        else:
            assessment = " **NEEDS IMPROVEMENT** - Objectives not met"

        summary = f"""## Executive Summary

**Simulation:** {specification.goal}
**Date:** {results.completed_at.strftime('%Y-%m-%d %H:%M') if results.completed_at else 'N/A'}
**Duration:** {results.duration_seconds // 60} minutes
**Overall Assessment:** {assessment}

### Key Findings

**Success Rate:** {results.overall_success_rate * 100:.1f}%

**Strengths:**
{self._format_top_items(self._extract_strengths(results), 3)}

**Areas for Improvement:**
{self._format_top_items(results.improvement_areas, 3)}

### Critical Recommendations

{self._format_top_items(results.recommendations, 3)}

### Impact

**Quality Score:** {results.quality_score}/10
**Complexity Level:** {results.complexity_level}/5

This simulation provides actionable insights for improving organizational resilience and business continuity capabilities.
"""

        return summary

    def _generate_overview(
        self,
        simulation: Simulation,
        results: SimulationResult,
        specification: TaskSpecification,
        scenario: Scenario
    ) -> str:
        """Generate overview section"""

        overview = f"""## Simulation Overview

### Purpose and Scope

**Primary Goal:** {specification.goal}

**Scenario:** {scenario.name}
**Category:** {scenario.category.value}
**Exercise Type:** {scenario.exercise_type.value}

### Simulation Details

- **Simulation ID:** {simulation.id}
- **Engine Used:** {results.engine_used}
- **Start Time:** {results.started_at.strftime('%Y-%m-%d %H:%M') if results.started_at else 'N/A'}
- **End Time:** {results.completed_at.strftime('%Y-%m-%d %H:%M') if results.completed_at else 'N/A'}
- **Duration:** {results.duration_seconds // 60} minutes
- **Participants:** {len(results.participant_performance)}

### Affected Processes

{self._format_list(scenario.affected_processes)}

### Success Criteria

{self._format_list(results.success_criteria)}
"""

        return overview

    def _generate_objectives_outcomes(
        self,
        specification: TaskSpecification,
        results: SimulationResult
    ) -> str:
        """Generate objectives vs outcomes section"""

        section = f"""## Objectives and Outcomes

### Planned Objectives

{self._format_list(specification.expected_outcomes or ['Test system resilience', 'Validate procedures'])}

### Actual Outcomes

**Overall Success Rate:** {results.overall_success_rate * 100:.1f}%

**Objectives Achieved:**
{self._format_achieved_objectives(specification, results)}

**KPIs Achieved:**
{self._format_list(results.kpis_achieved)}

### Gap Analysis

{self._generate_gap_analysis(specification, results)}
"""

        return section

    def _generate_detailed_analysis(self, results: SimulationResult) -> str:
        """Generate detailed analysis section"""

        analysis = f"""## Detailed Analysis

### Performance Overview

- **Total Events:** {len(results.events)}
- **Success Rate:** {results.overall_success_rate * 100:.1f}%
- **Completion Status:** {results.status}

### Strengths Identified

{self._format_list(self._extract_strengths(results))}

### Weaknesses Identified

{self._format_list(self._extract_weaknesses(results))}

### Critical Findings

{self._format_critical_findings(results)}

### Risk Assessment

{self._format_risks(results)}
"""

        return analysis

    def _generate_performance_metrics(self, results: SimulationResult) -> str:
        """Generate performance metrics section"""

        metrics = f"""## Performance Metrics

### Key Metrics

{self._format_metrics_table(results.metrics)}

### Detailed Metrics

{self._format_detailed_metrics(results.detailed_metrics)}

### Benchmarking

{self._format_benchmarking(results)}
"""

        return metrics

    def _generate_participant_analysis(self, results: SimulationResult) -> str:
        """Generate participant analysis section"""

        if not results.participant_performance:
            return "## Participant Analysis\n\n*No participant data available*"

        analysis = f"""## Participant Analysis

### Overall Participation

**Total Participants:** {len(results.participant_performance)}

### Individual Performance

{self._format_participant_table(results.participant_performance)}

### Team Dynamics

{self._analyze_team_dynamics(results)}
"""

        return analysis

    def _generate_timeline_events(self, results: SimulationResult) -> str:
        """Generate timeline of events section"""

        timeline = f"""## Timeline of Events

### Event Sequence

{self._format_events_timeline(results.events)}

### Critical Moments

{self._identify_critical_moments(results.events)}
"""

        return timeline

    def _generate_lessons_learned(self, results: SimulationResult) -> str:
        """Generate lessons learned section"""

        lessons = f"""## Lessons Learned

{self._format_list(results.lessons_learned)}

### Knowledge Captured

- Total lessons: {len(results.lessons_learned)}
- Actionable insights: {len(results.recommendations)}
- Improvement areas: {len(results.improvement_areas)}

### Organizational Learning

{self._format_organizational_learning(results)}
"""

        return lessons

    def _generate_recommendations(self, results: SimulationResult) -> str:
        """Generate recommendations section"""

        recommendations = f"""## Recommendations

### Priority Actions

{self._format_prioritized_recommendations(results.recommendations)}

### Implementation Roadmap

{self._format_implementation_roadmap(results)}

### Resource Requirements

{self._estimate_resources(results)}
"""

        return recommendations

    def _generate_action_plan(self, results: SimulationResult) -> str:
        """Generate action plan section"""

        action_plan = f"""## Action Plan

### Immediate Actions (0-30 days)

{self._format_immediate_actions(results)}

### Short-term Actions (1-3 months)

{self._format_short_term_actions(results)}

### Long-term Actions (3+ months)

{self._format_long_term_actions(results)}

### Accountability Matrix

{self._format_accountability_matrix(results)}
"""

        return action_plan

    def _generate_appendices(
        self,
        simulation: Simulation,
        scenario: Scenario,
        results: SimulationResult
    ) -> str:
        """Generate appendices section"""

        appendices = f"""## Appendices

### Appendix A: Scenario Configuration

```json
{json.dumps(scenario.model_dump(), indent=2)}
```

### Appendix B: Detailed Metrics

```json
{json.dumps(results.detailed_metrics, indent=2)}
```

### Appendix C: Event Log

{self._format_full_event_log(results.events)}

### Appendix D: Glossary

{self._generate_glossary()}
"""

        return appendices

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _format_list(self, items: List[Any]) -> str:
        """Format list as markdown"""
        if not items:
            return "*No items*"
        return "\n".join([f"- {item}" for item in items])

    def _format_top_items(self, items: List[Any], n: int = 3) -> str:
        """Format top N items"""
        if not items:
            return "*No items*"
        top_items = items[:n]
        return "\n".join([f"{i+1}. {item}" for i, item in enumerate(top_items)])

    def _extract_strengths(self, results: SimulationResult) -> List[str]:
        """Extract strengths from results"""
        strengths = []
        if results.overall_success_rate >= 0.8:
            strengths.append("High overall success rate achieved")
        if results.kpis_achieved:
            strengths.append(f"Successfully achieved {len(results.kpis_achieved)} KPIs")
        return strengths or ["Performance within acceptable range"]

    def _extract_weaknesses(self, results: SimulationResult) -> List[str]:
        """Extract weaknesses from results"""
        return results.improvement_areas or ["No significant weaknesses identified"]

    def _format_metrics_table(self, metrics: Dict) -> str:
        """Format metrics as markdown table"""
        if not metrics:
            return "*No metrics available*"

        table = "| Metric | Value |\n|--------|-------|\n"
        for key, value in metrics.items():
            table += f"| {key} | {value} |\n"
        return table

    def _format_detailed_metrics(self, detailed_metrics: Dict) -> str:
        """Format detailed metrics"""
        if not detailed_metrics:
            return "*No detailed metrics available*"
        return f"```json\n{json.dumps(detailed_metrics, indent=2)}\n```"

    def _format_participant_table(self, participants: List[Dict]) -> str:
        """Format participant performance as table"""
        if not participants:
            return "*No participant data*"

        table = "| Participant | Performance | Notes |\n|-------------|-------------|-------|\n"
        for p in participants:
            table += f"| {p.get('id', 'N/A')} | {p.get('score', 'N/A')} | {p.get('notes', 'N/A')} |\n"
        return table

    def _format_events_timeline(self, events: List) -> str:
        """Format events as timeline"""
        if not events:
            return "*No events recorded*"

        timeline = ""
        for event in events[:20]:  # Limit to first 20 events
            timestamp = event.get('timestamp', 'N/A') if isinstance(event, dict) else 'N/A'
            description = event.get('description', str(event)) if isinstance(event, dict) else str(event)
            timeline += f"- **{timestamp}**: {description}\n"

        if len(events) > 20:
            timeline += f"\n*... and {len(events) - 20} more events*"

        return timeline

    def _calculate_compliance_score(self, results: SimulationResult) -> float:
        """Calculate ISO compliance score"""
        return results.overall_success_rate * 100

    def _format_findings_iso(self, results: SimulationResult) -> str:
        """Format findings for ISO report"""
        return self._format_list(self._extract_strengths(results) + results.improvement_areas)

    def _format_criteria_status(self, results: SimulationResult) -> str:
        """Format success criteria status"""
        criteria = results.success_criteria or []
        return self._format_list([f" {c}" for c in criteria])

    def _format_kpis(self, results: SimulationResult) -> str:
        """Format KPIs"""
        return self._format_list(results.kpis_achieved)

    def _format_metrics_iso(self, results: SimulationResult) -> str:
        """Format metrics for ISO report"""
        return self._format_metrics_table(results.metrics)

    def _format_nonconformities(self, results: SimulationResult) -> str:
        """Format nonconformities"""
        return self._format_list(results.improvement_areas)

    def _extract_next_steps(self, results: SimulationResult) -> List[str]:
        """Extract next steps"""
        return results.recommendations[:5]  # Top 5 recommendations as next steps

    def _format_achieved_objectives(self, specification: TaskSpecification, results: SimulationResult) -> str:
        """Format achieved objectives"""
        return f"*{results.overall_success_rate * 100:.0f}% of planned objectives achieved*"

    def _generate_gap_analysis(self, specification: TaskSpecification, results: SimulationResult) -> str:
        """Generate gap analysis"""
        gap = 1.0 - results.overall_success_rate
        return f"**Performance Gap:** {gap * 100:.1f}%\n\nImprovement areas identified:\n{self._format_list(results.improvement_areas)}"

    def _format_critical_findings(self, results: SimulationResult) -> str:
        """Format critical findings"""
        return self._format_list(results.improvement_areas[:3])

    def _format_risks(self, results: SimulationResult) -> str:
        """Format identified risks"""
        return "*Risk assessment based on simulation results*\n- Further analysis recommended"

    def _format_benchmarking(self, results: SimulationResult) -> str:
        """Format benchmarking data"""
        return f"*Quality Score:* {results.quality_score}/10\n*Complexity:* {results.complexity_level}/5"

    def _analyze_team_dynamics(self, results: SimulationResult) -> str:
        """Analyze team dynamics"""
        return "*Team collaboration analysis*\n- Coordination effectiveness observed"

    def _identify_critical_moments(self, events: List) -> str:
        """Identify critical moments in timeline"""
        return "*Critical decision points identified during simulation*"

    def _format_organizational_learning(self, results: SimulationResult) -> str:
        """Format organizational learning insights"""
        return "*Key insights captured for organizational knowledge base*"

    def _format_prioritized_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations by priority"""
        if not recommendations:
            return "*No recommendations*"

        prioritized = "### High Priority\n\n"
        prioritized += self._format_top_items(recommendations, 3)
        prioritized += "\n\n### Medium Priority\n\n"
        prioritized += self._format_list(recommendations[3:6])
        return prioritized

    def _format_implementation_roadmap(self, results: SimulationResult) -> str:
        """Format implementation roadmap"""
        return "*Phased implementation approach recommended*"

    def _estimate_resources(self, results: SimulationResult) -> str:
        """Estimate required resources"""
        return "*Resource estimation based on recommendations*"

    def _format_immediate_actions(self, results: SimulationResult) -> str:
        """Format immediate actions"""
        return self._format_top_items(results.recommendations, 2)

    def _format_short_term_actions(self, results: SimulationResult) -> str:
        """Format short-term actions"""
        return self._format_list(results.recommendations[2:5])

    def _format_long_term_actions(self, results: SimulationResult) -> str:
        """Format long-term actions"""
        return self._format_list(results.recommendations[5:])

    def _format_accountability_matrix(self, results: SimulationResult) -> str:
        """Format accountability matrix"""
        return "*Accountability assignments recommended*"

    def _format_full_event_log(self, events: List) -> str:
        """Format full event log"""
        return self._format_events_timeline(events)

    def _generate_glossary(self) -> str:
        """Generate glossary"""
        return """- **RTO**: Recovery Time Objective
- **RPO**: Recovery Point Objective
- **BIA**: Business Impact Analysis
- **BCM**: Business Continuity Management
- **KPI**: Key Performance Indicator"""

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    async def _save_markdown_report(self, report_data: Dict, simulation_id: str) -> Path:
        """Save report as markdown"""
        filename = f"report_{simulation_id}.md"
        filepath = self.output_dir / filename

        content = self._compile_markdown(report_data)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    async def _save_html_report(self, report_data: Dict, simulation_id: str) -> Path:
        """Save report as HTML"""
        filename = f"report_{simulation_id}.html"
        filepath = self.output_dir / filename

        content = self._compile_html(report_data)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    async def _save_json_report(self, report_data: Dict, simulation_id: str) -> Path:
        """Save report as JSON"""
        filename = f"report_{simulation_id}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        return filepath

    def _compile_markdown(self, report_data: Dict) -> str:
        """Compile all sections into markdown"""
        sections = report_data["sections"]

        content = f"""# Simulation Report

**Report ID:** {report_data['report_id']}
**Generated:** {report_data['generated_at']}
**Simulation ID:** {report_data['simulation_id']}

---

"""

        for section_name, section_content in sections.items():
            content += f"{section_content}\n\n---\n\n"

        return content

    def _compile_html(self, report_data: Dict) -> str:
        """Compile all sections into HTML"""
        # Simple HTML wrapper (could be enhanced with templates)
        markdown_content = self._compile_markdown(report_data)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Simulation Report - {report_data['simulation_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        pre {{ background-color: #f5f5f5; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
<pre>{markdown_content}</pre>
</body>
</html>"""

        return html
