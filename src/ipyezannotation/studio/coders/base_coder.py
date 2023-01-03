from abc import ABC, abstractmethod
from typing import Any


class BaseCoder(ABC):
    @abstractmethod
    def encode(self, data: Any) -> bytes:
        pass

    @abstractmethod
    def decode(self, data: bytes) -> Any:
        pass
