from abc import ABC, abstractmethod

from src.handlers.models import BaseFieldRequest


class BaseVisibilityHandler(ABC):
    @abstractmethod
    def is_visible(self, request: BaseFieldRequest) -> bool:
        ...
