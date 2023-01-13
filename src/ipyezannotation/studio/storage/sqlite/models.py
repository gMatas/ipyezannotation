import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from ipyezannotation.studio.coders import BaseCoder
from ipyezannotation.studio.sample import Sample, SampleStatus


class SampleModel(SQLModel, table=True):
    sample_id: str = Field(primary_key=True)
    status: str
    data: bytes
    annotation: Optional[bytes]
    completed_at: Optional[datetime.datetime]

    def to_sample(self, *, coder: BaseCoder) -> Sample:
        return Sample(
            status=SampleStatus(self.status),
            data=coder.decode(self.data),
            annotation=None if self.annotation is None else coder.decode(self.annotation)
        )

    @classmethod
    def from_sample(cls, sample: Sample, *, coder: BaseCoder) -> "SampleModel":
        return cls(
            sample_id=sample.identity(coder),
            status=sample.status.value,
            data=coder.encode(sample.data),
            annotation=None if sample.annotation is None else coder.encode(sample.annotation),
            completed_at=None
        )
