from typing import List, Optional, Any

from homeassistant.components.light import LightEntity, SUPPORT_BRIGHTNESS
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.prana import const
from custom_components.prana.entity import PranaDependantEntity

PRANA_BRIGHTNESS_MAX = 6
PRANA_BRIGHTNESS_MIN = 0


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities, discovery_info=None):
    entities: List[PranaDependantEntity] = []

    for prana_fan in hass.data[const.DOMAIN][config_entry.entry_id][const.DATA_MAIN_ENTITIES]:
        entities.append(PranaBrightness(prana_fan))

    if len(entities) > 0:
        async_add_entities(entities)
        hass.data[const.DOMAIN][config_entry.entry_id][const.DATA_ENTITIES] += entities


class PranaBrightness(PranaDependantEntity, LightEntity):
    @property
    def unique_id(self) -> Optional[str]:
        return self.main_entity.unique_id + "_brightness"

    @property
    def name(self) -> Optional[str]:
        return self.main_entity.name + " Brightness"

    @property
    def is_on(self) -> bool:
        return self.main_entity.is_on and self.main_entity.state_attributes.get(const.ATTR_BRIGHTNESS, 0) > 0

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        prana_value = self.main_entity._prana_state.brightness
        return int(prana_value * (255 / PRANA_BRIGHTNESS_MAX))

    async def async_turn_on(self, brightness: int) -> None:
        pass  # Not supported yet

    async def async_turn_off(self, **kwargs: Any) -> None:
        pass  # Not supported yet
