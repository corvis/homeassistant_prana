from enum import Enum

# Common consts
DOMAIN = "prana"
PLATFORMS = ("fan", "switch", "light")  # MUST BE THE FIRST IN THE LIST

SIGNAL_PRANA_MAIN_INITIALIZED = "prana_main_initialized"

PRANA_DISCOVERY_TIMEOUT = 10


class ConnectionType(Enum):
    LOCAL_BLE = "local_ble"
    REMOTE_HTTP_SERVER = "remote_http"
    REMOTE_WEBSOCKET = "remore_ws"


# Config properties
CONF_CONNECTION_TYPE = "connection_type"
CONF_BASE_URL = "base_url"

CONNECTION_TYPE_MAP = {ConnectionType.REMOTE_HTTP_SERVER: "HTTP"}

# Options
OPT_LAST_UPDATE = "_timestamp"
OPT_DEVICES = "devices"
OPT_DEVICE_NAME = "name"
OPT_DEVICE_ADDRESS = "addr"

# Config flow user input keys
INP_DEVICE = "device"
INP_DISCOVERED_DEVICES = "discovered_device"
INP_DEVICE_ADD_DEVICE = "add_new"
INP_DEVICE_DISCOVER_DEVICE = "discover_new"

# Runtime data fields
DATA_API_CLIENT = "prana_rc_client"
DATA_MAIN_ENTITIES = "main_entities"
DATA_ENTITIES = "entities"
DATA_DISPATCHER_DISPOSERS = "dispatcher_disposers"
DATA_UNDO_UPDATE_CONF_UPDATE_LISTENER = "undo_config_update_listener"

# Entity attributes
ATTR_LAST_UPDATED = "last_updated"
ATTR_FLOWS_LOCKED = "flows_locked"
ATTR_IN_SPEED = "input_speed"
ATTR_OUT_SPEED = "output_speed"
ATTR_WINTER_MODE_ON = "winter_mode"
ATTR_HEATING = "heating"
ATTR_BRIGHTNESS = "brightness"

# Device attributes
ATTR_DEVICE_ADDRESS = "ble_address"
ATTR_DEVICE_NAME = "name"

# Other
DIRECTION_IN = "in"
DIRECTION_OUT = "out"
DIRECTION_BOTH = "both"
