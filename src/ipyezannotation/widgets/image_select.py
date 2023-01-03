from typing import Callable, Optional

from ipywidgets import widgets


class ImageSelect(widgets.VBox):
    _IS_SELECTED_STYLE = "info"
    _NOT_SELECTED_STYLE = ""

    def __init__(self, selected: bool, data: bytes, image_kwargs: dict):
        self._selected = selected
        self._button = widgets.Button(
            icon="check",
            button_style=self._get_button_style(),
            layout=widgets.Layout(width="auto")
        )
        self._image = widgets.Image(value=data, **image_kwargs)
        super().__init__([self._button, self._image], layout=widgets.Layout(display="inline-flex"))

        self._select_callback: Optional[Callable[["ImageSelect"], None]] = None
        self._button.on_click(lambda _: self._select())

    @property
    def selected(self) -> bool:
        return self._selected

    def select(self, value: bool = True, *, skip_callback: bool = False) -> None:
        self._selected = value
        self._button.button_style = self._get_button_style()
        if not skip_callback and self._select_callback:
            self._select_callback(self)

    def on_select(self, callback: Callable[["ImageSelect"], None] = None) -> None:
        self._select_callback = callback

    def _select(self) -> None:
        self.select(not self._selected, skip_callback=False)

    def _get_button_style(self) -> str:
        return self._IS_SELECTED_STYLE if self._selected else self._NOT_SELECTED_STYLE
