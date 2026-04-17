import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor

from . import Rp2040UartHub

CONF_RP2040_UART_ID = "rp2040_uart_id"
CONF_BUTTON_ID = "button_id"

CONFIG_SCHEMA = binary_sensor.binary_sensor_schema().extend(
    {
        cv.GenerateID(CONF_RP2040_UART_ID): cv.use_id(Rp2040UartHub),
        cv.Required(CONF_BUTTON_ID): cv.uint8_t,
    }
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_RP2040_UART_ID])
    var = await binary_sensor.new_binary_sensor(config)
    cg.add(hub.set_button_sensor(config[CONF_BUTTON_ID], var))
