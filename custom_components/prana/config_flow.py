import datetime
import logging
import urllib.parse
from typing import Dict

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from prana_rc.contrib.client.common import PranaRCAsyncClient

from . import const, utils

_LOGGER = logging.getLogger(__name__)


class PranaFlowHandler(config_entries.ConfigFlow, domain=const.DOMAIN):  # type: ignore[call-arg] # noqa
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input: dict = None):
        if user_input is not None:
            if user_input[const.CONF_CONNECTION_TYPE] == const.ConnectionType.REMOTE_HTTP_SERVER.value:
                return await self.async_step_remote_connection(
                    connection_type=const.ConnectionType(user_input[const.CONF_CONNECTION_TYPE])
                )
        else:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            const.CONF_CONNECTION_TYPE, default=const.ConnectionType.REMOTE_HTTP_SERVER.value
                        ): vol.In({k.value: v for k, v in const.CONNECTION_TYPE_MAP.items()}),
                    }
                ),
            )

    async def async_step_remote_connection(self, user_input: dict = None, connection_type: const.ConnectionType = None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            prana_client = utils.api_client_from_config(user_input)
            try:
                await prana_client.init()
                await prana_client.healthcheck()
                config = dict(user_input)
                parsed_url = urllib.parse.urlparse(user_input[const.CONF_BASE_URL])
                unique_id = utils.generate_unique_id(config)
                await self.async_set_unique_id(unique_id, raise_on_progress=False)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Prana Hub @ " + parsed_url.netloc, data=config)
            except Exception as e:
                utils.handle_prana_error(e, errors, _LOGGER)
            finally:
                await prana_client.close()

        if user_input is None:
            assert connection_type is not None, "connection_type must be passed as an argument from the prev. step"

            user_input = {
                const.CONF_BASE_URL: "http://localhost:8881",
                const.CONF_CONNECTION_TYPE: connection_type.value,
            }
        connection_type_name = const.CONNECTION_TYPE_MAP.get(
            const.ConnectionType(user_input.get(const.CONF_CONNECTION_TYPE))
        )
        return self.async_show_form(
            step_id="remote_connection",
            data_schema=vol.Schema(
                {
                    vol.Required(const.CONF_BASE_URL, default=user_input.get(const.CONF_BASE_URL)): str,
                    vol.Required(
                        const.CONF_CONNECTION_TYPE, default=user_input.get(const.CONF_CONNECTION_TYPE)
                    ): vol.In({user_input.get(const.CONF_CONNECTION_TYPE): connection_type_name}),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return PranaOptionsFlowHandler(config_entry)


class PranaOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry
        self.current_options = config_entry.options or {const.OPT_DEVICES: {}}

    def preserve_options_section(self, value: dict):
        result = dict(self.current_options)
        addr = value[const.OPT_DEVICE_ADDRESS] = value[const.OPT_DEVICE_ADDRESS].strip()
        result[const.OPT_DEVICES][addr] = value
        result[const.OPT_LAST_UPDATE] = int(datetime.datetime.now().timestamp())
        return self.async_create_entry(
            title="",
            data=result,
        )

    async def async_step_init(self, user_input=None):
        errors = {}

        if user_input is not None:
            if user_input[const.INP_DEVICE] == const.INP_DEVICE_ADD_DEVICE:
                return await self.async_step_edit_device()
            elif user_input[const.INP_DEVICE] == const.INP_DEVICE_DISCOVER_DEVICE:
                return await self.async_step_discover()
            elif user_input[const.INP_DEVICE] in self.current_options[const.OPT_DEVICES].keys():
                return await self.async_step_edit_device(addr=user_input[const.INP_DEVICE])

        devices_options = {
            x.get(const.OPT_DEVICE_ADDRESS): "{} [{}]".format(
                x.get(const.OPT_DEVICE_NAME), x.get(const.OPT_DEVICE_ADDRESS)
            )
            for x in self.current_options.get(const.OPT_DEVICES).values()
        }

        devices_options[const.INP_DEVICE_ADD_DEVICE] = "Add new device..."
        devices_options[const.INP_DEVICE_DISCOVER_DEVICE] = "Discover new device..."

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Required(const.INP_DEVICE, default=const.INP_DEVICE_DISCOVER_DEVICE): vol.In(devices_options)}
            ),
            errors=errors,
        )

    async def async_step_edit_device(self, user_input: Dict = None, addr: str = None):
        errors = {}
        current = {}
        if addr is not None:
            current = self.current_options[const.OPT_DEVICES].get(addr)

        if user_input is not None and addr is None:
            if current is None:
                current = self.current_options[const.OPT_DEVICES].get(user_input.get(const.OPT_DEVICE_ADDRESS))

            # Todo: validate input?
            prana_client: PranaRCAsyncClient = utils.api_client_from_config(self.config_entry.data)
            async with prana_client as c:
                try:
                    await c.get_state(user_input.get(const.OPT_DEVICE_ADDRESS))
                except Exception:
                    errors["base"] = "unable_to_connect"
                    _LOGGER.exception(
                        "Unable to conenct to ble device " + str(user_input.get(const.OPT_DEVICE_ADDRESS))
                    )

            if len(errors.keys()) == 0:
                return self.preserve_options_section(user_input)
        else:
            # We came here from the discover dialog
            if user_input is not None:
                current = user_input  # type: ignore

        schema_dict = {
            vol.Required(
                const.OPT_DEVICE_ADDRESS,
                default=current.get(const.OPT_DEVICE_ADDRESS, ""),
            ): str,
            vol.Required(
                const.OPT_DEVICE_NAME,
                default=current.get(const.OPT_DEVICE_NAME, ""),
            ): str,
        }

        return self.async_show_form(
            step_id="edit_device", data_schema=vol.Schema(schema_dict), description_placeholders={}, errors=errors
        )

    async def async_step_discover(self, user_input: Dict = None):
        errors = {}
        devs_options = {}

        if user_input is not None:
            address, name = user_input[const.INP_DISCOVERED_DEVICES].split("/", 1)
            return await self.async_step_edit_device(
                {const.OPT_DEVICE_NAME: name, const.OPT_DEVICE_ADDRESS: address}, addr=address
            )

        prana_client: PranaRCAsyncClient = utils.api_client_from_config(self.config_entry.data)
        async with prana_client as c:
            try:
                discovered_devs = (await c.discover(timeout=const.PRANA_DISCOVERY_TIMEOUT)) or []
                devs_options = {
                    "{}/{}".format(x["address"], x["name"]): "{} [{}]".format(x["name"], x["address"])
                    for x in discovered_devs
                }
            except Exception:
                errors["base"] = "discovery_error"
                _LOGGER.exception("Unable to complete BLE discovery")

        return self.async_show_form(
            step_id="discover",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        const.INP_DISCOVERED_DEVICES,
                        default=next(iter(devs_options)) if len(devs_options.keys()) > 0 else None,
                    ): vol.In(devs_options)
                }
            ),
            errors=errors,
        )
