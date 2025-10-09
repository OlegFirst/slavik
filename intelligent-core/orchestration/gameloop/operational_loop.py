"""
Game Loop - Fast operational response layer

Принцип:
- Быстрее полного цикла обучения
- Использует закэшированные паттерны
- Ориентируется на текущие ресурсы
- 10-100 раз в секунду

Примеры:
- CPU spike → throttle немедленно
- Memory leak → restart немедленно
- Latency > 500ms → cache немедленно
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time

if TYPE_CHECKING:
    from ai_foundation.memory.memory_system import MemorySystem

logger = logging.getLogger(__name__)


class ActionSpeed(Enum):
    INSTANT = "instant"      # < 10ms
    FAST = "fast"            # < 100ms
    NORMAL = "normal"        # < 1s
    SLOW = "slow"            # > 1s


@dataclass
class SystemState:
    """Snapshot of system state"""
    cpu_percent: float
    memory_percent: float
    response_time_ms: float
    error_rate: float
    active_requests: int
    timestamp: float = field(default_factory=time.time)


@dataclass
class CachedPattern:
    """Cached state-action pattern"""
    pattern_id: str
    state_signature: str
    action_type: str
    action_fn: Callable
    success_rate: float
    last_used: float
    use_count: int = 0


class GameLoop:
    """
    Fast operational response loop

    Главный цикл быстрой реакции на изменения состояния.
    """

    def __init__(
        self,
        loop_interval: float = 0.1,
        enable_fast_path: bool = True,
        memory_system: Optional['MemorySystem'] = None
    ):
        """
        Args:
            loop_interval: Interval in seconds (0.01 = 100Hz, 0.1 = 10Hz)
            enable_fast_path: Enable fast path optimization
            memory_system: MemorySystem instance for pattern storage
        """
        self.loop_interval = loop_interval
        self.enable_fast_path = enable_fast_path
        self.memory_system = memory_system

        self.pattern_cache: Dict[str, CachedPattern] = {}
        self.action_registry: Dict[str, Callable] = {}
        self.is_running = False

        self.stats = {
            'total_iterations': 0,
            'fast_path_hits': 0,
            'slow_path_delegations': 0,
            'actions_executed': 0,
            'average_loop_time_ms': 0.0,
            'memory_syncs': 0
        }

        logger.info(f"GameLoop initialized (interval: {loop_interval}s, memory: {memory_system is not None})")

    def cache_pattern(
        self,
        state_signature: str,
        action_type: str,
        action_fn: Callable,
        success_rate: float = 1.0
    ):
        """Cache state-action pattern for fast path"""
        pattern_id = f"{state_signature}:{action_type}"

        pattern = CachedPattern(
            pattern_id=pattern_id,
            state_signature=state_signature,
            action_type=action_type,
            action_fn=action_fn,
            success_rate=success_rate,
            last_used=time.time()
        )

        self.pattern_cache[pattern_id] = pattern
        logger.debug(f"Cached pattern: {pattern_id}")

    def register_action(self, action_type: str, action_fn: Callable):
        """Register action function"""
        self.action_registry[action_type] = action_fn
        logger.debug(f"Registered action: {action_type}")

    def match_pattern(self, state: SystemState) -> Optional[CachedPattern]:
        """Match current state to cached pattern"""
        state_sig = self._generate_state_signature(state)

        # First check local cache
        for pattern in self.pattern_cache.values():
            if self._is_pattern_match(state_sig, pattern.state_signature):
                pattern.use_count += 1
                pattern.last_used = time.time()
                return pattern

        # If memory system available, check long-term memory
        if self.memory_system:
            patterns = self.memory_system.find_matching_patterns(
                state_sig,
                min_success_rate=0.75
            )

            if patterns:
                # Convert first match to CachedPattern
                mem_pattern = patterns[0]
                action_fn = self.action_registry.get(mem_pattern.action_type)

                if action_fn:
                    cached = CachedPattern(
                        pattern_id=mem_pattern.pattern_id,
                        state_signature=mem_pattern.state_signature,
                        action_type=mem_pattern.action_type,
                        action_fn=action_fn,
                        success_rate=mem_pattern.success_rate,
                        last_used=time.time(),
                        use_count=0
                    )
                    # Add to local cache
                    self.pattern_cache[cached.pattern_id] = cached
                    logger.debug(f"Loaded pattern from memory: {mem_pattern.pattern_id}")
                    return cached

        return None

    def _generate_state_signature(self, state: SystemState) -> str:
        """Generate state signature for pattern matching"""
        # Bucket values into ranges for fuzzy matching
        cpu_bucket = int(state.cpu_percent / 10) * 10
        mem_bucket = int(state.memory_percent / 10) * 10
        latency_bucket = int(state.response_time_ms / 100) * 100

        return f"cpu_{cpu_bucket}_mem_{mem_bucket}_latency_{latency_bucket}"

    def _is_pattern_match(self, sig1: str, sig2: str) -> bool:
        """Check if two state signatures match"""
        return sig1 == sig2

    async def get_current_state_fast(self) -> SystemState:
        """
        Fast snapshot of current state

        В production: реальные метрики
        Сейчас: тестовые данные
        """
        # TODO: Integration with real monitoring
        import random

        return SystemState(
            cpu_percent=random.uniform(40, 90),
            memory_percent=random.uniform(50, 85),
            response_time_ms=random.uniform(100, 400),
            error_rate=random.uniform(0, 0.05),
            active_requests=random.randint(10, 100)
        )

    async def execute_fast_action(self, pattern: CachedPattern, state: SystemState):
        """Execute cached fast action"""
        success = False
        try:
            await pattern.action_fn()
            self.stats['actions_executed'] += 1
            success = True
            logger.debug(f"Executed fast action: {pattern.action_type}")
        except Exception as e:
            logger.error(f"Fast action failed: {e}")

        # Record result in memory
        if self.memory_system:
            state_sig = self._generate_state_signature(state)
            self.memory_system.remember_pattern(
                state_signature=state_sig,
                action_type=pattern.action_type,
                success=success,
                context={
                    'cpu': state.cpu_percent,
                    'memory': state.memory_percent,
                    'response_time': state.response_time_ms
                }
            )
            self.stats['memory_syncs'] += 1

    async def delegate_to_slow_path(self, state: SystemState):
        """Delegate to slow path (full analysis)"""
        self.stats['slow_path_delegations'] += 1
        logger.debug("Delegating to slow path")

        # TODO: Integration with full analysis pipeline
        # await full_analysis.analyze(state)

    async def run_game_loop(self):
        """Main game loop"""
        self.is_running = True
        logger.info(f"GameLoop started (Hz: {1/self.loop_interval:.1f})")

        loop_times = []

        while self.is_running:
            loop_start = time.time()

            try:
                self.stats['total_iterations'] += 1

                # Fast snapshot
                state = await self.get_current_state_fast()

                # Check cached patterns (fast path)
                if self.enable_fast_path:
                    pattern = self.match_pattern(state)

                    if pattern:
                        # Fast path HIT
                        self.stats['fast_path_hits'] += 1
                        await self.execute_fast_action(pattern, state)
                    else:
                        # No pattern - delegate to slow path
                        await self.delegate_to_slow_path(state)
                else:
                    # Fast path disabled - always delegate
                    await self.delegate_to_slow_path(state)

                # Track loop time
                loop_time = (time.time() - loop_start) * 1000  # ms
                loop_times.append(loop_time)

                if len(loop_times) > 100:
                    loop_times.pop(0)

                self.stats['average_loop_time_ms'] = sum(loop_times) / len(loop_times)

                # Wait for next iteration
                await asyncio.sleep(self.loop_interval)

            except Exception as e:
                logger.error(f"GameLoop error: {e}")
                await asyncio.sleep(self.loop_interval * 2)

    def stop(self):
        """Stop game loop"""
        self.is_running = False
        logger.info("GameLoop stopped")

    def get_stats(self) -> Dict[str, Any]:
        """Get game loop statistics"""
        hit_rate = 0.0
        if self.stats['total_iterations'] > 0:
            hit_rate = self.stats['fast_path_hits'] / self.stats['total_iterations']

        return {
            **self.stats,
            'fast_path_hit_rate': hit_rate,
            'cached_patterns': len(self.pattern_cache),
            'is_running': self.is_running,
            'loop_hz': 1 / self.loop_interval if self.loop_interval > 0 else 0
        }


# Predefined fast actions

async def action_throttle_requests():
    """Throttle incoming requests"""
    logger.info("Action: Throttling requests")
    # TODO: Actual throttling implementation

async def action_clear_cache():
    """Clear cache to free memory"""
    logger.info("Action: Clearing cache")
    # TODO: Actual cache clearing

async def action_scale_up():
    """Scale up resources"""
    logger.info("Action: Scaling up")
    # TODO: Actual scaling

async def action_enable_circuit_breaker():
    """Enable circuit breaker"""
    logger.info("Action: Circuit breaker enabled")
    # TODO: Actual circuit breaker


def create_default_patterns() -> Dict[str, CachedPattern]:
    """Create default pattern cache"""
    patterns = {}

    # High CPU pattern
    patterns['high_cpu'] = CachedPattern(
        pattern_id='high_cpu',
        state_signature='cpu_80_',
        action_type='throttle',
        action_fn=action_throttle_requests,
        success_rate=0.9,
        last_used=time.time()
    )

    # High memory pattern
    patterns['high_memory'] = CachedPattern(
        pattern_id='high_memory',
        state_signature='mem_80_',
        action_type='clear_cache',
        action_fn=action_clear_cache,
        success_rate=0.85,
        last_used=time.time()
    )

    # High latency pattern
    patterns['high_latency'] = CachedPattern(
        pattern_id='high_latency',
        state_signature='latency_400_',
        action_type='scale_up',
        action_fn=action_scale_up,
        success_rate=0.95,
        last_used=time.time()
    )

    # High error rate pattern
    patterns['high_errors'] = CachedPattern(
        pattern_id='high_errors',
        state_signature='errors_high',
        action_type='circuit_breaker',
        action_fn=action_enable_circuit_breaker,
        success_rate=0.92,
        last_used=time.time()
    )

    return patterns


async def start_game_loop(
    loop_interval: float = 0.1,
    enable_fast_path: bool = True,
    load_default_patterns: bool = True,
    memory_system: Optional['MemorySystem'] = None
) -> GameLoop:
    """
    Start game loop

    Args:
        loop_interval: Loop interval in seconds
        enable_fast_path: Enable fast path optimization
        load_default_patterns: Load default pattern cache
        memory_system: MemorySystem instance for pattern storage

    Returns:
        Started GameLoop instance
    """
    game_loop = GameLoop(loop_interval, enable_fast_path, memory_system)

    # Register default actions
    game_loop.register_action('throttle', action_throttle_requests)
    game_loop.register_action('clear_cache', action_clear_cache)
    game_loop.register_action('scale_up', action_scale_up)
    game_loop.register_action('circuit_breaker', action_enable_circuit_breaker)

    if load_default_patterns:
        default_patterns = create_default_patterns()
        game_loop.pattern_cache.update(default_patterns)
        logger.info(f"Loaded {len(default_patterns)} default patterns")

    # Start in background
    asyncio.create_task(game_loop.run_game_loop())

    return game_loop
