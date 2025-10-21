"""
Performance Metrics Collector
==============================

Collects performance metrics from various sources:
- Prometheus metrics
- Database query statistics
- Cache statistics
- Resource utilization (CPU, memory, disk)

Usage:
    python metrics_collector.py --duration 300 --interval 10
    python metrics_collector.py --config performance_targets.yaml --output reports/metrics.json
"""

import argparse
import asyncio
import json
import os
import psutil
import time
from datetime import datetime
from typing import Dict, List, Any
import requests
import yaml
from dotenv import load_dotenv

# Load environment
load_dotenv('.env.perf')


class MetricsCollector:
    """Collects performance metrics from multiple sources"""

    def __init__(self, config_file='performance_targets.yaml'):
        self.config = self._load_config(config_file)
        self.metrics = {
            'collection_start': datetime.now().isoformat(),
            'collection_end': None,
            'system_metrics': [],
            'service_metrics': [],
            'database_metrics': [],
            'cache_metrics': [],
            'prometheus_metrics': []
        }

    def _load_config(self, config_file):
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            return {}

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()

            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'per_cpu': psutil.cpu_percent(percpu=True)
                },
                'memory': {
                    'total_mb': memory.total / (1024 * 1024),
                    'available_mb': memory.available / (1024 * 1024),
                    'used_mb': memory.used / (1024 * 1024),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': disk.total / (1024 ** 3),
                    'used_gb': disk.used / (1024 ** 3),
                    'free_gb': disk.free / (1024 ** 3),
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            }
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            return {}

    def collect_service_health(self) -> List[Dict[str, Any]]:
        """Collect health status from all services"""
        services = [
            ('BIA', os.getenv('BIA_SERVICE_URL', 'http://localhost:8012')),
            ('Compliance', os.getenv('COMPLIANCE_SERVICE_URL', 'http://localhost:8014')),
            ('Planning', os.getenv('PLANNING_SERVICE_URL', 'http://localhost:8011')),
            ('Plans', os.getenv('PLANS_SERVICE_URL', 'http://localhost:8023'))
        ]

        health_status = []

        for service_name, service_url in services:
            try:
                start_time = time.time()
                response = requests.get(f"{service_url}/health", timeout=5)
                response_time = (time.time() - start_time) * 1000

                health_status.append({
                    'service': service_name,
                    'url': service_url,
                    'healthy': response.status_code == 200,
                    'status_code': response.status_code,
                    'response_time_ms': response_time,
                    'timestamp': datetime.now().isoformat(),
                    'details': response.json() if response.status_code == 200 else None
                })
            except Exception as e:
                health_status.append({
                    'service': service_name,
                    'url': service_url,
                    'healthy': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })

        return health_status

    def collect_cache_metrics(self) -> Dict[str, Any]:
        """Collect Redis cache metrics"""
        try:
            bia_service_url = os.getenv('BIA_SERVICE_URL', 'http://localhost:8012')
            response = requests.get(f"{bia_service_url}/metrics/cache", timeout=5)

            if response.status_code == 200:
                cache_data = response.json()
                cache_data['timestamp'] = datetime.now().isoformat()
                return cache_data
        except Exception as e:
            print(f"Error collecting cache metrics: {e}")

        return {
            'timestamp': datetime.now().isoformat(),
            'error': 'Could not collect cache metrics'
        }

    def collect_prometheus_metrics(self) -> Dict[str, Any]:
        """Collect metrics from Prometheus"""
        try:
            prometheus_url = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')

            # Query for key metrics
            queries = {
                'http_requests_total': 'sum(http_requests_total)',
                'http_request_duration_p95': 'histogram_quantile(0.95, http_request_duration_seconds)',
                'http_request_duration_p99': 'histogram_quantile(0.99, http_request_duration_seconds)'
            }

            metrics = {'timestamp': datetime.now().isoformat()}

            for metric_name, query in queries.items():
                try:
                    response = requests.get(
                        f"{prometheus_url}/api/v1/query",
                        params={'query': query},
                        timeout=5
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get('status') == 'success':
                            metrics[metric_name] = data.get('data', {}).get('result', [])
                except Exception as e:
                    metrics[metric_name] = {'error': str(e)}

            return metrics
        except Exception as e:
            print(f"Error collecting Prometheus metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def collect_all(self):
        """Collect all metrics at once"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Collecting metrics...")

        # System metrics
        system_metrics = self.collect_system_metrics()
        if system_metrics:
            self.metrics['system_metrics'].append(system_metrics)

        # Service health
        service_health = self.collect_service_health()
        if service_health:
            self.metrics['service_metrics'].append({
                'timestamp': datetime.now().isoformat(),
                'services': service_health
            })

        # Cache metrics
        cache_metrics = self.collect_cache_metrics()
        if cache_metrics:
            self.metrics['cache_metrics'].append(cache_metrics)

        # Prometheus metrics
        prom_metrics = self.collect_prometheus_metrics()
        if prom_metrics:
            self.metrics['prometheus_metrics'].append(prom_metrics)

    def run_collection(self, duration_seconds=300, interval_seconds=10):
        """Run continuous metric collection"""
        print("=" * 80)
        print("Performance Metrics Collection Started")
        print(f"Duration: {duration_seconds}s | Interval: {interval_seconds}s")
        print("=" * 80)

        end_time = time.time() + duration_seconds
        iterations = 0

        while time.time() < end_time:
            self.collect_all()
            iterations += 1

            remaining = int(end_time - time.time())
            if remaining > 0:
                print(f"  Collected {iterations} samples. {remaining}s remaining...")
                time.sleep(interval_seconds)

        self.metrics['collection_end'] = datetime.now().isoformat()

        print("=" * 80)
        print(f"Collection Complete: {iterations} samples collected")
        print("=" * 80)

    def save_metrics(self, output_file='reports/metrics.json'):
        """Save collected metrics to file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)

        print(f" Metrics saved to: {output_file}")

    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from collected metrics"""
        summary = {
            'collection_period': {
                'start': self.metrics['collection_start'],
                'end': self.metrics['collection_end']
            },
            'samples_collected': {
                'system_metrics': len(self.metrics['system_metrics']),
                'service_health': len(self.metrics['service_metrics']),
                'cache_metrics': len(self.metrics['cache_metrics']),
                'prometheus_metrics': len(self.metrics['prometheus_metrics'])
            }
        }

        # System metrics summary
        if self.metrics['system_metrics']:
            cpu_values = [m['cpu']['percent'] for m in self.metrics['system_metrics'] if 'cpu' in m]
            memory_values = [m['memory']['percent'] for m in self.metrics['system_metrics'] if 'memory' in m]

            if cpu_values:
                summary['system'] = {
                    'cpu': {
                        'avg': sum(cpu_values) / len(cpu_values),
                        'max': max(cpu_values),
                        'min': min(cpu_values)
                    },
                    'memory': {
                        'avg': sum(memory_values) / len(memory_values),
                        'max': max(memory_values),
                        'min': min(memory_values)
                    }
                }

        # Service health summary
        if self.metrics['service_metrics']:
            service_status = {}
            for metric in self.metrics['service_metrics']:
                for service in metric.get('services', []):
                    service_name = service['service']
                    if service_name not in service_status:
                        service_status[service_name] = {'healthy': 0, 'unhealthy': 0}

                    if service.get('healthy'):
                        service_status[service_name]['healthy'] += 1
                    else:
                        service_status[service_name]['unhealthy'] += 1

            summary['services'] = service_status

        return summary


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Collect performance metrics')
    parser.add_argument('--duration', type=int, default=300, help='Collection duration in seconds')
    parser.add_argument('--interval', type=int, default=10, help='Collection interval in seconds')
    parser.add_argument('--config', default='performance_targets.yaml', help='Config file')
    parser.add_argument('--output', default='reports/metrics.json', help='Output file')
    args = parser.parse_args()

    collector = MetricsCollector(args.config)
    collector.run_collection(args.duration, args.interval)
    collector.save_metrics(args.output)

    # Generate and display summary
    summary = collector.generate_summary()
    print("\n Collection Summary:")
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
