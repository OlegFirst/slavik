# BCM Platform Performance Testing Suite

Comprehensive performance testing and benchmarking suite for the BCM (Business Continuity Management) Platform, compliant with ISO 22301:2019 requirements.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [Test Scenarios](#test-scenarios)
- [Interpreting Results](#interpreting-results)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This performance testing suite provides:

- **Load Testing**: Locust-based load tests for realistic production scenarios
- **Benchmarking**: pytest-benchmark tests for API, database, and cache operations
- **Metrics Collection**: Comprehensive system and application metrics
- **Automated Reporting**: HTML reports with visualizations and recommendations
- **Regression Detection**: Automatic detection of performance degradation
- **CI/CD Integration**: GitHub Actions workflow for continuous performance testing

## ✨ Features

### Load Testing (Locust)

- **4 Test Scenarios**: Light, Medium, Heavy, and Stress tests
- **All 4 Services Covered**:
  - BIA Service (Port 8012)
  - Compliance Service (Port 8014)
  - Planning Service (Port 8011)
  - Plans Service (Port 8023)
- **Realistic Workflows**: User scenarios matching production usage patterns
- **Concurrent Users**: 10 to 200 concurrent users
- **Custom Metrics**: Response time percentiles, throughput, error rates

### Benchmark Tests (pytest-benchmark)

- **API Benchmarks**: 20+ endpoint tests across all services
- **Database Benchmarks**: Query performance, connection pooling, bulk operations
- **Cache Benchmarks**: Redis hit/miss rates, latency, bulk operations
- **Bulk Operation Benchmarks**: 10, 100, 500, 1000 item operations

### Metrics Collection

- **System Metrics**: CPU, memory, disk, network utilization
- **Service Health**: Real-time health checks for all services
- **Cache Metrics**: Hit rate, latency, memory usage
- **Prometheus Integration**: Collect metrics from Prometheus

### Reporting

- **HTML Reports**: Interactive reports with charts and metrics
- **Performance Analysis**: Automated comparison against targets
- **Recommendations**: Actionable optimization suggestions
- **Trend Analysis**: Compare current vs. baseline performance

## 🏗️ Architecture

```
performance-tests/
├── locustfile.py              # Main Locust test file (all services)
├── benchmark_tests/           # pytest-benchmark tests
│   ├── test_api_benchmarks.py
│   ├── test_database_benchmarks.py
│   ├── test_cache_benchmarks.py
│   └── test_bulk_operation_benchmarks.py
├── load_tests/                # Load test scenarios
│   ├── scenario_light.py      # 10 users, 5 min
│   ├── scenario_medium.py     # 50 users, 10 min
│   ├── scenario_heavy.py      # 100 users, 15 min
│   └── scenario_stress.py     # 10→200 users, 20 min
├── metrics_collector.py       # Metrics collection script
├── generate_report.py         # Report generation script
├── performance_regression.py  # Regression detection
├── performance_targets.yaml   # SLA definitions
├── requirements.txt           # Python dependencies
├── .env.perf                  # Environment variables
├── locust.conf                # Locust configuration
├── run_performance_tests.sh   # Main test runner
├── run_benchmark.sh           # Benchmark runner
├── run_load_test.sh           # Load test runner
└── reports/                   # Generated reports
```

## 🚀 Getting Started

### Prerequisites

- **Docker & Docker Compose**: For running services
- **Python 3.11+**: For test scripts
- **8GB RAM minimum**: For running all services and tests
- **10GB free disk space**: For logs and reports

### Installation

1. **Navigate to performance-tests directory:**

```bash
cd /Users/MD/AI-Platform-ISO/platform-services/performance-tests
```

2. **Create virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Start BCM Platform services:**

```bash
cd ..
docker-compose up -d
```

5. **Wait for services to be healthy:**

```bash
# Check health
curl http://localhost:8012/health  # BIA Service
curl http://localhost:8014/health  # Compliance Service
curl http://localhost:8011/health  # Planning Service
curl http://localhost:8023/health  # Plans Service
```

## 🧪 Running Tests

### Quick Start - Run All Tests

Run the complete performance testing suite:

```bash
./run_performance_tests.sh light
```

This will:
1. ✅ Check prerequisites
2. 📊 Run baseline benchmarks
3. 🚀 Execute load tests
4. 📈 Collect metrics
5. 📄 Generate HTML report

### Run Individual Components

#### Benchmarks Only

```bash
./run_benchmark.sh
```

Runs all pytest-benchmark tests:
- API endpoint benchmarks
- Database operation benchmarks
- Cache operation benchmarks
- Bulk operation benchmarks

#### Load Tests Only

```bash
./run_load_test.sh <scenario>
```

Available scenarios:
- `light`: 10 users, 5 minutes, ~1,000 requests
- `medium`: 50 users, 10 minutes, ~10,000 requests
- `heavy`: 100 users, 15 minutes, ~50,000 requests
- `stress`: 10→200 users, 20 minutes, gradual increase

Examples:

```bash
./run_load_test.sh light    # Light load test
./run_load_test.sh medium   # Medium load test
./run_load_test.sh heavy    # Heavy load test
./run_load_test.sh stress   # Stress test
```

#### Metrics Collection

```bash
python metrics_collector.py --duration 300 --interval 10
```

Options:
- `--duration`: Collection duration in seconds (default: 300)
- `--interval`: Collection interval in seconds (default: 10)
- `--output`: Output JSON file (default: reports/metrics.json)

#### Report Generation

```bash
python generate_report.py \
  --locust-stats reports/locust_stats.csv \
  --benchmark reports/benchmark_api.json \
  --metrics reports/metrics.json \
  --output reports/performance_report.html
```

#### Regression Detection

```bash
python performance_regression.py \
  --current reports/locust_stats.csv \
  --baseline reports/baseline.csv \
  --threshold 10
```

## 📊 Test Scenarios

### Light Load (Baseline)

**Purpose**: Establish baseline performance metrics

- **Users**: 10 concurrent
- **Duration**: 5 minutes
- **Expected Requests**: ~1,000
- **Use Case**: Daily regression testing, PR validation
- **Performance Target**: P95 < 200ms, Error Rate < 1%

### Medium Load (Normal Production)

**Purpose**: Simulate normal production load

- **Users**: 50 concurrent
- **Duration**: 10 minutes
- **Expected Requests**: ~10,000
- **Use Case**: Weekly performance validation
- **Performance Target**: P95 < 500ms, Error Rate < 2%

### Heavy Load (Peak Production)

**Purpose**: Test under peak production conditions

- **Users**: 100 concurrent
- **Duration**: 15 minutes
- **Expected Requests**: ~50,000
- **Use Case**: Pre-release testing, capacity planning
- **Performance Target**: P95 < 1000ms, Error Rate < 3%

### Stress Test (Breaking Point)

**Purpose**: Identify system limits and breaking points

- **Users**: 10 → 200 (gradual increase)
- **Duration**: 20 minutes
- **Stages**: 10 stages with increasing load
- **Use Case**: Capacity planning, scalability testing
- **Performance Target**: Identify degradation threshold

## 📈 Interpreting Results

### HTML Reports

Open generated reports in your browser:

```bash
open reports/performance_report_light.html
```

The report includes:
- **Executive Summary**: Key metrics at a glance
- **Performance Metrics**: Response times, throughput, error rates
- **Load Test Results**: Detailed statistics per endpoint
- **Recommendations**: Actionable optimization suggestions

### Performance Metrics

#### Response Time (Latency)

- **P50 (Median)**: 50% of requests faster than this
- **P95**: 95% of requests faster than this (SLA target)
- **P99**: 99% of requests faster than this
- **Max**: Slowest request

**Good Performance:**
- P95 < 500ms: ✅ Excellent
- P95 < 1000ms: ✅ Good
- P95 < 2000ms: ⚠️ Acceptable
- P95 > 2000ms: ❌ Poor

#### Throughput

- **Requests/sec**: Number of requests processed per second
- **Target**: > 50 req/sec for normal load

#### Error Rate

- **Failure Rate**: Percentage of failed requests
- **Target**: < 1% for production

### Benchmark Results

Benchmark results show:
- **Mean**: Average execution time
- **Std Dev**: Variation in execution time
- **Min/Max**: Fastest/slowest execution
- **Rounds**: Number of test iterations

**Example:**

```
test_bia_list_processes_benchmark     Mean: 45.23ms ± 5.12ms
test_bia_get_process_benchmark        Mean: 23.45ms ± 2.34ms
test_bia_create_process_benchmark     Mean: 89.12ms ± 8.45ms
```

### System Metrics

Monitor resource utilization:

- **CPU**: < 75% average (warning at 85%)
- **Memory**: < 80% usage (warning at 90%)
- **Disk I/O**: Monitor for bottlenecks
- **Network**: Check for bandwidth constraints

### Cache Metrics

Redis cache performance:

- **Hit Rate**: Target > 80%
- **Latency**: GET < 5ms, SET < 10ms
- **Memory**: Monitor for capacity

## 🔄 CI/CD Integration

### GitHub Actions Workflow

The performance testing workflow runs automatically:

- **On Pull Requests**: Light load test (5 min)
- **Nightly**: Medium load test (10 min)
- **Manual**: Any scenario via workflow_dispatch

### Workflow Features

- ✅ Automated test execution
- 📊 Performance report generation
- 💬 PR comments with results
- ❌ Fail build on regression (>10% degradation)
- 📦 Artifact upload (reports retained 30 days)

### Triggering Manual Runs

```bash
# Via GitHub UI: Actions → Performance Testing → Run workflow
# Select scenario: light, medium, heavy, or stress
```

### Performance Gates

The workflow fails if:
- P95 latency > 1000ms
- Error rate > 5%
- Performance degradation > 10% vs. baseline

## 🐛 Troubleshooting

### Services Not Starting

**Issue**: Services fail health checks

**Solution**:
```bash
# Check service logs
docker-compose logs bia-service
docker-compose logs compliance-service

# Restart services
docker-compose down
docker-compose up -d

# Wait for health
sleep 30
```

### High Failure Rates

**Issue**: > 5% request failures during tests

**Possible Causes**:
- Services not fully started
- Database connection issues
- Insufficient resources

**Solution**:
```bash
# Check service health
curl http://localhost:8012/health

# Check logs
docker-compose logs --tail=50

# Verify database connection
docker-compose exec postgres psql -U bcm_user -d bcm_platform -c "SELECT 1"
```

### Slow Performance

**Issue**: P95 > 1000ms

**Investigation**:
1. Check system resources: `python metrics_collector.py --duration 60`
2. Review database query performance
3. Check cache hit rate
4. Verify network latency

**Optimization**:
- Scale horizontally (add more service instances)
- Optimize database queries (add indexes)
- Increase cache size
- Review application code

### Memory Issues

**Issue**: Out of memory errors

**Solution**:
```bash
# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory: 8GB

# Reduce concurrent users
./run_load_test.sh light  # Start with light load

# Monitor memory usage
python metrics_collector.py --duration 60
```

### Connection Pool Exhausted

**Issue**: Database connection errors

**Solution**:
```bash
# Increase pool size in docker-compose.yml
# DB_POOL_SIZE: 20  # Increase from default
```

## 📚 Performance Targets Reference

See `performance_targets.yaml` for complete SLA definitions.

### Key Targets

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| P95 Latency | < 500ms | > 500ms | > 1000ms |
| P99 Latency | < 1000ms | > 1000ms | > 2000ms |
| Error Rate | < 1% | > 2% | > 5% |
| Throughput | > 50 req/s | < 50 req/s | < 20 req/s |
| CPU Usage | < 70% | > 75% | > 85% |
| Memory Usage | < 75% | > 80% | > 90% |
| Cache Hit Rate | > 80% | < 70% | < 50% |

## 🤝 Contributing

When adding new performance tests:

1. Add test scenarios to appropriate file
2. Update `performance_targets.yaml` with SLA
3. Document new scenarios in this README
4. Run full test suite before committing
5. Update CI/CD workflow if needed

## 📝 Best Practices

1. **Run baseline tests before major changes**
2. **Monitor trends over time** (save reports)
3. **Test with realistic data volumes**
4. **Use consistent test environments**
5. **Review reports regularly**
6. **Address regressions promptly**
7. **Document performance optimizations**

## 📞 Support

For issues or questions:
- Review this README
- Check troubleshooting section
- Review service logs: `docker-compose logs`
- Examine test reports in `reports/` directory

---

**Generated**: 2025-10-03
**Version**: 1.0.0
**ISO 22301:2019 Compliant**
**Powered by**: Locust, pytest-benchmark, Python
