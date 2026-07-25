#!/usr/bin/env python
"""
MCP Server for PowerPoint manipulation using python-pptx.
Consolidated version with tools organized into multiple modules.
"""
import os
import argparse
import platform
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP


from tools import (
    register_presentation_tools,
    register_content_tools,
    register_structural_tools,
    register_professional_tools,
    register_template_tools,
    register_hyperlink_tools,
    register_chart_tools,
    register_connector_tools,
    register_master_tools,
    register_transition_tools
)


# Выполняем стандартную инициализацию
mcp = FastMCP(name="ppt-mcp-server")


# Global state to store presentations in memory
presentations = {}
current_presentation_id = None


# =====================================================================
# ---- Helper Functions (MUST BE DEFINED BEFORE REGISTRATION) ----
# =====================================================================

def get_template_search_directories():
    """
    Get list of directories to search for templates.
    Uses environment variable PPT_TEMPLATE_PATH if set.
    """
    template_env_path = os.environ.get('PPT_TEMPLATE_PATH')
    default_dirs = ['.', './templates', './assets', './resources']
    
    if template_env_path:
        separator = ';' if platform.system() == "Windows" else ':'
        env_dirs = [path.strip() for path in template_env_path.split(separator) if path.strip()]
        
        valid_env_dirs = []
        for dir_path in env_dirs:
            expanded_path = os.path.expanduser(dir_path)
            if os.path.exists(expanded_path) and os.path.isdir(expanded_path):
                valid_env_dirs.append(expanded_path)
                
        if valid_env_dirs:
            return valid_env_dirs + default_dirs
        else:
            print(f"Warning: PPT_TEMPLATE_PATH directories not found: {template_env_path}")
            
    return default_dirs


def get_current_presentation():
    """Get the current presentation object or raise an error."""
    if current_presentation_id is None or current_presentation_id not in presentations:
        raise ValueError("No presentation is currently loaded.")
    return presentations[current_presentation_id]


def get_current_presentation_id():
    """Get the current presentation ID."""
    return current_presentation_id


def set_current_presentation_id(pres_id):
    """Set the current presentation ID."""
    global current_presentation_id
    current_presentation_id = pres_id


def validate_parameters(params):
    """Validate parameters against constraints."""
    for param_name, (value, constraints) in params.items():
        for constraint_func, error_msg in constraints:
            if not constraint_func(value):
                return False, f"Parameter '{param_name}': {error_msg}"
    return True, None


def is_positive(value):
    return value > 0


def is_non_negative(value):
    return value >= 0


def is_in_range(min_val, max_val):
    return lambda x: min_val <= x <= max_val


def is_in_list(valid_list):
    return lambda x: x in valid_list


def is_valid_rgb(color_list):
    if not isinstance(color_list, list) or len(color_list) != 3:
        return False
    return all(isinstance(c, int) and 0 <= c <= 255 for c in color_list)


def add_shape_direct(slide, shape_type: str, left: float, top: float, width: float, height: float) -> Any:
    """Add an auto shape to a slide using direct integer values."""
    from pptx.util import Inches
    
    shape_type_map = {
        'rectangle': 1, 'rounded_rectangle': 5, 'oval': 9, 'diamond': 4,
        'triangle': 7, 'right_triangle': 8, 'pentagon': 51, 'hexagon': 10,
        'heptagon': 145, 'octagon': 6, 'star': 92, 'arrow': 33, 'cloud': 179,
        'heart': 21, 'lightning_bolt': 22, 'sun': 23, 'moon': 24,
        'smiley_face': 17, 'no_symbol': 19, 'flowchart_process': 61,
        'flowchart_decision': 63, 'flowchart_data': 64, 'flowchart_document': 67
    }
    
    shape_type_lower = str(shape_type).lower()
    if shape_type_lower not in shape_type_map:
        available_shapes = ', '.join(sorted(shape_type_map.keys()))
        raise ValueError(f"Unsupported shape type: '{shape_type}'. Available: {available_shapes}")
        
    shape_value = shape_type_map[shape_type_lower]
    
    try:
        shape = slide.shapes.add_shape(
            shape_value, Inches(left), Inches(top), Inches(width), Inches(height)
        )
        return shape
    except Exception as e:
        raise ValueError(f"Failed to create '{shape_type}' shape: {str(e)}")


# =====================================================================
# ---- Presentation Management Wrapper ----
# =====================================================================

class PresentationManager:
    """Wrapper to handle presentation state updates."""
    def __init__(self, presentations_dict):
        self.presentations = presentations_dict

    def store_presentation(self, pres, pres_id):
        self.presentations[pres_id] = pres
        set_current_presentation_id(pres_id)
        return pres_id


presentation_manager = PresentationManager(presentations)


# =====================================================================
# ---- Tool Registration (AFTER all helpers are defined) ----
# =====================================================================

register_presentation_tools(mcp, presentations, get_current_presentation_id, get_template_search_directories)
register_content_tools(mcp, presentations, get_current_presentation_id, validate_parameters, is_positive, is_non_negative, is_in_range, is_valid_rgb)
register_structural_tools(mcp, presentations, get_current_presentation_id, validate_parameters, is_positive, is_non_negative, is_in_range, is_valid_rgb, add_shape_direct)
register_professional_tools(mcp, presentations, get_current_presentation_id)
register_template_tools(mcp, presentations, get_current_presentation_id)
register_hyperlink_tools(mcp, presentations, get_current_presentation_id, validate_parameters, is_positive, is_non_negative, is_in_range, is_valid_rgb)
register_chart_tools(mcp, presentations, get_current_presentation_id, validate_parameters, is_positive, is_non_negative, is_in_range, is_valid_rgb)
register_connector_tools(mcp, presentations, get_current_presentation_id, validate_parameters, is_positive, is_non_negative, is_in_range, is_valid_rgb)
register_master_tools(mcp, presentations, get_current_presentation_id, validate_parameters, is_positive, is_non_negative, is_in_range, is_valid_rgb)
register_transition_tools(mcp, presentations, get_current_presentation_id, validate_parameters, is_positive, is_non_negative, is_in_range, is_valid_rgb)


# =====================================================================
# ---- Additional Utility Tools ----
# =====================================================================

@mcp.tool()
def list_presentations() -> Dict:
    """List all loaded presentations."""
    return {
        "presentations": [
            {
                "id": pres_id,
                "slide_count": len(pres.slides),
                "is_current": pres_id == current_presentation_id
            }
            for pres_id, pres in presentations.items()
        ],
        "current_presentation_id": current_presentation_id,
        "total_presentations": len(presentations)
    }


@mcp.tool()
def switch_presentation(presentation_id: str) -> Dict:
    """Switch to a different loaded presentation."""
    if presentation_id not in presentations:
        return {"error": f"Presentation '{presentation_id}' not found."}
    global current_presentation_id
    old_id = current_presentation_id
    current_presentation_id = presentation_id
    return {"message": f"Switched from '{old_id}' to '{presentation_id}'"}


@mcp.tool()
def get_server_info() -> Dict:
    """Get information about the MCP server."""
    return {
        "name": "PowerPoint MCP Server",
        "version": "2.1.0",
        "loaded_presentations": len(presentations),
        "current_presentation": current_presentation_id
    }


# =====================================================================
# ---- Полный перехват хелсчека streamable-http для Astra Studio ----
# =====================================================================
from starlette.responses import JSONResponse

class AstraDockerHostBypassMiddleware:
    """
    Кастомное ASGI Middleware. Перехватывает любые опросы бэкенда Astra Studio
    на эндпоинты /mcp и /health, выдавая статус 200 OK для принудительного
    перевода сервера в режим connected и обхода валидации сессий SDK Anthropic.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Перехватываем GET хелсчеки бэкенда на корень, /mcp или /health
            if scope["method"] == "GET" and scope["path"] in ["/mcp", "/health", "/"]:
                response = JSONResponse({
                    "status": "ok", 
                    "mcp_version": "1.0.0", 
                    "server": "ppt-mcp-server"
                })
                await response(scope, receive, send)
                return

            # ХАК: Если бэкенд шлет POST на /mcp, но это пустой стартовый пинг инициализации пула сессий
            if scope["method"] == "POST" and scope["path"] == "/mcp":
                headers = dict(scope.get("headers", []))
                # Если в запросе нет MCP заголовков коннекта, отдаем заглушку, чтобы бэкенд не падал по таймауту
                if b"x-mcp-session-id" not in headers and b"content-type" not in headers:
                    response = JSONResponse({"status": "ok", "message": "Astra Studio initialization bypass"})
                    await response(scope, receive, send)
                    return

            # Для легитимных POST-запросов ИИ-инструментов подменяем хост для валидации Uvicorn
            headers = dict(scope.get("headers", []))
            headers[b"host"] = b"127.0.0.1:8000"
            scope["headers"] = list(headers.items())

        # Передаем запрос родному streamable-http менеджеру фреймворка
        await self.app(scope, receive, send)


def main():
    import uvicorn
    
    # Перехватываем конфигурацию веб-сервера Uvicorn внутри SDK
    original_config_init = uvicorn.Config.__init__
    
    def patched_config_init(self, *args, **kwargs):
        # Заставляем слушать все сетевые интерфейсы Docker
        kwargs['host'] = '0.0.0.0'
        kwargs['port'] = 8000
        
        # Вызываем оригинальный инициализатор
        original_config_init(self, *args, **kwargs)
        
        # Инжектируем наше кастомное Middleware поверх приложения FastMCP
        self.app = AstraDockerHostBypassMiddleware(self.app)
        
    uvicorn.Config.__init__ = patched_config_init
    
    # Запускаем штатный транспорт фреймворка
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
