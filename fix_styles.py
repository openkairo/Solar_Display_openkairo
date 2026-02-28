import re

path = 'custom_components/cyd_solar_display/www/cyd-preview.js'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Fix spacing around hyphens in alphanumeric names (running twice for overlapping matches: a-b-c)
c = re.sub(r'([a-zA-Z0-9]+) - ([a-zA-Z0-9]+)', r'\1-\2', c)
c = re.sub(r'([a-zA-Z0-9]+) - ([a-zA-Z0-9]+)', r'\1-\2', c)

# Fix percent spacing
c = re.sub(r'([0-9]+) %', r'\1%', c)

# Fix HTML
c = c.replace('< div ', '<div ')
c = c.replace('</div >', '</div>')

# Fix pseudo-classes
c = c.replace(': focus', ':focus')

# Fix attributes selectors
c = c.replace('[type = "text"]', '[type="text"]')
c = c.replace('[type = "number"]', '[type="number"]')

# Fix specifics
c = c.replace('ease -in -out', 'ease-in-out')
c = c.replace('background: conic - gradient', 'background: conic-gradient')
c = c.replace('stat - item', 'stat-item')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print('Success')
