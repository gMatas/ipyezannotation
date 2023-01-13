from typing import Dict, Optional, Sequence

from ipywidgets import widgets

from ipyezannotation.annotators.base_annotator import BaseAnnotator
from ipyezannotation.studio.sample import Sample, SampleStatus
from ipyezannotation.studio.storage.base_database import BaseDatabase
from ipyezannotation.studio.storage.sqlite import SQLiteDatabase
from ipyezannotation.studio.widgets.chip import Chip
from ipyezannotation.studio.widgets.navigation_box import NavigationBox
from ipyezannotation.studio.widgets.popup_message import PopupMessage
from ipyezannotation.utils.index_counter import IndexCounter
from ipyezannotation.widgets.multi_progress import MultiProgress


class Studio(widgets.VBox):
    # Progress box display modes.
    PROGRESS_BOX_INLINE_DISPLAY_MODE = "inline"
    PROGRESS_BOX_BLOCK_DISPLAY_MODE = "block"
    # Progress bar configuration.
    _COMPLETED_BAR_INDEX = 0
    _DROPPED_BAR_INDEX = 1
    _FILLED_STATUS_INDEX_MAP = {
        SampleStatus.COMPLETED: _COMPLETED_BAR_INDEX,
        SampleStatus.DROPPED: _DROPPED_BAR_INDEX
    }

    def __init__(
            self,
            annotator: BaseAnnotator,
            database: BaseDatabase = None,
            samples: Sequence[Sample] = None,
            *,
            display_progress: Optional[str] = PROGRESS_BOX_INLINE_DISPLAY_MODE
    ):
        # Setup core annotation components.
        self._annotator = annotator
        self._database = database or SQLiteDatabase()
        self._samples = self._database.sync(samples or [])
        self._sample_indexer = IndexCounter(
            length=len(self._samples),
            start=0,
            circular=True
        )
        if not self._samples:
            raise ValueError("No samples are available.")

        # Setup message component.
        self._message_box = widgets.VBox()
        self._message_register: Dict[str, PopupMessage] = {}

        # Setup progress bar.
        self._progress_bar = MultiProgress([0, 0], max_value=len(self._samples))
        self._progress_bar.children[self._COMPLETED_BAR_INDEX].bar_style = ""
        self._progress_bar.children[self._DROPPED_BAR_INDEX].bar_style = "danger"

        # Setup progress text.
        self._completed_progress_text = widgets.Label(style={"text_color": "green"})
        self._dropped_progress_text = widgets.Label(style={"text_color": "red"})
        self._total_progress_text = widgets.Label()

        # Setup progress component.
        progress_box = self._compile_progress_box(display_progress)

        # Setup navigation component.
        self._navigation_box = NavigationBox(display_mode=NavigationBox.NORMAL_DISPLAY_MODE)
        self._navigation_box.next_button.on_click(lambda _: self.navigate_forward())
        self._navigation_box.prev_button.on_click(lambda _: self.navigate_backward())
        self._navigation_box.command_submit_button.on_click(lambda _: self._handle_navigation_command())

        # Setup actions component.
        self._submit_action_button = widgets.Button(description="Submit", icon="check", button_style="success")
        self._submit_action_button.on_click(lambda _: self.submit_annotation())
        self._drop_action_button = widgets.Button(description="Drop", icon="trash", button_style="danger")
        self._drop_action_button.on_click(lambda _: self.drop_annotation())
        self._clear_action_button = widgets.Button(description="Clear", icon="times")
        self._clear_action_button.on_click(lambda _: self.clear_annotation())
        self._actions_box = widgets.HBox(
            [
                self._clear_action_button,
                self._submit_action_button,
                self._drop_action_button
            ]
        )

        # Setup current sample status component.
        self._sample_status_chips = {
            SampleStatus.PENDING: Chip(SampleStatus.PENDING.value, chip_style=""),
            SampleStatus.DROPPED: Chip(SampleStatus.DROPPED.value, chip_style="danger"),
            SampleStatus.COMPLETED: Chip(SampleStatus.COMPLETED.value, chip_style="success")
        }
        self._sample_status_box = widgets.HBox()

        # Setup current sample location component.
        self._sample_location_chip = Chip()

        # Compile all studio components.
        annotator_widget = self._annotator
        if not isinstance(self._annotator, widgets.Widget):
            annotator_widget = self._annotator.display_widget

        compiled_widgets = [self._message_box]

        if progress_box:
            compiled_widgets.append(progress_box)

        compiled_widgets.extend(
            [
                widgets.HBox(
                    [
                        self._navigation_box,
                        self._actions_box
                    ]
                ),
                widgets.HBox(
                    [
                        self._sample_location_chip,
                        self._sample_status_box
                    ]
                ),
                annotator_widget,
            ]
        )

        super().__init__(compiled_widgets)
        self.update()
        self.update_progress()

    def update(self, *, display: bool = True, status: bool = True, location: bool = True) -> None:
        sample_index = self._sample_indexer.index
        sample = self._samples[sample_index]
        if display:
            self._annotator.display(sample.data)
            self._annotator.set_data(sample.annotation)

        if status:
            self.update_status()

        if location:
            self.update_location()

        # Show message that all samples were annotated. Only one such message is displayed at a time.
        annotation_complete_message_id = "annotation-complete"
        if abs(sum(self._progress_bar.values) - self._progress_bar.max_value) < 1e-6:
            self.display_message(
                f"<p><b>All samples annotated! 🎉</b></p>",
                kind="success",
                message_id=annotation_complete_message_id
            )
        elif annotation_complete_message_id in self._message_register:
            self._message_register[annotation_complete_message_id].close_message()

    def update_location(self) -> None:
        self._sample_location_chip.description = f"{self._sample_indexer.index + 1} / {self._sample_indexer.length}"

    def update_status(self) -> None:
        sample = self._samples[self._sample_indexer.index]
        status = sample.status
        self._sample_status_box.children = [self._sample_status_chips[status]]

    def navigate_forward(self) -> None:
        prev_index = self._sample_indexer.index
        if self._navigation_box.fast_mode:
            self._seek_sample(SampleStatus.PENDING)
        else:
            self._sample_indexer.step(1)

        self.update()

    def navigate_backward(self) -> None:
        if self._navigation_box.fast_mode:
            self._seek_sample(SampleStatus.PENDING, forward=False)
        else:
            self._sample_indexer.step(-1)

        self.update()

    def _seek_sample(self, status: SampleStatus, forward: bool = True) -> None:
        step = 1 if forward else -1
        for i in range(self._sample_indexer.length):
            self._sample_indexer.step(step)
            sample = self._samples[self._sample_indexer.index]
            if sample.status == status:
                return

    def submit_annotation(self) -> None:
        # Validate data annotated data before submitting it.
        if not self._annotator.validate(on_error=self._handle_annotator_validation_error_message):
            return

        sample = self._samples[self._sample_indexer.index]
        old_status = sample.status
        sample.status = SampleStatus.COMPLETED
        sample.annotation = self._annotator.get_data()
        self._database.update(sample)
        self._count_sample_progress(old_status, sample.status)
        self.update(display=False, location=False)

    def _handle_annotator_validation_error_message(self, message: str) -> None:
        self.display_message(f"<p style='color: red'><b>Invalid annotator data!</b><br>{message}<p>")

    def drop_annotation(self) -> None:
        sample = self._samples[self._sample_indexer.index]
        old_status = sample.status
        sample.status = SampleStatus.DROPPED
        self._database.update(sample)
        self._count_sample_progress(old_status, sample.status)
        self.update(display=False, location=False)

    def clear_annotation(self) -> None:
        sample = self._samples[self._sample_indexer.index]
        old_status = sample.status
        sample.status = SampleStatus.PENDING
        self._annotator.clear()
        sample.annotation = self._annotator.get_data()
        self._database.update(sample)
        self._count_sample_progress(old_status, sample.status)
        self.update(display=False, location=False)

    def update_progress(self, completed: int = None, dropped: int = None, total: int = None) -> None:
        new_values = list(self._progress_bar.values)
        if completed is not None:
            new_values[self._COMPLETED_BAR_INDEX] = completed
        if dropped is not None:
            new_values[self._DROPPED_BAR_INDEX] = dropped
        if total is not None:
            self._progress_bar.max_value = total

        if all([value is None for value in (completed, dropped, total)]):
            # Count by rescanning all the samples.
            counts = {status: 0 for status in SampleStatus}
            for sample in self._samples:
                counts[sample.status] += 1

            completed = counts[SampleStatus.COMPLETED]
            dropped = counts[SampleStatus.DROPPED]
            self.update_progress(
                completed=completed,
                dropped=dropped,
                total=completed + dropped + counts[SampleStatus.PENDING]
            )
        else:
            # Update progress bar widget.
            self._progress_bar.values = new_values

            # Update progress text widgets.
            completed = new_values[self._COMPLETED_BAR_INDEX]
            dropped = new_values[self._DROPPED_BAR_INDEX]
            total = int(self._progress_bar.max_value)
            self._update_progress_text(completed, dropped, total)

    def display_message(self, html_value: str, kind: str = "danger", message_id: str = None) -> None:
        """Display HTML message and register it.
        """
        popup_message = PopupMessage(html_value=html_value, kind=kind, message_id=message_id)
        if popup_message.message_id in self._message_register:
            # Do not display the message if it is already being displayed.
            return

        def remove_message_item(message: PopupMessage) -> None:
            # Unregister message.
            self._message_register.pop(message.message_id)
            # Remove message from the message box.
            items_ = list(self._message_box.children)
            items_.remove(message)
            self._message_box.children = items_

        popup_message.on_close(remove_message_item)

        # Register new message.
        self._message_register[popup_message.message_id] = popup_message

        # Add message item to the beginning of the main messages box.
        items = list(self._message_box.children)
        items.append(popup_message)
        self._message_box.children = items

    def _count_sample_progress(self, old_status: SampleStatus, new_status: SampleStatus) -> None:
        # Compute deltas how change of sample status from the old to
        # the new one will affect progress bar values.
        deltas = [0, 0]
        if old_status != SampleStatus.PENDING:
            deltas[self._FILLED_STATUS_INDEX_MAP[old_status]] -= 1
        if new_status != SampleStatus.PENDING:
            deltas[self._FILLED_STATUS_INDEX_MAP[new_status]] += 1

        # Apply the derived deltas to the progress bar values.
        values = [value + delta for value, delta in zip(self._progress_bar.values, deltas)]
        self.update_progress(
            completed=int(values[self._COMPLETED_BAR_INDEX]),
            dropped=int(values[self._DROPPED_BAR_INDEX])
        )

    def _update_progress_text(self, completed: int, dropped: int, total: int) -> None:
        self._completed_progress_text.value = f"{completed} ({round(completed / total * 100)}%)"
        self._dropped_progress_text.value = f"{dropped} ({round(dropped / total * 100)}%)"
        self._total_progress_text.value = f"{total}"

    def _compile_progress_box(self, mode: Optional[str]) -> Optional[widgets.Box]:
        if mode == self.PROGRESS_BOX_INLINE_DISPLAY_MODE:
            progress_box = widgets.HBox(
                [
                    self._progress_bar,
                    widgets.HBox(
                        [
                            self._completed_progress_text,
                            self._dropped_progress_text,
                            self._total_progress_text
                        ]
                    )
                ], layout=widgets.Layout(justify_content="flex-start")
            )
        elif mode == self.PROGRESS_BOX_BLOCK_DISPLAY_MODE:
            progress_box = widgets.VBox(
                [
                    self._progress_bar,
                    widgets.HBox(
                        [
                            widgets.VBox(
                                [
                                    widgets.Label("Completed:"),
                                    widgets.Label("Dropped:"),
                                    widgets.Label("Total:")
                                ]
                            ),
                            widgets.VBox(
                                [
                                    self._completed_progress_text,
                                    self._dropped_progress_text,
                                    self._total_progress_text
                                ]
                            )
                        ]
                    )
                ]
            )
        elif mode is None:
            progress_box = None
        else:
            raise ValueError(f"Invalid {mode=} given.")

        return progress_box

    def _handle_navigation_command(self) -> None:
        text = self._navigation_box.command_text.value
        text = text.strip()
        if not text:
            # Command text is empty. Skip handling.
            return
        if text.isdecimal():
            # If command is a single decimal number.
            try:
                self._sample_indexer.index = int(text)
            except IndexError as e:
                self.display_message(f"<p style='color: red'>{repr(e)}</p>")

            self.update()
        else:
            self.display_message(f"<p style='color: red'>Invalid command: {text}.</p>")
