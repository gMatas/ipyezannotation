from ipywidgets import widgets


class NavigationBox(widgets.HBox):
    NORMAL_MODE = "normal"
    COMMAND_MODE = "command"
    _MODE_CHANGE_MAP = {
        NORMAL_MODE: COMMAND_MODE,
        COMMAND_MODE: NORMAL_MODE,
    }

    def __init__(self, mode: str = NORMAL_MODE):
        self._mode = mode
        self.mode_button = widgets.Button(layout=widgets.Layout(width="32px", min_width="32px"))
        self.mode_button.on_click(lambda _: self.set_mode(self._MODE_CHANGE_MAP[self._mode]))

        self.next_button = widgets.Button(icon="arrow-right")
        self.prev_button = widgets.Button(icon="arrow-left")

        self.command_text = widgets.Text(
            placeholder="Enter command...",
            continuous_update=False,
            layout=widgets.Layout(width="100%")
        )
        self.command_submit_button = widgets.Button(icon="check", layout=widgets.Layout(width="32px", min_width="32px"))

        super().__init__(layout=widgets.Layout(width="300px"))
        self.set_mode(self._mode, force=True)

    @property
    def mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str, force: bool = False) -> None:
        if not force and mode == self._mode:
            return
        elif mode == self.NORMAL_MODE:
            self.mode_button.tooltip = "Search"
            self.mode_button.icon = "search"
            self.children = [self.prev_button, self.next_button, self.mode_button]
            self.layout = widgets.Layout(width="300px")
        elif mode == self.COMMAND_MODE:
            self.command_text.value = ""
            self.mode_button.tooltip = "Back"
            self.mode_button.icon = "times"
            self.children = [self.command_text, self.command_submit_button, self.mode_button]
            self.layout = widgets.Layout(width="300px")

        self._mode = mode
