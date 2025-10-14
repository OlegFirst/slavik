"""
Process Framework - Каркас для формализации бизнес-процессов

Обеспечивает:
- Структурированное описание бизнес-процессов
- Валидацию шагов процесса
- Контроль переходов между этапами
- Стандартизацию взаимодействия с пользователем
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


class ValidationRule(Enum):
    """Правила валидации"""
    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    ENUM = "enum"
    NUMERIC_RANGE = "numeric_range"
    DATE_RANGE = "date_range"
    CUSTOM = "custom"


@dataclass
class FieldValidation:
    """Валидация поля"""
    rule: ValidationRule
    value: Any
    error_message: str

    def validate(self, field_value: Any) -> tuple[bool, Optional[str]]:
        """Валидация значения поля"""
        if self.rule == ValidationRule.REQUIRED:
            if not field_value:
                return False, self.error_message

        elif self.rule == ValidationRule.MIN_LENGTH:
            if len(str(field_value)) < self.value:
                return False, self.error_message

        elif self.rule == ValidationRule.MAX_LENGTH:
            if len(str(field_value)) > self.value:
                return False, self.error_message

        elif self.rule == ValidationRule.PATTERN:
            import re
            if not re.match(self.value, str(field_value)):
                return False, self.error_message

        elif self.rule == ValidationRule.ENUM:
            if field_value not in self.value:
                return False, self.error_message

        elif self.rule == ValidationRule.NUMERIC_RANGE:
            min_val, max_val = self.value
            if not (min_val <= float(field_value) <= max_val):
                return False, self.error_message

        elif self.rule == ValidationRule.DATE_RANGE:
            # Реализация date range validation
            pass

        return True, None


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
    validations: List[FieldValidation] = field(default_factory=list)
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


class ProcessFramework:
    """
    Фреймворк для управления бизнес-процессами

    Обеспечивает:
    - Регистрацию процессов
    - Создание экземпляров процессов
    - Выполнение шагов
    - Валидацию данных
    - Генерацию документов по шаблонам
    """

    def __init__(self, processes_dir: Path):
        self.processes_dir = processes_dir
        self.processes: Dict[str, ProcessDefinition] = {}
        self.instances: Dict[str, ProcessInstance] = {}

        # Загрузить процессы из файлов
        self._load_processes()

    def _load_processes(self):
        """Загрузить определения процессов из файлов"""
        if not self.processes_dir.exists():
            self.processes_dir.mkdir(parents=True, exist_ok=True)
            return

        for file_path in self.processes_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Создать ProcessDefinition из данных
                    # (упрощенная версия, полная реализация требует десериализации)
                    process_id = data.get('id')
                    if process_id:
                        # Сохранить в памяти
                        pass
            except Exception as e:
                print(f"Ошибка загрузки процесса {file_path}: {e}")

    def register_process(self, process: ProcessDefinition) -> bool:
        """Зарегистрировать процесс"""
        # Валидация процесса
        is_valid, errors = process.validate_process_flow()
        if not is_valid:
            print(f"Процесс {process.id} невалиден: {errors}")
            return False

        self.processes[process.id] = process

        # Сохранить в файл
        file_path = self.processes_dir / f"{process.id}.json"
        process.save_to_file(file_path)

        return True

    def start_process(self, process_id: str, started_by: str, initial_data: Dict[str, Any] = None) -> Optional[ProcessInstance]:
        """Запустить экземпляр процесса"""
        process = self.processes.get(process_id)
        if not process:
            return None

        # Создать экземпляр
        instance = ProcessInstance(
            id=f"{process_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            process_definition_id=process_id,
            status=ProcessStatus.IN_PROGRESS,
            current_step_id=process.start_step_id,
            started_by=started_by,
            started_at=datetime.now(),
            data=initial_data or {}
        )

        self.instances[instance.id] = instance
        return instance

    def execute_step(self, instance_id: str, step_data: Dict[str, Any], executed_by: str) -> tuple[bool, Optional[str], Any]:
        """
        Выполнить текущий шаг процесса

        Returns:
            (success, error_message, next_step_id)
        """
        instance = self.instances.get(instance_id)
        if not instance:
            return False, "Экземпляр процесса не найден", None

        process = self.processes.get(instance.process_definition_id)
        if not process:
            return False, "Определение процесса не найдено", None

        current_step = process.get_step(instance.current_step_id)
        if not current_step:
            return False, "Текущий шаг не найден", None

        # Проверка прав
        # (В реальной системе executed_by содержит роли пользователя)

        # Валидация входных данных
        is_valid, errors = current_step.validate_input(step_data)
        if not is_valid:
            return False, f"Ошибки валидации: {errors}", None

        # Обновить данные процесса
        instance.update_data(step_data)

        # Добавить в историю
        instance.add_step_to_history(
            step_id=current_step.id,
            data=step_data,
            result="success"
        )

        # Определить следующий шаг
        next_step_id = current_step.get_next_step(instance.data)

        if next_step_id in process.end_step_ids:
            # Процесс завершен
            instance.status = ProcessStatus.COMPLETED
            instance.completed_at = datetime.now()
        elif next_step_id:
            # Переход к следующему шагу
            instance.move_to_step(next_step_id)
        else:
            return False, "Невозможно определить следующий шаг", None

        return True, None, next_step_id

    def get_current_step_form(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Получить форму для текущего шага"""
        instance = self.instances.get(instance_id)
        if not instance:
            return None

        process = self.processes.get(instance.process_definition_id)
        if not process:
            return None

        current_step = process.get_step(instance.current_step_id)
        if not current_step:
            return None

        # Сформировать JSON описание формы для UI
        return {
            "step_id": current_step.id,
            "step_name": current_step.name,
            "description": current_step.description,
            "fields": [
                {
                    "name": field.name,
                    "label": field.label,
                    "type": field.field_type,
                    "description": field.description,
                    "required": field.required,
                    "default_value": field.default_value,
                    "placeholder": field.placeholder,
                    "options": field.options,
                    "help_text": field.help_text
                }
                for field in current_step.form_fields
            ]
        }

    def get_process_status(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Получить статус процесса"""
        instance = self.instances.get(instance_id)
        if not instance:
            return None

        process = self.processes.get(instance.process_definition_id)
        if not process:
            return None

        return {
            "instance_id": instance.id,
            "process_name": process.name,
            "status": instance.status.value,
            "current_step_id": instance.current_step_id,
            "current_step_name": process.get_step(instance.current_step_id).name if process.get_step(instance.current_step_id) else None,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
            "progress_percent": self._calculate_progress(instance, process)
        }

    def _calculate_progress(self, instance: ProcessInstance, process: ProcessDefinition) -> float:
        """Рассчитать прогресс выполнения процесса"""
        total_steps = len(process.steps)
        completed_steps = len(instance.step_history)

        if total_steps == 0:
            return 0.0

        return (completed_steps / total_steps) * 100.0


# Singleton instance
_framework_instance: Optional[ProcessFramework] = None


def get_process_framework(processes_dir: Path = None) -> ProcessFramework:
    """Получить singleton instance фреймворка"""
    global _framework_instance

    if _framework_instance is None:
        if processes_dir is None:
            processes_dir = Path(__file__).parent / "processes"
        _framework_instance = ProcessFramework(processes_dir)

    return _framework_instance
