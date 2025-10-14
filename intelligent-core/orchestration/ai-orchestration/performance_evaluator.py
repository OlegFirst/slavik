"""
Performance Evaluator for AI Orchestrator
==========================================

Автоматический расчет метрик эффективности и производительности
на основе стандартизированного framework.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics
import json


@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    # Performance
    latency_p50: float
    latency_p95: float
    latency_p99: float
    throughput: float
    cache_hit_rate: float

    # Quality
    auto_resolution_rate: float
    accuracy: float
    confidence_avg: float
    error_rate: float

    # Efficiency
    automation_rate: float
    escalation_rate: float
    delegation_accuracy: float

    # Business
    availability: float
    prevented_incidents: int
    cost_savings: float

    # Learning
    pdca_cycles: int
    quality_improvement: float
    pattern_reuse_rate: float

    # Safety
    safety_approval_rate: float
    policy_compliance: float
    audit_completeness: float


class PerformanceEvaluator:
    """
    Evaluates orchestrator performance against standardized framework.

    Calculates:
    - Individual metric scores
    - Category scores (6 categories)
    - Overall Performance Score (OPS)
    - Maturity Level
    - SLA Compliance
    """

    # Target values for metrics
    TARGETS = {
        # Performance
        'latency_p95': 50.0,  # ms
        'throughput': 100.0,  # decisions/sec
        'cache_hit_rate': 80.0,  # %

        # Quality
        'auto_resolution_rate': 70.0,  # %
        'accuracy': 90.0,  # %
        'confidence_avg': 80.0,  # %

        # Efficiency
        'automation_rate': 80.0,  # %
        'escalation_rate': 15.0,  # % (lower is better)
        'delegation_accuracy': 95.0,  # %

        # Business
        'availability': 99.9,  # %

        # Learning
        'pdca_cycles': 100,  # per month
        'quality_improvement': 5.0,  # % per month
        'pattern_reuse_rate': 70.0,  # %

        # Safety
        'safety_approval_rate': 95.0,  # %
        'policy_compliance': 99.0,  # %
        'audit_completeness': 100.0,  # %
    }

    # Weights for Overall Performance Score
    WEIGHTS = {
        'performance': 0.20,
        'quality': 0.25,
        'efficiency': 0.20,
        'business': 0.15,
        'learning': 0.10,
        'safety': 0.10
    }

    def __init__(self):
        self.evaluation_time = datetime.utcnow()

    def evaluate(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """
        Full performance evaluation.

        Returns:
            {
                'overall_score': float,
                'maturity_level': str,
                'category_scores': {...},
                'metric_scores': {...},
                'sla_compliance': {...},
                'recommendations': [...]
            }
        """
        # Calculate category scores
        category_scores = {
            'performance': self._score_performance(metrics),
            'quality': self._score_quality(metrics),
            'efficiency': self._score_efficiency(metrics),
            'business': self._score_business(metrics),
            'learning': self._score_learning(metrics),
            'safety': self._score_safety(metrics)
        }

        # Calculate Overall Performance Score
        ops = sum(
            category_scores[category] * self.WEIGHTS[category]
            for category in category_scores
        )

        # Determine maturity level
        maturity = self._calculate_maturity(ops)

        # SLA compliance
        sla_compliance = self._check_sla_compliance(metrics)

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, category_scores)

        return {
            'evaluation_time': self.evaluation_time.isoformat(),
            'overall_score': round(ops, 3),
            'maturity_level': maturity,
            'category_scores': {k: round(v, 3) for k, v in category_scores.items()},
            'sla_compliance': sla_compliance,
            'recommendations': recommendations,
            'targets_met': self._count_targets_met(metrics),
            'summary': self._generate_summary(ops, maturity, category_scores)
        }

    def _score_performance(self, metrics: PerformanceMetrics) -> float:
        """Score performance category (0.0 to 1.0)"""
        scores = []

        # Latency score (inverse - lower is better)
        if metrics.latency_p95 <= 50:
            latency_score = 1.0
        elif metrics.latency_p95 <= 100:
            latency_score = 0.7
        elif metrics.latency_p95 <= 150:
            latency_score = 0.4
        else:
            latency_score = 0.2
        scores.append(latency_score)

        # Throughput score
        throughput_score = min(metrics.throughput / self.TARGETS['throughput'], 1.0)
        scores.append(throughput_score)

        # Cache hit rate score
        cache_score = metrics.cache_hit_rate / 100.0
        scores.append(cache_score)

        return statistics.mean(scores)

    def _score_quality(self, metrics: PerformanceMetrics) -> float:
        """Score quality category (0.0 to 1.0)"""
        scores = []

        # Auto-resolution rate
        auto_res_score = min(metrics.auto_resolution_rate / self.TARGETS['auto_resolution_rate'], 1.0)
        scores.append(auto_res_score)

        # Accuracy
        if metrics.accuracy >= self.TARGETS['accuracy']:
            accuracy_score = 1.0
        elif metrics.accuracy >= 85:
            accuracy_score = 0.8
        elif metrics.accuracy >= 80:
            accuracy_score = 0.6
        else:
            accuracy_score = 0.3
        scores.append(accuracy_score)

        # Confidence
        confidence_score = metrics.confidence_avg / 100.0
        scores.append(confidence_score)

        # Error rate (inverse)
        error_score = max(1.0 - (metrics.error_rate * 10), 0.0)
        scores.append(error_score)

        return statistics.mean(scores)

    def _score_efficiency(self, metrics: PerformanceMetrics) -> float:
        """Score efficiency category (0.0 to 1.0)"""
        scores = []

        # Automation rate
        automation_score = min(metrics.automation_rate / self.TARGETS['automation_rate'], 1.0)
        scores.append(automation_score)

        # Escalation rate (inverse - lower is better)
        if metrics.escalation_rate <= self.TARGETS['escalation_rate']:
            escalation_score = 1.0
        elif metrics.escalation_rate <= 20:
            escalation_score = 0.7
        elif metrics.escalation_rate <= 30:
            escalation_score = 0.4
        else:
            escalation_score = 0.2
        scores.append(escalation_score)

        # Delegation accuracy
        delegation_score = metrics.delegation_accuracy / 100.0
        scores.append(delegation_score)

        return statistics.mean(scores)

    def _score_business(self, metrics: PerformanceMetrics) -> float:
        """Score business impact category (0.0 to 1.0)"""
        scores = []

        # Availability
        if metrics.availability >= 99.9:
            availability_score = 1.0
        elif metrics.availability >= 99.5:
            availability_score = 0.8
        elif metrics.availability >= 99.0:
            availability_score = 0.6
        else:
            availability_score = 0.3
        scores.append(availability_score)

        # Prevented incidents (normalized)
        prevented_score = min(metrics.prevented_incidents / 20, 1.0)
        scores.append(prevented_score)

        # Cost savings (normalized to $50k/month)
        cost_score = min(metrics.cost_savings / 50000, 1.0)
        scores.append(cost_score)

        return statistics.mean(scores)

    def _score_learning(self, metrics: PerformanceMetrics) -> float:
        """Score learning & evolution category (0.0 to 1.0)"""
        scores = []

        # PDCA cycles
        pdca_score = min(metrics.pdca_cycles / self.TARGETS['pdca_cycles'], 1.0)
        scores.append(pdca_score)

        # Quality improvement
        improvement_score = min(metrics.quality_improvement / self.TARGETS['quality_improvement'], 1.0)
        scores.append(improvement_score)

        # Pattern reuse
        reuse_score = metrics.pattern_reuse_rate / 100.0
        scores.append(reuse_score)

        return statistics.mean(scores)

    def _score_safety(self, metrics: PerformanceMetrics) -> float:
        """Score safety & reliability category (0.0 to 1.0)"""
        scores = []

        # Safety approval rate
        safety_score = metrics.safety_approval_rate / 100.0
        scores.append(safety_score)

        # Policy compliance
        policy_score = metrics.policy_compliance / 100.0
        scores.append(policy_score)

        # Audit completeness
        audit_score = metrics.audit_completeness / 100.0
        scores.append(audit_score)

        return statistics.mean(scores)

    def _calculate_maturity(self, ops: float) -> str:
        """Determine maturity level from OPS"""
        if ops >= 0.95:
            return "Level 5: Innovative"
        elif ops >= 0.85:
            return "Level 4: Optimized"
        elif ops >= 0.75:
            return "Level 3: Defined"
        elif ops >= 0.60:
            return "Level 2: Managed"
        else:
            return "Level 1: Initial"

    def _check_sla_compliance(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Check SLA compliance"""
        compliance = {}

        # Performance SLA
        compliance['performance'] = {
            'latency_p95': metrics.latency_p95 <= 50,
            'throughput': metrics.throughput >= 100,
            'met': metrics.latency_p95 <= 50 and metrics.throughput >= 100
        }

        # Quality SLA
        compliance['quality'] = {
            'accuracy': metrics.accuracy >= 90,
            'auto_resolution': metrics.auto_resolution_rate >= 70,
            'met': metrics.accuracy >= 90 and metrics.auto_resolution_rate >= 70
        }

        # Availability SLA
        compliance['availability'] = {
            'uptime': metrics.availability >= 99.9,
            'met': metrics.availability >= 99.9
        }

        # Safety SLA
        compliance['safety'] = {
            'policy_compliance': metrics.policy_compliance >= 99,
            'safety_approval': metrics.safety_approval_rate >= 95,
            'met': metrics.policy_compliance >= 99 and metrics.safety_approval_rate >= 95
        }

        # Overall SLA
        all_met = all(c['met'] for c in compliance.values())
        compliance['overall'] = {
            'met': all_met,
            'percentage': sum(1 for c in compliance.values() if c['met']) / len(compliance) * 100
        }

        return compliance

    def _count_targets_met(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Count how many targets were met"""
        targets_status = {}

        # Performance
        targets_status['latency_p95'] = metrics.latency_p95 <= self.TARGETS['latency_p95']
        targets_status['cache_hit_rate'] = metrics.cache_hit_rate >= self.TARGETS['cache_hit_rate']

        # Quality
        targets_status['auto_resolution'] = metrics.auto_resolution_rate >= self.TARGETS['auto_resolution_rate']
        targets_status['accuracy'] = metrics.accuracy >= self.TARGETS['accuracy']

        # Efficiency
        targets_status['automation'] = metrics.automation_rate >= self.TARGETS['automation_rate']
        targets_status['escalation'] = metrics.escalation_rate <= self.TARGETS['escalation_rate']

        # Safety
        targets_status['safety_approval'] = metrics.safety_approval_rate >= self.TARGETS['safety_approval_rate']
        targets_status['policy_compliance'] = metrics.policy_compliance >= self.TARGETS['policy_compliance']

        met_count = sum(1 for v in targets_status.values() if v)
        total_count = len(targets_status)

        return {
            'met': met_count,
            'total': total_count,
            'percentage': round(met_count / total_count * 100, 1),
            'details': targets_status
        }

    def _generate_recommendations(
        self,
        metrics: PerformanceMetrics,
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        # Performance recommendations
        if category_scores['performance'] < 0.8:
            if metrics.latency_p95 > 50:
                recommendations.append(
                    f"⚠️ Latency P95 ({metrics.latency_p95}ms) exceeds target (50ms). "
                    "Consider: caching optimization, async processing, resource scaling."
                )
            if metrics.cache_hit_rate < 80:
                recommendations.append(
                    f"⚠️ Cache hit rate ({metrics.cache_hit_rate}%) below target (80%). "
                    "Review cache strategy and TTL settings."
                )

        # Quality recommendations
        if category_scores['quality'] < 0.8:
            if metrics.accuracy < 90:
                recommendations.append(
                    f"⚠️ Accuracy ({metrics.accuracy}%) below target (90%). "
                    "Retrain models with recent data, review decision logic."
                )
            if metrics.auto_resolution_rate < 70:
                recommendations.append(
                    f"⚠️ Auto-resolution rate ({metrics.auto_resolution_rate}%) below target (70%). "
                    "Expand automation rules, improve confidence thresholds."
                )

        # Efficiency recommendations
        if category_scores['efficiency'] < 0.8:
            if metrics.escalation_rate > 15:
                recommendations.append(
                    f"⚠️ Escalation rate ({metrics.escalation_rate}%) above target (15%). "
                    "Review escalation criteria, enhance AI capabilities."
                )

        # Learning recommendations
        if category_scores['learning'] < 0.7:
            if metrics.pdca_cycles < 100:
                recommendations.append(
                    f"⚠️ PDCA cycles ({metrics.pdca_cycles}) below target (100/month). "
                    "Increase workflow completion rate, automate PDCA triggers."
                )

        # Safety recommendations
        if category_scores['safety'] < 0.9:
            if metrics.policy_compliance < 99:
                recommendations.append(
                    f"⚠️ Policy compliance ({metrics.policy_compliance}%) below target (99%). "
                    "Review policy violations, update safety rules."
                )

        if not recommendations:
            recommendations.append("✅ All metrics within targets. Continue monitoring.")

        return recommendations

    def _generate_summary(
        self,
        ops: float,
        maturity: str,
        category_scores: Dict[str, float]
    ) -> str:
        """Generate executive summary"""
        # Find best and worst categories
        best_category = max(category_scores.items(), key=lambda x: x[1])
        worst_category = min(category_scores.items(), key=lambda x: x[1])

        summary = f"""
Overall Performance Score: {ops:.3f} ({maturity})

Strengths:
  ✅ {best_category[0].title()}: {best_category[1]:.2f}

Areas for Improvement:
  ⚠️ {worst_category[0].title()}: {worst_category[1]:.2f}

Status: {'🟢 Excellent' if ops >= 0.90 else '🟡 Good' if ops >= 0.80 else '🟠 Needs Improvement' if ops >= 0.70 else '🔴 Critical'}
        """.strip()

        return summary


def example_evaluation():
    """Example usage of PerformanceEvaluator"""

    # Sample metrics (from our standalone API)
    metrics = PerformanceMetrics(
        # Performance
        latency_p50=28.3,
        latency_p95=42.5,
        latency_p99=87.2,
        throughput=14.4,  # per second
        cache_hit_rate=83.2,

        # Quality
        auto_resolution_rate=71.5,
        accuracy=92.3,
        confidence_avg=84.7,
        error_rate=0.08,  # 0.08%

        # Efficiency
        automation_rate=83.2,
        escalation_rate=6.2,
        delegation_accuracy=94.8,

        # Business
        availability=99.98,
        prevented_incidents=18,
        cost_savings=47500,

        # Learning
        pdca_cycles=189,
        quality_improvement=6.3,
        pattern_reuse_rate=78.4,

        # Safety
        safety_approval_rate=98.2,
        policy_compliance=99.8,
        audit_completeness=100.0
    )

    # Evaluate
    evaluator = PerformanceEvaluator()
    results = evaluator.evaluate(metrics)

    # Print results
    print("=" * 60)
    print("AI ORCHESTRATOR PERFORMANCE EVALUATION")
    print("=" * 60)
    print(f"\nTimestamp: {results['evaluation_time']}")
    print(f"\nOverall Performance Score (OPS): {results['overall_score']}")
    print(f"Maturity Level: {results['maturity_level']}")

    print(f"\nCategory Scores:")
    for category, score in results['category_scores'].items():
        status = "✅" if score >= 0.8 else "⚠️" if score >= 0.7 else "❌"
        print(f"  {status} {category.title()}: {score:.3f}")

    print(f"\nSLA Compliance:")
    for sla_type, status in results['sla_compliance'].items():
        if sla_type != 'overall':
            met = "✅" if status['met'] else "❌"
            print(f"  {met} {sla_type.title()}: {'PASS' if status['met'] else 'FAIL'}")

    overall_sla = results['sla_compliance']['overall']
    print(f"\n  Overall SLA: {overall_sla['percentage']:.1f}% ({overall_sla['met'] and 'PASS' or 'FAIL'})")

    print(f"\nTargets Met: {results['targets_met']['met']}/{results['targets_met']['total']} " +
          f"({results['targets_met']['percentage']}%)")

    print(f"\nRecommendations:")
    for rec in results['recommendations']:
        print(f"  {rec}")

    print(f"\n{results['summary']}")

    print("\n" + "=" * 60)

    # Save to file
    with open('/tmp/orchestrator_evaluation.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\nResults saved to: /tmp/orchestrator_evaluation.json")


if __name__ == '__main__':
    example_evaluation()
