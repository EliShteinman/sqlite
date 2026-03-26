from abc import ABC, abstractmethod

from src.handlers.models import BaseFieldRequest


class BaseDefaultsHandler(ABC):
    @abstractmethod
    def get_default(self, request: BaseFieldRequest) -> str:
        ...
