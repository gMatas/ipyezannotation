from abc import ABC, abstractmethod
from typing import List

from ipyezannotation.studio.sample import Sample


class BaseDatabase(ABC):
    @abstractmethod
    def sync(self, samples: List[Sample] = None) -> List[Sample]:
        pass

    @abstractmethod
    def update(self, sample: Sample) -> None:
        pass
