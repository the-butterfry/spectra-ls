import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ID, CONF_UART_ID

DEPENDENCIES = ["uart"]

arylic_uart_ns = cg.esphome_ns.namespace("arylic_uart")
ArylicUart = arylic_uart_ns.class_("ArylicUart", cg.Component, uart.UARTDevice)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(ArylicUart),
}).extend(uart.UART_DEVICE_SCHEMA)


async def to_code(config):
    uart_parent = await cg.get_variable(config[CONF_UART_ID])
    var = cg.new_Pvariable(config[CONF_ID], uart_parent)
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)
