import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import CONF_TYPE

from . import ArylicUart

CONF_ARYLIC_UART_ID = "arylic_uart_id"

TYPE_SOURCE = "source"
TYPE_TITLE = "title"
TYPE_ARTIST = "artist"
TYPE_ALBUM = "album"

CONFIG_SCHEMA = text_sensor.text_sensor_schema().extend(
    {
        cv.GenerateID(CONF_ARYLIC_UART_ID): cv.use_id(ArylicUart),
        cv.Required(CONF_TYPE): cv.one_of(TYPE_SOURCE, TYPE_TITLE, TYPE_ARTIST, TYPE_ALBUM, lower=True),
    }
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_ARYLIC_UART_ID])
    var = await text_sensor.new_text_sensor(config)
    sensor_type = config[CONF_TYPE]
    if sensor_type == TYPE_SOURCE:
        cg.add(hub.set_source_sensor(var))
    elif sensor_type == TYPE_TITLE:
        cg.add(hub.set_title_sensor(var))
    elif sensor_type == TYPE_ARTIST:
        cg.add(hub.set_artist_sensor(var))
    else:
        cg.add(hub.set_album_sensor(var))
