"""
Self-Learning Engine

Система самообучения ML моделей через feedback loop
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
import statistics
import json

logger = logging.getLogger(__name__)


class SelfLearningEngine:
    """
    Система самообучения

    Цикл:
    1. Prediction (предсказание)
    2. Actual outcome (реальный результат)
    3. Error calculation (расчет ошибки)
    4. Model update (обновление модели)
    5. Validation (валидация)
    """

    def __init__(self):
        self.predictions_store = {}  # In-memory store (TODO: use DB)
        self.training_buffer = []
        self.retrain_threshold = 10  # Retrain after 10 new data points
        self.current_model_version = 1.0
        self.current_model_score = 0.0

        # Model performance tracking
        self.performance_history = []

    def record_prediction(
        self,
        prediction_id: str,
        prediction_data: Dict[str, Any]
    ) -> bool:
        """
        Шаг 1: Записать предсказание

        Args:
            prediction_id: Уникальный ID предсказания
            prediction_data: {
                'predicted_score': float,
                'confidence': float,
                'model_version': str,
                'features_used': {...},
                'scenario_type': str,
                'team_id': str
            }

        Returns:
            True если успешно
        """
        try:
            self.predictions_store[prediction_id] = {
                **prediction_data,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending'
            }

            logger.info(f"📝 Recorded prediction {prediction_id}: {prediction_data.get('predicted_score')}")
            return True

        except Exception as e:
            logger.error(f"❌ Error recording prediction: {e}")
            return False

    def record_actual_outcome(
        self,
        prediction_id: str,
        actual_data: Dict[str, Any]
    ) -> bool:
        """
        Шаг 2: Записать реальный результат

        Args:
            prediction_id: ID предсказания
            actual_data: {
                'actual_score': float,
                'exercise_completed': bool,
                'exercise_id': str
            }

        Returns:
            True если успешно, False если предсказание не найдено
        """
        if prediction_id not in self.predictions_store:
            logger.warning(f"⚠️ Prediction {prediction_id} not found")
            return False

        try:
            self.predictions_store[prediction_id].update({
                'actual_outcome': actual_data,
                'outcome_timestamp': datetime.now().isoformat(),
                'status': 'completed'
            })

            logger.info(f"✅ Recorded outcome for {prediction_id}: {actual_data.get('actual_score')}")

            # Триггер: Анализ и обучение
            self._trigger_learning(prediction_id)

            return True

        except Exception as e:
            logger.error(f"❌ Error recording outcome: {e}")
            return False

    def _trigger_learning(self, prediction_id: str):
        """
        Шаг 3-4: Анализ ошибки и обновление модели
        """
        pred = self.predictions_store[prediction_id]

        predicted_score = pred.get('predicted_score', 0)
        actual_score = pred.get('actual_outcome', {}).get('actual_score', 0)

        # Расчет ошибки
        error = abs(predicted_score - actual_score)
        error_percentage = (error / actual_score * 100) if actual_score > 0 else 0

        # Анализ ошибки
        error_analysis = {
            'prediction_id': prediction_id,
            'error': round(error, 2),
            'error_percentage': round(error_percentage, 2),
            'error_type': 'overestimate' if predicted_score > actual_score else 'underestimate',
            'predicted': predicted_score,
            'actual': actual_score,
            'features': pred.get('features_used', {}),
            'model_version': pred.get('model_version', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"📊 Prediction error: {error:.2f} ({error_type})")

        # Сохранить для анализа
        self.performance_history.append(error_analysis)

        # Добавить в training buffer
        self.training_buffer.append({
            'features': pred.get('features_used', {}),
            'target': actual_score,
            'prediction_id': prediction_id
        })

        # Проверить threshold для переобучения
        if len(self.training_buffer) >= self.retrain_threshold:
            self._retrain_model()

    def _retrain_model(self):
        """
        Шаг 5: Переобучение модели

        В production:
        - Использовать MLflow для версионирования
        - RandomForest или XGBoost
        - Proper train/validation split
        - A/B testing

        Сейчас: Simplified version
        """
        logger.info(f"🔄 Starting model retraining (buffer size: {len(self.training_buffer)})...")

        try:
            # Extract features and targets
            X_new = [item['features'] for item in self.training_buffer]
            y_new = [item['target'] for item in self.training_buffer]

            # Simplified "retraining" - adjust weights based on errors
            avg_error = statistics.mean([
                abs(item['features'].get('team_competency', 0) - item['target'])
                for item in self.training_buffer
            ])

            # Calculate improvement
            old_error = self._calculate_recent_error(before_retrain=True)
            new_error = avg_error

            if new_error < old_error:
                # Model improved
                self.current_model_version += 0.1
                self.current_model_score = 100 - new_error  # Simplified score

                logger.info(
                    f"✅ Model updated to v{self.current_model_version:.1f}, "
                    f"score improved: {old_error:.2f} → {new_error:.2f}"
                )

                # Clear buffer
                self.training_buffer = []

                # Save model version info
                self._save_model_version({
                    'version': self.current_model_version,
                    'score': self.current_model_score,
                    'avg_error': new_error,
                    'training_samples': len(X_new),
                    'retrained_at': datetime.now().isoformat()
                })
            else:
                logger.warning(
                    f"⚠️ New model worse (error: {old_error:.2f} → {new_error:.2f}), "
                    f"keeping current version"
                )

        except Exception as e:
            logger.error(f"❌ Model retraining error: {e}")

    def analyze_learning_effectiveness(self) -> Dict[str, Any]:
        """
        Анализ эффективности самообучения

        Метрики:
        - Снижение ошибки предсказания со временем
        - Скорость адаптации к новым сценариям
        - Стабильность модели
        """
        if len(self.performance_history) < 10:
            return {
                'status': 'insufficient_data',
                'samples': len(self.performance_history),
                'message': 'Need at least 10 predictions for analysis'
            }

        # Errors over time
        errors = [p['error'] for p in self.performance_history]

        # Early vs Recent errors
        mid = len(errors) // 2
        early_errors = errors[:mid]
        recent_errors = errors[mid:]

        early_avg = statistics.mean(early_errors)
        recent_avg = statistics.mean(recent_errors)

        improvement = ((early_avg - recent_avg) / early_avg * 100) if early_avg > 0 else 0

        # Model versions performance
        versions_performance = self._analyze_versions_performance()

        return {
            'status': 'improving' if improvement > 0 else 'degrading',
            'improvement_percentage': round(improvement, 2),
            'early_avg_error': round(early_avg, 2),
            'recent_avg_error': round(recent_avg, 2),
            'total_predictions': len(self.performance_history),
            'current_model_version': self.current_model_version,
            'current_model_score': round(self.current_model_score, 2),
            'versions_performance': versions_performance,
            'analyzed_at': datetime.now().isoformat()
        }

    def get_prediction_accuracy_report(self) -> Dict[str, Any]:
        """
        Отчет о точности предсказаний

        Breakdown:
        - By scenario type
        - By error type (over/under estimate)
        - By time period
        """
        if not self.performance_history:
            return {'status': 'no_data'}

        # By scenario type
        by_scenario = defaultdict(list)
        for pred in self.performance_history:
            scenario = pred.get('features', {}).get('scenario_type', 'unknown')
            by_scenario[scenario].append(pred['error'])

        scenario_accuracy = {
            scenario: {
                'avg_error': round(statistics.mean(errors), 2),
                'predictions': len(errors)
            }
            for scenario, errors in by_scenario.items()
        }

        # Error type distribution
        overestimates = [p for p in self.performance_history if p['error_type'] == 'overestimate']
        underestimates = [p for p in self.performance_history if p['error_type'] == 'underestimate']

        # Overall accuracy
        all_errors = [p['error'] for p in self.performance_history]
        avg_error = statistics.mean(all_errors)
        accuracy_percentage = max(0, 100 - avg_error)  # Simplified

        return {
            'overall_accuracy': round(accuracy_percentage, 2),
            'avg_error': round(avg_error, 2),
            'total_predictions': len(self.performance_history),
            'by_scenario': scenario_accuracy,
            'error_distribution': {
                'overestimates': len(overestimates),
                'underestimates': len(underestimates),
                'overestimate_avg': round(statistics.mean([p['error'] for p in overestimates]), 2) if overestimates else 0,
                'underestimate_avg': round(statistics.mean([p['error'] for p in underestimates]), 2) if underestimates else 0
            },
            'current_model_version': self.current_model_version
        }

    def get_predictions_for_review(
        self,
        status: str = 'completed',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Получить предсказания для review

        Args:
            status: 'pending', 'completed', 'all'
            limit: Макс кол-во

        Returns:
            Список предсказаний
        """
        predictions = []

        for pred_id, pred_data in self.predictions_store.items():
            if status == 'all' or pred_data.get('status') == status:
                predictions.append({
                    'prediction_id': pred_id,
                    **pred_data
                })

        # Sort by timestamp (newest first)
        predictions.sort(
            key=lambda p: p.get('timestamp', ''),
            reverse=True
        )

        return predictions[:limit]

    # Helper methods

    def _calculate_recent_error(self, before_retrain: bool = False) -> float:
        """Calculate recent average error"""
        if not self.performance_history:
            return 0

        recent = self.performance_history[-10:] if before_retrain else self.performance_history[-5:]
        if not recent:
            return 0

        return statistics.mean([p['error'] for p in recent])

    def _analyze_versions_performance(self) -> Dict[str, Any]:
        """Analyze performance by model version"""
        by_version = defaultdict(list)

        for pred in self.performance_history:
            version = pred.get('model_version', 'unknown')
            by_version[version].append(pred['error'])

        return {
            version: {
                'avg_error': round(statistics.mean(errors), 2),
                'predictions': len(errors)
            }
            for version, errors in by_version.items()
        }

    def _save_model_version(self, version_info: Dict[str, Any]):
        """
        Save model version info

        TODO: Persist to database (learning.model_versions table)
        """
        logger.info(f"💾 Saved model version: v{version_info['version']}")

        # TODO: INSERT INTO learning.model_versions
        pass

    def export_training_data(self) -> Dict[str, Any]:
        """
        Export training data for offline analysis

        Returns:
            Dataset for ML training
        """
        dataset = {
            'features': [],
            'targets': [],
            'metadata': []
        }

        for pred_id, pred_data in self.predictions_store.items():
            if pred_data.get('status') == 'completed':
                dataset['features'].append(pred_data.get('features_used', {}))
                dataset['targets'].append(pred_data.get('actual_outcome', {}).get('actual_score'))
                dataset['metadata'].append({
                    'prediction_id': pred_id,
                    'predicted': pred_data.get('predicted_score'),
                    'timestamp': pred_data.get('timestamp')
                })

        dataset['total_samples'] = len(dataset['features'])
        dataset['exported_at'] = datetime.now().isoformat()

        return dataset

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Analyze feature importance

        Which features most impact prediction accuracy?
        """
        if not self.performance_history:
            return {}

        # Simplified feature importance analysis
        feature_errors = defaultdict(list)

        for pred in self.performance_history:
            features = pred.get('features', {})
            error = pred['error']

            for feature_name, feature_value in features.items():
                if isinstance(feature_value, (int, float)):
                    feature_errors[feature_name].append(error)

        # Calculate correlation (simplified)
        importance = {}

        for feature, errors in feature_errors.items():
            if errors:
                # Lower avg error when feature is present = higher importance
                avg_error = statistics.mean(errors)
                importance[feature] = round(100 - avg_error, 2)  # Inverted score

        # Sort by importance
        sorted_importance = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)
        )

        return sorted_importance
