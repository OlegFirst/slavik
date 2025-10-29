#!/usr/bin/env python3
"""
Architecture Classifier - ML-powered architecture pattern recognition
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ArchitectureRecommendation:
    """Architecture recommendation with confidence score"""
    pattern: str
    confidence: float
    reasons: List[str]
    components: List[str]
    deployment_strategy: str

class ArchitectureClassifier:
    """Classifies project architecture and provides recommendations"""

    def __init__(self):
        self.patterns = {
            "monolith": {
                "description": "Single deployable unit with all functionality",
                "pros": ["Simple deployment", "Easy development", "Good for small teams"],
                "cons": ["Scaling limitations", "Technology lock-in", "Large blast radius"]
            },
            "microservices": {
                "description": "Distributed services with single responsibilities",
                "pros": ["Independent scaling", "Technology diversity", "Team autonomy"],
                "cons": ["Complexity overhead", "Network latency", "Data consistency"]
            },
            "serverless": {
                "description": "Function-as-a-Service event-driven architecture",
                "pros": ["Auto-scaling", "Pay-per-use", "No server management"],
                "cons": ["Vendor lock-in", "Cold starts", "Debugging complexity"]
            },
            "hybrid": {
                "description": "Mix of different architectural patterns",
                "pros": ["Flexibility", "Gradual migration", "Best of both worlds"],
                "cons": ["Complexity", "Multiple deployment strategies", "Team coordination"]
            }
        }

    async def classify(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Classify architecture and provide recommendations"""
        try:
            logger.info("Starting architecture classification")

            # Extract features for classification
            features = self._extract_features(analysis_result)

            # Classify architecture pattern
            primary_pattern = self._classify_pattern(features)

            # Generate specific recommendations
            recommendations = self._generate_architecture_recommendations(features, primary_pattern)

            # Create deployment strategy
            deployment = primary_pattern.deployment_strategy

            # Generate component breakdown
            components = primary_pattern.components

            result = {
                "primary_pattern": primary_pattern.pattern,
                "confidence": primary_pattern.confidence,
                "reasons": primary_pattern.reasons,
                "alternative_patterns": self._get_alternative_patterns(features),
                "recommended_components": components,
                "deployment_strategy": deployment,
                "implementation_steps": self._generate_implementation_steps(primary_pattern),
                "estimated_complexity": self._estimate_implementation_complexity(features),
                "technology_stack": self._suggest_technology_stack(features, primary_pattern)
            }

            logger.info(f"Classification completed: {primary_pattern.pattern}")
            return result

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise

    def _extract_features(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features for ML classification"""
        features = {
            "lines_of_code": analysis_result.get("metrics", {}).get("lines_of_code", 0),
            "files_count": analysis_result.get("metrics", {}).get("files_count", 0),
            "dependencies_count": analysis_result.get("dependencies", {}).get("count", 0),
            "languages": list(analysis_result.get("languages", {}).keys()),
            "frameworks": analysis_result.get("frameworks", []),
            "patterns": analysis_result.get("patterns", []),
            "complexity_score": analysis_result.get("complexity_score", "low"),
            "has_tests": analysis_result.get("metrics", {}).get("test_files", 0) > 0,
            "has_docker": "Docker" in analysis_result.get("frameworks", []),
            "has_api": self._detect_api_pattern(analysis_result),
            "has_database": self._detect_database_usage(analysis_result),
            "has_frontend": self._detect_frontend_pattern(analysis_result),
            "has_services": "microservices" in analysis_result.get("patterns", [])
        }

        return features

    def _detect_api_pattern(self, analysis_result: Dict[str, Any]) -> bool:
        """Detect if project has API endpoints"""
        frameworks = analysis_result.get("frameworks", [])
        api_frameworks = ["Express.js", "FastAPI", "Flask", "Django", "Spring"]
        return any(fw in frameworks for fw in api_frameworks)

    def _detect_database_usage(self, analysis_result: Dict[str, Any]) -> bool:
        """Detect database usage patterns"""
        dependencies = analysis_result.get("dependencies", {}).get("external", [])
        db_keywords = ["mongoose", "sequelize", "prisma", "sqlalchemy", "django.db", "spring.data"]
        return any(keyword in dep.lower() for dep in dependencies for keyword in db_keywords)

    def _detect_frontend_pattern(self, analysis_result: Dict[str, Any]) -> bool:
        """Detect frontend framework usage"""
        frameworks = analysis_result.get("frameworks", [])
        frontend_frameworks = ["React", "Vue.js", "Angular", "Next.js", "Nuxt.js"]
        return any(fw in frameworks for fw in frontend_frameworks)

    def _classify_pattern(self, features: Dict[str, Any]) -> ArchitectureRecommendation:
        """Main classification logic"""
        scores = {}
        reasons = {}

        # Monolith scoring
        monolith_score = 0
        monolith_reasons = []

        if features["lines_of_code"] < 10000:
            monolith_score += 0.3
            monolith_reasons.append("Small codebase suitable for monolith")

        if len(features["languages"]) == 1:
            monolith_score += 0.2
            monolith_reasons.append("Single language project")

        if not features["has_services"]:
            monolith_score += 0.3
            monolith_reasons.append("No microservices patterns detected")

        if features["files_count"] < 100:
            monolith_score += 0.2
            monolith_reasons.append("Small file count")

        scores["monolith"] = monolith_score
        reasons["monolith"] = monolith_reasons

        # Microservices scoring
        microservices_score = 0
        microservices_reasons = []

        if features["has_services"] or "microservices" in features["patterns"]:
            microservices_score += 0.4
            microservices_reasons.append("Microservices patterns detected")

        if features["has_docker"]:
            microservices_score += 0.2
            microservices_reasons.append("Docker containerization present")

        if features["lines_of_code"] > 20000:
            microservices_score += 0.2
            microservices_reasons.append("Large codebase benefits from decomposition")

        if features["has_api"] and features["has_database"]:
            microservices_score += 0.2
            microservices_reasons.append("API and database layers present")

        scores["microservices"] = microservices_score
        reasons["microservices"] = microservices_reasons

        # Serverless scoring
        serverless_score = 0
        serverless_reasons = []

        if any("lambda" in fw.lower() or "serverless" in fw.lower() for fw in features["frameworks"]):
            serverless_score += 0.4
            serverless_reasons.append("Serverless frameworks detected")

        if features["lines_of_code"] < 5000 and features["has_api"]:
            serverless_score += 0.3
            serverless_reasons.append("Small API suitable for functions")

        if "event" in str(features["patterns"]).lower():
            serverless_score += 0.3
            serverless_reasons.append("Event-driven patterns detected")

        scores["serverless"] = serverless_score
        reasons["serverless"] = serverless_reasons

        # Hybrid scoring
        hybrid_score = 0
        hybrid_reasons = []

        if len(features["languages"]) > 1:
            hybrid_score += 0.2
            hybrid_reasons.append("Multiple languages suggest hybrid approach")

        if features["has_frontend"] and features["has_api"]:
            hybrid_score += 0.3
            hybrid_reasons.append("Frontend and backend separation")

        if features["complexity_score"] in ["high", "very_high"]:
            hybrid_score += 0.3
            hybrid_reasons.append("High complexity benefits from hybrid approach")

        scores["hybrid"] = hybrid_score
        reasons["hybrid"] = hybrid_reasons

        # Find best pattern
        best_pattern = max(scores, key=scores.get)
        confidence = scores[best_pattern]

        # Ensure minimum confidence
        if confidence < 0.3:
            best_pattern = "monolith"  # Default fallback
            confidence = 0.5
            pattern_reasons = ["Default recommendation for unclear architecture"]
        else:
            pattern_reasons = reasons[best_pattern]

        # Generate components based on pattern
        components = self._generate_pattern_components(best_pattern, features)

        return ArchitectureRecommendation(
            pattern=best_pattern,
            confidence=min(confidence, 1.0),
            reasons=pattern_reasons,
            components=components,
            deployment_strategy=self._get_deployment_strategy(best_pattern)
        )

    def _generate_pattern_components(self, pattern: str, features: Dict[str, Any]) -> List[str]:
        """Generate recommended components for the pattern"""
        components = []

        if pattern == "monolith":
            components = ["Web Application", "Database", "Static Assets"]
            if features["has_api"]:
                components.append("REST API")

        elif pattern == "microservices":
            components = ["API Gateway", "Service Discovery", "Load Balancer"]
            if features["has_database"]:
                components.append("Database per Service")
            if features["has_frontend"]:
                components.append("Frontend Service")
            components.extend(["User Service", "Business Logic Service", "Data Service"])

        elif pattern == "serverless":
            components = ["API Gateway", "Lambda Functions", "Event Bus"]
            if features["has_database"]:
                components.append("Managed Database")
            if features["has_frontend"]:
                components.append("Static Site Hosting")

        elif pattern == "hybrid":
            components = ["Monolith Core", "Microservices Extensions", "API Gateway"]
            if features["has_frontend"]:
                components.append("Frontend Application")

        return components

    def _get_deployment_strategy(self, pattern: str) -> str:
        """Get deployment strategy for pattern"""
        strategies = {
            "monolith": "Single container deployment",
            "microservices": "Kubernetes with service mesh",
            "serverless": "Function-as-a-Service platform",
            "hybrid": "Mixed container and serverless deployment"
        }
        return strategies.get(pattern, "Container-based deployment")

    def _generate_architecture_recommendations(self, features: Dict[str, Any], recommendation: ArchitectureRecommendation) -> List[str]:
        """Generate specific architecture recommendations"""
        recommendations = []

        if not features["has_tests"]:
            recommendations.append("Implement comprehensive testing strategy")

        if not features["has_docker"]:
            recommendations.append("Add containerization for consistent deployment")

        if recommendation.pattern == "microservices":
            recommendations.extend([
                "Implement service discovery mechanism",
                "Add distributed tracing",
                "Set up centralized logging",
                "Implement circuit breaker pattern"
            ])

        if features["complexity_score"] in ["high", "very_high"]:
            recommendations.append("Consider implementing monitoring and observability")

        return recommendations

    def _get_alternative_patterns(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get alternative architecture patterns"""
        alternatives = []

        for pattern_name, pattern_info in self.patterns.items():
            alternatives.append({
                "pattern": pattern_name,
                "description": pattern_info["description"],
                "pros": pattern_info["pros"],
                "cons": pattern_info["cons"]
            })

        return alternatives

    def _generate_implementation_steps(self, recommendation: ArchitectureRecommendation) -> List[str]:
        """Generate implementation steps"""
        steps = []

        if recommendation.pattern == "monolith":
            steps = [
                "Set up single application structure",
                "Implement core business logic",
                "Add database layer",
                "Create API endpoints",
                "Add testing framework",
                "Set up CI/CD pipeline"
            ]

        elif recommendation.pattern == "microservices":
            steps = [
                "Design service boundaries",
                "Set up API gateway",
                "Implement core services",
                "Add service discovery",
                "Set up inter-service communication",
                "Implement monitoring and logging",
                "Add deployment automation"
            ]

        elif recommendation.pattern == "serverless":
            steps = [
                "Identify function boundaries",
                "Set up serverless framework",
                "Implement core functions",
                "Add event triggers",
                "Set up API gateway",
                "Add monitoring and alerts"
            ]

        return steps

    def _estimate_implementation_complexity(self, features: Dict[str, Any]) -> str:
        """Estimate implementation complexity"""
        if features["lines_of_code"] > 50000 or features["dependencies_count"] > 100:
            return "very_high"
        elif features["lines_of_code"] > 20000 or features["dependencies_count"] > 50:
            return "high"
        elif features["lines_of_code"] > 5000 or features["dependencies_count"] > 20:
            return "medium"
        else:
            return "low"

    def _suggest_technology_stack(self, features: Dict[str, Any], recommendation: ArchitectureRecommendation) -> Dict[str, List[str]]:
        """Suggest technology stack based on analysis"""
        stack = {
            "backend": [],
            "frontend": [],
            "database": [],
            "infrastructure": [],
            "monitoring": []
        }

        # Backend suggestions
        if "python" in features["languages"]:
            stack["backend"].extend(["FastAPI", "Python 3.11+"])
        if "javascript" in features["languages"]:
            stack["backend"].extend(["Node.js", "Express.js"])

        # Frontend suggestions
        if features["has_frontend"]:
            frameworks = features.get("frameworks", [])
            if "React" in frameworks:
                stack["frontend"].append("React")
            else:
                stack["frontend"].append("React (recommended)")

        # Database suggestions
        if features["has_database"]:
            if recommendation.pattern == "microservices":
                stack["database"].extend(["PostgreSQL", "Redis"])
            else:
                stack["database"].append("PostgreSQL")

        # Infrastructure
        if recommendation.pattern == "microservices":
            stack["infrastructure"].extend(["Docker", "Kubernetes", "API Gateway"])
        elif recommendation.pattern == "serverless":
            stack["infrastructure"].extend(["AWS Lambda", "API Gateway", "CloudWatch"])
        else:
            stack["infrastructure"].extend(["Docker", "Load Balancer"])

        # Monitoring
        stack["monitoring"].extend(["Prometheus", "Grafana", "ELK Stack"])

        return stack