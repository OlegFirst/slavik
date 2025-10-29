#!/usr/bin/env python3
"""
Fix BCM modules dependencies and errors
"""

import os
import re
import json

BCM_MODULES_PATH = "/Users/MD/ISO-22301/core/odoo-18.0/addons"

# Correct dependency order (no circular references)
MODULE_DEPENDENCIES = {
    'bcm_base': ['base', 'mail'],
    'bcm_intelligent_base': ['base', 'mail'],
    'bcm_core': ['base', 'mail', 'bcm_base'],
    'bcm_context': ['base', 'bcm_core'],
    'bcm_config': ['base', 'bcm_core'],
    'bcm_governance': ['base', 'bcm_core'],
    'bcm_community': ['base', 'bcm_core'],
    'bcm_audit': ['base', 'bcm_core'],
    'bcm_clients': ['base', 'bcm_core'],
    'bcm_ai_control': ['base', 'web', 'mail', 'bcm_core', 'bcm_intelligent_base'],
    'bcm_digital_twin_core': ['base', 'bcm_core', 'bcm_intelligent_base'],
    'bcm_ai_consultant': ['base', 'bcm_core', 'bcm_ai_control'],
    'bcm_ai_twin_orchestrator': ['base', 'bcm_core', 'bcm_ai_control'],
    'bcm_corporate_twin': ['base', 'bcm_core', 'bcm_digital_twin_core'],
    'bcm_digital_copy_manager': ['base', 'bcm_core', 'bcm_digital_twin_core'],
    'bcm_bia': ['base', 'bcm_core'],
    'bcm_risk_management': ['base', 'bcm_core'],
    'bcm_incident': ['base', 'bcm_core'],
    'bcm_incident_management': ['base', 'bcm_core', 'bcm_incident'],
    'bcm_plans': ['base', 'web', 'mail', 'bcm_core'],
    'bcm_exercise': ['base', 'bcm_core', 'bcm_plans'],
    'bcm_scenario_hub': ['base', 'bcm_core', 'bcm_plans'],
    'bcm_kpi': ['base', 'bcm_core'],
    'bcm_training': ['base', 'bcm_core'],
    'bcm_templates': ['base', 'bcm_core'],
    'bcm_portal': ['base', 'portal', 'bcm_core'],
    'bcm_admin_website': ['base', 'website', 'bcm_core'],
    'bcm_reporting': ['base', 'bcm_core'],
}

def fix_manifest_dependencies(module_name):
    """Fix dependencies in __manifest__.py file"""
    manifest_path = os.path.join(BCM_MODULES_PATH, module_name, '__manifest__.py')

    if not os.path.exists(manifest_path):
        print(f"❌ {module_name}: manifest not found")
        return False

    with open(manifest_path, 'r') as f:
        content = f.read()

    # Get correct dependencies
    correct_deps = MODULE_DEPENDENCIES.get(module_name, ['base', 'bcm_core'])
    deps_str = str(correct_deps)

    # Replace depends line
    pattern = r"'depends'\s*:\s*\[.*?\]"
    replacement = f"'depends': {deps_str}"

    # Handle multiline depends
    pattern_multiline = r"'depends'\s*:\s*\[[\s\S]*?\]"

    if re.search(pattern_multiline, content):
        new_content = re.sub(pattern_multiline, replacement, content)
    else:
        new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        with open(manifest_path, 'w') as f:
            f.write(new_content)
        print(f"✅ {module_name}: dependencies fixed")
        return True
    else:
        print(f"ℹ️ {module_name}: no changes needed")
        return False

def fix_plan_id_issue():
    """Fix the plan_id KeyError issue"""
    bcm_models_path = os.path.join(BCM_MODULES_PATH, 'bcm_core', 'models', 'bcm_models.py')

    with open(bcm_models_path, 'r') as f:
        content = f.read()

    # Ensure plan_id field exists in BCMIncident
    if 'class BCMIncident' in content and "plan_id = fields.Many2one('bcm.plan'" not in content:
        # Find the BCMIncident class and add plan_id field
        lines = content.split('\n')
        new_lines = []
        in_incident_class = False
        field_added = False

        for i, line in enumerate(lines):
            new_lines.append(line)

            if 'class BCMIncident' in line:
                in_incident_class = True

            if in_incident_class and '# Relationships' in line and not field_added:
                # Add plan_id field after relationships comment
                new_lines.append("    plan_id = fields.Many2one('bcm.plan', string='Associated Plan', ondelete='set null')")
                field_added = True
                in_incident_class = False

        if field_added:
            with open(bcm_models_path, 'w') as f:
                f.write('\n'.join(new_lines))
            print("✅ Fixed plan_id field in BCMIncident")
            return True

    print("ℹ️ plan_id field already exists or not needed")
    return False

def main():
    print("🔧 Fixing BCM Module Issues")
    print("=" * 40)

    # Fix plan_id issue first
    print("\n1️⃣ Fixing plan_id KeyError...")
    fix_plan_id_issue()

    # Fix all module dependencies
    print("\n2️⃣ Fixing module dependencies...")
    fixed_count = 0

    for module_name in MODULE_DEPENDENCIES.keys():
        if fix_manifest_dependencies(module_name):
            fixed_count += 1

    print("\n" + "=" * 40)
    print(f"✅ Fixed {fixed_count} modules")
    print("\n🔄 Restart Odoo to apply changes:")
    print("docker-compose restart odoo")

if __name__ == "__main__":
    main()