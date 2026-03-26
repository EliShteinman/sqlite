from src.enums import Environment
from src.handlers.handlers_registry import VALIDATION_HANDLERS
from src.handlers.validation.base_validation_handler import BaseValidationHandler
from src.transaction_context import TransactionContext


class ValidationFactory:
    def create_handlers(
        self,
        field_name: str,
        environment: Environment,
        ctx: TransactionContext | None = None,
    ) -> list[BaseValidationHandler]:
        entries = VALIDATION_HANDLERS.get(field_name, {}).get(environment, [])
        handlers: list[BaseValidationHandler] = []
        for entry in entries:
            if entry.requires_dal:
                handlers.append(entry.handler_class(ctx=ctx, **entry.params))
            else:
                handlers.append(entry.handler_class(**entry.params))
        return handlers
