import re
from datetime import datetime, timedelta

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. AGRANDAR TODOS LOS TextInput height=40 a 55
content = re.sub(
    r'height=40([,\)])',
    r'height=55\1',
    content
)

# 2. AGRANDAR Labels de 25 a 35
content = re.sub(
    r"height=25([,\)])",
    r"height=35\1",
    content
)

# 3. AUMENTAR spacing de 10 a 15
content = re.sub(
    r'spacing=10',
    r'spacing=15',
    content
)

# 4. AGREGAR CÁLCULO DE % PARTOS
stats_section = """        cursor.execute('SELECT AVG(weight) FROM cattle WHERE weight IS NOT NULL')
        avg_weight = cursor.fetchone()[0]
        stats['avg_weight'] = round(avg_weight, 1) if avg_weight else 0
        
        future_30 = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(DISTINCT cattle_id) FROM vaccination_history
            WHERE next_vaccination_date BETWEEN ? AND ?
        ''', (today, future_30))
        stats['need_vaccine'] = cursor.fetchone()[0]"""

new_stats_section = """        cursor.execute('SELECT AVG(weight) FROM cattle WHERE weight IS NOT NULL')
        avg_weight = cursor.fetchone()[0]
        stats['avg_weight'] = round(avg_weight, 1) if avg_weight else 0
        
        future_30 = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(DISTINCT cattle_id) FROM vaccination_history
            WHERE next_vaccination_date BETWEEN ? AND ?
        ''', (today, future_30))
        stats['need_vaccine'] = cursor.fetchone()[0]
        
        # Calcular % de partos anuales (últimos 2 años)
        two_years_ago = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM cattle')
        total_cows = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM events WHERE event_type = ? AND event_date >= ?', ('birth', two_years_ago))
        births_2y = cursor.fetchone()[0]
        
        if total_cows > 0:
            births_per_cow = births_2y / total_cows
            stats['birth_rate_annual'] = round((births_per_cow / 2) * 100, 1)
        else:
            stats['birth_rate_annual'] = 0"""

content = content.replace(stats_section, new_stats_section)

# 5. AGREGAR TARJETA EN HomeScreen
old_home = """            self.stats_container.add_widget(self.create_stat_card('🐮', 'Total', stats.get('total_cattle', 0)))
            self.stats_container.add_widget(self.create_stat_card('🤰', 'Preñadas', stats.get('pregnant', 0)))
            self.stats_container.add_widget(self.create_stat_card('⚠️', 'Próximas', stats.get('near_birth_60', 0)))
            self.stats_container.add_widget(self.create_stat_card('🚫', 'Secar', stats.get('to_dry', 0)))
            self.stats_container.add_widget(self.create_stat_card('👶', 'Partos 30d', stats.get('recent_births', 0)))
            self.stats_container.add_widget(self.create_stat_card('📊', f'Año {datetime.now().year}', stats.get('births_this_year', 0)))"""

new_home = """            self.stats_container.add_widget(self.create_stat_card('🐮', 'Total', stats.get('total_cattle', 0)))
            self.stats_container.add_widget(self.create_stat_card('🤰', 'Preñadas', stats.get('pregnant', 0)))
            self.stats_container.add_widget(self.create_stat_card('⚠️', 'Próximas', stats.get('near_birth_60', 0)))
            self.stats_container.add_widget(self.create_stat_card('🚫', 'Secar', stats.get('to_dry', 0)))
            self.stats_container.add_widget(self.create_stat_card('👶', 'Partos 30d', stats.get('recent_births', 0)))
            self.stats_container.add_widget(self.create_stat_card('📊', f'Año {datetime.now().year}', stats.get('births_this_year', 0)))
            self.stats_container.add_widget(self.create_stat_card('📈', '% Partos/Año', f"{stats.get('birth_rate_annual', 0)}%"))
            self.stats_container.add_widget(self.create_stat_card('⚖️', 'Peso Prom', f"{stats.get('avg_weight', 0)} kg"))"""

content = content.replace(old_home, new_home)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Mejoras aplicadas:")
print("  • TextInput: height=55")
print("  • Labels: height=35")
print("  • Spacing: 15px")
print("  • Nueva tarjeta: 📈 % Partos/Año")
print("  • Reorganizada: ⚖️ Peso Promedio")
