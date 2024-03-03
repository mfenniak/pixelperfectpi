from .box import Box
from .drawpanel import DrawPanel
from data import StaticDataResolver
from typing import Any, List, Generic, TypeVar

T = TypeVar('T')

class PrioritizedPanel(Generic[T]):
    def priority(self, now: float, data: T) -> float:
        raise NotImplementedError()


class MultiPanelPanel(DrawPanel[None]):
    def __init__(self, box: Box, font_path: str, panels: List[DrawPanel[Any]] | None = None, time_per_frame: int = 5) -> None:
        super().__init__(data_resolver=StaticDataResolver(None), box=box, font_path=font_path)
        assert panels is not None
        self.panels = panels
        self.time_per_frame = time_per_frame

    def do_draw(self, now: float, data: None, frame: int) -> None:
        # First; get a snapshot of the data for each panel so that it doesn't change while we're calculating this.
        panel_datas = [x.data_resolver.data for x in self.panels]

        # Group all the panels by their priority; defaulting to 0 if they don't have a priority.  We'll draw only the panels in the highest priority group.
        panels_by_priority: dict[float, List[DrawPanel[Any]]] = {}
        panel_data_by_priority: dict[float, List[Any]] = {}
        highest_priority = None
        for panel_index, panel in enumerate(self.panels):
            if isinstance(panel, PrioritizedPanel):
                priority = panel.priority(now=now, data=panel_datas[panel_index])
            else:
                priority = 0
            panels_by_priority.setdefault(priority, []).append(panel)
            panel_data_by_priority.setdefault(priority, []).append(panel_datas[panel_index])
            if highest_priority is None or priority > highest_priority:
                highest_priority = priority

        if highest_priority is None:
            # No panels?
            self.fill((0, 0, 0))
            return

        panels = panels_by_priority[highest_priority]
        panel_datas = panel_data_by_priority[highest_priority]

        # Ask each panel how many frames they will have, considering their data.
        frame_count: list[int] = [x.frame_count(data=panel_datas[i], now=now) for i, x in enumerate(panels)]

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
        assert target_frame_index is not None

        panels[target_panel_index].draw(self.buffer, now=now, data=panel_datas[target_panel_index], frame=target_frame_index)
