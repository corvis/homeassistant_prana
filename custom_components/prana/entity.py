from abc import ABCMeta

from homeassistant.components.fan import FanEntity, SUPPORT_SET_SPEED
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from prana_rc.contrib.api import PranaStateDTO
from prana_rc.contrib.client.common import PranaRCAsyncClient
from typing import Optional, Dict, Any, Union

from . import const, utils

PranaEntity = Union["BasePranaEntity", "PranaDependantEntity"]


class BasePranaEntity(CoordinatorEntity):
    """Parent class for Prana entities"""

    def __init__(
        self,
        coordinator,
        api_client: PranaRCAsyncClient,
        device_config: dict,
        base_entity_id: str,
        base_entity_name: str,
    ):
        super().__init__(coordinator)
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
    def device_info(self) -> Optional[Dict[str, Any]]:
        return {
            const.ATTR_DEVICE_ADDRESS: self._device_config.get(const.OPT_DEVICE_ADDRESS),
            const.ATTR_DEVICE_NAME: self._device_config.get(const.OPT_DEVICE_NAME),
        }

    @property
    def assumed_state(self) -> bool:
        return False


class BaseMainPranaFan(BasePranaEntity, FanEntity, metaclass=ABCMeta):
    pass


class PranaDependantEntity(Entity):
    def __init__(self, prana_main_entity: BaseMainPranaFan) -> None:
        super().__init__()
        self.main_entity: BaseMainPranaFan = prana_main_entity

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self.main_entity.device_info

    @property
    def should_poll(self) -> bool:
        return True


class PranaSupplementaryFan(PranaDependantEntity, FanEntity):
    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_SET_SPEED

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return utils.PRANA_SPEEDS
