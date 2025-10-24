"""
Process Framework - Core framework implementation

Provides:
- Process registration and management
- Process instance execution
- Step validation and progression
"""

from typing import Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import json

from .models import (
    ProcessDefinition,
    ProcessInstance,
    ProcessStatus,
    ProcessStep
)


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
            processes_dir = Path(__file__).parent.parent.parent / "processes"
        _framework_instance = ProcessFramework(processes_dir)

    return _framework_instance
