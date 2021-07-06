from abc import ABCMeta
from typing import Optional, Dict, Any, Union

from homeassistant.components.fan import FanEntity, SUPPORT_SET_SPEED
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from prana_rc.contrib.api import PranaStateDTO
from prana_rc.contrib.client.common import PranaRCAsyncClient
from prana_rc.entity import Speed

from . import const, utils

PranaEntity = Union["BasePranaEntity", "PranaDependantEntity"]


class CoordinatorEntity(Entity):
    """A class for entities using DataUpdateCoordinator."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Create the entity with a DataUpdateCoordinator."""
        self.coordinator = coordinator

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_coordinator_update))

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update the entity.

        Only used by the generic entity update service.
        """

        # Ignore manual update requests if the entity is disabled
        if not self.enabled:
            return

        await self.coordinator.async_request_refresh()


class BasePranaEntity(CoordinatorEntity):
    """Parent class for Prana entities"""

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            api_client: PranaRCAsyncClient,
            device_config: dict,
            base_entity_id: str,
            base_entity_name: str,
    ):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._base_entity_id = base_entity_id
        self._base_entity_name = base_entity_name
        self._device_config = device_config
        self.api_client = api_client

    @property
    def _prana_state(self) -> PranaStateDTO:
        return self.coordinator.data

    @property
    def device_address(self):
        return self._device_config[const.OPT_DEVICE_ADDRESS]

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo({
            'identifiers': {(const.DOMAIN, self.unique_id)},
            const.ATTR_DEVICE_ADDRESS: self._device_config.get(const.OPT_DEVICE_ADDRESS),
            const.ATTR_DEVICE_NAME: self._device_config.get(const.OPT_DEVICE_NAME),
        })

    @property
    def assumed_state(self) -> bool:
        return False


class PranaFanEntity(FanEntity, metaclass=ABCMeta):
    @property
    def preset_modes(self) -> Optional[list]:
        return utils.PRANA_SPEEDS + [None]  # type:ignore

    def percentage_to_speed(self, percentage: int) -> str:
        return utils.percentage_to_speed(percentage)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        if not hasattr(self, "_supported_features"):
            features = SUPPORT_SET_SPEED
            try:
                from homeassistant.components.fan import SUPPORT_PRESET_MODE

                features = SUPPORT_PRESET_MODE
            except ImportError:
                pass
            setattr(self, "_supported_features", features)
        return getattr(self, "_supported_features")

    @property
    def speed_list(self) -> Optional[list]:
        """Get the list of available speeds."""
        return self.preset_modes

    def speed_to_percentage(self, speed: str) -> int:
        speed_int = Speed.from_str(speed).value
        return speed_int * 10


class BaseMainPranaFan(BasePranaEntity, PranaFanEntity, metaclass=ABCMeta):
    pass


class PranaDependantEntity(CoordinatorEntity):
    def __init__(self, prana_main_entity: BaseMainPranaFan) -> None:
        super().__init__(prana_main_entity.coordinator)
        self.main_entity: BaseMainPranaFan = prana_main_entity

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self.main_entity.device_info

    @property
    def should_poll(self) -> bool:
        return True


class PranaSupplementaryFan(PranaDependantEntity, PranaFanEntity):
    pass
