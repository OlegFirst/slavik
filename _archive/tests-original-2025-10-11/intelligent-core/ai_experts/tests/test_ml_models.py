"""
Tests for ML Models
"""

import pytest
from ..ml.predictive_models import WorkflowPredictor
from ..ml.anomaly_detection import AnomalyDetector


class TestWorkflowPredictor:
    """Test Workflow Predictor"""

    @pytest.mark.asyncio
    async def test_workflow_predictor_initialization(self):
        """Test predictor initialization"""
        predictor = WorkflowPredictor()

        assert predictor is not None

    @pytest.mark.asyncio
    async def test_heuristic_prediction(self, mock_org_context):
        """Test heuristic prediction (when models not trained)"""
        predictor = WorkflowPredictor()

        prediction = await predictor.predict_journey(
            org_context=mock_org_context,
            current_state='bia',
            current_progress={'current_stage_index': 0, 'total_stages': 6}
        )

        assert 'current_stage_prediction' in prediction
        assert 'stuck_probability' in prediction
        assert 'expert_help_needed' in prediction


class TestAnomalyDetector:
    """Test Anomaly Detector"""

    @pytest.mark.asyncio
    async def test_anomaly_detector_initialization(self):
        """Test anomaly detector initialization"""
        detector = AnomalyDetector()

        assert detector is not None

    @pytest.mark.asyncio
    async def test_workflow_anomaly_detection(self, mock_workflow_data):
        """Test workflow anomaly detection"""
        detector = AnomalyDetector()

        results = await detector.detect_workflow_anomalies(
            workflow_data=mock_workflow_data
        )

        assert 'anomalies_detected' in results
        assert 'risk_level' in results
        assert 'recommendations' in results
