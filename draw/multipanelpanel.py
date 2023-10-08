from .drawpanel import DrawPanel
from typing import Any
from . import Box
from data import StaticDataResolver

class MultiPanelPanel(DrawPanel[None]):
    # FIXME: correct types for panel_constructors
    def __init__(self, panel_constructors: Any, box: Box, font_path: str, time_per_frame: int = 5, **kwargs: Any) -> None:
        super().__init__(data_resolver=StaticDataResolver(None), box=box, font_path=font_path)
        # inner_kwargs = kwargs.copy()
        # # same width & height, but don't inherit the x/y position
        # inner_kwargs['x'] = 0
        # inner_kwargs['y'] = 0
        self.panels = [
            constructor(box=(0, 0, self.w, self.h), font_path=font_path, **kwargs) for constructor in panel_constructors
        ]
        self.time_per_frame = time_per_frame

    def do_draw(self, now: float, data: None, frame: int) -> None:
        # First; get a snapshot of the data for each panel so that it doesn't change while we're calculating this.
        panel_datas = [x.data_resolver.data for x in self.panels]

        # Ask each panel how many frames they will have, considering their data.
        frame_count: list[int] = [x.frame_count(data=panel_datas[i]) for i, x in enumerate(self.panels)]

        # Based upon the total number of frames on all panels, and the time, calculate the active frame.
        total_frames = sum(frame_count)

        if total_frames == 0:
            self.fill((0, 0, 0))
            return

        active_frame = int(now / self.time_per_frame) % total_frames

        # Find the panel for that frame, and the index of that frame in that panel.
        running_total = 0
        target_panel_index = None
        target_frame_index = None
        for panel_index, _frame_count in enumerate(frame_count):
            maybe_frame_index = active_frame - running_total
            if maybe_frame_index < _frame_count:
                target_panel_index = panel_index
                target_frame_index = maybe_frame_index
                break
            running_total += _frame_count
        assert target_panel_index is not None

        self.panels[target_panel_index].draw(self.buffer, now=now, data=panel_datas[target_panel_index], frame=target_frame_index)
