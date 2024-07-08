from data import MediaPlayerDataResolver, MediaPlayerState
from draw import TextNode, CarouselPanel, ContainerNode, IconNode

class MediaPlayerComponent(ContainerNode, CarouselPanel):
    def __init__(self, media_player: MediaPlayerDataResolver, font_path: str, icon_path: str) -> None:
        super().__init__()
        self.media_player = media_player
        self.add_child(self.MediaPlayerIcon(icon_path))
        self.add_child(self.MediaPlayerText(media_player, font_path))

    def is_carousel_visible(self) -> bool:
        if self.media_player.data is None:
            return False
        if self.media_player.data.state not in (MediaPlayerState.PLAYING, MediaPlayerState.IDLE):
            return False
        if self.media_player.data.remaining_total_seconds is None:
            return False
        return True

    class MediaPlayerIcon(IconNode):
        def __init__(self, icon_path: str) -> None:
            super().__init__(icon_path=icon_path, icon_file="tv.png", background_color=(21, 40, 33))

    class MediaPlayerText(TextNode):
        def __init__(self, media_player: MediaPlayerDataResolver, font_path: str) -> None:
            super().__init__(font="5x8", font_path=font_path)
            self.media_player = media_player

        def get_background_color(self) -> tuple[int, int, int]:
            return (21, 40, 33)

        def get_text_color(self) -> tuple[int, int, int]:
            return (127, 181, 181)

        def get_text(self) -> str:
            if self.media_player.data is None:
                return ""
            remaining_total_seconds = self.media_player.data.remaining_total_seconds
            if remaining_total_seconds is None:
                return ""
            remaining_minutes = int(remaining_total_seconds / 60)
            remaining_seconds = int(remaining_total_seconds % 60)
            return f"Remaining {remaining_minutes}:{remaining_seconds:02}"
