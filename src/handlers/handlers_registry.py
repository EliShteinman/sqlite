from src.enums import Environment
from src.handlers.handler_config import HandlerEntry


VALIDATION_HANDLERS: dict[str, dict[Environment, list[HandlerEntry]]] = {}

OPTIONS_HANDLERS: dict[str, dict[Environment, list[HandlerEntry]]] = {}

VISIBILITY_HANDLERS: dict[str, dict[Environment, list[HandlerEntry]]] = {}

DEFAULTS_HANDLERS: dict[str, dict[Environment, list[HandlerEntry]]] = {}
