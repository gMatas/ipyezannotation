from abc import ABC, abstractmethod
from typing import List

from ipyezannotation.studio.coders import BaseCoder
from ipyezannotation.studio.sample import Sample


class BaseDatabase(ABC):
    @property
    @abstractmethod
    def coder(self) -> BaseCoder:
        pass

    @abstractmethod
    def sync(self, samples: List[Sample] = None) -> List[Sample]:
        pass

    @abstractmethod
    def update(self, sample: Sample) -> None:
        pass
