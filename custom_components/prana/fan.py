import logging

from homeassistant.components.fan import FanEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# from prana_rc.contrib.client.common import PranaRCAsyncClient
from typing import List

from .entity import BasePranaEntityEntity
from . import const

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities, discovery_info=None):
    # prana_client: PranaRCAsyncClient = hass.data[const.DOMAIN][config_entry.entry_id][const.DATA_API_CLIENT]
    entities: List[BasePranaEntityEntity] = []

    if config_entry.get(const.CONF_CONNECTION_TYPE) == const.ConnectionType.REMOTE_HTTP_SERVER.value:
        pass
        #
        # async def async_get_state():
        #     try:
        #         return await prana_client.get_state()

        # Configure update coordinator
        # coordinator = DataUpdateCoordinator(
        #     hass, _LOGGER, update_method=
        # )

    else:
        _LOGGER.warning(
            "Connection type {} is not yet supported. This config entry will be ignored.".format(
                config_entry.get(const.CONF_CONNECTION_TYPE)
            )
        )

    if len(entities) > 0:
        async_add_entities(entities)
    return True


class PranaFan(FanEntity):
    def __init__(self, hass: HomeAssistant, entity_id: str, entity_name):
        self._unique_id = entity_id
        self._name = entity_name
        self._hass = hass
        _LOGGER.debug("Configured Prana main fan entity {}".format(self.name))

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def should_poll(self):
        return True
