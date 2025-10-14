"""
Document Templates - Шаблоны документов для стандартизации

Обеспечивает:
- Генерацию документов по шаблонам
- Стандартизацию форматирования
- Валидацию структуры документов
- ISO 22301 compliance
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
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
        bia_template = self.create_bia_report_template()
        self.register_template(bia_template)

        # Risk Register Template
        risk_template = self.create_risk_register_template()
        self.register_template(risk_template)

        # BC Plan Template
        bc_plan_template = self.create_bc_plan_template()
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

    def create_bia_report_template(self) -> DocumentTemplate:
        """Создать шаблон отчета BIA"""
        template = DocumentTemplate(
            id="bia_report_v1",
            name="Business Impact Analysis Report",
            version="1.0",
            description="Стандартный отчет BIA в соответствии с ISO 22301",
            document_type="bia_report",
            iso_clause="8.2.2",
            required_variables=[
                "organization_name",
                "analysis_date",
                "prepared_by",
                "scope",
                "critical_functions",
                "rto_summary",
                "rpo_summary",
                "impact_analysis"
            ]
        )

        # Header
        template.header_template = """
# BUSINESS IMPACT ANALYSIS REPORT

**Organization:** {{organization_name}}
**Date:** {{analysis_date}}
**Prepared by:** {{prepared_by}}
**Version:** 1.0
**Status:** {{status}}

---

**Document Control:**
- Confidentiality: {{confidentiality_level}}
- Distribution: {{distribution_list}}
- Review Date: {{review_date}}

---
"""

        # Section 1: Executive Summary
        section1 = DocumentSection(
            id="executive_summary",
            title="1. Executive Summary",
            content_template="""
This Business Impact Analysis was conducted to identify critical business functions,
assess the potential impact of disruptions, and determine recovery objectives.

**Key Findings:**
{{key_findings}}

**Critical Functions Identified:** {{critical_functions_count}}

**Average RTO:** {{average_rto}} hours
**Average RPO:** {{average_rpo}} minutes
""",
            required=True,
            order=1
        )

        # Section 2: Scope and Objectives
        section2 = DocumentSection(
            id="scope_objectives",
            title="2. Scope and Objectives",
            content_template="""
### 2.1 Scope

{{scope}}

### 2.2 Objectives

The objectives of this BIA are:
{{objectives}}

### 2.3 Methodology

{{methodology}}
""",
            required=True,
            order=2
        )

        # Section 3: Critical Functions
        section3 = DocumentSection(
            id="critical_functions",
            title="3. Critical Business Functions",
            content_template="""
The following critical business functions have been identified:

{{critical_functions}}

### 3.1 Function Dependencies

{{function_dependencies}}
""",
            required=True,
            order=3,
            min_length=200
        )

        # Section 4: Impact Analysis
        section4 = DocumentSection(
            id="impact_analysis",
            title="4. Impact Analysis",
            content_template="""
### 4.1 Recovery Time Objectives (RTO)

{{rto_summary}}

### 4.2 Recovery Point Objectives (RPO)

{{rpo_summary}}

### 4.3 Financial Impact

{{financial_impact}}

### 4.4 Reputational Impact

{{reputational_impact}}

### 4.5 Regulatory Impact

{{regulatory_impact}}

### 4.6 Overall Impact Assessment

{{impact_assessment}}
""",
            required=True,
            order=4
        )

        # Section 5: Resource Requirements
        section5 = DocumentSection(
            id="resource_requirements",
            title="5. Resource Requirements",
            content_template="""
### 5.1 Personnel

{{personnel_requirements}}

### 5.2 Technology

{{technology_requirements}}

### 5.3 Facilities

{{facilities_requirements}}

### 5.4 Third-Party Dependencies

{{third_party_dependencies}}
""",
            required=True,
            order=5
        )

        # Section 6: Recommendations
        section6 = DocumentSection(
            id="recommendations",
            title="6. Recommendations",
            content_template="""
Based on this analysis, the following recommendations are made:

{{recommendations}}

### 6.1 Priority Actions

{{priority_actions}}

### 6.2 Resource Allocation

{{resource_allocation_recommendations}}
""",
            required=True,
            order=6
        )

        # Section 7: Approval
        section7 = DocumentSection(
            id="approval",
            title="7. Approval",
            content_template="""
This Business Impact Analysis has been reviewed and approved by:

**Name:** {{approver_name}}
**Position:** {{approver_position}}
**Date:** {{approval_date}}
**Signature:** _________________________

**Comments:**
{{approval_comments}}
""",
            required=True,
            order=7
        )

        # Footer
        template.footer_template = """
---

**Document Information:**
- Template: BIA Report v1.0
- Generated: {{generation_timestamp}}
- ISO 22301:2019 Clause 8.2.2 Compliant
- Confidentiality: Internal Use Only

**Next Review Date:** {{next_review_date}}
"""

        # Добавить секции
        template.add_section(section1)
        template.add_section(section2)
        template.add_section(section3)
        template.add_section(section4)
        template.add_section(section5)
        template.add_section(section6)
        template.add_section(section7)

        return template

    def create_risk_register_template(self) -> DocumentTemplate:
        """Создать шаблон Risk Register"""
        template = DocumentTemplate(
            id="risk_register_v1",
            name="Risk Register",
            version="1.0",
            description="Реестр рисков непрерывности бизнеса",
            document_type="risk_register",
            iso_clause="8.2.3",
            required_variables=[
                "organization_name",
                "register_date",
                "risks"
            ]
        )

        template.header_template = """
# RISK REGISTER

**Organization:** {{organization_name}}
**Date:** {{register_date}}
**Version:** {{version}}

---
"""

        section1 = DocumentSection(
            id="risk_list",
            title="1. Identified Risks",
            content_template="""
{{risks}}

### Risk Matrix

| Likelihood / Impact | 1 (Low) | 2 | 3 | 4 | 5 (High) |
|---------------------|---------|---|---|---|----------|
| **5 (Almost Certain)** | {{risk_5_1}} | {{risk_5_2}} | {{risk_5_3}} | {{risk_5_4}} | {{risk_5_5}} |
| **4 (Likely)** | {{risk_4_1}} | {{risk_4_2}} | {{risk_4_3}} | {{risk_4_4}} | {{risk_4_5}} |
| **3 (Possible)** | {{risk_3_1}} | {{risk_3_2}} | {{risk_3_3}} | {{risk_3_4}} | {{risk_3_5}} |
| **2 (Unlikely)** | {{risk_2_1}} | {{risk_2_2}} | {{risk_2_3}} | {{risk_2_4}} | {{risk_2_5}} |
| **1 (Rare)** | {{risk_1_1}} | {{risk_1_2}} | {{risk_1_3}} | {{risk_1_4}} | {{risk_1_5}} |
""",
            required=True,
            order=1
        )

        section2 = DocumentSection(
            id="treatment_plan",
            title="2. Risk Treatment Plan",
            content_template="""
{{treatment_plan}}
""",
            required=True,
            order=2
        )

        template.add_section(section1)
        template.add_section(section2)

        return template

    def create_bc_plan_template(self) -> DocumentTemplate:
        """Создать шаблон Business Continuity Plan"""
        template = DocumentTemplate(
            id="bc_plan_v1",
            name="Business Continuity Plan",
            version="1.0",
            description="План обеспечения непрерывности бизнеса",
            document_type="bc_plan",
            iso_clause="8.4",
            required_variables=[
                "organization_name",
                "plan_date",
                "scope",
                "critical_functions",
                "recovery_strategies",
                "roles_responsibilities",
                "contact_list",
                "recovery_procedures"
            ]
        )

        template.header_template = """
# BUSINESS CONTINUITY PLAN

**Organization:** {{organization_name}}
**Date:** {{plan_date}}
**Version:** {{version}}
**Status:** {{status}}

---

**Plan Owner:** {{plan_owner}}
**Review Frequency:** {{review_frequency}}
**Last Updated:** {{last_updated}}

---
"""

        # Sections
        sections = [
            DocumentSection(
                id="introduction",
                title="1. Introduction",
                content_template="{{introduction}}",
                order=1
            ),
            DocumentSection(
                id="scope",
                title="2. Scope",
                content_template="{{scope}}",
                order=2
            ),
            DocumentSection(
                id="critical_functions",
                title="3. Critical Business Functions",
                content_template="{{critical_functions}}",
                order=3
            ),
            DocumentSection(
                id="recovery_strategies",
                title="4. Recovery Strategies",
                content_template="{{recovery_strategies}}",
                order=4
            ),
            DocumentSection(
                id="roles",
                title="5. Roles and Responsibilities",
                content_template="""
### 5.1 Incident Management Team

{{incident_management_team}}

### 5.2 Recovery Teams

{{recovery_teams}}

### 5.3 Contact List

{{contact_list}}
""",
                order=5
            ),
            DocumentSection(
                id="procedures",
                title="6. Recovery Procedures",
                content_template="{{recovery_procedures}}",
                order=6
            ),
            DocumentSection(
                id="communication",
                title="7. Communication Plan",
                content_template="{{communication_plan}}",
                order=7
            ),
            DocumentSection(
                id="testing",
                title="8. Testing and Maintenance",
                content_template="""
### 8.1 Testing Schedule

{{testing_schedule}}

### 8.2 Plan Maintenance

{{plan_maintenance}}
""",
                order=8
            )
        ]

        for section in sections:
            template.add_section(section)

        return template


# Singleton
_library_instance: Optional[DocumentTemplateLibrary] = None


def get_document_library(templates_dir: Path = None) -> DocumentTemplateLibrary:
    """Получить singleton библиотеки шаблонов"""
    global _library_instance

    if _library_instance is None:
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "document_templates"
        _library_instance = DocumentTemplateLibrary(templates_dir)

    return _library_instance
