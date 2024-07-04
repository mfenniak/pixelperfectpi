# from data import CurrentWeatherData, DataResolver
# from draw import DrawPanel, Box
# from typing import Any, Tuple

# class CurrentUvIndexComponent(DrawPanel[CurrentWeatherData]):
#     def __init__(self, data_resolver: DataResolver[CurrentWeatherData], box: Box, font_path: str, **kwargs: Any) -> None:
#         assert data_resolver is not None
#         assert box is not None
#         assert font_path is not None
#         super().__init__(data_resolver=data_resolver, box=box, font_path=font_path)
#         self.load_font("4x6")

#     def frame_count(self, data: CurrentWeatherData | None, now: float) -> int:
#         if data is None:
#             return 0
#         else:
#             return 1

#     def do_draw(self, now: float, data: CurrentWeatherData | None, frame: int) -> None:
#         self.fill((0, 0, 0))
#         if data is None or data.uv is None:
#             return
#         # curr_c = data.uv
#         self.draw_text(
#             (192, 191, 159),
#             f"UV {data.uv}",
#             halign="center",
#             valign="top",
#         )
#         for i in range(0, data.uv):
#             color = self.interpolate_color(i)
#             row = self.h - i - 1
#             if row < 0:
#                 # Probably should never happen, would require UV index greater
#                 # than the height of this panel.
#                 break
#             for x in range(0, self.w):
#                 self.set_pixel(x, row, color)

#     def interpolate_color(self, uv_index: int) -> Tuple[int, int, int]:
#         """
#         Interpolate RGB colors based on UV index using linear interpolation.
        
#         :param uv_index: float, the UV index value
#         :return: tuple, interpolated RGB color based on the UV index
#         """

#         def lerp_color(start_color, end_color, t):
#             """
#             Linearly interpolate between two RGB colors.
            
#             :param start_color: tuple, starting RGB color
#             :param end_color: tuple, ending RGB color
#             :param t: float, interpolation factor between 0 and 1
#             :return: tuple, interpolated RGB color
#             """
#             return (
#                 int(start_color[0] + (end_color[0] - start_color[0]) * t),
#                 int(start_color[1] + (end_color[1] - start_color[1]) * t),
#                 int(start_color[2] + (end_color[2] - start_color[2]) * t)
#             )

#         uv_colors = [
#             (0, (0, 255, 0)),   # Green
#             (3, (255, 255, 0)), # Yellow
#             (6, (255, 165, 0)), # Orange
#             (8, (255, 0, 0)),   # Red
#             (10, (255, 0, 255)) # Fuschia
#         ]
#         prev = uv_colors[0]
#         for uv, color in uv_colors:
#             if uv_index <= uv:
#                 if uv == uv_index:
#                     return color
#                 return lerp_color(prev[1], color, (uv_index - prev[0]) / (uv - prev[0]))
#             prev = uv, color
#         return prev[1]
