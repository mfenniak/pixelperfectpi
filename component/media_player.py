from data import MediaPlayerDataResolver, MediaPlayerInformation, MediaPlayerState
from draw import DrawPanel, Box
from typing import Any
import pytz
import datetime
import os.path
from PIL import Image

class MediaPlayerComponent(DrawPanel[MediaPlayerInformation]):
    def __init__(self, media_player: MediaPlayerDataResolver, box: Box, font_path: str, icon_path: str) -> None:
        super().__init__(data_resolver=media_player, box=box, font_path=font_path)
        self.load_font("5x8")
        self.icon = Image.open(os.path.join(icon_path, "tv.png"))

    def frame_count(self, data: MediaPlayerInformation | None) -> int:
        if data is None:
            return 0
        if data.state not in (MediaPlayerState.PLAYING, MediaPlayerState.IDLE):
            return 0
        if data.remaining_total_seconds is None:
            return 0
        return 1

    def do_draw(self, now: float, data: MediaPlayerInformation | None, frame: int) -> None:
        self.fill((44, 85, 69))

        if data is None:
            return

        remaining_total_seconds = data.remaining_total_seconds
        if remaining_total_seconds is None:
            return

        remaining_minutes = int(remaining_total_seconds / 60)
        remaining_seconds = int(remaining_total_seconds % 60)

        self.draw_icon(self.icon)
        self.draw_text((127, 181, 181), f"Remaining {remaining_minutes}:{remaining_seconds:02}", pad_left=self.icon.width)
