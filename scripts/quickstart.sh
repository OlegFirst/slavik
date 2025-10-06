#!/bin/bash

# BCM Platform - Quick Start
# Запускает всю платформу за 3-5 минут

echo "🚀 BCM Platform - Quick Start"
echo "=============================="

# 1. Generate seed data
echo ""
echo "1️⃣  Generating seed data..."
python scripts/seed_data_generator.py \
    --bia-cases 50 \
    --risk-cases 30 \
    --planning-cases 20 \
    --output data/seed/

# 2. Start infrastructure
echo ""
echo "2️⃣  Starting infrastructure services..."
docker-compose up -d postgres redis neo4j

echo "   Waiting for databases to be ready..."
sleep 10

# 3. Run migrations
echo ""
echo "3️⃣  Running database migrations..."
docker-compose run --rm intelligent-core python scripts/migrate.py

# 4. Load seed data
echo ""
echo "4️⃣  Loading seed data..."
docker-compose run --rm seed-data

# 5. Start all services
echo ""
echo "5️⃣  Starting all services..."
docker-compose up -d

echo ""
echo "   Waiting for services to start..."
sleep 15

# 6. Run integration test
echo ""
echo "6️⃣  Running integration test..."
python scripts/end_to_end_integration.py

# 7. Show status
echo ""
echo "✅ Platform is running!"
echo ""
echo "📍 Access points:"
echo "   Main API:        http://localhost:8000"
echo "   AI Orchestrator: http://localhost:8001"
echo "   API Docs:        http://localhost:8000/docs"
echo "   Grafana:         http://localhost:3000 (admin/admin)"
echo "   MLflow:          http://localhost:5000"
echo "   Neo4j Browser:   http://localhost:7474 (neo4j/neo4j_password)"
echo ""
echo "📚 Next steps:"
echo "   - Open http://localhost:8000/docs for API documentation"
echo "   - Check docker-compose logs for service logs"
echo "   - Run 'docker-compose down' to stop all services"
