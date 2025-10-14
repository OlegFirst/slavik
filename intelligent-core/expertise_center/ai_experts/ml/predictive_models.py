"""
Predictive Models

ML models for workflow prediction:
- Stage duration prediction (Random Forest Regressor)
- Stuck probability prediction (Gradient Boosting Classifier)
- Expert help needed prediction
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
import numpy as np
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class WorkflowPredictor:
    """
    Workflow Prediction Model

    Predicts:
    - Stage duration (hours)
    - Stuck probability (0-1)
    - Expert help needed (boolean)
    - Total completion time

    Uses:
    - Random Forest for duration regression
    - Gradient Boosting for classification
    """

    def __init__(
        self,
        case_library=None,
        model_path: Optional[Path] = None
    ):
        """
        Initialize workflow predictor

        Args:
            case_library: Historical case data for training
            model_path: Path to saved models
        """
        self.case_library = case_library
        self.model_path = model_path

        # Models (initialized on training or loading)
        self.duration_model = None
        self.stuck_model = None
        self.help_model = None

        # Feature configuration
        self.feature_config = {
            'org_features': ['size', 'maturity', 'industry_encoded'],
            'stage_features': ['stage_index', 'total_stages', 'complexity'],
            'historical_features': ['ai_usage', 'challenges_count']
        }

        # Industry encoding
        self.industry_encoder = {
            'healthcare': 0,
            'finance': 1,
            'manufacturing': 2,
            'technology': 3,
            'retail': 4,
            'other': 5
        }

        # Size encoding
        self.size_encoder = {
            'small': 0,
            'medium': 1,
            'large': 2
        }

        # Load models if path provided
        if model_path and model_path.exists():
            self.load_models(model_path)

    def extract_features(
        self,
        org_context: Dict[str, Any],
        current_state: str,
        current_progress: Dict[str, Any]
    ) -> np.ndarray:
        """
        Extract features from workflow context

        Args:
            org_context: Organization context
            current_state: Current workflow state
            current_progress: Current progress data

        Returns:
            Feature vector
        """

        features = []

        # Organization features
        size = org_context.get('size', 'medium')
        features.append(self.size_encoder.get(size, 1))

        maturity = org_context.get('maturity', 3)
        features.append(maturity)

        industry = org_context.get('industry', 'other')
        features.append(self.industry_encoder.get(industry.lower(), 5))

        # Stage features
        stage_index = current_progress.get('current_stage_index', 0)
        features.append(stage_index)

        total_stages = current_progress.get('total_stages', 6)
        features.append(total_stages)

        complexity = current_progress.get('complexity_score', 3)
        features.append(complexity)

        # Historical features
        ai_usage = current_progress.get('ai_usage_count', 0)
        features.append(ai_usage)

        challenges_count = len(current_progress.get('challenges', []))
        features.append(challenges_count)

        return np.array(features).reshape(1, -1)

    async def predict_journey(
        self,
        org_context: Dict[str, Any],
        current_state: str,
        current_progress: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict workflow journey

        Args:
            org_context: Organization context
            current_state: Current workflow state
            current_progress: Current progress data

        Returns:
            Predictions including timeline, risks, help needs
        """

        # Check if models are trained
        if not self.duration_model:
            logger.warning("Models not trained, using heuristics")
            return self._heuristic_prediction(org_context, current_state, current_progress)

        # Extract features
        features = self.extract_features(org_context, current_state, current_progress)

        # Predict stage duration
        predicted_hours = self.duration_model.predict(features)[0]

        # Predict stuck probability
        stuck_proba = self.stuck_model.predict_proba(features)[0][1]  # Probability of class 1 (stuck)

        # Predict help needed
        help_needed = self.help_model.predict(features)[0] == 1

        # Calculate total completion time
        stages_remaining = current_progress.get('total_stages', 6) - current_progress.get('current_stage_index', 0)
        estimated_total_hours = predicted_hours * stages_remaining

        # Risk assessment
        risk_level = self._assess_risk_level(stuck_proba, help_needed)

        result = {
            'current_stage_prediction': {
                'estimated_duration_hours': round(predicted_hours, 1),
                'confidence': self._calculate_confidence(features)
            },
            'stuck_probability': {
                'probability': round(stuck_proba, 3),
                'risk_level': 'high' if stuck_proba > 0.7 else 'medium' if stuck_proba > 0.4 else 'low'
            },
            'expert_help_needed': help_needed,
            'total_completion_estimate': {
                'estimated_hours': round(estimated_total_hours, 1),
                'estimated_days': round(estimated_total_hours / 8, 1),
                'stages_remaining': stages_remaining
            },
            'risk_assessment': risk_level,
            'recommendations': self._generate_recommendations(stuck_proba, help_needed, predicted_hours)
        }

        return result

    def _heuristic_prediction(
        self,
        org_context: Dict[str, Any],
        current_state: str,
        current_progress: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Heuristic-based prediction when models not available

        Args:
            org_context: Organization context
            current_state: Current state
            current_progress: Current progress

        Returns:
            Heuristic predictions
        """

        # Base hours per stage
        size = org_context.get('size', 'medium')
        base_hours = {
            'small': 8,
            'medium': 16,
            'large': 32
        }.get(size, 16)

        # Adjust for maturity
        maturity = org_context.get('maturity', 3)
        maturity_multiplier = {
            1: 1.5,
            2: 1.2,
            3: 1.0,
            4: 0.8,
            5: 0.6
        }.get(maturity, 1.0)

        predicted_hours = base_hours * maturity_multiplier

        # Stuck probability based on challenges
        challenges = len(current_progress.get('challenges', []))
        stuck_proba = min(0.9, challenges * 0.15)

        # Help needed if low maturity or many challenges
        help_needed = maturity <= 2 or challenges >= 3

        stages_remaining = current_progress.get('total_stages', 6) - current_progress.get('current_stage_index', 0)
        estimated_total_hours = predicted_hours * stages_remaining

        return {
            'current_stage_prediction': {
                'estimated_duration_hours': round(predicted_hours, 1),
                'confidence': 0.6  # Lower confidence for heuristics
            },
            'stuck_probability': {
                'probability': round(stuck_proba, 3),
                'risk_level': 'high' if stuck_proba > 0.7 else 'medium' if stuck_proba > 0.4 else 'low'
            },
            'expert_help_needed': help_needed,
            'total_completion_estimate': {
                'estimated_hours': round(estimated_total_hours, 1),
                'estimated_days': round(estimated_total_hours / 8, 1),
                'stages_remaining': stages_remaining
            },
            'risk_assessment': self._assess_risk_level(stuck_proba, help_needed),
            'recommendations': self._generate_recommendations(stuck_proba, help_needed, predicted_hours),
            'note': 'Predictions based on heuristics (models not trained)'
        }

    def _assess_risk_level(self, stuck_proba: float, help_needed: bool) -> Dict[str, Any]:
        """Assess overall risk level"""

        if stuck_proba > 0.7 or help_needed:
            level = 'high'
            description = 'High risk of delays or getting stuck'
        elif stuck_proba > 0.4:
            level = 'medium'
            description = 'Moderate risk, monitor progress closely'
        else:
            level = 'low'
            description = 'Low risk, progressing normally'

        return {
            'level': level,
            'description': description
        }

    def _calculate_confidence(self, features: np.ndarray) -> float:
        """Calculate prediction confidence"""

        # Simple confidence based on feature completeness
        # In production, use model uncertainty estimates

        confidence = 0.8  # Base confidence

        return confidence

    def _generate_recommendations(
        self,
        stuck_proba: float,
        help_needed: bool,
        predicted_hours: float
    ) -> List[str]:
        """Generate actionable recommendations"""

        recommendations = []

        if stuck_proba > 0.7:
            recommendations.append("High risk of getting stuck - consider scheduling expert consultation")
            recommendations.append("Review similar cases in case library for guidance")

        if help_needed:
            recommendations.append("Expert assistance recommended for this stage")
            recommendations.append("Use AI assistants for initial analysis and drafts")

        if predicted_hours > 24:
            recommendations.append("This stage may take longer than typical - allocate sufficient time")
            recommendations.append("Consider breaking down into smaller sub-tasks")

        if not recommendations:
            recommendations.append("Progress is on track - continue with current approach")

        return recommendations

    async def train(
        self,
        training_data: Optional[List[Dict[str, Any]]] = None,
        min_samples: int = 50
    ) -> Dict[str, Any]:
        """
        Train prediction models

        Args:
            training_data: Training data (uses case_library if not provided)
            min_samples: Minimum samples required for training

        Returns:
            Training results
        """

        # Get training data
        if not training_data:
            if not self.case_library:
                raise ValueError("No training data or case library provided")
            training_data = await self._get_training_data_from_library()

        if len(training_data) < min_samples:
            logger.warning(f"Insufficient training data: {len(training_data)} < {min_samples}")
            return {
                'status': 'insufficient_data',
                'samples': len(training_data),
                'min_required': min_samples
            }

        # Prepare features and targets
        X, y_duration, y_stuck, y_help = self._prepare_training_data(training_data)

        # Train models
        try:
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import r2_score, accuracy_score, mean_absolute_error

            # Split data
            X_train, X_test, y_dur_train, y_dur_test = train_test_split(
                X, y_duration, test_size=0.2, random_state=42
            )
            _, _, y_stuck_train, y_stuck_test = train_test_split(
                X, y_stuck, test_size=0.2, random_state=42
            )
            _, _, y_help_train, y_help_test = train_test_split(
                X, y_help, test_size=0.2, random_state=42
            )

            # Train duration model (Random Forest)
            self.duration_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.duration_model.fit(X_train, y_dur_train)
            dur_pred = self.duration_model.predict(X_test)
            dur_r2 = r2_score(y_dur_test, dur_pred)
            dur_mae = mean_absolute_error(y_dur_test, dur_pred)

            # Train stuck model (Gradient Boosting)
            self.stuck_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
            self.stuck_model.fit(X_train, y_stuck_train)
            stuck_pred = self.stuck_model.predict(X_test)
            stuck_acc = accuracy_score(y_stuck_test, stuck_pred)

            # Train help model (Gradient Boosting)
            self.help_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
            self.help_model.fit(X_train, y_help_train)
            help_pred = self.help_model.predict(X_test)
            help_acc = accuracy_score(y_help_test, help_pred)

            logger.info(f"Models trained: Duration R²={dur_r2:.3f}, Stuck Acc={stuck_acc:.3f}, Help Acc={help_acc:.3f}")

            return {
                'status': 'success',
                'samples_total': len(training_data),
                'samples_train': len(X_train),
                'samples_test': len(X_test),
                'metrics': {
                    'duration_r2': round(dur_r2, 3),
                    'duration_mae_hours': round(dur_mae, 2),
                    'stuck_accuracy': round(stuck_acc, 3),
                    'help_accuracy': round(help_acc, 3)
                }
            }

        except ImportError as e:
            logger.error(f"sklearn not available: {e}")
            return {
                'status': 'error',
                'error': 'sklearn not installed'
            }

    async def _get_training_data_from_library(self) -> List[Dict[str, Any]]:
        """Get training data from case library"""

        # This would query the case library for completed workflows
        # For now, return empty list
        logger.warning("Case library integration not implemented")
        return []

    def _prepare_training_data(
        self,
        data: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare training data

        Args:
            data: Raw training data

        Returns:
            Features (X), Duration labels, Stuck labels, Help labels
        """

        X_list = []
        y_duration = []
        y_stuck = []
        y_help = []

        for case in data:
            # Extract features (same as extract_features but for historical data)
            features = []

            # Org features
            size = case.get('org_size', 'medium')
            features.append(self.size_encoder.get(size, 1))

            maturity = case.get('org_maturity', 3)
            features.append(maturity)

            industry = case.get('industry', 'other')
            features.append(self.industry_encoder.get(industry.lower(), 5))

            # Stage features
            features.append(case.get('stage_index', 0))
            features.append(case.get('total_stages', 6))
            features.append(case.get('complexity', 3))

            # Historical features
            features.append(case.get('ai_usage', 0))
            features.append(case.get('challenges_count', 0))

            X_list.append(features)

            # Labels
            y_duration.append(case.get('duration_hours', 16))
            y_stuck.append(1 if case.get('got_stuck', False) else 0)
            y_help.append(1 if case.get('needed_help', False) else 0)

        X = np.array(X_list)
        return X, np.array(y_duration), np.array(y_stuck), np.array(y_help)

    def save_models(self, path: Path):
        """Save trained models"""

        path.mkdir(parents=True, exist_ok=True)

        if self.duration_model:
            with open(path / 'duration_model.pkl', 'wb') as f:
                pickle.dump(self.duration_model, f)

        if self.stuck_model:
            with open(path / 'stuck_model.pkl', 'wb') as f:
                pickle.dump(self.stuck_model, f)

        if self.help_model:
            with open(path / 'help_model.pkl', 'wb') as f:
                pickle.dump(self.help_model, f)

        logger.info(f"Models saved to {path}")

    def load_models(self, path: Path):
        """Load trained models"""

        try:
            if (path / 'duration_model.pkl').exists():
                with open(path / 'duration_model.pkl', 'rb') as f:
                    self.duration_model = pickle.load(f)

            if (path / 'stuck_model.pkl').exists():
                with open(path / 'stuck_model.pkl', 'rb') as f:
                    self.stuck_model = pickle.load(f)

            if (path / 'help_model.pkl').exists():
                with open(path / 'help_model.pkl', 'rb') as f:
                    self.help_model = pickle.load(f)

            logger.info(f"Models loaded from {path}")

        except Exception as e:
            logger.error(f"Failed to load models: {e}")
