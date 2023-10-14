from data import DoorDataResolver, DoorInformation, DoorStatus
from draw import DrawPanel, Box, PrioritizedPanel
from PIL import Image
import datetime
import os.path
import pytz

class DoorComponent(DrawPanel[DoorInformation], PrioritizedPanel[DoorInformation]):
    def __init__(self, door: DoorDataResolver, box: Box, font_path: str, icon_path: str, name: str) -> None:
        super().__init__(data_resolver=door, box=box, font_path=font_path)
        self.load_font("5x8")
        self.icon = Image.open(os.path.join(icon_path, "garage.png"))
        self.name = name
        self.just_changed_timeframe = datetime.timedelta(seconds=10)
        self.left_open_timeframe = datetime.timedelta(minutes=5)

    # FIXME: Maybe splitting the "Just Changed" and "Left Open" states into two different components would make more
    # sense... everything here has two logic paths.

    def priority(self, now: float, data: DoorInformation | None) -> float:
        # For the first 15 seconds after the door status changes, we want to show the status.
        if data is None:
            return 0
        now_dt = datetime.datetime.now(pytz.utc)
        delta = now_dt - data.status_since
        if delta < self.just_changed_timeframe:
            return 10
        return 0

    def frame_count(self, data: DoorInformation | None) -> int:
        if data is None or data.status == DoorStatus.UNKNOWN:
            return 0
        now_dt = datetime.datetime.now(pytz.utc)
        delta = now_dt - data.status_since
        if delta < self.just_changed_timeframe:
            return 1
        if data.status == DoorStatus.OPEN and delta > self.left_open_timeframe:
            return 1
        return 0

    def do_draw(self, now: float, data: DoorInformation | None, frame: int) -> None:
        if data is None:
            return
        self.fill((0, 32, 32))
        self.draw_icon(self.icon)

        now_dt = datetime.datetime.now(pytz.utc)
        delta = now_dt - data.status_since
        if delta < self.just_changed_timeframe:
            if data.status == DoorStatus.OPEN:
                self.draw_text((255, 128, 0), f"{self.name} Opening", pad_left=self.icon.width)
            else:
                self.draw_text((255, 128, 0), f"{self.name} Closed", pad_left=self.icon.width)
        else:
            self.draw_text((255, 128, 0), f"{self.name} Left Open", pad_left=self.icon.width)
