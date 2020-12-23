import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, Config
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from custom_components.prana.entity import BaseMainPranaFan
from . import const, utils

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured Prana integration based on the yaml config"""
    # TODO: transform yaml into config entry
    hass.data.setdefault(const.DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up Prana from a config entry."""
    _LOGGER.debug("Loading config entry {} (id: {})".format(config_entry.title, config_entry.entry_id))
    api_client = utils.api_client_from_config(config_entry.data)
    await api_client.init()

    # Subscribe for changes to config entry
    undo_config_update_listener = config_entry.add_update_listener(update_config_listener)

    # Bootstrap data structure for config entry
    hass.data[const.DOMAIN][config_entry.entry_id] = {
        const.DATA_API_CLIENT: api_client,
        const.DATA_UNDO_UPDATE_CONF_UPDATE_LISTENER: undo_config_update_listener,
        const.DATA_ENTITIES: [],
        const.DATA_MAIN_ENTITIES: [],
        const.DATA_DISPATCHER_DISPOSERS: [],
    }

    entry_data = hass.data[const.DOMAIN][config_entry.entry_id]

    async def handle_main_entities_initialized():  # Initialize the rest of the platforms (supplementary entities)
        for component in const.PLATFORMS[1:]:
            hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, component))

    entry_data[const.DATA_DISPATCHER_DISPOSERS].append(
        async_dispatcher_connect(hass, const.SIGNAL_PRANA_MAIN_INITIALIZED, handle_main_entities_initialized)
    )

    # Run fan platform initialization
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, const.PLATFORMS[0]))

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Destroy resources related to config entry"""
    _LOGGER.debug("Unloading config entry {} (id: {})".format(config_entry.title, config_entry.entry_id))
    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(config_entry, component) for component in const.PLATFORMS]
        )
    )
    entry_data = hass.data[const.DOMAIN][config_entry.entry_id]

    # Disposing client
    try:
        await entry_data[const.DATA_API_CLIENT].close()
    except Exception as e:
        _LOGGER.warning("Unable to gracefully close prana_rc client session: " + str(e))
    finally:
        entry_data[const.DATA_API_CLIENT] = None

    # Remove entities from hass
    # await asyncio.gather(*[entity.async_remove() for entity in entry_data[const.DATA_ENTITIES]])
    entry_data[const.DATA_ENTITIES] = []

    entry_data[const.DATA_UNDO_UPDATE_CONF_UPDATE_LISTENER]()

    # Cancel dispatchers
    for dispose in entry_data[const.DATA_DISPATCHER_DISPOSERS]:
        dispose()

    if unload_ok:
        hass.data[const.DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_config_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Will be invoked after once entry updated."""
    _LOGGER.debug(
        "Config entry {}(id: {}) updated. Platform reload will be triggered".format(
            config_entry.title, config_entry.entry_id
        )
    )
    await hass.config_entries.async_reload(config_entry.entry_id)
