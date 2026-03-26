#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script automático para agrandar las tarjetas y cajas
"""

import re
import sys

def fix_main_py(filename='main.py'):
    print("📖 Leyendo archivo...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ No se encontró {filename}")
        return False
    
    print("🔧 Aplicando correcciones...")
    
    # 1. Tarjetas más grandes: height=70 → height=100
    content = re.sub(
        r'(def create_stat_card.*?card = StyledCard\(.*?)height=70',
        r'\1height=100',
        content,
        flags=re.DOTALL
    )
    
    # 2. Padding más grande en tarjetas
    content = re.sub(
        r'(StyledCard\(orientation=.horizontal., size_hint_y=None, height=100,) padding=10, spacing=8',
        r'\1 padding=15, spacing=10',
        content
    )
    
    # 3. Iconos más grandes: 28sp → 36sp
    content = re.sub(
        r"(icon_label = Label\(text=icon,) font_size='28sp'",
        r"\1 font_size='36sp'",
        content
    )
    
    # 4. Título más grande: 11sp → 14sp (en create_stat_card)
    content = re.sub(
        r"(title_label = Label\(.*?font_size=)'11sp'",
        r"\1'14sp'",
        content
    )
    
    # 5. Valor más grande: 20sp → 26sp
    content = re.sub(
        r"(value_label = Label\(.*?font_size=)'20sp'",
        r"\1'26sp'",
        content
    )
    
    # 6. Subtítulo más grande: 9sp → 12sp
    content = re.sub(
        r"(sub_label = Label\(.*?font_size=)'9sp'",
        r"\1'12sp'",
        content
    )
    
    # 7. Grid de 2 columnas → 1 columna
    content = re.sub(
        r'self\.stats_container = GridLayout\(cols=2, spacing=8, size_hint_y=None, padding=5\)',
        r'self.stats_container = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)',
        content
    )
    
    # 8. Scroll más grande para estadísticas
    content = re.sub(
        r'(scroll = ScrollView\()size_hint_y=0\.5\)',
        r'\1size_hint_y=0.55)',
        content
    )
    
    print("💾 Guardando cambios...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ ¡Cambios aplicados exitosamente!")
    print("")
    print("📋 Cambios realizados:")
    print("   • Tarjetas: 70px → 100px")
    print("   • Iconos: 28sp → 36sp")
    print("   • Títulos: 11sp → 14sp")
    print("   • Valores: 20sp → 26sp")
    print("   • Subtítulos: 9sp → 12sp")
    print("   • Layout: 2 columnas → 1 columna")
    print("")
    print("🚀 Siguiente paso:")
    print("   git add main.py")
    print("   git commit -m 'UI grande: tarjetas 100px + 1 columna'")
    print("   git push origin main -f")
    
    return True

if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) > 1 else 'main.py'
    success = fix_main_py(filename)
    sys.exit(0 if success else 1)
