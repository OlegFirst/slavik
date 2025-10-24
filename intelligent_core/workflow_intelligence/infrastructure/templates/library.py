"""
Document Template Library - Template management and generation

Provides:
- Template registration
- Template retrieval
- Document generation from templates
"""

from typing import Dict, Optional, Any
from pathlib import Path

from .models import DocumentTemplate
from .generators import (
    create_bia_report_template,
    create_risk_register_template,
    create_bc_plan_template
)


class DocumentTemplateLibrary:
    """Библиотека шаблонов документов"""

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.templates: Dict[str, DocumentTemplate] = {}

        # Загрузить шаблоны
        self._load_templates()

    def _load_templates(self):
        """Загрузить шаблоны из файлов"""
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            # Создать стандартные шаблоны
            self._create_standard_templates()

    def _create_standard_templates(self):
        """Создать стандартные шаблоны BCM документов"""
        # BIA Report Template
        bia_template = create_bia_report_template()
        self.register_template(bia_template)

        # Risk Register Template
        risk_template = create_risk_register_template()
        self.register_template(risk_template)

        # BC Plan Template
        bc_plan_template = create_bc_plan_template()
        self.register_template(bc_plan_template)

    def register_template(self, template: DocumentTemplate):
        """Зарегистрировать шаблон"""
        self.templates[template.id] = template

        # Сохранить в файл
        file_path = self.templates_dir / f"{template.id}.json"
        # (упрощенная сериализация)

    def get_template(self, template_id: str) -> Optional[DocumentTemplate]:
        """Получить шаблон по ID"""
        return self.templates.get(template_id)

    def generate_document(self, template_id: str, variables: Dict[str, Any]) -> str:
        """Сгенерировать документ по шаблону"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Шаблон {template_id} не найден")

        return template.generate_content(variables)


# Singleton
_library_instance: Optional[DocumentTemplateLibrary] = None


def get_document_library(templates_dir: Path = None) -> DocumentTemplateLibrary:
    """Получить singleton библиотеки шаблонов"""
    global _library_instance

    if _library_instance is None:
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent.parent / "document_templates"
        _library_instance = DocumentTemplateLibrary(templates_dir)

    return _library_instance
