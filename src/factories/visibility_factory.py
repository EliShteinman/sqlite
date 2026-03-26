from src.enums import Environment
from src.handlers.handlers_registry import VISIBILITY_HANDLERS
from src.handlers.visibility.base_visibility_handler import BaseVisibilityHandler
from src.transaction_context import TransactionContext


class VisibilityFactory:
    def create_handlers(
        self,
        field_name: str,
        environment: Environment,
        ctx: TransactionContext | None = None,
    ) -> list[BaseVisibilityHandler]:
        entries = VISIBILITY_HANDLERS.get(field_name, {}).get(environment, [])
        handlers: list[BaseVisibilityHandler] = []
        for entry in entries:
            if entry.requires_dal:
                handlers.append(entry.handler_class(ctx=ctx, **entry.params))
            else:
                handlers.append(entry.handler_class(**entry.params))
        return handlers
