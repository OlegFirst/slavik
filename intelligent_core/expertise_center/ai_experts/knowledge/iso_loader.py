"""
ISO 22301 Knowledge Loader

Loads ISO 22301:2019 clauses from ISO_22301_Library into Knowledge Graph
for use by AI Experts and RAG Pipeline.
"""

from typing import List, Dict, Any
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


class ISO22301Clause:
    """Structured representation of ISO 22301 clause"""

    def __init__(
        self,
        clause_number: str,
        clause_title: str,
        requirements: List[str],
        evidence_needed: List[str],
        audit_questions: List[str],
        description: str = ""
    ):
        self.clause_number = clause_number
        self.clause_title = clause_title
        self.requirements = requirements
        self.evidence_needed = evidence_needed
        self.audit_questions = audit_questions
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'clause_number': self.clause_number,
            'clause_title': self.clause_title,
            'requirements': self.requirements,
            'evidence_needed': self.evidence_needed,
            'audit_questions': self.audit_questions,
            'description': self.description,
            'full_text': self._generate_full_text()
        }

    def _generate_full_text(self) -> str:
        """Generate full searchable text for RAG"""
        parts = [
            f"ISO 22301:2019 Clause {self.clause_number}: {self.clause_title}",
            "",
            self.description,
            "",
            "Requirements:",
            *[f"- {req}" for req in self.requirements],
            "",
            "Evidence Needed:",
            *[f"- {ev}" for ev in self.evidence_needed],
        ]

        if self.audit_questions:
            parts.extend([
                "",
                "Audit Questions:",
                *[f"- {q}" for q in self.audit_questions]
            ])

        return "\n".join(parts)


class ISO22301Loader:
    """
    Load ISO 22301:2019 standard from ISO_22301_Library

    Parses clauses_breakdown.md and extracts structured clause data
    """

    def __init__(self, library_path: str = "/Users/MD/AI-Platform-ISO/data/knowledge/standards/iso/iso-22301"):
        self.library_path = Path(library_path)
        self.clauses_file = self.library_path / "standards" / "clauses_breakdown.md"

        if not self.clauses_file.exists():
            raise FileNotFoundError(f"ISO clauses file not found: {self.clauses_file}")

    def load_all_clauses(self) -> List[ISO22301Clause]:
        """
        Load all ISO 22301:2019 clauses

        Returns:
            List of ISO22301Clause objects
        """

        logger.info(f"Loading ISO 22301 clauses from {self.clauses_file}")

        with open(self.clauses_file, 'r', encoding='utf-8') as f:
            content = f.read()

        clauses = []

        # Parse Clause 4
        clauses.extend(self._parse_clause_4(content))

        # Parse Clause 5
        clauses.extend(self._parse_clause_5(content))

        # Parse Clause 6
        clauses.extend(self._parse_clause_6(content))

        # Parse Clause 7
        clauses.extend(self._parse_clause_7(content))

        # Parse Clause 8 (most important!)
        clauses.extend(self._parse_clause_8(content))

        # Parse Clause 9
        clauses.extend(self._parse_clause_9(content))

        # Parse Clause 10
        clauses.extend(self._parse_clause_10(content))

        logger.info(f"✅ Loaded {len(clauses)} ISO 22301 clauses")

        return clauses

    def _parse_clause_4(self, content: str) -> List[ISO22301Clause]:
        """Parse Clause 4: Context of the Organization"""

        clauses = []

        # 4.1 Understanding the organization and its context
        clauses.append(ISO22301Clause(
            clause_number="4.1",
            clause_title="Understanding the organization and its context",
            requirements=[
                "Determine external and internal issues relevant to BCMS",
                "Consider legal, regulatory, financial, technological, competitive, market, social, cultural environment"
            ],
            evidence_needed=[
                "Context analysis document",
                "PESTLE or SWOT analysis",
                "Stakeholder analysis"
            ],
            audit_questions=[
                "How does the organization identify internal/external factors affecting BC?",
                "Are these factors documented and reviewed regularly?"
            ],
            description="The organization must understand its internal and external context to establish an effective BCMS."
        ))

        # 4.2 Understanding the needs and expectations of interested parties
        clauses.append(ISO22301Clause(
            clause_number="4.2",
            clause_title="Understanding the needs and expectations of interested parties",
            requirements=[
                "Identify interested parties (stakeholders)",
                "Determine their requirements and expectations",
                "Understand which requirements become compliance obligations"
            ],
            evidence_needed=[
                "Stakeholder register",
                "Requirements documentation",
                "Compliance obligations list"
            ],
            audit_questions=[
                "How are interested parties identified?",
                "Are stakeholder requirements documented?"
            ],
            description="Identify all stakeholders (customers, regulators, suppliers, employees, shareholders, community) and their requirements."
        ))

        # 4.3 Determining the scope of the BCMS
        clauses.append(ISO22301Clause(
            clause_number="4.3",
            clause_title="Determining the scope of the BCMS",
            requirements=[
                "Define boundaries and applicability of BCMS",
                "Consider context, interested parties, products/services",
                "Document scope clearly"
            ],
            evidence_needed=[
                "BCMS scope statement (documented)",
                "Justification for any exclusions"
            ],
            audit_questions=[
                "Is scope clearly defined and documented?",
                "Does scope cover all critical operations?"
            ],
            description="The scope defines what parts of the organization are covered by the BCMS."
        ))

        # 4.4 Business continuity management system
        clauses.append(ISO22301Clause(
            clause_number="4.4",
            clause_title="Business continuity management system",
            requirements=[
                "Establish, implement, maintain, continually improve BCMS",
                "Include processes and interactions"
            ],
            evidence_needed=[
                "BCMS documentation",
                "Process maps",
                "Process interactions diagram"
            ],
            audit_questions=[
                "Is the BCMS established and documented?",
                "Are process interactions defined?"
            ],
            description="The organization must establish and maintain a complete BCMS."
        ))

        return clauses

    def _parse_clause_5(self, content: str) -> List[ISO22301Clause]:
        """Parse Clause 5: Leadership"""

        clauses = []

        # 5.1 Leadership and commitment
        clauses.append(ISO22301Clause(
            clause_number="5.1",
            clause_title="Leadership and commitment",
            requirements=[
                "Top management demonstrates leadership and commitment",
                "Ensure BCMS policy and objectives are established",
                "Ensure resources available",
                "Communicate importance of effective BCMS"
            ],
            evidence_needed=[
                "Management meeting minutes",
                "Resource allocation records",
                "Communication records"
            ],
            audit_questions=[
                "How does top management demonstrate commitment to BCMS?",
                "Are adequate resources allocated?"
            ],
            description="Top management must demonstrate visible commitment to the BCMS."
        ))

        # 5.2 Policy
        clauses.append(ISO22301Clause(
            clause_number="5.2",
            clause_title="BC Policy",
            requirements=[
                "Establish BC policy appropriate to purpose and context",
                "Provide framework for BC objectives",
                "Include commitment to satisfy requirements",
                "Include commitment to continual improvement"
            ],
            evidence_needed=[
                "BC Policy (documented, approved by top management)",
                "Policy communication records"
            ],
            audit_questions=[
                "Is BC policy established and documented?",
                "Has policy been communicated to all relevant parties?"
            ],
            description="The BC policy sets the direction for the organization's BCMS."
        ))

        # 5.3 Organizational roles, responsibilities and authorities
        clauses.append(ISO22301Clause(
            clause_number="5.3",
            clause_title="Organizational roles, responsibilities and authorities",
            requirements=[
                "Assign and communicate responsibilities and authorities for BCMS",
                "Define roles for ensuring BCMS conforms to requirements",
                "Define roles for reporting on BCMS performance"
            ],
            evidence_needed=[
                "Organizational chart with BC roles",
                "Job descriptions with BC responsibilities",
                "RACI matrix"
            ],
            audit_questions=[
                "Are BC roles and responsibilities clearly defined?",
                "Have responsibilities been communicated?"
            ],
            description="Clear roles and responsibilities must be defined for BCMS management."
        ))

        return clauses

    def _parse_clause_6(self, content: str) -> List[ISO22301Clause]:
        """Parse Clause 6: Planning"""

        clauses = []

        # 6.1 Actions to address risks and opportunities
        clauses.append(ISO22301Clause(
            clause_number="6.1",
            clause_title="Actions to address risks and opportunities",
            requirements=[
                "Determine risks and opportunities for BCMS",
                "Plan actions to address them",
                "Integrate actions into BCMS processes",
                "Evaluate effectiveness of actions"
            ],
            evidence_needed=[
                "Risk register",
                "Risk treatment plans",
                "Action plans"
            ],
            audit_questions=[
                "How are BCMS risks identified?",
                "Are actions to address risks documented and implemented?"
            ],
            description="The organization must identify and address risks to the BCMS itself."
        ))

        # 6.2 Business continuity objectives and planning
        clauses.append(ISO22301Clause(
            clause_number="6.2",
            clause_title="Business continuity objectives and planning to achieve them",
            requirements=[
                "Establish BC objectives at relevant functions and levels",
                "Objectives must be consistent with BC policy",
                "Objectives must be measurable",
                "Objectives must be monitored and updated"
            ],
            evidence_needed=[
                "BC objectives documentation",
                "Measurement criteria",
                "Progress tracking"
            ],
            audit_questions=[
                "Are BC objectives defined and measurable?",
                "How are objectives monitored and reviewed?"
            ],
            description="BC objectives provide measurable targets for BCMS performance."
        ))

        # 6.3 Planning of changes
        clauses.append(ISO22301Clause(
            clause_number="6.3",
            clause_title="Planning of changes",
            requirements=[
                "When changes to BCMS are needed, carry them out in planned manner",
                "Consider purpose of changes and potential consequences"
            ],
            evidence_needed=[
                "Change management records",
                "Change impact assessments"
            ],
            audit_questions=[
                "How are BCMS changes managed?",
                "Are changes assessed for impact?"
            ],
            description="Changes to the BCMS must be planned and controlled."
        ))

        return clauses

    def _parse_clause_7(self, content: str) -> List[ISO22301Clause]:
        """Parse Clause 7: Support"""

        clauses = []

        # 7.1 Resources
        clauses.append(ISO22301Clause(
            clause_number="7.1",
            clause_title="Resources",
            requirements=[
                "Determine and provide resources needed for BCMS",
                "Include people, infrastructure, technology, financial resources"
            ],
            evidence_needed=[
                "Resource allocation documentation",
                "Budget for BC activities",
                "Infrastructure inventory"
            ],
            audit_questions=[
                "Are adequate resources allocated to BCMS?",
                "How are resource needs determined?"
            ],
            description="Adequate resources must be provided for the BCMS."
        ))

        # 7.2 Competence
        clauses.append(ISO22301Clause(
            clause_number="7.2",
            clause_title="Competence",
            requirements=[
                "Determine necessary competence for BC roles",
                "Ensure persons are competent (education, training, experience)",
                "Take actions to acquire competence",
                "Retain documented information as evidence"
            ],
            evidence_needed=[
                "Competency matrix",
                "Training records",
                "Qualifications/certifications",
                "Training plans"
            ],
            audit_questions=[
                "How is BC competence determined and maintained?",
                "Are training records maintained?"
            ],
            description="Personnel involved in BCMS must be competent based on education, training, and experience."
        ))

        # 7.3 Awareness
        clauses.append(ISO22301Clause(
            clause_number="7.3",
            clause_title="Awareness",
            requirements=[
                "Ensure persons are aware of BC policy",
                "Ensure awareness of their contribution to BCMS effectiveness",
                "Ensure awareness of implications of not conforming"
            ],
            evidence_needed=[
                "Awareness campaign materials",
                "Communication records",
                "Awareness surveys"
            ],
            audit_questions=[
                "How is BC awareness promoted?",
                "Are personnel aware of their BC responsibilities?"
            ],
            description="All personnel must be aware of the BCMS and their role in it."
        ))

        # 7.4 Communication
        clauses.append(ISO22301Clause(
            clause_number="7.4",
            clause_title="Communication",
            requirements=[
                "Determine what to communicate",
                "Determine when to communicate",
                "Determine with whom to communicate",
                "Determine how to communicate",
                "Determine who communicates"
            ],
            evidence_needed=[
                "Communication plan",
                "Communication logs",
                "Crisis communication procedures"
            ],
            audit_questions=[
                "Is there a BC communication plan?",
                "Are communication channels defined?"
            ],
            description="Internal and external communications relevant to BCMS must be planned."
        ))

        # 7.5 Documented information
        clauses.append(ISO22301Clause(
            clause_number="7.5",
            clause_title="Documented information",
            requirements=[
                "BCMS must include documented information required by standard",
                "BCMS must include documented information determined necessary for effectiveness",
                "Control documented information (creation, update, access, retention)"
            ],
            evidence_needed=[
                "Document control procedure",
                "Document register",
                "Version control",
                "Access controls"
            ],
            audit_questions=[
                "Is documented information controlled?",
                "Are documents up to date and accessible?"
            ],
            description="Documented information must be created, updated, and controlled."
        ))

        return clauses

    def _parse_clause_8(self, content: str) -> List[ISO22301Clause]:
        """Parse Clause 8: Operation (MOST IMPORTANT!)"""

        clauses = []

        # 8.2.2 Business Impact Analysis (BIA)
        clauses.append(ISO22301Clause(
            clause_number="8.2.2",
            clause_title="Business Impact Analysis (BIA)",
            requirements=[
                "Analyze impact of disruptions over time",
                "Identify activities supporting products/services",
                "Assess impacts over time if not resumed",
                "Establish time frames for resumption (RTO)",
                "Identify resources to support prioritized activities",
                "Identify dependencies and supporting activities"
            ],
            evidence_needed=[
                "BIA methodology document",
                "BIA reports for critical processes",
                "RTO/RPO definitions",
                "MTPD (Maximum Tolerable Period of Disruption)",
                "Impact assessment (financial, operational, reputational, regulatory)",
                "Dependencies mapping"
            ],
            audit_questions=[
                "How often is BIA conducted?",
                "Are all critical processes covered?",
                "Are RTOs realistic and tested?"
            ],
            description="BIA identifies critical business activities, their recovery time objectives, and dependencies. For healthcare: must include patient impact, clinical service prioritization, essential services (WHO framework), and regulatory compliance (HIPAA)."
        ))

        # 8.2.3 Risk Assessment
        clauses.append(ISO22301Clause(
            clause_number="8.2.3",
            clause_title="Risk Assessment",
            requirements=[
                "Identify risks of disruption",
                "Analyze and evaluate risks",
                "Identify risk treatment options"
            ],
            evidence_needed=[
                "Risk assessment methodology",
                "Risk register",
                "Risk analysis (likelihood × impact)",
                "Risk treatment plans"
            ],
            audit_questions=[
                "How are disruption risks identified?",
                "Is risk assessment methodology documented?",
                "Are risks regularly reviewed?"
            ],
            description="Risk assessment identifies threats that could disrupt critical activities. Methodologies include qualitative (High/Medium/Low), quantitative (FAIR, Monte Carlo), and scenario-based approaches."
        ))

        # 8.3 Business Continuity Strategy
        clauses.append(ISO22301Clause(
            clause_number="8.3",
            clause_title="Business Continuity Strategy",
            requirements=[
                "Determine appropriate strategies based on BIA and risk assessment",
                "Select strategies for pre-incident activities (prevention, mitigation)",
                "Select strategies for during-incident activities (response)",
                "Select strategies for post-incident activities (recovery, resumption)"
            ],
            evidence_needed=[
                "BC strategy document",
                "Strategy options analysis",
                "Chosen strategies with justification",
                "Recovery strategies (work area recovery, technology recovery, people)"
            ],
            audit_questions=[
                "Are strategies aligned with RTOs?",
                "Are multiple scenarios considered?",
                "Are strategies cost-effective?"
            ],
            description="BC strategies define HOW the organization will achieve its recovery objectives."
        ))

        # 8.4.2 Incident Response Structure
        clauses.append(ISO22301Clause(
            clause_number="8.4.2",
            clause_title="Incident Response Structure",
            requirements=[
                "Establish structure to respond to disruptive incidents",
                "Define roles and responsibilities",
                "Define authority to act",
                "Define incident response process"
            ],
            evidence_needed=[
                "Incident response plan",
                "Call tree/escalation matrix",
                "Incident management team structure",
                "24/7 contact information"
            ],
            audit_questions=[
                "Is incident response structure documented?",
                "Are response team members trained?",
                "Can the team be activated 24/7?"
            ],
            description="The incident response structure defines WHO responds to incidents and HOW."
        ))

        # 8.4.4 Business Continuity Plans
        clauses.append(ISO22301Clause(
            clause_number="8.4.4",
            clause_title="Business Continuity Plans and Procedures",
            requirements=[
                "Develop BC plans covering immediate actions during disruption",
                "Ensure continuity of prioritized activities",
                "Define resources needed",
                "Document dependencies",
                "Include communication procedures",
                "Include escalation procedures"
            ],
            evidence_needed=[
                "BC plans for each critical process",
                "Procedure documents (step-by-step)",
                "Resource lists (people, facilities, technology)",
                "Alternative site procedures",
                "Supplier continuity arrangements"
            ],
            audit_questions=[
                "Are BC plans documented for all critical activities?",
                "Are plans tested regularly?",
                "Do personnel know how to access plans?"
            ],
            description="BC plans are step-by-step procedures to maintain or recover critical activities."
        ))

        # 8.5 Exercising and Testing
        clauses.append(ISO22301Clause(
            clause_number="8.5",
            clause_title="Exercising and Testing",
            requirements=[
                "Exercise and test BC plans at planned intervals",
                "Base exercises on test objectives and organization size/nature",
                "Evaluate results and implement corrective actions"
            ],
            evidence_needed=[
                "Exercise schedule",
                "Exercise plans/scenarios",
                "Exercise reports",
                "Lessons learned",
                "Corrective action plans"
            ],
            audit_questions=[
                "How often are exercises conducted?",
                "Do exercises test all critical processes?",
                "Are lessons learned implemented?"
            ],
            description="Exercises validate BC plans and build response capability. Types: desktop (tabletop), walkthroughs, simulations, full-scale, component testing."
        ))

        return clauses

    def _parse_clause_9(self, content: str) -> List[ISO22301Clause]:
        """Parse Clause 9: Performance Evaluation"""

        clauses = []

        # 9.1 Monitoring, measurement, analysis and evaluation
        clauses.append(ISO22301Clause(
            clause_number="9.1",
            clause_title="Monitoring, measurement, analysis and evaluation",
            requirements=[
                "Determine what to monitor and measure",
                "Determine methods for valid results",
                "Determine when to monitor and measure",
                "Determine who analyzes and evaluates",
                "Retain documented information"
            ],
            evidence_needed=[
                "Performance metrics",
                "Measurement procedures",
                "Analysis reports",
                "Trend analysis"
            ],
            audit_questions=[
                "What BCMS metrics are monitored?",
                "How often are metrics reviewed?",
                "Are metrics used to drive improvement?"
            ],
            description="Performance must be monitored using metrics. Examples: % critical processes with BC plans, RTO achievement rate, exercise participation, training completion, incident response times."
        ))

        # 9.2 Internal Audit
        clauses.append(ISO22301Clause(
            clause_number="9.2",
            clause_title="Internal Audit",
            requirements=[
                "Conduct internal audits at planned intervals",
                "Ensure BCMS conforms to requirements",
                "Ensure BCMS is effectively implemented and maintained",
                "Select competent auditors",
                "Ensure objectivity and impartiality",
                "Report results to relevant management"
            ],
            evidence_needed=[
                "Audit program/schedule",
                "Audit plans",
                "Audit checklists (clause-by-clause)",
                "Audit reports",
                "Nonconformity reports",
                "Corrective action plans"
            ],
            audit_questions=[
                "How often are internal audits conducted?",
                "Are auditors independent and competent?",
                "Are audit findings addressed?"
            ],
            description="Internal audits verify BCMS compliance and effectiveness. Frequency: typically annual minimum, more frequent for high-risk areas, after major changes, after incidents."
        ))

        # 9.3 Management Review
        clauses.append(ISO22301Clause(
            clause_number="9.3",
            clause_title="Management Review",
            requirements=[
                "Top management reviews BCMS at planned intervals",
                "Review inputs: previous actions, changes, performance, feedback, improvement opportunities",
                "Review outputs: improvement decisions, BCMS changes, resource needs"
            ],
            evidence_needed=[
                "Management review agenda",
                "Management review minutes",
                "Action items",
                "Follow-up documentation"
            ],
            audit_questions=[
                "How often is management review conducted?",
                "Does top management participate?",
                "Are review outputs acted upon?"
            ],
            description="Management review ensures continuing suitability, adequacy, and effectiveness of BCMS."
        ))

        return clauses

    def _parse_clause_10(self, content: str) -> List[ISO22301Clause]:
        """Parse Clause 10: Improvement"""

        clauses = []

        # 10.1 Nonconformity and Corrective Action
        clauses.append(ISO22301Clause(
            clause_number="10.1",
            clause_title="Nonconformity and Corrective Action",
            requirements=[
                "React to nonconformity and take action",
                "Evaluate need for action to eliminate causes",
                "Implement corrective action",
                "Review effectiveness of corrective action",
                "Update BCMS if necessary"
            ],
            evidence_needed=[
                "Nonconformity register",
                "Root cause analysis",
                "Corrective action plans",
                "Effectiveness reviews",
                "Closure evidence"
            ],
            audit_questions=[
                "How are nonconformities identified and recorded?",
                "Is root cause analysis performed?",
                "Are corrective actions effective?"
            ],
            description="When things go wrong, the organization must identify root causes and take corrective action."
        ))

        # 10.2 Continual Improvement
        clauses.append(ISO22301Clause(
            clause_number="10.2",
            clause_title="Continual Improvement",
            requirements=[
                "Continually improve suitability, adequacy, effectiveness of BCMS",
                "Consider results of analysis and evaluation, management review"
            ],
            evidence_needed=[
                "Improvement initiatives",
                "Lessons learned repository",
                "Best practices library"
            ],
            audit_questions=[
                "How is continual improvement demonstrated?",
                "Are improvement opportunities identified and acted upon?"
            ],
            description="The BCMS must continually improve. Examples: enhanced BC strategies, improved training, better technology, streamlined processes, reduced RTOs, increased resilience."
        ))

        return clauses

    def get_clause_by_number(self, clause_number: str) -> ISO22301Clause:
        """Get specific clause by number"""
        all_clauses = self.load_all_clauses()

        for clause in all_clauses:
            if clause.clause_number == clause_number:
                return clause

        raise ValueError(f"Clause {clause_number} not found")

    def get_clauses_by_category(self, category: str) -> List[ISO22301Clause]:
        """
        Get clauses by category

        Categories: context, leadership, planning, support, operation,
                   performance, improvement
        """

        category_ranges = {
            'context': ['4.1', '4.2', '4.3', '4.4'],
            'leadership': ['5.1', '5.2', '5.3'],
            'planning': ['6.1', '6.2', '6.3'],
            'support': ['7.1', '7.2', '7.3', '7.4', '7.5'],
            'operation': ['8.2.2', '8.2.3', '8.3', '8.4.2', '8.4.4', '8.5'],
            'performance': ['9.1', '9.2', '9.3'],
            'improvement': ['10.1', '10.2']
        }

        if category not in category_ranges:
            raise ValueError(f"Invalid category. Choose from: {list(category_ranges.keys())}")

        all_clauses = self.load_all_clauses()
        clause_numbers = category_ranges[category]

        return [c for c in all_clauses if c.clause_number in clause_numbers]


# Example usage
if __name__ == "__main__":
    loader = ISO22301Loader()

    # Load all clauses
    clauses = loader.load_all_clauses()

    print(f"Loaded {len(clauses)} ISO 22301:2019 clauses\n")

    # Example: BIA clause
    bia_clause = loader.get_clause_by_number("8.2.2")
    print(f"Clause {bia_clause.clause_number}: {bia_clause.clause_title}")
    print(f"\nRequirements:")
    for req in bia_clause.requirements:
        print(f"  - {req}")
    print(f"\nEvidence needed:")
    for ev in bia_clause.evidence_needed:
        print(f"  - {ev}")

    # Example: Operation clauses
    operation_clauses = loader.get_clauses_by_category('operation')
    print(f"\n\nOperation category has {len(operation_clauses)} clauses:")
    for clause in operation_clauses:
        print(f"  - {clause.clause_number}: {clause.clause_title}")
