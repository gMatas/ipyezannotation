from typing import Any, Callable

from ipywidgets import widgets


class AbstractAnnotator:
    def get_data(self) -> Any:
        raise NotImplementedError

    def set_data(self, data: Any) -> None:
        raise NotImplementedError

    def validate(self, *, on_error: Callable[[str], None] = None) -> bool:
        return True

    def clear(self) -> None:
        self.set_data(None)


class BaseAnnotator(AbstractAnnotator):  # noqa: ignore linter wanting this class to inherit from `abc.ABC`
    def __init__(self, display_function: Callable[[Any], None]):
        self._display_output = widgets.Output()
        self._display_function = display_function

    @property
    def display_widget(self) -> widgets.Output:
        return self._display_output

    def display(self, item: Any) -> None:
        self.clear()
        self._display_output.clear_output(wait=True)
        with self._display_output:
            self._display_function(item)
