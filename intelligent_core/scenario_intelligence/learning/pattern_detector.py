"""
Pattern Detector
Находит паттерны в выполнении сценариев для обучения системы
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)


class PatternDetector:
    """
    Детектор паттернов в сценариях

    Анализирует статистику выполнений и находит:
    - Частые сбои (failure patterns)
    - Временные паттерны (time-based patterns)
    - Зависимости между сценариями (dependency patterns)
    - Успешные комбинации (success patterns)
    - Аномалии (anomaly patterns)
    """

    def __init__(self):
        self.detected_patterns: List[Dict[str, Any]] = []
        self.failure_threshold = 0.3  # 30% failure rate = pattern
        self.min_executions = 5  # Минимум выполнений для паттерна

    async def detect_patterns(
        self,
        execution_history: List[Dict[str, Any]],
        scenarios: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect all patterns from execution history

        Args:
            execution_history: List of execution results
            scenarios: List of scenario definitions

        Returns:
            List of detected patterns
        """
        try:
            logger.info(f"Detecting patterns from {len(execution_history)} executions")

            patterns = []

            # 1. Failure patterns
            failure_patterns = self._detect_failure_patterns(execution_history)
            patterns.extend(failure_patterns)

            # 2. Time-based patterns
            time_patterns = self._detect_time_patterns(execution_history)
            patterns.extend(time_patterns)

            # 3. Dependency patterns
            dependency_patterns = self._detect_dependency_patterns(execution_history)
            patterns.extend(dependency_patterns)

            # 4. Success patterns
            success_patterns = self._detect_success_patterns(execution_history)
            patterns.extend(success_patterns)

            # 5. Anomaly patterns
            anomaly_patterns = self._detect_anomalies(execution_history)
            patterns.extend(anomaly_patterns)

            # 6. Sequence patterns
            sequence_patterns = self._detect_sequence_patterns(execution_history)
            patterns.extend(sequence_patterns)

            self.detected_patterns = patterns
            logger.info(f"✅ Detected {len(patterns)} patterns")

            return patterns

        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return []

    def _detect_failure_patterns(
        self,
        execution_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect failure patterns

        Находит сценарии с высоким процентом сбоев
        """
        patterns = []

        # Group by scenario_id
        scenario_stats = defaultdict(lambda: {"total": 0, "failed": 0, "errors": []})

        for execution in execution_history:
            scenario_id = execution.get("scenario_id")
            status = execution.get("status")

            scenario_stats[scenario_id]["total"] += 1

            if status in ["failed", "error"]:
                scenario_stats[scenario_id]["failed"] += 1
                error = execution.get("error", "Unknown error")
                scenario_stats[scenario_id]["errors"].append(error)

        # Analyze each scenario
        for scenario_id, stats in scenario_stats.items():
            if stats["total"] < self.min_executions:
                continue

            failure_rate = stats["failed"] / stats["total"]

            if failure_rate >= self.failure_threshold:
                # High failure rate pattern detected
                # Find most common error
                error_counts = Counter(stats["errors"])
                most_common_error = error_counts.most_common(1)[0] if error_counts else ("Unknown", 0)

                pattern = {
                    "type": "failure_pattern",
                    "scenario_id": scenario_id,
                    "failure_rate": failure_rate,
                    "total_executions": stats["total"],
                    "failed_executions": stats["failed"],
                    "most_common_error": most_common_error[0],
                    "error_frequency": most_common_error[1],
                    "confidence": min(failure_rate * (stats["total"] / 10), 1.0),  # More executions = higher confidence
                    "detected_at": datetime.now().isoformat(),
                    "severity": "high" if failure_rate > 0.7 else "medium",
                    "recommendation": f"Investigate scenario {scenario_id} - {failure_rate*100:.1f}% failure rate"
                }

                patterns.append(pattern)

        return patterns

    def _detect_time_patterns(
        self,
        execution_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect time-based patterns

        Находит паттерны по времени выполнения (утро/вечер, будни/выходные)
        """
        patterns = []

        # Group by hour of day
        hourly_stats = defaultdict(lambda: {"total": 0, "failed": 0})

        for execution in execution_history:
            try:
                started_at = execution.get("started_at")
                if not started_at:
                    continue

                # Parse datetime
                if isinstance(started_at, str):
                    dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                else:
                    dt = started_at

                hour = dt.hour
                status = execution.get("status")

                hourly_stats[hour]["total"] += 1
                if status in ["failed", "error"]:
                    hourly_stats[hour]["failed"] += 1

            except Exception:
                continue

        # Analyze hourly patterns
        for hour, stats in hourly_stats.items():
            if stats["total"] < self.min_executions:
                continue

            failure_rate = stats["failed"] / stats["total"]

            if failure_rate >= self.failure_threshold:
                pattern = {
                    "type": "time_pattern",
                    "hour": hour,
                    "time_range": f"{hour:02d}:00-{(hour+1)%24:02d}:00",
                    "failure_rate": failure_rate,
                    "total_executions": stats["total"],
                    "failed_executions": stats["failed"],
                    "confidence": min(failure_rate * (stats["total"] / 10), 1.0),
                    "detected_at": datetime.now().isoformat(),
                    "severity": "medium",
                    "recommendation": f"High failure rate during {hour:02d}:00-{(hour+1)%24:02d}:00"
                }

                patterns.append(pattern)

        return patterns

    def _detect_dependency_patterns(
        self,
        execution_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect dependency patterns

        Находит зависимости: "если A падает, то B тоже падает"
        """
        patterns = []

        # Group by execution batch (same time window = 5 minutes)
        time_window = timedelta(minutes=5)
        batches = []
        current_batch = []
        last_time = None

        sorted_history = sorted(
            execution_history,
            key=lambda x: x.get("started_at", "")
        )

        for execution in sorted_history:
            try:
                started_at = execution.get("started_at")
                if not started_at:
                    continue

                if isinstance(started_at, str):
                    dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                else:
                    dt = started_at

                if last_time is None or (dt - last_time) <= time_window:
                    current_batch.append(execution)
                else:
                    if current_batch:
                        batches.append(current_batch)
                    current_batch = [execution]

                last_time = dt

            except Exception:
                continue

        if current_batch:
            batches.append(current_batch)

        # Analyze co-failures
        co_failure_counts = defaultdict(int)
        total_batches = len(batches)

        for batch in batches:
            failed_scenarios = set()

            for execution in batch:
                if execution.get("status") in ["failed", "error"]:
                    failed_scenarios.add(execution.get("scenario_id"))

            # Record co-failures
            failed_list = list(failed_scenarios)
            for i in range(len(failed_list)):
                for j in range(i + 1, len(failed_list)):
                    pair = tuple(sorted([failed_list[i], failed_list[j]]))
                    co_failure_counts[pair] += 1

        # Find significant co-failures
        for (scenario_a, scenario_b), count in co_failure_counts.items():
            if count < 3:  # Minimum 3 co-failures
                continue

            co_failure_rate = count / total_batches

            if co_failure_rate >= 0.2:  # 20% co-failure rate
                pattern = {
                    "type": "dependency_pattern",
                    "scenario_a": scenario_a,
                    "scenario_b": scenario_b,
                    "co_failure_count": count,
                    "total_batches": total_batches,
                    "co_failure_rate": co_failure_rate,
                    "confidence": min(co_failure_rate * (count / 5), 1.0),
                    "detected_at": datetime.now().isoformat(),
                    "severity": "medium",
                    "recommendation": f"{scenario_a} and {scenario_b} often fail together"
                }

                patterns.append(pattern)

        return patterns

    def _detect_success_patterns(
        self,
        execution_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect success patterns

        Находит сценарии с высоким успехом
        """
        patterns = []

        scenario_stats = defaultdict(lambda: {"total": 0, "success": 0})

        for execution in execution_history:
            scenario_id = execution.get("scenario_id")
            status = execution.get("status")

            scenario_stats[scenario_id]["total"] += 1

            if status == "success":
                scenario_stats[scenario_id]["success"] += 1

        for scenario_id, stats in scenario_stats.items():
            if stats["total"] < self.min_executions:
                continue

            success_rate = stats["success"] / stats["total"]

            if success_rate >= 0.95:  # 95%+ success rate
                pattern = {
                    "type": "success_pattern",
                    "scenario_id": scenario_id,
                    "success_rate": success_rate,
                    "total_executions": stats["total"],
                    "success_executions": stats["success"],
                    "confidence": min(success_rate * (stats["total"] / 10), 1.0),
                    "detected_at": datetime.now().isoformat(),
                    "severity": "low",
                    "recommendation": f"{scenario_id} is highly reliable ({success_rate*100:.1f}% success)"
                }

                patterns.append(pattern)

        return patterns

    def _detect_anomalies(
        self,
        execution_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect anomaly patterns

        Находит аномалии в duration, необычные ошибки
        """
        patterns = []

        # Group by scenario_id
        scenario_durations = defaultdict(list)

        for execution in execution_history:
            scenario_id = execution.get("scenario_id")
            duration = execution.get("duration_ms")

            if duration is not None:
                scenario_durations[scenario_id].append(duration)

        # Detect duration anomalies
        for scenario_id, durations in scenario_durations.items():
            if len(durations) < self.min_executions:
                continue

            try:
                mean_duration = statistics.mean(durations)
                stdev_duration = statistics.stdev(durations) if len(durations) > 1 else 0

                # Check for outliers (> 3 standard deviations)
                anomaly_count = 0
                for duration in durations:
                    if stdev_duration > 0:
                        z_score = abs((duration - mean_duration) / stdev_duration)
                        if z_score > 3:
                            anomaly_count += 1

                if anomaly_count > 0:
                    anomaly_rate = anomaly_count / len(durations)

                    if anomaly_rate >= 0.1:  # 10%+ anomalies
                        pattern = {
                            "type": "anomaly_pattern",
                            "subtype": "duration_anomaly",
                            "scenario_id": scenario_id,
                            "mean_duration_ms": mean_duration,
                            "stdev_duration_ms": stdev_duration,
                            "anomaly_count": anomaly_count,
                            "total_executions": len(durations),
                            "anomaly_rate": anomaly_rate,
                            "confidence": min(anomaly_rate * (len(durations) / 10), 1.0),
                            "detected_at": datetime.now().isoformat(),
                            "severity": "medium",
                            "recommendation": f"{scenario_id} has unstable execution time"
                        }

                        patterns.append(pattern)

            except Exception as e:
                logger.warning(f"Error analyzing durations for {scenario_id}: {e}")

        return patterns

    def _detect_sequence_patterns(
        self,
        execution_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect sequence patterns

        Находит частые последовательности выполнения сценариев
        """
        patterns = []

        # Group by time windows
        time_window = timedelta(minutes=10)
        sequences = []
        current_sequence = []
        last_time = None

        sorted_history = sorted(
            execution_history,
            key=lambda x: x.get("started_at", "")
        )

        for execution in sorted_history:
            try:
                started_at = execution.get("started_at")
                if not started_at:
                    continue

                if isinstance(started_at, str):
                    dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                else:
                    dt = started_at

                if last_time is None or (dt - last_time) <= time_window:
                    current_sequence.append(execution.get("scenario_id"))
                else:
                    if len(current_sequence) >= 2:
                        sequences.append(tuple(current_sequence))
                    current_sequence = [execution.get("scenario_id")]

                last_time = dt

            except Exception:
                continue

        if len(current_sequence) >= 2:
            sequences.append(tuple(current_sequence))

        # Find frequent sequences
        sequence_counts = Counter(sequences)

        for sequence, count in sequence_counts.most_common(10):
            if count >= 3:  # Minimum 3 occurrences
                pattern = {
                    "type": "sequence_pattern",
                    "sequence": list(sequence),
                    "occurrences": count,
                    "total_sequences": len(sequences),
                    "frequency": count / len(sequences) if sequences else 0,
                    "confidence": min((count / 5), 1.0),
                    "detected_at": datetime.now().isoformat(),
                    "severity": "low",
                    "recommendation": f"Common execution sequence: {' → '.join(sequence)}"
                }

                patterns.append(pattern)

        return patterns

    async def get_patterns_by_type(self, pattern_type: str) -> List[Dict[str, Any]]:
        """Get all patterns of specific type"""
        return [p for p in self.detected_patterns if p.get("type") == pattern_type]

    async def get_patterns_by_scenario(self, scenario_id: str) -> List[Dict[str, Any]]:
        """Get all patterns related to specific scenario"""
        return [
            p for p in self.detected_patterns
            if p.get("scenario_id") == scenario_id
            or p.get("scenario_a") == scenario_id
            or p.get("scenario_b") == scenario_id
            or scenario_id in p.get("sequence", [])
        ]

    async def get_high_severity_patterns(self) -> List[Dict[str, Any]]:
        """Get all high severity patterns"""
        return [p for p in self.detected_patterns if p.get("severity") == "high"]


# Global instance
_pattern_detector: Optional[PatternDetector] = None


def get_pattern_detector() -> PatternDetector:
    """Get or create global pattern detector"""
    global _pattern_detector

    if _pattern_detector is None:
        _pattern_detector = PatternDetector()

    return _pattern_detector
