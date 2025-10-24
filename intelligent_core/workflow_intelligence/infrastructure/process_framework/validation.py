"""
Process Framework Validation - Field validation rules

Provides:
- Validation rules enumeration
- Field validation implementation
"""

from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum


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
