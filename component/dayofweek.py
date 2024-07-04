# from data import StaticDataResolver
# from draw import DrawPanel, Box
# from PIL import ImageColor
# from typing import Any
# import time

# class DayOfWeekComponent(DrawPanel[None]):
#     def __init__(self, box: Box, font_path: str, **kwargs: Any) -> None:
#         assert box is not None
#         assert font_path is not None
#         super().__init__(data_resolver=StaticDataResolver(None), box=box, font_path=font_path)
#         self.load_font("7x13")

#     def do_draw(self, now: float, data: None, frame: int) -> None:
#         self.fill((0, 0, 0))

#         # FIXME: color is synced to the time, but, only by copy-and-paste
#         hue = int(now*50 % 360)
#         color = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

#         timestr = time.strftime("%a")
#         self.draw_text(color, timestr)
