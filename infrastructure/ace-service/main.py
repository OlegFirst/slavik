"""
ACE Service - Agentic Context Engineering
Centralized microservice for continuous learning across all platform modules

Version: 2.0.0
Port: 8050
Database: Supabase PostgreSQL
"""

import os
import asyncio
import asyncpg
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="ACE Service",
    description="Agentic Context Engineering - Continuous Learning Infrastructure",
    version="2.0.0"
)

# Database pool (will be initialized on startup)
db_pool = None


# ============================================================================
# Pydantic Models
# ============================================================================

class GenerateContextRequest(BaseModel):
    task_type: str
    base_context: Dict[str, Any]
    module_name: Optional[str] = None
    domain_knowledge: Optional[Dict[str, Any]] = None


class ReflectTrajectoryRequest(BaseModel):
    task_type: str
    trajectory: Dict[str, Any]
    module_name: Optional[str] = None


class CuratePlaybookRequest(BaseModel):
    task_type: str
    insights: Dict[str, Any]
    module_name: Optional[str] = None
    preserve_knowledge: bool = True


# ============================================================================
# ACE Service Core
# ============================================================================

class ACEService:
    """Core ACE Service implementation"""

    def __init__(self):
        self.db_pool = None

    async def initialize(self, database_url: str):
        """Initialize database connection pool"""
        try:
            self.db_pool = await asyncpg.create_pool(
                database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("✅ Database connection pool initialized")

            # Verify tables exist
            async with self.db_pool.acquire() as conn:
                tables = await conn.fetch("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_name LIKE 'ace_%'
                """)
                logger.info(f"✅ Found {len(tables)} ACE tables: {[t['table_name'] for t in tables]}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise

    async def close(self):
        """Close database connection pool"""
        if self.db_pool:
            await self.db_pool.close()
            logger.info("✅ Database connection pool closed")

    async def _get_latest_playbook(
        self,
        task_type: str,
        module_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get latest playbook for task type"""
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT playbook, id, version
                FROM ace_playbooks
                WHERE task_type = $1
                  AND ($2::text IS NULL OR module_name = $2)
                ORDER BY version DESC
                LIMIT 1
            """, task_type, module_name)

            if result:
                return {
                    'playbook': result['playbook'],
                    'playbook_id': str(result['id']),
                    'version': result['version']
                }
            else:
                # Return default empty playbook
                return {
                    'playbook': {
                        'strategies': [],
                        'patterns': [],
                        'domain_knowledge': [],
                        'successful_examples': [],
                        'failed_examples': []
                    },
                    'playbook_id': None,
                    'version': 0
                }

    async def generate_context(
        self,
        task_type: str,
        base_context: Dict[str, Any],
        module_name: Optional[str] = None,
        domain_knowledge: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        GENERATOR: Generate enhanced context from evolving playbook
        """
        logger.info(f"🎯 Generator: task_type={task_type}, module={module_name}")

        # Get latest playbook
        playbook_data = await self._get_latest_playbook(task_type, module_name)
        playbook = playbook_data['playbook']

        # Enhance context with playbook
        enhanced_context = {
            **base_context,
            'playbook_strategies': playbook.get('strategies', []),
            'known_patterns': playbook.get('patterns', []),
            'domain_expertise': playbook.get('domain_knowledge', []),
            'successful_examples': playbook.get('successful_examples', [])[:5],  # Top 5
            'playbook_version': playbook_data['version'],
            'playbook_id': playbook_data['playbook_id']
        }

        # Add custom domain knowledge if provided
        if domain_knowledge:
            enhanced_context['custom_domain_knowledge'] = domain_knowledge

        logger.info(f"✅ Context enhanced: {len(playbook.get('strategies', []))} strategies, "
                   f"{len(playbook.get('patterns', []))} patterns")

        return enhanced_context

    async def reflect_on_trajectory(
        self,
        task_type: str,
        trajectory: Dict[str, Any],
        module_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        REFLECTOR: Analyze execution trajectory and extract insights
        """
        logger.info(f"🔍 Reflector: task_type={task_type}, module={module_name}")

        # Extract key metrics
        success = trajectory.get('success', False)
        effectiveness = trajectory.get('effectiveness', 0.0)

        # Analyze trajectory
        insights = {
            'effectiveness_score': effectiveness,
            'success': success,
            'patterns_identified': [],
            'failure_reasons': [],
            'recommendations': []
        }

        # Identify patterns based on success
        if success and effectiveness > 0.8:
            insights['patterns_identified'].append({
                'type': 'high_effectiveness',
                'confidence': 0.9,
                'description': 'Task completed successfully with high effectiveness'
            })
            insights['recommendations'].append('Preserve current strategy')

        elif success and effectiveness > 0.6:
            insights['patterns_identified'].append({
                'type': 'moderate_effectiveness',
                'confidence': 0.7,
                'description': 'Task completed but with room for improvement'
            })
            insights['recommendations'].append('Analyze for optimization opportunities')

        else:
            insights['failure_reasons'].append('Low effectiveness or task failure')
            insights['recommendations'].append('Review approach and try alternative strategies')

        # Log trajectory to database
        playbook_id = trajectory.get('input_context', {}).get('playbook_id')
        if playbook_id:
            try:
                async with self.db_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO ace_trajectory_log (
                            playbook_id, task_type, input_context, output_result,
                            trajectory, insights, effectiveness, success
                        ) VALUES ($1, $2, $3::jsonb, $4::jsonb, $5::jsonb, $6::jsonb, $7, $8)
                    """,
                    playbook_id,
                    task_type,
                    json.dumps(trajectory.get('input_context', {})),
                    json.dumps(trajectory.get('output_result', {})),
                    json.dumps(trajectory),
                    json.dumps(insights),
                    effectiveness,
                    success
                    )
                logger.info("✅ Trajectory logged to database")
            except Exception as e:
                logger.warning(f"⚠️  Failed to log trajectory: {e}")

        return insights

    async def curate_playbook(
        self,
        task_type: str,
        insights: Dict[str, Any],
        module_name: Optional[str] = None,
        preserve_knowledge: bool = True
    ) -> Dict[str, Any]:
        """
        CURATOR: Update playbook incrementally (NO context collapse!)
        """
        logger.info(f"📚 Curator: task_type={task_type}, module={module_name}")

        # Get current playbook
        current = await self._get_latest_playbook(task_type, module_name)
        current_playbook = current['playbook']
        current_version = current['version']

        # Build updated playbook (PRESERVE existing knowledge)
        updated_playbook = {
            'strategies': current_playbook.get('strategies', []).copy(),
            'patterns': current_playbook.get('patterns', []).copy(),
            'domain_knowledge': current_playbook.get('domain_knowledge', []).copy(),
            'successful_examples': current_playbook.get('successful_examples', []).copy(),
            'failed_examples': current_playbook.get('failed_examples', []).copy()
        }

        # Add new patterns from insights
        for pattern in insights.get('patterns_identified', []):
            if pattern not in updated_playbook['patterns']:
                updated_playbook['patterns'].append(pattern)

        # Add recommendations as new strategies
        for rec in insights.get('recommendations', []):
            if rec not in updated_playbook['strategies']:
                updated_playbook['strategies'].append(rec)

        # Limit list sizes to prevent bloat
        updated_playbook['strategies'] = updated_playbook['strategies'][-20:]  # Keep last 20
        updated_playbook['patterns'] = updated_playbook['patterns'][-20:]
        updated_playbook['successful_examples'] = updated_playbook['successful_examples'][-10:]

        # Save new version to database
        new_version = current_version + 1

        async with self.db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO ace_playbooks (
                    task_type, module_name, playbook, version
                )
                VALUES ($1, $2, $3::jsonb, $4)
                RETURNING id
            """, task_type, module_name, json.dumps(updated_playbook), new_version)

            new_playbook_id = result['id']

            logger.info(f"✅ Playbook updated: v{current_version} → v{new_version}")

        return {
            **updated_playbook,
            'version': new_version,
            'playbook_id': str(new_playbook_id),
            'previous_version': current_version
        }

    async def get_analytics(
        self,
        module_name: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get analytics and statistics"""
        async with self.db_pool.acquire() as conn:
            # Total playbooks
            total_playbooks = await conn.fetchval("""
                SELECT COUNT(DISTINCT task_type) FROM ace_playbooks
                WHERE ($1::text IS NULL OR module_name = $1)
            """, module_name)

            # Active modules
            active_modules = await conn.fetch("""
                SELECT DISTINCT module_name FROM ace_playbooks
                WHERE module_name IS NOT NULL
            """)

            # Total trajectories
            total_trajectories = await conn.fetchval("""
                SELECT COUNT(*) FROM ace_trajectory_log
                WHERE ($1::text IS NULL OR task_type = $1)
            """, task_type)

            # Average effectiveness
            avg_effectiveness = await conn.fetchval("""
                SELECT AVG(effectiveness) FROM ace_trajectory_log
                WHERE ($1::text IS NULL OR task_type = $1)
            """, task_type) or 0.0

            # Success rate
            success_rate = await conn.fetchval("""
                SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END)
                FROM ace_trajectory_log
                WHERE ($1::text IS NULL OR task_type = $1)
            """, task_type) or 0.0

            # Top performers
            top_performers = await conn.fetch("""
                SELECT task_type, AVG(effectiveness) as avg_eff
                FROM ace_trajectory_log
                GROUP BY task_type
                ORDER BY avg_eff DESC
                LIMIT 5
            """)

            return {
                'total_playbooks': total_playbooks,
                'active_modules': [m['module_name'] for m in active_modules],
                'total_trajectories': total_trajectories,
                'avg_effectiveness': float(avg_effectiveness),
                'success_rate': float(success_rate),
                'top_performers': [
                    {'task_type': p['task_type'], 'effectiveness': float(p['avg_eff'])}
                    for p in top_performers
                ]
            }


# ============================================================================
# Global ACE Service instance
# ============================================================================

ace_service = ACEService()


# ============================================================================
# FastAPI Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize ACE Service on startup"""
    logger.info("🚀 Starting ACE Service...")

    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set!")
        raise RuntimeError("DATABASE_URL not configured")

    # Initialize ACE Service
    await ace_service.initialize(database_url)
    logger.info("✅ ACE Service started successfully on port 8050")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down ACE Service...")
    await ace_service.close()
    logger.info("✅ ACE Service stopped")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        async with ace_service.db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")

        return {
            "status": "healthy",
            "service": "ACE Service",
            "version": "2.0.0",
            "database": "connected"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    try:
        analytics = await ace_service.get_analytics()
        return {
            "service": "ACE Service",
            "version": "2.0.0",
            **analytics
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ace/generate-context")
async def api_generate_context(request: GenerateContextRequest):
    """Generate enhanced context (GENERATOR)"""
    try:
        result = await ace_service.generate_context(
            task_type=request.task_type,
            base_context=request.base_context,
            module_name=request.module_name,
            domain_knowledge=request.domain_knowledge
        )
        return {"enhanced_context": result}
    except Exception as e:
        logger.error(f"Error in generate_context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ace/reflect")
async def api_reflect_trajectory(request: ReflectTrajectoryRequest):
    """Analyze trajectory (REFLECTOR)"""
    try:
        result = await ace_service.reflect_on_trajectory(
            task_type=request.task_type,
            trajectory=request.trajectory,
            module_name=request.module_name
        )
        return {"insights": result}
    except Exception as e:
        logger.error(f"Error in reflect_trajectory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ace/curate")
async def api_curate_playbook(request: CuratePlaybookRequest):
    """Update playbook (CURATOR)"""
    try:
        result = await ace_service.curate_playbook(
            task_type=request.task_type,
            insights=request.insights,
            module_name=request.module_name,
            preserve_knowledge=request.preserve_knowledge
        )
        return {"updated_playbook": result}
    except Exception as e:
        logger.error(f"Error in curate_playbook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ace/analytics")
async def api_get_analytics(
    module_name: Optional[str] = None,
    task_type: Optional[str] = None
):
    """Get analytics and statistics"""
    try:
        result = await ace_service.get_analytics(
            module_name=module_name,
            task_type=task_type
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ace/playbooks")
async def api_list_playbooks(
    module_name: Optional[str] = None,
    task_type: Optional[str] = None
):
    """List all playbooks"""
    try:
        async with ace_service.db_pool.acquire() as conn:
            query = """
                SELECT
                    id, task_type, module_name, version,
                    usage_count, success_rate, avg_effectiveness,
                    created_at, updated_at, last_used_at
                FROM ace_playbooks
                WHERE ($1::text IS NULL OR module_name = $1)
                  AND ($2::text IS NULL OR task_type = $2)
                ORDER BY task_type, version DESC
            """
            results = await conn.fetch(query, module_name, task_type)

            return {
                "playbooks": [
                    {
                        "id": str(r['id']),
                        "task_type": r['task_type'],
                        "module_name": r['module_name'],
                        "version": r['version'],
                        "usage_count": r['usage_count'],
                        "success_rate": float(r['success_rate']) if r['success_rate'] else 0.0,
                        "avg_effectiveness": float(r['avg_effectiveness']) if r['avg_effectiveness'] else 0.0,
                        "created_at": r['created_at'].isoformat() if r['created_at'] else None,
                    }
                    for r in results
                ]
            }
    except Exception as e:
        logger.error(f"Error listing playbooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv('ACE_SERVICE_PORT', 8050))

    print("\n" + "="*60)
    print("🚀 ACE Service - Agentic Context Engineering")
    print("="*60)
    print(f"Port: {port}")
    print(f"Version: 2.0.0")
    print(f"Docs: http://localhost:{port}/docs")
    print("="*60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
