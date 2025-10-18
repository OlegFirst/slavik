"""
Root Cause Analysis Templates
ISO 22301 Clause 10.1 - Nonconformity and Corrective Action

Structured RCA methods:
- 5 Whys: Drill down to root cause through iterative questioning
- Fishbone Diagram (Ishikawa): Categorize causes by 6M framework
- Fault Tree Analysis: Top-down deductive analysis with probability
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from compliance.models.enums import RCAMethod


# =============================================================================
# 5 WHYS TEMPLATE
# =============================================================================

class FiveWhysTemplate(BaseModel):
    """5 Whys RCA Template - Drill down to root cause"""
    problem_statement: str
    why_1: str = ""
    why_2: str = ""
    why_3: str = ""
    why_4: str = ""
    why_5: str = ""
    root_cause: Optional[str] = None

    def get_chain(self) -> List[str]:
        """Get the complete why chain"""
        chain = []
        for i in range(1, 6):
            why = getattr(self, f"why_{i}")
            if why:
                chain.append(why)
        return chain

    def auto_extract_root_cause(self) -> str:
        """Extract root cause from last Why"""
        chain = self.get_chain()
        if self.root_cause:
            return self.root_cause
        return chain[-1] if chain else self.problem_statement


# =============================================================================
# FISHBONE DIAGRAM TEMPLATE
# =============================================================================

class FishboneCause(BaseModel):
    """Single cause in fishbone diagram"""
    description: str
    sub_causes: List[str] = Field(default_factory=list)


class FishboneTemplate(BaseModel):
    """Fishbone (Ishikawa) Diagram Template - 6M Categories"""
    problem_statement: str

    # 6M Categories
    people: List[FishboneCause] = Field(default_factory=list)
    process: List[FishboneCause] = Field(default_factory=list)
    technology: List[FishboneCause] = Field(default_factory=list)
    environment: List[FishboneCause] = Field(default_factory=list)
    materials: List[FishboneCause] = Field(default_factory=list)
    measurement: List[FishboneCause] = Field(default_factory=list)

    def get_all_causes(self) -> Dict[str, List[FishboneCause]]:
        """Get all causes organized by category"""
        return {
            "People": self.people,
            "Process": self.process,
            "Technology": self.technology,
            "Environment": self.environment,
            "Materials": self.materials,
            "Measurement": self.measurement,
        }

    def extract_root_causes(self) -> List[str]:
        """Extract most likely root causes (causes with sub-causes)"""
        root_causes = []
        for category, causes in self.get_all_causes().items():
            for cause in causes:
                if cause.sub_causes:  # Has contributing factors
                    root_causes.append(f"{category}: {cause.description}")
        return root_causes


# =============================================================================
# FAULT TREE ANALYSIS TEMPLATE
# =============================================================================

class FaultTreeNode(BaseModel):
    """Node in fault tree"""
    id: str
    description: str
    gate_type: str = "AND"  # AND, OR
    probability: Optional[float] = None
    children: List['FaultTreeNode'] = Field(default_factory=list)

    def calculate_probability(self) -> float:
        """Calculate probability based on children"""
        if not self.children:
            return self.probability or 0.0

        child_probs = [child.calculate_probability() for child in self.children]

        if self.gate_type == "AND":
            # All must occur
            result = 1.0
            for prob in child_probs:
                result *= prob
            return result
        else:  # OR
            # At least one occurs
            result = 1.0
            for prob in child_probs:
                result *= (1 - prob)
            return 1 - result


# Enable forward references
FaultTreeNode.model_rebuild()


class FaultTreeTemplate(BaseModel):
    """Fault Tree Analysis Template"""
    problem_statement: str
    top_event: FaultTreeNode

    def get_critical_path(self) -> List[str]:
        """Get path with highest probability"""
        def traverse(node: FaultTreeNode, path: List[str]) -> tuple:
            current_path = path + [node.description]

            if not node.children:
                return (node.calculate_probability(), current_path)

            child_paths = [traverse(child, current_path) for child in node.children]
            return max(child_paths, key=lambda x: x[0])

        prob, path = traverse(self.top_event, [])
        return path

    def extract_root_causes(self) -> List[Dict[str, Any]]:
        """Extract leaf nodes (root causes) with probabilities"""
        def get_leaves(node: FaultTreeNode) -> List[Dict[str, Any]]:
            if not node.children:
                return [{
                    "description": node.description,
                    "probability": node.probability or 0.0
                }]

            leaves = []
            for child in node.children:
                leaves.extend(get_leaves(child))
            return leaves

        leaves = get_leaves(self.top_event)
        # Sort by probability descending
        return sorted(leaves, key=lambda x: x["probability"], reverse=True)


# =============================================================================
# RCA TEMPLATE FACTORY
# =============================================================================

class RCATemplateFactory:
    """Factory for creating RCA templates"""

    @staticmethod
    def create_template(method: RCAMethod, problem_statement: str) -> Any:
        """Create appropriate RCA template"""
        if method == RCAMethod.FIVE_WHYS:
            return FiveWhysTemplate(problem_statement=problem_statement)

        elif method == RCAMethod.FISHBONE:
            return FishboneTemplate(problem_statement=problem_statement)

        elif method == RCAMethod.FAULT_TREE:
            top_event = FaultTreeNode(
                id="top",
                description=problem_statement,
                gate_type="OR"
            )
            return FaultTreeTemplate(
                problem_statement=problem_statement,
                top_event=top_event
            )

        else:
            raise ValueError(f"Unknown RCA method: {method}")

    @staticmethod
    def template_to_dict(template: Any) -> Dict[str, Any]:
        """Convert template to dictionary for storage"""
        return template.model_dump()

    @staticmethod
    def dict_to_template(method: RCAMethod, data: Dict[str, Any]) -> Any:
        """Reconstruct template from dictionary"""
        if method == RCAMethod.FIVE_WHYS:
            return FiveWhysTemplate(**data)
        elif method == RCAMethod.FISHBONE:
            return FishboneTemplate(**data)
        elif method == RCAMethod.FAULT_TREE:
            return FaultTreeTemplate(**data)
        else:
            raise ValueError(f"Unknown RCA method: {method}")


# =============================================================================
# RCA ANALYZER
# =============================================================================

class RCAAnalyzer:
    """Helper for RCA analysis"""

    @staticmethod
    def extract_root_causes(method: RCAMethod, template_data: Dict[str, Any]) -> List[str]:
        """Extract root causes from completed template"""
        template = RCATemplateFactory.dict_to_template(method, template_data)

        if isinstance(template, FiveWhysTemplate):
            root_cause = template.auto_extract_root_cause()
            return [root_cause] if root_cause else []

        elif isinstance(template, FishboneTemplate):
            return template.extract_root_causes()

        elif isinstance(template, FaultTreeTemplate):
            causes = template.extract_root_causes()
            return [c["description"] for c in causes[:3]]  # Top 3

        return []

    @staticmethod
    def generate_summary(method: RCAMethod, template_data: Dict[str, Any]) -> str:
        """Generate RCA summary text"""
        template = RCATemplateFactory.dict_to_template(method, template_data)

        if isinstance(template, FiveWhysTemplate):
            chain = template.get_chain()
            return f"5 Whys analysis revealed {len(chain)} levels of causation, " \
                   f"leading to root cause: {template.auto_extract_root_cause()}"

        elif isinstance(template, FishboneTemplate):
            all_causes = template.get_all_causes()
            total = sum(len(causes) for causes in all_causes.values())
            return f"Fishbone analysis identified {total} contributing factors " \
                   f"across 6 categories, with {len(template.extract_root_causes())} " \
                   f"primary root causes"

        elif isinstance(template, FaultTreeTemplate):
            critical_path = template.get_critical_path()
            return f"Fault tree analysis identified critical path with " \
                   f"{len(critical_path)} nodes, probability: " \
                   f"{template.top_event.calculate_probability():.2%}"

        return "RCA completed"
