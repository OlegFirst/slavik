# BCM Platform Testing Suite

## 🧪 Test Categories

### Integration Tests (`tests/integration/`)

**Continuous testing scripts for CI/CD and development workflows**

- `test-docker-ai.sh` - Complete Docker AI platform testing
- `test-ai-agents.sh` - AI agent orchestration testing

### Unit Tests (`tests/unit/`)
- Service-specific unit tests
- MCP tool validation
- API endpoint testing

### End-to-End Tests (`tests/e2e/`)
- Full user journey testing
- Cross-service integration
- Performance validation

### Performance Tests (`tests/performance/`)
- Load testing
- Stress testing
- GPU acceleration benchmarks

## 🚀 Running Tests

### Quick Test
```bash
# Test entire Docker AI platform
./tests/integration/test-docker-ai.sh
```

### Specific Tests
```bash
# AI agents only
./tests/integration/test-ai-agents.sh

# MCP tools
cd docker-ai/mcp-server && python -m pytest

# Performance
./tests/performance/load-test.sh
```

## ✅ Test Coverage

- ✅ Docker AI infrastructure
- ✅ MCP protocol integration
- ✅ AI agent orchestration
- ✅ Local LLM inference
- ✅ BCM tool integration
- ✅ Health monitoring
- 🔄 Performance benchmarks
- 🔄 Security validation

These tests are designed for continuous integration and regular development validation.