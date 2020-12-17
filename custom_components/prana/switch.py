from typing import Optional, Any, List

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from prana_rc.contrib.api import SetStateDTO

from custom_components.prana import const
from custom_components.prana.entity import PranaDependantEntity


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities, discovery_info=None):
    entities: List[PranaDependantEntity] = []

    for prana_fan in hass.data[const.DOMAIN][config_entry.entry_id][const.DATA_MAIN_ENTITIES]:
        entities.append(PranaHeating(prana_fan))
        entities.append(PranaWinterMode(prana_fan))

    if len(entities) > 0:
        async_add_entities(entities)
        hass.data[const.DOMAIN][config_entry.entry_id][const.DATA_ENTITIES] += entities


class PranaHeating(PranaDependantEntity, SwitchEntity):
    @property
    def unique_id(self) -> Optional[str]:
        return self.main_entity.unique_id + "_heating"

    @property
    def name(self) -> Optional[str]:
        return self.main_entity.name + " Heating"

    @property
    def is_on(self) -> bool:
        return self.main_entity.is_on and self.main_entity.state_attributes.get(const.ATTR_HEATING, False)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.main_entity.api_client.set_state(self.main_entity.device_address, SetStateDTO(heating=False))
        await self.main_entity.coordinator.async_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.main_entity.api_client.set_state(self.main_entity.device_address, SetStateDTO(heating=True))
        await self.main_entity.coordinator.async_refresh()


class PranaWinterMode(PranaDependantEntity, SwitchEntity):
    @property
    def unique_id(self) -> Optional[str]:
        return self.main_entity.unique_id + "_winter_mode"

    @property
    def name(self) -> Optional[str]:
        return self.main_entity.name + " Winter Mode"

    @property
    def is_on(self) -> bool:
        return self.main_entity.is_on and self.main_entity.state_attributes.get(const.ATTR_WINTER_MODE_ON, False)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.main_entity.api_client.set_state(self.main_entity.device_address, SetStateDTO(winter_mode=False))
        await self.main_entity.coordinator.async_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.main_entity.api_client.set_state(self.main_entity.device_address, SetStateDTO(winter_mode=True))
        await self.main_entity.coordinator.async_refresh()
