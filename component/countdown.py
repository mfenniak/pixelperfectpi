from data import TimerDataResolver, TimerState, DataResolver
from draw import TextNode, CarouselPanel, ContainerNode, IconNode
from typing import Any
from PIL import ImageColor
import pytz
from datetime import datetime
from stretchable.style.geometry.size import SizeAvailableSpace, SizePoints
from stretchable.style.geometry.length import Scale, LengthPoints

class CountdownComponent(ContainerNode, CarouselPanel):
    def __init__(self, current_time: DataResolver[float], target_date: datetime, font_path: str, icon_path: str, **kwargs: Any) -> None:
        super().__init__()
        # self.display_tz = display_tz
        self.current_time = current_time
        self.target_date = target_date
        self.add_child(self.CountdownIcon(icon_path))
        self.add_child(self.CountdownText(current_time, target_date, font_path))
        # self.load_font("5x8")
        # self.icon = Image.open(os.path.join(icon_path, "france.png"))

    def is_carousel_visible(self) -> bool:
        if self.current_time.data is None:
            return False
        now_dt = datetime.fromtimestamp(self.current_time.data, pytz.utc)
        if now_dt > self.target_date:
            return False
        else:
            return True

    class CountdownIcon(IconNode):
        def __init__(self, icon_path: str) -> None:
            super().__init__(icon_path=icon_path, icon_file="france.png", background_color=(0, 32, 0))

    class CountdownText(TextNode):
        def __init__(self, current_time: DataResolver[float], target_date: datetime, font_path: str) -> None:
            super().__init__(font="5x8", font_path=font_path)
            self.current_time = current_time
            self.target_date = target_date

        def get_background_color(self) -> tuple[int, int, int]:
            return (0, 32, 0)

        def get_text_color(self) -> tuple[int, int, int] | tuple[int, int, int, int]:
            now = self.current_time.data
            assert now is not None
            hue = int(now*50 % 360)
            return ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

        def get_text(self) -> str:
            now = self.current_time.data
            assert now is not None

            now_dt = datetime.fromtimestamp(now, pytz.utc)
            delta = self.target_date - now_dt

            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds // 60) % 60
            seconds = delta.seconds % 60

            return  f"{days}d {hours}h {minutes}m {seconds}s"



    # def frame_count(self, data: datetime | None, now: float) -> int:
    #     now_dt = datetime.fromtimestamp(now, pytz.utc)
    #     if data is None or now_dt > data:
    #         return 0
    #     else:
    #         return 1

    # def do_draw(self, now: float, data: datetime | None, frame: int) -> None:
    #     if data is None:
    #         return

    #     now_dt = datetime.fromtimestamp(now, pytz.utc)
    #     delta = data - now_dt

    #     days = delta.days
    #     hours = delta.seconds // 3600
    #     minutes = (delta.seconds // 60) % 60
    #     seconds = delta.seconds % 60

    #     # blue: #001E96
    #     # white: #FFFFFF
    #     # red: #EE2436
    #     # blue = (0, 30, 150)
    #     # white = (255, 255, 255)
    #     # red = (238, 36, 54)
    #     # self.buffer.paste(blue,  box=(0 * (self.w // 3), 0, 1 * (self.w // 3), self.h))
    #     # self.buffer.paste(white, box=(1 * (self.w // 3), 0, 2 * (self.w // 3), self.h))
    #     # self.buffer.paste(red,   box=(2 * (self.w // 3), 0, 3 * (self.w // 3), self.h))

    #     hue = int(now*50 % 360)
    #     color = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

    #     self.fill((0, 32, 0))
    #     self.draw_icon(self.icon)
    #     self.draw_text(color, f"{days}d {hours}h {minutes}m {seconds}s", pad_left=self.icon.width)
