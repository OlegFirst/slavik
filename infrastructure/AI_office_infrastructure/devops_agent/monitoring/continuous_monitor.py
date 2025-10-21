#!/usr/bin/env python3
"""
Continuous Event Intelligence Monitor

Непрерывный мониторинг качества событийной архитектуры:
- Отслеживает изменения в событиях
- Обнаруживает регрессии
- Отправляет уведомления
- Интегрируется с мониторингом (Prometheus/Grafana)

Использование:
    python3 continuous_monitor.py --watch
    python3 continuous_monitor.py --export-metrics
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventIntelligenceMonitor:
    """Непрерывный мониторинг Event Intelligence"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.report_path = self.project_root / "infrastructure/eventbus/events/intelligence_report.json"
        self.metrics_path = self.project_root / "infrastructure/eventbus/events/metrics.prom"
        self.history_path = self.project_root / "infrastructure/eventbus/events/history.json"

        self.history: List[Dict] = self._load_history()

    def _load_history(self) -> List[Dict]:
        """Загружает историю метрик"""
        if self.history_path.exists():
            with open(self.history_path, 'r') as f:
                return json.load(f)
        return []

    def _save_history(self):
        """Сохраняет историю"""
        with open(self.history_path, 'w') as f:
            json.dump(self.history, f, indent=2)

    def run_scan(self) -> Dict:
        """Запускает сканирование Event Intelligence"""
        logger.info(" Running Event Intelligence scan...")

        cmd = [
            'python3',
            str(self.project_root / 'tools/event_intelligence/event_intelligence_system.py'),
            '--scan',
            '--validate',
            '--suggest',
            '--report',
            str(self.report_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Scan failed: {result.stderr}")
            return {}

        with open(self.report_path, 'r') as f:
            return json.load(f)

    def export_prometheus_metrics(self, report: Dict):
        """Экспортирует метрики в формате Prometheus"""

        summary = report.get('summary', {})
        gaps = report.get('gaps', [])

        metrics = f"""# HELP event_intelligence_schema_events Number of events defined in AsyncAPI schema
# TYPE event_intelligence_schema_events gauge
event_intelligence_schema_events {summary.get('schema_events', 0)}

# HELP event_intelligence_code_events Number of events found in code
# TYPE event_intelligence_code_events gauge
event_intelligence_code_events {summary.get('code_events', 0)}

# HELP event_intelligence_gaps_total Total number of event gaps
# TYPE event_intelligence_gaps_total gauge
event_intelligence_gaps_total {summary.get('gaps_found', 0)}

# HELP event_intelligence_gaps_critical Number of critical event gaps
# TYPE event_intelligence_gaps_critical gauge
event_intelligence_gaps_critical {len([g for g in gaps if g['severity'] == 'critical'])}

# HELP event_intelligence_gaps_warning Number of warning event gaps
# TYPE event_intelligence_gaps_warning gauge
event_intelligence_gaps_warning {len([g for g in gaps if g['severity'] == 'warning'])}

# HELP event_intelligence_potential_events Number of potential events discovered
# TYPE event_intelligence_potential_events gauge
event_intelligence_potential_events {summary.get('potential_events', 0)}

# HELP event_intelligence_coverage_percent Event coverage percentage
# TYPE event_intelligence_coverage_percent gauge
event_intelligence_coverage_percent {self._calculate_coverage(summary)}

# HELP event_intelligence_last_scan_timestamp Unix timestamp of last scan
# TYPE event_intelligence_last_scan_timestamp gauge
event_intelligence_last_scan_timestamp {int(time.time())}
"""

        with open(self.metrics_path, 'w') as f:
            f.write(metrics)

        logger.info(f" Metrics exported to {self.metrics_path}")

    def _calculate_coverage(self, summary: Dict) -> float:
        """Вычисляет процент покрытия событий"""
        schema = summary.get('schema_events', 0)
        code = summary.get('code_events', 0)

        if schema == 0:
            return 100.0

        return (code / schema) * 100.0

    def detect_regressions(self, current_report: Dict) -> List[Dict]:
        """Обнаруживает регрессии по сравнению с предыдущим сканированием"""
        if not self.history:
            return []

        previous = self.history[-1]
        regressions = []

        # Увеличение критических пробелов
        prev_critical = len([g for g in previous['gaps'] if g['severity'] == 'critical'])
        curr_critical = len([g for g in current_report['gaps'] if g['severity'] == 'critical'])

        if curr_critical > prev_critical:
            regressions.append({
                'type': 'critical_gaps_increased',
                'previous': prev_critical,
                'current': curr_critical,
                'delta': curr_critical - prev_critical
            })

        # Уменьшение покрытия
        prev_coverage = self._calculate_coverage(previous['summary'])
        curr_coverage = self._calculate_coverage(current_report['summary'])

        if curr_coverage < prev_coverage - 5:  # Снижение более чем на 5%
            regressions.append({
                'type': 'coverage_decreased',
                'previous': prev_coverage,
                'current': curr_coverage,
                'delta': curr_coverage - prev_coverage
            })

        return regressions

    def watch(self, interval: int = 3600):
        """
        Непрерывный мониторинг с заданным интервалом

        Args:
            interval: Интервал между сканированиями в секундах (default: 1 час)
        """
        logger.info(f"️ Starting continuous monitoring (interval: {interval}s)...")

        while True:
            try:
                # Запуск сканирования
                report = self.run_scan()

                if report:
                    # Экспорт метрик
                    self.export_prometheus_metrics(report)

                    # Обнаружение регрессий
                    regressions = self.detect_regressions(report)

                    if regressions:
                        self._alert_regressions(regressions)

                    # Сохранение в историю
                    self.history.append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'summary': report['summary'],
                        'gaps': report['gaps']
                    })
                    self._save_history()

                    logger.info(" Scan completed successfully")

            except Exception as e:
                logger.error(f" Error during monitoring: {e}")

            # Ожидание следующего сканирования
            time.sleep(interval)

    def _alert_regressions(self, regressions: List[Dict]):
        """Отправляет уведомления о регрессиях"""
        logger.warning(f"️ Detected {len(regressions)} regressions:")

        for regression in regressions:
            logger.warning(f"  - {regression['type']}: {regression['previous']} -> {regression['current']}")

        # TODO: Интеграция с системой уведомлений
        # - Slack
        # - Email
        # - PagerDuty

    def generate_trend_report(self, days: int = 7) -> Dict:
        """Генерирует отчёт о трендах за указанный период"""

        cutoff_date = datetime.utcnow().timestamp() - (days * 86400)

        recent_history = [
            h for h in self.history
            if datetime.fromisoformat(h['timestamp']).timestamp() > cutoff_date
        ]

        if not recent_history:
            return {}

        # Вычисляем тренды
        coverages = [self._calculate_coverage(h['summary']) for h in recent_history]
        critical_gaps = [
            len([g for g in h['gaps'] if g['severity'] == 'critical'])
            for h in recent_history
        ]

        return {
            'period_days': days,
            'scans_count': len(recent_history),
            'coverage': {
                'start': coverages[0],
                'end': coverages[-1],
                'trend': 'improving' if coverages[-1] > coverages[0] else 'degrading',
                'delta': coverages[-1] - coverages[0]
            },
            'critical_gaps': {
                'start': critical_gaps[0],
                'end': critical_gaps[-1],
                'trend': 'improving' if critical_gaps[-1] < critical_gaps[0] else 'degrading',
                'delta': critical_gaps[-1] - critical_gaps[0]
            }
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Continuous Event Intelligence Monitor')
    parser.add_argument('--watch', action='store_true',
                       help='Start continuous monitoring')
    parser.add_argument('--export-metrics', action='store_true',
                       help='Export Prometheus metrics once and exit')
    parser.add_argument('--trend-report', type=int, metavar='DAYS',
                       help='Generate trend report for last N days')
    parser.add_argument('--interval', type=int, default=3600,
                       help='Monitoring interval in seconds (default: 3600)')
    parser.add_argument('--project-root', type=str,
                       default='/Users/MD/AI-Platform-ISO',
                       help='Project root directory')

    args = parser.parse_args()

    monitor = EventIntelligenceMonitor(args.project_root)

    if args.watch:
        monitor.watch(interval=args.interval)

    elif args.export_metrics:
        report = monitor.run_scan()
        if report:
            monitor.export_prometheus_metrics(report)

    elif args.trend_report:
        trend = monitor.generate_trend_report(days=args.trend_report)
        print(json.dumps(trend, indent=2))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
