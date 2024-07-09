from .drawpanel import Drawable
from PIL import Image
from typing import List

class ContainerNode(Drawable):
    def __init__(self, *args, **kwargs) -> None:
        super(ContainerNode, self).__init__(*args, **kwargs)
        # self.is_root = is_root
        self._children: List[Drawable] = []
        self.size = (0, 0)
        self.background_color = (0, 0, 0)

    def set_size(self, width: int, height: int) -> None:
        self.size = (width, height)

    def add_child(self, child: Drawable) -> None:
        self._children.append(child)
        self.append(child)

    def verify_layout_is_clean(self) -> None:
        for child in self._children:
            child.verify_layout_is_clean()

    def draw(self, parent_buffer: Image.Image) -> None:
        if self.is_root:
            self.verify_layout_is_clean()
            if self.is_dirty:
                # print("Recomputing layout")
                self.compute_layout(available_space=self.size, use_rounding=True)
        super().draw(parent_buffer)

    def do_draw(self) -> None:
        assert self.buffer is not None
        self.fill(self.background_color)
        for child in self._children:
            child.draw(self.buffer)
