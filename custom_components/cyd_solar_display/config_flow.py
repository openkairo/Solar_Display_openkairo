from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    DEFAULT_PORT,
    CONF_SOLAR_ENTITY,
    CONF_GRID_ENTITY,
    CONF_HOUSE_ENTITY,
    CONF_BATTERY_ENTITY,
    CONF_BATTERY_SOC_ENTITY,
    CONF_ENABLE_PAGE1,
    CONF_ENABLE_PAGE2,
    CONF_YIELD_TODAY_ENTITY,
    CONF_YIELD_MONTH_ENTITY,
    CONF_YIELD_YEAR_ENTITY,
    CONF_YIELD_TOTAL_ENTITY,
    CONF_GRID_IMPORT_ENTITY,
    CONF_GRID_EXPORT_ENTITY,
    CONF_ENABLE_PAGE3,
    CONF_CUSTOM1_NAME,
    CONF_CUSTOM1_ENTITY,
    CONF_CUSTOM2_NAME,
    CONF_CUSTOM2_ENTITY,
    CONF_CUSTOM3_NAME,
    CONF_CUSTOM3_ENTITY,
    CONF_CUSTOM4_NAME,
    CONF_CUSTOM4_ENTITY,
    CONF_ENABLE_PAGE4,
    CONF_CUSTOM5_NAME,
    CONF_CUSTOM5_ENTITY,
    CONF_CUSTOM6_NAME,
    CONF_CUSTOM6_ENTITY,
    CONF_CUSTOM7_NAME,
    CONF_CUSTOM7_ENTITY,
    CONF_CUSTOM7_ENTITY,
    CONF_CUSTOM8_NAME,
    CONF_CUSTOM8_ENTITY,
    CONF_ENABLE_PAGE5,
    CONF_MINING1_NAME,
    CONF_MINING1_ENTITY,
    CONF_MINING2_NAME,
    CONF_MINING2_ENTITY,
    CONF_MINING3_NAME,
    CONF_MINING3_ENTITY,
    CONF_MINING4_NAME,
    CONF_MINING4_ENTITY,
    CONF_ENABLE_PAGE6,
    CONF_CUSTOM9_NAME,
    CONF_CUSTOM9_ENTITY,
    CONF_CUSTOM10_NAME,
    CONF_CUSTOM10_ENTITY,
    CONF_CUSTOM11_NAME,
    CONF_CUSTOM11_ENTITY,
    CONF_CUSTOM12_NAME,
    CONF_CUSTOM12_ENTITY,
    CONF_ENABLE_PAGE7,
    CONF_CUSTOM13_NAME,
    CONF_CUSTOM13_ENTITY,
    CONF_CUSTOM14_NAME,
    CONF_CUSTOM14_ENTITY,
    CONF_CUSTOM15_NAME,
    CONF_CUSTOM15_ENTITY,
    CONF_CUSTOM16_NAME,
    CONF_CUSTOM16_ENTITY,
    CONF_ENABLE_PAGE8,
    CONF_CUSTOM17_NAME,
    CONF_CUSTOM17_ENTITY,
    CONF_CUSTOM18_NAME,
    CONF_CUSTOM18_ENTITY,
    CONF_CUSTOM19_NAME,
    CONF_CUSTOM19_ENTITY,
    CONF_CUSTOM20_NAME,
    CONF_CUSTOM20_ENTITY,
    CONF_ENABLE_PAGE9,
    CONF_CUSTOM21_NAME,
    CONF_CUSTOM21_ENTITY,
    CONF_CUSTOM22_NAME,
    CONF_CUSTOM22_ENTITY,
    CONF_CUSTOM23_NAME,
    CONF_CUSTOM23_ENTITY,
    CONF_CUSTOM24_NAME,
    CONF_CUSTOM24_ENTITY,
    CONF_SHOW_KW,
    CONF_AUTO_PAGE_SWITCH,
    CONF_PAGE_INTERVAL,
    CONF_PAGE_SWITCH_MODE,
    CONF_PAGE_ROTATION_SOURCE,
    CONF_BROADCAST_MODE,
    PAGE_SWITCH_AUTO,
    PAGE_SWITCH_TOUCH,
    PAGE_SWITCH_BOTH,
)

# Shorthand for entity selector (sensor + input_number domains)
def _entity_selector():
    return selector.EntitySelector(
        selector.EntitySelectorConfig(domain=["sensor", "input_number"])
    )

class CYDSolarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CYD Solar Display."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Basic validation
            if not user_input[CONF_HOST]:
                errors["base"] = "invalid_host"
            else:
                return self.async_create_entry(title=f"CYD Solar ({user_input[CONF_HOST]})", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_BROADCAST_MODE, default=False): bool,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CYDSolarOptionsFlow(config_entry)


class CYDSolarOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Erhalte versteckte System-Tasten (wie die letzte Seite)
            old_opt = dict(self.config_entry.options)
            for k in ["last_page", "_last_sync"]:
                if k in old_opt:
                    user_input[k] = old_opt[k]
                    
            return self.async_create_entry(title="", data=user_input)

        opt = getattr(self.config_entry, "options", {})
        data_dict = getattr(self.config_entry, "data", {})

        def get_opt(key):
            val = opt.get(key, data_dict.get(key))
            if val is None:
                import voluptuous as vol
                return vol.UNDEFINED
            return val

        opt = self.config_entry.options
        data = self.config_entry.data

        def get_val(key):
            val = opt.get(key, data.get(key))
            if val is None:
                return vol.UNDEFINED
            return val

        # Entity selection schema – using description/suggested_value like local_growbox
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                # Core Entities
                vol.Optional(CONF_ENABLE_PAGE1, default=opt.get(CONF_ENABLE_PAGE1, True)): bool,
                vol.Optional(CONF_SOLAR_ENTITY, description={"suggested_value": get_val(CONF_SOLAR_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_GRID_ENTITY, description={"suggested_value": get_val(CONF_GRID_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_HOUSE_ENTITY, description={"suggested_value": get_val(CONF_HOUSE_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_BATTERY_ENTITY, description={"suggested_value": get_val(CONF_BATTERY_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_BATTERY_SOC_ENTITY, description={"suggested_value": get_val(CONF_BATTERY_SOC_ENTITY)}): _entity_selector(),

                # Page 2
                vol.Optional(CONF_ENABLE_PAGE2, default=opt.get(CONF_ENABLE_PAGE2, True)): bool,
                vol.Optional(CONF_YIELD_TODAY_ENTITY, description={"suggested_value": get_val(CONF_YIELD_TODAY_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_YIELD_MONTH_ENTITY, description={"suggested_value": get_val(CONF_YIELD_MONTH_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_YIELD_YEAR_ENTITY, description={"suggested_value": get_val(CONF_YIELD_YEAR_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_YIELD_TOTAL_ENTITY, description={"suggested_value": get_val(CONF_YIELD_TOTAL_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_GRID_IMPORT_ENTITY, description={"suggested_value": get_val(CONF_GRID_IMPORT_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_GRID_EXPORT_ENTITY, description={"suggested_value": get_val(CONF_GRID_EXPORT_ENTITY)}): _entity_selector(),

                # Page 3 (Custom Sensors)
                vol.Optional(CONF_ENABLE_PAGE3, default=opt.get(CONF_ENABLE_PAGE3, True)): bool,
                vol.Optional(CONF_CUSTOM1_NAME, default=opt.get(CONF_CUSTOM1_NAME, "Custom 1")): str,
                vol.Optional(CONF_CUSTOM1_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM1_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM2_NAME, default=opt.get(CONF_CUSTOM2_NAME, "Custom 2")): str,
                vol.Optional(CONF_CUSTOM2_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM2_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM3_NAME, default=opt.get(CONF_CUSTOM3_NAME, "Custom 3")): str,
                vol.Optional(CONF_CUSTOM3_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM3_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM4_NAME, default=opt.get(CONF_CUSTOM4_NAME, "Custom 4")): str,
                vol.Optional(CONF_CUSTOM4_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM4_ENTITY)}): _entity_selector(),

                # Page 4 (More Custom Sensors)
                vol.Optional(CONF_ENABLE_PAGE4, default=opt.get(CONF_ENABLE_PAGE4, True)): bool,
                vol.Optional(CONF_CUSTOM5_NAME, default=opt.get(CONF_CUSTOM5_NAME, "Custom 5")): str,
                vol.Optional(CONF_CUSTOM5_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM5_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM6_NAME, default=opt.get(CONF_CUSTOM6_NAME, "Custom 6")): str,
                vol.Optional(CONF_CUSTOM6_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM6_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM7_NAME, default=opt.get(CONF_CUSTOM7_NAME, "Custom 7")): str,
                vol.Optional(CONF_CUSTOM7_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM7_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM8_NAME, default=opt.get(CONF_CUSTOM8_NAME, "Custom 8")): str,
                vol.Optional(CONF_CUSTOM8_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM8_ENTITY)}): _entity_selector(),

                # Page 5 (Mining Sensors)
                vol.Optional(CONF_ENABLE_PAGE5, default=opt.get(CONF_ENABLE_PAGE5, True)): bool,
                vol.Optional(CONF_MINING1_NAME, default=opt.get(CONF_MINING1_NAME, "Mining 1")): str,
                vol.Optional(CONF_MINING1_ENTITY, description={"suggested_value": get_val(CONF_MINING1_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_MINING2_NAME, default=opt.get(CONF_MINING2_NAME, "Mining 2")): str,
                vol.Optional(CONF_MINING2_ENTITY, description={"suggested_value": get_val(CONF_MINING2_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_MINING3_NAME, default=opt.get(CONF_MINING3_NAME, "Mining 3")): str,
                vol.Optional(CONF_MINING3_ENTITY, description={"suggested_value": get_val(CONF_MINING3_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_MINING4_NAME, default=opt.get(CONF_MINING4_NAME, "Mining 4")): str,
                vol.Optional(CONF_MINING4_ENTITY, description={"suggested_value": get_val(CONF_MINING4_ENTITY)}): _entity_selector(),

                # Page 6 (Custom Sensors Vol 3)
                vol.Optional(CONF_ENABLE_PAGE6, default=opt.get(CONF_ENABLE_PAGE6, False)): bool,
                vol.Optional(CONF_CUSTOM9_NAME, default=opt.get(CONF_CUSTOM9_NAME, "Custom 9")): str,
                vol.Optional(CONF_CUSTOM9_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM9_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM10_NAME, default=opt.get(CONF_CUSTOM10_NAME, "Custom 10")): str,
                vol.Optional(CONF_CUSTOM10_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM10_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM11_NAME, default=opt.get(CONF_CUSTOM11_NAME, "Custom 11")): str,
                vol.Optional(CONF_CUSTOM11_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM11_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM12_NAME, default=opt.get(CONF_CUSTOM12_NAME, "Custom 12")): str,
                vol.Optional(CONF_CUSTOM12_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM12_ENTITY)}): _entity_selector(),

                # Page 7 (Custom Sensors Vol 4)
                vol.Optional(CONF_ENABLE_PAGE7, default=opt.get(CONF_ENABLE_PAGE7, False)): bool,
                vol.Optional(CONF_CUSTOM13_NAME, default=opt.get(CONF_CUSTOM13_NAME, "Custom 13")): str,
                vol.Optional(CONF_CUSTOM13_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM13_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM14_NAME, default=opt.get(CONF_CUSTOM14_NAME, "Custom 14")): str,
                vol.Optional(CONF_CUSTOM14_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM14_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM15_NAME, default=opt.get(CONF_CUSTOM15_NAME, "Custom 15")): str,
                vol.Optional(CONF_CUSTOM15_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM15_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM16_NAME, default=opt.get(CONF_CUSTOM16_NAME, "Custom 16")): str,
                vol.Optional(CONF_CUSTOM16_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM16_ENTITY)}): _entity_selector(),

                # Page 8 (Custom Sensors Vol 5)
                vol.Optional(CONF_ENABLE_PAGE8, default=opt.get(CONF_ENABLE_PAGE8, False)): bool,
                vol.Optional(CONF_CUSTOM17_NAME, default=opt.get(CONF_CUSTOM17_NAME, "Custom 17")): str,
                vol.Optional(CONF_CUSTOM17_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM17_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM18_NAME, default=opt.get(CONF_CUSTOM18_NAME, "Custom 18")): str,
                vol.Optional(CONF_CUSTOM18_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM18_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM19_NAME, default=opt.get(CONF_CUSTOM19_NAME, "Custom 19")): str,
                vol.Optional(CONF_CUSTOM19_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM19_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM20_NAME, default=opt.get(CONF_CUSTOM20_NAME, "Custom 20")): str,
                vol.Optional(CONF_CUSTOM20_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM20_ENTITY)}): _entity_selector(),

                # Page 9 (Custom Sensors Vol 6)
                vol.Optional(CONF_ENABLE_PAGE9, default=opt.get(CONF_ENABLE_PAGE9, False)): bool,
                vol.Optional(CONF_CUSTOM21_NAME, default=opt.get(CONF_CUSTOM21_NAME, "Custom 21")): str,
                vol.Optional(CONF_CUSTOM21_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM21_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM22_NAME, default=opt.get(CONF_CUSTOM22_NAME, "Custom 22")): str,
                vol.Optional(CONF_CUSTOM22_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM22_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM23_NAME, default=opt.get(CONF_CUSTOM23_NAME, "Custom 23")): str,
                vol.Optional(CONF_CUSTOM23_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM23_ENTITY)}): _entity_selector(),
                vol.Optional(CONF_CUSTOM24_NAME, default=opt.get(CONF_CUSTOM24_NAME, "Custom 24")): str,
                vol.Optional(CONF_CUSTOM24_ENTITY, description={"suggested_value": get_val(CONF_CUSTOM24_ENTITY)}): _entity_selector(),

                # Settings
                vol.Optional("antigravity_test", default=False): bool,
                vol.Optional(CONF_SHOW_KW, default=opt.get(CONF_SHOW_KW, False)): bool,
                vol.Optional(CONF_BROADCAST_MODE, default=opt.get(CONF_BROADCAST_MODE, False)): bool,
                vol.Optional("update_interval", default=opt.get("update_interval", 5)): int,
                vol.Optional(CONF_PAGE_INTERVAL, default=opt.get(CONF_PAGE_INTERVAL, 10)): int,
                vol.Optional(CONF_PAGE_SWITCH_MODE, default=opt.get(CONF_PAGE_SWITCH_MODE, PAGE_SWITCH_AUTO)):
                    selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                {"value": PAGE_SWITCH_AUTO,  "label": "🔄 Automatisch (HA steuert Seitenwechsel)"},
                                {"value": PAGE_SWITCH_TOUCH, "label": "👆 Nur Touch (manuell per Display-Tippen)"},
                                {"value": PAGE_SWITCH_BOTH,  "label": "🔄👆 Beides (Auto + Touch-Override)"},
                            ],
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                vol.Optional(CONF_PAGE_ROTATION_SOURCE, default=opt.get(CONF_PAGE_ROTATION_SOURCE, "ha")):
                    selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                {"value": "ha", "label": "🏠 Home Assistant (Zentral gesteuert)"},
                                {"value": "display", "label": "📱 Display lokal (Jedes Display rotiert selbst)"},
                            ],
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
            })
        )
