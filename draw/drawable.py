from PIL import Image, ImageDraw
from stretchable import Node
from stretchable.style import AlignItems
from typing import TypeVar, Any

class Drawable(Node):
    def __init__(self, debug_border: tuple[int, int, int] | None = None, **kwargs: Any) -> None:
        self.buffer: Image.Image | None = None
        self.imagedraw = ImageDraw.Draw(Image.new("RGBA", (1, 1))) # FIXME: typing hack
        self.debug_border = debug_border
        if "flex_grow" not in kwargs:
            kwargs["flex_grow"] = 1
        if "align_items" not in kwargs:
            kwargs["align_items"] = AlignItems.STRETCH
        super().__init__(**kwargs)

    def verify_layout_is_clean(self) -> None:
        # Before drawing, a chance to mark ourselves as dirty if our
        # requirements have changed (typically due to data resolver's data
        # change)
        return

    # Internal - subclasses implement this to draw onto self.buffer.
    def do_draw(self) -> None:
        raise NotImplementedError

    def draw(self, parent_buffer: Image.Image) -> None:
        box = self.get_box()
        if self.buffer is None or self.buffer.width != box.width or self.buffer.height != box.height:
            self.buffer = Image.new("RGBA", (int(box.width), int(box.height)))
            self.imagedraw = ImageDraw.Draw(self.buffer)

        self.do_draw()
        if self.debug_border is not None:
            self.imagedraw.rectangle((0, 0, box.width-1, box.height-1), outline=self.debug_border)
        parent_buffer.paste(self.buffer, box=(int(box.x), int(box.y)))

    def fill(self, color: tuple[int, int, int] | tuple[int, int, int, int]) -> None:
        assert self.buffer is not None
        self.buffer.paste(color, box=(0,0,self.buffer.width,self.buffer.height))

    def rect(self, color: tuple[int, int, int], x: int, y: int, width: int, height: int) -> None:
        if width == 0 or height == 0:
            return
        # imagedraw rectangle is inclusive on both sides; the -1 is required to make
        # the width/height of the rectangle correct
        self.imagedraw.rectangle((x, y, x+width-1, y+height-1), outline=color)
