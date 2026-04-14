import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ID, CONF_UART_ID

DEPENDENCIES = ["uart"]

rp2040_uart_ns = cg.esphome_ns.namespace("rp2040_uart")
Rp2040UartHub = rp2040_uart_ns.class_("Rp2040UartHub", cg.Component, uart.UARTDevice)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(Rp2040UartHub),
}).extend(uart.UART_DEVICE_SCHEMA)


async def to_code(config):
    uart_parent = await cg.get_variable(config[CONF_UART_ID])
    var = cg.new_Pvariable(config[CONF_ID], uart_parent)
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)
