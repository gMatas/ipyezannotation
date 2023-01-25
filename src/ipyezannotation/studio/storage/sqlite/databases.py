from typing import List, Union

import sqlmodel

from ipyezannotation.studio.coders import BaseCoder, JsonCoder
from ipyezannotation.studio.sample import Sample
from ipyezannotation.studio.storage.base_database import BaseDatabase
from ipyezannotation.studio.storage.sqlite.models import SampleModel


class SQLiteDatabase(BaseDatabase):
    def __init__(self, url: str = "sqlite:///:memory:", coder: BaseCoder = None):
        self._coder = coder or JsonCoder()

        # Setup SQLite database engine.
        self._engine = sqlmodel.create_engine(url)
        SampleModel.metadata.create_all(self._engine)

    @property
    def coder(self) -> BaseCoder:
        return self._coder

    def sync(self, samples: List[Sample] = None) -> List[Sample]:
        existing_ids = self.get_existing_ids()
        if samples:
            provided_samples = {sample.identity(self._coder): sample for sample in samples}
            provided_ids = set(provided_samples.keys())

            # Add new samples.
            missing_ids = provided_ids.difference(existing_ids)
            missing_samples = [provided_samples[sample_id] for sample_id in missing_ids]
            self.add_all(missing_samples)

            # Update existing samples with new data.
            matched_ids = provided_ids.intersection(existing_ids)
            for sample_id in matched_ids:
                sample = provided_samples[sample_id]
                self.update(sample)

        # Retrieve all samples.
        samples = self.get_all(existing_ids)
        return samples

    def add(self, sample: Sample) -> None:
        model = SampleModel.from_sample(sample, coder=self._coder)
        with sqlmodel.Session(self._engine) as session:
            session.add(model)
            session.commit()

    def add_all(self, samples: List[Sample]) -> None:
        models = [SampleModel.from_sample(sample, coder=self._coder) for sample in samples]
        with sqlmodel.Session(self._engine) as session:
            session.add_all(models)
            session.commit()

    def get(self, sample_id: str) -> Sample:
        statement = sqlmodel.select(SampleModel).where(SampleModel.sample_id == sample_id)
        with sqlmodel.Session(self._engine) as session:
            model = session.exec(statement).one()

        sample = model.to_sample(coder=self._coder)
        return sample

    def get_all(self, sample_ids: List[str]) -> List[Sample]:
        statement = sqlmodel.select(SampleModel)
        with sqlmodel.Session(self._engine) as session:
            models = session.exec(statement).all()

        samples = [model.to_sample(coder=self._coder) for model in models]
        return samples

    def get_existing_ids(self) -> List[str]:
        statement = sqlmodel.select(SampleModel.sample_id)
        with sqlmodel.Session(self._engine) as session:
            return session.exec(statement).all()

    def update(self, sample: Sample) -> None:
        model = SampleModel.from_sample(sample, coder=self._coder)
        statement = sqlmodel.update(
            SampleModel
        ).values(
            {
                "status": model.status,
                "annotation": model.annotation,
                "completed_at": model.completed_at
            }
        ).where(
            SampleModel.sample_id == model.sample_id
        )
        with sqlmodel.Session(self._engine) as session:
            session.execute(statement)
            session.commit()

    def remove(self, sample: Union[str, Sample]) -> None:
        sample_id = sample
        if isinstance(sample, Sample):
            sample_id = sample.identity(coder=self._coder)

        statement = sqlmodel.select(SampleModel).where(SampleModel.sample_id == sample_id)
        with sqlmodel.Session(self._engine) as session:
            model = session.exec(statement).one()
            session.delete(model)
            session.commit()
