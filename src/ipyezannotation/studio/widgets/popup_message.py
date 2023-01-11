import uuid
from typing import Callable

from ipywidgets import widgets


class PopupMessage(widgets.HBox):
    def __init__(self, html_value: str, kind: str = "info", message_id: str = None):
        self.message_id = message_id or str(uuid.uuid4())
        self._close_callbacks = []

        if kind == "danger":
            button_style = "danger"
            background = "mistyrose"
        elif kind == "success":
            button_style = "success"
            background = "lightgoldenrodyellow"
        elif kind == "info":
            button_style = "info"
            background = "aliceblue"
        else:
            raise ValueError(f"Invalid message {kind=}. Can't display the message.")

        close_button = widgets.Button(
            button_style=button_style,
            layout=widgets.Layout(width="0", height="auto", padding="4px")
        )
        close_button.on_click(lambda _: self.close_message())

        super().__init__(
            [
                close_button,
                widgets.HTML(
                    html_value,
                    style={
                        "text_color": "black",
                        "background": background
                    },
                    layout=widgets.Layout(width="100%", padding="4px")
                )
            ]
        )

    def close_message(self) -> None:
        for callback in self._close_callbacks:
            callback(self)

    def on_close(self, callback: Callable[["PopupMessage"], None], *, remove: bool = False) -> None:
        if remove:
            self._close_callbacks.remove(callback)
            return

        self._close_callbacks.append(callback)
