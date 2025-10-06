"""
Test Root Cause Analysis Templates
Tests for 5 Whys, Fishbone, and Fault Tree Analysis templates
"""

import pytest
from services.rca_templates import (
    FiveWhysTemplate, FishboneTemplate, FishboneCause,
    FaultTreeTemplate, FaultTreeNode, RCATemplateFactory,
    RCAAnalyzer, RCAMethod
)


class TestFiveWhysTemplate:
    """Test 5 Whys RCA Template"""

    def test_should_create_five_whys_template(self):
        """Test creating 5 Whys template"""
        template = FiveWhysTemplate(
            problem_statement="System failed during peak hours",
            why_1="Insufficient server capacity",
            why_2="No capacity planning performed",
            why_3="Lack of monitoring tools",
            why_4="Budget not allocated for monitoring",
            why_5="No business case presented for monitoring tools"
        )
        assert template.problem_statement == "System failed during peak hours"
        assert len(template.get_chain()) == 5

    def test_should_get_complete_why_chain(self, sample_five_whys_template):
        """Test extracting complete why chain"""
        template = FiveWhysTemplate(**sample_five_whys_template)
        chain = template.get_chain()

        assert len(chain) == 5
        assert "Insufficient staff availability" in chain[0]
        assert "resource allocation" in chain[4].lower()

    def test_should_auto_extract_root_cause_from_last_why(self, sample_five_whys_template):
        """Test auto-extracting root cause from last why"""
        template = FiveWhysTemplate(**sample_five_whys_template)
        root_cause = template.auto_extract_root_cause()

        assert "resource allocation" in root_cause.lower()
        assert root_cause == template.get_chain()[-1]

    def test_should_use_explicit_root_cause_if_provided(self):
        """Test explicit root cause overrides auto-extraction"""
        template = FiveWhysTemplate(
            problem_statement="Problem",
            why_1="Cause 1",
            why_2="Cause 2",
            root_cause="Explicitly defined root cause"
        )
        root_cause = template.auto_extract_root_cause()

        assert root_cause == "Explicitly defined root cause"

    def test_should_handle_partial_why_chain(self):
        """Test handling incomplete why chain"""
        template = FiveWhysTemplate(
            problem_statement="Problem",
            why_1="Cause 1",
            why_2="Cause 2",
            why_3="Cause 3"
            # why_4 and why_5 empty
        )
        chain = template.get_chain()

        assert len(chain) == 3
        assert template.auto_extract_root_cause() == "Cause 3"


class TestFishboneTemplate:
    """Test Fishbone Diagram RCA Template"""

    def test_should_create_fishbone_template(self):
        """Test creating Fishbone template"""
        template = FishboneTemplate(
            problem_statement="Quality issues in production",
            people=[
                FishboneCause(
                    description="Inadequate training",
                    sub_causes=["No onboarding", "No refresher training"]
                )
            ],
            process=[
                FishboneCause(
                    description="No quality checks",
                    sub_causes=["Missing QA step", "No review process"]
                )
            ]
        )
        assert template.problem_statement == "Quality issues in production"
        assert len(template.people) == 1
        assert len(template.process) == 1

    def test_should_organize_causes_by_6m_categories(self, sample_fishbone_template):
        """Test organizing causes by 6M framework"""
        template = FishboneTemplate(**sample_fishbone_template)
        all_causes = template.get_all_causes()

        assert "People" in all_causes
        assert "Process" in all_causes
        assert "Technology" in all_causes
        assert "Environment" in all_causes
        assert "Materials" in all_causes
        assert "Measurement" in all_causes

    def test_should_extract_root_causes_with_sub_causes(self, sample_fishbone_template):
        """Test extracting root causes (causes with sub-causes)"""
        template = FishboneTemplate(**sample_fishbone_template)
        root_causes = template.extract_root_causes()

        # Root causes are those with contributing factors (sub_causes)
        assert len(root_causes) > 0
        assert any("training" in rc.lower() for rc in root_causes)

    def test_should_handle_empty_categories(self):
        """Test handling empty fishbone categories"""
        template = FishboneTemplate(
            problem_statement="Simple problem",
            people=[FishboneCause(description="Staff issue", sub_causes=["Shortage"])]
            # All other categories empty
        )
        all_causes = template.get_all_causes()

        assert len(all_causes["People"]) == 1
        assert len(all_causes["Materials"]) == 0
        assert len(all_causes["Measurement"]) == 0

    def test_should_identify_causes_with_multiple_sub_causes(self):
        """Test identifying complex causes with multiple contributing factors"""
        template = FishboneTemplate(
            problem_statement="System failure",
            technology=[
                FishboneCause(
                    description="Software bugs",
                    sub_causes=["Untested code", "No code review", "Insufficient QA"]
                )
            ]
        )
        root_causes = template.extract_root_causes()

        assert len(root_causes) >= 1
        assert "Technology" in root_causes[0]
        assert "Software bugs" in root_causes[0]


class TestFaultTreeTemplate:
    """Test Fault Tree Analysis Template"""

    def test_should_create_fault_tree_template(self):
        """Test creating Fault Tree template"""
        top_event = FaultTreeNode(
            id="top",
            description="System unavailable",
            gate_type="OR",
            children=[
                FaultTreeNode(
                    id="hw_fail",
                    description="Hardware failure",
                    gate_type="AND",
                    probability=0.05,
                    children=[]
                )
            ]
        )
        template = FaultTreeTemplate(
            problem_statement="System unavailability",
            top_event=top_event
        )
        assert template.problem_statement == "System unavailability"
        assert template.top_event.description == "System unavailable"

    def test_should_calculate_probability_with_and_gate(self):
        """Test probability calculation for AND gate"""
        node = FaultTreeNode(
            id="and_gate",
            description="Both must fail",
            gate_type="AND",
            children=[
                FaultTreeNode(id="c1", description="Child 1", probability=0.1, children=[]),
                FaultTreeNode(id="c2", description="Child 2", probability=0.2, children=[])
            ]
        )
        # AND gate: multiply probabilities
        prob = node.calculate_probability()
        assert prob == pytest.approx(0.02, rel=1e-5)  # 0.1 * 0.2 = 0.02

    def test_should_calculate_probability_with_or_gate(self):
        """Test probability calculation for OR gate"""
        node = FaultTreeNode(
            id="or_gate",
            description="Either can fail",
            gate_type="OR",
            children=[
                FaultTreeNode(id="c1", description="Child 1", probability=0.1, children=[]),
                FaultTreeNode(id="c2", description="Child 2", probability=0.2, children=[])
            ]
        )
        # OR gate: 1 - (1-p1)*(1-p2)
        prob = node.calculate_probability()
        expected = 1 - (1 - 0.1) * (1 - 0.2)  # 1 - 0.9 * 0.8 = 0.28
        assert prob == pytest.approx(expected, rel=1e-5)

    def test_should_get_critical_path_highest_probability(self, sample_fault_tree_template):
        """Test extracting critical path (highest probability path)"""
        template = FaultTreeTemplate(**sample_fault_tree_template)
        critical_path = template.get_critical_path()

        assert len(critical_path) > 0
        assert "Critical system unavailable" in critical_path[0]

    def test_should_extract_leaf_nodes_as_root_causes(self, sample_fault_tree_template):
        """Test extracting leaf nodes (root causes) sorted by probability"""
        template = FaultTreeTemplate(**sample_fault_tree_template)
        root_causes = template.extract_root_causes()

        # Should return leaf nodes sorted by probability descending
        assert len(root_causes) > 0
        assert all("description" in rc and "probability" in rc for rc in root_causes)

        # Check sorted by probability descending
        probs = [rc["probability"] for rc in root_causes]
        assert probs == sorted(probs, reverse=True)

    def test_should_handle_nested_fault_tree(self):
        """Test complex nested fault tree"""
        template = FaultTreeTemplate(
            problem_statement="Service outage",
            top_event=FaultTreeNode(
                id="top",
                description="Service outage",
                gate_type="OR",
                children=[
                    FaultTreeNode(
                        id="level1_a",
                        description="Level 1 A",
                        gate_type="AND",
                        children=[
                            FaultTreeNode(id="leaf1", description="Leaf 1", probability=0.1, children=[]),
                            FaultTreeNode(id="leaf2", description="Leaf 2", probability=0.2, children=[])
                        ]
                    ),
                    FaultTreeNode(
                        id="level1_b",
                        description="Level 1 B",
                        gate_type="OR",
                        children=[
                            FaultTreeNode(id="leaf3", description="Leaf 3", probability=0.15, children=[]),
                            FaultTreeNode(id="leaf4", description="Leaf 4", probability=0.05, children=[])
                        ]
                    )
                ]
            )
        )
        root_causes = template.extract_root_causes()

        # Should extract all 4 leaf nodes
        assert len(root_causes) == 4
        # Highest probability should be first (0.2)
        assert root_causes[0]["probability"] == 0.2


class TestRCATemplateFactory:
    """Test RCA Template Factory"""

    def test_should_create_five_whys_template(self):
        """Test factory creates 5 Whys template"""
        template = RCATemplateFactory.create_template(
            RCAMethod.FIVE_WHYS,
            "Problem statement"
        )
        assert isinstance(template, FiveWhysTemplate)
        assert template.problem_statement == "Problem statement"

    def test_should_create_fishbone_template(self):
        """Test factory creates Fishbone template"""
        template = RCATemplateFactory.create_template(
            RCAMethod.FISHBONE,
            "Problem statement"
        )
        assert isinstance(template, FishboneTemplate)
        assert template.problem_statement == "Problem statement"

    def test_should_create_fault_tree_template(self):
        """Test factory creates Fault Tree template"""
        template = RCATemplateFactory.create_template(
            RCAMethod.FAULT_TREE,
            "Problem statement"
        )
        assert isinstance(template, FaultTreeTemplate)
        assert template.problem_statement == "Problem statement"
        assert template.top_event is not None

    def test_should_convert_template_to_dict(self, sample_five_whys_template):
        """Test converting template to dictionary"""
        template = FiveWhysTemplate(**sample_five_whys_template)
        template_dict = RCATemplateFactory.template_to_dict(template)

        assert isinstance(template_dict, dict)
        assert "problem_statement" in template_dict
        assert "why_1" in template_dict

    def test_should_reconstruct_template_from_dict(self, sample_five_whys_template):
        """Test reconstructing template from dictionary"""
        original = FiveWhysTemplate(**sample_five_whys_template)
        template_dict = RCATemplateFactory.template_to_dict(original)
        reconstructed = RCATemplateFactory.dict_to_template(RCAMethod.FIVE_WHYS, template_dict)

        assert isinstance(reconstructed, FiveWhysTemplate)
        assert reconstructed.problem_statement == original.problem_statement
        assert reconstructed.get_chain() == original.get_chain()


class TestRCAAnalyzer:
    """Test RCA Analyzer Helper"""

    def test_should_extract_root_causes_from_five_whys(self, sample_five_whys_template):
        """Test extracting root causes from 5 Whys"""
        root_causes = RCAAnalyzer.extract_root_causes(
            RCAMethod.FIVE_WHYS,
            sample_five_whys_template
        )

        assert len(root_causes) > 0
        assert isinstance(root_causes[0], str)
        assert "resource allocation" in root_causes[0].lower()

    def test_should_extract_root_causes_from_fishbone(self, sample_fishbone_template):
        """Test extracting root causes from Fishbone"""
        root_causes = RCAAnalyzer.extract_root_causes(
            RCAMethod.FISHBONE,
            sample_fishbone_template
        )

        assert len(root_causes) > 0
        assert all(isinstance(rc, str) for rc in root_causes)

    def test_should_extract_top_3_root_causes_from_fault_tree(self, sample_fault_tree_template):
        """Test extracting top 3 root causes from Fault Tree"""
        root_causes = RCAAnalyzer.extract_root_causes(
            RCAMethod.FAULT_TREE,
            sample_fault_tree_template
        )

        # Should return max 3 causes
        assert len(root_causes) <= 3
        assert all(isinstance(rc, str) for rc in root_causes)

    def test_should_generate_summary_for_five_whys(self, sample_five_whys_template):
        """Test generating summary for 5 Whys"""
        summary = RCAAnalyzer.generate_summary(
            RCAMethod.FIVE_WHYS,
            sample_five_whys_template
        )

        assert isinstance(summary, str)
        assert "5 Whys" in summary
        assert "levels of causation" in summary.lower()
        assert "root cause" in summary.lower()

    def test_should_generate_summary_for_fishbone(self, sample_fishbone_template):
        """Test generating summary for Fishbone"""
        summary = RCAAnalyzer.generate_summary(
            RCAMethod.FISHBONE,
            sample_fishbone_template
        )

        assert isinstance(summary, str)
        assert "Fishbone" in summary
        assert "contributing factors" in summary.lower()
        assert "6 categories" in summary

    def test_should_generate_summary_for_fault_tree(self, sample_fault_tree_template):
        """Test generating summary for Fault Tree"""
        summary = RCAAnalyzer.generate_summary(
            RCAMethod.FAULT_TREE,
            sample_fault_tree_template
        )

        assert isinstance(summary, str)
        assert "Fault tree" in summary
        assert "critical path" in summary.lower()
        assert "probability" in summary.lower()
