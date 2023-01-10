from typing import Callable

from ipywidgets import widgets


class ToggleButton(widgets.Button):
    def __init__(
            self,
            value: bool = False,
            *,
            selected_button_callback: Callable = None,
            unselected_button_callback: Callable = None,
            **kwargs
    ):
        self._value = value
        self._selected_button_callback = selected_button_callback or self._default_selected_button_callback
        self._unselected_button_callback = unselected_button_callback or self._default_unselected_button_callback
        super().__init__(**kwargs)
        self.on_click(lambda _: self._select(not self._value))
        self._select(self._value)

    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, value: bool) -> None:
        self._select(value)

    def _select(self, value: bool) -> None:
        self._value = value
        if self._value:
            self._default_selected_button_callback()
        else:
            self._default_unselected_button_callback()

    def _default_selected_button_callback(self) -> None:
        self.button_style = "info"

    def _default_unselected_button_callback(self) -> None:
        self.button_style = ""
