from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import const


class BasePranaEntityEntity(CoordinatorEntity):
    """Parent class for Prana entities"""

    def __init__(self, hass, entry_data: dict, base_entity_id: str, base_entity_name: str):
        super().__init__(entry_data[const.DATA_COORDINATOR])
        self._base_entity_id = base_entity_id
        self._base_entity_name = base_entity_name
