from abc import ABC, abstractmethod

from src.handlers.models import BaseFieldRequest


class BaseOptionsHandler(ABC):
    @abstractmethod
    def get_options(self, request: BaseFieldRequest) -> list[str]:
        ...
