from data import DoorDataResolver, DoorInformation, DoorStatus
from draw import DrawPanel, Box
from PIL import Image
import datetime
import os.path
import pytz

class DoorComponent(DrawPanel[DoorInformation]):
    def __init__(self, door: DoorDataResolver, box: Box, font_path: str, icon_path: str, name: str) -> None:
        super().__init__(data_resolver=door, box=box, font_path=font_path)
        self.load_font("5x8")
        self.icon = Image.open(os.path.join(icon_path, "garage.png"))
        self.name = name

    def frame_count(self, data: DoorInformation | None) -> int:
        if data is None:
            return 0
        if data.status != DoorStatus.OPEN:
            return 0
        now = datetime.datetime.now(pytz.utc)
        if (now - data.status_since) < datetime.timedelta(minutes=5):
            return 0
        return 1

    def do_draw(self, now: float, data: DoorInformation | None, frame: int) -> None:
        if data is None:
            return
        self.fill((0, 32, 32))
        self.draw_icon(self.icon)
        self.draw_text((255, 128, 0), f"{self.name} Open", pad_left=self.icon.width)
