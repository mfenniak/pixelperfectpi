from data import OvenOnDataResolver, OvenStatus
from draw import TextNode, CarouselPanel, ContainerNode, IconNode
from stretchable.style import AlignItems

class OvenOnComponent(ContainerNode, CarouselPanel):
    def __init__(self, oven_on: OvenOnDataResolver, font_path: str, icon_path: str) -> None:
        super().__init__(
            flex_grow=1,
            align_items=AlignItems.STRETCH,
        )
        self.oven_on = oven_on
        self.add_child(self.OvenOnIcon(icon_path))
        self.add_child(self.OvenOnText(oven_on, font_path))

    def is_carousel_visible(self) -> bool:
        if self.oven_on.data is None:
            return False
        if self.oven_on.data.status != OvenStatus.ON:
            return False
        return True

    class OvenOnIcon(IconNode):
        def __init__(self, icon_path: str) -> None:
            super().__init__(icon_path=icon_path, icon_file="oven-on.png", background_color=(32, 0, 0))

    class OvenOnText(TextNode):
        def __init__(self, oven_on: OvenOnDataResolver, font_path: str) -> None:
            super().__init__(font="5x8", font_path=font_path)
            self.oven_on = oven_on

        def get_background_color(self) -> tuple[int, int, int]:
            return (32, 0, 0)

        def get_text_color(self) -> tuple[int, int, int]:
            return (255, 0, 0)

        def get_text(self) -> str:
            if self.oven_on.data is None:
                return ""
            return "Oven is on"
