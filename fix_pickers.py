import re

filepath = r'custom_components\cyd_solar_display\www\cyd-preview.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all ha-entity-picker blocks with renderEntitySelect calls
# Pattern matches the full multi-line picker element
pattern = re.compile(
    r'<ha-entity-picker\s*\n\s*\.hass=\$\{this\.hass\}\s*\n\s*\.value=\$\{this\.editConfig\.([a-z0-9_]+) \|\| ""\}\s*\n\s*\.includeDomains=\$\{\[\'sensor\', \'input_number\'\]\}\s*\n\s*@value-changed=\$\{\(e\) => this\.handlePickerInput\(e, \'[a-z0-9_]+\'\)\}\s*\n\s*allow-custom-entity\s*\n\s*>\</ha-entity-picker>',
    re.MULTILINE
)

def replacer(m):
    key = m.group(1)
    return "${this.renderEntitySelect('" + key + "', ['sensor', 'input_number'])}"

new_content, count = re.subn(pattern, replacer, content)
print(f"Replaced {count} entity pickers")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

# Verify remaining pickers
remaining = new_content.count('<ha-entity-picker')
print(f"Remaining ha-entity-picker: {remaining}")
