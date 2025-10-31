# AnyLogic Pypeline Adapter for NASH 4.0 Digital Twin

## Overview
This adapter integrates AnyLogic's powerful hybrid simulation capabilities with the NASH 4.0 Digital Twin platform, providing:

- **Hybrid Simulation**: Combine agent-based, system dynamics, and discrete event paradigms
- **ML/AI Integration**: Leverage Python's ML ecosystem through Pypeline
- **Advanced Optimization**: Genetic algorithms, linear programming, and more
- **Professional Visualization**: 3D animations and interactive dashboards

## Architecture

```
┌─────────────────────────────────────────────────┐
│           NASH 4.0 Digital Twin Platform        │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│         AnyLogic Pypeline Adapter API           │
│            (FastAPI on port 7004)               │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌──────────────────┐ ┌──────────────────┐
│  AnyLogic Model  │ │  Python Scripts  │
│  (Java-based)    │ │  (ML/Analytics)  │
└──────────────────┘ └──────────────────┘
         │                   │
         └─────────┬─────────┘
                   ▼
┌─────────────────────────────────────────────────┐
│           Pypeline Bridge (JSON)                │
└─────────────────────────────────────────────────┘
```

## Features

### Simulation Paradigms
1. **Agent-Based Modeling**: Individual behaviors and interactions
2. **System Dynamics**: Feedback loops and stock-flow relationships
3. **Discrete Event**: Process flows and resource utilization
4. **Hybrid Models**: Combine multiple paradigms seamlessly

### ML/AI Capabilities
- Demand forecasting with time series models
- Behavior prediction using neural networks
- Resource optimization with genetic algorithms
- Anomaly detection for early warning systems

### NPO-Specific Features
- Donor behavior prediction
- Program outcome forecasting
- Resource allocation optimization
- Impact measurement and validation
- Stakeholder network analysis

## Quick Start

### Using Docker

```bash
# Build the adapter
cd external-adapters/anylogic-adapter
docker build -f docker/Dockerfile -t anylogic-adapter:latest .

# Run standalone
docker run -p 7004:7004 anylogic-adapter:latest

# Or use with docker-compose
docker-compose up anylogic-adapter
```

### Local Development

```bash
# Install dependencies
pip install -r docker/requirements.txt

# Run the API server
cd api_server
python app.py
```

## API Usage

### Run Hybrid Simulation

```bash
curl -X POST http://localhost:7004/run \
  -H "Content-Type: application/json" \
  -d '{
    "experiment": "anylogic_hybrid",
    "params": {
      "model_type": "hybrid",
      "organization": {
        "name": "Example NPO",
        "budget": 500000,
        "staff": 50
      },
      "scenario": "optimization",
      "ml_integration": true,
      "optimization_goal": "impact",
      "simulation_time": 365,
      "replications": 10
    },
    "monte_carlo_runs": 100
  }'
```

### Check Capabilities

```bash
curl http://localhost:7004/capabilities
```

### Health Check

```bash
curl http://localhost:7004/health
```

## Integration with NASH 4.0

The adapter is automatically registered as the 30th experiment type in the Digital Twin platform:

```javascript
// In simulation-router.js
anylogic_hybrid: 'http://localhost:7004/run'
```

Access through the UI:
1. Navigate to Impact Dashboard
2. Click "Run Simulation"
3. Select "AnyLogic Hybrid Simulation"
4. Configure parameters
5. View results with advanced visualizations

## Python ML Integration Examples

### Donor Behavior Prediction
```python
from enhanced_analytics import process_for_anylogic

donor_profile = {
    'previous_donor': True,
    'engagement_score': 0.8,
    'giving_capacity': 5000
}

prediction = process_for_anylogic('predict_donor', donor_profile)
print(f"Donation probability: {prediction['donation_probability']}")
print(f"Predicted amount: ${prediction['predicted_amount']}")
```

### Resource Optimization
```python
resources = {'budget': 100000, 'staff_hours': 2000}
programs = [
    {'name': 'Education', 'cost': 30000, 'staff_hours': 500, 'impact_score': 85},
    {'name': 'Healthcare', 'cost': 40000, 'staff_hours': 600, 'impact_score': 90}
]

optimization = process_for_anylogic('optimize_resources', {
    'resources': resources,
    'programs': programs
})
```

## AnyLogic Model Development

### Prerequisites
- AnyLogic Professional or University Edition
- Pypeline library JAR file
- Python 3.8+ installed

### Model Structure
```
NPO_Digital_Twin.alp
├── Main Agent
│   ├── Python Communicator
│   ├── Organization Agent
│   └── Simulation Controller
├── Agent Types
│   ├── Donor Agent
│   ├── Volunteer Agent
│   ├── Program Agent
│   └── Beneficiary Agent
├── System Dynamics
│   ├── Financial Flows
│   ├── Impact Accumulation
│   └── Resource Dynamics
└── Process Modeling
    ├── Donation Process
    ├── Service Delivery
    └── Volunteer Management
```

### Pypeline Configuration
1. Add Pypeline JAR to model dependencies
2. Create Python Communicator object
3. Configure Python path and scripts location
4. Use `run()` and `runResults()` methods for data exchange

## Advanced Features

### Real-time Optimization
The adapter supports real-time optimization during simulation:
- Dynamic resource reallocation
- Adaptive policy adjustments
- Learning from simulation outcomes

### Visualization Export
Generate professional visualizations:
- 3D organizational structure
- Process flow animations
- Interactive dashboards
- Geographic impact maps

### Scenario Comparison
Compare multiple scenarios simultaneously:
- Baseline vs optimized
- Different intervention strategies
- Sensitivity analysis
- Monte Carlo confidence intervals

## Performance Considerations

- **Overhead**: Pypeline adds ~10-20ms per Python call
- **Optimization**: Batch Python calls when possible
- **Caching**: Results are cached for repeated queries
- **Scaling**: Use async processing for long-running simulations

## Troubleshooting

### Common Issues

1. **Python not found**: Ensure Python is in system PATH
2. **Module import errors**: Check Python script paths in AnyLogic
3. **Performance issues**: Reduce Python call frequency
4. **Memory errors**: Increase JVM heap size in AnyLogic

### Debug Mode
Enable debug logging:
```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License and Support

This adapter is part of the NASH 4.0 Digital Twin platform.
For AnyLogic licensing, visit: https://www.anylogic.com/

## Contributing

Contributions welcome! Please ensure:
- No emojis in code or documentation
- Professional naming conventions
- Comprehensive error handling
- Full test coverage

## Resources

- [AnyLogic Pypeline Documentation](https://www.anylogic.com/features/artificial-intelligence/pypeline/)
- [NASH 4.0 Digital Twin Docs](../../../docs/README.md)
- [Python ML Examples](anylogic-model/python_scripts/)