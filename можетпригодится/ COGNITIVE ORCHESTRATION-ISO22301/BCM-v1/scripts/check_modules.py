#!/usr/bin/env python3
"""
Odoo Module Checker - проверяет модули перед установкой
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import re

class OdooModuleChecker:
    def __init__(self, addons_path):
        self.addons_path = Path(addons_path)
        self.errors = []
        self.warnings = []

    def check_manifest(self, module_path):
        """Проверка __manifest__.py"""
        manifest_file = module_path / '__manifest__.py'
        if not manifest_file.exists():
            self.errors.append(f"{module_path.name}: __manifest__.py не найден")
            return False

        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Проверка на базовую структуру
                if 'name' not in content:
                    self.errors.append(f"{module_path.name}: отсутствует 'name' в манифесте")
                if 'depends' not in content:
                    self.warnings.append(f"{module_path.name}: отсутствует 'depends' в манифесте")

        except Exception as e:
            self.errors.append(f"{module_path.name}: ошибка чтения манифеста: {e}")
            return False

        return True

    def check_xml_files(self, module_path):
        """Проверка XML файлов"""
        for xml_file in module_path.rglob('*.xml'):
            try:
                ET.parse(xml_file)
            except ET.ParseError as e:
                self.errors.append(f"{module_path.name}: XML ошибка в {xml_file.relative_to(module_path)}: {e}")

    def check_python_files(self, module_path):
        """Проверка Python файлов"""
        for py_file in module_path.rglob('*.py'):
            if py_file.name == '__manifest__.py':
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Проверка на базовые ошибки
                if '_name =' in content and '_inherit =' in content:
                    # Проверка корректности модели
                    model_name_match = re.search(r"_name\s*=\s*['\"]([^'\"]+)['\"]", content)
                    if model_name_match:
                        model_name = model_name_match.group(1)
                        if not model_name.startswith(('bcm.', 'res.', 'ir.')):
                            self.warnings.append(f"{module_path.name}: модель {model_name} не соответствует конвенции BCM")

            except Exception as e:
                self.errors.append(f"{module_path.name}: ошибка чтения Python файла {py_file.relative_to(module_path)}: {e}")

    def check_dependencies(self, module_path):
        """Проверка зависимостей"""
        manifest_file = module_path / '__manifest__.py'
        if manifest_file.exists():
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Извлечение зависимостей
                depends_match = re.search(r"'depends'\s*:\s*\[(.*?)\]", content, re.DOTALL)
                if depends_match:
                    deps_str = depends_match.group(1)
                    deps = re.findall(r"'([^']+)'", deps_str)

                    for dep in deps:
                        if dep.startswith('bcm_'):
                            dep_path = self.addons_path / dep
                            if not dep_path.exists():
                                self.errors.append(f"{module_path.name}: зависимость {dep} не найдена")

            except Exception as e:
                self.errors.append(f"{module_path.name}: ошибка проверки зависимостей: {e}")

    def check_module(self, module_name):
        """Проверка одного модуля"""
        module_path = self.addons_path / module_name
        if not module_path.exists():
            self.errors.append(f"Модуль {module_name} не найден")
            return False

        print(f"Проверка модуля {module_name}...")

        # Проверки
        self.check_manifest(module_path)
        self.check_xml_files(module_path)
        self.check_python_files(module_path)
        self.check_dependencies(module_path)

        return True

    def check_all_bcm_modules(self):
        """Проверка всех BCM модулей"""
        bcm_modules = [d for d in self.addons_path.iterdir()
                      if d.is_dir() and d.name.startswith('bcm_')]

        for module_path in bcm_modules:
            self.check_module(module_path.name)

    def print_results(self):
        """Вывод результатов"""
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ ПРОВЕРКИ МОДУЛЕЙ")
        print("="*50)

        if self.errors:
            print(f"\n❌ ОШИБКИ ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ Все модули прошли проверку!")
        elif not self.errors:
            print(f"\n✅ Критических ошибок не найдено. {len(self.warnings)} предупреждений.")
        else:
            print(f"\n❌ Найдено {len(self.errors)} ошибок и {len(self.warnings)} предупреждений.")

        return len(self.errors) == 0

def main():
    if len(sys.argv) < 2:
        print("Использование: python check_modules.py <путь_к_addons> [модуль]")
        sys.exit(1)

    addons_path = sys.argv[1]
    checker = OdooModuleChecker(addons_path)

    if len(sys.argv) > 2:
        # Проверка конкретного модуля
        module_name = sys.argv[2]
        checker.check_module(module_name)
    else:
        # Проверка всех BCM модулей
        checker.check_all_bcm_modules()

    success = checker.print_results()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()