import hashlib
import logging
from typing import Dict

from prana_rc.contrib.client.aiohttp import PranaRCAioHttpClient
from prana_rc.contrib.client.common import PranaRCAsyncClient

from . import const

PRANA_SPEEDS = ["Off", "Low", "2", "3", "4", "5", "6", "7", "8", "High"]
PRANA_DEFAULT_SPEED = "2"


def api_client_from_config(config: Dict) -> PranaRCAsyncClient:
    return PranaRCAioHttpClient(config.get(const.CONF_BASE_URL))


def handle_prana_error(e: Exception, errors: Dict, logger: logging.Logger):
    errors["base"] = "unable_to_connect_to_server"
    logger.exception("Unable to connect to prana rc server")


def generate_unique_id(config: Dict):
    hash_alg = hashlib.sha1()
    hash_alg.update(config[const.CONF_CONNECTION_TYPE].encode("utf-8"))
    hash_alg.update(config[const.CONF_BASE_URL].encode("utf-8"))
    return hash_alg.hexdigest()


def speed_int_to_str(speed: int) -> str:
    return PRANA_SPEEDS[speed]


def percentage_to_speed(percentage: int) -> str:
    if percentage == 0:
        return PRANA_SPEEDS[0]
    return PRANA_SPEEDS[int(percentage / len(PRANA_SPEEDS))]
