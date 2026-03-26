import re

with open('main.py', 'r') as f:
    content = f.read()

# Reemplazar .hex por función hex_color()
content = re.sub(r'(\w+)\.hex', r'hex_color(\1)', content)

with open('main.py', 'w') as f:
    f.write(content)

print("✅ Archivo corregido!")
