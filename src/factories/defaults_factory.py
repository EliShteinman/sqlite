from src.enums import Environment
from src.handlers.handlers_registry import DEFAULTS_HANDLERS
from src.handlers.defaults.base_defaults_handler import BaseDefaultsHandler
from src.transaction_context import TransactionContext


class DefaultsFactory:
    def create_handlers(
        self,
        field_name: str,
        environment: Environment,
        ctx: TransactionContext | None = None,
    ) -> list[BaseDefaultsHandler]:
        entries = DEFAULTS_HANDLERS.get(field_name, {}).get(environment, [])
        handlers: list[BaseDefaultsHandler] = []
        for entry in entries:
            if entry.requires_dal:
                handlers.append(entry.handler_class(ctx=ctx, **entry.params))
            else:
                handlers.append(entry.handler_class(**entry.params))
        return handlers
