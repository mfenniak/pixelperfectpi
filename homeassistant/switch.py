"""Platform for sensor integration."""

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity

from .const import DOMAIN

# See cover.py for more details.
# Note how both entities for each roller sensor (battry and illuminance) are added at
# the same time to the same list. This way only a single async_add_devices call is
# required.
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    hub = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([ PipixelperfectSwitch(hub) ])

    # new_devices = []
    # for roller in hub.rollers:
    #     new_devices.append(BatterySensor(roller))
    #     new_devices.append(IlluminanceSensor(roller))
    # if new_devices:
    #     async_add_entities(new_devices)


# This base class shows the common properties and methods for a sensor as used in this
# example. See each sensor for further details about properties and methods that
# have been overridden.
class PipixelperfectSwitch(SwitchEntity):
    """Base representation of a Hello World Sensor."""

    _attr_should_poll = False

    def __init__(self, hub):
        """Initialize the sensor."""
        self._hub = hub
        self._attr_name = f"pixelperfectpi {self._hub._host}"
        self._status = self._hub.last_status

    async def async_added_to_hass(self) -> None:
        self._hub.event_receivers.append(self.event_receiver)

    async def async_will_remove_from_hass(self):
        self._hub.event_receivers.remove(self.event_receiver)

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
        await self._hub.turn_on()

    async def async_turn_off(self, **kwargs) -> None:
        await self._hub.turn_off()
