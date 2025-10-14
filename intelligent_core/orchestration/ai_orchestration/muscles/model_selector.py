"""
BCM Platform Model Router
Smart routing of AI tasks to optimal models based on complexity and speed requirements
"""

from enum import Enum
from typing import Dict, Any, Optional
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)

class TaskComplexity(str, Enum):
    FAST = "fast"           # Emergency response, simple classification
    MEDIUM = "medium"       # General analysis, Q&A
    COMPLEX = "complex"     # BIA analysis, compliance reports
    HEAVY = "heavy"         # Scenario generation, comprehensive reports

class BCMModelRouter:
    """Smart model routing for BCM tasks"""

    def __init__(self):
        self.model_endpoints = {
            "local": "http://model_runner:8080/v1",
            "cloud_openai": "https://api.openai.com/v1",
            "cloud_anthropic": "https://api.anthropic.com/v1"
        }

        # Optimized model selection for BCM tasks
        self.model_strategy = {
            TaskComplexity.FAST: {
                "local": "smollm2:135M-Q4_K_M",           # 100MB, 0.5s response
                "cloud": "gpt-3.5-turbo"
            },
            TaskComplexity.MEDIUM: {
                "local": "gemma3:latest",                 # 2.3GB, Google quality
                "cloud": "gpt-4-turbo"
            },
            TaskComplexity.COMPLEX: {
                "local": "deepseek-r1-distill-llama:latest", # 4.6GB, real-world optimized
                "cloud": "gpt-4"
            },
            TaskComplexity.HEAVY: {
                "local": "deepcoder-preview:latest",      # 8.4GB, code reasoning + long context
                "cloud": "claude-3-sonnet-20240229"
            }
        }

        # BCM task classification
        self.bcm_task_complexity = {
            # Fast response tasks
            "incident_classify": TaskComplexity.FAST,
            "status_check": TaskComplexity.FAST,
            "quick_question": TaskComplexity.FAST,

            # Medium complexity tasks
            "process_analysis": TaskComplexity.MEDIUM,
            "risk_assessment": TaskComplexity.MEDIUM,
            "general_chat": TaskComplexity.MEDIUM,

            # Complex analysis tasks
            "bia_analysis": TaskComplexity.COMPLEX,
            "compliance_check": TaskComplexity.COMPLEX,
            "audit_preparation": TaskComplexity.COMPLEX,

            # Heavy computation tasks
            "scenario_generation": TaskComplexity.HEAVY,
            "comprehensive_report": TaskComplexity.HEAVY,
            "strategic_planning": TaskComplexity.HEAVY
        }

    def get_optimal_model(self,
                         task_type: str,
                         use_local: bool = True,
                         priority: str = "normal") -> Dict[str, Any]:
        """Get optimal model for BCM task"""

        # Determine task complexity
        complexity = self.bcm_task_complexity.get(task_type, TaskComplexity.MEDIUM)

        # Adjust for priority
        if priority == "urgent" and complexity != TaskComplexity.FAST:
            complexity = TaskComplexity.FAST
        elif priority == "detailed" and complexity != TaskComplexity.HEAVY:
            complexity = TaskComplexity.COMPLEX

        # Choose local vs cloud
        strategy = "local" if use_local else "cloud"
        model_name = self.model_strategy[complexity][strategy]
        endpoint = self.model_endpoints["local" if use_local else "cloud_openai"]

        return {
            "model": model_name,
            "endpoint": endpoint,
            "complexity": complexity.value,
            "strategy": strategy,
            "estimated_time": self._estimate_response_time(complexity, use_local),
            "recommended_for": self._get_task_recommendations(complexity)
        }

    def _estimate_response_time(self, complexity: TaskComplexity, use_local: bool) -> str:
        """Estimate response time based on model complexity"""
        if use_local:
            times = {
                TaskComplexity.FAST: "0.5-2 seconds",
                TaskComplexity.MEDIUM: "2-10 seconds",
                TaskComplexity.COMPLEX: "10-30 seconds",
                TaskComplexity.HEAVY: "30-120 seconds"
            }
        else:
            times = {
                TaskComplexity.FAST: "1-3 seconds",
                TaskComplexity.MEDIUM: "3-8 seconds",
                TaskComplexity.COMPLEX: "8-20 seconds",
                TaskComplexity.HEAVY: "20-60 seconds"
            }
        return times.get(complexity, "5-15 seconds")

    def _get_task_recommendations(self, complexity: TaskComplexity) -> list:
        """Get recommended use cases for complexity level"""
        recommendations = {
            TaskComplexity.FAST: [
                "Emergency incident classification",
                "Quick status checks",
                "Simple Q&A responses",
                "Real-time alerts"
            ],
            TaskComplexity.MEDIUM: [
                "Process risk assessment",
                "General business analysis",
                "User conversations",
                "Standard reporting"
            ],
            TaskComplexity.COMPLEX: [
                "Business Impact Analysis (BIA)",
                "ISO 22301 compliance checking",
                "Audit evidence analysis",
                "Detailed risk modeling"
            ],
            TaskComplexity.HEAVY: [
                "Comprehensive scenario generation",
                "Strategic BCM planning",
                "Complex report generation",
                "Multi-process optimization"
            ]
        }
        return recommendations.get(complexity, [])

    async def route_bcm_request(self,
                               task_type: str,
                               prompt: str,
                               context: Optional[Dict] = None,
                               priority: str = "normal") -> Dict[str, Any]:
        """Route BCM request to optimal model"""

        # Get model configuration
        model_config = self.get_optimal_model(task_type, use_local=True, priority=priority)

        # Prepare request
        request_data = {
            "model": model_config["model"],
            "messages": [
                {"role": "system", "content": self._get_bcm_system_prompt(task_type)},
                {"role": "user", "content": prompt}
            ],
            "temperature": self._get_optimal_temperature(task_type),
            "max_tokens": self._get_optimal_max_tokens(task_type)
        }

        # Add context if provided
        if context:
            request_data["messages"].insert(1, {
                "role": "system",
                "content": f"Context: {context}"
            })

        try:
            # Send to model
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{model_config['endpoint']}/chat/completions",
                    json=request_data,
                    timeout=120.0
                )
                response.raise_for_status()
                result = response.json()

            return {
                "success": True,
                "response": result["choices"][0]["message"]["content"],
                "model_used": model_config["model"],
                "complexity": model_config["complexity"],
                "processing_time": model_config["estimated_time"]
            }

        except Exception as e:
            logger.error(f"Model routing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_needed": True
            }

    def _get_bcm_system_prompt(self, task_type: str) -> str:
        """Get BCM-specific system prompt for task"""
        prompts = {
            "incident_classify": "Вы эксперт по классификации инцидентов BCM. Анализируйте инциденты по категориям: operational, security, technology, natural_disaster, human_error, external_threat. Определяйте уровень критичности: low, medium, high, critical.",

            "bia_analysis": "Вы специалист по анализу влияния на бизнес (BIA). Анализируйте бизнес-процессы для определения RTO, RPO и критичности. Учитывайте финансовые, операционные и регуляторные риски.",

            "scenario_generation": "Вы эксперт по планированию сценариев BCM. Создавайте реалистичные сценарии нарушений с учетом отраслевых угроз, географических факторов и зависимостей.",

            "compliance_check": "Вы аудитор ISO 22301. Проверяйте соответствие требованиям стандарта и выявляйте gaps в системе BCM."
        }
        return prompts.get(task_type, "Вы ассистент BCM платформы. Помогайте с задачами непрерывности бизнеса.")

    def _get_optimal_temperature(self, task_type: str) -> float:
        """Get optimal temperature for task type"""
        temperatures = {
            "incident_classify": 0.1,      # Precise classification
            "bia_analysis": 0.2,           # Accurate analysis
            "compliance_check": 0.1,       # Strict compliance
            "scenario_generation": 0.7,    # Creative scenarios
            "general_chat": 0.5            # Balanced conversation
        }
        return temperatures.get(task_type, 0.3)

    def _get_optimal_max_tokens(self, task_type: str) -> int:
        """Get optimal max tokens for task type"""
        token_limits = {
            "incident_classify": 200,      # Quick classification
            "status_check": 100,           # Brief status
            "bia_analysis": 1500,          # Detailed analysis
            "scenario_generation": 2000,   # Comprehensive scenarios
            "compliance_check": 1000,      # Compliance report
            "general_chat": 500            # Conversation
        }
        return token_limits.get(task_type, 800)

# Global router instance
bcm_model_router = BCMModelRouter()