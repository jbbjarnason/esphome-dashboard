import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.components import web_server_base
from esphome.components.web_server_base import CONF_WEB_SERVER_BASE_ID
from esphome.const import (
    CONF_PORT,
    CONF_AUTH,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_ID,
    CONF_TYPE,
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_MIN_VALUE,
    CONF_MAX_VALUE,
    CONF_LAMBDA,
)
from esphome.core import coroutine_with_priority
from esphome.cpp_generator import MockObj

AUTO_LOAD = ["json", "async_tcp"]

CONF_TABS = "tabs"
CONF_CARDS = "cards"
CONF_CHARTS = "charts"
CONF_DEFAULT_VALUE = "default_value"
CONF_NAVIGATION_NAME = "navigation_name"
CONF_HEADER = "header"
CONF_STATISTICS = "statistics"

CODEOWNERS = ["@jbbjarnason"]
DEPENDENCIES = ["network"]

dashboard_ns = cg.esphome_ns.namespace("dashboard")
global_ns = cg.global_ns
web_server_ns = cg.esphome_ns.namespace("web_server")

WebServer = web_server_ns.class_("WebServer", cg.Component, cg.Controller)
Dashboard = dashboard_ns.class_("Dashboard", cg.PollingComponent)
CardClass = global_ns.class_("Card")
ChartClass = global_ns.class_("Chart")
TabClass = global_ns.class_("Tab")


CardTypes = global_ns.enum("CardTypes")
CARD_TYPES = {
    "generic": CardTypes.GENERIC_CARD,
    "temperature": CardTypes.TEMPERATURE_CARD,
    "humidity": CardTypes.HUMIDITY_CARD,
    "status": CardTypes.STATUS_CARD,
    "slider": CardTypes.SLIDER_CARD,
    "button": CardTypes.BUTTON_CARD,
    "progress": CardTypes.PROGRESS_CARD,
}

ChartTypes = global_ns.enum("ChartTypes")
CHART_TYPES = {
    "bar": ChartTypes.BAR_CHART,
}

CARDS_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(CardClass),
        cv.Required(CONF_TYPE): cv.enum(CARD_TYPES),
        cv.Required(CONF_NAME): cv.string_strict,
        cv.Optional(CONF_UNIT_OF_MEASUREMENT): cv.string_strict,
        cv.Optional(CONF_MIN_VALUE): cv.float_,
        cv.Optional(CONF_MAX_VALUE): cv.float_,
        cv.Optional(CONF_DEFAULT_VALUE): cv.Any(cv.float_, cv.string, cv.int_),
        cv.Optional(CONF_LAMBDA): cv.lambda_,
    }
)

CHARTS_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(ChartClass),
        cv.Required(CONF_TYPE): cv.enum(CHART_TYPES),
        cv.Required(CONF_NAME): cv.string_strict,
    }
)

TABS_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(TabClass),
        cv.Required(CONF_NAME): cv.string_strict,
        cv.Required(CONF_NAVIGATION_NAME): cv.string_strict,
        cv.Optional(CONF_HEADER): cv.string_strict,
        cv.Optional(CONF_CARDS): cv.ensure_list(CARDS_SCHEMA),
        cv.Optional(CONF_CHARTS): cv.ensure_list(CHARTS_SCHEMA),
    }
)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(Dashboard),
        cv.Optional(CONF_PORT, default=80): cv.port,
        cv.Optional(CONF_AUTH): cv.Schema(
            {
                cv.Required(CONF_USERNAME): cv.string_strict,
                cv.Required(CONF_PASSWORD): cv.string_strict,
            }
        ),
        cv.Optional(CONF_STATISTICS): cv.boolean,
        cv.Optional(CONF_TABS): cv.ensure_list(TABS_SCHEMA),
        cv.Optional(CONF_CARDS): cv.ensure_list(CARDS_SCHEMA),
        cv.Optional(CONF_CHARTS): cv.ensure_list(CHARTS_SCHEMA),
        cv.GenerateID(CONF_WEB_SERVER_BASE_ID): cv.use_id(
            web_server_base.WebServerBase
        ),
    }
).extend(cv.COMPONENT_SCHEMA)


async def create_cards(config: dict, parent: MockObj):
    for card in config.get(CONF_CARDS, []):
        new_card = cg.new_Pvariable(
            card[CONF_ID],
            parent,
            card[CONF_TYPE],
            card[CONF_NAME],
            card[CONF_UNIT_OF_MEASUREMENT] if CONF_UNIT_OF_MEASUREMENT in card else "",
            card[CONF_MIN_VALUE] if CONF_MIN_VALUE in card else 0,
            card[CONF_MAX_VALUE] if CONF_MAX_VALUE in card else 0,
        )

        if CONF_DEFAULT_VALUE in card:
            cg.add(new_card.update(card[CONF_DEFAULT_VALUE]))

        if CONF_LAMBDA in card:
            lambda_ = await cg.process_lambda(card[CONF_LAMBDA], [(int, "value")], return_type=cg.void)
            cg.add(new_card.attachCallback(lambda_))


def create_charts(config: dict, parent: MockObj):
    for chart in config.get(CONF_CHARTS, []):
        new_chart = cg.new_Pvariable(
            chart[CONF_ID],
            parent,
            chart[CONF_TYPE],
            chart[CONF_NAME],
        )


@coroutine_with_priority(0.0)
async def to_code(config):
    server = await cg.get_variable(config[CONF_WEB_SERVER_BASE_ID])
    cg.add(server.set_port(config[CONF_PORT]))
    cg.add_define("WEBSERVER_PORT", config[CONF_PORT])

    dash = cg.new_Pvariable(config[CONF_ID], server)
    await cg.register_component(dash, config)

    if CONF_AUTH in config:
        auth = config[CONF_AUTH]
        cg.add(dash.setAuthentication(auth[CONF_USERNAME], auth[CONF_PASSWORD]))

    if CONF_STATISTICS in config:
        cg.add(dash.displayStatistics(config[CONF_STATISTICS]))

    for tab in config.get(CONF_TABS, []):
        new_tab = cg.new_Pvariable(
            tab[CONF_ID],
            dash,
            tab[CONF_NAME],
            tab[CONF_NAVIGATION_NAME],
            tab[CONF_HEADER] if CONF_HEADER in tab else ""
        )
        await create_cards(tab, new_tab)
        create_charts(tab, new_tab)

    await create_cards(config, dash)
    create_charts(config, dash)

