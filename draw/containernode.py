from stretchable import Node
from .drawpanel import Drawable
from PIL import Image, ImageFont, ImageDraw
from typing import List

class ContainerNode(Drawable):
    def __init__(self, *args, **kwargs) -> None:
        super(ContainerNode, self).__init__(*args, **kwargs)
        self._children: List[Drawable] = []
        self.size = (0, 0)

    def set_size(self, width: int, height: int) -> None:
        self.size = (width, height)

    def add_child(self, child: Drawable) -> None:
        self._children.append(child)
        self.append(child)

    def draw(self, parent_buffer: Image.Image) -> None:
        if self.is_dirty:
            self.compute_layout(available_space=self.size, use_rounding=True)
            print("Layout computed w/ size", self.size)
            print(self.get_box(relative=False))
            for child in self._children:
                print(child.get_box(relative=False))
        super().draw(parent_buffer)

    def do_draw(self) -> None:
        assert self.buffer is not None
        for child in self._children:
            child.draw(self.buffer)
