"""
Test Cost-Benefit Analysis Calculations
Critical business logic tests for NPV, payback period, and recommendations
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock

from services.business_logic import StrategyService
from models.domain import CostBenefitRequest, CostBreakdown, BenefitAnalysis
from models.database import Strategy, StrategyType, StrategyPhase, StrategyStatus


class TestNPVCalculation:
    """Test Net Present Value calculations"""

    def setup_method(self):
        """Setup test dependencies"""
        self.mock_repo = Mock()
        self.service = StrategyService(self.mock_repo)

    def test_npv_calculation_basic(self):
        """Test NPV with known values - should return positive NPV"""
        # Initial: 100K, Benefits: 30K/year, Costs: 5K/year, Years: 5, Rate: 10%
        # Net cash flow per year: 25K
        # NPV = -100,000 + 25,000/(1.1) + 25,000/(1.1)^2 + ... + 25,000/(1.1)^5
        # Expected NPV ≈ -100,000 + 94,770 ≈ -5,230 (slight loss)

        npv = self.service._calculate_npv(
            initial_investment=100000,
            annual_benefits=30000,
            annual_costs=5000,
            years=5,
            discount_rate=0.10
        )

        # With 10% discount rate, this investment doesn't quite break even
        assert npv < 0, "NPV should be negative with high discount rate"
        assert npv > -10000, "NPV should be close to break-even"
        assert abs(npv - (-5230)) < 500, "NPV calculation accuracy check"

    def test_npv_calculation_positive(self):
        """Test NPV with profitable investment"""
        # Initial: 50K, Benefits: 30K/year, Costs: 5K/year, Years: 5, Rate: 5%
        # Net cash flow per year: 25K
        # Expected positive NPV

        npv = self.service._calculate_npv(
            initial_investment=50000,
            annual_benefits=30000,
            annual_costs=5000,
            years=5,
            discount_rate=0.05
        )

        assert npv > 0, "NPV should be positive for profitable investment"
        assert npv > 50000, "NPV should exceed initial investment"
        # Expected: ~58,144
        assert abs(npv - 58144) < 1000, "NPV should be approximately 58,144"

    def test_npv_negative(self):
        """Test NPV with costs exceeding benefits"""
        # Initial: 100K, Benefits: 10K/year, Costs: 15K/year (net -5K/year)
        # This investment loses money every year

        npv = self.service._calculate_npv(
            initial_investment=100000,
            annual_benefits=10000,
            annual_costs=15000,
            years=5,
            discount_rate=0.10
        )

        assert npv < -100000, "NPV should be significantly negative"
        # Expected: approximately -118,954
        assert npv < -115000, "NPV should reflect cumulative losses"

    def test_npv_zero_discount_rate(self):
        """Test NPV with zero discount rate (no time value of money)"""
        # Initial: 100K, Benefits: 30K/year, Costs: 5K/year, Years: 5, Rate: 0%
        # NPV = -100,000 + (25,000 * 5) = 25,000

        npv = self.service._calculate_npv(
            initial_investment=100000,
            annual_benefits=30000,
            annual_costs=5000,
            years=5,
            discount_rate=0.0
        )

        assert npv == 25000, "NPV with zero discount should be simple sum"

    def test_npv_high_discount_rate(self):
        """Test NPV with high discount rate (30%)"""
        # High discount rate should significantly reduce NPV

        npv = self.service._calculate_npv(
            initial_investment=100000,
            annual_benefits=50000,
            annual_costs=10000,
            years=5,
            discount_rate=0.30
        )

        # Even with 40K net annual cash flow, high discount reduces value
        assert npv < 50000, "High discount rate should significantly reduce NPV"

    def test_npv_long_term(self):
        """Test NPV over longer time period"""
        # 20 years investment period

        npv = self.service._calculate_npv(
            initial_investment=200000,
            annual_benefits=50000,
            annual_costs=20000,
            years=20,
            discount_rate=0.08
        )

        # Long term with steady cash flow should be profitable
        assert npv > 0, "Long-term investment should have positive NPV"
        assert npv > 100000, "NPV should be substantial over 20 years"


class TestPaybackPeriodCalculation:
    """Test Payback Period calculations"""

    def setup_method(self):
        """Setup test dependencies"""
        self.mock_repo = Mock()
        self.service = StrategyService(self.mock_repo)

    def test_payback_period_simple(self):
        """Test payback period with simple values"""
        # Initial: 100K, Net cash flow: 25K/year
        # Expected: 48 months (4 years)

        payback = self.service._calculate_payback_period(
            initial_investment=100000,
            annual_net_cash_flow=25000,
            discount_rate=0.0
        )

        assert payback == 48, "Payback should be 48 months without discounting"

    def test_payback_period_with_discounting(self):
        """Test payback period with discount rate"""
        # Initial: 100K, Net cash flow: 25K/year, Discount: 10%
        # With discounting, payback takes longer

        payback = self.service._calculate_payback_period(
            initial_investment=100000,
            annual_net_cash_flow=25000,
            discount_rate=0.10
        )

        # Should take longer than 48 months due to discounting
        assert payback > 48, "Discounted payback should be longer"
        assert payback < 100, "Should still pay back in reasonable time"

    def test_payback_period_quick_return(self):
        """Test payback period with high annual returns"""
        # Initial: 50K, Net cash flow: 50K/year
        # Expected: 12 months

        payback = self.service._calculate_payback_period(
            initial_investment=50000,
            annual_net_cash_flow=50000,
            discount_rate=0.0
        )

        assert payback == 12, "Should pay back in exactly 12 months"

    def test_payback_period_never(self):
        """Test when investment never pays back (negative cash flow)"""

        payback = self.service._calculate_payback_period(
            initial_investment=100000,
            annual_net_cash_flow=-10000,  # Losing money
            discount_rate=0.10
        )

        assert payback == float('inf'), "Should return infinity for negative cash flow"

    def test_payback_period_zero_cash_flow(self):
        """Test when cash flow is zero"""

        payback = self.service._calculate_payback_period(
            initial_investment=100000,
            annual_net_cash_flow=0,
            discount_rate=0.10
        )

        assert payback == float('inf'), "Should return infinity for zero cash flow"

    def test_payback_period_exceeds_max(self):
        """Test when payback exceeds maximum period"""
        # Initial: 1M, Net cash flow: 1K/year
        # Would take 1000 years, exceeds max_years (20)

        payback = self.service._calculate_payback_period(
            initial_investment=1000000,
            annual_net_cash_flow=1000,
            discount_rate=0.0,
            max_years=20
        )

        assert payback == 999, "Should return 999 when exceeding max years"

    def test_payback_period_fractional_month(self):
        """Test payback with fractional months"""
        # Initial: 100K, Net cash flow: 30K/year
        # Expected: 40 months (3 years 4 months)

        payback = self.service._calculate_payback_period(
            initial_investment=100000,
            annual_net_cash_flow=30000,
            discount_rate=0.0
        )

        assert payback == 40, "Should handle fractional months correctly"


class TestRecommendationLogic:
    """Test recommendation determination logic"""

    def setup_method(self):
        """Setup test dependencies"""
        self.mock_repo = Mock()
        self.service = StrategyService(self.mock_repo)

    def test_recommendation_proceed(self):
        """Test 'proceed' recommendation for excellent investments"""
        # cost_benefit_ratio >= 2.0 AND ROI >= 50%

        recommendation = self.service._determine_recommendation(
            cost_benefit_ratio=2.5,
            roi_percentage=75.0
        )

        assert recommendation == "proceed", "Should recommend proceed for strong investment"

    def test_recommendation_proceed_boundary(self):
        """Test 'proceed' at boundary conditions"""
        # Exactly at thresholds

        recommendation = self.service._determine_recommendation(
            cost_benefit_ratio=2.0,
            roi_percentage=50.0
        )

        assert recommendation == "proceed", "Should recommend proceed at exact thresholds"

    def test_recommendation_review_good_roi(self):
        """Test 'review' recommendation for moderate investments"""
        # cost_benefit_ratio >= 1.0 but < 2.0, ROI >= 0

        recommendation = self.service._determine_recommendation(
            cost_benefit_ratio=1.5,
            roi_percentage=25.0
        )

        assert recommendation == "review", "Should recommend review for moderate investment"

    def test_recommendation_review_break_even(self):
        """Test 'review' recommendation at break-even"""

        recommendation = self.service._determine_recommendation(
            cost_benefit_ratio=1.0,
            roi_percentage=0.0
        )

        assert recommendation == "review", "Should recommend review at break-even"

    def test_recommendation_reject_negative_roi(self):
        """Test 'reject' recommendation for negative ROI"""

        recommendation = self.service._determine_recommendation(
            cost_benefit_ratio=0.8,
            roi_percentage=-20.0
        )

        assert recommendation == "reject", "Should recommend reject for negative ROI"

    def test_recommendation_reject_low_ratio(self):
        """Test 'reject' recommendation for poor cost-benefit ratio"""

        recommendation = self.service._determine_recommendation(
            cost_benefit_ratio=0.5,
            roi_percentage=-50.0
        )

        assert recommendation == "reject", "Should recommend reject for poor ratio"

    def test_recommendation_reject_boundary(self):
        """Test 'reject' at boundary (just below break-even)"""

        recommendation = self.service._determine_recommendation(
            cost_benefit_ratio=0.99,
            roi_percentage=-1.0
        )

        assert recommendation == "reject", "Should recommend reject below break-even"


class TestConfidenceAssessment:
    """Test confidence level assessment"""

    def setup_method(self):
        """Setup test dependencies"""
        self.mock_repo = Mock()
        self.service = StrategyService(self.mock_repo)

    def test_confidence_high(self):
        """Test high confidence with 3+ quantitative benefits"""

        cost_benefit_data = CostBenefitRequest(
            cost_breakdown=CostBreakdown(capex=100000),
            expected_benefits=BenefitAnalysis(
                quantitative_benefits={
                    "revenue_protection": 50000,
                    "cost_savings": 30000,
                    "efficiency": 20000
                },
                qualitative_benefits=["Improved reputation"]
            ),
            implementation_years=5
        )

        confidence = self.service._assess_confidence(cost_benefit_data)

        assert confidence == "high", "Should return high confidence with 3+ metrics"

    def test_confidence_medium(self):
        """Test medium confidence with 1-2 quantitative benefits"""

        cost_benefit_data = CostBenefitRequest(
            cost_breakdown=CostBreakdown(capex=100000),
            expected_benefits=BenefitAnalysis(
                quantitative_benefits={
                    "revenue_protection": 50000
                },
                qualitative_benefits=["Improved reputation"]
            ),
            implementation_years=5
        )

        confidence = self.service._assess_confidence(cost_benefit_data)

        assert confidence == "medium", "Should return medium confidence with 1-2 metrics"

    def test_confidence_low(self):
        """Test low confidence with no quantitative benefits"""

        cost_benefit_data = CostBenefitRequest(
            cost_breakdown=CostBreakdown(capex=100000),
            expected_benefits=BenefitAnalysis(
                quantitative_benefits={},  # Empty but validator requires at least one
                qualitative_benefits=["Improved reputation"]
            ),
            implementation_years=5
        )

        # Note: This would actually fail validation, but testing the logic
        # Let's use a mock instead
        mock_request = Mock()
        mock_request.expected_benefits.quantitative_benefits = {}

        confidence = self.service._assess_confidence(mock_request)

        assert confidence == "low", "Should return low confidence with no metrics"


@pytest.mark.asyncio
class TestCostBenefitIntegration:
    """Integration tests for full cost-benefit calculation flow"""

    async def test_calculate_cost_benefit_full_flow(self, db_session):
        """Test complete cost-benefit calculation"""
        # Create mock repository
        mock_repo = AsyncMock()
        service = StrategyService(mock_repo)

        # Create a strategy
        strategy_id = uuid4()
        strategy = Strategy(
            id=strategy_id,
            tenant_id="test-tenant",
            strategy_number="STRAT-2025-TEST01",
            name="Test Strategy",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Test objective",
            created_by="test-user"
        )

        # Mock repository methods
        mock_repo.get_by_id.return_value = strategy
        mock_repo.update.return_value = strategy

        # Create cost-benefit request
        cost_benefit_request = CostBenefitRequest(
            cost_breakdown=CostBreakdown(
                capex=100000,
                opex=5000,
                training=10000,
                maintenance=3000,
                other=2000
            ),
            expected_benefits=BenefitAnalysis(
                quantitative_benefits={
                    "annual_revenue_protection": 80000,
                    "cost_avoidance": 40000,
                    "efficiency_gains": 20000
                },
                qualitative_benefits=[
                    "Improved customer satisfaction",
                    "Enhanced compliance"
                ]
            ),
            implementation_years=5,
            discount_rate=0.10
        )

        # Calculate cost-benefit
        result = await service.calculate_cost_benefit(
            strategy_id=strategy_id,
            cost_benefit_data=cost_benefit_request
        )

        # Assertions
        assert result.strategy_id == str(strategy_id)
        assert result.total_cost > 0
        assert result.total_benefits == 140000  # Sum of quantitative benefits
        assert result.cost_benefit_ratio > 0
        assert result.roi_analysis is not None
        assert result.recommendation in ["proceed", "review", "reject"]
        assert result.confidence_level in ["high", "medium", "low"]

        # Verify repository was called
        mock_repo.get_by_id.assert_called_once_with(strategy_id)
        assert mock_repo.update.call_count == 1

    async def test_calculate_cost_benefit_strategy_not_found(self):
        """Test cost-benefit calculation with non-existent strategy"""
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None
        service = StrategyService(mock_repo)

        cost_benefit_request = CostBenefitRequest(
            cost_breakdown=CostBreakdown(capex=100000),
            expected_benefits=BenefitAnalysis(
                quantitative_benefits={"revenue": 50000},
                qualitative_benefits=["Good"]
            )
        )

        with pytest.raises(ValueError, match="Strategy not found"):
            await service.calculate_cost_benefit(
                strategy_id=uuid4(),
                cost_benefit_data=cost_benefit_request
            )
