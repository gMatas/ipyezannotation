from typing import List, Sequence, Tuple

from ipywidgets import widgets


class MultiProgress(widgets.HBox):
    def __init__(self, values: List[float], max_value: float = 1):
        self._validate_values(values, max_value)
        super().__init__(
            [
                widgets.FloatProgress(
                    value=0,
                    min=0,
                    max=1,
                    layout=widgets.Layout(margin="0 0 0 0")
                )
                for _ in range(len(values))
            ],
            layout=widgets.Layout(width="300px")
        )
        self._values = values
        self._max_value = max_value
        self.update()

    @property
    def max_value(self) -> float:
        return self._max_value

    @max_value.setter
    def max_value(self, value: float) -> None:
        self._validate_values(self._values, value)
        self._max_value = value
        self.update()

    @property
    def values(self) -> Tuple[float]:
        return tuple(self._values)

    @values.setter
    def values(self, values: Sequence[float]) -> None:
        self._validate_values(values, self._max_value)
        self._values = list(values)
        self.update()

    def update(self) -> None:
        bar_values, bar_widths = self._compute_progress_bar_params(self._values, self._max_value)
        for bar, value, width in zip(self.children, bar_values, bar_widths):
            bar.value = value
            bar.layout.width = f"{width * 100}%"

    @staticmethod
    def _validate_values(values: Sequence[float], max_value: float) -> None:
        if not all(0 <= value <= max_value for value in values):
            raise ValueError(f"Given values must be in range of [0, {max_value=}].")
        if (values_sum := sum(values)) > max_value:
            raise ValueError(
                f"Sum of given values {values_sum} can not be "
                f"greater to that of {max_value=}."
            )

    @staticmethod
    def _compute_progress_bar_params(
            values: List[float],
            max_value: float,
            *,
            eps: float = 1e-6
    ) -> Tuple[List[float], List[float]]:
        # Normalize values.
        values = [value / max_value for value in values]

        # Compute bar widgets' widths.
        last_width = 1 - sum(values[:-1])
        if abs(1 - last_width) <= eps:
            last_width = 0

        bar_widths = values[:-1] + [last_width]

        # Compute bar widgets' values.
        last_value = values[-1] if last_width == 0 else (values[-1] / last_width)
        bar_values = [1.0] * (len(values) - 1) + [last_value]

        return bar_values, bar_widths
