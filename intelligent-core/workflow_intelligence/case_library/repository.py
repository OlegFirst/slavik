"""
Case Repository - поиск и анализ workflow cases

Features:
- Semantic search (похожие cases)
- Filtering (industry, size, success)
- Benchmarking (статистика)
- Trending analysis
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, timedelta
from .database import WorkflowCaseDB
from .models import WorkflowCase, OrganizationContext, WorkflowStepRecord, WorkflowMetrics
import statistics

class CaseRepository:
    """
    Repository для поиска и анализа workflow cases

    Features:
    - Semantic search (похожие cases)
    - Filtering (industry, size, success)
    - Benchmarking (статистика)
    - Trending analysis
    """

    def __init__(self, db_session: AsyncSession, vector_db_client=None):
        self.db = db_session
        self.vector_db = vector_db_client

    async def find_similar_cases(
        self,
        industry: str,
        size: str,
        module: str,
        current_stage: Optional[str] = None,
        success_only: bool = True,
        limit: int = 5
    ) -> List[WorkflowCase]:
        """
        Найти похожие успешные cases

        Использует комбинацию:
        1. Exact match (industry, size, module)
        2. Semantic search (если есть vector DB)
        3. Success filter
        """

        # Build query
        query = select(WorkflowCaseDB).where(
            and_(
                WorkflowCaseDB.org_industry == industry,
                WorkflowCaseDB.org_size == size,
                WorkflowCaseDB.module == module
            )
        )

        if success_only:
            query = query.where(WorkflowCaseDB.success == True)

        # Order by relevance (recent + high AI usage = more relevant)
        query = query.order_by(
            WorkflowCaseDB.created_at.desc(),
            WorkflowCaseDB.ai_usage_count.desc()
        ).limit(limit)

        result = await self.db.execute(query)
        case_records = result.scalars().all()

        # Convert to domain models
        cases = [self._to_domain_model(record) for record in case_records]

        return cases

    async def semantic_search(
        self,
        query_text: str,
        module: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> List[WorkflowCase]:
        """
        Semantic search через vector DB

        Использует embeddings для поиска концептуально похожих cases
        """
        if not self.vector_db:
            # Fallback to regular search
            return await self.find_similar_cases(
                industry=filters.get('industry', 'healthcare'),
                size=filters.get('size', 'medium'),
                module=module,
                limit=limit
            )

        # Create embedding for query
        query_embedding = await self.vector_db.embed(query_text)

        # Search in vector DB
        vector_results = await self.vector_db.query(
            vector=query_embedding,
            filter={
                'module': module,
                **(filters or {})
            },
            top_k=limit
        )

        # Get full cases from PostgreSQL
        case_ids = [result['id'] for result in vector_results]

        result = await self.db.execute(
            select(WorkflowCaseDB).where(
                WorkflowCaseDB.case_id.in_(case_ids)
            )
        )
        case_records = result.scalars().all()

        cases = [self._to_domain_model(record) for record in case_records]

        return cases

    async def get_benchmarks(
        self,
        industry: str,
        size: str,
        module: str
    ) -> Dict[str, Any]:
        """
        Получить industry benchmarks

        Агрегирует статистику по всем успешным cases
        """

        # Get all successful cases for this context
        result = await self.db.execute(
            select(WorkflowCaseDB).where(
                and_(
                    WorkflowCaseDB.org_industry == industry,
                    WorkflowCaseDB.org_size == size,
                    WorkflowCaseDB.module == module,
                    WorkflowCaseDB.success == True
                )
            )
        )
        cases = result.scalars().all()

        if not cases:
            return {
                'message': 'No benchmark data available yet',
                'total_cases': 0
            }

        # Calculate statistics
        durations = [c.duration_days for c in cases]
        ai_usage = [c.ai_usage_count for c in cases]
        challenges = [c.challenges_count for c in cases]

        # Aggregate success patterns
        all_patterns = []
        for case in cases:
            if case.success_patterns:
                all_patterns.extend(case.success_patterns)

        # Count pattern frequency
        pattern_counts = {}
        for pattern in all_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        # Top patterns
        top_patterns = sorted(
            pattern_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Calculate AI correlation
        high_ai_cases = [c for c in cases if c.ai_usage_count > statistics.median(ai_usage)]
        ai_success_rate = len(high_ai_cases) / len(cases)

        return {
            'total_cases': len(cases),
            'duration': {
                'avg_days': round(statistics.mean(durations), 1),
                'median_days': round(statistics.median(durations), 1),
                'min_days': round(min(durations), 1),
                'max_days': round(max(durations), 1),
                'std_dev': round(statistics.stdev(durations), 1) if len(durations) > 1 else 0
            },
            'ai_usage': {
                'avg_count': round(statistics.mean(ai_usage), 1),
                'median_count': int(statistics.median(ai_usage)),
                'correlation_with_success': round(ai_success_rate, 2)
            },
            'challenges': {
                'avg_count': round(statistics.mean(challenges), 1),
                'cases_with_challenges': len([c for c in cases if c.challenges_count > 0])
            },
            'top_success_patterns': [
                {'pattern': pattern, 'frequency': count}
                for pattern, count in top_patterns
            ],
            'success_rate': 1.0,  # Already filtered by success
            'sample_size_reliability': self._assess_reliability(len(cases))
        }

    def _assess_reliability(self, sample_size: int) -> str:
        """Оценить надежность benchmarks"""
        if sample_size < 5:
            return 'low - very limited data'
        elif sample_size < 15:
            return 'medium - some data available'
        elif sample_size < 50:
            return 'good - reasonable sample size'
        else:
            return 'high - large dataset'

    async def get_trending_patterns(
        self,
        module: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Получить trending success patterns за последний период
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await self.db.execute(
            select(WorkflowCaseDB).where(
                and_(
                    WorkflowCaseDB.module == module,
                    WorkflowCaseDB.success == True,
                    WorkflowCaseDB.created_at >= cutoff_date
                )
            )
        )
        recent_cases = result.scalars().all()

        if not recent_cases:
            return []

        # Aggregate patterns
        pattern_frequency = {}
        for case in recent_cases:
            if case.success_patterns:
                for pattern in case.success_patterns:
                    pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1

        # Calculate trend score (frequency × recency weight)
        trends = []
        for pattern, count in pattern_frequency.items():
            # Recent patterns weighted higher
            recent_weight = sum(
                1.0 if (datetime.utcnow() - c.created_at).days < 7 else 0.5
                for c in recent_cases
                if c.success_patterns and pattern in c.success_patterns
            )

            trend_score = count * recent_weight
            trends.append({
                'pattern': pattern,
                'frequency': count,
                'trend_score': round(trend_score, 2)
            })

        # Sort by trend score
        trends.sort(key=lambda x: x['trend_score'], reverse=True)

        return trends[:10]

    async def compare_to_benchmarks(
        self,
        current_metrics: Dict[str, Any],
        industry: str,
        size: str,
        module: str
    ) -> Dict[str, Any]:
        """
        Сравнить текущий progress с benchmarks
        """
        benchmarks = await self.get_benchmarks(industry, size, module)

        if benchmarks.get('total_cases', 0) == 0:
            return {
                'message': 'No benchmark data available for comparison',
                'comparison': None
            }

        current_duration = current_metrics.get('duration_days', 0)
        current_ai_usage = current_metrics.get('ai_usage_count', 0)

        comparison = {
            'duration': {
                'current': current_duration,
                'benchmark_avg': benchmarks['duration']['avg_days'],
                'vs_benchmark': 'on track' if current_duration <= benchmarks['duration']['avg_days'] else 'slower than average',
                'percentile': self._calculate_percentile(
                    current_duration,
                    benchmarks['duration']
                )
            },
            'ai_usage': {
                'current': current_ai_usage,
                'benchmark_avg': benchmarks['ai_usage']['avg_count'],
                'vs_benchmark': 'above average' if current_ai_usage > benchmarks['ai_usage']['avg_count'] else 'below average'
            },
            'overall_assessment': self._assess_progress(
                current_metrics, benchmarks
            )
        }

        return {
            'benchmarks': benchmarks,
            'comparison': comparison
        }

    def _calculate_percentile(self, value: float, distribution: Dict[str, float]) -> int:
        """Вычислить percentile"""
        if value <= distribution['min_days']:
            return 10
        elif value <= distribution['median_days']:
            return 50
        elif value <= distribution['avg_days']:
            return 70
        elif value <= distribution['max_days']:
            return 90
        else:
            return 95

    def _assess_progress(
        self,
        current: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> str:
        """Общая оценка прогресса"""
        duration_ok = current.get('duration_days', 0) <= benchmarks['duration']['avg_days'] * 1.2
        ai_usage_ok = current.get('ai_usage_count', 0) >= benchmarks['ai_usage']['avg_count'] * 0.5

        if duration_ok and ai_usage_ok:
            return 'excellent - on track and using AI effectively'
        elif duration_ok:
            return 'good - on schedule, consider more AI assistance'
        elif ai_usage_ok:
            return 'needs improvement - taking longer than average despite AI usage'
        else:
            return 'at risk - slower than average and low AI usage'

    def _to_domain_model(self, record: WorkflowCaseDB) -> WorkflowCase:
        """Convert database record to domain model"""

        org_context = OrganizationContext(
            industry=record.org_industry,
            size=record.org_size,
            maturity_level=record.org_maturity,
            region=record.org_region,
            regulatory_context=record.org_regulatory or []
        )

        # Reconstruct journey from JSON
        journey = []
        for step_data in record.journey:
            journey.append(WorkflowStep(
                stage=step_data['stage'],
                started_at=datetime.fromisoformat(step_data['started_at']),
                completed_at=datetime.fromisoformat(step_data['completed_at']) if step_data.get('completed_at') else None,
                duration_hours=step_data.get('duration_hours'),
                actions=step_data.get('actions', []),
                challenges=step_data.get('challenges', []),
                ai_interventions=step_data.get('ai_interventions', [])
            ))

        metrics = WorkflowMetrics(
            total_duration_days=record.duration_days,
            processes_count=record.processes_count,
            ai_usage_count=record.ai_usage_count,
            user_satisfaction=record.user_satisfaction,
            challenges_encountered=record.challenges_count,
            challenges_resolved=0,  # Would need to parse from journey
            completed_successfully=record.success
        )

        return WorkflowCase(
            case_id=str(record.case_id),
            module=record.module,
            workflow_name=record.workflow_name,
            organization_context=org_context,
            journey=journey,
            metrics=metrics,
            success_patterns=record.success_patterns or [],
            lessons_learned=record.lessons_learned or [],
            features=record.features or {},
            created_at=record.created_at,
            status=CaseStatus(record.status)
        )
