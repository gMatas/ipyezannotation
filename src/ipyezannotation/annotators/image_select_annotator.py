import os
from typing import Dict, List, Optional

import IPython.display
from ipywidgets import widgets

from ipyezannotation.annotators.base_annotator import BaseAnnotator
from ipyezannotation.widgets.image_select_gallery import ImageSelectGallery


class ImageSelectAnnotator(BaseAnnotator):
    def __init__(self, n_rows: int = None, n_columns: int = None):
        self._n_rows = n_rows
        self._n_columns = n_columns
        self._gallery_widget: Optional[ImageSelectGallery] = None
        super().__init__(display_function=self._display)

    def get_data(self) -> Optional[Dict]:
        if self._gallery_widget:
            return {"selected": self._gallery_widget.selected}

    def set_data(self, data: Optional[Dict]) -> None:
        if not self._gallery_widget:
            # No data can be set while gallery widget is not created.
            return

        if data is None:
            data = {"selected": [False] * len(self._gallery_widget.selected)}

        for index, value in enumerate(data["selected"]):
            self._gallery_widget.select(index, value, skip_callback=False)

    def _display(self, image_paths: List[str]) -> None:
        self._gallery_widget = self._create_gallery(image_paths)
        gallery_controls = self._create_gallery_controls(self._gallery_widget)
        gallery_with_controls = widgets.VBox([gallery_controls, widgets.HTML("<hr/>"), self._gallery_widget])
        IPython.display.display(gallery_with_controls)

    def _create_gallery(self, image_paths: List[str]) -> ImageSelectGallery:
        gallery_items = []
        for image_path in image_paths:
            image_encoding = os.path.splitext(image_path)[1].lstrip(os.path.extsep)
            with open(image_path, "rb") as file:
                gallery_items.append(
                    ImageSelectGallery.Item(
                        selected=False,
                        image=file.read(),
                        format=image_encoding
                    )
                )

        return ImageSelectGallery(gallery_items, n_rows=self._n_rows, n_columns=self._n_columns)

    @staticmethod
    def _create_gallery_controls(gallery: ImageSelectGallery) -> widgets.HBox:
        """Create top level controls for gallery widget.
        """
        select_all_button = widgets.Button(description="All", layout=widgets.Layout(width="4em"))
        select_all_button.on_click(lambda _: gallery.selectall())

        select_none_button = widgets.Button(description="None", layout=widgets.Layout(width="4em"))
        select_none_button.on_click(lambda _: gallery.unselectall())

        return widgets.HBox([select_all_button, select_none_button])
