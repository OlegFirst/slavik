"""
BPMN Expression Evaluator

Safely evaluates BPMN conditional expressions like ${approved == true}
"""

import re
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class ExpressionEvaluator:
    """
    Evaluates BPMN conditional expressions safely

    Supports:
    - Comparison: ==, !=, >, <, >=, <=
    - Boolean: ${approved}, ${!rejected}
    - Logical: and, or

    Examples:
        ${approved == true}
        ${revenue > 1000000}
        ${status == "completed"}
        ${tier == 1 or tier == 2}
    """

    # Regex to extract expression from ${...}
    EXPR_PATTERN = re.compile(r'\$\{([^}]+)\}')

    # Allowed operators
    COMPARISON_OPS = {
        '==': lambda a, b: a == b,
        '!=': lambda a, b: a != b,
        '>': lambda a, b: a > b,
        '<': lambda a, b: a < b,
        '>=': lambda a, b: a >= b,
        '<=': lambda a, b: a <= b,
    }

    LOGICAL_OPS = {
        'and': lambda a, b: a and b,
        'or': lambda a, b: a or b,
    }

    @classmethod
    def evaluate(cls, expression: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate expression in context

        Args:
            expression: BPMN expression (e.g., "${approved == true}")
            context: Variable context (instance variables)

        Returns:
            bool: Result of evaluation

        Examples:
            >>> evaluate("${approved == true}", {"approved": True})
            True
            >>> evaluate("${revenue > 1000000}", {"revenue": 1500000})
            True
            >>> evaluate("${tier == 1 or tier == 2}", {"tier": 1})
            True
        """
        try:
            # Extract expression from ${...}
            match = cls.EXPR_PATTERN.search(expression)
            if match:
                expr = match.group(1).strip()
            else:
                # No ${} wrapper, use as-is
                expr = expression.strip()

            # Evaluate
            result = cls._evaluate_expression(expr, context)

            logger.debug(f"Expression '{expression}' evaluated to {result}")
            return result

        except Exception as e:
            logger.error(f"Expression evaluation error: {expression} - {e}")
            # Default to False on error (safe)
            return False

    @classmethod
    def _evaluate_expression(cls, expr: str, context: Dict[str, Any]) -> bool:
        """
        Internal expression evaluator

        Handles:
        1. Logical operators (and, or)
        2. Comparison operators (==, !=, >, <, >=, <=)
        3. Boolean variables (approved, !rejected)
        """
        # Check for logical operators
        if ' or ' in expr:
            parts = expr.split(' or ')
            return any(cls._evaluate_expression(part.strip(), context) for part in parts)

        if ' and ' in expr:
            parts = expr.split(' and ')
            return all(cls._evaluate_expression(part.strip(), context) for part in parts)

        # Check for comparison operators
        for op, func in cls.COMPARISON_OPS.items():
            if op in expr:
                left, right = expr.split(op, 1)
                left_val = cls._parse_value(left.strip(), context)
                right_val = cls._parse_value(right.strip(), context)
                return func(left_val, right_val)

        # Check for negation
        if expr.startswith('!'):
            var_name = expr[1:].strip()
            return not cls._get_variable(var_name, context)

        # Simple boolean variable
        return cls._get_variable(expr, context)

    @classmethod
    def _parse_value(cls, value: str, context: Dict[str, Any]) -> Any:
        """
        Parse value - can be variable, string, number, or boolean

        Args:
            value: Value to parse
            context: Variable context

        Returns:
            Parsed value
        """
        value = value.strip()

        # String literal
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]

        # Boolean literal
        if value == 'true':
            return True
        if value == 'false':
            return False

        # Null
        if value == 'null' or value == 'None':
            return None

        # Number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Variable
        return cls._get_variable(value, context)

    @classmethod
    def _get_variable(cls, var_name: str, context: Dict[str, Any]) -> Any:
        """
        Get variable from context (supports dot notation)

        Examples:
            "approved" -> context["approved"]
            "org.industry" -> context["org"]["industry"]
        """
        if '.' in var_name:
            # Nested access
            parts = var_name.split('.')
            value = context
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                    if value is None:
                        return None
                else:
                    return None
            return value
        else:
            # Direct access
            return context.get(var_name)


# Convenience function
def evaluate(expression: str, context: Dict[str, Any]) -> bool:
    """Evaluate BPMN expression"""
    return ExpressionEvaluator.evaluate(expression, context)
