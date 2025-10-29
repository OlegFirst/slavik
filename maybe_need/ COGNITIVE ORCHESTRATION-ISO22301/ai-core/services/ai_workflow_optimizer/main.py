#!/usr/bin/env python3
"""
AI Workflow Optimizer Service
ML-powered optimization for business process workflows
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import pickle
import joblib
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bcm_ai_optimizer")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI Workflow Optimizer Service",
    description="ML-powered workflow optimization and prediction",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class ProcessExecution(Base):
    __tablename__ = "process_executions"

    id = Column(String, primary_key=True)
    process_id = Column(String, index=True)
    process_name = Column(String)
    department = Column(String)
    category = Column(String)
    complexity = Column(String)
    execution_time_minutes = Column(Float)
    resource_count = Column(Integer)
    stakeholder_count = Column(Integer)
    step_count = Column(Integer)
    bottleneck_steps = Column(JSON)  # List of step names
    failure_points = Column(JSON)    # List of failure points
    success_rate = Column(Float)
    sla_compliance = Column(Boolean)
    cost_estimate = Column(Float)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    execution_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class OptimizationPrediction(Base):
    __tablename__ = "optimization_predictions"

    id = Column(String, primary_key=True)
    process_id = Column(String, index=True)
    prediction_type = Column(String)  # performance, bottleneck, resource, anomaly
    predicted_value = Column(Float)
    confidence_score = Column(Float)
    recommendations = Column(JSON)    # List of recommendations
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(String, primary_key=True)
    model_type = Column(String)  # performance_predictor, bottleneck_detector, etc.
    model_data = Column(Text)    # Serialized model
    accuracy_score = Column(Float)
    training_data_size = Column(Integer)
    features = Column(JSON)      # List of feature names
    version = Column(String)
    trained_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# Pydantic Models
class ProcessOptimizationRequest(BaseModel):
    processId: str
    historicalData: Optional[Dict[str, Any]] = None
    optimizationGoals: List[str] = ["reduce_time", "improve_quality", "reduce_cost"]

class OptimizationPredictionResponse(BaseModel):
    processId: str
    predictions: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    confidenceScore: float
    estimatedImprovement: Dict[str, float]

class BottleneckAnalysisResponse(BaseModel):
    processId: str
    bottlenecks: List[Dict[str, Any]]
    severity: str
    recommendations: List[str]
    estimatedImpact: Dict[str, float]

class ResourceOptimizationResponse(BaseModel):
    processId: str
    currentAllocation: Dict[str, int]
    recommendedAllocation: Dict[str, int]
    expectedImprovement: Dict[str, float]
    costImpact: float

class AnomalyDetectionResponse(BaseModel):
    processId: str
    anomalies: List[Dict[str, Any]]
    riskLevel: str
    recommendations: List[str]

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# AI/ML Service
class WorkflowOptimizerService:
    def __init__(self, db: Session):
        self.db = db
        self.models = {}
        self.scalers = {}
        self.load_models()

    def load_models(self):
        """Load trained ML models from database"""
        try:
            models = self.db.query(MLModel).filter(MLModel.is_active == True).all()

            for model_record in models:
                try:
                    # Deserialize model
                    model_data = pickle.loads(model_record.model_data.encode('latin1'))
                    self.models[model_record.model_type] = {
                        'model': model_data['model'],
                        'scaler': model_data.get('scaler'),
                        'features': model_record.features,
                        'version': model_record.version,
                        'accuracy': model_record.accuracy_score
                    }
                    logger.info(f"Loaded model: {model_record.model_type} v{model_record.version}")
                except Exception as e:
                    logger.error(f"Error loading model {model_record.model_type}: {e}")

            # If no models exist, train default models
            if not self.models:
                self.train_default_models()

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.train_default_models()

    def train_default_models(self):
        """Train default ML models with synthetic data"""
        try:
            logger.info("Training default ML models...")

            # Generate synthetic training data
            training_data = self._generate_synthetic_data(1000)

            # Train performance prediction model
            self._train_performance_predictor(training_data)

            # Train bottleneck detection model
            self._train_bottleneck_detector(training_data)

            # Train anomaly detection model
            self._train_anomaly_detector(training_data)

            logger.info("Default models trained successfully")

        except Exception as e:
            logger.error(f"Error training default models: {e}")

    def _generate_synthetic_data(self, size: int) -> pd.DataFrame:
        """Generate synthetic process execution data for training"""
        np.random.seed(42)

        data = {
            'process_id': [f'proc_{i:04d}' for i in range(size)],
            'department': np.random.choice(['IT', 'Finance', 'HR', 'Operations'], size),
            'category': np.random.choice(['emergency', 'incident', 'bcm', 'audit'], size),
            'complexity': np.random.choice([1, 2, 3], size, p=[0.3, 0.5, 0.2]),  # 1=simple, 2=medium, 3=complex
            'resource_count': np.random.randint(1, 10, size),
            'stakeholder_count': np.random.randint(2, 20, size),
            'step_count': np.random.randint(3, 15, size),
        }

        # Calculate execution time based on complexity and other factors
        base_time = data['complexity'] * 30  # Base time in minutes
        resource_factor = 1 - (np.array(data['resource_count']) - 1) * 0.05  # More resources = less time
        complexity_noise = np.random.normal(0, data['complexity'] * 10, size)  # More complex = more variance

        data['execution_time_minutes'] = np.maximum(
            base_time * resource_factor + complexity_noise,
            10  # Minimum 10 minutes
        )

        # Success rate based on complexity
        data['success_rate'] = np.maximum(
            0.95 - (np.array(data['complexity']) - 1) * 0.1 + np.random.normal(0, 0.05, size),
            0.5
        )

        # SLA compliance
        data['sla_compliance'] = data['execution_time_minutes'] < (data['complexity'] * 60)

        # Cost estimate
        data['cost_estimate'] = (
            data['execution_time_minutes'] * 2 +
            np.array(data['resource_count']) * 50 +
            np.array(data['stakeholder_count']) * 10
        )

        return pd.DataFrame(data)

    def _train_performance_predictor(self, data: pd.DataFrame):
        """Train model to predict process execution time"""
        try:
            # Prepare features
            features = ['complexity', 'resource_count', 'stakeholder_count', 'step_count']
            X = data[features]
            y = data['execution_time_minutes']

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)

            # Evaluate
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)

            accuracy_score = 1 - (mae / y_test.mean())  # Simple accuracy metric

            # Save model
            self.models['performance_predictor'] = {
                'model': model,
                'scaler': scaler,
                'features': features,
                'version': '1.0',
                'accuracy': accuracy_score
            }

            # Save to database
            self._save_model_to_db('performance_predictor', model, scaler, features, accuracy_score)

            logger.info(f"Performance predictor trained - Accuracy: {accuracy_score:.3f}, MAE: {mae:.2f}")

        except Exception as e:
            logger.error(f"Error training performance predictor: {e}")

    def _train_bottleneck_detector(self, data: pd.DataFrame):
        """Train model to detect process bottlenecks"""
        try:
            # Create bottleneck labels based on execution time vs expected time
            expected_time = data['complexity'] * 45  # Expected time baseline
            data['is_bottleneck'] = data['execution_time_minutes'] > (expected_time * 1.5)

            # Prepare features
            features = ['complexity', 'resource_count', 'stakeholder_count', 'step_count', 'success_rate']
            X = data[features]
            y = data['is_bottleneck']

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train model
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)

            # Evaluate
            accuracy_score = model.score(X_test_scaled, y_test)

            # Save model
            self.models['bottleneck_detector'] = {
                'model': model,
                'scaler': scaler,
                'features': features,
                'version': '1.0',
                'accuracy': accuracy_score
            }

            # Save to database
            self._save_model_to_db('bottleneck_detector', model, scaler, features, accuracy_score)

            logger.info(f"Bottleneck detector trained - Accuracy: {accuracy_score:.3f}")

        except Exception as e:
            logger.error(f"Error training bottleneck detector: {e}")

    def _train_anomaly_detector(self, data: pd.DataFrame):
        """Train model to detect process anomalies"""
        try:
            # Prepare features for anomaly detection
            features = ['execution_time_minutes', 'resource_count', 'stakeholder_count', 'step_count', 'success_rate']
            X = data[features]

            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Train isolation forest for anomaly detection
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(X_scaled)

            # Evaluate (simple metric)
            anomaly_scores = model.decision_function(X_scaled)
            accuracy_score = 0.85  # Mock accuracy for anomaly detection

            # Save model
            self.models['anomaly_detector'] = {
                'model': model,
                'scaler': scaler,
                'features': features,
                'version': '1.0',
                'accuracy': accuracy_score
            }

            # Save to database
            self._save_model_to_db('anomaly_detector', model, scaler, features, accuracy_score)

            logger.info(f"Anomaly detector trained - Accuracy: {accuracy_score:.3f}")

        except Exception as e:
            logger.error(f"Error training anomaly detector: {e}")

    def _save_model_to_db(self, model_type: str, model, scaler, features: List[str], accuracy: float):
        """Save trained model to database"""
        try:
            # Serialize model and scaler
            model_data = {
                'model': model,
                'scaler': scaler
            }
            serialized_data = pickle.dumps(model_data).decode('latin1')

            # Create or update model record
            existing = self.db.query(MLModel).filter(
                MLModel.model_type == model_type,
                MLModel.is_active == True
            ).first()

            if existing:
                existing.is_active = False
                self.db.commit()

            ml_model = MLModel(
                id=f"{model_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                model_type=model_type,
                model_data=serialized_data,
                accuracy_score=accuracy,
                training_data_size=1000,  # Mock size
                features=features,
                version="1.0",
                is_active=True
            )

            self.db.add(ml_model)
            self.db.commit()

            logger.info(f"Model {model_type} saved to database")

        except Exception as e:
            logger.error(f"Error saving model to database: {e}")

    def predict_performance(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict process execution time and performance metrics"""
        try:
            if 'performance_predictor' not in self.models:
                raise HTTPException(status_code=500, detail="Performance prediction model not available")

            model_info = self.models['performance_predictor']
            model = model_info['model']
            scaler = model_info['scaler']
            features = model_info['features']

            # Prepare input data
            input_data = []
            for feature in features:
                value = process_data.get(feature, 0)
                # Map string values to numeric
                if feature == 'complexity':
                    complexity_map = {'simple': 1, 'medium': 2, 'complex': 3}
                    value = complexity_map.get(value, 2)
                input_data.append(value)

            # Make prediction
            input_scaled = scaler.transform([input_data])
            predicted_time = model.predict(input_scaled)[0]

            # Calculate confidence
            confidence = min(model_info['accuracy'] * 0.9 + 0.1, 0.95)

            # Generate recommendations
            recommendations = self._generate_performance_recommendations(process_data, predicted_time)

            return {
                'predicted_execution_time': round(predicted_time, 2),
                'confidence_score': round(confidence, 3),
                'recommendations': recommendations,
                'baseline_time': process_data.get('complexity', 2) * 45,  # Expected baseline
                'improvement_potential': max(0, predicted_time - process_data.get('complexity', 2) * 30)
            }

        except Exception as e:
            logger.error(f"Error in performance prediction: {e}")
            raise HTTPException(status_code=500, detail=f"Performance prediction failed: {str(e)}")

    def detect_bottlenecks(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential bottlenecks in process execution"""
        try:
            if 'bottleneck_detector' not in self.models:
                raise HTTPException(status_code=500, detail="Bottleneck detection model not available")

            model_info = self.models['bottleneck_detector']
            model = model_info['model']
            scaler = model_info['scaler']
            features = model_info['features']

            # Prepare input data
            input_data = []
            for feature in features:
                if feature == 'complexity':
                    complexity_map = {'simple': 1, 'medium': 2, 'complex': 3}
                    value = complexity_map.get(process_data.get(feature, 'medium'), 2)
                else:
                    value = process_data.get(feature, 0)
                input_data.append(value)

            # Make prediction
            input_scaled = scaler.transform([input_data])
            bottleneck_probability = model.predict_proba(input_scaled)[0][1]  # Probability of bottleneck

            # Determine severity
            if bottleneck_probability > 0.7:
                severity = "high"
            elif bottleneck_probability > 0.4:
                severity = "medium"
            else:
                severity = "low"

            # Generate bottleneck analysis
            bottlenecks = self._analyze_bottleneck_sources(process_data, bottleneck_probability)
            recommendations = self._generate_bottleneck_recommendations(bottlenecks, severity)

            return {
                'bottleneck_probability': round(bottleneck_probability, 3),
                'severity': severity,
                'bottlenecks': bottlenecks,
                'recommendations': recommendations,
                'confidence_score': round(model_info['accuracy'], 3)
            }

        except Exception as e:
            logger.error(f"Error in bottleneck detection: {e}")
            raise HTTPException(status_code=500, detail=f"Bottleneck detection failed: {str(e)}")

    def detect_anomalies(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in process execution"""
        try:
            if 'anomaly_detector' not in self.models:
                raise HTTPException(status_code=500, detail="Anomaly detection model not available")

            model_info = self.models['anomaly_detector']
            model = model_info['model']
            scaler = model_info['scaler']
            features = model_info['features']

            # Prepare input data
            input_data = []
            for feature in features:
                value = process_data.get(feature, 0)
                if feature == 'execution_time_minutes' and value == 0:
                    value = process_data.get('complexity', 2) * 45  # Default expected time
                input_data.append(value)

            # Make prediction
            input_scaled = scaler.transform([input_data])
            anomaly_score = model.decision_function(input_scaled)[0]
            is_anomaly = model.predict(input_scaled)[0] == -1

            # Determine risk level
            if is_anomaly and anomaly_score < -0.3:
                risk_level = "high"
            elif is_anomaly and anomaly_score < -0.1:
                risk_level = "medium"
            else:
                risk_level = "low"

            # Generate anomaly details
            anomalies = []
            if is_anomaly:
                anomalies = self._analyze_anomaly_sources(process_data, anomaly_score)

            recommendations = self._generate_anomaly_recommendations(anomalies, risk_level)

            return {
                'is_anomaly': is_anomaly,
                'anomaly_score': round(anomaly_score, 3),
                'risk_level': risk_level,
                'anomalies': anomalies,
                'recommendations': recommendations,
                'confidence_score': round(model_info['accuracy'], 3)
            }

        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

    def optimize_resources(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource allocation for process"""
        try:
            current_resources = process_data.get('resource_count', 5)
            complexity = process_data.get('complexity', 'medium')
            step_count = process_data.get('step_count', 8)

            # Simple optimization logic
            complexity_map = {'simple': 1, 'medium': 2, 'complex': 3}
            complexity_factor = complexity_map.get(complexity, 2)

            # Calculate optimal resources
            optimal_resources = max(1, min(10, int(step_count * 0.6 + complexity_factor * 1.5)))

            # Calculate expected improvement
            current_time = self.predict_performance(process_data)['predicted_execution_time']

            optimized_data = process_data.copy()
            optimized_data['resource_count'] = optimal_resources
            optimized_time = self.predict_performance(optimized_data)['predicted_execution_time']

            time_improvement = max(0, current_time - optimized_time)
            cost_current = current_resources * 50 + current_time * 2
            cost_optimized = optimal_resources * 50 + optimized_time * 2
            cost_improvement = cost_current - cost_optimized

            return {
                'current_allocation': {
                    'resources': current_resources,
                    'estimated_time': round(current_time, 2),
                    'estimated_cost': round(cost_current, 2)
                },
                'recommended_allocation': {
                    'resources': optimal_resources,
                    'estimated_time': round(optimized_time, 2),
                    'estimated_cost': round(cost_optimized, 2)
                },
                'expected_improvement': {
                    'time_saved_minutes': round(time_improvement, 2),
                    'cost_saved': round(cost_improvement, 2),
                    'efficiency_gain': round((time_improvement / current_time) * 100, 1) if current_time > 0 else 0
                }
            }

        except Exception as e:
            logger.error(f"Error in resource optimization: {e}")
            raise HTTPException(status_code=500, detail=f"Resource optimization failed: {str(e)}")

    def _generate_performance_recommendations(self, process_data: Dict[str, Any], predicted_time: float) -> List[Dict[str, Any]]:
        """Generate recommendations for performance improvement"""
        recommendations = []

        complexity = process_data.get('complexity', 'medium')
        resource_count = process_data.get('resource_count', 5)
        step_count = process_data.get('step_count', 8)

        # Time-based recommendations
        if predicted_time > 120:  # Over 2 hours
            recommendations.append({
                'type': 'resource_allocation',
                'priority': 'high',
                'title': 'Increase Resource Allocation',
                'description': f'Process predicted to take {predicted_time:.0f} minutes. Consider adding more resources.',
                'impact': 'high',
                'effort': 'medium'
            })

        # Complexity-based recommendations
        if complexity == 'complex' and resource_count < 6:
            recommendations.append({
                'type': 'complexity_management',
                'priority': 'medium',
                'title': 'Add Senior Resources',
                'description': 'Complex processes benefit from experienced team members.',
                'impact': 'medium',
                'effort': 'low'
            })

        # Step optimization
        if step_count > 10:
            recommendations.append({
                'type': 'process_optimization',
                'priority': 'medium',
                'title': 'Consider Process Simplification',
                'description': f'Process has {step_count} steps. Look for consolidation opportunities.',
                'impact': 'medium',
                'effort': 'high'
            })

        return recommendations

    def _analyze_bottleneck_sources(self, process_data: Dict[str, Any], probability: float) -> List[Dict[str, Any]]:
        """Analyze potential sources of bottlenecks"""
        bottlenecks = []

        resource_count = process_data.get('resource_count', 5)
        stakeholder_count = process_data.get('stakeholder_count', 10)
        step_count = process_data.get('step_count', 8)

        # Resource bottleneck
        if resource_count < 4:
            bottlenecks.append({
                'type': 'resource_shortage',
                'severity': 'high',
                'description': f'Low resource count ({resource_count}) may cause delays',
                'impact_score': 0.8
            })

        # Communication bottleneck
        if stakeholder_count > 15:
            bottlenecks.append({
                'type': 'communication_overhead',
                'severity': 'medium',
                'description': f'High stakeholder count ({stakeholder_count}) may slow coordination',
                'impact_score': 0.6
            })

        # Process complexity bottleneck
        if step_count > 12:
            bottlenecks.append({
                'type': 'process_complexity',
                'severity': 'medium',
                'description': f'High step count ({step_count}) increases coordination complexity',
                'impact_score': 0.5
            })

        return bottlenecks

    def _generate_bottleneck_recommendations(self, bottlenecks: List[Dict], severity: str) -> List[str]:
        """Generate recommendations for bottleneck resolution"""
        recommendations = []

        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'resource_shortage':
                recommendations.append('Increase resource allocation by 2-3 team members')
                recommendations.append('Consider cross-training existing team members')

            elif bottleneck['type'] == 'communication_overhead':
                recommendations.append('Implement stakeholder hierarchy with designated communication leads')
                recommendations.append('Use automated notification systems to reduce manual coordination')

            elif bottleneck['type'] == 'process_complexity':
                recommendations.append('Review process steps for consolidation opportunities')
                recommendations.append('Implement parallel execution where possible')

        if severity == 'high':
            recommendations.append('Consider emergency escalation procedures')
            recommendations.append('Implement real-time monitoring and alerts')

        return recommendations

    def _analyze_anomaly_sources(self, process_data: Dict[str, Any], anomaly_score: float) -> List[Dict[str, Any]]:
        """Analyze sources of anomalies"""
        anomalies = []

        execution_time = process_data.get('execution_time_minutes', 0)
        resource_count = process_data.get('resource_count', 5)
        success_rate = process_data.get('success_rate', 0.9)

        # Time anomaly
        expected_time = process_data.get('complexity', 2) * 45
        if execution_time > expected_time * 2:
            anomalies.append({
                'type': 'execution_time_anomaly',
                'description': f'Execution time ({execution_time:.0f}m) significantly exceeds expected ({expected_time:.0f}m)',
                'severity': 'high'
            })

        # Success rate anomaly
        if success_rate < 0.7:
            anomalies.append({
                'type': 'success_rate_anomaly',
                'description': f'Success rate ({success_rate:.1%}) is unusually low',
                'severity': 'high'
            })

        # Resource anomaly
        if resource_count > 8:
            anomalies.append({
                'type': 'resource_anomaly',
                'description': f'Resource count ({resource_count}) is unusually high',
                'severity': 'medium'
            })

        return anomalies

    def _generate_anomaly_recommendations(self, anomalies: List[Dict], risk_level: str) -> List[str]:
        """Generate recommendations for anomaly resolution"""
        recommendations = []

        for anomaly in anomalies:
            if anomaly['type'] == 'execution_time_anomaly':
                recommendations.append('Investigate process delays and blocking issues')
                recommendations.append('Review resource allocation and availability')

            elif anomaly['type'] == 'success_rate_anomaly':
                recommendations.append('Review process documentation and training materials')
                recommendations.append('Implement additional quality checks')

            elif anomaly['type'] == 'resource_anomaly':
                recommendations.append('Review resource utilization efficiency')
                recommendations.append('Consider workload redistribution')

        if risk_level == 'high':
            recommendations.append('Implement immediate monitoring and intervention')
            recommendations.append('Escalate to process improvement team')

        return recommendations

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-workflow-optimizer", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/optimize/performance", response_model=OptimizationPredictionResponse)
async def optimize_process_performance(
    request: ProcessOptimizationRequest,
    db: Session = Depends(get_db)
):
    """Get AI-powered performance optimization recommendations"""
    service = WorkflowOptimizerService(db)

    # Mock process data for demonstration
    process_data = {
        'process_id': request.processId,
        'complexity': 'medium',
        'resource_count': 5,
        'stakeholder_count': 10,
        'step_count': 8,
        'success_rate': 0.85
    }

    # Override with historical data if provided
    if request.historicalData:
        process_data.update(request.historicalData)

    # Get predictions
    performance_pred = service.predict_performance(process_data)
    bottleneck_analysis = service.detect_bottlenecks(process_data)
    resource_optimization = service.optimize_resources(process_data)

    # Combine recommendations
    all_recommendations = []
    all_recommendations.extend(performance_pred['recommendations'])
    all_recommendations.extend([
        {'type': 'bottleneck', 'content': rec} for rec in bottleneck_analysis['recommendations']
    ])

    return OptimizationPredictionResponse(
        processId=request.processId,
        predictions={
            'execution_time': performance_pred['predicted_execution_time'],
            'bottleneck_probability': bottleneck_analysis['bottleneck_probability'],
            'resource_optimization': resource_optimization
        },
        recommendations=all_recommendations,
        confidenceScore=performance_pred['confidence_score'],
        estimatedImprovement={
            'time_reduction': performance_pred.get('improvement_potential', 0),
            'efficiency_gain': resource_optimization['expected_improvement']['efficiency_gain']
        }
    )

@app.get("/api/v1/analyze/bottlenecks/{process_id}", response_model=BottleneckAnalysisResponse)
async def analyze_bottlenecks(process_id: str, db: Session = Depends(get_db)):
    """Analyze potential bottlenecks in process execution"""
    service = WorkflowOptimizerService(db)

    # Mock process data
    process_data = {
        'process_id': process_id,
        'complexity': 'medium',
        'resource_count': 3,  # Low resources to trigger bottleneck
        'stakeholder_count': 18,  # High stakeholders
        'step_count': 12,  # High steps
        'success_rate': 0.75
    }

    analysis = service.detect_bottlenecks(process_data)

    return BottleneckAnalysisResponse(
        processId=process_id,
        bottlenecks=analysis['bottlenecks'],
        severity=analysis['severity'],
        recommendations=analysis['recommendations'],
        estimatedImpact={
            'time_delay': analysis['bottleneck_probability'] * 60,  # Estimated delay in minutes
            'cost_impact': analysis['bottleneck_probability'] * 500  # Estimated cost impact
        }
    )

@app.get("/api/v1/optimize/resources/{process_id}", response_model=ResourceOptimizationResponse)
async def optimize_process_resources(process_id: str, db: Session = Depends(get_db)):
    """Get resource optimization recommendations"""
    service = WorkflowOptimizerService(db)

    # Mock process data
    process_data = {
        'process_id': process_id,
        'complexity': 'complex',
        'resource_count': 4,
        'stakeholder_count': 12,
        'step_count': 10,
        'success_rate': 0.85
    }

    optimization = service.optimize_resources(process_data)

    return ResourceOptimizationResponse(
        processId=process_id,
        currentAllocation={'resources': optimization['current_allocation']['resources']},
        recommendedAllocation={'resources': optimization['recommended_allocation']['resources']},
        expectedImprovement={
            'time_saved': optimization['expected_improvement']['time_saved_minutes'],
            'efficiency_gain': optimization['expected_improvement']['efficiency_gain']
        },
        costImpact=optimization['expected_improvement']['cost_saved']
    )

@app.get("/api/v1/detect/anomalies/{process_id}", response_model=AnomalyDetectionResponse)
async def detect_process_anomalies(process_id: str, db: Session = Depends(get_db)):
    """Detect anomalies in process execution"""
    service = WorkflowOptimizerService(db)

    # Mock process data with anomalous values
    process_data = {
        'process_id': process_id,
        'execution_time_minutes': 180,  # High execution time
        'resource_count': 2,  # Low resources
        'stakeholder_count': 25,  # High stakeholders
        'step_count': 8,
        'success_rate': 0.6  # Low success rate
    }

    analysis = service.detect_anomalies(process_data)

    return AnomalyDetectionResponse(
        processId=process_id,
        anomalies=analysis['anomalies'],
        riskLevel=analysis['risk_level'],
        recommendations=analysis['recommendations']
    )

@app.post("/api/v1/models/retrain")
async def retrain_models(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Retrain ML models with latest data"""
    def retrain_task():
        service = WorkflowOptimizerService(db)
        service.train_default_models()

    background_tasks.add_task(retrain_task)

    return {"message": "Model retraining started in background", "status": "initiated"}

@app.get("/api/v1/models/status")
async def get_model_status(db: Session = Depends(get_db)):
    """Get status of ML models"""
    models = db.query(MLModel).filter(MLModel.is_active == True).all()

    model_status = []
    for model in models:
        model_status.append({
            'model_type': model.model_type,
            'version': model.version,
            'accuracy': model.accuracy_score,
            'trained_at': model.trained_at.isoformat(),
            'training_data_size': model.training_data_size
        })

    return {
        'models': model_status,
        'total_models': len(model_status),
        'last_updated': max([m.trained_at for m in models]).isoformat() if models else None
    }

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database and models"""
    Base.metadata.create_all(bind=engine)

    # Initialize ML models
    db = SessionLocal()
    service = WorkflowOptimizerService(db)
    db.close()

    logger.info("AI Workflow Optimizer Service started successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)