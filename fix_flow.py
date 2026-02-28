import re
import os

filepath = 'custom_components/cyd_solar_display/config_flow.py'
with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

prefix = '''        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        opt = getattr(self.config_entry, "options", {})
        data_dict = getattr(self.config_entry, "data", {})

        def get_opt(key):
            val = opt.get(key, data_dict.get(key))
            if val is None:
                import voluptuous as vol
                return vol.UNDEFINED
            return val
'''

# Replace the beginning of async_step_init
if 'def get_opt(' not in text:
    text = text.replace('        if user_input is not None:\n            return self.async_create_entry(title="", data=user_input)\n', prefix)

# Replace the entity selectors with the local_growbox syntax
# Match: vol.Optional(CONF_SOLAR_ENTITY, default=self.config_entry.options.get(CONF_SOLAR_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig(domain=["sensor", "input_number"])),
#   or selector.selector(...)
pattern = re.compile(r'vol\.Optional\(([^,]+),\s*default=self\.config_entry\.options\.get\([^)]+\)\):\s*selector\.(EntitySelector\([^\)]+\)|selector\([^\)]+\))\),')

# We'll just do a more robust string replacement for the entity definitions
for var_name in ['CONF_SOLAR_ENTITY', 'CONF_GRID_ENTITY', 'CONF_HOUSE_ENTITY', 'CONF_BATTERY_ENTITY', 'CONF_BATTERY_SOC_ENTITY',
                'CONF_YIELD_TODAY_ENTITY', 'CONF_YIELD_MONTH_ENTITY', 'CONF_YIELD_YEAR_ENTITY', 'CONF_YIELD_TOTAL_ENTITY',
                'CONF_GRID_IMPORT_ENTITY', 'CONF_GRID_EXPORT_ENTITY',
                'CONF_CUSTOM1_ENTITY', 'CONF_CUSTOM2_ENTITY', 'CONF_CUSTOM3_ENTITY', 'CONF_CUSTOM4_ENTITY',
                'CONF_CUSTOM5_ENTITY', 'CONF_CUSTOM6_ENTITY', 'CONF_CUSTOM7_ENTITY', 'CONF_CUSTOM8_ENTITY',
                'CONF_MINING1_ENTITY', 'CONF_MINING2_ENTITY', 'CONF_MINING3_ENTITY', 'CONF_MINING4_ENTITY']:
    # Replace default=self.config_entry.options.get(var_name)
    # with description={"suggested_value": get_opt(var_name)}
    old_default = f'default=self.config_entry.options.get({var_name})'
    new_desc = f'description={{"suggested_value": get_opt({var_name})}}'
    text = text.replace(old_default, new_desc)
    
text = re.sub(
    r'selector\.selector\(\{.*?\}\)',
    r'selector.EntitySelector(selector.EntitySelectorConfig(domain=["sensor", "input_number"]))',
    text
)

text = re.sub(
    r'selector\.EntitySelector\(\)',
    r'selector.EntitySelector(selector.EntitySelectorConfig(domain=["sensor", "input_number"]))',
    text
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)
