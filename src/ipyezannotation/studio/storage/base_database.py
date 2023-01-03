from abc import ABC, abstractmethod
from typing import Union

from ipyezannotation.studio.sample import Sample


class BaseDatabase(ABC):
    @abstractmethod
    def sync(self, samples: list[Sample] = None) -> list[Sample]:
        pass

    @abstractmethod
    def add(self, sample: Sample) -> None:
        pass

    def add_all(self, samples: list[Sample]) -> None:
        for sample in samples:
            self.add(sample)

    @abstractmethod
    def get(self, sample_id: str) -> Sample:
        pass

    @abstractmethod
    def get_all(self, sample_ids: list[str]) -> list[Sample]:
        pass

    @abstractmethod
    def get_existing_ids(self) -> list[str]:
        pass

    @abstractmethod
    def update(self, sample: Sample) -> None:
        pass

    @abstractmethod
    def remove(self, sample: Union[str, Sample]) -> None:
        pass
