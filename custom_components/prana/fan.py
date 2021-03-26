import datetime
import logging
from typing import List, Tuple, Optional, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from prana_rc.contrib.api import SetStateDTO
from prana_rc.contrib.client.common import PranaRCAsyncClient
from prana_rc.entity import Speed

from . import const, utils
from .entity import PranaEntity, BaseMainPranaFan, PranaSupplementaryFan

_LOGGER = logging.getLogger(__name__)
UPDATE_INTERVAL = datetime.timedelta(seconds=30)
PRANA_API_ATTEMPTS = 5
PRANA_API_TIMEOUT = 5


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities, discovery_info=None):
    prana_client: PranaRCAsyncClient = hass.data[const.DOMAIN][config_entry.entry_id][const.DATA_API_CLIENT]
    entities: List[PranaEntity] = []

    if config_entry.data.get(const.CONF_CONNECTION_TYPE) == const.ConnectionType.REMOTE_HTTP_SERVER.value:
        for device_config in config_entry.options.get(const.OPT_DEVICES, {}).values():
            device_coordinator, device_entities = await setup_prana_device(
                hass, prana_client, device_config, config_entry.data
            )
            entities += device_entities
    else:
        _LOGGER.warning(
            "Connection type {} is not yet supported. This config entry will be ignored.".format(
                config_entry.get(const.CONF_CONNECTION_TYPE)
            )
        )

    if len(entities) > 0:
        hass.data[const.DOMAIN][config_entry.entry_id][const.DATA_MAIN_ENTITIES] += entities
        # At the moment we registered just main entities. Let's build supplementary fans
        for main_entity in entities.copy():
            entities.append(PranaInputFan(main_entity))
            entities.append(PranaOutputFan(main_entity))
        hass.data[const.DOMAIN][config_entry.entry_id][const.DATA_ENTITIES] += entities
        async_add_entities(entities)

    async_dispatcher_send(hass, const.SIGNAL_PRANA_MAIN_INITIALIZED)

    return True


async def setup_prana_device(
    hass: HomeAssistant, prana_client: PranaRCAsyncClient, device_config: dict, hub_config: dict
) -> Tuple[DataUpdateCoordinator, List[PranaEntity]]:
    device_entities = []
    entity_id = "prana_" + device_config[const.OPT_DEVICE_ADDRESS].replace(":", "_")
    entity_name = device_config[const.OPT_DEVICE_NAME]

    async def async_get_state():
        try:
            return await prana_client.get_state(
                device_config[const.OPT_DEVICE_ADDRESS], timeout=PRANA_API_TIMEOUT, attempts=PRANA_API_ATTEMPTS
            )
        except Exception as e:
            _LOGGER.warning("Can't read data from prana recuperator {} ({}): ".format(entity_name, entity_id) + str(e))
            raise e

    # Configure update coordinator
    coordinator = DataUpdateCoordinator(
        hass, _LOGGER, name=entity_id, update_method=async_get_state, update_interval=UPDATE_INTERVAL
    )

    main_entity = PranaMainFan(coordinator, prana_client, device_config, entity_id, entity_name)
    device_entities.append(main_entity)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    return coordinator, device_entities


class PranaMainFan(BaseMainPranaFan):
    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api_client: PranaRCAsyncClient,
        device_config: dict,
        base_entity_id: str,
        base_entity_name,
    ):
        super().__init__(coordinator, api_client, device_config, base_entity_id, base_entity_name)
        _LOGGER.debug("Configured Prana main fan entity {}".format(self.name))

    @property
    def unique_id(self) -> str:
        return self._base_entity_id

    @property
    def name(self) -> str:
        return self._base_entity_name

    @property
    def is_on(self) -> Optional[bool]:
        if self._prana_state is not None:
            return self._prana_state.is_on
        else:
            return None

    @property
    def speed(self) -> Optional[str]:
        if self._prana_state is not None:
            return utils.speed_int_to_str(self._prana_state.speed_locked)
        else:
            return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode == utils.PRANA_SPEEDS[0]:
            await self.async_turn_off()
        prana_speed = Speed.from_str(preset_mode if preset_mode is not None else utils.PRANA_DEFAULT_SPEED)
        await self.api_client.set_state(self.device_address, SetStateDTO(speed=prana_speed))
        await self.coordinator.async_refresh()

    @property
    def current_direction(self) -> Optional[str]:
        state = self._prana_state
        if state is None or not state.is_on:
            return None
        if state.flows_locked:
            return const.DIRECTION_BOTH
        else:
            return const.DIRECTION_IN if state.is_input_fan_on else const.DIRECTION_OUT

    @property
    def state_attributes(self) -> dict:
        state = self._prana_state
        if state is None or not state.is_on:
            return {}
        attributes = super().state_attributes
        in_speed, out_speed = state.speed_locked, state.speed_locked if state.is_on else (0, 0)
        if not state.flows_locked:
            in_speed = state.speed_in if state.is_input_fan_on else 0
            out_speed = state.speed_out if state.is_output_fan_on else 0
        attributes.update(
            {
                # const.ATTR_LAST_UPDATED: state.timestamp.isoformat()
                const.ATTR_BRIGHTNESS: state.brightness,
                const.ATTR_FLOWS_LOCKED: state.flows_locked,
                const.ATTR_HEATING: state.mini_heating_enabled,
                const.ATTR_WINTER_MODE_ON: state.winter_mode_enabled,
                const.ATTR_IN_SPEED: in_speed,
                const.ATTR_OUT_SPEED: out_speed,
            }
        )
        return attributes

    async def async_turn_on(self, speed: Optional[str] = "2", **kwargs):
        """Turn on the fan."""
        await self.async_set_preset_mode(speed or utils.PRANA_DEFAULT_SPEED)
        return self.is_on

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn onn the fan."""
        await self.api_client.set_state(self.device_address, SetStateDTO(speed=Speed.OFF))
        await self.coordinator.async_refresh()


class PranaInputFan(PranaSupplementaryFan):
    @property
    def unique_id(self) -> Optional[str]:
        return self.main_entity.unique_id + "_input"

    @property
    def name(self) -> Optional[str]:
        return self.main_entity.name + " Input"

    @property
    def is_on(self) -> bool:
        return self.main_entity.state_attributes.get(const.ATTR_IN_SPEED, 0) != 0

    @property
    def speed(self) -> Optional[str]:
        return utils.speed_int_to_str(self.main_entity.state_attributes.get(const.ATTR_IN_SPEED, 0))

    async def async_turn_on(self, speed: Optional[str] = "2", **kwargs) -> None:
        pass  # Not supported yet

    async def async_turn_off(self, **kwargs: Any) -> None:
        pass  # Not supported yet


class PranaOutputFan(PranaSupplementaryFan):
    @property
    def unique_id(self) -> Optional[str]:
        return self.main_entity.unique_id + "_output"

    @property
    def name(self) -> Optional[str]:
        return self.main_entity.name + " Output"

    @property
    def is_on(self) -> bool:
        return self.main_entity.state_attributes.get(const.ATTR_OUT_SPEED, 0) != 0

    @property
    def speed(self) -> Optional[str]:
        return utils.speed_int_to_str(self.main_entity.state_attributes.get(const.ATTR_OUT_SPEED, 0))

    async def async_turn_on(self, speed: Optional[str] = "2", **kwargs) -> None:
        pass  # Not supported yet

    async def async_turn_off(self, **kwargs: Any) -> None:
        pass  # Not supported yet
