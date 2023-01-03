from ipywidgets import widgets


class Chip(widgets.Button):
    def __init__(self, description: str = "", chip_style: str = ""):
        super().__init__(
            description=description.upper(),
            disabled=True,
            button_style=chip_style,
            layout=widgets.Layout(width="auto", height="auto", padding="0 8px 0 8px"),
            style={
                "font_weight": "bold",
                "font_size": "12px"
            }
        )
