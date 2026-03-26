from src.enums import Environment
from src.handlers.handlers_registry import OPTIONS_HANDLERS
from src.handlers.options.base_options_handler import BaseOptionsHandler
from src.transaction_context import TransactionContext


class OptionsFactory:
    def create_handlers(
        self,
        field_name: str,
        environment: Environment,
        ctx: TransactionContext | None = None,
    ) -> list[BaseOptionsHandler]:
        entries = OPTIONS_HANDLERS.get(field_name, {}).get(environment, [])
        handlers: list[BaseOptionsHandler] = []
        for entry in entries:
            if entry.requires_dal:
                handlers.append(entry.handler_class(ctx=ctx, **entry.params))
            else:
                handlers.append(entry.handler_class(**entry.params))
        return handlers
