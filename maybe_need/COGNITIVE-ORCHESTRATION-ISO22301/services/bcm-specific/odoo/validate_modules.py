#!/usr/bin/env python3
"""
Скрипт валидации BCM модулей для Odoo 18
Проверяет модули на распространенные ошибки перед установкой
"""

import os
import glob
import xml.etree.ElementTree as ET
import csv
import re
import json
from pathlib import Path

class ModuleValidator:
    def __init__(self, modules_path="/Users/MD/ISO-22301/core/odoo-18.0/addons"):
        self.modules_path = modules_path
        self.errors = []
        self.warnings = []

    def validate_all_modules(self):
        """Проверить все BCM модули"""
        print("🔍 Начинаем валидацию BCM модулей...\n")

        bcm_modules = glob.glob(f"{self.modules_path}/bcm_*")

        for module_path in bcm_modules:
            if os.path.isdir(module_path):
                module_name = os.path.basename(module_path)
                print(f"📦 Проверяем модуль: {module_name}")
                self.validate_module(module_path)
                print()

        self.print_summary()

    def validate_module(self, module_path):
        """Проверить один модуль"""
        module_name = os.path.basename(module_path)

        # 1. Проверка манифеста
        self.check_manifest(module_path, module_name)

        # 2. Проверка файлов безопасности
        self.check_security_files(module_path, module_name)

        # 3. Проверка моделей
        models = self.check_models(module_path, module_name)

        # 4. Проверка представлений
        self.check_views(module_path, module_name, models)

        # 5. Проверка импортов
        self.check_imports(module_path, module_name)

        # 6. Проверка JavaScript/CSS
        self.check_assets(module_path, module_name)

        # 7. Проверка связей и зависимостей
        self.check_dependencies(module_path, module_name)

    def check_manifest(self, module_path, module_name):
        """Проверка __manifest__.py"""
        manifest_path = os.path.join(module_path, "__manifest__.py")

        if not os.path.exists(manifest_path):
            self.errors.append(f"{module_name}: Отсутствует __manifest__.py")
            return

        try:
            with open(manifest_path, 'r') as f:
                content = f.read()

            # Проверка на эмодзи
            if re.search(r'[\U0001F300-\U0001F9FF]', content):
                self.warnings.append(f"{module_name}: Манифест содержит эмодзи")

            # Загрузка манифеста
            local_vars = {}
            exec(content, {}, local_vars)

            # Проверка зависимостей
            depends = local_vars.get('depends', [])
            for dep in depends:
                dep_path = os.path.join(self.modules_path, dep)
                if dep.startswith('bcm_') and not os.path.exists(dep_path):
                    self.errors.append(f"{module_name}: Зависимость '{dep}' не найдена")

            # Проверка файлов данных
            data_files = local_vars.get('data', [])
            for data_file in data_files:
                file_path = os.path.join(module_path, data_file)
                if not os.path.exists(file_path):
                    self.errors.append(f"{module_name}: Файл данных '{data_file}' не найден")

            print(f"  ✓ Манифест проверен")

        except Exception as e:
            self.errors.append(f"{module_name}: Ошибка в манифесте - {e}")

    def check_security_files(self, module_path, module_name):
        """Проверка файлов безопасности"""
        security_file = os.path.join(module_path, "security/ir.model.access.csv")

        if os.path.exists(security_file):
            try:
                with open(security_file, 'r') as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames

                    # Проверка правильных заголовков
                    if headers and 'model_id:id' not in headers:
                        self.errors.append(f"{module_name}: security/ir.model.access.csv - неправильный формат заголовков (нужен model_id:id)")

                    # Проверка ссылок на модели
                    for row in reader:
                        if row.get('model_id:id'):
                            model_ref = row['model_id:id']
                            if model_ref and not model_ref.startswith('model_'):
                                self.errors.append(f"{module_name}: security - неправильная ссылка на модель '{model_ref}' (должна начинаться с 'model_')")

                print(f"  ✓ Файлы безопасности проверены")

            except Exception as e:
                self.errors.append(f"{module_name}: Ошибка чтения security файла - {e}")

    def check_models(self, module_path, module_name):
        """Проверка моделей и сбор их имен"""
        models = set()
        models_path = os.path.join(module_path, "models")

        if os.path.exists(models_path):
            # Проверка __init__.py
            init_file = os.path.join(models_path, "__init__.py")
            if os.path.exists(init_file):
                with open(init_file, 'r') as f:
                    init_content = f.read()

                # Собираем все .py файлы в папке models
                py_files = glob.glob(os.path.join(models_path, "*.py"))
                for py_file in py_files:
                    filename = os.path.basename(py_file)
                    if filename != "__init__.py":
                        module_import = filename[:-3]  # убираем .py
                        if f"from . import {module_import}" not in init_content:
                            self.warnings.append(f"{module_name}: Файл models/{filename} не импортируется в __init__.py")

            # Собираем имена моделей
            for py_file in glob.glob(os.path.join(models_path, "*.py")):
                if "__init__" not in py_file:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        # Ищем определения моделей
                        model_names = re.findall(r'_name\s*=\s*["\']([^"\']+)["\']', content)
                        models.update(model_names)

            if models:
                print(f"  ✓ Найдено моделей: {len(models)}")

        return models

    def check_views(self, module_path, module_name, models):
        """Проверка представлений"""
        views_path = os.path.join(module_path, "views")

        if os.path.exists(views_path):
            xml_files = glob.glob(os.path.join(views_path, "*.xml"))

            for xml_file in xml_files:
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()

                    # Проверка представлений
                    for record in root.findall(".//record[@model='ir.ui.view']"):
                        view_model = None
                        view_name = record.get('id', 'unknown')

                        # Находим модель представления
                        for field in record.findall("field[@name='model']"):
                            view_model = field.text
                            break

                        # Проверка полей в представлении
                        if view_model:
                            arch = record.find(".//field[@name='arch']")
                            if arch is not None:
                                # Проверяем поля в форме
                                fields_in_view = re.findall(r'<field\s+name=["\']([^"\']+)["\']', ET.tostring(arch, encoding='unicode'))

                                # Получаем поля модели для сравнения
                                model_fields = self.get_model_fields(module_path, view_model)
                                for field in fields_in_view:
                                    if field not in model_fields and field not in ['id', 'create_uid', 'create_date', 'write_uid', 'write_date']:
                                        self.errors.append(f"{module_name}: Field '{field}' используется в view '{view_name}' но отсутствует в модели '{view_model}'")

                                # Проверяем кнопки с методами
                                buttons = re.findall(r'<button[^>]+name=["\']([^"\']+)["\'][^>]+type=["\']object["\']', ET.tostring(arch, encoding='unicode'))
                                if buttons:
                                    self.warnings.append(f"{module_name}: View '{view_name}' имеет кнопки с методами: {buttons} - убедитесь что они определены в модели")

                                # Проверка на использование tree вместо list
                                if '<tree' in ET.tostring(arch, encoding='unicode'):
                                    self.errors.append(f"{module_name}: View '{view_name}' использует <tree> вместо <list> (Odoo 18)")

                    print(f"  ✓ Представления проверены")

                except ET.ParseError as e:
                    self.errors.append(f"{module_name}: XML ошибка в {os.path.basename(xml_file)} - {e}")
                except Exception as e:
                    self.errors.append(f"{module_name}: Ошибка проверки представления - {e}")

    def check_imports(self, module_path, module_name):
        """Проверка __init__.py импортов"""
        init_file = os.path.join(module_path, "__init__.py")

        if os.path.exists(init_file):
            with open(init_file, 'r') as f:
                content = f.read()

            # Проверяем что models импортируется если папка существует
            if os.path.exists(os.path.join(module_path, "models")):
                if "from . import models" not in content:
                    self.errors.append(f"{module_name}: Папка models существует но не импортируется в __init__.py")

            print(f"  ✓ Импорты проверены")

    def check_assets(self, module_path, module_name):
        """Проверка JavaScript и CSS файлов"""
        manifest_path = os.path.join(module_path, "__manifest__.py")

        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                content = f.read()

            local_vars = {}
            exec(content, {}, local_vars)

            assets = local_vars.get('assets', {})
            for asset_bundle, files in assets.items():
                for file_ref in files:
                    # Пропускаем если это ссылка на другой модуль
                    if not file_ref.startswith(module_name):
                        continue

                    file_path = file_ref.replace(f"{module_name}/", "")
                    full_path = os.path.join(module_path, file_path)

                    if not os.path.exists(full_path):
                        self.errors.append(f"{module_name}: Asset файл '{file_path}' не найден")

                    # Проверка JavaScript на OWL компоненты
                    if file_path.endswith('.js') and os.path.exists(full_path):
                        with open(full_path, 'r') as f:
                            js_content = f.read()

                        # Проверка правильной регистрации компонентов для Odoo 18
                        if 'registry.category("fields").add' in js_content:
                            if 'component:' not in js_content:
                                self.errors.append(f"{module_name}: JS widget не имеет 'component:' в регистрации (требуется для Odoo 18)")

    def check_dependencies(self, module_path, module_name):
        """Проверка зависимостей и связей между модулями"""
        manifest_path = os.path.join(module_path, "__manifest__.py")

        if not os.path.exists(manifest_path):
            return

        try:
            with open(manifest_path, 'r') as f:
                content = f.read()

            local_vars = {}
            exec(content, {}, local_vars)

            depends = local_vars.get('depends', [])

            # Собираем все установленные модули
            all_modules = set()
            for module_dir in glob.glob(f"{self.modules_path}/*"):
                if os.path.isdir(module_dir):
                    all_modules.add(os.path.basename(module_dir))

            # Собираем стандартные модули Odoo
            standard_modules = {'base', 'web', 'mail', 'base_setup', 'sale', 'purchase',
                              'stock', 'account', 'hr', 'crm', 'project', 'website'}

            # Проверяем каждую зависимость
            dependency_graph = {}
            missing_deps = []
            circular_deps = []

            for dep in depends:
                if dep not in all_modules and dep not in standard_modules:
                    missing_deps.append(dep)
                    self.errors.append(f"{module_name}: Зависимость '{dep}' не найдена в системе")

                # Проверка циклических зависимостей
                if dep in all_modules:
                    dep_manifest = os.path.join(self.modules_path, dep, "__manifest__.py")
                    if os.path.exists(dep_manifest):
                        try:
                            with open(dep_manifest, 'r') as f:
                                dep_content = f.read()
                            dep_vars = {}
                            exec(dep_content, {}, dep_vars)
                            dep_depends = dep_vars.get('depends', [])

                            # Проверка на прямую циклическую зависимость
                            if module_name in dep_depends:
                                circular_deps.append(f"{module_name} <-> {dep}")
                                self.errors.append(f"{module_name}: Циклическая зависимость с модулем '{dep}'")
                        except:
                            pass

            # Проверка связей через модели (Many2one, One2many, Many2many)
            external_refs = []
            models_path = os.path.join(module_path, "models")
            if os.path.exists(models_path):
                for py_file in glob.glob(os.path.join(models_path, "*.py")):
                    if "__init__" not in py_file:
                        with open(py_file, 'r') as f:
                            content = f.read()

                        # Поиск связей Many2one
                        many2one_refs = re.findall(r'fields\.Many2one\([\'"]([^\'"]+)[\'"]', content)
                        # Поиск связей One2many
                        one2many_refs = re.findall(r'fields\.One2many\([\'"]([^\'"]+)[\'"]', content)
                        # Поиск связей Many2many
                        many2many_refs = re.findall(r'fields\.Many2many\([\'"]([^\'"]+)[\'"]', content)

                        all_refs = many2one_refs + one2many_refs + many2many_refs

                        for ref_model in all_refs:
                            # Проверяем если это внешняя модель (не из текущего модуля)
                            if not ref_model.startswith(module_name.replace('bcm_', 'bcm.')):
                                external_refs.append(ref_model)

                                # Проверяем нужна ли зависимость для этой модели
                                if ref_model.startswith('bcm.'):
                                    required_module = 'bcm_' + ref_model.split('.')[1]
                                    if required_module not in depends and required_module != module_name:
                                        self.warnings.append(f"{module_name}: Модель '{ref_model}' используется, но модуль '{required_module}' не в зависимостях")

            # Вывод информации о связях
            if missing_deps or circular_deps or external_refs:
                print(f"  ✓ Проверка зависимостей:")
                if depends:
                    print(f"    • Объявленные зависимости: {', '.join(depends)}")
                if external_refs:
                    unique_refs = list(set(external_refs))
                    print(f"    • Внешние связи моделей: {', '.join(unique_refs[:5])}" +
                          (f" и еще {len(unique_refs)-5}" if len(unique_refs) > 5 else ""))
                if missing_deps:
                    print(f"    • ⚠️ Отсутствующие модули: {', '.join(missing_deps)}")
                if circular_deps:
                    print(f"    • ⚠️ Циклические зависимости: {', '.join(circular_deps)}")
            else:
                print(f"  ✓ Зависимости проверены")

        except Exception as e:
            self.errors.append(f"{module_name}: Ошибка проверки зависимостей - {e}")

    def print_summary(self):
        """Вывод итогов"""
        print("\n" + "="*60)
        print("📊 ИТОГИ ВАЛИДАЦИИ")
        print("="*60)

        if self.errors:
            print(f"\n❌ Найдено ошибок: {len(self.errors)}")
            for error in self.errors:
                print(f"  • {error}")
        else:
            print("\n✅ Критических ошибок не найдено!")

        if self.warnings:
            print(f"\n⚠️  Предупреждений: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  • {warning}")

        print("\n" + "="*60)

        if self.errors:
            print("🔧 Рекомендация: Исправьте ошибки перед установкой модулей")
        else:
            print("✨ Все модули готовы к установке!")

    def get_all_modules(self):
        """Получить список всех BCM модулей"""
        bcm_modules = []
        for module_dir in glob.glob(f"{self.modules_path}/bcm_*"):
            if os.path.isdir(module_dir):
                bcm_modules.append(module_dir)
        return bcm_modules

    def get_module_info(self, module_path):
        """Получить информацию о модуле из манифеста"""
        manifest_path = os.path.join(module_path, "__manifest__.py")

        if not os.path.exists(manifest_path):
            return {}

        try:
            with open(manifest_path, 'r') as f:
                content = f.read()

            local_vars = {}
            exec(content, {}, local_vars)

            return {
                'name': local_vars.get('name', ''),
                'version': local_vars.get('version', ''),
                'category': local_vars.get('category', ''),
                'summary': local_vars.get('summary', ''),
                'description': local_vars.get('description', ''),
                'author': local_vars.get('author', ''),
                'website': local_vars.get('website', ''),
                'dependencies': local_vars.get('depends', []),
                'installed': local_vars.get('installable', False),
                'application': local_vars.get('application', False),
                'auto_install': local_vars.get('auto_install', False),
                'license': local_vars.get('license', ''),
                'data': local_vars.get('data', []),
                'assets': local_vars.get('assets', {})
            }
        except:
            return {}

    def get_model_fields(self, module_path, model_name):
        """Получить список полей из модели"""
        fields = []
        models_path = os.path.join(module_path, "models")

        if os.path.exists(models_path):
            for py_file in glob.glob(os.path.join(models_path, "*.py")):
                if "__init__" not in py_file:
                    with open(py_file, 'r') as f:
                        content = f.read()

                    # Ищем определение модели
                    model_pattern = f"_name\s*=\s*['\"]{ re.escape(model_name)}['\"]"
                    if re.search(model_pattern, content):
                        # Извлекаем все поля
                        field_patterns = [
                            r'(\w+)\s*=\s*fields\.\w+',  # Обычные поля
                        ]
                        for pattern in field_patterns:
                            matches = re.findall(pattern, content)
                            fields.extend(matches)

        # Добавляем стандартные поля Odoo
        fields.extend(['name', 'active', 'state', 'company_id', 'user_id'])

        return fields

    def get_dependencies_info(self, module_path):
        """Получить информацию о зависимостях модуля"""
        module_name = os.path.basename(module_path)
        manifest_info = self.get_module_info(module_path)

        dependencies = {
            'declared': manifest_info.get('dependencies', []),
            'missing': [],
            'circular': [],
            'external_models': []
        }

        # Проверяем зависимости
        all_modules = set(os.path.basename(m) for m in self.get_all_modules())
        standard_modules = {'base', 'web', 'mail', 'base_setup', 'sale', 'purchase',
                           'stock', 'account', 'hr', 'crm', 'project', 'website'}

        for dep in dependencies['declared']:
            if dep not in all_modules and dep not in standard_modules:
                dependencies['missing'].append(dep)

        # Проверяем внешние модели
        models_path = os.path.join(module_path, "models")
        if os.path.exists(models_path):
            for py_file in glob.glob(os.path.join(models_path, "*.py")):
                if "__init__" not in py_file:
                    with open(py_file, 'r') as f:
                        content = f.read()

                    # Поиск связей
                    many2one_refs = re.findall(r'fields\.Many2one\([\'"]([^\'"]+)[\'"]', content)
                    one2many_refs = re.findall(r'fields\.One2many\([\'"]([^\'"]+)[\'"]', content)
                    many2many_refs = re.findall(r'fields\.Many2many\([\'"]([^\'"]+)[\'"]', content)

                    all_refs = many2one_refs + one2many_refs + many2many_refs

                    for ref_model in all_refs:
                        if not ref_model.startswith(module_name.replace('bcm_', 'bcm.')):
                            dependencies['external_models'].append(ref_model)

        dependencies['external_models'] = list(set(dependencies['external_models']))

        return dependencies

    def auto_fix_missing_fields(self, module_path):
        """Автоматически добавляет отсутствующие поля в модели"""
        fixed_fields = []
        module_name = os.path.basename(module_path)
        models_path = os.path.join(module_path, "models")
        views_path = os.path.join(module_path, "views")

        if not os.path.exists(views_path):
            return fixed_fields

        # Собираем все отсутствующие поля
        missing_fields = {}

        for xml_file in glob.glob(os.path.join(views_path, "*.xml")):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                for record in root.findall(".//record[@model='ir.ui.view']"):
                    view_model = None
                    for field in record.findall("field[@name='model']"):
                        view_model = field.text
                        break

                    if view_model:
                        arch = record.find(".//field[@name='arch']")
                        if arch is not None:
                            fields_in_view = re.findall(r'<field\s+name=["\']([^"\']+)["\']', ET.tostring(arch, encoding='unicode'))
                            model_fields = self.get_model_fields(module_path, view_model)

                            for field_name in fields_in_view:
                                if field_name not in model_fields and field_name not in ['id', 'create_uid', 'create_date', 'write_uid', 'write_date']:
                                    if view_model not in missing_fields:
                                        missing_fields[view_model] = []
                                    if field_name not in missing_fields[view_model]:
                                        missing_fields[view_model].append(field_name)
            except:
                continue

        # Добавляем отсутствующие поля в модели
        for model_name, fields in missing_fields.items():
            if os.path.exists(models_path):
                for py_file in glob.glob(os.path.join(models_path, "*.py")):
                    if "__init__" not in py_file:
                        with open(py_file, 'r') as f:
                            content = f.read()

                        # Ищем модель
                        model_pattern = f"_name\s*=\s*['\"]{ re.escape(model_name)}['\"]"
                        if re.search(model_pattern, content):
                            # Добавляем поля после _description или _name
                            lines = content.split('\n')
                            insert_index = -1

                            for i, line in enumerate(lines):
                                if '_description' in line or '_inherit' in line:
                                    insert_index = i + 1
                                    break
                                elif '_name' in line:
                                    insert_index = i + 1

                            if insert_index > 0:
                                # Добавляем поля
                                new_fields = []
                                for field_name in fields:
                                    # Определяем тип поля по имени
                                    if 'description' in field_name.lower() or 'note' in field_name.lower() or 'comment' in field_name.lower():
                                        field_type = 'Text'
                                    elif 'date' in field_name.lower():
                                        field_type = 'Date'
                                    elif 'amount' in field_name.lower() or 'price' in field_name.lower() or 'cost' in field_name.lower():
                                        field_type = 'Float'
                                    elif '_id' in field_name:
                                        continue  # Пропускаем связи
                                    else:
                                        field_type = 'Char'

                                    field_def = f"    {field_name} = fields.{field_type}('{field_name.replace('_', ' ').title()}')"
                                    new_fields.append(field_def)
                                    fixed_fields.append(f"{model_name}.{field_name}")

                                if new_fields:
                                    # Вставляем поля
                                    lines.insert(insert_index, '\n    # Auto-generated missing fields')
                                    for i, field in enumerate(new_fields):
                                        lines.insert(insert_index + i + 1, field)

                                    # Сохраняем файл
                                    with open(py_file, 'w') as f:
                                        f.write('\n'.join(lines))

                                    print(f"  🔧 Добавлено {len(new_fields)} полей в модель {model_name}")

        return fixed_fields

    def auto_fix_module(self, module_path):
        """Автоматически исправить проблемы в модуле"""
        fixed_issues = []
        module_name = os.path.basename(module_path)

        # Исправление отсутствующих полей в моделях
        fixed_fields = self.auto_fix_missing_fields(module_path)
        if fixed_fields:
            fixed_issues.append(f"Added missing fields: {', '.join(fixed_fields)}")

        # Исправление файлов безопасности
        security_file = os.path.join(module_path, "security/ir.model.access.csv")
        if os.path.exists(security_file):
            try:
                with open(security_file, 'r') as f:
                    lines = f.readlines()

                if lines:
                    # Исправляем заголовки
                    if 'model_id,' in lines[0] and 'model_id:id,' not in lines[0]:
                        lines[0] = lines[0].replace('model_id,', 'model_id:id,')
                        fixed_issues.append(f"Fixed security file header in {module_name}")

                    # Исправляем ссылки на модели
                    for i, line in enumerate(lines[1:], 1):
                        parts = line.strip().split(',')
                        if len(parts) >= 3:
                            model_ref = parts[2]
                            if model_ref and not model_ref.startswith('model_'):
                                parts[2] = 'model_' + model_ref.replace('.', '_')
                                lines[i] = ','.join(parts) + '\n'
                                fixed_issues.append(f"Fixed model reference: {model_ref} -> {parts[2]}")

                    # Записываем исправленный файл
                    with open(security_file, 'w') as f:
                        f.writelines(lines)
            except Exception as e:
                pass

        # Исправление импортов в __init__.py
        models_path = os.path.join(module_path, "models")
        if os.path.exists(models_path):
            init_file = os.path.join(models_path, "__init__.py")
            if os.path.exists(init_file):
                with open(init_file, 'r') as f:
                    init_content = f.read()

                # Находим все .py файлы
                py_files = glob.glob(os.path.join(models_path, "*.py"))
                imports_added = []

                for py_file in py_files:
                    filename = os.path.basename(py_file)
                    if filename != "__init__.py":
                        module_import = filename[:-3]  # убираем .py
                        if f"from . import {module_import}" not in init_content:
                            init_content += f"\nfrom . import {module_import}"
                            imports_added.append(module_import)

                if imports_added:
                    with open(init_file, 'w') as f:
                        f.write(init_content)
                    fixed_issues.append(f"Added missing imports: {', '.join(imports_added)}")

        return fixed_issues

if __name__ == "__main__":
    validator = ModuleValidator()
    validator.validate_all_modules()