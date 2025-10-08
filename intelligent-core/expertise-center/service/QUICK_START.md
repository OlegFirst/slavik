# Expertise Center - Quick Start Guide

## 🚀 Start Service (3 options)

### Option 1: Local Development (Fastest)

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/expertise-center/service

# Install dependencies
pip install -r requirements.txt

# Configure (optional)
cp .env.example .env

# Start service
python main.py
```

Service: http://localhost:8035

### Option 2: Docker Compose (Recommended)

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/expertise-center/service

# Start service
docker-compose up expertise-center

# Start with dependencies
docker-compose --profile with-dependencies up
```

Service: http://localhost:8035

### Option 3: Docker Build

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/expertise-center

# Build image
docker build -t expertise-center:latest -f service/Dockerfile ../..

# Run container
docker run -d \
  --name expertise-center \
  -p 8035:8035 \
  -e AI_FOUNDATION_URL=http://localhost:8040 \
  expertise-center:latest

# View logs
docker logs -f expertise-center
```

Service: http://localhost:8035

---

## ✅ Verify Installation

```bash
# 1. Health check
curl http://localhost:8035/health

# Expected: {"status":"healthy","service":"expertise-center-service","version":"1.0.0"}

# 2. Service info
curl http://localhost:8035/expertise/info

# Expected: List of 12 tactical assistants + 10 analyzers

# 3. List experts
curl http://localhost:8035/expertise/experts

# Expected: Array of expert objects
```

---

## 🧪 Test API

### Query BIA Specialist

```bash
curl -X POST http://localhost:8035/expertise/tactical/bia/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are critical processes for healthcare organization?",
    "context": {"industry": "healthcare", "size": "medium"}
  }'
```

### Query Risk Analyst

```bash
curl -X POST http://localhost:8035/expertise/tactical/risk/assess \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Assess ransomware risk",
    "context": {"industry": "finance"}
  }'
```

### Run Compliance Analyzer

```bash
curl -X POST http://localhost:8035/expertise/analyzers/compliance/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "standard": "ISO22301",
      "current_practices": ["BIA conducted", "Plans documented"]
    },
    "context": {"industry": "finance"}
  }'
```

### Generic Expert Query

```bash
curl -X POST http://localhost:8035/expertise/query \
  -H "Content-Type: application/json" \
  -d '{
    "expert_type": "compliance_copilot",
    "query": "Check ISO 22301 compliance for clause 8.2",
    "context": {"standard": "iso22301"}
  }'
```

---

## 📖 Documentation

- **Swagger UI:** http://localhost:8035/docs
- **ReDoc:** http://localhost:8035/redoc
- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **Full Report:** `../INFRASTRUCTURE_COMPLETE.md`

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
cp .env.example .env
```

Key variables:

```bash
# Service
EXPERTISE_CENTER_PORT=8035
LOG_LEVEL=INFO

# AI Foundation
AI_FOUNDATION_URL=http://localhost:8040

# API Keys (for AI models)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

---

## 📊 Monitoring

### Prometheus Metrics

```bash
curl http://localhost:8035/metrics
```

### Health Status

```bash
# Basic health
curl http://localhost:8035/health

# Detailed info
curl http://localhost:8035/expertise/info
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Change port in .env
EXPERTISE_CENTER_PORT=8036

# Or use environment variable
EXPERTISE_CENTER_PORT=8036 python main.py
```

### Import Errors

```bash
# Set PYTHONPATH
export PYTHONPATH=/Users/MD/AI-Platform-ISO/intelligent-core:$PYTHONPATH

# Or add to .env
echo "PYTHONPATH=/Users/MD/AI-Platform-ISO/intelligent-core" >> .env
```

### AI Foundation Not Available

```bash
# Check AI Foundation is running
curl http://localhost:8040/health

# Update URL in .env
AI_FOUNDATION_URL=http://ai-foundation:8040
```

---

## 📚 Available Endpoints

### Tactical Assistants (12)

```
POST /expertise/tactical/bia/analyze           - BIA Specialist
POST /expertise/tactical/risk/assess           - Risk Analyst
POST /expertise/tactical/compliance/check      - Compliance Copilot
POST /expertise/tactical/incident/advise       - Incident Advisor
POST /expertise/tactical/plan/generate         - Plan Generator
POST /expertise/tactical/exercise/design       - Exercise Designer
POST /expertise/tactical/project/manage        - Project Manager
POST /expertise/tactical/documents/create      - Documents Specialist
POST /expertise/tactical/governance/analyze    - Governance Specialist
POST /expertise/tactical/learning/design       - Learning Specialist
POST /expertise/tactical/validation/validate   - Validation Specialist
POST /expertise/tactical/community/engage      - Community Specialist
```

### Strategic Analyzers (10)

```
POST /expertise/analyzers/compliance/analyze   - Compliance Analyzer
POST /expertise/analyzers/risk/analyze         - Risk Analyzer
POST /expertise/analyzers/governance/analyze   - Governance Analyzer
POST /expertise/analyzers/lifecycle/analyze    - Lifecycle Analyzer
POST /expertise/analyzers/learning/analyze     - Learning Analyzer
POST /expertise/analyzers/performance/analyze  - Performance Analyzer
POST /expertise/analyzers/emergency/analyze    - Emergency Analyzer
POST /expertise/analyzers/impact/analyze       - Impact Analyzer
POST /expertise/analyzers/plan/analyze         - Plan Analyzer
POST /expertise/analyzers/scenario/analyze     - Scenario Analyzer
```

---

## 🎯 Next Steps

1. **Start Service** (see options above)
2. **Test API** (curl examples above)
3. **View Docs** (http://localhost:8035/docs)
4. **Read Full Guide** (`DEPLOYMENT_GUIDE.md`)
5. **Integrate with Temporal** (see workflow examples in DEPLOYMENT_GUIDE.md)

---

**Need Help?** See `DEPLOYMENT_GUIDE.md` for detailed instructions.

**Status:** Production Ready
**Port:** 8035
**Version:** 1.0.0
