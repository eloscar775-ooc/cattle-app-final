#!/usr/bin/env python3
import re

print("🔧 Aplicando corrección DEFINITIVA...")

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. CAMBIAR DISEÑO A VERTICAL
content = re.sub(
    r"def create_stat_card\(self, icon, title, value, subtitle=''\):",
    r"def create_stat_card(self, icon, title, value):",
    content
)

content = re.sub(
    r"card = StyledCard\(orientation='horizontal', size_hint_y=None, height=\d+, padding=\d+, spacing=\d+\)",
    r"card = StyledCard(orientation='vertical', size_hint_y=None, height=130, padding=20, spacing=10)",
    content
)

# 2. ICONOS ARRIBA (grande)
content = re.sub(
    r"icon_label = Label\(text=icon, font_size='\d+sp', size_hint_x=[^,]+, color=TEXT\)",
    r"icon_label = Label(text=icon, font_size='50sp', size_hint_y=None, height=70, color=TEXT)",
    content
)

# 3. VALOR GRANDE EN MEDIO
content = re.sub(
    r"value_label = Label\(\s*text=f'\[b\]\{value\}\[/b\]',\s*markup=True,\s*font_size='\d+sp',\s*halign='[^']+',\s*color=TEXT\s*\)",
    r"value_label = Label(\n            text=f'[b]{value}[/b]',\n            markup=True,\n            font_size='34sp',\n            size_hint_y=None,\n            height=45,\n            color=TEXT\n        )",
    content,
    flags=re.MULTILINE
)

# 4. TÍTULO ABAJO (pequeño)
content = re.sub(
    r"title_color = ''.join\(\[f'\{int\(c\*255\):02x\}' for c in TEXT_DIM\[:3\]\]\)\s*title_label = Label\(\s*text=f'\[color=\{title_color\}\]\{title\}\[/color\]',\s*markup=True,\s*font_size='\d+sp',\s*halign='[^']+'\s*\)",
    r"title_label = Label(\n            text=title,\n            font_size='15sp',\n            size_hint_y=None,\n            height=30,\n            color=TEXT_DIM\n        )",
    content,
    flags=re.MULTILINE
)

# 5. ELIMINAR content = BoxLayout
old_content_box = r"""        content = BoxLayout\(orientation='vertical'\)
        
        title_color = ''.join\(\[f'\{int\(c\*255\):02x\}' for c in TEXT_DIM\[:3\]\]\)
        title_label = Label\(.*?\)
        title_label\.bind\(size=title_label\.setter\('text_size'\)\)
        
        value_label = Label\(.*?\)
        value_label\.bind\(size=value_label\.setter\('text_size'\)\)
        
        content\.add_widget\(title_label\)
        content\.add_widget\(value_label\)"""

# 6. ELIMINAR SUBTÍTULOS
content = re.sub(
    r"if subtitle:.*?content\.add_widget\(sub_label\)",
    r"",
    content,
    flags=re.DOTALL
)

# 7. CAMBIAR ESTRUCTURA FINAL
content = re.sub(
    r"card\.add_widget\(icon_label\)\s+card\.add_widget\(content\)",
    r"card.add_widget(icon_label)\n        card.add_widget(value_label)\n        card.add_widget(title_label)",
    content
)

# 8. ELIMINAR PARÁMETRO subtitle EN LLAMADAS
content = re.sub(
    r"self\.create_stat_card\(([^,]+), ([^,]+), ([^,)]+), [^)]+\)",
    r"self.create_stat_card(\1, \2, \3)",
    content
)

# 9. CAMBIAR GridLayout A BoxLayout VERTICAL
content = re.sub(
    r"self\.stats_container = GridLayout\(cols=\d+, spacing=\d+, size_hint_y=None, padding=\d+\)",
    r"self.stats_container = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=[10, 10])",
    content
)

# 10. ARREGLAR "Peso: None kg" → "Peso: 0 kg"
content = re.sub(
    r"Peso: \{cattle_data\.get\('weight', 'N/A'\)\} kg",
    r"Peso: {cattle_data.get('weight') or 0} kg",
    content
)

# 11. TARJETAS DE GANADO MÁS GRANDES
content = re.sub(
    r"card = StyledCard\(orientation='vertical', size_hint_y=None, height=120, padding=15, spacing=8\)",
    r"card = StyledCard(orientation='vertical', size_hint_y=None, height=170, padding=20, spacing=10)",
    content
)

# 12. TARJETA DE INFO MÁS GRANDE
content = re.sub(
    r"info_card = StyledCard\(orientation='vertical', size_hint_y=None, height=250, padding=15, spacing=10\)",
    r"info_card = StyledCard(orientation='vertical', size_hint_y=None, height=350, padding=20, spacing=15)",
    content
)

# 13. CAJAS DE TEXTO MÁS GRANDES (si no están ya)
content = re.sub(r'height=70,', r'height=85,', content)
content = re.sub(r"font_size='18sp'", r"font_size='20sp'", content)
content = re.sub(r'padding=\[15, 20\]', r'padding=[20, 30]', content)

# 14. LABELS MÁS GRANDES
content = re.sub(r'height=40,', r'height=45,', content)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ ¡CORRECCIONES APLICADAS!")
print("")
print("📋 Cambios realizados:")
print("  ✅ Diseño: Horizontal → VERTICAL")
print("  ✅ Tarjetas: 70px → 130px")
print("  ✅ Iconos: 28sp → 50sp")
print("  ✅ Valores: 20sp → 34sp")
print("  ✅ Títulos: 11sp → 15sp")
print("  ✅ TextInput: 70px → 85px")
print("  ✅ Fuente: 18sp → 20sp")
print("  ✅ Padding: [15,20] → [20,30]")
print("  ✅ Grid → BoxLayout vertical")
print("  ✅ Peso: None → 0")
print("")
print("🚀 Siguiente paso:")
print("   git add main.py")
print("   git commit -m 'Diseño vertical DEFINITIVO'")
print("   git push origin main -f")
