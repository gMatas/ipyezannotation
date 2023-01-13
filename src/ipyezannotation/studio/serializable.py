from abc import ABC, abstractmethod

from ipyezannotation.studio.coders import BaseCoder


class Serializable(ABC):
    @abstractmethod
    def serialize(self, coder: BaseCoder) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: bytes, coder: BaseCoder) -> "Serializable":
        pass
