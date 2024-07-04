# from data import CalendarDataResolver
# from draw import DrawPanel, Box
# from typing import Any
# from PIL import ImageColor
# import pytz
# import datetime

# class CalendarComponent(DrawPanel[dict[str, Any]]):
#     def __init__(self, calendar: CalendarDataResolver, display_tz: pytz.BaseTzInfo, box: Box, font_path: str, **kwargs: Any) -> None:
#         super().__init__(data_resolver=calendar, box=box, font_path=font_path)
#         self.display_tz = display_tz
#         self.load_font("4x6")

#     def frame_count(self, data: dict[str, Any] | None, now: float) -> int:
#         if data is None:
#             return 0
#         return min(len(data["future_events"]), 3) # no more than this many events

#     def do_draw(self, now: float, data: dict[str, Any] | None, frame: int) -> None:
#         self.fill((0, 0, 16))

#         if data is None:
#             return

#         # FIXME: color is synced to the time, but, only by copy-and-paste
#         hue = int(now*50 % 360)
#         textColor = ImageColor.getrgb(f"hsl({hue}, 100%, 50%)")

#         (dt, summary) = data["future_events"][frame]

#         preamble = ""
#         now_dt = datetime.datetime.now(self.display_tz)

#         if dt.time() == datetime.time(0,0,0):
#             # full day event probably
#             if dt.date() == now_dt.date():
#                 preamble = "tdy"
#             elif dt.date() == (now_dt + datetime.timedelta(days=1)).date():
#                 preamble = dt.strftime("tmw")
#             elif (dt - now_dt) < datetime.timedelta(days=7):
#                 preamble = dt.strftime("%a")
#             else:
#                 preamble = dt.strftime("%a %-d")
#         else:
#             # timed event
#             if dt.date() == now_dt.date():
#                 preamble = dt.strftime("%-I:%M%p").replace(":00", "")
#             elif dt.date() == (now_dt + datetime.timedelta(days=1)).date():
#                 preamble = dt.strftime("tmw %-I%p")
#             elif (dt - now_dt) < datetime.timedelta(days=7):
#                 preamble = dt.strftime("%a %-I%p")
#             else:
#                 preamble = dt.strftime("%a %-d")

#         if preamble.endswith("M"): # PM/AM -> P/A; no strftime option for that
#             preamble = preamble[:-1]
#         if preamble.endswith("P") or preamble.endswith("A"): # lowercase this
#             preamble = preamble[:-1] + preamble[-1].lower()

#         text = f"{preamble}: {summary}"
#         self.draw_text(textColor, text.encode("ascii", errors="ignore").decode("ascii"))
