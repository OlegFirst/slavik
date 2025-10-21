"""
Performance Regression Detection
=================================

Compares current performance test results with baseline to detect regressions.

Usage:
    python performance_regression.py --current reports/locust_stats.csv --baseline reports/baseline.csv
    python performance_regression.py --current reports/locust_stats.csv --threshold 10
"""

import argparse
import csv
import json
import sys
from typing import Dict, List, Tuple
from datetime import datetime


class PerformanceRegression:
    """Detect performance regressions"""

    def __init__(self, threshold_percent=10):
        self.threshold_percent = threshold_percent
        self.regressions = []
        self.improvements = []

    def load_stats(self, csv_file: str) -> Dict:
        """Load Locust statistics from CSV"""
        stats = {}

        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Type') == 'Aggregated':
                        stats['aggregated'] = row
                    elif row.get('Name') and row.get('Type') != 'Aggregated':
                        stats[row['Name']] = row

            return stats
        except Exception as e:
            print(f"Error loading stats from {csv_file}: {e}")
            return {}

    def compare_metric(self, current: float, baseline: float, metric_name: str) -> Tuple[float, str]:
        """Compare a metric and determine if regression occurred"""
        if baseline == 0:
            return 0.0, 'unknown'

        change_percent = ((current - baseline) / baseline) * 100

        # For response time metrics, increase is bad
        if 'time' in metric_name.lower() or 'latency' in metric_name.lower():
            if change_percent > self.threshold_percent:
                return change_percent, 'regression'
            elif change_percent < -self.threshold_percent:
                return change_percent, 'improvement'
            else:
                return change_percent, 'stable'
        # For throughput metrics, decrease is bad
        elif 'rps' in metric_name.lower() or 'throughput' in metric_name.lower():
            if change_percent < -self.threshold_percent:
                return change_percent, 'regression'
            elif change_percent > self.threshold_percent:
                return change_percent, 'improvement'
            else:
                return change_percent, 'stable'
        else:
            return change_percent, 'stable'

    def compare_stats(self, current_stats: Dict, baseline_stats: Dict) -> Dict:
        """Compare current stats against baseline"""
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'threshold_percent': self.threshold_percent,
            'regressions': [],
            'improvements': [],
            'stable': [],
            'summary': {
                'total_endpoints': 0,
                'regressions_count': 0,
                'improvements_count': 0,
                'stable_count': 0
            }
        }

        # Compare aggregated stats
        if 'aggregated' in current_stats and 'aggregated' in baseline_stats:
            current_agg = current_stats['aggregated']
            baseline_agg = baseline_stats['aggregated']

            metrics_to_compare = [
                ('Average Response Time', 'avg_response_time'),
                ('95%', 'p95'),
                ('99%', 'p99'),
                ('Requests/s', 'throughput')
            ]

            for csv_key, metric_key in metrics_to_compare:
                try:
                    current_val = float(current_agg.get(csv_key, 0))
                    baseline_val = float(baseline_agg.get(csv_key, 0))

                    change_percent, status = self.compare_metric(current_val, baseline_val, metric_key)

                    result = {
                        'metric': metric_key,
                        'current': current_val,
                        'baseline': baseline_val,
                        'change_percent': change_percent,
                        'status': status
                    }

                    if status == 'regression':
                        comparison['regressions'].append(result)
                    elif status == 'improvement':
                        comparison['improvements'].append(result)
                    else:
                        comparison['stable'].append(result)

                except (ValueError, KeyError):
                    pass

        # Compare per-endpoint stats
        for endpoint_name in current_stats:
            if endpoint_name == 'aggregated':
                continue

            if endpoint_name not in baseline_stats:
                continue  # New endpoint, skip comparison

            comparison['summary']['total_endpoints'] += 1

            current_endpoint = current_stats[endpoint_name]
            baseline_endpoint = baseline_stats[endpoint_name]

            try:
                # Compare P95 response time
                current_p95 = float(current_endpoint.get('95%', 0))
                baseline_p95 = float(baseline_endpoint.get('95%', 0))

                change_percent, status = self.compare_metric(current_p95, baseline_p95, 'p95')

                result = {
                    'endpoint': endpoint_name,
                    'metric': 'p95',
                    'current': current_p95,
                    'baseline': baseline_p95,
                    'change_percent': change_percent,
                    'status': status
                }

                if status == 'regression':
                    comparison['regressions'].append(result)
                    comparison['summary']['regressions_count'] += 1
                elif status == 'improvement':
                    comparison['improvements'].append(result)
                    comparison['summary']['improvements_count'] += 1
                else:
                    comparison['summary']['stable_count'] += 1

            except (ValueError, KeyError):
                pass

        return comparison

    def print_report(self, comparison: Dict):
        """Print regression detection report"""
        print("=" * 80)
        print("PERFORMANCE REGRESSION DETECTION REPORT")
        print("=" * 80)
        print(f"Timestamp: {comparison['timestamp']}")
        print(f"Threshold: {comparison['threshold_percent']}%")
        print("")

        # Summary
        summary = comparison['summary']
        print(" Summary:")
        print(f"  Total Endpoints Compared: {summary['total_endpoints']}")
        print(f"  Regressions: {summary['regressions_count']}")
        print(f"  Improvements: {summary['improvements_count']}")
        print(f"  Stable: {summary['stable_count']}")
        print("")

        # Regressions
        if comparison['regressions']:
            print(" REGRESSIONS DETECTED:")
            print("-" * 80)
            for reg in comparison['regressions']:
                if 'endpoint' in reg:
                    print(f"  Endpoint: {reg['endpoint']}")
                print(f"  Metric: {reg['metric']}")
                print(f"  Current: {reg['current']:.2f}")
                print(f"  Baseline: {reg['baseline']:.2f}")
                print(f"  Change: {reg['change_percent']:+.2f}%")
                print("-" * 80)
        else:
            print(" No regressions detected")
            print("")

        # Improvements
        if comparison['improvements']:
            print(" IMPROVEMENTS:")
            print("-" * 80)
            for imp in comparison['improvements']:
                if 'endpoint' in imp:
                    print(f"  Endpoint: {imp['endpoint']}")
                print(f"  Metric: {imp['metric']}")
                print(f"  Current: {imp['current']:.2f}")
                print(f"  Baseline: {imp['baseline']:.2f}")
                print(f"  Change: {imp['change_percent']:+.2f}%")
                print("-" * 80)

        print("=" * 80)

    def save_report(self, comparison: Dict, output_file: str):
        """Save comparison report to JSON"""
        with open(output_file, 'w') as f:
            json.dump(comparison, f, indent=2)

        print(f" Report saved to: {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Detect performance regressions')
    parser.add_argument('--current', required=True, help='Current test results CSV')
    parser.add_argument('--baseline', help='Baseline results CSV (optional)')
    parser.add_argument('--threshold', type=float, default=10, help='Regression threshold percentage')
    parser.add_argument('--output', default='reports/regression_report.json', help='Output JSON file')
    args = parser.parse_args()

    detector = PerformanceRegression(threshold_percent=args.threshold)

    # Load current stats
    current_stats = detector.load_stats(args.current)
    if not current_stats:
        print(" Failed to load current stats")
        sys.exit(1)

    # Load baseline stats
    if args.baseline:
        baseline_stats = detector.load_stats(args.baseline)
        if not baseline_stats:
            print(" Failed to load baseline stats")
            sys.exit(1)
    else:
        # If no baseline provided, compare against target thresholds from config
        print("ℹ️  No baseline provided - checking against absolute thresholds")

        # Simple check: P95 should be under 500ms, failure rate under 2%
        if 'aggregated' in current_stats:
            agg = current_stats['aggregated']
            p95 = float(agg.get('95%', 0))
            failures = int(agg.get('Failure Count', 0))
            requests = int(agg.get('Request Count', 1))
            failure_rate = (failures / requests * 100) if requests > 0 else 0

            print(f"\nCurrent Performance:")
            print(f"  P95: {p95:.2f}ms (target: <500ms)")
            print(f"  Failure Rate: {failure_rate:.2f}% (target: <2%)")

            if p95 > 500 or failure_rate > 2:
                print("\n Performance does not meet targets!")
                sys.exit(1)
            else:
                print("\n Performance meets targets!")
                sys.exit(0)

    # Compare stats
    comparison = detector.compare_stats(current_stats, baseline_stats)

    # Print report
    detector.print_report(comparison)

    # Save report
    detector.save_report(comparison, args.output)

    # Exit with error code if regressions detected
    if comparison['summary']['regressions_count'] > 0:
        print("\n Performance regressions detected!")
        sys.exit(1)
    else:
        print("\n No performance regressions!")
        sys.exit(0)


if __name__ == '__main__':
    main()
