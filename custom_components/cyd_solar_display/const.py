"""Constants for the CYD Solar Display integration."""

DOMAIN = "cyd_solar_display"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_UPDATE_INTERVAL = "update_interval"

# Entity Config Keys
CONF_SOLAR_ENTITY = "solar_entity"
CONF_GRID_ENTITY = "grid_entity"
CONF_HOUSE_ENTITY = "house_entity"
CONF_BATTERY_ENTITY = "battery_entity"
CONF_BATTERY_SOC_ENTITY = "battery_soc_entity"

# Page 1
CONF_ENABLE_PAGE1 = "enable_page1"

# Page 2 Entities
CONF_ENABLE_PAGE2 = "enable_page2"
CONF_YIELD_TODAY_ENTITY = "yield_today_entity"
CONF_YIELD_MONTH_ENTITY = "yield_month_entity"
CONF_YIELD_YEAR_ENTITY = "yield_year_entity"
CONF_YIELD_TOTAL_ENTITY = "yield_total_entity"
CONF_GRID_IMPORT_ENTITY = "grid_import_entity"
CONF_GRID_EXPORT_ENTITY = "grid_export_entity"

# Page 3 (Custom OpenKairo Sensors)
CONF_ENABLE_PAGE3 = "enable_page3"
CONF_CUSTOM1_NAME = "custom1_name"
CONF_CUSTOM1_ENTITY = "custom1_entity"
CONF_CUSTOM2_NAME = "custom2_name"
CONF_CUSTOM2_ENTITY = "custom2_entity"
CONF_CUSTOM3_NAME = "custom3_name"
CONF_CUSTOM3_ENTITY = "custom3_entity"
CONF_CUSTOM4_NAME = "custom4_name"
CONF_CUSTOM4_ENTITY = "custom4_entity"

# Page 4 (More Custom Sensors)
CONF_ENABLE_PAGE4 = "enable_page4"
CONF_CUSTOM5_NAME = "custom5_name"
CONF_CUSTOM5_ENTITY = "custom5_entity"
CONF_CUSTOM6_NAME = "custom6_name"
CONF_CUSTOM6_ENTITY = "custom6_entity"
CONF_CUSTOM7_NAME = "custom7_name"
CONF_CUSTOM7_ENTITY = "custom7_entity"
CONF_CUSTOM8_NAME = "custom8_name"
CONF_CUSTOM8_ENTITY = "custom8_entity"

# Page 5 (Mining Sensors)
CONF_ENABLE_PAGE5 = "enable_page5"
CONF_MINING1_NAME = "mining1_name"
CONF_MINING1_ENTITY = "mining1_entity"
CONF_MINING2_NAME = "mining2_name"
CONF_MINING2_ENTITY = "mining2_entity"
CONF_MINING3_NAME = "mining3_name"
CONF_MINING3_ENTITY = "mining3_entity"
CONF_MINING4_NAME = "mining4_name"
CONF_MINING4_ENTITY = "mining4_entity"

# Page 6 (Custom Sensors Vol 3)
CONF_ENABLE_PAGE6 = "enable_page6"
CONF_CUSTOM9_NAME = "custom9_name"
CONF_CUSTOM9_ENTITY = "custom9_entity"
CONF_CUSTOM10_NAME = "custom10_name"
CONF_CUSTOM10_ENTITY = "custom10_entity"
CONF_CUSTOM11_NAME = "custom11_name"
CONF_CUSTOM11_ENTITY = "custom11_entity"
CONF_CUSTOM12_NAME = "custom12_name"
CONF_CUSTOM12_ENTITY = "custom12_entity"

# Page 7 (Custom Sensors Vol 4)
CONF_ENABLE_PAGE7 = "enable_page7"
CONF_CUSTOM13_NAME = "custom13_name"
CONF_CUSTOM13_ENTITY = "custom13_entity"
CONF_CUSTOM14_NAME = "custom14_name"
CONF_CUSTOM14_ENTITY = "custom14_entity"
CONF_CUSTOM15_NAME = "custom15_name"
CONF_CUSTOM15_ENTITY = "custom15_entity"
CONF_CUSTOM16_NAME = "custom16_name"
CONF_CUSTOM16_ENTITY = "custom16_entity"

# Page 8 (Custom Sensors Vol 5)
CONF_ENABLE_PAGE8 = "enable_page8"
CONF_CUSTOM17_NAME = "custom17_name"
CONF_CUSTOM17_ENTITY = "custom17_entity"
CONF_CUSTOM18_NAME = "custom18_name"
CONF_CUSTOM18_ENTITY = "custom18_entity"
CONF_CUSTOM19_NAME = "custom19_name"
CONF_CUSTOM19_ENTITY = "custom19_entity"
CONF_CUSTOM20_NAME = "custom20_name"
CONF_CUSTOM20_ENTITY = "custom20_entity"

# Page 9 (Custom Sensors Vol 6)
CONF_ENABLE_PAGE9 = "enable_page9"
CONF_CUSTOM21_NAME = "custom21_name"
CONF_CUSTOM21_ENTITY = "custom21_entity"
CONF_CUSTOM22_NAME = "custom22_name"
CONF_CUSTOM22_ENTITY = "custom22_entity"
CONF_CUSTOM23_NAME = "custom23_name"
CONF_CUSTOM23_ENTITY = "custom23_entity"
CONF_CUSTOM24_NAME = "custom24_name"
CONF_CUSTOM24_ENTITY = "custom24_entity"

# Meta
CONF_SHOW_KW = "show_kw"
CONF_AUTO_PAGE_SWITCH = "auto_page_switch"
CONF_PAGE_INTERVAL = "page_interval"
CONF_PAGE_SWITCH_MODE = "page_switch_mode"   # "auto" | "touch" | "both"
CONF_PAGE_ROTATION_SOURCE = "page_rotation_source" # "ha" | "display"
CONF_THEME_COLOR = "theme_color"
CONF_BROADCAST_MODE = "broadcast_mode"

PAGE_SWITCH_AUTO  = "auto"
PAGE_SWITCH_TOUCH = "touch"
PAGE_SWITCH_BOTH  = "both"

DEFAULT_PORT = 80
DEFAULT_UPDATE_INTERVAL = 5
DEFAULT_PAGE_INTERVAL = 10
DEFAULT_THEME_COLOR = "#fdd835"  # Home Assistant Solar Yellow
