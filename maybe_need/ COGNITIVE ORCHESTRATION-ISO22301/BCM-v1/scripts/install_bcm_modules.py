#!/usr/bin/env python3
"""
BCM Modules Installation Script
Installs all BCM modules in correct dependency order
"""

import subprocess
import sys
import time

# Module installation order based on dependencies
INSTALLATION_ORDER = [
    # Level 1: Base modules (no BCM dependencies)
    [
        'bcm_base',        # Foundation module
        'bcm_intelligent_base',  # Intelligent features base
    ],

    # Level 2: Core modules
    [
        'bcm_core',        # Core BCM functionality
        'bcm_context',     # Organization context
        'bcm_config',      # Configuration
    ],

    # Level 3: Infrastructure modules
    [
        'bcm_governance',  # Governance framework
        'bcm_community',   # Community features
        'bcm_audit',       # Audit functionality
        'bcm_clients',     # Client management
    ],

    # Level 4: AI and Digital Twin modules
    [
        'bcm_ai_control',  # AI control center
        'bcm_digital_twin_core',  # Digital twin core
        'bcm_ai_consultant',  # AI consultant
        'bcm_ai_twin_orchestrator',  # AI orchestrator
        'bcm_corporate_twin',  # Corporate digital twin
        'bcm_digital_copy_manager',  # Digital copy manager
    ],

    # Level 5: Business modules
    [
        'bcm_bia',         # Business Impact Analysis
        'bcm_risk_management',  # Risk management
        'bcm_incident',    # Basic incident management
        'bcm_incident_management',  # Advanced incident management
        'bcm_plans',       # BCM plans
        'bcm_exercise',    # Exercises
    ],

    # Level 6: Advanced features
    [
        'bcm_scenario_hub',  # Scenario management
        'bcm_kpi',         # KPI management
        'bcm_training',    # Training module
        'bcm_templates',   # Templates
    ],

    # Level 7: Portal and reporting
    [
        'bcm_portal',      # User portal
        'bcm_admin_website',  # Admin website
        'bcm_reporting',   # Reporting
    ]
]

def install_module(module_name, db_name='odoo'):
    """Install a single BCM module"""
    cmd = [
        'docker', 'exec', 'iso-22301-odoo-1',
        'odoo', '-c', '/etc/odoo/odoo.conf',
        '-d', db_name,
        '-i', module_name,
        '--stop-after-init',
        '--no-http'
    ]

    print(f"📦 Installing {module_name}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {module_name} installed successfully")
            return True
        else:
            print(f"❌ {module_name} failed: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ {module_name} timed out")
        return False
    except Exception as e:
        print(f"❌ {module_name} error: {str(e)}")
        return False

def main():
    print("🚀 BCM Modules Installation Script")
    print("=" * 40)

    # Check if Odoo is running
    check_cmd = ['docker', 'exec', 'iso-22301-odoo-1', 'pgrep', 'python']
    result = subprocess.run(check_cmd, capture_output=True)
    if result.returncode != 0:
        print("⚠️ Starting Odoo service...")
        subprocess.run(['docker', 'exec', '-d', 'iso-22301-odoo-1',
                       'odoo', '-c', '/etc/odoo/odoo.conf'])
        time.sleep(5)

    total_modules = sum(len(level) for level in INSTALLATION_ORDER)
    installed = 0
    failed = []

    for level_idx, level_modules in enumerate(INSTALLATION_ORDER, 1):
        print(f"\n📌 Level {level_idx}: Installing {len(level_modules)} modules")
        print("-" * 40)

        for module in level_modules:
            if install_module(module):
                installed += 1
            else:
                failed.append(module)
            time.sleep(2)  # Small delay between modules

    print("\n" + "=" * 40)
    print(f"📊 Installation Complete:")
    print(f"✅ Installed: {installed}/{total_modules}")
    if failed:
        print(f"❌ Failed: {', '.join(failed)}")

    # Restart Odoo after all modules installed
    print("\n🔄 Restarting Odoo...")
    subprocess.run(['docker-compose', 'restart', 'odoo'])

    return 0 if not failed else 1

if __name__ == "__main__":
    sys.exit(main())