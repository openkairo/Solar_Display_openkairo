import os

files = [
    r'README.md',
    r'webflasher\manifest.json',
    r'webflasher\index.html',
    r'cyd_solar_display.yaml',
    r'custom_components\cyd_solar_display\www\cyd-preview.js',
    r'custom_components\cyd_solar_display\update.py',
    r'custom_components\cyd_solar_display\coordinator.py'
]

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        content = content.replace('1.2.6', '1.2.7')
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated {f}")
    else:
        print(f"File not found: {f}")
