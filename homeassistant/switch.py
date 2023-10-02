from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity

from .const import DOMAIN

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

    async def async_added_to_hass(self) -> None:
        self._clock.event_receivers.append(self.event_receiver)

    async def async_will_remove_from_hass(self):
        self._clock.event_receivers.remove(self.event_receiver)

    def event_receiver(self, event):
        # event: { event: True, status: ON/OFF }
        status = event.get("status")
        if status != self._status:
            self._status = status
            self.async_schedule_update_ha_state(True)

    @property
    def is_on(self) -> bool:
        return self._status == "ON"

    async def async_turn_on(self, **kwargs) -> None:
        await self._clock.turn_on()

    async def async_turn_off(self, **kwargs) -> None:
        await self._clock.turn_off()
