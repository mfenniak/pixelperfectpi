from PIL import Image, ImageDraw
from stretchable import Node
from typing import TypeVar, Any

class Drawable(Node):
    def __init__(self, **kwargs: Any) -> None:
        self.buffer: Image.Image | None = None
        self.imagedraw = ImageDraw.Draw(Image.new("RGBA", (1, 1))) # FIXME: typing hack
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
