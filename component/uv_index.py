from data import DataResolver, CurrentWeatherData
from draw import TextNode, CarouselPanel, ContainerNode, BarChart

class CurrentUvIndexComponent(ContainerNode, CarouselPanel):
    def __init__(self, data_resolver: DataResolver[CurrentWeatherData], font_path: str) -> None:
        super().__init__()
        self.data_resolver = data_resolver
        self.add_child(self.UvTextComponent(data_resolver, font_path))
        self.add_child(self.UvGraphComponent(data_resolver))

    def is_carousel_visible(self) -> bool:
        if self.data_resolver.data is None:
            return False
        if self.data_resolver.data.uv is None:
            return False
        return True

    class UvTextComponent(TextNode):
        def __init__(self, data_resolver: DataResolver[CurrentWeatherData], font_path: str) -> None:
            super().__init__(font="4x6", font_path=font_path)
            self.data_resolver = data_resolver

        def get_background_color(self) -> tuple[int, int, int]:
            return (0, 0, 0)

        def get_text_color(self) -> tuple[int, int, int]:
            return (192, 191, 159)

        def get_text(self) -> str:
            if self.data_resolver.data is None or self.data_resolver.data.uv is None:
                return ""
            return f"UV {self.data_resolver.data.uv}"

    class UvGraphComponent(BarChart):
        def __init__(self, data_resolver: DataResolver[CurrentWeatherData]) -> None:
            super().__init__(orientation="vertical", size=(3, 10))
            self.data_resolver = data_resolver

        def min_value(self) -> float:
            return 0
        
        def max_value(self) -> float:
            return 10

        def value(self) -> float | None:
            if self.data_resolver.data is None:
                return None
            return self.data_resolver.data.uv

        def color_scale(self) -> list[tuple[float, tuple[int, int, int]]]:
            return [
                (0, (0, 255, 0)),   # Green
                (3, (255, 255, 0)), # Yellow
                (6, (255, 165, 0)), # Orange
                (8, (255, 0, 0)),   # Red
                (10, (255, 0, 255)) # Fuschia
            ]
