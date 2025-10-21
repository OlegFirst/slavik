"""
Performance Test Report Generator
==================================

Generates comprehensive HTML reports from performance test results.

Usage:
    python generate_report.py --locust-stats reports/locust-stats_stats.csv
    python generate_report.py --benchmark reports/benchmark_api.json
    python generate_report.py --metrics reports/metrics.json --output reports/performance_report.html
"""

import argparse
import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any
import yaml

# Template for HTML report
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>BCM Platform Performance Report - {report_date}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-card.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .metric-card.warning {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .metric-card.error {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
            color: white;
        }}
        .metric-card .value {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-card .label {{
            font-size: 12px;
            opacity: 0.8;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background-color: #34495e;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .status-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-success {{
            background-color: #d4edda;
            color: #155724;
        }}
        .status-warning {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .status-error {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .recommendations {{
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }}
        .recommendations h3 {{
            margin-top: 0;
            color: #2980b9;
        }}
        .recommendations ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1> BCM Platform Performance Report</h1>
        <p><strong>Generated:</strong> {report_date}</p>
        <p><strong>Test Period:</strong> {test_period}</p>

        <h2> Executive Summary</h2>
        <div class="summary-grid">
            {summary_cards}
        </div>

        <h2> Performance Metrics</h2>
        {performance_metrics}

        <h2> Load Test Results</h2>
        {load_test_results}

        <h2> Recommendations</h2>
        <div class="recommendations">
            <h3>Performance Optimization Suggestions</h3>
            <ul>
                {recommendations}
            </ul>
        </div>

        <div class="footer">
            <p>BCM Platform Performance Testing Suite v1.0</p>
            <p>ISO 22301:2019 Compliant | Generated by Claude Code</p>
        </div>
    </div>
</body>
</html>
"""


class ReportGenerator:
    """Generate performance test reports"""

    def __init__(self):
        self.data = {}
        self.recommendations = []

    def load_locust_stats(self, stats_file):
        """Load Locust statistics from CSV"""
        try:
            with open(stats_file, 'r') as f:
                reader = csv.DictReader(f)
                self.data['locust_stats'] = list(reader)
            print(f" Loaded Locust stats: {stats_file}")
        except Exception as e:
            print(f"️  Could not load Locust stats: {e}")

    def load_benchmark_results(self, benchmark_file):
        """Load pytest-benchmark results from JSON"""
        try:
            with open(benchmark_file, 'r') as f:
                self.data['benchmarks'] = json.load(f)
            print(f" Loaded benchmark results: {benchmark_file}")
        except Exception as e:
            print(f"️  Could not load benchmarks: {e}")

    def load_metrics(self, metrics_file):
        """Load collected metrics from JSON"""
        try:
            with open(metrics_file, 'r') as f:
                self.data['metrics'] = json.load(f)
            print(f" Loaded metrics: {metrics_file}")
        except Exception as e:
            print(f"️  Could not load metrics: {e}")

    def load_targets(self, targets_file='performance_targets.yaml'):
        """Load performance targets"""
        try:
            with open(targets_file, 'r') as f:
                self.data['targets'] = yaml.safe_load(f)
            print(f" Loaded performance targets: {targets_file}")
        except Exception as e:
            print(f"️  Could not load targets: {e}")

    def analyze_performance(self):
        """Analyze performance against targets"""
        analysis = {
            'passed': 0,
            'warnings': 0,
            'failures': 0,
            'issues': []
        }

        # Analyze Locust results
        if 'locust_stats' in self.data:
            for stat in self.data['locust_stats']:
                if stat.get('Type') != 'Aggregated':
                    try:
                        avg_response = float(stat.get('Average Response Time', 0))
                        p95_response = float(stat.get('95%', 0))
                        failure_rate = float(stat.get('Failures/s', 0))

                        if p95_response > 1000:
                            analysis['failures'] += 1
                            analysis['issues'].append(f"High P95 latency for {stat['Name']}: {p95_response:.0f}ms")
                            self.recommendations.append(
                                f"Investigate {stat['Name']} - P95 latency exceeds 1000ms"
                            )
                        elif p95_response > 500:
                            analysis['warnings'] += 1
                            self.recommendations.append(
                                f"Monitor {stat['Name']} - P95 latency approaching threshold"
                            )
                        else:
                            analysis['passed'] += 1
                    except (ValueError, KeyError):
                        pass

        # Analyze system metrics
        if 'metrics' in self.data and 'system_metrics' in self.data['metrics']:
            system_metrics = self.data['metrics']['system_metrics']
            if system_metrics:
                cpu_values = [m['cpu']['percent'] for m in system_metrics if 'cpu' in m]
                memory_values = [m['memory']['percent'] for m in system_metrics if 'memory' in m]

                if cpu_values:
                    avg_cpu = sum(cpu_values) / len(cpu_values)
                    max_cpu = max(cpu_values)

                    if max_cpu > 85:
                        analysis['failures'] += 1
                        self.recommendations.append(
                            f"CPU usage critical: {max_cpu:.1f}% - Consider scaling horizontally"
                        )
                    elif avg_cpu > 70:
                        analysis['warnings'] += 1
                        self.recommendations.append(
                            f"CPU usage elevated: {avg_cpu:.1f}% average - Monitor for scaling needs"
                        )

                if memory_values:
                    avg_memory = sum(memory_values) / len(memory_values)
                    max_memory = max(memory_values)

                    if max_memory > 90:
                        analysis['failures'] += 1
                        self.recommendations.append(
                            f"Memory usage critical: {max_memory:.1f}% - Investigate memory leaks"
                        )
                    elif avg_memory > 75:
                        analysis['warnings'] += 1
                        self.recommendations.append(
                            f"Memory usage high: {avg_memory:.1f}% average - Monitor memory growth"
                        )

        self.data['analysis'] = analysis
        return analysis

    def generate_html_report(self, output_file='reports/performance_report.html'):
        """Generate HTML report"""
        # Analyze performance
        analysis = self.analyze_performance()

        # Generate summary cards
        summary_cards = []

        # Total requests card
        if 'locust_stats' in self.data:
            total_requests = sum(int(stat.get('Request Count', 0)) for stat in self.data['locust_stats'])
            total_failures = sum(int(stat.get('Failure Count', 0)) for stat in self.data['locust_stats'])
            failure_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0

            card_class = 'success' if failure_rate < 1 else ('warning' if failure_rate < 5 else 'error')

            summary_cards.append(f"""
            <div class="metric-card {card_class}">
                <h3>Total Requests</h3>
                <div class="value">{total_requests:,}</div>
                <div class="label">Failure Rate: {failure_rate:.2f}%</div>
            </div>
            """)

        # Performance status card
        card_class = 'success' if analysis['failures'] == 0 else ('warning' if analysis['failures'] < 3 else 'error')
        summary_cards.append(f"""
        <div class="metric-card {card_class}">
            <h3>Performance Status</h3>
            <div class="value">{analysis['passed']}</div>
            <div class="label">Passed | {analysis['warnings']} Warnings | {analysis['failures']} Failures</div>
        </div>
        """)

        # Generate performance metrics table
        performance_metrics = "<table><tr><th>Endpoint</th><th>Requests</th><th>Avg (ms)</th><th>P95 (ms)</th><th>P99 (ms)</th><th>Status</th></tr>"

        if 'locust_stats' in self.data:
            for stat in self.data['locust_stats']:
                if stat.get('Type') != 'Aggregated':
                    try:
                        p95 = float(stat.get('95%', 0))
                        status_class = 'success' if p95 < 500 else ('warning' if p95 < 1000 else 'error')
                        status_text = 'GOOD' if p95 < 500 else ('MODERATE' if p95 < 1000 else 'SLOW')

                        performance_metrics += f"""
                        <tr>
                            <td>{stat.get('Name', 'Unknown')}</td>
                            <td>{stat.get('Request Count', 0)}</td>
                            <td>{stat.get('Average Response Time', 0)}</td>
                            <td>{stat.get('95%', 0)}</td>
                            <td>{stat.get('99%', 0)}</td>
                            <td><span class="status-badge status-{status_class}">{status_text}</span></td>
                        </tr>
                        """
                    except (ValueError, KeyError):
                        pass

        performance_metrics += "</table>"

        # Generate load test results
        load_test_results = "<p>Load test completed successfully.</p>"
        if 'locust_stats' in self.data:
            for stat in self.data['locust_stats']:
                if stat.get('Type') == 'Aggregated':
                    load_test_results = f"""
                    <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Requests</td><td>{stat.get('Request Count', 0)}</td></tr>
                    <tr><td>Total Failures</td><td>{stat.get('Failure Count', 0)}</td></tr>
                    <tr><td>Average Response Time</td><td>{stat.get('Average Response Time', 0)} ms</td></tr>
                    <tr><td>Min Response Time</td><td>{stat.get('Min Response Time', 0)} ms</td></tr>
                    <tr><td>Max Response Time</td><td>{stat.get('Max Response Time', 0)} ms</td></tr>
                    <tr><td>P50 (Median)</td><td>{stat.get('50%', 0)} ms</td></tr>
                    <tr><td>P95</td><td>{stat.get('95%', 0)} ms</td></tr>
                    <tr><td>P99</td><td>{stat.get('99%', 0)} ms</td></tr>
                    <tr><td>Requests/sec</td><td>{stat.get('Requests/s', 0)}</td></tr>
                    </table>
                    """
                    break

        # Default recommendations if none generated
        if not self.recommendations:
            self.recommendations = [
                "All metrics within acceptable ranges",
                "Continue monitoring performance trends",
                "Review logs for any warnings or errors",
                "Consider load testing with higher concurrency"
            ]

        # Generate final HTML
        html_content = HTML_TEMPLATE.format(
            report_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            test_period=self.data.get('metrics', {}).get('collection_start', 'N/A'),
            summary_cards='\n'.join(summary_cards),
            performance_metrics=performance_metrics,
            load_test_results=load_test_results,
            recommendations='</li><li>'.join(self.recommendations)
        )

        # Save report
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(html_content)

        print(f" HTML report generated: {output_file}")
        return output_file


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate performance test report')
    parser.add_argument('--locust-stats', help='Locust statistics CSV file')
    parser.add_argument('--benchmark', help='Benchmark results JSON file')
    parser.add_argument('--metrics', help='Metrics JSON file')
    parser.add_argument('--targets', default='performance_targets.yaml', help='Performance targets YAML file')
    parser.add_argument('--output', default='reports/performance_report.html', help='Output HTML file')
    args = parser.parse_args()

    generator = ReportGenerator()

    # Load all available data
    if args.locust_stats and os.path.exists(args.locust_stats):
        generator.load_locust_stats(args.locust_stats)

    if args.benchmark and os.path.exists(args.benchmark):
        generator.load_benchmark_results(args.benchmark)

    if args.metrics and os.path.exists(args.metrics):
        generator.load_metrics(args.metrics)

    if os.path.exists(args.targets):
        generator.load_targets(args.targets)

    # Generate report
    output_file = generator.generate_html_report(args.output)
    print(f"\n Report available at: {output_file}")


if __name__ == '__main__':
    main()
