from .resolver import DataResolver, StaticDataResolver
from .purpleair import PurpleAirDataResolver
from .envcanada import EnvironmentCanadaDataResolver
from .calendar import CalendarDataResolver

__all__ = [
    'CalendarDataResolver',
    'DataResolver',
    'EnvironmentCanadaDataResolver',
    'PurpleAirDataResolver',
    'StaticDataResolver',
]
