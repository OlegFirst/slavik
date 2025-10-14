# ACE Service - Quick Start Guide

**5-Minute Setup** | **Production Ready** | **Supabase Integrated**

---

## ✅ Prerequisites Check

```bash
# 1. Check .env file exists
ls -la /Users/MD/AI-Platform-ISO/.env

# 2. Check DATABASE_URL is set
grep DATABASE_URL /Users/MD/AI-Platform-ISO/.env

# Expected: DATABASE_URL=postgresql://...supabase.com.../postgres
```

---

## 🚀 Three-Step Deployment

### Step 1: Apply Database Schema (✅ DONE)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/ace-service
bash setup_ace_in_supabase.sh
```

**Expected Output:**
```
✅ ACE schema applied successfully!
📊 Checking tables...
   ace_playbooks
   ace_trajectory_log
   ace_playbook_history
   ace_playbook_stats
   ace_playbook_evolution
✅ ACE Setup Complete!
```

### Step 2: Start ACE Service

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/ace-service

# Option A: Background mode (recommended)
bash start_ace_service.sh

# Option B: Foreground mode (with logs)
bash start_ace_service.sh --foreground
```

**Expected Output:**
```
🚀 Starting ACE Service...
✅ Loaded environment from .env
📊 Database: Connected to Supabase
🌐 Service will run on: http://localhost:8050
✅ ACE Service started (PID: 12345)
✅ Service is running!
```

### Step 3: Verify Service

```bash
# Health check
curl http://localhost:8050/health
# Expected: {"status":"healthy","database":"connected"}

# Statistics
curl http://localhost:8050/stats
# Expected: {"total_playbooks":2,"total_trajectories":0,...}

# Run integration tests
python3 test_ace_integration.py
# Expected: 🎉 ALL TESTS PASSED!
```

---

## 🔧 Service Management

### Start Service

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/ace-service
bash start_ace_service.sh
```

### Stop Service

```bash
# Find process
lsof -ti:8050

# Kill it
lsof -ti:8050 | xargs kill -9
```

### Check Status

```bash
# Is it running?
lsof -i :8050

# View logs
tail -f /Users/MD/AI-Platform-ISO/infrastructure/ace-service/ace_service.log
```

### Restart Service

```bash
# Kill old instance
lsof -ti:8050 | xargs kill -9

# Start new instance
bash start_ace_service.sh
```

---

## 🔌 Integrate with Your Module

### 1. Add Import

```python
from infrastructure.ace_service.ace_client import ACEClient
```

### 2. Initialize Client

```python
class YourModule:
    def __init__(self):
        self.ace = ACEClient(base_url="http://localhost:8050")
```

### 3. Use ACE Workflow

**Option A: Convenience Function (Recommended)**

```python
async def your_task(self, input_data):
    # Define your task logic
    async def execute_task(context, **kwargs):
        # Use enhanced context to perform your task
        result = await self._do_work(context)
        return {
            "success": True,
            "output": result,
            "effectiveness": 0.85  # Your metric
        }

    # ACE handles everything: Generate → Execute → Reflect → Curate
    result = await self.ace.ace_workflow(
        task_type="your_module_task_name",
        base_context={"input": input_data},
        execute_task_fn=execute_task,
        module_name="your_module_name"
    )

    return result
```

**Option B: Explicit Control**

```python
async def your_task(self, input_data):
    task_type = "your_module_task_name"

    # 1. Generator: Get enhanced context
    enhanced_context = await self.ace.generate_context(
        task_type=task_type,
        base_context={"input": input_data},
        module_name="your_module_name"
    )

    # 2. Execute with enhanced context
    result = await self._do_work(enhanced_context)

    # 3. Reflector: Analyze what happened
    trajectory = {
        "input_context": enhanced_context,
        "output_result": result,
        "success": result["success"],
        "effectiveness": result["effectiveness"]
    }
    insights = await self.ace.reflect_on_trajectory(
        task_type=task_type,
        trajectory=trajectory,
        module_name="your_module_name"
    )

    # 4. Curator: Update playbook
    await self.ace.curate_playbook(
        task_type=task_type,
        insights=insights,
        module_name="your_module_name"
    )

    return result
```

---

## 📊 Monitor Your Playbooks

### Check Supabase

```bash
# Connect to Supabase
export DATABASE_URL="your_supabase_url"
psql "$DATABASE_URL"
```

```sql
-- View all playbooks
SELECT task_type, version, usage_count, success_rate, avg_effectiveness
FROM ace_playbooks
ORDER BY task_type, version;

-- View recent trajectories
SELECT task_type, success, effectiveness, created_at
FROM ace_trajectory_log
ORDER BY created_at DESC
LIMIT 10;

-- View playbook evolution
SELECT * FROM ace_playbook_evolution
WHERE task_type = 'your_task_type';

-- View statistics
SELECT * FROM ace_playbook_stats
ORDER BY avg_effectiveness DESC;
```

### Check Service API

```bash
# Get analytics
curl http://localhost:8050/api/v1/ace/analytics

# List playbooks for a module
curl http://localhost:8050/api/v1/ace/playbooks?module_name=your_module

# Get service stats
curl http://localhost:8050/stats
```

---

## 🎯 Module Integration Checklist

- [ ] ACE Service is running (`curl http://localhost:8050/health`)
- [ ] Import ACEClient in your module
- [ ] Initialize client in `__init__`
- [ ] Wrap task execution with `ace_workflow()` or explicit workflow
- [ ] Test with a few executions
- [ ] Check playbook was created in Supabase
- [ ] Monitor effectiveness improvements over time

---

## 🧪 Test Integration

```python
# test_your_module_with_ace.py

import asyncio
from your_module import YourModule

async def test():
    module = YourModule()

    # Run task multiple times
    for i in range(10):
        result = await module.your_task({"test": f"data_{i}"})
        print(f"Run {i+1}: success={result['success']}, eff={result.get('effectiveness', 0):.2f}")

    # Check playbook in Supabase
    # You should see version increasing and effectiveness improving

asyncio.run(test())
```

---

## 📈 Expected Improvements

| Runs | Expected Behavior |
|------|------------------|
| 1-10 | Playbook learning, version 1-2 |
| 10-50 | Patterns emerging, effectiveness rising |
| 50-100 | Stable playbook, +8-15% improvement |
| 100+ | Continuous refinement, high performance |

---

## ⚠️ Troubleshooting

### Service won't start

```bash
# Check if port is already in use
lsof -i :8050

# If yes, kill it
lsof -ti:8050 | xargs kill -9

# Check DATABASE_URL
echo $DATABASE_URL

# Start with logs visible
bash start_ace_service.sh --foreground
```

### Client can't connect

```python
# Test connection
import aiohttp
import asyncio

async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8050/health') as resp:
            print(await resp.json())

asyncio.run(test())
```

### Playbook not updating

```sql
-- Check if trajectories are being logged
SELECT COUNT(*) FROM ace_trajectory_log
WHERE task_type = 'your_task_type';

-- Check playbook versions
SELECT version, updated_at FROM ace_playbooks
WHERE task_type = 'your_task_type'
ORDER BY version;
```

### Need to reset playbooks

```sql
-- Delete all playbooks for a task type
DELETE FROM ace_playbooks
WHERE task_type = 'your_task_type';

-- Or reset all ACE data
DELETE FROM ace_trajectory_log;
DELETE FROM ace_playbook_history;
DELETE FROM ace_playbooks;
```

---

## 📚 Full Documentation

- **Complete Integration Guide:** `INTEGRATION_GUIDE.md`
- **Architecture:** `/doc-project/ACE_CENTRALIZED_ARCHITECTURE.md`
- **Summary:** `/doc-project/ACE_INTEGRATION_COMPLETE.md`
- **Service README:** `README.md`

---

## 💡 Quick Tips

1. **Start Simple:** Use `ace_workflow()` convenience function
2. **Monitor Early:** Check Supabase after first few runs
3. **Be Patient:** Improvements appear after 10-20 executions
4. **Measure Baseline:** Run without ACE first, then compare
5. **Use Good Task Types:** Be specific (e.g., `scenario_L1_BIA` not just `scenario`)
6. **Track Effectiveness:** Return meaningful 0-1 scores
7. **Check Logs:** View `ace_service.log` for debugging

---

## 🎉 You're Ready!

ACE Service is production-ready. Start integrating with your modules and watch performance improve over time!

**Questions?** Check the full documentation in `INTEGRATION_GUIDE.md`

**Issues?** Review troubleshooting section above

**Need Examples?** See `test_ace_integration.py`

---

**Last Updated:** October 14, 2025
**Status:** ✅ Production Ready
