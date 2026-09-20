"""MCP SDK compatibility helpers for attribute name changes in v1.9+."""


def get_tool_input_schema(tool) -> dict:
    """Возвращает input_schema инструмента независимо от версии MCP SDK."""
    return getattr(tool, "input_schema", None) or getattr(tool, "inputSchema", None) or {}


def get_tool_output_schema(tool):
    """Возвращает output_schema инструмента независимо от версии MCP SDK."""
    return getattr(tool, "output_schema", None) or getattr(tool, "outputSchema", None)


def is_call_error(result) -> bool:
    """Проверяет, является ли результат MCP-вызова ошибкой."""
    return bool(getattr(result, "is_error", getattr(result, "isError", False)))
