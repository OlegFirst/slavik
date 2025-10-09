# Code Quality Report

**Status:** OK

## Summary

- High complexity functions: **1**
- Duplicate blocks: **11**
- Tech debt items: **9**

## High Complexity Functions (Top 10)

- `src/app.py:38` — **health_check()** (complexity: 11)

## Top Duplicate Code Blocks

- Found **2** times: `def test_risk_assessment():
    """Test risk assessment"""
    assessor = RiskAs...`
- Found **2** times: `res.json({
        status: 'operational',
        incidents: 0,
        uptime: ...`
- Found **2** times: `status: 'operational',
        incidents: 0,
        uptime: '99.9%'
    });
});...`
- Found **2** times: `incidents: 0,
        uptime: '99.9%'
    });
});...`
- Found **2** times: `def __init__(self):
        # TODO: Load from config
        self.password = "ad...`

## Technical Debt (9 items)

- **TODO**: 5 items
- **FIXME**: 2 items
- **HACK**: 1 items
- **XXX**: 1 items

### Recent Items (10)

- `src/index.js:5` — TODO: // TODO: Move to environment variables
- `src/index.js:11` — FIXME: // FIXME: Add authentication
- `src/risk_assessment.py:7` — TODO: # TODO: Load from config
- `src/risk_assessment.py:31` — TODO: # TODO: Implement proper FAIR methodology
- `src/risk_assessment.py:59` — TODO: # TODO: Implement proper FAIR methodology
- `src/app.py:8` — TODO: # TODO: Move this to config file
- `src/app.py:20` — FIXME: # FIXME: Add proper validation
- `src/app.py:30` — HACK: # HACK: Quick fix for demo, refactor later
- `src/app.py:70` — XXX: # XXX: Debug mode in production?
