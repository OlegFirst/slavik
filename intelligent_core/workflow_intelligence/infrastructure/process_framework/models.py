"""
Process Framework Models - Data classes for process definitions

Provides:
- Process status and step types
- Process definition structures
- Process instance tracking
- Form field definitions
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
from pathlib import Path


class ProcessStatus(Enum):
    """Статус процесса"""
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class StepType(Enum):
    """Тип шага процесса"""
    FORM_INPUT = "form_input"           # Ввод данных через форму
    APPROVAL = "approval"               # Согласование
    ANALYSIS = "analysis"               # Анализ (AI/человек)
    DECISION = "decision"               # Принятие решения
    DOCUMENT_GENERATION = "document_generation"  # Генерация документа
    NOTIFICATION = "notification"       # Уведомление
    VALIDATION = "validation"           # Валидация данных
    EXECUTION = "execution"             # Выполнение действия


@dataclass
class FormField:
    """Поле формы для взаимодействия с пользователем"""
    name: str
    label: str
    field_type: str  # text, number, date, select, textarea, etc.
    description: Optional[str] = None
    required: bool = False
    default_value: Optional[Any] = None
    placeholder: Optional[str] = None
    validations: List['FieldValidation'] = field(default_factory=list)
    options: Optional[List[Dict[str, Any]]] = None  # Для select, radio
    help_text: Optional[str] = None

    def validate(self, value: Any) -> tuple[bool, List[str]]:
        """Валидация значения поля"""
        errors = []

        for validation in self.validations:
            is_valid, error_msg = validation.validate(value)
            if not is_valid:
                errors.append(error_msg)

        return len(errors) == 0, errors


@dataclass
class ProcessStep:
    """Шаг бизнес-процесса"""
    id: str
    name: str
    step_type: StepType
    description: str

    # Форма для взаимодействия с пользователем
    form_fields: List[FormField] = field(default_factory=list)

    # Условия перехода к следующему шагу
    next_steps: List[str] = field(default_factory=list)

    # Условия перехода (если несколько вариантов)
    transition_conditions: Dict[str, Callable] = field(default_factory=dict)

    # Роли, которые могут выполнять этот шаг
    allowed_roles: List[str] = field(default_factory=list)

    # Шаблон документа (если генерируется)
    document_template: Optional[str] = None

    # AI-агент для выполнения (если нужен)
    ai_agent: Optional[str] = None

    # Метаданные
    estimated_duration_minutes: Optional[int] = None
    sla_hours: Optional[int] = None
    auto_approve: bool = False

    def can_execute(self, user_roles: List[str]) -> bool:
        """Проверка, может ли пользователь выполнить шаг"""
        if not self.allowed_roles:
            return True
        return any(role in self.allowed_roles for role in user_roles)

    def validate_input(self, data: Dict[str, Any]) -> tuple[bool, Dict[str, List[str]]]:
        """Валидация входных данных"""
        all_valid = True
        errors = {}

        for field in self.form_fields:
            value = data.get(field.name)
            is_valid, field_errors = field.validate(value)

            if not is_valid:
                all_valid = False
                errors[field.name] = field_errors

        return all_valid, errors

    def get_next_step(self, data: Dict[str, Any]) -> Optional[str]:
        """Определить следующий шаг на основе данных"""
        # Если есть условия перехода
        for step_id, condition in self.transition_conditions.items():
            if condition(data):
                return step_id

        # Если нет условий - первый из списка
        if self.next_steps:
            return self.next_steps[0]

        return None


@dataclass
class ProcessDefinition:
    """Определение бизнес-процесса"""
    id: str
    name: str
    version: str
    description: str

    # Шаги процесса
    steps: Dict[str, ProcessStep] = field(default_factory=dict)

    # Стартовый шаг
    start_step_id: str = ""

    # Конечные шаги
    end_step_ids: List[str] = field(default_factory=list)

    # Метаданные
    category: str = "general"
    owner: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # ISO 22301 compliance
    iso_clause: Optional[str] = None
    compliance_requirements: List[str] = field(default_factory=list)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def add_step(self, step: ProcessStep) -> None:
        """Добавить шаг в процесс"""
        self.steps[step.id] = step

    def get_step(self, step_id: str) -> Optional[ProcessStep]:
        """Получить шаг по ID"""
        return self.steps.get(step_id)

    def validate_process_flow(self) -> tuple[bool, List[str]]:
        """Валидация корректности процесса"""
        errors = []

        # Проверка наличия стартового шага
        if not self.start_step_id:
            errors.append("Процесс должен иметь стартовый шаг")
        elif self.start_step_id not in self.steps:
            errors.append(f"Стартовый шаг {self.start_step_id} не найден")

        # Проверка наличия конечных шагов
        if not self.end_step_ids:
            errors.append("Процесс должен иметь хотя бы один конечный шаг")

        # Проверка связности графа
        for step_id, step in self.steps.items():
            for next_step_id in step.next_steps:
                if next_step_id not in self.steps and next_step_id not in self.end_step_ids:
                    errors.append(f"Шаг {step_id} ссылается на несуществующий шаг {next_step_id}")

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "start_step_id": self.start_step_id,
            "end_step_ids": self.end_step_ids,
            "category": self.category,
            "owner": self.owner,
            "tags": self.tags,
            "iso_clause": self.iso_clause,
            "compliance_requirements": self.compliance_requirements,
            "steps": {
                step_id: {
                    "id": step.id,
                    "name": step.name,
                    "step_type": step.step_type.value,
                    "description": step.description,
                    "next_steps": step.next_steps,
                    "allowed_roles": step.allowed_roles,
                    "document_template": step.document_template,
                    "ai_agent": step.ai_agent,
                    "estimated_duration_minutes": step.estimated_duration_minutes,
                    "sla_hours": step.sla_hours,
                    "auto_approve": step.auto_approve,
                    "form_fields": [
                        {
                            "name": field.name,
                            "label": field.label,
                            "field_type": field.field_type,
                            "description": field.description,
                            "required": field.required,
                            "default_value": field.default_value,
                            "placeholder": field.placeholder,
                            "options": field.options,
                            "help_text": field.help_text
                        }
                        for field in step.form_fields
                    ]
                }
                for step_id, step in self.steps.items()
            }
        }

    def save_to_file(self, file_path: Path) -> None:
        """Сохранить определение в файл"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


@dataclass
class ProcessInstance:
    """Экземпляр выполняемого процесса"""
    id: str
    process_definition_id: str
    status: ProcessStatus

    # Текущий шаг
    current_step_id: str

    # История выполнения
    step_history: List[Dict[str, Any]] = field(default_factory=list)

    # Данные процесса (собранные от пользователя)
    data: Dict[str, Any] = field(default_factory=dict)

    # Метаданные
    started_by: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Участники
    participants: List[str] = field(default_factory=list)

    def add_step_to_history(self, step_id: str, data: Dict[str, Any], result: str):
        """Добавить шаг в историю"""
        self.step_history.append({
            "step_id": step_id,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "result": result
        })

    def update_data(self, new_data: Dict[str, Any]):
        """Обновить данные процесса"""
        self.data.update(new_data)

    def move_to_step(self, step_id: str):
        """Переход к следующему шагу"""
        self.current_step_id = step_id
