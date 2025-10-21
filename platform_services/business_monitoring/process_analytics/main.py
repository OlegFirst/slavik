"""
 Process Mining Service - Advanced Process Analytics
Analyzes real process execution logs to discover patterns,
bottlenecks, deviations, and optimization opportunities.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import (
    create_engine, Column, String, DateTime, Float, Integer,
    JSON, Text, Boolean, ForeignKey
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware
import time
import sys
from pathlib import Path
import asyncio

# Add infrastructure to path for EventBus
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# EventBus imports
try:
    from infrastructure.eventbus import create_eventbus, Event, EventPriority
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    logger.warning("️  EventBus not available - running without event integration")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================================
# PROMETHEUS METRICS
# ================================================

# Request metrics
process_analytics_requests_total = Counter(
    'process_analytics_requests_total',
    'Total number of requests to Process Analytics service',
    ['method', 'endpoint', 'status']
)

process_analytics_request_duration_seconds = Histogram(
    'process_analytics_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# Business metrics
process_analytics_patterns_discovered = Counter(
    'process_analytics_patterns_discovered',
    'Total number of patterns discovered',
    ['process_id', 'pattern_type']
)

process_analytics_deviations_detected = Counter(
    'process_analytics_deviations_detected',
    'Total number of deviations detected',
    ['process_id', 'deviation_type', 'severity']
)

process_analytics_active_analyses = Gauge(
    'process_analytics_active_analyses',
    'Number of currently running analyses'
)

process_analytics_executions_analyzed = Counter(
    'process_analytics_executions_analyzed',
    'Total number of process executions analyzed',
    ['process_id', 'status']
)

# Performance metrics
process_analytics_analysis_duration_seconds = Histogram(
    'process_analytics_analysis_duration_seconds',
    'Duration of process mining analysis',
    ['analysis_type']
)

# Database metrics
process_analytics_db_connections = Gauge(
    'process_analytics_db_connections',
    'Number of active database connections'
)


# ================================================
# PROMETHEUS MIDDLEWARE
# ================================================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track request metrics"""

    async def dispatch(self, request, call_next):
        # Skip metrics endpoint
        if request.url.path == "/metrics":
            return await call_next(request)

        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time

        process_analytics_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        process_analytics_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response

# Database setup - Use Supabase PostgreSQL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.tpdkhddtbhpoqzzgxfni:K%40x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"
)
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# EventBus instance (will be initialized in lifespan)
eventbus = None

# FastAPI app with lifespan
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management

    Startup:
    - Initialize EventBus connection
    - Publish service started event

    Shutdown:
    - Publish service stopped event
    - Disconnect EventBus
    """
    global eventbus

    logger.info(" Process Mining Service starting...")

    # Startup: Initialize EventBus
    if EVENTBUS_AVAILABLE:
        try:
            logger.info("Connecting to EventBus...")
            eventbus = create_eventbus('redis')
            await eventbus.connect()
            logger.info(" EventBus connected")

            # Publish service started event
            await eventbus.publish(Event.create(
                event_type='platform.service.started',
                source='process-analytics',
                data={
                    'service_name': 'process-analytics',
                    'port': int(os.getenv("PORT", "8780")),
                    'version': '1.0.0',
                    'capabilities': [
                        'process_performance_analysis',
                        'pattern_discovery',
                        'deviation_detection',
                        'process_mining'
                    ]
                }
            ))
            logger.info(" Published service started event")

        except Exception as e:
            logger.error(f"EventBus initialization failed: {e}")
            logger.warning("️  Running without EventBus integration")
            eventbus = None

    yield

    # Shutdown: Cleanup
    logger.info(" Process Mining Service shutting down...")

    if eventbus:
        try:
            # Publish service stopped event
            await eventbus.publish(Event.create(
                event_type='platform.service.stopped',
                source='process-analytics',
                data={
                    'service_name': 'process-analytics',
                    'timestamp': datetime.utcnow().isoformat(),
                    'reason': 'graceful_shutdown'
                }
            ))

            # Disconnect
            await eventbus.disconnect()
            logger.info(" EventBus disconnected")
        except Exception as e:
            logger.error(f"EventBus shutdown error: {e}")

    logger.info(" Shutdown complete")

app = FastAPI(
    title="Process Mining Service",
    description="Advanced process analytics and mining service for BCM platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# Database Models
class ProcessExecution(Base):
    __tablename__ = "process_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(String, nullable=False, index=True)
    execution_id = Column(String, nullable=False, unique=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String, nullable=False)  # running, completed, failed, cancelled
    duration_minutes = Column(Float)
    executed_by = Column(String)
    execution_metadata = Column(JSON)

    # Relationships
    events = relationship("ProcessEvent", back_populates="execution")

class ProcessEvent(Base):
    __tablename__ = "process_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("process_executions.id"), nullable=False)
    event_type = Column(String, nullable=False)  # start, end, checkpoint, error, decision
    step_name = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    duration_minutes = Column(Float)
    actor = Column(String)
    data = Column(JSON)

    # Relationships
    execution = relationship("ProcessExecution", back_populates="events")

class ProcessPattern(Base):
    __tablename__ = "discovered_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id = Column(String, nullable=False, index=True)
    pattern_type = Column(String, nullable=False)  # sequence, parallel, loop, skip
    pattern_name = Column(String, nullable=False)
    frequency = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    pattern_data = Column(JSON)
    discovered_at = Column(DateTime, default=datetime.utcnow)

class ProcessDeviation(Base):
    __tablename__ = "process_deviations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("process_executions.id"), nullable=False)
    deviation_type = Column(String, nullable=False)  # timing, sequence, resource, quality
    severity = Column(String, nullable=False)  # low, medium, high, critical
    description = Column(Text)
    expected_value = Column(String)
    actual_value = Column(String)
    impact_score = Column(Float)
    detected_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class ProcessEventCreate(BaseModel):
    execution_id: str
    event_type: str
    step_name: str
    timestamp: datetime
    duration_minutes: Optional[float] = None
    actor: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ProcessExecutionCreate(BaseModel):
    process_id: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    executed_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ProcessAnalysisResult(BaseModel):
    process_id: str
    analysis_type: str
    results: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    confidence_score: float

class ProcessMiningRequest(BaseModel):
    process_id: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_patterns: bool = True
    include_deviations: bool = True
    include_performance: bool = True

@dataclass
class ProcessTrace:
    """Represents a complete process execution trace"""
    execution_id: str
    process_id: str
    events: List[Dict[str, Any]]
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    status: str

class ProcessMiningEngine:
    """Advanced process mining and analytics engine"""

    def __init__(self, db: Session):
        self.db = db

    def analyze_process_performance(self, process_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Analyze process performance metrics"""
        # Track active analyses
        process_analytics_active_analyses.inc()
        start_time = time.time()

        try:
            # Get process executions
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)

            executions = self.db.query(ProcessExecution).filter(
                ProcessExecution.process_id == process_id,
                ProcessExecution.start_time >= start_date,
                ProcessExecution.end_time.isnot(None)
            ).all()

            if not executions:
                return {"error": "No completed executions found for analysis"}

            # Calculate performance metrics
            durations = [exec.duration_minutes for exec in executions if exec.duration_minutes]
            statuses = [exec.status for exec in executions]

            performance_metrics = {
                "total_executions": len(executions),
                "average_duration": statistics.mean(durations) if durations else 0,
                "median_duration": statistics.median(durations) if durations else 0,
                "min_duration": min(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0,
                "duration_std": statistics.stdev(durations) if len(durations) > 1 else 0,
                "success_rate": (statuses.count("completed") / len(statuses)) * 100,
                "failure_rate": (statuses.count("failed") / len(statuses)) * 100,
                "cancellation_rate": (statuses.count("cancelled") / len(statuses)) * 100,
                "status_distribution": dict(Counter(statuses))
            }

            # Analyze trends
            executions_by_day = defaultdict(list)
            for exec in executions:
                day = exec.start_time.date()
                executions_by_day[day].append(exec)

            daily_metrics = []
            for day, day_executions in sorted(executions_by_day.items()):
                day_durations = [e.duration_minutes for e in day_executions if e.duration_minutes]
                daily_metrics.append({
                    "date": day.isoformat(),
                    "executions": len(day_executions),
                    "avg_duration": statistics.mean(day_durations) if day_durations else 0,
                    "success_rate": (sum(1 for e in day_executions if e.status == "completed") / len(day_executions)) * 100
                })

            # Record metrics for analyzed executions
            for exec in executions:
                process_analytics_executions_analyzed.labels(
                    process_id=process_id,
                    status=exec.status
                ).inc()

            result = {
                "process_id": process_id,
                "analysis_period": {"from": start_date.isoformat(), "to": end_date.isoformat()},
                "performance_metrics": performance_metrics,
                "trends": daily_metrics,
                "insights": self._generate_performance_insights(performance_metrics, daily_metrics)
            }

            # Record analysis duration
            duration = time.time() - start_time
            process_analytics_analysis_duration_seconds.labels(
                analysis_type="performance"
            ).observe(duration)

            # Publish performance analyzed event
            if eventbus and EVENTBUS_AVAILABLE:
                try:
                    asyncio.create_task(eventbus.publish(Event.create(
                        event_type='process_analytics.performance_analyzed',
                        source='process-analytics',
                        data={
                            'process_id': process_id,
                            'analysis_period_days': days_back,
                            'total_executions': performance_metrics['total_executions'],
                            'success_rate': performance_metrics['success_rate'],
                            'avg_duration': performance_metrics['average_duration'],
                            'duration_seconds': duration,
                            'timestamp': datetime.utcnow().isoformat()
                        },
                        priority=EventPriority.LOW
                    )))
                except Exception as e:
                    logger.error(f"Failed to publish performance_analyzed event: {e}")

            return result

        except Exception as e:
            logger.error(f"Error analyzing process performance: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
        finally:
            process_analytics_active_analyses.dec()

    def discover_process_patterns(self, process_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Discover common patterns in process execution"""
        process_analytics_active_analyses.inc()
        start_time = time.time()

        try:
            # Get process traces
            traces = self._get_process_traces(process_id, days_back)

            if len(traces) < 3:
                return {"error": "Insufficient data for pattern discovery (minimum 3 traces required)"}

            patterns = {
                "sequence_patterns": self._discover_sequence_patterns(traces),
                "parallel_patterns": self._discover_parallel_patterns(traces),
                "loop_patterns": self._discover_loop_patterns(traces),
                "skip_patterns": self._discover_skip_patterns(traces),
                "timing_patterns": self._discover_timing_patterns(traces)
            }

            # Store discovered patterns and record metrics
            for pattern_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    self._store_pattern(process_id, pattern_type, pattern)
                    # Record pattern discovery metric
                    process_analytics_patterns_discovered.labels(
                        process_id=process_id,
                        pattern_type=pattern_type
                    ).inc()

                    # Publish pattern discovered event
                    if eventbus and EVENTBUS_AVAILABLE:
                        try:
                            asyncio.create_task(eventbus.publish(Event.create(
                                event_type='process_analytics.pattern_discovered',
                                source='process-analytics',
                                data={
                                    'process_id': process_id,
                                    'pattern_type': pattern_type,
                                    'pattern': pattern,
                                    'confidence': pattern.get('confidence', 0.0),
                                    'frequency': pattern.get('frequency', 0),
                                    'timestamp': datetime.utcnow().isoformat()
                                },
                                priority=EventPriority.NORMAL
                            )))
                        except Exception as e:
                            logger.error(f"Failed to publish pattern_discovered event: {e}")

            result = {
                "process_id": process_id,
                "total_traces_analyzed": len(traces),
                "patterns": patterns,
                "insights": self._generate_pattern_insights(patterns)
            }

            # Record analysis duration
            duration = time.time() - start_time
            process_analytics_analysis_duration_seconds.labels(
                analysis_type="pattern_discovery"
            ).observe(duration)

            return result

        except Exception as e:
            logger.error(f"Error discovering patterns: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Pattern discovery error: {str(e)}")
        finally:
            process_analytics_active_analyses.dec()

    def detect_process_deviations(self, process_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Detect deviations from normal process behavior"""
        process_analytics_active_analyses.inc()
        start_time = time.time()

        try:
            traces = self._get_process_traces(process_id, days_back)

            if len(traces) < 5:
                return {"error": "Insufficient data for deviation detection (minimum 5 traces required)"}

            deviations = {
                "timing_deviations": self._detect_timing_deviations(traces),
                "sequence_deviations": self._detect_sequence_deviations(traces),
                "resource_deviations": self._detect_resource_deviations(traces),
                "quality_deviations": self._detect_quality_deviations(traces)
            }

            # Store detected deviations and record metrics
            for deviation_type, deviation_list in deviations.items():
                for deviation in deviation_list:
                    self._store_deviation(deviation)
                    # Record deviation metric
                    process_analytics_deviations_detected.labels(
                        process_id=process_id,
                        deviation_type=deviation.get("deviation_type", "unknown"),
                        severity=deviation.get("severity", "low")
                    ).inc()

                    # Publish deviation detected event
                    if eventbus and EVENTBUS_AVAILABLE:
                        try:
                            # Determine priority based on severity
                            priority = EventPriority.NORMAL
                            if deviation.get("severity") == "critical":
                                priority = EventPriority.HIGH
                            elif deviation.get("severity") == "high":
                                priority = EventPriority.NORMAL

                            asyncio.create_task(eventbus.publish(Event.create(
                                event_type='process_analytics.deviation_detected',
                                source='process-analytics',
                                data={
                                    'process_id': process_id,
                                    'execution_id': deviation.get('execution_id'),
                                    'deviation_type': deviation.get('deviation_type', 'unknown'),
                                    'severity': deviation.get('severity', 'low'),
                                    'description': deviation.get('description', ''),
                                    'expected_value': deviation.get('expected_value'),
                                    'actual_value': deviation.get('actual_value'),
                                    'impact_score': deviation.get('deviation_score', 0.0),
                                    'timestamp': datetime.utcnow().isoformat()
                                },
                                priority=priority
                            )))
                        except Exception as e:
                            logger.error(f"Failed to publish deviation_detected event: {e}")

            # Calculate deviation statistics
            total_deviations = sum(len(dev_list) for dev_list in deviations.values())
            deviation_rate = (total_deviations / len(traces)) * 100

            result = {
                "process_id": process_id,
                "total_traces_analyzed": len(traces),
                "total_deviations": total_deviations,
                "deviation_rate": deviation_rate,
                "deviations": deviations,
                "severity_breakdown": self._calculate_severity_breakdown(deviations),
                "insights": self._generate_deviation_insights(deviations, deviation_rate)
            }

            # Record analysis duration
            duration = time.time() - start_time
            process_analytics_analysis_duration_seconds.labels(
                analysis_type="deviation_detection"
            ).observe(duration)

            return result

        except Exception as e:
            logger.error(f"Error detecting deviations: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Deviation detection error: {str(e)}")
        finally:
            process_analytics_active_analyses.dec()

    def _get_process_traces(self, process_id: str, days_back: int) -> List[ProcessTrace]:
        """Get process execution traces for analysis"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        executions = self.db.query(ProcessExecution).filter(
            ProcessExecution.process_id == process_id,
            ProcessExecution.start_time >= start_date
        ).all()

        traces = []
        for execution in executions:
            events = self.db.query(ProcessEvent).filter(
                ProcessEvent.execution_id == execution.id
            ).order_by(ProcessEvent.timestamp).all()

            event_data = []
            for event in events:
                event_data.append({
                    "event_type": event.event_type,
                    "step_name": event.step_name,
                    "timestamp": event.timestamp,
                    "duration_minutes": event.duration_minutes,
                    "actor": event.actor,
                    "data": event.data or {}
                })

            traces.append(ProcessTrace(
                execution_id=execution.execution_id,
                process_id=execution.process_id,
                events=event_data,
                start_time=execution.start_time,
                end_time=execution.end_time,
                duration=execution.duration_minutes,
                status=execution.status
            ))

        return traces

    def _discover_sequence_patterns(self, traces: List[ProcessTrace]) -> List[Dict[str, Any]]:
        """Discover common sequence patterns"""
        sequence_patterns = []

        # Extract step sequences
        sequences = []
        for trace in traces:
            if len(trace.events) >= 2:
                sequence = [event["step_name"] for event in trace.events]
                sequences.append(sequence)

        # Find common subsequences
        subsequence_counts = defaultdict(int)
        for sequence in sequences:
            for i in range(len(sequence)):
                for j in range(i + 2, min(i + 6, len(sequence) + 1)):  # Max length 5
                    subseq = tuple(sequence[i:j])
                    subsequence_counts[subseq] += 1

        # Filter frequent patterns
        min_frequency = max(2, len(traces) * 0.3)  # At least 30% of traces
        for subseq, count in subsequence_counts.items():
            if count >= min_frequency and len(subseq) >= 2:
                confidence = count / len(sequences)
                sequence_patterns.append({
                    "pattern": list(subseq),
                    "frequency": count,
                    "confidence": confidence,
                    "support": count / len(traces)
                })

        # Sort by confidence
        sequence_patterns.sort(key=lambda x: x["confidence"], reverse=True)
        return sequence_patterns[:10]  # Top 10 patterns

    def _discover_parallel_patterns(self, traces: List[ProcessTrace]) -> List[Dict[str, Any]]:
        """Discover parallel execution patterns"""
        parallel_patterns = []

        for trace in traces:
            # Group events by timestamp windows (same minute = parallel)
            time_windows = defaultdict(list)
            for event in trace.events:
                minute_key = event["timestamp"].replace(second=0, microsecond=0)
                time_windows[minute_key].append(event["step_name"])

            # Find parallel step combinations
            for timestamp, steps in time_windows.items():
                if len(steps) > 1:
                    parallel_combo = tuple(sorted(steps))
                    parallel_patterns.append({
                        "execution_id": trace.execution_id,
                        "timestamp": timestamp,
                        "parallel_steps": list(parallel_combo)
                    })

        # Count pattern frequencies
        pattern_counts = defaultdict(int)
        for pattern in parallel_patterns:
            pattern_counts[tuple(pattern["parallel_steps"])] += 1

        result_patterns = []
        for pattern, count in pattern_counts.items():
            if count >= 2:  # Appears in at least 2 traces
                result_patterns.append({
                    "pattern": list(pattern),
                    "frequency": count,
                    "confidence": count / len(traces)
                })

        return sorted(result_patterns, key=lambda x: x["confidence"], reverse=True)

    def _discover_loop_patterns(self, traces: List[ProcessTrace]) -> List[Dict[str, Any]]:
        """Discover loop patterns in process execution"""
        loop_patterns = []

        for trace in traces:
            step_sequence = [event["step_name"] for event in trace.events]

            # Detect repeated step patterns
            for i in range(len(step_sequence)):
                for j in range(i + 1, len(step_sequence)):
                    if step_sequence[i] == step_sequence[j]:
                        # Found a potential loop
                        loop_steps = step_sequence[i:j]
                        if len(loop_steps) > 1:  # Multi-step loop
                            loop_patterns.append({
                                "execution_id": trace.execution_id,
                                "loop_steps": loop_steps,
                                "start_index": i,
                                "end_index": j
                            })

        # Count loop pattern frequencies
        pattern_counts = defaultdict(int)
        for pattern in loop_patterns:
            pattern_counts[tuple(pattern["loop_steps"])] += 1

        result_patterns = []
        for pattern, count in pattern_counts.items():
            if count >= 2:
                result_patterns.append({
                    "pattern": list(pattern),
                    "frequency": count,
                    "avg_iterations": count / len(traces)
                })

        return result_patterns

    def _discover_skip_patterns(self, traces: List[ProcessTrace]) -> List[Dict[str, Any]]:
        """Discover step skip patterns"""
        # Get all unique steps across all traces
        all_steps = set()
        for trace in traces:
            all_steps.update(event["step_name"] for event in trace.events)

        skip_patterns = []
        for step in all_steps:
            executions_with_step = 0
            executions_without_step = 0

            for trace in traces:
                trace_steps = {event["step_name"] for event in trace.events}
                if step in trace_steps:
                    executions_with_step += 1
                else:
                    executions_without_step += 1

            if executions_without_step > 0:
                skip_rate = executions_without_step / len(traces)
                skip_patterns.append({
                    "step": step,
                    "skip_frequency": executions_without_step,
                    "skip_rate": skip_rate,
                    "execution_frequency": executions_with_step
                })

        # Sort by skip rate
        return sorted(skip_patterns, key=lambda x: x["skip_rate"], reverse=True)

    def _discover_timing_patterns(self, traces: List[ProcessTrace]) -> List[Dict[str, Any]]:
        """Discover timing patterns in process execution"""
        timing_patterns = []

        # Analyze step durations
        step_durations = defaultdict(list)
        for trace in traces:
            for event in trace.events:
                if event["duration_minutes"]:
                    step_durations[event["step_name"]].append(event["duration_minutes"])

        for step, durations in step_durations.items():
            if len(durations) >= 3:
                timing_patterns.append({
                    "step": step,
                    "avg_duration": statistics.mean(durations),
                    "median_duration": statistics.median(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "std_duration": statistics.stdev(durations) if len(durations) > 1 else 0,
                    "sample_size": len(durations)
                })

        return sorted(timing_patterns, key=lambda x: x["avg_duration"], reverse=True)

    def _detect_timing_deviations(self, traces: List[ProcessTrace]) -> List[Dict[str, Any]]:
        """Detect timing deviations from normal behavior"""
        timing_deviations = []

        # Calculate normal timing for each step
        step_timings = defaultdict(list)
        for trace in traces:
            for event in trace.events:
                if event["duration_minutes"]:
                    step_timings[event["step_name"]].append(event["duration_minutes"])

        # Calculate baseline statistics
        step_baselines = {}
        for step, durations in step_timings.items():
            if len(durations) >= 3:
                mean_duration = statistics.mean(durations)
                std_duration = statistics.stdev(durations) if len(durations) > 1 else 0
                step_baselines[step] = {
                    "mean": mean_duration,
                    "std": std_duration,
                    "threshold_high": mean_duration + 2 * std_duration,
                    "threshold_low": max(0, mean_duration - 2 * std_duration)
                }

        # Detect deviations
        for trace in traces:
            for event in trace.events:
                step = event["step_name"]
                if step in step_baselines and event["duration_minutes"]:
                    baseline = step_baselines[step]
                    duration = event["duration_minutes"]

                    severity = "low"
                    deviation_type = None

                    if duration > baseline["threshold_high"]:
                        deviation_type = "duration_too_high"
                        if duration > baseline["mean"] + 3 * baseline["std"]:
                            severity = "critical"
                        elif duration > baseline["mean"] + 2.5 * baseline["std"]:
                            severity = "high"
                        else:
                            severity = "medium"
                    elif duration < baseline["threshold_low"]:
                        deviation_type = "duration_too_low"
                        severity = "medium"

                    if deviation_type:
                        timing_deviations.append({
                            "execution_id": trace.execution_id,
                            "deviation_type": "timing",
                            "subtype": deviation_type,
                            "step": step,
                            "actual_duration": duration,
                            "expected_duration": baseline["mean"],
                            "severity": severity,
                            "deviation_score": abs(duration - baseline["mean"]) / baseline["std"] if baseline["std"] > 0 else 0
                        })

        return timing_deviations

    def _detect_sequence_deviations(self, traces: List[ProcessTrace]) -> List[Dict[str, Any]]:
        """Detect deviations from normal sequence patterns"""
        # Get most common sequence patterns
        sequences = []
        for trace in traces:
            sequence = [event["step_name"] for event in trace.events]
            sequences.append((trace.execution_id, sequence))

        # Find the most common sequence as baseline
        sequence_counts = defaultdict(int)
        for exec_id, sequence in sequences:
            sequence_counts[tuple(sequence)] += 1

        if not sequence_counts:
            return []

        # Get baseline sequence (most frequent)
        baseline_sequence = max(sequence_counts.items(), key=lambda x: x[1])[0]
        baseline_frequency = sequence_counts[baseline_sequence]

        # If baseline is less than 30% of traces, no strong baseline exists
        if baseline_frequency < len(traces) * 0.3:
            return []

        sequence_deviations = []
        for exec_id, sequence in sequences:
            if tuple(sequence) != baseline_sequence:
                # Calculate sequence similarity
                similarity = self._calculate_sequence_similarity(list(baseline_sequence), sequence)

                deviation_severity = "low"
                if similarity < 0.3:
                    deviation_severity = "high"
                elif similarity < 0.6:
                    deviation_severity = "medium"

                sequence_deviations.append({
                    "execution_id": exec_id,
                    "deviation_type": "sequence",
                    "actual_sequence": sequence,
                    "expected_sequence": list(baseline_sequence),
                    "similarity_score": similarity,
                    "severity": deviation_severity
                })

        return sequence_deviations

    def _detect_resource_deviations(self, traces: List[ProcessTrace]) -> List[Dict[str, Any]]:
        """Detect resource allocation deviations"""
        resource_deviations = []

        # Analyze actor patterns for each step
        step_actors = defaultdict(lambda: defaultdict(int))
        for trace in traces:
            for event in trace.events:
                if event["actor"]:
                    step_actors[event["step_name"]][event["actor"]] += 1

        # Find most common actor for each step
        step_primary_actors = {}
        for step, actor_counts in step_actors.items():
            if actor_counts:
                primary_actor = max(actor_counts.items(), key=lambda x: x[1])
                step_primary_actors[step] = {
                    "actor": primary_actor[0],
                    "frequency": primary_actor[1],
                    "total": sum(actor_counts.values())
                }

        # Detect deviations
        for trace in traces:
            for event in trace.events:
                step = event["step_name"]
                if step in step_primary_actors and event["actor"]:
                    primary = step_primary_actors[step]
                    if event["actor"] != primary["actor"]:
                        # Resource deviation detected
                        frequency_ratio = primary["frequency"] / primary["total"]
                        severity = "high" if frequency_ratio > 0.8 else "medium"

                        resource_deviations.append({
                            "execution_id": trace.execution_id,
                            "deviation_type": "resource",
                            "step": step,
                            "actual_actor": event["actor"],
                            "expected_actor": primary["actor"],
                            "severity": severity,
                            "primary_actor_frequency": frequency_ratio
                        })

        return resource_deviations

    def _detect_quality_deviations(self, traces: List[ProcessTrace]) -> List[Dict[str, Any]]:
        """Detect quality-related deviations"""
        quality_deviations = []

        for trace in traces:
            # Check for failed executions
            if trace.status == "failed":
                quality_deviations.append({
                    "execution_id": trace.execution_id,
                    "deviation_type": "quality",
                    "subtype": "execution_failure",
                    "severity": "high",
                    "description": "Process execution failed"
                })

            # Check for cancellations
            elif trace.status == "cancelled":
                quality_deviations.append({
                    "execution_id": trace.execution_id,
                    "deviation_type": "quality",
                    "subtype": "execution_cancelled",
                    "severity": "medium",
                    "description": "Process execution was cancelled"
                })

            # Check for error events
            error_events = [e for e in trace.events if e["event_type"] == "error"]
            for error_event in error_events:
                quality_deviations.append({
                    "execution_id": trace.execution_id,
                    "deviation_type": "quality",
                    "subtype": "step_error",
                    "step": error_event["step_name"],
                    "severity": "high",
                    "description": f"Error in step: {error_event['step_name']}"
                })

        return quality_deviations

    def _calculate_sequence_similarity(self, seq1: List[str], seq2: List[str]) -> float:
        """Calculate similarity between two sequences using Levenshtein distance"""
        if not seq1 or not seq2:
            return 0.0

        # Simple implementation of normalized Levenshtein distance
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])

        max_len = max(m, n)
        similarity = 1 - (dp[m][n] / max_len) if max_len > 0 else 0
        return max(0, similarity)

    def _store_pattern(self, process_id: str, pattern_type: str, pattern: Dict[str, Any]):
        """Store discovered pattern in database"""
        try:
            db_pattern = ProcessPattern(
                process_id=process_id,
                pattern_type=pattern_type,
                pattern_name=f"{pattern_type}_{pattern.get('pattern', 'unknown')}",
                frequency=pattern.get("frequency", 0),
                confidence=pattern.get("confidence", 0.0),
                pattern_data=pattern
            )
            self.db.add(db_pattern)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error storing pattern: {str(e)}")
            self.db.rollback()

    def _store_deviation(self, deviation: Dict[str, Any]):
        """Store detected deviation in database"""
        try:
            db_deviation = ProcessDeviation(
                execution_id=deviation.get("execution_id"),
                deviation_type=deviation.get("deviation_type"),
                severity=deviation.get("severity", "low"),
                description=deviation.get("description", ""),
                expected_value=str(deviation.get("expected_value", "")),
                actual_value=str(deviation.get("actual_value", "")),
                impact_score=deviation.get("deviation_score", 0.0)
            )
            self.db.add(db_deviation)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error storing deviation: {str(e)}")
            self.db.rollback()

    def _calculate_severity_breakdown(self, deviations: Dict[str, List]) -> Dict[str, int]:
        """Calculate breakdown of deviations by severity"""
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        for deviation_type, deviation_list in deviations.items():
            for deviation in deviation_list:
                severity = deviation.get("severity", "low")
                severity_counts[severity] += 1

        return severity_counts

    def _generate_performance_insights(self, metrics: Dict[str, Any], trends: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from performance analysis"""
        insights = []

        # Success rate insights
        if metrics["success_rate"] < 90:
            insights.append(f"️ Success rate is {metrics['success_rate']:.1f}% - below optimal threshold of 90%")
        elif metrics["success_rate"] > 95:
            insights.append(f" Excellent success rate of {metrics['success_rate']:.1f}%")

        # Duration insights
        if metrics["duration_std"] > metrics["average_duration"] * 0.5:
            insights.append(" High duration variability detected - process timing is inconsistent")

        # Trend insights
        if len(trends) >= 7:
            recent_success = statistics.mean([t["success_rate"] for t in trends[-3:]])
            early_success = statistics.mean([t["success_rate"] for t in trends[:3]])

            if recent_success < early_success - 5:
                insights.append(" Success rate declining in recent executions")
            elif recent_success > early_success + 5:
                insights.append(" Success rate improving in recent executions")

        return insights

    def _generate_pattern_insights(self, patterns: Dict[str, List]) -> List[str]:
        """Generate insights from pattern discovery"""
        insights = []

        # Sequence patterns
        if patterns["sequence_patterns"]:
            top_pattern = patterns["sequence_patterns"][0]
            insights.append(f" Most common sequence pattern: {' → '.join(top_pattern['pattern'])} ({top_pattern['confidence']:.1%} of cases)")

        # Parallel patterns
        if patterns["parallel_patterns"]:
            insights.append(f" {len(patterns['parallel_patterns'])} parallel execution patterns discovered")

        # Loop patterns
        if patterns["loop_patterns"]:
            insights.append(f" {len(patterns['loop_patterns'])} loop patterns detected - potential optimization opportunities")

        # Skip patterns
        high_skip_patterns = [p for p in patterns["skip_patterns"] if p["skip_rate"] > 0.3]
        if high_skip_patterns:
            insights.append(f"⏭️ {len(high_skip_patterns)} steps frequently skipped - consider making them optional")

        return insights

    def _generate_deviation_insights(self, deviations: Dict[str, List], deviation_rate: float) -> List[str]:
        """Generate insights from deviation analysis"""
        insights = []

        if deviation_rate > 30:
            insights.append(f" High deviation rate ({deviation_rate:.1f}%) - process standardization needed")
        elif deviation_rate < 10:
            insights.append(f" Low deviation rate ({deviation_rate:.1f}%) - process is well-standardized")

        # Timing deviations
        timing_devs = deviations["timing_deviations"]
        if timing_devs:
            high_timing = [d for d in timing_devs if d["severity"] in ["high", "critical"]]
            if high_timing:
                insights.append(f"⏱️ {len(high_timing)} critical timing deviations require attention")

        # Sequence deviations
        seq_devs = deviations["sequence_deviations"]
        if seq_devs:
            insights.append(f" {len(seq_devs)} sequence deviations - process flow inconsistencies detected")

        # Quality deviations
        quality_devs = deviations["quality_deviations"]
        if quality_devs:
            failures = [d for d in quality_devs if d["subtype"] == "execution_failure"]
            if failures:
                insights.append(f" {len(failures)} execution failures require root cause analysis")

        return insights

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints
@app.post("/api/v1/process-mining/log-execution")
async def log_process_execution(
    execution: ProcessExecutionCreate,
    db: Session = next(get_db())
):
    """Log a new process execution"""
    try:
        # Calculate duration if end_time is provided
        duration = None
        if execution.end_time:
            duration = (execution.end_time - execution.start_time).total_seconds() / 60

        db_execution = ProcessExecution(
            process_id=execution.process_id,
            execution_id=execution.execution_id,
            start_time=execution.start_time,
            end_time=execution.end_time,
            status=execution.status,
            duration_minutes=duration,
            executed_by=execution.executed_by,
            metadata=execution.metadata
        )

        db.add(db_execution)
        db.commit()
        db.refresh(db_execution)

        return {"message": "Process execution logged successfully", "id": str(db_execution.id)}

    except Exception as e:
        logger.error(f"Error logging execution: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log execution: {str(e)}")

@app.post("/api/v1/process-mining/log-event")
async def log_process_event(
    event: ProcessEventCreate,
    db: Session = next(get_db())
):
    """Log a process event"""
    try:
        # Find the execution
        execution = db.query(ProcessExecution).filter(
            ProcessExecution.execution_id == event.execution_id
        ).first()

        if not execution:
            raise HTTPException(status_code=404, detail="Process execution not found")

        db_event = ProcessEvent(
            execution_id=execution.id,
            event_type=event.event_type,
            step_name=event.step_name,
            timestamp=event.timestamp,
            duration_minutes=event.duration_minutes,
            actor=event.actor,
            data=event.data
        )

        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        return {"message": "Process event logged successfully", "id": str(db_event.id)}

    except Exception as e:
        logger.error(f"Error logging event: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log event: {str(e)}")

@app.post("/api/v1/process-mining/analyze-performance/{process_id}")
async def analyze_performance(
    process_id: str,
    days_back: int = 30,
    db: Session = next(get_db())
):
    """Analyze process performance metrics"""
    engine = ProcessMiningEngine(db)
    result = engine.analyze_process_performance(process_id, days_back)
    return result

@app.post("/api/v1/process-mining/discover-patterns/{process_id}")
async def discover_patterns(
    process_id: str,
    days_back: int = 30,
    db: Session = next(get_db())
):
    """Discover process execution patterns"""
    engine = ProcessMiningEngine(db)
    result = engine.discover_process_patterns(process_id, days_back)
    return result

@app.post("/api/v1/process-mining/detect-deviations/{process_id}")
async def detect_deviations(
    process_id: str,
    days_back: int = 30,
    db: Session = next(get_db())
):
    """Detect process execution deviations"""
    engine = ProcessMiningEngine(db)
    result = engine.detect_process_deviations(process_id, days_back)
    return result

@app.post("/api/v1/process-mining/comprehensive-analysis")
async def comprehensive_analysis(
    request: ProcessMiningRequest,
    db: Session = next(get_db())
):
    """Perform comprehensive process mining analysis"""
    engine = ProcessMiningEngine(db)

    # Calculate days back from date range
    days_back = 30
    if request.date_from:
        days_back = (datetime.utcnow() - request.date_from).days

    results = {
        "process_id": request.process_id,
        "analysis_date": datetime.utcnow().isoformat(),
        "analysis_scope": {
            "days_back": days_back,
            "date_from": request.date_from.isoformat() if request.date_from else None,
            "date_to": request.date_to.isoformat() if request.date_to else None
        }
    }

    try:
        if request.include_performance:
            results["performance_analysis"] = engine.analyze_process_performance(request.process_id, days_back)

        if request.include_patterns:
            results["pattern_discovery"] = engine.discover_process_patterns(request.process_id, days_back)

        if request.include_deviations:
            results["deviation_detection"] = engine.detect_process_deviations(request.process_id, days_back)

        # Generate overall insights
        overall_insights = []
        if "performance_analysis" in results:
            overall_insights.extend(results["performance_analysis"].get("insights", []))
        if "pattern_discovery" in results:
            overall_insights.extend(results["pattern_discovery"].get("insights", []))
        if "deviation_detection" in results:
            overall_insights.extend(results["deviation_detection"].get("insights", []))

        results["overall_insights"] = overall_insights
        results["analysis_summary"] = {
            "total_insights": len(overall_insights),
            "performance_included": request.include_performance,
            "patterns_included": request.include_patterns,
            "deviations_included": request.include_deviations
        }

        return results

    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint

    Exposes metrics for:
    - Request counts and durations
    - Pattern discovery metrics
    - Deviation detection metrics
    - Analysis performance
    """
    from starlette.responses import Response
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/api/v1/process-mining/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Process Mining Service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics_enabled": True,
        "metrics_endpoint": "/metrics",
        "eventbus_connected": eventbus is not None,
        "events_published": [
            "process_analytics.pattern_discovered",
            "process_analytics.deviation_detected",
            "process_analytics.performance_analyzed"
        ] if eventbus else []
    }

@app.get("/api/v1/process-mining/processes/{process_id}/summary")
async def get_process_summary(
    process_id: str,
    db: Session = next(get_db())
):
    """Get summary statistics for a process"""
    try:
        # Get basic execution statistics
        total_executions = db.query(ProcessExecution).filter(
            ProcessExecution.process_id == process_id
        ).count()

        completed_executions = db.query(ProcessExecution).filter(
            ProcessExecution.process_id == process_id,
            ProcessExecution.status == "completed"
        ).count()

        failed_executions = db.query(ProcessExecution).filter(
            ProcessExecution.process_id == process_id,
            ProcessExecution.status == "failed"
        ).count()

        # Get recent execution trends (last 7 days)
        recent_date = datetime.utcnow() - timedelta(days=7)
        recent_executions = db.query(ProcessExecution).filter(
            ProcessExecution.process_id == process_id,
            ProcessExecution.start_time >= recent_date
        ).count()

        # Get discovered patterns count
        patterns_count = db.query(ProcessPattern).filter(
            ProcessPattern.process_id == process_id
        ).count()

        # Get deviations count
        deviations_count = db.query(ProcessDeviation).join(ProcessExecution).filter(
            ProcessExecution.process_id == process_id
        ).count()

        return {
            "process_id": process_id,
            "statistics": {
                "total_executions": total_executions,
                "completed_executions": completed_executions,
                "failed_executions": failed_executions,
                "success_rate": (completed_executions / total_executions * 100) if total_executions > 0 else 0,
                "recent_executions_7d": recent_executions,
                "discovered_patterns": patterns_count,
                "detected_deviations": deviations_count
            },
            "last_updated": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting process summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.getenv("PORT", "8780"))
    logger.info(f"Starting Process Mining Service on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)