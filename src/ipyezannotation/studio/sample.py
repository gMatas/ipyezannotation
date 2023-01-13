import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from ipyezannotation.studio.coders import BaseCoder
from ipyezannotation.studio.serializable import Serializable


class SampleStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DROPPED = "dropped"


@dataclass
class Sample(Serializable):
    status: SampleStatus
    data: Any
    annotation: Optional[Any]

    def identity(self, coder: BaseCoder) -> str:
        return hashlib.md5(coder.encode(self.data)).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "data": self.data,
            "annotation": self.annotation
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Sample":
        return cls(
            status=SampleStatus(data["status"]),
            data=data["data"],
            annotation=data["annotation"]
        )

    def serialize(self, coder: BaseCoder) -> bytes:
        return coder.encode(self.to_dict())

    @classmethod
    def deserialize(cls, data: bytes, coder: BaseCoder) -> "Sample":
        return cls.from_dict(coder.decode(data))
