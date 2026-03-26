from abc import ABC, abstractmethod

from src.handlers.models import BaseFieldRequest, ValidationResponse


class BaseValidationHandler(ABC):
    @abstractmethod
    def validate(self, request: BaseFieldRequest) -> ValidationResponse:
        ...
