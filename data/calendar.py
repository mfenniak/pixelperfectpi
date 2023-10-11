from .resolver import ScheduledDataResolver
from typing import Any
import aiohttp
import datetime
import icalendar # type: ignore
import pytz
import recurring_ical_events # type: ignore

class CalendarDataResolver(ScheduledDataResolver[dict[str, Any]]): # FIXME: change to a dataclass
    def __init__(self, ical_url: str, display_tz: pytz.BaseTzInfo) -> None:
        super().__init__(refresh_interval=3600)
        self.ical_url = ical_url
        self.display_tz = display_tz

    async def fetch_ical(self) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.ical_url) as response:
                if response.status != 200:
                    raise Exception(f"Unexpected status code: {response.status}")
                return await response.read()

    async def do_collection(self) -> dict[str, Any]:
        ical_content = await self.fetch_ical()
        calendar = icalendar.Calendar.from_ical(ical_content)
        future_events = []

        now = datetime.datetime.now(pytz.utc) # datetime.timezone.utc)
        today = datetime.date.today()

        start_date = now
        end_date = now + datetime.timedelta(days=14)
        events = recurring_ical_events.of(calendar).between(start_date, end_date)
        for event in events:
            dtstart = event.get("dtstart").dt
            if isinstance(dtstart, datetime.datetime):
                if dtstart > now:
                    future_events.append((dtstart.astimezone(self.display_tz), str(event.get("SUMMARY"))))
            elif isinstance(dtstart, datetime.date):
                # Show "today" events until 8am, then move on
                dtstart_morning = datetime.datetime.combine(dtstart, datetime.time(8, 0, 0)).astimezone(self.display_tz)
                if dtstart_morning > now:
                    start = datetime.datetime.combine(dtstart, datetime.time()).astimezone(self.display_tz)
                    future_events.append((start, str(event.get("SUMMARY"))))
            else:
                print("unexpected dt type", repr(dtstart))

        future_cutoff = now + datetime.timedelta(days=6)
        near_future_events = [x for x in future_events if x[0] < future_cutoff]
        near_future_events = sorted(near_future_events, key=lambda event: event[0])

        return {
            "future_events": near_future_events
        }
