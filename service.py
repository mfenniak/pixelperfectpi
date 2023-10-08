from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from displaybase import DisplayBase

class Service(object):
    def __init__(self) -> None:
        pass

    async def status_update(self, state: Literal["ON"] | Literal["OFF"]) -> None:
        pass

    async def start(self, clock: "DisplayBase") -> None:
        pass
