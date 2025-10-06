# Security Report

**Status:** FAIL

## Summary

- Secrets found: **3**
- Vulnerabilities found: **2**
- High risk issues: **1**

## Secrets Found

- `src/index.js:6` — Secret Key/Token
- `src/risk_assessment.py:8` — Password
- `src/app.py:9` — API Key

## Vulnerabilities

- `src/index.js:23` — eval() usage (code injection risk)
- `src/incident_manager.py:17` — pickle usage (deserialization risk)

