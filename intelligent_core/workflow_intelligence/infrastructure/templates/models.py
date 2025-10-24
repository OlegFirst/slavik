"""
Document Template Models - Data structures for document templates

Provides:
- Document section structure
- Document template definition
- Template variable management
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class DocumentSection:
    """Секция документа"""
    id: str
    title: str
    content_template: str  # Template с плейсхолдерами {{variable}}
    required: bool = True
    order: int = 0
    subsections: List['DocumentSection'] = field(default_factory=list)

    # Правила валидации контента
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    must_contain: List[str] = field(default_factory=list)  # Обязательные ключевые слова


@dataclass
class DocumentTemplate:
    """Шаблон документа"""
    id: str
    name: str
    description: str
    version: str

    # Метаданные документа
    document_type: str  # bia_report, risk_register, bc_plan, etc.
    iso_clause: Optional[str] = None

    # Структура документа
    header_template: str = ""
    footer_template: str = ""
    sections: List[DocumentSection] = field(default_factory=list)

    # Стиль документа
    style_config: Dict[str, Any] = field(default_factory=dict)

    # Требуемые переменные
    required_variables: List[str] = field(default_factory=list)

    def add_section(self, section: DocumentSection):
        """Добавить секцию"""
        self.sections.append(section)
        # Автоматическая сортировка по order
        self.sections.sort(key=lambda s: s.order)

    def validate_variables(self, variables: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Валидация наличия всех требуемых переменных"""
        missing = []
        for var in self.required_variables:
            if var not in variables:
                missing.append(var)

        return len(missing) == 0, missing

    def generate_content(self, variables: Dict[str, Any]) -> str:
        """Генерация контента документа"""
        # Валидация
        is_valid, missing = self.validate_variables(variables)
        if not is_valid:
            raise ValueError(f"Отсутствуют обязательные переменные: {missing}")

        # Генерация
        content = []

        # Header
        if self.header_template:
            content.append(self._replace_variables(self.header_template, variables))

        # Sections
        for section in self.sections:
            content.append(self._generate_section(section, variables))

        # Footer
        if self.footer_template:
            content.append(self._replace_variables(self.footer_template, variables))

        return "\n\n".join(content)

    def _generate_section(self, section: DocumentSection, variables: Dict[str, Any]) -> str:
        """Генерация секции"""
        content = []

        # Title
        content.append(f"## {section.title}")

        # Content
        section_content = self._replace_variables(section.content_template, variables)
        content.append(section_content)

        # Subsections
        for subsection in section.subsections:
            content.append(self._generate_section(subsection, variables))

        return "\n\n".join(content)

    def _replace_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Замена переменных в шаблоне"""
        result = template

        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"

            # Форматирование значения
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, list):
                value = "\n".join([f"- {item}" for item in value])
            elif isinstance(value, dict):
                value = json.dumps(value, indent=2, ensure_ascii=False)

            result = result.replace(placeholder, str(value))

        return result
