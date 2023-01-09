import math
from dataclasses import dataclass
from typing import Callable, List, Tuple

from ipywidgets import widgets

from ipyezannotation.widgets.image_select import ImageSelect


class ImageSelectGallery(widgets.GridspecLayout):
    @dataclass
    class Item:
        selected: bool
        image: bytes
        format: str = None

        def __repr__(self) -> str:
            return (
                f"{self.__class__.__qualname__}("
                f"selected={self.selected}, "
                f"image=<bytes length={len(self.image)}>, "
                f"format={self.format}"
                ")"
            )

    def __init__(self, items: List[Item], n_rows: int = None, n_columns: int = None, grid_gap="8px", **kwargs):
        n_items = len(items)
        if not (n_rows or n_columns):
            raise ValueError("Either n_rows or n_columns must be not None.")
        if n_rows is None:
            n_rows = math.ceil(n_items / n_columns)
        else:
            n_columns = math.ceil(n_items / n_rows)

        if n_items > n_rows * n_columns:
            raise ValueError("There are more items than allocated grid cells.")

        super().__init__(n_rows, n_columns, **{"grid_gap": grid_gap, **kwargs})
        self._populate_grid(items, n_rows, n_columns)

        self._select_all_hooks: List[Callable[["ImageSelectGallery"], None]] = []
        self._select_item_hooks: List[Callable[[int, ImageSelect], None]] = []

        def create_select_callback(index: int, widget: ImageSelect):
            def callback(*args):
                select_hooks = [self._select_item] + self._select_item_hooks
                for hook in select_hooks:
                    hook(index, widget)  # noqa: ignore false "Unexpected argument" warning

            return callback

        self._selected = [child.selected for child in self.children]
        for i, image_select in enumerate(self.children):
            image_select.on_select(create_select_callback(i, image_select))

    @property
    def selected(self) -> Tuple[bool, ...]:
        return tuple(self._selected)

    def is_selected(self, index: int) -> bool:
        return self._selected[index]

    def select(self, index: int, selected: bool = True, *, skip_callback: bool = False) -> None:
        item = self.children[index]
        item.select(selected, skip_callback=skip_callback)
        self._selected[index] = item.selected

    def selectall(self, *, skip_callback: bool = False) -> None:
        for index, item in enumerate(self.children):
            item.select(True, skip_callback=True)
            self._selected[index] = True

        for hook in self._select_all_hooks:
            hook(self)

    def unselectall(self, *, skip_callback: bool = False) -> None:
        for index, item in enumerate(self.children):
            item.select(False, skip_callback=True)
            self._selected[index] = False

        for hook in self._select_all_hooks:
            hook(self)

    def on_select_item(self, callback: Callable[[int, ImageSelect], None]) -> None:
        self._select_item_hooks.append(callback)

    def on_select_all(self, callback: Callable[["ImageSelectGallery"], None]) -> None:
        self._select_all_hooks.append(callback)

    @staticmethod
    def _make_item_widget(item: Item) -> ImageSelect:
        image_kwargs = {
            "width": "auto"
        }
        if item.format is not None:
            image_kwargs["format"] = item.format

        return ImageSelect(
            selected=item.selected,
            data=item.image,
            image_kwargs=image_kwargs
        )

    def _populate_grid(self, items: List[Item], n_rows: int, n_columns: int) -> None:
        n_items = len(items)
        i_item = 0
        for i in range(n_rows):
            for j in range(n_columns):
                if i_item >= n_items:
                    return
                self[i, j] = self._make_item_widget(items[i_item])
                i_item += 1

    def _select_item(self, index: int, widget: ImageSelect) -> None:
        self._selected[index] = widget.selected
