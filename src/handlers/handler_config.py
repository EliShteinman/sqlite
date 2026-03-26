from dataclasses import dataclass, field


@dataclass(frozen=True)
class HandlerEntry:
    handler_class: type
    params: dict = field(default_factory=dict)
    requires_dal: bool = False
