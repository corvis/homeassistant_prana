#    hass-hikvision-connector
#    Copyright (C) 2020 Dmitry Berezovsky
#    The MIT License (MIT)
#
#    Permission is hereby granted, free of charge, to any person obtaining
#    a copy of this software and associated documentation files
#    (the "Software"), to deal in the Software without restriction,
#    including without limitation the rights to use, copy, modify, merge,
#    publish, distribute, sublicense, and/or sell copies of the Software,
#    and to permit persons to whom the Software is furnished to do so,
#    subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from enum import Enum

# Common consts
DOMAIN = "prana"
PLATFORMS = ("fan",)


class ConnectionType(Enum):
    LOCAL_BLE = "local_ble"
    REMOTE_HTTP_SERVER = "remote_http"
    REMOTE_WEBSOCKET = "remore_ws"


# Config properties
CONF_CONNECTION_TYPE = "connection_type"
CONF_BASE_URL = "base_url"

CONNECTION_TYPE_MAP = {ConnectionType.REMOTE_HTTP_SERVER: "HTTP"}

# Options
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
DATA_ENTITIES = "entities"
DATA_COORDINATOR = "coordinator"
DATA_UNDO_UPDATE_CONF_UPDATE_LISTENER = "undo_config_update_listener"

# Entity attributes
ATTR_LAST_UPDATED = "last_updated"
