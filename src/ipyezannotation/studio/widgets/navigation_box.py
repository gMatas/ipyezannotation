from typing import Dict

from ipywidgets import widgets


class NavigationBox(widgets.HBox):
    NORMAL_DISPLAY_MODE = "normal"
    COMMAND_DISPLAY_MODE = "command"
    _DISPLAY_MODE_CHANGE_MAP = {
        NORMAL_DISPLAY_MODE: COMMAND_DISPLAY_MODE,
        COMMAND_DISPLAY_MODE: NORMAL_DISPLAY_MODE,
    }

    def __init__(self, display_mode: str = NORMAL_DISPLAY_MODE):
        self._display_mode = display_mode
        self.display_mode_button = widgets.Button(layout=widgets.Layout(width="32px", min_width="32px"))
        self.display_mode_button.on_click(
            lambda _: self.set_display_mode(self._DISPLAY_MODE_CHANGE_MAP[self._display_mode])
        )

        self.prev_button = widgets.Button(tooltip="Left", icon="arrow-left")
        self.next_button = widgets.Button(tooltip="Right", icon="arrow-right")
        self.speed_toggle_button = widgets.ToggleButton(
            value=False,
            tooltip="Super mode",
            icon="bolt",
            layout=widgets.Layout(width="32px", min_width="32px")
        )
        self.speed_toggle_button.observe(self._handle_speed_toggle_button_change, names="value")

        self.command_text = widgets.Text(
            placeholder="Enter command...",
            continuous_update=False,
            layout=widgets.Layout(width="100%")
        )
        self.command_submit_button = widgets.Button(icon="check", layout=widgets.Layout(width="32px", min_width="32px"))

        super().__init__(layout=widgets.Layout(width="300px"))
        self.set_display_mode(self._display_mode, force=True)

    @property
    def display_mode(self) -> str:
        return self._display_mode

    @property
    def fast_mode(self) -> bool:
        return self.speed_toggle_button.value

    @fast_mode.setter
    def fast_mode(self, value: bool) -> None:
        self.speed_toggle_button.value = value

    def set_display_mode(self, mode: str, force: bool = False) -> None:
        if not force and mode == self._display_mode:
            return
        elif mode == self.NORMAL_DISPLAY_MODE:
            self.display_mode_button.tooltip = "Command mode"
            self.display_mode_button.icon = "terminal"
            self.children = [self.prev_button, self.next_button, self.speed_toggle_button, self.display_mode_button]
            self.layout = widgets.Layout(width="300px")
        elif mode == self.COMMAND_DISPLAY_MODE:
            self.command_text.value = ""
            self.display_mode_button.tooltip = "Normal mode"
            self.display_mode_button.icon = "times"
            self.children = [self.command_text, self.command_submit_button, self.display_mode_button]
            self.layout = widgets.Layout(width="300px")

        self._display_mode = mode

    def _handle_speed_toggle_button_change(self, change: Dict) -> None:
        new_toggle_value = change["new"]
        self.speed_toggle_button.button_style = "warning" if new_toggle_value else ""
