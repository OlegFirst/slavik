"""Command Interpreter - парсинг и трансляция AI Intent в API calls."""
import re
from typing import Dict, Any, Optional, Tuple
from models.schemas import Intent, ActionType
from core.tool_registry import tool_registry


class CommandInterpreter:
    """Interprets AI intents and translates them into executable API calls."""

    def __init__(self):
        self.registry = tool_registry

    def parse_intent(self, intent: Intent) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Parse intent and prepare for execution.

        Returns:
            (success, error_message, prepared_command)
        """
        # 1. Determine which tool to use
        tool = self._find_tool(intent)
        if not tool:
            return False, f"No tool found for action '{intent.action}' on entity '{intent.entity}'", None

        # 2. Map intent action to tool action
        tool_action = self._map_action(intent.action, tool)
        if not tool_action:
            return False, f"Cannot map action '{intent.action}' to tool '{tool.tool_id}'", None

        # 3. Validate action is supported
        is_valid, error = self.registry.validate_action(tool.tool_id, tool_action, intent.params)
        if not is_valid:
            return False, error, None

        # 4. Build API call command
        command = self._build_command(tool, tool_action, intent)

        return True, None, command

    def _find_tool(self, intent: Intent) -> Optional[Any]:
        """Find appropriate tool for intent."""
        # Try to find tool based on entity
        if intent.entity:
            tool = self.registry.find_tool_for_action(intent.action, intent.entity)
            if tool:
                return tool

        # Try to extract entity from action (e.g., "create_bia" -> entity="bia")
        match = re.match(r'(create|read|update|delete|run|execute|simulate)_(.+)', intent.action)
        if match:
            action_type, entity = match.groups()
            tool = self.registry.find_tool_for_action(action_type, entity)
            if tool:
                return tool

        return None

    def _map_action(self, intent_action: str, tool: Any) -> Optional[str]:
        """Map intent action to tool action."""
        # Direct mapping
        if intent_action in tool.supported_actions:
            return intent_action

        # Extract base action (e.g., "create_bia" -> "create")
        match = re.match(r'(create|read|update|delete|run|execute|simulate|analyze)', intent_action)
        if match:
            base_action = match.group(1)
            if base_action in tool.supported_actions:
                return base_action

        return None

    def _build_command(self, tool: Any, action: str, intent: Intent) -> Dict[str, Any]:
        """Build executable command from intent."""
        # Get endpoint template
        endpoint_template = tool.endpoints.get(action)
        if not endpoint_template:
            raise ValueError(f"No endpoint defined for action '{action}'")

        # Enrich parameters with context
        enriched_params = self._enrich_parameters(intent.params, intent.context)

        # Build full URL
        url = f"{tool.base_url}{endpoint_template}"

        # Replace path parameters (e.g., /processes/{id} -> /processes/123)
        url = self._replace_path_params(url, enriched_params)

        # Separate path params from body params
        body_params = {k: v for k, v in enriched_params.items() if f"{{{k}}}" not in endpoint_template}

        return {
            "tool_id": tool.tool_id,
            "tool_name": tool.name,
            "action": action,
            "method": self._get_http_method(action),
            "url": url,
            "body": body_params if body_params else None,
            "headers": self._build_headers(intent.context, tool),
            "requires_auth": tool.requires_auth,
            "rate_limit": tool.rate_limit,
        }

    def _enrich_parameters(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Enrich parameters with context data."""
        enriched = params.copy()

        # Add tenant_id if not present
        if "tenant_id" not in enriched and hasattr(context, 'tenant_id'):
            enriched["tenant_id"] = context.tenant_id

        # Add user_id if not present
        if "user_id" not in enriched and hasattr(context, 'user_id'):
            enriched["user_id"] = context.user_id
            enriched["created_by"] = context.user_id

        # Add session_id if available
        if hasattr(context, 'session_id') and context.session_id:
            enriched["session_id"] = context.session_id

        return enriched

    def _replace_path_params(self, url: str, params: Dict[str, Any]) -> str:
        """Replace path parameters in URL template."""
        for key, value in params.items():
            url = url.replace(f"{{{key}}}", str(value))
        return url

    def _get_http_method(self, action: str) -> str:
        """Determine HTTP method based on action."""
        method_map = {
            "create": "POST",
            "read": "GET",
            "update": "PUT",
            "delete": "DELETE",
            "list": "GET",
            "execute": "POST",
            "run": "POST",
            "simulate": "POST",
            "analyze": "POST",
            "assess": "POST",
            "activate": "POST",
            "escalate": "POST",
            "resolve": "POST",
        }
        return method_map.get(action, "POST")

    def _build_headers(self, context: Any, tool: Any) -> Dict[str, str]:
        """Build HTTP headers."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Coordination-Center/1.0",
        }

        # Add tenant and user headers (for RLS)
        if hasattr(context, 'tenant_id'):
            headers["X-Tenant-ID"] = context.tenant_id

        if hasattr(context, 'user_id'):
            headers["X-User-ID"] = context.user_id

        # Add session header if available
        if hasattr(context, 'session_id') and context.session_id:
            headers["X-Session-ID"] = context.session_id

        return headers

    def validate_command(self, command: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate prepared command before execution."""
        required_fields = ["tool_id", "action", "method", "url"]

        for field in required_fields:
            if field not in command:
                return False, f"Missing required field: {field}"

        # Check if URL has unresolved path parameters
        if "{" in command["url"] and "}" in command["url"]:
            return False, f"Unresolved path parameters in URL: {command['url']}"

        return True, None


# Global interpreter instance
command_interpreter = CommandInterpreter()
