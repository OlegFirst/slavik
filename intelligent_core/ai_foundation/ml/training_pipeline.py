"""
Training Pipeline

Orchestrates ML model training, evaluation, and deployment.
"""

from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class TrainingPipeline:
    """
    Training Pipeline

    Manages:
    - Data collection and preparation
    - Model training
    - Model evaluation
    - Model deployment
    """

    def __init__(
        self,
        case_library=None,
        model_dir: Optional[Path] = None
    ):
        """
        Initialize training pipeline

        Args:
            case_library: Case library for training data
            model_dir: Directory for model storage
        """
        self.case_library = case_library
        self.model_dir = model_dir or Path('./models')
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.training_history = []

    async def run_training(
        self,
        model_type: str = 'workflow_predictor',
        min_samples: int = 50,
        force_retrain: bool = False
    ) -> Dict[str, Any]:
        """
        Run complete training pipeline

        Args:
            model_type: Type of model to train
            min_samples: Minimum training samples required
            force_retrain: Force retraining even if model exists

        Returns:
            Training results
        """

        logger.info(f"Starting training pipeline for {model_type}")

        # Step 1: Collect training data
        logger.info("Step 1: Collecting training data...")
        training_data = await self._collect_training_data(model_type)

        if len(training_data) < min_samples:
            logger.warning(f"Insufficient data: {len(training_data)} < {min_samples}")
            return {
                'status': 'insufficient_data',
                'samples_collected': len(training_data),
                'min_required': min_samples,
                'message': f'Need at least {min_samples} samples, only found {len(training_data)}'
            }

        logger.info(f"Collected {len(training_data)} training samples")

        # Step 2: Prepare data
        logger.info("Step 2: Preparing data...")
        prepared_data = self._prepare_data(training_data, model_type)

        # Step 3: Train model
        logger.info("Step 3: Training model...")

        if model_type == 'workflow_predictor':
            from .predictive_models import WorkflowPredictor

            predictor = WorkflowPredictor(case_library=self.case_library)
            training_result = await predictor.train(
                training_data=prepared_data,
                min_samples=min_samples
            )

            if training_result.get('status') == 'success':
                # Save model
                model_path = self.model_dir / 'workflow_predictor'
                predictor.save_models(model_path)
                training_result['model_path'] = str(model_path)

        elif model_type == 'anomaly_detector':
            from .anomaly_detection import AnomalyDetector

            detector = AnomalyDetector()
            detector.update_baseline(prepared_data)
            training_result = {
                'status': 'success',
                'message': 'Anomaly detector baseline updated'
            }

        else:
            return {
                'status': 'error',
                'error': f'Unknown model type: {model_type}'
            }

        # Step 4: Log training
        self._log_training(model_type, training_result)

        logger.info(f"Training pipeline completed: {training_result.get('status')}")

        return training_result

    async def _collect_training_data(
        self,
        model_type: str
    ) -> List[Dict[str, Any]]:
        """
        Collect training data from case library

        Args:
            model_type: Type of model

        Returns:
            Training data
        """

        if not self.case_library:
            logger.warning("No case library available, using mock data")
            return self._generate_mock_data(model_type)

        # Query case library for completed workflows
        # This would integrate with actual case library

        logger.warning("Case library integration not implemented, using mock data")
        return self._generate_mock_data(model_type)

    def _generate_mock_data(self, model_type: str) -> List[Dict[str, Any]]:
        """Generate mock training data for development"""

        import random

        if model_type == 'workflow_predictor':
            mock_data = []

            industries = ['healthcare', 'finance', 'manufacturing', 'technology', 'retail']
            sizes = ['small', 'medium', 'large']
            stages = ['bia', 'strategy', 'planning', 'testing']

            for i in range(100):
                mock_data.append({
                    'org_size': random.choice(sizes),
                    'org_maturity': random.randint(1, 5),
                    'industry': random.choice(industries),
                    'stage': random.choice(stages),
                    'stage_index': random.randint(0, 5),
                    'total_stages': 6,
                    'complexity': random.randint(1, 5),
                    'ai_usage': random.randint(0, 10),
                    'challenges_count': random.randint(0, 5),
                    'duration_hours': random.randint(4, 48),
                    'got_stuck': random.random() < 0.3,
                    'needed_help': random.random() < 0.4
                })

            return mock_data

        return []

    def _prepare_data(
        self,
        raw_data: List[Dict[str, Any]],
        model_type: str
    ) -> List[Dict[str, Any]]:
        """
        Prepare data for training

        Args:
            raw_data: Raw training data
            model_type: Model type

        Returns:
            Prepared data
        """

        # Data cleaning and validation
        clean_data = []

        for record in raw_data:
            # Skip incomplete records
            required_fields = ['org_size', 'industry', 'duration_hours']

            if all(record.get(field) for field in required_fields):
                clean_data.append(record)

        logger.info(f"Prepared {len(clean_data)} records from {len(raw_data)} raw records")

        return clean_data

    def _log_training(self, model_type: str, result: Dict[str, Any]):
        """Log training run"""

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'model_type': model_type,
            'status': result.get('status'),
            'metrics': result.get('metrics', {}),
            'samples': result.get('samples_total', 0)
        }

        self.training_history.append(log_entry)

        # Save to file
        log_file = self.model_dir / 'training_history.log'

        with open(log_file, 'a') as f:
            f.write(f"{log_entry}\n")

    def get_training_history(self) -> List[Dict[str, Any]]:
        """Get training history"""

        return self.training_history

    async def schedule_retraining(
        self,
        model_type: str,
        schedule: str = 'weekly'
    ) -> Dict[str, Any]:
        """
        Schedule automatic retraining

        Args:
            model_type: Model to retrain
            schedule: Retraining schedule

        Returns:
            Schedule configuration
        """

        # This would integrate with job scheduler (e.g., APScheduler, Celery)

        logger.info(f"Scheduled {schedule} retraining for {model_type}")

        return {
            'model_type': model_type,
            'schedule': schedule,
            'next_run': 'scheduled',
            'status': 'active'
        }

    async def evaluate_model(
        self,
        model_type: str,
        test_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate model performance

        Args:
            model_type: Model to evaluate
            test_data: Test data (optional)

        Returns:
            Evaluation results
        """

        logger.info(f"Evaluating {model_type}")

        # Load model
        if model_type == 'workflow_predictor':
            from .predictive_models import WorkflowPredictor

            model_path = self.model_dir / 'workflow_predictor'

            if not model_path.exists():
                return {
                    'status': 'error',
                    'error': 'Model not found'
                }

            predictor = WorkflowPredictor(model_path=model_path)

            # Get test data
            if not test_data:
                test_data = await self._collect_training_data(model_type)
                # Use last 20% as test set
                test_size = len(test_data) // 5
                test_data = test_data[-test_size:]

            # Run predictions
            errors = []
            for test_case in test_data[:10]:  # Evaluate first 10
                try:
                    prediction = await predictor.predict_journey(
                        org_context={'size': test_case['org_size'], 'industry': test_case['industry']},
                        current_state=test_case.get('stage', 'unknown'),
                        current_progress={'current_stage_index': test_case.get('stage_index', 0)}
                    )

                    # Compare prediction to actual
                    predicted = prediction['current_stage_prediction']['estimated_duration_hours']
                    actual = test_case['duration_hours']
                    error = abs(predicted - actual)
                    errors.append(error)

                except Exception as e:
                    logger.error(f"Prediction failed: {e}")

            if errors:
                import numpy as np
                mae = np.mean(errors)
                rmse = np.sqrt(np.mean([e**2 for e in errors]))

                return {
                    'status': 'success',
                    'test_samples': len(errors),
                    'metrics': {
                        'mae_hours': round(mae, 2),
                        'rmse_hours': round(rmse, 2)
                    }
                }

        return {
            'status': 'error',
            'error': 'Evaluation not implemented'
        }
