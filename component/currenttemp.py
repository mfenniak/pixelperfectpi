# from data import CurrentWeatherData, DataResolver
# from draw import DrawPanel, Box
# from typing import Any

# class CurrentTemperatureComponent(DrawPanel[CurrentWeatherData]):
#     def __init__(self, data_resolver: DataResolver[CurrentWeatherData], box: Box, font_path: str, **kwargs: Any) -> None:
#         assert data_resolver is not None
#         assert box is not None
#         assert font_path is not None
#         super().__init__(data_resolver=data_resolver, box=box, font_path=font_path)
#         self.load_font("7x13")

#     def frame_count(self, data: CurrentWeatherData | None, now: float) -> int:
#         if data is None:
#             return 0
#         else:
#             return 1

#     def do_draw(self, now: float, data: CurrentWeatherData | None, frame: int) -> None:
#         self.fill((0, 0, 0))
#         if data is None or data.temperature is None:
#             return
#         curr_c = data.temperature
#         self.draw_text((128,128,128), f"{curr_c:.0f}°")
