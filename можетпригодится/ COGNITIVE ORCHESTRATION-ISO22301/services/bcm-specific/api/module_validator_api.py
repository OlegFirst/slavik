#!/usr/bin/env python3
"""
API для валидатора модулей BCM
Предоставляет REST API для валидации и управления модулями
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
import json

# Добавляем путь к валидатору (относительный путь для контейнера)
sys.path.insert(0, '/app')
from validate_modules import ModuleValidator

app = Flask(__name__)
CORS(app)

@app.route('/api/modules/validate', methods=['GET'])
def validate_all_modules():
    """Запустить валидацию всех модулей"""
    try:
        validator = ModuleValidator()

        # Собираем информацию о модулях
        modules_info = []
        bcm_modules = validator.get_all_modules()

        for module_path in bcm_modules:
            module_name = os.path.basename(module_path)

            # Сбрасываем ошибки для каждого модуля
            validator.errors = []
            validator.warnings = []

            # Валидируем модуль
            validator.validate_module(module_path)

            # Получаем информацию о модуле
            module_info = validator.get_module_info(module_path)
            module_info.update({
                'name': module_name,
                'path': module_path,
                'errors': validator.errors.copy(),
                'warnings': validator.warnings.copy(),
                'status': 'error' if validator.errors else ('warning' if validator.warnings else 'success')
            })

            modules_info.append(module_info)

        return jsonify({
            'success': True,
            'modules': modules_info,
            'total_errors': sum(len(m['errors']) for m in modules_info),
            'total_warnings': sum(len(m['warnings']) for m in modules_info)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/modules/list', methods=['GET'])
def list_modules():
    """Получить список всех модулей с базовой информацией"""
    try:
        validator = ModuleValidator()
        modules = []

        bcm_modules = validator.get_all_modules()

        for module_path in bcm_modules:
            module_name = os.path.basename(module_path)
            module_info = validator.get_module_info(module_path)

            modules.append({
                'name': module_name,
                'path': module_path,
                'version': module_info.get('version', 'N/A'),
                'category': module_info.get('category', 'N/A'),
                'installed': module_info.get('installed', False),
                'dependencies': module_info.get('dependencies', []),
                'summary': module_info.get('summary', '')
            })

        return jsonify({
            'success': True,
            'modules': modules,
            'total': len(modules)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/modules/<module_name>', methods=['GET'])
def get_module_details(module_name):
    """Получить детальную информацию о модуле"""
    try:
        validator = ModuleValidator()
        module_path = os.path.join(validator.modules_path, module_name)

        if not os.path.exists(module_path):
            return jsonify({
                'success': False,
                'error': f'Module {module_name} not found'
            }), 404

        # Валидируем модуль
        validator.errors = []
        validator.warnings = []
        validator.validate_module(module_path)

        # Получаем полную информацию
        module_info = validator.get_module_info(module_path)

        # Получаем связи и зависимости
        dependencies_info = validator.get_dependencies_info(module_path)

        return jsonify({
            'success': True,
            'module': {
                'name': module_name,
                'info': module_info,
                'errors': validator.errors,
                'warnings': validator.warnings,
                'dependencies': dependencies_info,
                'status': 'error' if validator.errors else ('warning' if validator.warnings else 'success')
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/modules/dependencies', methods=['GET'])
def get_dependencies_graph():
    """Получить граф зависимостей всех модулей"""
    try:
        validator = ModuleValidator()
        bcm_modules = validator.get_all_modules()

        nodes = []
        edges = []

        for module_path in bcm_modules:
            module_name = os.path.basename(module_path)
            module_info = validator.get_module_info(module_path)

            # Добавляем узел
            nodes.append({
                'id': module_name,
                'label': module_name,
                'category': module_info.get('category', 'Other'),
                'version': module_info.get('version', 'N/A')
            })

            # Добавляем связи
            for dep in module_info.get('dependencies', []):
                if dep.startswith('bcm_'):
                    edges.append({
                        'source': module_name,
                        'target': dep,
                        'type': 'depends'
                    })

        return jsonify({
            'success': True,
            'graph': {
                'nodes': nodes,
                'edges': edges
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/modules/fix/<module_name>', methods=['POST'])
def fix_module_issues(module_name):
    """Автоматически исправить проблемы в модуле"""
    try:
        validator = ModuleValidator()
        module_path = os.path.join(validator.modules_path, module_name)

        if not os.path.exists(module_path):
            return jsonify({
                'success': False,
                'error': f'Module {module_name} not found'
            }), 404

        # Запускаем автоматическое исправление
        fixed_issues = validator.auto_fix_module(module_path)

        return jsonify({
            'success': True,
            'fixed_issues': fixed_issues
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)