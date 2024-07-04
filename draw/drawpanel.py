# from .box import Box
# from data import DataResolver
from PIL import Image, ImageFont, ImageDraw
from typing import TypeVar, Generic, Literal
# import os.path

T = TypeVar('T')

from stretchable import Node

class Drawable(Node, Generic[T]):
    def __init__(self, *args, **kwargs) -> None:
        self.buffer: Image.Image | None = None
        self.imagedraw = ImageDraw.Draw(Image.new("RGBA", (1, 1))) # FIXME: typing hack
        super(Drawable, self).__init__(*args, **kwargs)

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

    def fill(self, color: tuple[int, int, int]) -> None:
        assert self.buffer is not None
        self.buffer.paste(color, box=(0,0,self.buffer.width,self.buffer.height))


# class DrawPanel(Generic[T]):
#     def __init__(self, box: Box, font_path: str, data_resolver: DataResolver[T]) -> None:
#         self.box = box
#         self.font_path = font_path
#         self.buffer: Image.Image = Image.new("RGBA", (self.w, self.h))
#         self.imagedraw = ImageDraw.Draw(self.buffer)
#         self.pil_font: None | ImageFont.ImageFont = None
#         self.data_resolver = data_resolver

#     x = property(lambda self: self.box[0])
#     y = property(lambda self: self.box[1])
#     w = property(lambda self: self.box[2])
#     h = property(lambda self: self.box[3])

#     def load_font(self, name: str) -> None:
#         self.pil_font = ImageFont.load(os.path.join(self.font_path, f"{name}.pil"))

#     def frame_count(self, data: T | None, now: float) -> int:
#         return 1

#     def do_draw(self, now: float, data: T | None, frame: int) -> None:
#         raise NotImplementedError

#     def draw(self, parent_buffer: Image.Image, now: float, data: T | None, frame: int) -> None:
#         self.do_draw(now, data, frame)
#         parent_buffer.paste(self.buffer, box=(self.x, self.y))

#     def fill(self, color: tuple[int, int, int]) -> None:
#         self.buffer.paste(color, box=(0,0,self.w,self.h))

#     def rect(self, color: tuple[int, int, int], x: int, y: int, width: int, height) -> None:
#         if width == 0 or height == 0:
#             return
#         # imagedraw rectangle is inclusive on both sides; the -1 is required to make
#         # the width/height of the rectangle correct
#         self.imagedraw.rectangle((x, y, x+width-1, y+height-1), fill=color)

#     def set_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
#         self.buffer.putpixel((x, y), color)

#     def draw_icon(self,
#         icon: Image.Image, 
#         halign: Literal["center"] | Literal["left"] | Literal["right"]="left",
#         valign: Literal["top"] | Literal["middle"] | Literal["bottom"]="middle") -> None:
#         dest = (0, 0)
#         if halign == "center":
#             dest = ((self.w - icon.width) // 2, dest[1])
#         elif halign == "right":
#             dest = (self.w - icon.width, dest[1])
#         if valign == "middle":
#             dest = (dest[0], (self.h - icon.height) // 2)
#         elif valign == "bottom":
#             dest = (dest[0], self.h - icon.height)
#         self.buffer.alpha_composite(icon, dest)

#     # Calculate the width and height required to render the given text with the
#     # current font, wrapping if necessary to fit within max_width.  There is no
#     # max height just to keep this simple...
#     def measure_text(self, text: str,
#         max_width: int,
#         halign: Literal["center"] | Literal["left"] | Literal["right"]="center") -> tuple[int, int]:
#         if self.pil_font is None:
#             raise Exception("must call load_font first")

#         # measure the total width of the text...
#         (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), text, font=self.pil_font, spacing=0, align="left")
#         if right <= max_width:
#             # it will fit in a single-line; nice and easy peasy...
#             return (right, bottom)

#         # alright... let's just go line-by-line then, shall we.  First find the most text that will fit into one line,
#         # word-by-word.
#         lines = []
#         text_words = text.split(" ")
#         line = ""
#         height_total = 0
#         widest_line = 0
#         while True:
#             if len(text_words) == 0:
#                 # Ran out of words -- eg. we're done.
#                 if line != "":
#                     height_total += bottom
#                     lines.append(line)
#                     (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), line, font=self.pil_font, spacing=0, align="left")
#                     widest_line = max(widest_line, right)
#                 return (widest_line, height_total)

#             next_word = text_words[0]
#             proposed_line = line
#             if proposed_line != "":
#                 proposed_line += " "
#             proposed_line += next_word
            
#             # will "proposed_line" fit onto a line?
#             (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), proposed_line, font=self.pil_font, spacing=0, align="left")
#             if right > max_width:
#                 height_total += bottom
#                 # no, proposed_line is too big; we'll make do with the last `line`
#                 if line != "":
#                     lines.append(line)
#                     (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), line, font=self.pil_font, spacing=0, align="left")
#                     widest_line = max(widest_line, right)
#                     line = ""
#                     # leave next_word in text_words and keep going
#                 else:
#                     # next_word by itself won't fit on a line; well, we can't skip the middle of a sentence so we'll
#                     # just consume it regardless as it's own line.  Ignore it for widest_line calc.
#                     lines.append(next_word)
#                     text_words = text_words[1:]
#             else:
#                 # yes, it will fit on the line
#                 line = proposed_line
#                 text_words = text_words[1:]

#     # halign - left, center, right
#     # valign - top, middle, bottom
#     def draw_text(self,
#         color: tuple[int, int, int] | tuple[int, int, int, int], # RGB / RGBA
#         text: str,
#         halign: Literal["center"] | Literal["left"] | Literal["right"]="center",
#         valign: Literal["top"] | Literal["middle"] | Literal["bottom"]="middle",
#         pad_left: int = 0,
#         pad_top: int = 0
#         ) -> None:

#         if self.pil_font is None:
#             raise Exception("must call load_font first")

#         # measure the total width of the text...
#         (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), text, font=self.pil_font, spacing=0, align="left")
#         if right <= (self.w - pad_left):
#             # it will fit in a single-line; nice and easy peasy...
#             text_height = bottom
#             if valign == "top":
#                 text_y = 0
#             elif valign == "bottom":
#                 text_y = self.h - bottom
#             else: # middle
#                 text_y = (self.h - text_height - pad_top) // 2
#             text_width = right
#             if halign == "left":
#                 text_x = 0
#             elif halign == "right":
#                 text_x = self.w - text_width
#             else: # center
#                 text_x = (self.w - text_width - pad_left) // 2
#             self.imagedraw.multiline_text((pad_left + text_x, pad_top + text_y), text, fill=color, font=self.pil_font, spacing=0, align=halign)
#             return

#         # alright... let's just go line-by-line then, shall we.  First find the most text that will fit into one line,
#         # word-by-word.
#         lines = []
#         text_words = text.split(" ")
#         line = ""
#         height_total = 0
#         widest_line = 0
#         while True:
#             if len(text_words) == 0:
#                 # Ran out of words.
#                 if line != "":
#                     height_total += bottom
#                     lines.append(line)
#                     (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), line, font=self.pil_font, spacing=0, align="left")
#                     widest_line = max(widest_line, right)
#                 break

#             next_word = text_words[0]
#             proposed_line = line
#             if proposed_line != "":
#                 proposed_line += " "
#             proposed_line += next_word
            
#             # will "proposed_line" fit onto a line?
#             (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), proposed_line, font=self.pil_font, spacing=0, align="left")
#             if right > (self.w - pad_left):
#                 height_total += bottom
#                 # no, proposed_line is too big; we'll make do with the last `line`
#                 if line != "":
#                     lines.append(line)
#                     (left, top, right, bottom) = self.imagedraw.multiline_textbbox((0, 0), line, font=self.pil_font, spacing=0, align="left")
#                     widest_line = max(widest_line, right)
#                     line = ""
#                     # leave next_word in text_words and keep going
#                 else:
#                     # next_word by itself won't fit on a line; well, we can't skip the middle of a sentence so we'll
#                     # just consume it regardless as it's own line.  Ignore it for widest_line calc.
#                     lines.append(next_word)
#                     text_words = text_words[1:]
#             else:
#                 # yes, it will fit on the line
#                 line = proposed_line
#                 text_words = text_words[1:]

#         new_text = "\n".join(lines)

#         text_height = height_total
#         if valign == "top":
#             text_y = 0
#         elif valign == "bottom":
#             text_y = max(0, self.h - bottom)
#         else: # middle
#             text_y = max(0, (self.h - text_height - pad_top) // 2)
#         text_width = widest_line
#         if halign == "left":
#             text_x = 0
#         elif halign == "right":
#             text_x = max(0, self.w - text_width)
#         else: # center
#             text_x = max(0, (self.w - text_width - pad_left) // 2)

#         self.imagedraw.multiline_text((pad_left + text_x, pad_top + text_y), new_text, fill=color, font=self.pil_font, spacing=0, align=halign)
