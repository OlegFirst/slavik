"""
ACE Service - Centralized Agentic Context Engineering Service
==============================================================

Централизованный сервис для всей платформы:
- Evolving context playbooks для всех модулей
- PostgreSQL интеграция
- Monitoring & Analytics
- REST API для всех компонентов

Port: 8050
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
import asyncpg
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Models
# ============================================================================

class GenerateContextRequest(BaseModel):
    """Request to generate enhanced context"""
    task_type: str = Field(..., description="Type of task (e.g., 'scenario_generation_L1')")
    base_context: Dict[str, Any] = Field(..., description="Base context dictionary")
    module_name: Optional[str] = Field(None, description="Module name (e.g., 'scenario_intelligence')")
    domain_knowledge: Optional[Dict[str, Any]] = Field(None, description="Additional domain knowledge")


class TrajectoryData(BaseModel):
    """Trajectory data for reflection"""
    input_context: Dict[str, Any]
    output_result: Dict[str, Any]
    execution_time_ms: float
    success: bool
    effectiveness: Optional[float] = None
    validation: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ReflectRequest(BaseModel):
    """Request to reflect on trajectory"""
    task_type: str
    trajectory: TrajectoryData
    module_name: Optional[str] = None


class CurateRequest(BaseModel):
    """Request to curate playbook"""
    task_type: str
    insights: Dict[str, Any]
    module_name: Optional[str] = None
    preserve_knowledge: bool = True


class PlaybookStatsResponse(BaseModel):
    """Playbook statistics"""
    task_type: str
    module_name: Optional[str]
    version: int
    strategies_count: int
    patterns_count: int
    knowledge_count: int
    successful_examples_count: int
    failed_examples_count: int
    usage_count: int
    success_rate: float
    avg_effectiveness: float
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]


# ============================================================================
# ACE Service Core
# ============================================================================

class ACEService:
    """Centralized ACE Service with PostgreSQL backend"""

    def __init__(self):
        self.db_pool: Optional[asyncpg.Pool] = None
        self.initialized = False

        # Statistics
        self.stats = {
            'contexts_generated': 0,
            'trajectories_reflected': 0,
            'playbooks_curated': 0,
            'total_tasks': 0
        }

    async def initialize(self):
        """Initialize ACE Service with database connection"""
        if self.initialized:
            logger.warning("ACE Service already initialized")
            return

        try:
            # Connect to PostgreSQL
            db_url = os.getenv(
                'DATABASE_URL',
                'postgresql://postgres:postgres@localhost:5432/bcm_platform'
            )

            logger.info(f"Connecting to database...")
            self.db_pool = await asyncpg.create_pool(
                db_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )

            # Test connection
            async with self.db_pool.acquire() as conn:
                version = await conn.fetchval('SELECT version()')
                logger.info(f"✅ Connected to PostgreSQL: {version[:50]}...")

            # Initialize schema (if not exists)
            await self._initialize_schema()

            self.initialized = True
            logger.info("✅ ACE Service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize ACE Service: {e}")
            raise

    async def _initialize_schema(self):
        """Initialize ACE schema in database"""
        try:
            async with self.db_pool.acquire() as conn:
                # Check if tables exist
                exists = await conn.fetchval('''
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'ace_playbooks'
                    )
                ''')

                if exists:
                    logger.info("✅ ACE tables already exist")
                    return

                # Read and execute schema
                schema_path = os.path.join(
                    os.path.dirname(__file__),
                    '../database/schemas/ace_playbooks.sql'
                )

                if os.path.exists(schema_path):
                    with open(schema_path, 'r') as f:
                        schema_sql = f.read()

                    await conn.execute(schema_sql)
                    logger.info("✅ ACE schema created successfully")
                else:
                    logger.warning(f"Schema file not found: {schema_path}")

        except Exception as e:
            logger.error(f"Schema initialization error: {e}")
            # Non-critical - continue without schema

    async def shutdown(self):
        """Shutdown ACE Service"""
        if self.db_pool:
            await self.db_pool.close()
            logger.info("✅ Database pool closed")

    # ========================================================================
    # 1. GENERATOR - Create enhanced context
    # ========================================================================

    async def generate_context(
        self,
        task_type: str,
        base_context: Dict[str, Any],
        module_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate enhanced context with evolving playbook

        Args:
            task_type: Task type identifier
            base_context: Base context dictionary
            module_name: Optional module name
            **kwargs: Additional context

        Returns:
            Enhanced context with playbook strategies, patterns, knowledge
        """
        if not self.initialized:
            raise RuntimeError("ACE Service not initialized")

        try:
            # Get latest playbook from database
            playbook = await self._get_latest_playbook(task_type, module_name)

            # Generate enhanced context
            enhanced_context = {
                **base_context,
                'playbook_strategies': playbook.get('strategies', []),
                'known_patterns': playbook.get('patterns', []),
                'domain_expertise': playbook.get('domain_knowledge', []),
                'successful_examples': playbook.get('successful_examples', [])[:5],
                **kwargs
            }

            # Update stats
            self.stats['contexts_generated'] += 1

            logger.info(
                f"Generated context for {task_type}: "
                f"{len(enhanced_context.get('playbook_strategies', []))} strategies, "
                f"{len(enhanced_context.get('known_patterns', []))} patterns"
            )

            return enhanced_context

        except Exception as e:
            logger.error(f"Error generating context: {e}")
            # Fallback to base context
            return base_context

    # ========================================================================
    # 2. REFLECTOR - Analyze trajectory
    # ========================================================================

    async def reflect_on_trajectory(
        self,
        task_type: str,
        trajectory: Dict[str, Any],
        module_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze trajectory and identify insights

        Args:
            task_type: Task type
            trajectory: Execution trajectory
            module_name: Optional module name

        Returns:
            Insights dictionary with successful/failed strategies, patterns, improvements
        """
        if not self.initialized:
            raise RuntimeError("ACE Service not initialized")

        try:
            insights = {
                'successful_strategies': [],
                'failed_strategies': [],
                'new_patterns': [],
                'improvements': []
            }

            # Analyze trajectory
            # Check validation
            if trajectory.get('validation', {}).get('approved'):
                insights['successful_strategies'].append(
                    "Validation approved by community/system"
                )

            # Check effectiveness
            effectiveness = trajectory.get('effectiveness', 0)
            if effectiveness > 0.8:
                insights['successful_strategies'].append(
                    f"High effectiveness achieved: {effectiveness:.1%}"
                )
            elif effectiveness < 0.5:
                insights['failed_strategies'].append(
                    f"Low effectiveness: {effectiveness:.1%}"
                )

            # Check execution time
            exec_time = trajectory.get('execution_time_ms', 0)
            if exec_time < 1000:
                insights['improvements'].append(
                    "Fast execution time achieved"
                )

            # Check success
            if trajectory.get('success'):
                insights['successful_strategies'].append(
                    "Task completed successfully"
                )
            else:
                insights['failed_strategies'].append(
                    "Task failed - analyze root cause"
                )

            # Detect patterns from metadata
            metadata = trajectory.get('metadata', {})
            if metadata.get('pattern_detected'):
                insights['new_patterns'].append({
                    'type': metadata.get('pattern_type', 'unknown'),
                    'confidence': metadata.get('pattern_confidence', 0.5),
                    'detected_at': datetime.utcnow().isoformat()
                })

            # Log trajectory to database
            await self._log_trajectory(task_type, trajectory, insights, module_name)

            # Update stats
            self.stats['trajectories_reflected'] += 1

            logger.info(
                f"Reflected on {task_type}: "
                f"{len(insights['successful_strategies'])} successful, "
                f"{len(insights['new_patterns'])} patterns"
            )

            return insights

        except Exception as e:
            logger.error(f"Error reflecting on trajectory: {e}")
            return {
                'successful_strategies': [],
                'failed_strategies': [],
                'new_patterns': [],
                'improvements': []
            }

    # ========================================================================
    # 3. CURATOR - Update playbook
    # ========================================================================

    async def curate_playbook(
        self,
        task_type: str,
        insights: Dict[str, Any],
        module_name: Optional[str] = None,
        preserve_knowledge: bool = True
    ) -> Dict[str, Any]:
        """
        Update playbook incrementally (no context collapse!)

        Args:
            task_type: Task type
            insights: Insights from reflector
            module_name: Optional module name
            preserve_knowledge: Preserve existing knowledge (default: True)

        Returns:
            Updated playbook
        """
        if not self.initialized:
            raise RuntimeError("ACE Service not initialized")

        try:
            # Get current playbook
            current_playbook = await self._get_latest_playbook(task_type, module_name)

            # Create updated playbook (preserve knowledge!)
            updated_playbook = {
                'strategies': current_playbook.get('strategies', []).copy() if preserve_knowledge else [],
                'patterns': current_playbook.get('patterns', []).copy() if preserve_knowledge else [],
                'domain_knowledge': current_playbook.get('domain_knowledge', []).copy() if preserve_knowledge else [],
                'successful_examples': current_playbook.get('successful_examples', []).copy() if preserve_knowledge else [],
                'failed_examples': current_playbook.get('failed_examples', []).copy() if preserve_knowledge else []
            }

            # Add successful strategies
            for strategy in insights.get('successful_strategies', []):
                if strategy not in updated_playbook['strategies']:
                    updated_playbook['strategies'].append(strategy)

            # Remove failed strategies
            for strategy in insights.get('failed_strategies', []):
                if strategy in updated_playbook['strategies']:
                    updated_playbook['strategies'].remove(strategy)

            # Add new patterns
            for pattern in insights.get('new_patterns', []):
                updated_playbook['patterns'].append(pattern)

            # Add improvements
            for improvement in insights.get('improvements', []):
                if improvement not in updated_playbook['domain_knowledge']:
                    updated_playbook['domain_knowledge'].append(improvement)

            # Limit sizes (keep most relevant)
            if len(updated_playbook['strategies']) > 50:
                updated_playbook['strategies'] = updated_playbook['strategies'][-50:]

            if len(updated_playbook['patterns']) > 100:
                updated_playbook['patterns'] = updated_playbook['patterns'][-100:]

            # Save to database
            await self._update_playbook(task_type, updated_playbook, module_name, insights)

            # Update stats
            self.stats['playbooks_curated'] += 1

            logger.info(
                f"Curated playbook for {task_type}: "
                f"{len(updated_playbook['strategies'])} strategies, "
                f"{len(updated_playbook['patterns'])} patterns"
            )

            return updated_playbook

        except Exception as e:
            logger.error(f"Error curating playbook: {e}")
            raise

    # ========================================================================
    # Database Operations
    # ========================================================================

    async def _get_latest_playbook(
        self,
        task_type: str,
        module_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get latest playbook from database"""
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.fetchval(
                    'SELECT get_latest_ace_playbook($1)',
                    task_type
                )

                if result:
                    return dict(result)
                else:
                    # Return empty playbook
                    return {
                        'strategies': [],
                        'patterns': [],
                        'domain_knowledge': [],
                        'successful_examples': [],
                        'failed_examples': []
                    }

        except Exception as e:
            logger.error(f"Error fetching playbook: {e}")
            # Return empty playbook on error
            return {
                'strategies': [],
                'patterns': [],
                'domain_knowledge': [],
                'successful_examples': [],
                'failed_examples': []
            }

    async def _update_playbook(
        self,
        task_type: str,
        playbook: Dict[str, Any],
        module_name: Optional[str],
        insights: Dict[str, Any]
    ):
        """Update playbook in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.fetchval(
                    'SELECT update_ace_playbook($1, $2, $3, $4)',
                    task_type,
                    module_name,
                    playbook,
                    insights
                )

                logger.info(f"✅ Playbook updated in database: {task_type}")

        except Exception as e:
            logger.error(f"Error updating playbook: {e}")
            # Non-critical - continue

    async def _log_trajectory(
        self,
        task_type: str,
        trajectory: Dict[str, Any],
        insights: Dict[str, Any],
        module_name: Optional[str]
    ):
        """Log trajectory to database"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get playbook ID
                playbook_id = await conn.fetchval('''
                    SELECT id FROM ace_playbooks
                    WHERE task_type = $1
                    ORDER BY version DESC
                    LIMIT 1
                ''', task_type)

                if not playbook_id:
                    logger.warning(f"No playbook found for {task_type}, skipping trajectory log")
                    return

                # Log trajectory
                await conn.fetchval(
                    'SELECT log_ace_trajectory($1, $2, $3, $4, $5, $6, $7, $8)',
                    playbook_id,
                    task_type,
                    trajectory.get('input_context', {}),
                    trajectory.get('output_result', {}),
                    trajectory,
                    insights,
                    trajectory.get('effectiveness', 0.0),
                    trajectory.get('success', False)
                )

                logger.debug(f"✅ Trajectory logged: {task_type}")

        except Exception as e:
            logger.error(f"Error logging trajectory: {e}")
            # Non-critical - continue

    async def get_playbook_stats(
        self,
        task_type: str,
        module_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get playbook statistics"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow('''
                    SELECT * FROM ace_playbook_stats
                    WHERE task_type = $1
                    ORDER BY version DESC
                    LIMIT 1
                ''', task_type)

                if row:
                    return dict(row)
                else:
                    return None

        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return None

    async def get_all_playbooks_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all playbooks"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch('''
                    SELECT DISTINCT ON (task_type)
                        task_type,
                        module_name,
                        version,
                        strategies_count,
                        patterns_count,
                        knowledge_count,
                        successful_examples_count,
                        failed_examples_count,
                        usage_count,
                        success_rate,
                        avg_effectiveness,
                        created_at,
                        updated_at,
                        last_used_at
                    FROM ace_playbook_stats
                    ORDER BY task_type, version DESC
                ''')

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error fetching all stats: {e}")
            return []

    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            **self.stats,
            'initialized': self.initialized,
            'db_connected': self.db_pool is not None
        }


# ============================================================================
# FastAPI Application
# ============================================================================

# Global ACE Service instance
ace_service = ACEService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    # Startup
    await ace_service.initialize()
    yield
    # Shutdown
    await ace_service.shutdown()


# Create FastAPI app
app = FastAPI(
    title="ACE Service",
    description="Centralized Agentic Context Engineering Service for AI Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ace-service",
        "version": "1.0.0",
        "initialized": ace_service.initialized,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    return ace_service.get_service_stats()


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        all_stats = await ace_service.get_all_playbooks_stats()
        service_stats = ace_service.get_service_stats()

        # Generate Prometheus metrics
        metrics_output = []

        # Counter metrics
        metrics_output.append("# HELP ace_playbooks_total Total number of playbooks")
        metrics_output.append("# TYPE ace_playbooks_total gauge")
        metrics_output.append(f"ace_playbooks_total {len(all_stats)}")

        metrics_output.append("# HELP ace_trajectories_total Total trajectories logged")
        metrics_output.append("# TYPE ace_trajectories_total counter")
        metrics_output.append(f"ace_trajectories_total {service_stats.get('trajectories_reflected', 0)}")

        metrics_output.append("# HELP ace_contexts_generated_total Total contexts generated")
        metrics_output.append("# TYPE ace_contexts_generated_total counter")
        metrics_output.append(f"ace_contexts_generated_total {service_stats.get('contexts_generated', 0)}")

        # Gauge metrics
        if all_stats:
            avg_effectiveness = sum(s.get('avg_effectiveness', 0) for s in all_stats) / len(all_stats)
            avg_success_rate = sum(s.get('success_rate', 0) for s in all_stats) / len(all_stats)

            metrics_output.append("# HELP ace_avg_effectiveness Average task effectiveness")
            metrics_output.append("# TYPE ace_avg_effectiveness gauge")
            metrics_output.append(f"ace_avg_effectiveness {avg_effectiveness:.4f}")

            metrics_output.append("# HELP ace_success_rate Overall success rate")
            metrics_output.append("# TYPE ace_success_rate gauge")
            metrics_output.append(f"ace_success_rate {avg_success_rate:.4f}")

        # Active modules
        active_modules = len(set(s.get('module_name') for s in all_stats if s.get('module_name')))
        metrics_output.append("# HELP ace_active_modules Number of active modules")
        metrics_output.append("# TYPE ace_active_modules gauge")
        metrics_output.append(f"ace_active_modules {active_modules}")

        return "\n".join(metrics_output)

    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return "# Error generating metrics"


@app.post("/api/v1/ace/generate-context")
async def generate_context(request: GenerateContextRequest):
    """
    Generate enhanced context with evolving playbook

    This is the GENERATOR component of ACE.
    """
    try:
        enhanced_context = await ace_service.generate_context(
            task_type=request.task_type,
            base_context=request.base_context,
            module_name=request.module_name,
            domain_knowledge=request.domain_knowledge
        )

        return {
            "success": True,
            "task_type": request.task_type,
            "enhanced_context": enhanced_context,
            "playbook_applied": True
        }

    except Exception as e:
        logger.error(f"Error in generate_context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ace/reflect")
async def reflect_on_trajectory(request: ReflectRequest):
    """
    Analyze trajectory and identify insights

    This is the REFLECTOR component of ACE.
    """
    try:
        insights = await ace_service.reflect_on_trajectory(
            task_type=request.task_type,
            trajectory=request.trajectory.dict(),
            module_name=request.module_name
        )

        return {
            "success": True,
            "task_type": request.task_type,
            "insights": insights
        }

    except Exception as e:
        logger.error(f"Error in reflect: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ace/curate")
async def curate_playbook(request: CurateRequest):
    """
    Update playbook incrementally

    This is the CURATOR component of ACE.
    """
    try:
        updated_playbook = await ace_service.curate_playbook(
            task_type=request.task_type,
            insights=request.insights,
            module_name=request.module_name,
            preserve_knowledge=request.preserve_knowledge
        )

        return {
            "success": True,
            "task_type": request.task_type,
            "playbook": updated_playbook,
            "updated": True
        }

    except Exception as e:
        logger.error(f"Error in curate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ace/playbook/{task_type}/stats")
async def get_playbook_stats(task_type: str, module_name: Optional[str] = None):
    """Get statistics for specific playbook"""
    try:
        stats = await ace_service.get_playbook_stats(task_type, module_name)

        if stats:
            return {
                "success": True,
                "task_type": task_type,
                "stats": stats
            }
        else:
            raise HTTPException(status_code=404, detail=f"Playbook not found: {task_type}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ace/playbooks")
async def get_all_playbooks():
    """Get statistics for all playbooks"""
    try:
        stats = await ace_service.get_all_playbooks_stats()

        return {
            "success": True,
            "count": len(stats),
            "playbooks": stats
        }

    except Exception as e:
        logger.error(f"Error fetching all playbooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ace/analytics")
async def get_analytics():
    """
    Get ACE analytics and insights

    Provides monitoring data for measuring improvements
    """
    try:
        all_stats = await ace_service.get_all_playbooks_stats()

        # Aggregate analytics
        analytics = {
            'total_playbooks': len(all_stats),
            'total_usage': sum(s.get('usage_count', 0) for s in all_stats),
            'avg_success_rate': sum(s.get('success_rate', 0) for s in all_stats) / len(all_stats) if all_stats else 0,
            'avg_effectiveness': sum(s.get('avg_effectiveness', 0) for s in all_stats) / len(all_stats) if all_stats else 0,
            'by_module': {},
            'by_task_type': {},
            'service_stats': ace_service.get_service_stats(),
            'timestamp': datetime.utcnow().isoformat()
        }

        # Group by module
        for stat in all_stats:
            module = stat.get('module_name', 'unknown')
            if module not in analytics['by_module']:
                analytics['by_module'][module] = {
                    'count': 0,
                    'avg_success_rate': 0,
                    'avg_effectiveness': 0
                }
            analytics['by_module'][module]['count'] += 1
            analytics['by_module'][module]['avg_success_rate'] += stat.get('success_rate', 0)
            analytics['by_module'][module]['avg_effectiveness'] += stat.get('avg_effectiveness', 0)

        # Average per module
        for module in analytics['by_module']:
            count = analytics['by_module'][module]['count']
            if count > 0:
                analytics['by_module'][module]['avg_success_rate'] /= count
                analytics['by_module'][module]['avg_effectiveness'] /= count

        return {
            "success": True,
            "analytics": analytics
        }

    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv('ACE_SERVICE_PORT', 8060))

    logger.info(f"Starting ACE Service on port {port}...")
    logger.info("Service provides:")
    logger.info("  - Generator: Enhanced context with evolving playbooks")
    logger.info("  - Reflector: Trajectory analysis and insights")
    logger.info("  - Curator: Incremental playbook updates")
    logger.info("  - Analytics: Performance monitoring")
    logger.info("Expected improvement: +8-15% across all modules")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
