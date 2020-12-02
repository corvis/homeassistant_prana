import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, Config

from . import const

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured Prana integration based on the yaml config"""
    # TODO: transform yaml into config entry
    hass.data.setdefault(const.DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up Prana from a config entry."""
    _LOGGER.debug("Loading config entry {} (id: {})".format(config_entry.title, config_entry.entry_id))


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Destroy resources related to config entry"""
    pass


async def update_config_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Will be invoked after once entry updated."""
    _LOGGER.debug(
        "Config entry {}(id: {}) updated. Platform reload will be triggered".format(
            config_entry.title, config_entry.entry_id
        )
    )
    await hass.config_entries.async_reload(config_entry.entry_id)
