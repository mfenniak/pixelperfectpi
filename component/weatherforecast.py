from data import EnvironmentCanadaDataResolver
from draw import DrawPanel, Box
from typing import Any

class WeatherForecastComponent(DrawPanel[dict[str, Any]]):
    def __init__(self, env_canada: EnvironmentCanadaDataResolver, box: Box, font_path: str, **kwargs: Any) -> None:
        super().__init__(data_resolver=env_canada, box=box, font_path=font_path)
        self.load_font("4x6")

    def frame_count(self, data: dict[str, Any] | None) -> int:
        if data == None:
            return 0
        else:
            return 1

    def do_draw(self, now: float, data: dict[str, Any] | None, frame: int) -> None:
        self.fill((16, 0, 0))
        if data is None:
            return
        n = data['forecast']['name']
        s = data['forecast']['text_summary']
        t = data['forecast']['type'].capitalize()
        deg_c = data['forecast']['deg_c']
        self.draw_text((255, 255, 255), f"{n} {s} {t} {deg_c:.0f}°")
