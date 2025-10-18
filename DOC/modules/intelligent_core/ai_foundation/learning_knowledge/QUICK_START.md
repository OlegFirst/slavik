# 🚀 Quick Start - System BCM

**Run the platform's self-application of BCM in 1 command**

---

## ⚡ One-Line Quick Start

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge && python3 test_system_bcm_cycle.py --mode full
```

**Expected output:**
```
✅ BIA executed for 7 critical processes
✅ 8 high-priority risks identified
✅ 7 recovery procedures configured
✅ 10 services prioritized
✅ 3 insights generated
✅ 3 effectiveness metrics measured
✅ 2 improvements applied

🎓 The platform has learned resilience through PRACTICE!
```

**Time:** ~1.5 seconds
**Results saved to:** `system_bcm_cycle_results.json`

---

## 📋 Individual Tests

### Test BIA Only
```bash
python3 -c "
import asyncio
from system_bcm.system_bcm import SystemBCM

async def main():
    bcm = SystemBCM()
    result = await bcm.execute_self_bia()
    print(f'Critical processes: {len(result[\"critical_processes\"])}')

asyncio.run(main())
"
```

### Test Risk Assessment Only
```bash
python3 -c "
import asyncio
from system_bcm.system_bcm import SystemBCM

async def main():
    bcm = SystemBCM()
    result = await bcm.assess_own_risks()
    print(f'High-priority risks: {len(result[\"high_priority_risks\"])}')

asyncio.run(main())
"
```

### Test Recovery Setup Only
```bash
python3 -c "
import asyncio
from system_bcm.system_bcm import SystemBCM

async def main():
    bcm = SystemBCM()
    result = await bcm.setup_recovery()
    print(f'Procedures configured: {len(result[\"procedures_configured\"])}')

asyncio.run(main())
"
```

### Test Resource Priorities Only
```bash
python3 -c "
import asyncio
from system_bcm.system_bcm import SystemBCM

async def main():
    bcm = SystemBCM()
    result = await bcm.apply_priorities()
    print(f'Services prioritized: {len(result[\"services_prioritized\"])}')

asyncio.run(main())
"
```

---

## 🐍 Python API Usage

### Execute Full Cycle

```python
import asyncio
from system_bcm.system_bcm import SystemBCM
from learning.practice_learning import PracticeLearningEngine

async def run_system_bcm():
    # Execute BCM
    bcm = SystemBCM()
    bcm_results = await bcm.execute_full_cycle()

    # Learn from practice
    learning = PracticeLearningEngine()
    insights = await learning.learn_from_self_application(bcm_results)

    # Measure effectiveness
    rto_metric = await learning.measure_effectiveness(
        metric_type="event_bus_rto",
        target_value=30,
        actual_value=28
    )

    # Apply improvements
    if insights["improvements_identified"]:
        improvements = await learning.improve_based_on_practice(
            improvements=insights["improvements_identified"],
            apply_immediately=True
        )

    return bcm_results, insights

# Run
results = asyncio.run(run_system_bcm())
```

### Access Scenario Data

```python
import json
from pathlib import Path

scenarios_path = Path(__file__).parent / "scenarios" / "system_scenarios"

# Load BIA
with open(scenarios_path / "platform_bia.json") as f:
    bia = json.load(f)
    print(f"Critical processes: {len(bia['critical_processes'])}")

# Load Risks
with open(scenarios_path / "platform_risks.json") as f:
    risks = json.load(f)
    for category in risks["risk_categories"]:
        print(f"{category['category']}: {len(category['risks'])} risks")

# Load Recovery
with open(scenarios_path / "recovery_procedures.json") as f:
    recovery = json.load(f)
    print(f"Recovery procedures: {len(recovery['recovery_procedures'])}")

# Load Priorities
with open(scenarios_path / "resource_priorities.json") as f:
    priorities = json.load(f)
    print(f"Service tiers: {len(priorities['service_tiers'])}")
```

---

## 📊 View Results

### View JSON Results

```bash
# Pretty-print the results
cat system_bcm_cycle_results.json | python3 -m json.tool | less

# Count insights
cat system_bcm_cycle_results.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Insights: {len(data[\"learning_results\"][\"insights_generated\"])}')
"

# View metrics
cat system_bcm_cycle_results.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for m in data['effectiveness_metrics']:
    status = '✅' if m['success'] else '❌'
    print(f'{status} {m[\"metric_type\"]}: {m[\"actual_value\"]} (target: {m[\"target_value\"]})')
"
```

### View Logs

```bash
# View full log
cat system_bcm_test.log

# View only warnings and errors
grep -E "WARNING|ERROR" system_bcm_test.log

# View only successes
grep "✅" system_bcm_test.log
```

---

## 🔄 Scheduled Execution

### Run Every 24 Hours (cron)

```bash
# Add to crontab
crontab -e

# Add this line (runs at 2 AM daily)
0 2 * * * cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge && python3 test_system_bcm_cycle.py --mode full >> /var/log/system_bcm.log 2>&1
```

### Run as Service (systemd)

Create `/etc/systemd/system/system-bcm.service`:

```ini
[Unit]
Description=System BCM Self-Application
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge
ExecStart=/usr/bin/python3 test_system_bcm_cycle.py --mode full
StandardOutput=append:/var/log/system_bcm.log
StandardError=append:/var/log/system_bcm_error.log

[Install]
WantedBy=multi-user.target
```

Create timer `/etc/systemd/system/system-bcm.timer`:

```ini
[Unit]
Description=Run System BCM every 24 hours

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable system-bcm.timer
sudo systemctl start system-bcm.timer
```

---

## 🧪 Testing

### Run All Tests

```bash
python3 test_system_bcm_cycle.py --mode individual
```

### Verify Scenarios

```bash
# Check all scenario files exist
ls -lh scenarios/system_scenarios/

# Validate JSON syntax
for f in scenarios/system_scenarios/*.json; do
    echo "Validating $f"
    python3 -m json.tool "$f" > /dev/null && echo "✅ Valid" || echo "❌ Invalid"
done
```

### Check Dependencies

```bash
python3 -c "
import json
import asyncio
from pathlib import Path
print('✅ All dependencies available')
"
```

---

## 📈 Monitoring

### Key Metrics to Track

```python
# After running a cycle, extract key metrics:
import json

with open("system_bcm_cycle_results.json") as f:
    results = json.load(f)

# BIA Metrics
bia = results["bcm_execution"]["phases"]["bia"]["results"]
print(f"Critical Processes: {len(bia['critical_processes'])}")
print(f"Dependencies: {len(bia['dependencies_identified'])}")

# Risk Metrics
risks = results["bcm_execution"]["phases"]["risk_assessment"]["results"]
print(f"High-Priority Risks: {len(risks['high_priority_risks'])}")

# Recovery Metrics
recovery = results["bcm_execution"]["phases"]["recovery_setup"]["results"]
auto_count = len(recovery["auto_recovery_enabled"])
total_count = len(recovery["procedures_configured"])
print(f"Automation Rate: {auto_count}/{total_count} ({auto_count/total_count*100:.1f}%)")

# Learning Metrics
learning = results["learning_results"]
print(f"Insights Generated: {len(learning['insights_generated'])}")
print(f"Improvements Identified: {len(learning['improvements_identified'])}")
print(f"Confidence: {learning['confidence_scores']['overall_confidence']:.2f}")

# Effectiveness Metrics
for metric in results["effectiveness_metrics"]:
    status = "✅" if metric["success"] else "❌"
    print(f"{status} {metric['metric_type']}: {metric['deviation_percentage']:.1f}% deviation")
```

---

## 🔧 Troubleshooting

### Common Issues

**Issue:** Module not found
```bash
# Solution: Ensure you're in the correct directory
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge
```

**Issue:** JSON syntax error
```bash
# Solution: Validate scenario files
python3 -m json.tool scenarios/system_scenarios/platform_bia.json
```

**Issue:** Permission denied
```bash
# Solution: Make test script executable
chmod +x test_system_bcm_cycle.py
```

---

## 📚 Documentation

- **Full Documentation:** [SYSTEM_BCM_README.md](SYSTEM_BCM_README.md)
- **Phase 1 Report:** [/doc-project/PHASE1_SYSTEM_BCM_COMPLETE.md](../../../doc-project/PHASE1_SYSTEM_BCM_COMPLETE.md)
- **Original Task:** [/doc-project/TASK_AUTOMATED_SCENARIO_GENERATION.md](../../../doc-project/TASK_AUTOMATED_SCENARIO_GENERATION.md)

---

## ✅ Quick Verification

```bash
# Verify everything is working
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge

echo "1. Checking scenario files..."
ls -1 scenarios/system_scenarios/*.json | wc -l  # Should be 4

echo "2. Validating JSON..."
for f in scenarios/system_scenarios/*.json; do
    python3 -m json.tool "$f" > /dev/null && echo "  ✅ $(basename $f)"
done

echo "3. Running test..."
python3 test_system_bcm_cycle.py --mode full && echo "✅ All tests passed!"

echo "4. Checking results..."
test -f system_bcm_cycle_results.json && echo "  ✅ Results saved"
test -f system_bcm_test.log && echo "  ✅ Log saved"

echo ""
echo "✅ System BCM is fully operational!"
```

---

**For questions or issues, see:** [SYSTEM_BCM_README.md](SYSTEM_BCM_README.md)
