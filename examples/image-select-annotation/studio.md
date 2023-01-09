# Images selection annotation

Annotation using `ImageSelectAnnotator`.


```python
source_groups = [
    ["./surprized-pikachu.png"] * 16,
    ["./surprized-pikachu.png"] * 7,
    ["./surprized-pikachu.png"] * 8,
    ["./surprized-pikachu.png"] * 4,
]
```


```python
from ipyezannotation.studio.sample import Sample, SampleStatus

samples = [
    Sample(
        status=SampleStatus.PENDING,
        data=group,
        annotation=None
    )
    for group in source_groups
]
```


```python
from ipyezannotation.studio.storage.sqlite import SQLiteDatabase

samples_db = SQLiteDatabase("sqlite:///:memory:")
synced_samples = samples_db.sync(samples)
```


```python
from ipyezannotation.studio import Studio
from ipyezannotation.annotators import ImageSelectAnnotator

studio = Studio(
    annotator=ImageSelectAnnotator(n_columns=8),
    database=samples_db
)
studio
```

![](C:\Users\matas\Documents\Work\ipyezannotation\examples\image-select-annotation\output.png)
