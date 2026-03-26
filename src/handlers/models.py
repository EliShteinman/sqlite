from pydantic import BaseModel, ConfigDict

from src.enums import Environment
from src.handlers.enums import ValidationStatus


class BaseFieldRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    environment: Environment


class ValidationResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: ValidationStatus
    message: str
