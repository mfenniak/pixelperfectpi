import asyncio
from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity

from .const import DOMAIN, LOGGER

async def async_setup_entry(hass, config_entry, async_add_entities):
    clock = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([ PipixelperfectSwitch(clock) ])


class PipixelperfectSwitch(SwitchEntity):
    _attr_should_poll = False

    def __init__(self, clock):
        self._clock = clock
        self._attr_name = f"pixelperfectpi {self._clock._host}"
        self._attr_unique_id = f"pixelperfectpi_{self._clock._host}_switch"
        self._status = self._clock.last_status
        self._pending_events = {"ON": [], "OFF": []}

    async def async_added_to_hass(self) -> None:
        self._clock.event_receivers.append(self.event_receiver)

    async def async_will_remove_from_hass(self):
        self._clock.event_receivers.remove(self.event_receiver)

    def event_receiver(self, event):
        # event: { event: True, status: ON/OFF }
        LOGGER.debug("%s: received event=%r", self._attr_name, event)
        status = event.get("status")
        for evt in self._pending_events.get(status, []):
            evt.set()
        if status != self._status:
            self._status = status
            LOGGER.debug("%s: changed _status to %r; is_on would now be %s", self._attr_name, self._status, self.is_on)
            self.async_schedule_update_ha_state(False)

    @property
    def is_on(self) -> bool:
        return self._status == "ON"

    async def async_turn_on(self, **kwargs) -> None:
        LOGGER.debug("%s: start async_turn_on", self._attr_name)
        evt = asyncio.Event()
        self._pending_events["ON"].append(evt)
        await self._clock.turn_on()
        LOGGER.debug("%s: waiting for async_turn_on evt", self._attr_name)
        await evt.wait()
        self._pending_events["ON"].remove(evt)
        LOGGER.debug("%s: finish async_turn_on", self._attr_name)

    async def async_turn_off(self, **kwargs) -> None:
        LOGGER.debug("%s: start async_turn_off", self._attr_name)
        evt = asyncio.Event()
        self._pending_events["OFF"].append(evt)
        await self._clock.turn_off()
        LOGGER.debug("%s: waiting for async_turn_off evt", self._attr_name)
        await evt.wait()
        self._pending_events["OFF"].remove(evt)
        LOGGER.debug("%s: finish async_turn_off", self._attr_name)
