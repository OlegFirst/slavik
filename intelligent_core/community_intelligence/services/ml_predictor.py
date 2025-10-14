"""
ML Predictor Service

Machine Learning predictions based on community case library:
- Success probability prediction
- Duration estimation
- Risk factor identification
- Pattern recognition

Uses sklearn models trained on approved community cases.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging
import numpy as np
import joblib
import os
from pathlib import Path

from ..models.database import CaseContribution, ContributionStatus
from ..config import settings

logger = logging.getLogger(__name__)

# Lazy imports for ML libraries
try:
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    ML_AVAILABLE = True
except ImportError:
    logger.warning("sklearn not available - ML predictions disabled")
    ML_AVAILABLE = False


class MLPredictor:
    """
    ML predictions from case library

    Models:
    - Success predictor: Will workflow complete successfully?
    - Duration predictor: How long will it take?
    - Risk detector: What are the risk factors?
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.models_path = Path(settings.ML_MODEL_PATH)
        self.models_path.mkdir(exist_ok=True)

        # Models
        self.success_model: Optional[RandomForestClassifier] = None
        self.duration_model: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        self.label_encoders: Dict[str, LabelEncoder] = {}

        # Load existing models
        self._load_models()

    def _load_models(self):
        """Load pre-trained models from disk"""
        try:
            success_path = self.models_path / "success_predictor.pkl"
            duration_path = self.models_path / "duration_predictor.pkl"
            scaler_path = self.models_path / "scaler.pkl"
            encoders_path = self.models_path / "label_encoders.pkl"

            if success_path.exists():
                self.success_model = joblib.load(success_path)
                logger.info("✅ Loaded success predictor model")

            if duration_path.exists():
                self.duration_model = joblib.load(duration_path)
                logger.info("✅ Loaded duration predictor model")

            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
                logger.info("✅ Loaded feature scaler")

            if encoders_path.exists():
                self.label_encoders = joblib.load(encoders_path)
                logger.info("✅ Loaded label encoders")

        except Exception as e:
            logger.error(f"Error loading models: {e}")

    async def train_models(self) -> Dict[str, Any]:
        """
        Train ML models on approved community cases

        Returns:
            Training metrics
        """

        if not ML_AVAILABLE:
            return {'error': 'sklearn not available'}

        logger.info("🤖 Starting ML model training...")

        # Get approved cases
        result = await self.db.execute(
            select(CaseContribution).where(
                CaseContribution.status == ContributionStatus.APPROVED
            )
        )
        cases = result.scalars().all()

        if len(cases) < settings.ML_MIN_TRAINING_CASES:
            logger.warning(
                f"Not enough cases for training: {len(cases)} < "
                f"{settings.ML_MIN_TRAINING_CASES}"
            )
            return {
                'trained': False,
                'reason': 'insufficient_data',
                'case_count': len(cases),
                'minimum_required': settings.ML_MIN_TRAINING_CASES
            }

        # Extract features and targets
        X, y_success, y_duration = self._extract_training_data(cases)

        # Split data
        X_train, X_test, y_success_train, y_success_test = train_test_split(
            X, y_success, test_size=0.2, random_state=42
        )
        _, _, y_duration_train, y_duration_test = train_test_split(
            X, y_duration, test_size=0.2, random_state=42
        )

        # Train success model
        self.success_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.success_model.fit(X_train, y_success_train)
        success_score = self.success_model.score(X_test, y_success_test)

        # Train duration model
        self.duration_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.duration_model.fit(X_train, y_duration_train)
        duration_score = self.duration_model.score(X_test, y_duration_test)

        # Save models
        self._save_models()

        logger.info(
            f"✅ ML models trained: success_acc={success_score:.3f}, "
            f"duration_r2={duration_score:.3f}"
        )

        return {
            'trained': True,
            'case_count': len(cases),
            'train_size': len(X_train),
            'test_size': len(X_test),
            'success_accuracy': float(success_score),
            'duration_r2': float(duration_score),
            'trained_at': datetime.utcnow().isoformat()
        }

    def _extract_training_data(
        self,
        cases: List[CaseContribution]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Extract features and targets from cases

        Features:
        - industry (encoded)
        - org size (encoded)
        - maturity level (encoded)
        - module (encoded)
        - AI usage count
        - Challenges count
        - Initial processes count

        Targets:
        - success (boolean)
        - duration (days)
        """

        features = []
        y_success = []
        y_duration = []

        for case in cases:
            case_data = case.case_data
            org_ctx = case_data.get('organization_context', {})
            metrics = case_data.get('metrics', {})

            # Extract features
            industry = org_ctx.get('industry', 'unknown')
            size = org_ctx.get('size', 'medium')
            maturity = org_ctx.get('maturity_level', 'developing')
            module = case.module

            # Encode categorical features
            industry_enc = self._encode_label('industry', industry)
            size_enc = self._encode_label('size', size)
            maturity_enc = self._encode_label('maturity', maturity)
            module_enc = self._encode_label('module', module)

            # Numerical features
            ai_usage = metrics.get('ai_usage_count', 0)
            challenges = metrics.get('challenges_count', 0)
            processes = metrics.get('processes_count', 0)

            # Assemble feature vector
            feature_vector = [
                industry_enc,
                size_enc,
                maturity_enc,
                module_enc,
                ai_usage,
                challenges,
                processes
            ]

            features.append(feature_vector)

            # Targets
            y_success.append(metrics.get('success', False))
            y_duration.append(metrics.get('duration_days', 0))

        # Convert to numpy arrays
        X = np.array(features)
        y_success = np.array(y_success, dtype=int)
        y_duration = np.array(y_duration, dtype=float)

        # Scale features
        if self.scaler is None:
            self.scaler = StandardScaler()
            X = self.scaler.fit_transform(X)
        else:
            X = self.scaler.transform(X)

        return X, y_success, y_duration

    def _encode_label(self, category: str, value: str) -> int:
        """Encode categorical label to integer"""

        if category not in self.label_encoders:
            self.label_encoders[category] = LabelEncoder()

        encoder = self.label_encoders[category]

        # Fit if new category
        if not hasattr(encoder, 'classes_'):
            encoder.fit([value])
            return 0
        elif value not in encoder.classes_:
            # Unknown category - add it
            encoder.classes_ = np.append(encoder.classes_, value)

        return encoder.transform([value])[0]

    def _save_models(self):
        """Save trained models to disk"""

        try:
            joblib.dump(self.success_model, self.models_path / "success_predictor.pkl")
            joblib.dump(self.duration_model, self.models_path / "duration_predictor.pkl")
            joblib.dump(self.scaler, self.models_path / "scaler.pkl")
            joblib.dump(self.label_encoders, self.models_path / "label_encoders.pkl")

            logger.info("💾 ML models saved to disk")

        except Exception as e:
            logger.error(f"Error saving models: {e}")

    async def predict_success(
        self,
        org_context: Dict[str, Any],
        module: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict probability of workflow success

        Args:
            org_context: Organization context (industry, size, maturity)
            module: BCM module
            initial_data: Initial workflow data (optional)

        Returns:
            {
                'success_probability': float (0-1),
                'confidence': float (0-1),
                'risk_factors': List[str]
            }
        """

        if not self.success_model:
            return {
                'success_probability': 0.5,
                'confidence': 0.0,
                'message': 'Model not trained'
            }

        # Extract features
        features = self._extract_prediction_features(org_context, module, initial_data)

        # Predict
        success_proba = self.success_model.predict_proba([features])[0][1]
        confidence = max(self.success_model.predict_proba([features])[0])

        # Identify risk factors
        risk_factors = self._identify_risk_factors(org_context, module, initial_data)

        return {
            'success_probability': float(success_proba),
            'confidence': float(confidence),
            'risk_factors': risk_factors,
            'prediction_date': datetime.utcnow().isoformat()
        }

    async def predict_duration(
        self,
        org_context: Dict[str, Any],
        module: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict workflow duration

        Returns:
            {
                'predicted_days': float,
                'range_min': float,
                'range_max': float,
                'confidence': float
            }
        """

        if not self.duration_model:
            return {
                'predicted_days': 30.0,
                'confidence': 0.0,
                'message': 'Model not trained'
            }

        # Extract features
        features = self._extract_prediction_features(org_context, module, initial_data)

        # Predict
        predicted_days = self.duration_model.predict([features])[0]

        # Estimate confidence (based on feature similarity to training data)
        confidence = 0.7  # Placeholder

        # Prediction interval (±20%)
        range_min = predicted_days * 0.8
        range_max = predicted_days * 1.2

        return {
            'predicted_days': float(predicted_days),
            'range_min': float(range_min),
            'range_max': float(range_max),
            'confidence': confidence,
            'prediction_date': datetime.utcnow().isoformat()
        }

    def _extract_prediction_features(
        self,
        org_context: Dict[str, Any],
        module: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """Extract features for prediction"""

        industry = org_context.get('industry', 'unknown')
        size = org_context.get('size', 'medium')
        maturity = org_context.get('maturity_level', 'developing')

        # Encode
        industry_enc = self._encode_label('industry', industry)
        size_enc = self._encode_label('size', size)
        maturity_enc = self._encode_label('maturity', maturity)
        module_enc = self._encode_label('module', module)

        # Initial data (if available)
        ai_usage = 0
        challenges = 0
        processes = 0

        if initial_data:
            ai_usage = initial_data.get('ai_usage_count', 0)
            challenges = initial_data.get('challenges_count', 0)
            processes = initial_data.get('processes_count', 0)

        # Feature vector
        features = np.array([
            industry_enc,
            size_enc,
            maturity_enc,
            module_enc,
            ai_usage,
            challenges,
            processes
        ])

        # Scale
        if self.scaler:
            features = self.scaler.transform([features])[0]

        return features

    def _identify_risk_factors(
        self,
        org_context: Dict[str, Any],
        module: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Identify potential risk factors"""

        risk_factors = []

        maturity = org_context.get('maturity_level', 'developing')
        if maturity == 'basic':
            risk_factors.append("Low BCM maturity level")

        size = org_context.get('size', 'medium')
        if size == 'small':
            risk_factors.append("Limited resources in small organization")
        elif size == 'enterprise':
            risk_factors.append("Complexity of large enterprise environment")

        if initial_data:
            if initial_data.get('challenges_count', 0) > 5:
                risk_factors.append("High number of initial challenges")

        return risk_factors

    async def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model"""

        if not self.success_model:
            return {}

        feature_names = [
            'industry',
            'org_size',
            'maturity',
            'module',
            'ai_usage',
            'challenges',
            'processes'
        ]

        importances = self.success_model.feature_importances_

        return dict(zip(feature_names, importances.tolist()))
