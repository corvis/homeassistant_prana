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
        entities.append(PranaVOC(prana_fan))
        entities.append(PranaHumidity(prana_fan))
        entities.append(PranaAirPressure(prana_fan))
        entities.append(PranaAirTemperatureIn(prana_fan))
        entities.append(PranaAirTemperatureOut(prana_fan))

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
        prana_value = self.main_entity._prana_state.sensors.co2
        return prana_value


class PranaVOC(PranaDependantEntity, SensorEntity):

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:air-filter"

    @property
    def unique_id(self) -> Optional[str]:
        return self.main_entity.unique_id + "_voc"

    @property
    def name(self) -> Optional[str]:
        return self.main_entity.name + " VOC"

    @property
    def native_value(self):
        prana_value = self.main_entity._prana_state.sensors.voc
        return prana_value


class PranaHumidity(PranaDependantEntity, SensorEntity):

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:water-percent"

    @property
    def unique_id(self) -> Optional[str]:
        return self.main_entity.unique_id + "_humidity"

    @property
    def name(self) -> Optional[str]:
        return self.main_entity.name + " Humidity"

    @property
    def native_value(self):
        prana_value = self.main_entity._prana_state.sensors.humidity
        return prana_value


class PranaAirPressure(PranaDependantEntity, SensorEntity):

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:gauge"

    @property
    def unique_id(self) -> Optional[str]:
        return self.main_entity.unique_id + "_pressure"

    @property
    def name(self) -> Optional[str]:
        return self.main_entity.name + " Pressure"

    @property
    def native_value(self):
        prana_value = self.main_entity._prana_state.sensors.pressure
        return prana_value


class PranaAirTemperatureIn(PranaDependantEntity, SensorEntity):

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer"

    @property
    def unique_id(self) -> Optional[str]:
        return self.main_entity.unique_id + "_temperature_in"

    @property
    def name(self) -> Optional[str]:
        return self.main_entity.name + " Temperature In"

    @property
    def native_value(self):
        prana_value = self.main_entity._prana_state.sensors.temperature_in
        return prana_value


class PranaAirTemperatureOut(PranaDependantEntity, SensorEntity):

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer"

    @property
    def unique_id(self) -> Optional[str]:
        return self.main_entity.unique_id + "_temperature_out"

    @property
    def name(self) -> Optional[str]:
        return self.main_entity.name + " Temperature Out"

    @property
    def native_value(self):
        prana_value = self.main_entity._prana_state.sensors.temperature_out
        return prana_value
