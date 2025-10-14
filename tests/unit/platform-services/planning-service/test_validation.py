"""
Test Pydantic Model Validation
Tests for input validation rules on domain models
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from models.domain import (
    StrategyCreate,
    CostBenefitRequest,
    CostBreakdown,
    BenefitAnalysis,
    ROIAnalysis,
    ResourceRequirement,
    ImplementationPhase,
    StrategyType,
    StrategyPhase
)


class TestCostBenefitRequestValidation:
    """Test CostBenefitRequest validation"""

    def test_implementation_years_valid(self):
        """Test valid implementation years (1-30)"""
        request = CostBenefitRequest(
            cost_breakdown=CostBreakdown(capex=100000),
            expected_benefits=BenefitAnalysis(
                quantitative_benefits={"revenue": 50000},
                qualitative_benefits=["Good"]
            ),
            implementation_years=5,
            discount_rate=0.10
        )
        assert request.implementation_years == 5

    def test_implementation_years_boundary_min(self):
        """Test minimum boundary (1 year)"""
        request = CostBenefitRequest(
            cost_breakdown=CostBreakdown(capex=100000),
            expected_benefits=BenefitAnalysis(
                quantitative_benefits={"revenue": 50000},
                qualitative_benefits=["Good"]
            ),
            implementation_years=1
        )
        assert request.implementation_years == 1

    def test_implementation_years_boundary_max(self):
        """Test maximum boundary (30 years)"""
        request = CostBenefitRequest(
            cost_breakdown=CostBreakdown(capex=100000),
            expected_benefits=BenefitAnalysis(
                quantitative_benefits={"revenue": 50000},
                qualitative_benefits=["Good"]
            ),
            implementation_years=30
        )
        assert request.implementation_years == 30

    def test_implementation_years_invalid_too_low(self):
        """Test years < 1 raises error"""
        with pytest.raises(ValidationError) as exc_info:
            CostBenefitRequest(
                cost_breakdown=CostBreakdown(capex=100000),
                expected_benefits=BenefitAnalysis(
                    quantitative_benefits={"revenue": 50000},
                    qualitative_benefits=["Good"]
                ),
                implementation_years=0
            )
        assert "Implementation years must be at least 1" in str(exc_info.value)

    def test_implementation_years_invalid_too_high(self):
        """Test years > 30 raises error"""
        with pytest.raises(ValidationError) as exc_info:
            CostBenefitRequest(
                cost_breakdown=CostBreakdown(capex=100000),
                expected_benefits=BenefitAnalysis(
                    quantitative_benefits={"revenue": 50000},
                    qualitative_benefits=["Good"]
                ),
                implementation_years=31
            )
        assert "must not exceed 30 years" in str(exc_info.value)

    def test_implementation_years_negative(self):
        """Test negative years raises error"""
        with pytest.raises(ValidationError) as exc_info:
            CostBenefitRequest(
                cost_breakdown=CostBreakdown(capex=100000),
                expected_benefits=BenefitAnalysis(
                    quantitative_benefits={"revenue": 50000},
                    qualitative_benefits=["Good"]
                ),
                implementation_years=-5
            )
        assert "must be at least 1" in str(exc_info.value)

    def test_discount_rate_valid(self):
        """Test valid discount rate (0-50%)"""
        request = CostBenefitRequest(
            cost_breakdown=CostBreakdown(capex=100000),
            expected_benefits=BenefitAnalysis(
                quantitative_benefits={"revenue": 50000},
                qualitative_benefits=["Good"]
            ),
            discount_rate=0.15
        )
        assert request.discount_rate == 0.15

    def test_discount_rate_zero(self):
        """Test zero discount rate (valid)"""
        request = CostBenefitRequest(
            cost_breakdown=CostBreakdown(capex=100000),
            expected_benefits=BenefitAnalysis(
                quantitative_benefits={"revenue": 50000},
                qualitative_benefits=["Good"]
            ),
            discount_rate=0.0
        )
        assert request.discount_rate == 0.0

    def test_discount_rate_max(self):
        """Test maximum discount rate (50%)"""
        request = CostBenefitRequest(
            cost_breakdown=CostBreakdown(capex=100000),
            expected_benefits=BenefitAnalysis(
                quantitative_benefits={"revenue": 50000},
                qualitative_benefits=["Good"]
            ),
            discount_rate=0.5
        )
        assert request.discount_rate == 0.5

    def test_discount_rate_invalid_too_high(self):
        """Test discount rate > 50% raises error"""
        with pytest.raises(ValidationError) as exc_info:
            CostBenefitRequest(
                cost_breakdown=CostBreakdown(capex=100000),
                expected_benefits=BenefitAnalysis(
                    quantitative_benefits={"revenue": 50000},
                    qualitative_benefits=["Good"]
                ),
                discount_rate=0.51
            )
        assert "cannot exceed 50%" in str(exc_info.value)

    def test_discount_rate_negative(self):
        """Test negative discount rate raises error"""
        with pytest.raises(ValidationError) as exc_info:
            CostBenefitRequest(
                cost_breakdown=CostBreakdown(capex=100000),
                expected_benefits=BenefitAnalysis(
                    quantitative_benefits={"revenue": 50000},
                    qualitative_benefits=["Good"]
                ),
                discount_rate=-0.1
            )
        assert "cannot be negative" in str(exc_info.value)


class TestStrategyCreateValidation:
    """Test StrategyCreate validation"""

    def test_strategy_name_valid(self):
        """Test valid strategy name"""
        strategy = StrategyCreate(
            tenant_id="test-tenant",
            name="Valid Strategy Name",
            strategy_type=StrategyType.RECOVERY,
            objective="Clear objective statement here",
            scope=["Finance", "IT"],
            risk_mitigation=["Risk 1"]
        )
        assert strategy.name == "Valid Strategy Name"

    def test_strategy_name_too_short(self):
        """Test name < 3 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            StrategyCreate(
                tenant_id="test-tenant",
                name="AB",  # Only 2 characters
                strategy_type=StrategyType.RECOVERY,
                objective="Clear objective statement",
                scope=["Finance"],
                risk_mitigation=["Risk 1"]
            )
        assert "at least 3 characters" in str(exc_info.value)

    def test_strategy_name_whitespace_trimmed(self):
        """Test name with leading/trailing whitespace is trimmed"""
        strategy = StrategyCreate(
            tenant_id="test-tenant",
            name="  Valid Name  ",
            strategy_type=StrategyType.RECOVERY,
            objective="Clear objective",
            scope=["Finance"],
            risk_mitigation=["Risk 1"]
        )
        assert strategy.name == "Valid Name"

    def test_objective_valid(self):
        """Test valid objective (min 10 chars)"""
        strategy = StrategyCreate(
            tenant_id="test-tenant",
            name="Strategy Name",
            strategy_type=StrategyType.RECOVERY,
            objective="This is a clear and detailed objective statement",
            scope=["Finance"],
            risk_mitigation=["Risk 1"]
        )
        assert len(strategy.objective) >= 10

    def test_objective_too_short(self):
        """Test objective < 10 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            StrategyCreate(
                tenant_id="test-tenant",
                name="Strategy Name",
                strategy_type=StrategyType.RECOVERY,
                objective="Short",  # Only 5 characters
                scope=["Finance"],
                risk_mitigation=["Risk 1"]
            )
        assert "at least 10 characters" in str(exc_info.value)

    def test_scope_required(self):
        """Test scope is required (at least 1 item)"""
        with pytest.raises(ValidationError) as exc_info:
            StrategyCreate(
                tenant_id="test-tenant",
                name="Strategy Name",
                strategy_type=StrategyType.RECOVERY,
                objective="Clear objective statement",
                scope=[],  # Empty scope
                risk_mitigation=["Risk 1"]
            )
        assert "At least one scope item" in str(exc_info.value)

    def test_scope_valid(self):
        """Test valid scope with multiple items"""
        strategy = StrategyCreate(
            tenant_id="test-tenant",
            name="Strategy Name",
            strategy_type=StrategyType.RECOVERY,
            objective="Clear objective",
            scope=["Finance", "IT", "Operations"],
            risk_mitigation=["Risk 1"]
        )
        assert len(strategy.scope) == 3


class TestCostBreakdownValidation:
    """Test CostBreakdown validation"""

    def test_all_costs_non_negative(self):
        """Test all cost fields must be non-negative"""
        cost_breakdown = CostBreakdown(
            capex=100000,
            opex=50000,
            training=10000,
            maintenance=5000,
            other=2000
        )
        assert cost_breakdown.capex >= 0
        assert cost_breakdown.opex >= 0

    def test_negative_capex(self):
        """Test negative capex raises error"""
        with pytest.raises(ValidationError) as exc_info:
            CostBreakdown(capex=-1000)
        assert "cannot be negative" in str(exc_info.value)

    def test_negative_opex(self):
        """Test negative opex raises error"""
        with pytest.raises(ValidationError) as exc_info:
            CostBreakdown(opex=-5000)
        assert "cannot be negative" in str(exc_info.value)

    def test_cost_exceeds_limit(self):
        """Test cost exceeding 1 billion raises error"""
        with pytest.raises(ValidationError) as exc_info:
            CostBreakdown(capex=1_500_000_000)  # 1.5 billion
        assert "exceeds reasonable limit" in str(exc_info.value)

    def test_currency_code_valid(self):
        """Test valid 3-letter currency code"""
        cost_breakdown = CostBreakdown(
            capex=100000,
            currency="USD"
        )
        assert cost_breakdown.currency == "USD"

    def test_currency_code_uppercase(self):
        """Test currency code is converted to uppercase"""
        cost_breakdown = CostBreakdown(
            capex=100000,
            currency="usd"
        )
        assert cost_breakdown.currency == "USD"

    def test_currency_code_invalid_length(self):
        """Test invalid currency code length"""
        with pytest.raises(ValidationError) as exc_info:
            CostBreakdown(capex=100000, currency="US")
        assert "3-letter ISO code" in str(exc_info.value)

    def test_currency_code_non_alpha(self):
        """Test currency code with non-letters"""
        with pytest.raises(ValidationError) as exc_info:
            CostBreakdown(capex=100000, currency="U$D")
        assert "must contain only letters" in str(exc_info.value)


class TestBenefitAnalysisValidation:
    """Test BenefitAnalysis validation"""

    def test_quantitative_benefits_required(self):
        """Test at least one quantitative benefit is required"""
        with pytest.raises(ValidationError) as exc_info:
            BenefitAnalysis(
                quantitative_benefits={},
                qualitative_benefits=["Good reputation"]
            )
        assert "At least one quantitative benefit" in str(exc_info.value)

    def test_quantitative_benefits_valid(self):
        """Test valid quantitative benefits"""
        benefits = BenefitAnalysis(
            quantitative_benefits={
                "revenue_protection": 100000,
                "cost_savings": 50000
            },
            qualitative_benefits=["Good reputation"]
        )
        assert len(benefits.quantitative_benefits) == 2

    def test_quantitative_benefit_negative_value(self):
        """Test negative benefit value raises error"""
        with pytest.raises(ValidationError) as exc_info:
            BenefitAnalysis(
                quantitative_benefits={"revenue": -50000},
                qualitative_benefits=["Good"]
            )
        assert "cannot be negative" in str(exc_info.value)

    def test_qualitative_benefits_required(self):
        """Test at least one qualitative benefit is required"""
        with pytest.raises(ValidationError) as exc_info:
            BenefitAnalysis(
                quantitative_benefits={"revenue": 50000},
                qualitative_benefits=[]
            )
        assert "At least one qualitative benefit" in str(exc_info.value)

    def test_qualitative_benefit_too_short(self):
        """Test qualitative benefit must be at least 3 chars"""
        with pytest.raises(ValidationError) as exc_info:
            BenefitAnalysis(
                quantitative_benefits={"revenue": 50000},
                qualitative_benefits=["OK"]  # Only 2 characters
            )
        assert "at least 3 characters" in str(exc_info.value)

    def test_risk_reduction_percentage_valid(self):
        """Test valid risk reduction percentage (0-100%)"""
        benefits = BenefitAnalysis(
            quantitative_benefits={"revenue": 50000},
            qualitative_benefits=["Good reputation"],
            risk_reduction_percentage=75.0
        )
        assert benefits.risk_reduction_percentage == 75.0

    def test_risk_reduction_percentage_invalid_high(self):
        """Test risk reduction > 100% raises error"""
        with pytest.raises(ValidationError) as exc_info:
            BenefitAnalysis(
                quantitative_benefits={"revenue": 50000},
                qualitative_benefits=["Good"],
                risk_reduction_percentage=101.0
            )
        assert "between 0% and 100%" in str(exc_info.value)

    def test_risk_reduction_percentage_negative(self):
        """Test negative risk reduction raises error"""
        with pytest.raises(ValidationError) as exc_info:
            BenefitAnalysis(
                quantitative_benefits={"revenue": 50000},
                qualitative_benefits=["Good"],
                risk_reduction_percentage=-10.0
            )
        assert "between 0% and 100%" in str(exc_info.value)


class TestROIAnalysisValidation:
    """Test ROIAnalysis validation"""

    def test_roi_analysis_valid(self):
        """Test valid ROI analysis"""
        roi = ROIAnalysis(
            total_investment=100000,
            annual_savings=30000,
            payback_period_months=48,
            roi_percentage=50.0
        )
        assert roi.total_investment == 100000
        assert roi.roi_percentage == 50.0

    def test_total_investment_negative(self):
        """Test negative total investment raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ROIAnalysis(
                total_investment=-100000,
                annual_savings=30000,
                payback_period_months=48,
                roi_percentage=50.0
            )
        assert "cannot be negative" in str(exc_info.value)

    def test_annual_savings_negative(self):
        """Test negative annual savings raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ROIAnalysis(
                total_investment=100000,
                annual_savings=-30000,
                payback_period_months=48,
                roi_percentage=50.0
            )
        assert "cannot be negative" in str(exc_info.value)

    def test_payback_period_negative(self):
        """Test negative payback period raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ROIAnalysis(
                total_investment=100000,
                annual_savings=30000,
                payback_period_months=-10,
                roi_percentage=50.0
            )
        assert "cannot be negative" in str(exc_info.value)

    def test_payback_period_exceeds_limit(self):
        """Test payback period > 600 months raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ROIAnalysis(
                total_investment=100000,
                annual_savings=30000,
                payback_period_months=601,
                roi_percentage=50.0
            )
        assert "exceeds reasonable timeframe" in str(exc_info.value)

    def test_roi_percentage_can_be_negative(self):
        """Test ROI percentage can be negative (loss scenario)"""
        roi = ROIAnalysis(
            total_investment=100000,
            annual_savings=10000,
            payback_period_months=120,
            roi_percentage=-25.0  # Negative ROI is valid
        )
        assert roi.roi_percentage == -25.0


class TestResourceRequirementValidation:
    """Test ResourceRequirement validation"""

    def test_resource_requirement_valid(self):
        """Test valid resource requirement"""
        resource = ResourceRequirement(
            resource_type="Technology",
            description="High-availability server cluster",
            quantity=5,
            estimated_cost=50000,
            criticality="high"
        )
        assert resource.resource_type == "Technology"
        assert resource.quantity == 5

    def test_resource_type_empty(self):
        """Test empty resource type raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ResourceRequirement(
                resource_type="",
                description="Valid description",
                criticality="high"
            )
        assert "cannot be empty" in str(exc_info.value)

    def test_description_too_short(self):
        """Test description < 3 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ResourceRequirement(
                resource_type="Technology",
                description="AB",  # Too short
                criticality="high"
            )
        assert "at least 3 characters" in str(exc_info.value)

    def test_quantity_negative(self):
        """Test negative quantity raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ResourceRequirement(
                resource_type="Technology",
                description="Valid description",
                quantity=-5,
                criticality="high"
            )
        assert "cannot be negative" in str(exc_info.value)

    def test_estimated_cost_negative(self):
        """Test negative estimated cost raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ResourceRequirement(
                resource_type="Technology",
                description="Valid description",
                estimated_cost=-1000,
                criticality="high"
            )
        assert "cannot be negative" in str(exc_info.value)


class TestImplementationPhaseValidation:
    """Test ImplementationPhase validation"""

    def test_implementation_phase_valid(self):
        """Test valid implementation phase"""
        phase = ImplementationPhase(
            phase_number=1,
            phase_name="Planning Phase",
            description="Initial planning and preparation activities"
        )
        assert phase.phase_number == 1
        assert phase.phase_name == "Planning Phase"

    def test_phase_number_too_low(self):
        """Test phase number < 1 raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ImplementationPhase(
                phase_number=0,
                phase_name="Phase",
                description="Description here"
            )
        assert "must be at least 1" in str(exc_info.value)

    def test_phase_number_too_high(self):
        """Test phase number > 100 raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ImplementationPhase(
                phase_number=101,
                phase_name="Phase",
                description="Description here"
            )
        assert "exceeds reasonable limit" in str(exc_info.value)

    def test_end_date_before_start_date(self):
        """Test end date before start date raises error"""
        start = datetime(2025, 1, 1)
        end = datetime(2024, 12, 31)

        with pytest.raises(ValidationError) as exc_info:
            ImplementationPhase(
                phase_number=1,
                phase_name="Phase",
                description="Description here",
                start_date=start,
                end_date=end
            )
        assert "cannot be before start date" in str(exc_info.value)

    def test_dates_valid(self):
        """Test valid start and end dates"""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 6, 30)

        phase = ImplementationPhase(
            phase_number=1,
            phase_name="Phase",
            description="Description here",
            start_date=start,
            end_date=end
        )
        assert phase.start_date < phase.end_date
