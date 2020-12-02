import logging
import urllib.parse

import voluptuous as vol
from homeassistant import config_entries
from typing import Dict

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
