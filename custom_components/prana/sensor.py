from typing import List, Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.prana import const
from custom_components.prana.entity import PranaDependantEntity


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities, discovery_info=None):
    entities: List[PranaDependantEntity] = []

    for prana_fan in hass.data[const.DOMAIN][config_entry.entry_id][const.DATA_MAIN_ENTITIES]:
        entities.append(PranaCO2(prana_fan))

    if len(entities) > 0:
        async_add_entities(entities)
        hass.data[const.DOMAIN][config_entry.entry_id][const.DATA_ENTITIES] += entities


class PranaCO2(PranaDependantEntity, SensorEntity):

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:molecule-co2"

    @property
    def unique_id(self) -> Optional[str]:
        return self.main_entity.unique_id + "_co2"

    @property
    def name(self) -> Optional[str]:
        return self.main_entity.name + " CO2"

    @property
    def native_value(self):
        """Return the brightness of this light between 0..255."""
        prana_value = self.main_entity._prana_state.sensors.co2
        return prana_value
