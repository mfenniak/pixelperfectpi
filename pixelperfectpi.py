# from draw.multipanelpanel import MultiPanelPanel
from component.time import TimeComponent
from data import DataResolver
from data.currenttime import CurrentTimeDataResolver
from draw import ContainerNode
from displaybase import DisplayBase
from PIL import Image
from rgbmatrix import RGBMatrix # type: ignore
from service import Service
from stretchable import Node
from typing import Set, TypeVar, Any, List, Callable
import asyncio
import time
from stretchable.style import PCT, AUTO, FlexDirection, AlignItems, AlignContent, JustifyContent

T = TypeVar('T')

# TODO List:
# - Add icons - like a lightning bolt for power, or, sun^ sunv for high and low?
# - Animations - don't know where, when, but let's use all the pixels sometimes
# - Add capability for panels to have subpanels, since drawing ops are full panel size
# - Add something with an icon/image -- maybe the weather forecast
# New data:
# - Power: Usage, Solar Generation
# - Home Assistant: Back door / Garage door / etc. Open
# - Google Location: Distance to Mathieu?
# - Home Assistant: Presence
# - Countdown - France Flag & # days to France
# - Errors from any of the other data collectors / displayers
# - anxi - Any errors on Prometheus?


class Clock(DisplayBase):
    def __init__(self,
        rgbmatrix_provider: Callable[[], RGBMatrix],
        data_resolvers: List[DataResolver[T]],
        current_time: CurrentTimeDataResolver,
        root: ContainerNode,
        # time_component: TimeComponent,
        # current_component: MultiPanelPanel,
        # lower_panels: MultiPanelPanel,
        shutdown_event: asyncio.Event, services: List[Service]) -> None:
        super().__init__(rgbmatrix_provider=rgbmatrix_provider, shutdown_event=shutdown_event, services=services)
        self.data_resolvers = data_resolvers
        # self.layout_node = Node()
        self.current_time = current_time
        # self.time_component = time_component
        self.root = root
        # self.current_component = current_component
        # self.lower_panels = lower_panels

    def pre_run(self) -> None:
        self.background_tasks: Set[asyncio.Task[Any]] = set()

    async def create_canvas(self, matrix: RGBMatrix) -> None:
        self.offscreen_canvas = matrix.CreateFrameCanvas()
        self.buffer = Image.new("RGB", (self.offscreen_canvas.width, self.offscreen_canvas.height))
        self.root.set_size(self.offscreen_canvas.width, self.offscreen_canvas.height)
        # self.layout_node = Node(
        #     size=(self.offscreen_canvas.width, self.offscreen_canvas.height),
        #     flex_direction=FlexDirection.COLUMN,
        #     justify_content=JustifyContent.CENTER,
        #     align_items=AlignItems.CENTER,
        # )
        # self.layout_node.append(self.time_component)

    async def update_data(self) -> None:
        now = time.time()
        for data_resolver in self.data_resolvers:
            task = asyncio.create_task(data_resolver.maybe_refresh(now))
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)

    async def draw_frame(self, matrix: RGBMatrix) -> None:
        # if self.layout_node.is_dirty:
        #     self.layout_node.compute_layout(use_rounding=True)

        self.current_time.freeze_time()

        assert self.buffer is not None
        self.root.draw(self.buffer)

        # self.time_component.draw(self.buffer) # FIXME: find a way to remove frame/data params
        # self.current_component.draw(self.buffer, frame=0, data=None)
        # self.lower_panels.draw(self.buffer, frame=0, data=None)

        self.offscreen_canvas.SetImage(self.buffer, 0, 0)

        self.offscreen_canvas = matrix.SwapOnVSync(self.offscreen_canvas)

        self.current_time.release_time()
