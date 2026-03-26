from enum import Enum


class ValidationStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    DANGER = "danger"
