from .drawpanel import Drawable
from data import DataResolver
from typing import List

class CarouselPanel(object):
    def get_drawable(self) -> Drawable:
        assert isinstance(self, Drawable)
        return self

    def is_carousel_visible(self) -> bool:
        return True

    def priority(self) -> float:
        return 0


class CarouselDrawable(Drawable):
    def __init__(self, current_time: DataResolver[float], time_per_frame: int = 5, *args, **kwargs) -> None:
        super(CarouselDrawable, self).__init__(*args, **kwargs)
        self.current_time = current_time
        self.time_per_frame = time_per_frame
        self.all_panels: List[CarouselPanel] = []
        self.last_panel: CarouselPanel | None = None
        self.current_panel: CarouselPanel | None = None

    def add_panel(self, panel: CarouselPanel) -> None:
        self.all_panels.append(panel)

    def compute_current_panel(self) -> None:
        # Group all the panels by their priority; defaulting to 0 if they don't have a priority.  We'll draw only the panels in the highest priority group.
        panels_by_priority: dict[float, List[CarouselPanel]] = {}
        highest_priority = None
        for panel in self.all_panels:
            if not panel.is_carousel_visible():
                continue
            priority = panel.priority()
            panels_by_priority.setdefault(priority, []).append(panel)
            if highest_priority is None or priority > highest_priority:
                highest_priority = priority

        if highest_priority is None:
            # No panels?
            self.current_panel = None
            return

        panels = panels_by_priority[highest_priority]
        total_panels = len(panels)
        if total_panels == 0:
            self.current_panel = None
            return

        now = self.current_time.data
        assert now is not None
        active_panel = int(now / self.time_per_frame) % total_panels
        self.current_panel = panels[active_panel]

    def verify_layout_is_clean(self) -> None:
        self.compute_current_panel()
        if self.current_panel is not None and self.current_panel is not self.last_panel:
            if self.last_panel is not None:
                self.remove(self.last_panel.get_drawable())
            self.last_panel = self.current_panel
            self.add(self.current_panel.get_drawable())
        if self.current_panel is not None:
            self.current_panel.get_drawable().verify_layout_is_clean()

    def do_draw(self) -> None:
        assert self.buffer is not None
        self.fill((0, 0, 0))
        if self.current_panel is not None:
            self.current_panel.get_drawable().draw(self.buffer)
