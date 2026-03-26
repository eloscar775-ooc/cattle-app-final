#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐄 CATTLE MILK PRO AI - Sistema Completo de Gestión Lechera
Versión: 1.0 DEFINITIVA COMPLETA
Todas las funciones + IA avanzada
"""

import os
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import get_color_from_hex, platform
import sqlite3

BG = get_color_from_hex('#0D111A')
S1 = get_color_from_hex('#161B22')
S2 = get_color_from_hex('#1C2333')
BD = get_color_from_hex('#30363D')
GOLD = get_color_from_hex('#D4A017')
GREEN = get_color_from_hex('#3FB950')
RED = get_color_from_hex('#F85149')
BLUE = get_color_from_hex('#58A6FF')
YELLOW = get_color_from_hex('#F0C330')
TEXT = get_color_from_hex('#E6EDF3')
MUTED = get_color_from_hex('#8B949E')
INP = get_color_from_hex('#21262D')

Window.clearcolor = BG

class ModernButton(Button):
    def __init__(self, bg_color=GOLD, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (0, 0, 0, 1) if bg_color in [GOLD, GREEN, YELLOW] else TEXT
        self.bold = True
        self.bg_color = bg_color
        with self.canvas.before:
            self.rect_color = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ModernCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*S1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class Database:
    def __init__(self):
        try:
            if platform == 'android':
                from android.storage import app_storage_path
                storage_path = app_storage_path()
                self.db_path = os.path.join(storage_path, 'cattle_milk_ai.db')
            else:
                self.db_path = os.path.expanduser('~/cattle_milk_ai.db')
        except:
            self.db_path = os.path.expanduser('~/cattle_milk_ai.db')
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute("""CREATE TABLE IF NOT EXISTS cattle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_number TEXT UNIQUE NOT NULL,
            name TEXT,
            birth_date TEXT,
            race TEXT DEFAULT 'Holstein',
            num_partos INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'seca',
            is_pregnant INTEGER DEFAULT 0,
            pregnancy_date TEXT,
            expected_birth_date TEXT,
            last_birth_date TEXT,
            dias_lactancia INTEGER DEFAULT 0,
            pico_produccion REAL DEFAULT 0,
            last_heat_date TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        
        c.execute("""CREATE TABLE IF NOT EXISTS milk_production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cattle_id INTEGER,
            fecha TEXT NOT NULL,
            litros_manana REAL DEFAULT 0,
            litros_tarde REAL DEFAULT 0,
            litros_total REAL DEFAULT 0,
            FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
        )""")
        
        c.execute("""CREATE TABLE IF NOT EXISTS feeding (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            kg_forraje REAL DEFAULT 0,
            kg_concentrado REAL DEFAULT 0,
            horas_pastoreo REAL DEFAULT 0,
            costo_forraje REAL DEFAULT 0,
            costo_concentrado REAL DEFAULT 0,
            costo_total REAL DEFAULT 0
        )""")
        
        c.execute("""CREATE TABLE IF NOT EXISTS heat_control (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cattle_id INTEGER,
            fecha_celo TEXT NOT NULL,
            observaciones TEXT,
            FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
        )""")
        
        c.execute("""CREATE TABLE IF NOT EXISTS insemination (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cattle_id INTEGER,
            fecha TEXT NOT NULL,
            toro_usado TEXT,
            num_servicio INTEGER DEFAULT 1,
            resultado TEXT DEFAULT 'pendiente',
            FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
        )""")
        
        c.execute("""CREATE TABLE IF NOT EXISTS vaccination (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cattle_id INTEGER,
            vaccine_name TEXT,
            fecha TEXT,
            proxima_fecha TEXT,
            costo REAL DEFAULT 0,
            FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
        )""")
        
        c.execute("""CREATE TABLE IF NOT EXISTS health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cattle_id INTEGER,
            fecha TEXT,
            tipo TEXT,
            tratamiento TEXT,
            medicamento TEXT,
            costo REAL DEFAULT 0,
            FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
        )""")
        
        c.execute("""CREATE TABLE IF NOT EXISTS births (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cattle_id INTEGER,
            fecha_parto TEXT,
            sexo_cria TEXT,
            peso_becerro REAL,
            problemas TEXT,
            FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
        )""")
        
        conn.commit()
        conn.close()
    
    def add_cattle(self, data):
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute("""INSERT INTO cattle (tag_number, name, birth_date, race, estado, num_partos)
                VALUES (?, ?, ?, ?, ?, ?)""", (
                data.get('tag_number'), data.get('name', ''), data.get('birth_date'),
                data.get('race', 'Holstein'), data.get('estado', 'seca'), data.get('num_partos', 0)
            ))
            conn.commit()
            return c.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_all_cattle(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM cattle ORDER BY tag_number')
        cols = [d[0] for d in c.description]
        result = [dict(zip(cols, row)) for row in c.fetchall()]
        conn.close()
        return result
    
    def get_cattle_by_id(self, cid):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM cattle WHERE id = ?', (cid,))
        cols = [d[0] for d in c.description]
        row = c.fetchone()
        conn.close()
        return dict(zip(cols, row)) if row else None
    
    def update_cattle(self, cid, data):
        conn = self.get_connection()
        c = conn.cursor()
        fields = []
        values = []
        for k, v in data.items():
            if k != 'id':
                fields.append(f"{k} = ?")
                values.append(v)
        values.append(cid)
        c.execute(f"UPDATE cattle SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        conn.close()
    
    def delete_cattle(self, cid):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM cattle WHERE id = ?', (cid,))
        conn.commit()
        conn.close()
    
    def add_milk_production(self, cid, fecha, lm, lt):
        conn = self.get_connection()
        c = conn.cursor()
        total = lm + lt
        c.execute("""INSERT INTO milk_production (cattle_id, fecha, litros_manana, litros_tarde, litros_total)
            VALUES (?, ?, ?, ?, ?)""", (cid, fecha, lm, lt, total))
        c.execute('SELECT pico_produccion FROM cattle WHERE id = ?', (cid,))
        pico = c.fetchone()[0] or 0
        if total > pico:
            c.execute('UPDATE cattle SET pico_produccion = ? WHERE id = ?', (total, cid))
        c.execute('UPDATE cattle SET dias_lactancia = dias_lactancia + 1 WHERE id = ?', (cid,))
        conn.commit()
        conn.close()
    
    def get_milk_stats(self, cid):
        conn = self.get_connection()
        c = conn.cursor()
        f7 = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        c.execute('SELECT AVG(litros_total), SUM(litros_total) FROM milk_production WHERE cattle_id = ? AND fecha >= ?', (cid, f7))
        r = c.fetchone()
        a7 = round(r[0] if r[0] else 0, 1)
        t7 = round(r[1] if r[1] else 0, 1)
        f30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        c.execute('SELECT AVG(litros_total), SUM(litros_total) FROM milk_production WHERE cattle_id = ? AND fecha >= ?', (cid, f30))
        r = c.fetchone()
        a30 = round(r[0] if r[0] else 0, 1)
        t30 = round(r[1] if r[1] else 0, 1)
        conn.close()
        return {'promedio_7d': a7, 'total_7d': t7, 'promedio_30d': a30, 'total_30d': t30}
    
    def add_heat(self, cid, fecha, obs=''):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO heat_control (cattle_id, fecha_celo, observaciones) VALUES (?, ?, ?)', (cid, fecha, obs))
        c.execute('UPDATE cattle SET last_heat_date = ? WHERE id = ?', (fecha, cid))
        conn.commit()
        conn.close()
    
    def add_insemination(self, cid, fecha, toro, num=1):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO insemination (cattle_id, fecha, toro_usado, num_servicio) VALUES (?, ?, ?, ?)', (cid, fecha, toro, num))
        exp = (datetime.strptime(fecha, '%Y-%m-%d') + timedelta(days=283)).strftime('%Y-%m-%d')
        c.execute('UPDATE cattle SET is_pregnant = 1, pregnancy_date = ?, expected_birth_date = ?, estado = ? WHERE id = ?', 
                  (fecha, exp, 'gestante', cid))
        conn.commit()
        conn.close()
    
    def add_vaccination(self, cid, vname, fecha, prox, cost=0):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO vaccination (cattle_id, vaccine_name, fecha, proxima_fecha, costo) VALUES (?, ?, ?, ?, ?)', 
                  (cid, vname, fecha, prox, cost))
        conn.commit()
        conn.close()
    
    def register_birth(self, cid, fecha, sexo='', peso=0, prob=''):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO births (cattle_id, fecha_parto, sexo_cria, peso_becerro, problemas) VALUES (?, ?, ?, ?, ?)', 
                  (cid, fecha, sexo, peso, prob))
        c.execute("""UPDATE cattle SET is_pregnant = 0, pregnancy_date = NULL, expected_birth_date = NULL,
            last_birth_date = ?, num_partos = num_partos + 1, estado = ?, dias_lactancia = 0 WHERE id = ?""", 
                  (fecha, 'lactando', cid))
        conn.commit()
        conn.close()
    
    def add_feeding(self, fecha, forra, conc, past, cf, cc):
        conn = self.get_connection()
        c = conn.cursor()
        ct = cf + cc
        c.execute("""INSERT INTO feeding (fecha, kg_forraje, kg_concentrado, horas_pastoreo, costo_forraje, costo_concentrado, costo_total)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (fecha, forra, conc, past, cf, cc, ct))
        conn.commit()
        conn.close()
    
    def get_global_stats(self):
        conn = self.get_connection()
        c = conn.cursor()
        s = {}
        c.execute('SELECT COUNT(*) FROM cattle')
        s['total_cattle'] = c.fetchone()[0]
        c.execute('SELECT estado, COUNT(*) FROM cattle GROUP BY estado')
        s['by_estado'] = dict(c.fetchall())
        c.execute('SELECT race, COUNT(*) FROM cattle GROUP BY race')
        s['by_race'] = dict(c.fetchall())
        c.execute('SELECT COUNT(*) FROM cattle WHERE is_pregnant = 1')
        s['pregnant'] = c.fetchone()[0]
        
        f7 = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        c.execute('SELECT SUM(litros_total), AVG(litros_total), COUNT(DISTINCT cattle_id) FROM milk_production WHERE fecha >= ?', (f7,))
        r = c.fetchone()
        s['leche_total_semana'] = round(r[0] if r[0] else 0, 1)
        s['leche_promedio_vaca_dia'] = round(r[1] if r[1] else 0, 1)
        s['vacas_produciendo'] = r[2] if r[2] else 0
        
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute('SELECT SUM(litros_total) FROM milk_production WHERE fecha = ?', (today,))
        r = c.fetchone()
        s['leche_hoy'] = round(r[0] if r[0] else 0, 1)
        
        c.execute('SELECT AVG(pico_produccion) FROM cattle WHERE pico_produccion > 0')
        r = c.fetchone()
        s['pico_promedio'] = round(r[0] if r[0] else 0, 1)
        
        f30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        c.execute('SELECT COUNT(*) FROM births WHERE fecha_parto >= ?', (f30,))
        s['partos_mes'] = c.fetchone()[0]
        
        two_y = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        c.execute('SELECT COUNT(*) FROM cattle')
        tc = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM births WHERE fecha_parto >= ?', (two_y,))
        b2 = c.fetchone()[0]
        s['birth_rate_annual'] = round((b2 / tc / 2) * 100, 1) if tc > 0 else 0
        
        future60 = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        c.execute('SELECT COUNT(*) FROM cattle WHERE is_pregnant = 1 AND expected_birth_date BETWEEN ? AND ?', (today, future60))
        s['near_birth_60'] = c.fetchone()[0]
        
        c.execute('SELECT SUM(kg_forraje), SUM(kg_concentrado), SUM(costo_total) FROM feeding WHERE fecha >= ?', (f7,))
        r = c.fetchone()
        s['forraje_semana'] = round(r[0] if r[0] else 0, 1)
        s['concentrado_semana'] = round(r[1] if r[1] else 0, 1)
        s['costo_alimento_semana'] = round(r[2] if r[2] else 0, 2)
        
        conn.close()
        return s
    
    def get_ia_alerts(self):
        conn = self.get_connection()
        c = conn.cursor()
        alerts = []
        today = datetime.now().strftime('%Y-%m-%d')
        
        c.execute('SELECT tag_number, expected_birth_date FROM cattle WHERE is_pregnant = 1 AND expected_birth_date < ? ORDER BY expected_birth_date', (today,))
        for row in c.fetchall():
            days = (datetime.now() - datetime.strptime(row[1], '%Y-%m-%d')).days
            alerts.append({'type': 'critico', 'title': f'🚨 Vaca {row[0]} VENCIDA', 'desc': f'Hace {days} días', 'cow': row[0]})
        
        f15 = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
        c.execute('SELECT tag_number, expected_birth_date FROM cattle WHERE is_pregnant = 1 AND expected_birth_date BETWEEN ? AND ?', (today, f15))
        for row in c.fetchall():
            days = (datetime.strptime(row[1], '%Y-%m-%d') - datetime.now()).days
            alerts.append({'type': 'urgente', 'title': f'⚠️ Vaca {row[0]} próxima', 'desc': f'Faltan {days}d ({row[1]})', 'cow': row[0]})
        
        f60to90 = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        f90 = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        c.execute('SELECT tag_number, expected_birth_date FROM cattle WHERE is_pregnant = 1 AND expected_birth_date BETWEEN ? AND ?', (f60to90, f90))
        for row in c.fetchall():
            days = (datetime.strptime(row[1], '%Y-%m-%d') - datetime.now()).days
            alerts.append({'type': 'aviso', 'title': f'🚫 Secar vaca {row[0]}', 'desc': f'Parto en {days}d - Secar YA', 'cow': row[0]})
        
        f30v = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        c.execute("""SELECT c.tag_number, v.vaccine_name, v.proxima_fecha FROM vaccination v
            JOIN cattle c ON v.cattle_id = c.id WHERE v.proxima_fecha BETWEEN ? AND ? ORDER BY v.proxima_fecha""", (today, f30v))
        for row in c.fetchall():
            days = (datetime.strptime(row[2], '%Y-%m-%d') - datetime.now()).days
            alerts.append({'type': 'aviso', 'title': f'💉 Vacuna {row[0]}', 'desc': f'{row[1]} en {days}d', 'cow': row[0]})
        
        f90d = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        c.execute('SELECT tag_number, last_birth_date FROM cattle WHERE is_pregnant = 0 AND estado = ? AND last_birth_date < ? AND last_birth_date IS NOT NULL', 
                  ('lactando', f90d))
        for row in c.fetchall():
            days = (datetime.now() - datetime.strptime(row[1], '%Y-%m-%d')).days
            alerts.append({'type': 'aviso', 'title': f'📋 Vaca {row[0]} abierta', 'desc': f'{days} días sin preñar', 'cow': row[0]})
        
        f7d = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        c.execute("""SELECT c.tag_number, c.pico_produccion, AVG(mp.litros_total) as pa FROM cattle c
            JOIN milk_production mp ON c.id = mp.cattle_id WHERE mp.fecha >= ? AND c.estado = ? AND c.pico_produccion > 0
            GROUP BY c.id HAVING pa < (c.pico_produccion * 0.7)""", (f7d, 'lactando'))
        for row in c.fetchall():
            perd = round(((row[1] - row[2]) / row[1]) * 100, 1)
            alerts.append({'type': 'urgente', 'title': f'📉 Vaca {row[0]} bajo', 'desc': f'Bajó {perd}% vs pico', 'cow': row[0]})
        
        conn.close()
        return alerts
    
    def get_ia_race_analysis(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""SELECT c.race, COUNT(c.id) as nv, AVG(c.pico_produccion) as ap, AVG(c.num_partos) as anp,
            CAST(SUM(CASE WHEN c.is_pregnant = 1 THEN 1 ELSE 0 END) AS REAL) * 100.0 / COUNT(c.id) as tp
            FROM cattle c GROUP BY c.race HAVING nv > 0 ORDER BY ap DESC""")
        cols = ['race', 'num_vacas', 'avg_pico', 'avg_partos', 'tasa_prenez']
        result = [dict(zip(cols, row)) for row in c.fetchall()]
        for r in result:
            r['avg_pico'] = round(r['avg_pico'] if r['avg_pico'] else 0, 1)
            r['avg_partos'] = round(r['avg_partos'] if r['avg_partos'] else 0, 1)
            r['tasa_prenez'] = round(r['tasa_prenez'] if r['tasa_prenez'] else 0, 1)
        conn.close()
        return result
    
    def get_ia_profitability(self, cid, days=30):
        conn = self.get_connection()
        c = conn.cursor()
        f = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        c.execute('SELECT SUM(litros_total) FROM milk_production WHERE cattle_id = ? AND fecha >= ?', (cid, f))
        r = c.fetchone()
        leche = r[0] if r[0] else 0
        c.execute('SELECT tag_number FROM cattle WHERE id = ?', (cid,))
        tag = c.fetchone()[0]
        c.execute('SELECT AVG(costo_total) FROM feeding WHERE fecha >= ?', (f,))
        r = c.fetchone()
        costo_dia = r[0] if r[0] else 0
        costo_total_vaca = costo_dia * days / c.execute('SELECT COUNT(*) FROM cattle').fetchone()[0] if c.execute('SELECT COUNT(*) FROM cattle').fetchone()[0] > 0 else 0
        c.execute('SELECT SUM(costo) FROM vaccination WHERE cattle_id = ? AND fecha >= ?', (cid, f))
        r = c.fetchone()
        costo_vacunas = r[0] if r[0] else 0
        c.execute('SELECT SUM(costo) FROM health WHERE cattle_id = ? AND fecha >= ?', (cid, f))
        r = c.fetchone()
        costo_salud = r[0] if r[0] else 0
        costo_total = costo_total_vaca + costo_vacunas + costo_salud
        conn.close()
        precio_litro = 10.0
        ingreso = leche * precio_litro
        ganancia = ingreso - costo_total
        return {
            'tag': tag,
            'leche_total': round(leche, 1),
            'ingreso': round(ingreso, 2),
            'costo_total': round(costo_total, 2),
            'ganancia': round(ganancia, 2),
            'rentable': ganancia > 0
        }

def calc_age(bd):
    if not bd: return "N/A"
    try:
        b = datetime.strptime(bd, '%Y-%m-%d')
        t = datetime.now()
        y = t.year - b.year
        m = t.month - b.month
        if m < 0:
            y -= 1
            m += 12
        return f"{y}a {m}m"
    except:
        return "N/A"

def days_until(ed):
    if not ed: return None
    try:
        return (datetime.strptime(ed, '%Y-%m-%d') - datetime.now()).days
    except:
        return None

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=[16, 10], spacing=12)
        hb = BoxLayout(size_hint_y=None, height=60, spacing=10)
        t = Label(text='[b]🐄 CattlePRO Milk AI[/b]', markup=True, font_size='22sp', color=GOLD, size_hint_x=0.7)
        ab = ModernButton(text='⚠️', size_hint_x=0.3, bg_color=RED)
        ab.bind(on_press=lambda x: setattr(self.manager, 'current', 'alertas'))
        hb.add_widget(t)
        hb.add_widget(ab)
        self.layout.add_widget(hb)
        
        sc = ScrollView()
        self.content = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, padding=[5, 5])
        self.content.bind(minimum_height=self.content.setter('height'))
        sc.add_widget(self.content)
        self.layout.add_widget(sc)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.content.clear_widgets()
        try:
            db = App.get_running_app().db
            s = db.get_global_stats()
            
            ia = ModernCard(orientation='vertical', size_hint_y=None, height=200, padding=18, spacing=10)
            badge = Label(text='🤖 IA ANÁLISIS', font_size='12sp', color=(0,0,0,1), size_hint_y=None, height=30)
            with badge.canvas.before:
                Color(*GOLD)
                badge.r = RoundedRectangle(pos=badge.pos, size=badge.size, radius=[8])
            badge.bind(pos=lambda *a: setattr(badge.r, 'pos', badge.pos), size=lambda *a: setattr(badge.r, 'size', badge.size))
            txt = Label(text=f"Leche hoy: {s['leche_hoy']}L\nSemana: {s['leche_total_semana']}L\nForraje/sem: {s['forraje_semana']}kg\nConcentrado/sem: {s['concentrado_semana']}kg\nCosto/sem: ${s['costo_alimento_semana']}\n% Partos: {s['birth_rate_annual']}%",
                       font_size='15sp', color=TEXT, size_hint_y=None, height=120, halign='left', valign='top')
            txt.bind(size=txt.setter('text_size'))
            ib = ModernButton(text='Ver IA Completo', size_hint_y=None, height=50, font_size='15sp', bg_color=BLUE)
            ib.bind(on_press=lambda x: setattr(self.manager, 'current', 'ia'))
            ia.add_widget(badge)
            ia.add_widget(txt)
            ia.add_widget(ib)
            self.content.add_widget(ia)
            
            sg = GridLayout(cols=2, spacing=10, size_hint_y=None, height=320)
            items = [
                ('Total Vacas', s['total_cattle']),
                ('Lactando', s['by_estado'].get('lactando', 0)),
                ('Preñadas', s['pregnant']),
                ('Secas', s['by_estado'].get('seca', 0)),
                ('Leche Hoy', f"{s['leche_hoy']}L"),
                ('Pico Prom', f"{s['pico_promedio']}L"),
                ('Partos/Mes', s['partos_mes']),
                ('Próximas 60d', s['near_birth_60'])
            ]
            for lb, vl in items:
                cd = ModernCard(orientation='vertical', padding=14, spacing=5)
                l1 = Label(text=lb, font_size='12sp', color=MUTED, size_hint_y=None, height=18)
                l2 = Label(text=f'[b]{vl}[/b]', markup=True, font_size='26sp', color=TEXT, size_hint_y=None, height=35)
                cd.add_widget(l1)
                cd.add_widget(l2)
                sg.add_widget(cd)
            self.content.add_widget(sg)
            
            self.content.add_widget(Label(text='[b]Accesos Rápidos[/b]', markup=True, font_size='18sp', color=GOLD, size_hint_y=None, height=35, halign='left'))
            qg = GridLayout(cols=2, spacing=10, size_hint_y=None, height=160)
            btns = [
                ('📋 Ganado', 'ganado'),
                ('➕ Agregar', 'agregar'),
                ('🥛 Leche', 'leche'),
                ('📅 Alertas', 'alertas')
            ]
            for txt, scr in btns:
                b = ModernButton(text=txt, font_size='16sp', bg_color=S2)
                b.color = TEXT
                b.bind(on_press=lambda x, s=scr: setattr(self.manager, 'current', s))
                qg.add_widget(b)
            self.content.add_widget(qg)
        except Exception as e:
            print(f"[ERROR] HomeScreen: {e}")

class GanadoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=[16, 10], spacing=12)
        hb = BoxLayout(size_hint_y=None, height=60, spacing=10)
        bb = ModernButton(text='← Inicio', bg_color=S2, font_size='18sp')
        bb.color = TEXT
        bb.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        t = Label(text='[b]Mi Ganado[/b]', markup=True, font_size='22sp', color=GOLD)
        hb.add_widget(bb)
        hb.add_widget(t)
        self.layout.add_widget(hb)
        
        sc = ScrollView()
        self.cc = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, padding=[5, 5])
        self.cc.bind(minimum_height=self.cc.setter('height'))
        sc.add_widget(self.cc)
        self.layout.add_widget(sc)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.cc.clear_widgets()
        try:
            db = App.get_running_app().db
            cattle = db.get_all_cattle()
            if not cattle:
                self.cc.add_widget(Label(text='Sin vacas', size_hint_y=None, height=100, font_size='18sp', color=MUTED))
                return
            for c in cattle:
                cd = ModernCard(orientation='vertical', size_hint_y=None, height=140, padding=20, spacing=10)
                tag = Label(text=f"[b]{c['tag_number']}[/b]", markup=True, font_size='32sp', color=GOLD, size_hint_y=None, height=40)
                info = f"{c.get('race', 'N/A')} • {c.get('estado', 'N/A')}"
                if c['is_pregnant'] and c.get('expected_birth_date'):
                    d = days_until(c['expected_birth_date'])
                    if d is not None:
                        if d < 0:
                            info += f"\n🚨 Vencida ({abs(d)}d)"
                        elif d <= 60:
                            info += f"\n⚠️ Parto en {d}d"
                        else:
                            info += f"\n🤰 Gestante ({d}d)"
                inf = Label(text=info, font_size='16sp', color=TEXT, size_hint_y=None, height=50, halign='left', valign='top')
                inf.bind(size=inf.setter('text_size'))
                btn = ModernButton(text='Ver Detalle', size_hint_y=None, height=50, font_size='16sp')
                btn.bind(on_press=lambda x, i=c['id']: self.view_detail(i))
                cd.add_widget(tag)
                cd.add_widget(inf)
                cd.add_widget(btn)
                self.cc.add_widget(cd)
        except Exception as e:
            print(f"[ERROR] GanadoScreen: {e}")
    
    def view_detail(self, cid):
        ds = self.manager.get_screen('detalle')
        ds.load_cattle(cid)
        self.manager.current = 'detalle'

class AgregarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=[16, 10], spacing=12)
        hb = BoxLayout(size_hint_y=None, height=60, spacing=10)
        bb = ModernButton(text='← Atrás', bg_color=S2, font_size='18sp')
        bb.color = TEXT
        bb.bind(on_press=lambda x: setattr(self.manager, 'current', 'ganado'))
        t = Label(text='[b]Agregar Vaca[/b]', markup=True, font_size='22sp', color=GOLD)
        hb.add_widget(bb)
        hb.add_widget(t)
        self.layout.add_widget(hb)
        
        sc = ScrollView()
        form = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=[10, 10])
        form.bind(minimum_height=form.setter('height'))
        
        form.add_widget(Label(text='ARETE', font_size='14sp', color=MUTED, size_hint_y=None, height=25, halign='left'))
        self.tag_btn = ModernButton(text='Click para ingresar', size_hint_y=None, height=60, font_size='18sp', bg_color=S2)
        self.tag_btn.color = TEXT
        self.tag_btn.bind(on_press=self.show_keypad)
        self.tag_value = ''
        form.add_widget(self.tag_btn)
        
        form.add_widget(Label(text='RAZA', font_size='14sp', color=MUTED, size_hint_y=None, height=25, halign='left'))
        self.race_sp = Spinner(text='Holstein', values=('Holstein', 'Jersey', 'Pardo Suizo', 'Simmental', 'Otro'), 
                               size_hint_y=None, height=60, background_color=INP, color=TEXT, font_size='18sp')
        form.add_widget(self.race_sp)
        
        form.add_widget(Label(text='ESTADO', font_size='14sp', color=MUTED, size_hint_y=None, height=25, halign='left'))
        self.estado_sp = Spinner(text='seca', values=('seca', 'lactando', 'gestante'), 
                                 size_hint_y=None, height=60, background_color=INP, color=TEXT, font_size='18sp')
        form.add_widget(self.estado_sp)
        
        sc.add_widget(form)
        self.layout.add_widget(sc)
        
        btn_save = ModernButton(text='💾 Guardar', size_hint_y=None, height=70, bg_color=GREEN, font_size='20sp')
        btn_save.bind(on_press=self.save)
        self.layout.add_widget(btn_save)
        self.add_widget(self.layout)
    
    def show_keypad(self, inst):
        cnt = BoxLayout(orientation='vertical', spacing=15, padding=20)
        cnt.add_widget(Label(text='Número de Arete:', font_size='20sp', size_hint_y=None, height=40))
        disp = Label(text='', font_size='32sp', size_hint_y=None, height=60, color=GOLD)
        cnt.add_widget(disp)
        
        kb = GridLayout(cols=3, spacing=10, size_hint_y=None, height=320)
        for n in ['1','2','3','4','5','6','7','8','9','0','←','OK']:
            b = ModernButton(text=n, font_size='28sp', bg_color=GREEN if n=='OK' else RED if n=='←' else S2)
            b.color = (0,0,0,1) if n=='OK' else TEXT
            def press(x, num=n):
                if num == 'OK':
                    self.tag_value = disp.text
                    self.tag_btn.text = self.tag_value if self.tag_value else 'Click para ingresar'
                    pop.dismiss()
                elif num == '←':
                    disp.text = disp.text[:-1]
                else:
                    disp.text += num
            b.bind(on_press=press)
            kb.add_widget(b)
        cnt.add_widget(kb)
        pop = Popup(title='Arete', content=cnt, size_hint=(0.9, 0.8))
        pop.open()
    
    def save(self, inst):
        if not self.tag_value:
            return
        try:
            db = App.get_running_app().db
            today = datetime.now().strftime('%Y-%m-%d')
            db.add_cattle({
                'tag_number': self.tag_value,
                'birth_date': today,
                'race': self.race_sp.text,
                'estado': self.estado_sp.text
            })
            self.tag_value = ''
            self.tag_btn.text = 'Click para ingresar'
            self.manager.current = 'ganado'
        except Exception as e:
            print(f"[ERROR] save: {e}")

class DetalleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cid = None
        self.layout = BoxLayout(orientation='vertical', padding=[16, 10], spacing=12)
        hb = BoxLayout(size_hint_y=None, height=60, spacing=10)
        bb = ModernButton(text='← Lista', bg_color=S2, font_size='18sp')
        bb.color = TEXT
        bb.bind(on_press=lambda x: setattr(self.manager, 'current', 'ganado'))
        self.title = Label(text='Detalle', font_size='22sp', color=GOLD)
        bd = ModernButton(text='🗑️', size_hint_x=0.25, bg_color=RED, font_size='18sp')
        bd.bind(on_press=self.delete)
        hb.add_widget(bb)
        hb.add_widget(self.title)
        hb.add_widget(bd)
        self.layout.add_widget(hb)
        
        sc = ScrollView()
        self.content = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, padding=[10, 10])
        self.content.bind(minimum_height=self.content.setter('height'))
        sc.add_widget(self.content)
        self.layout.add_widget(sc)
        self.add_widget(self.layout)
    
    def load_cattle(self, cid):
        self.cid = cid
        self.content.clear_widgets()
        try:
            db = App.get_running_app().db
            c = db.get_cattle_by_id(cid)
            if not c: return
            
            cd = ModernCard(orientation='vertical', size_hint_y=None, height=300, padding=20, spacing=12)
            tag = Label(text=f"[b]{c['tag_number']}[/b]", markup=True, font_size='36sp', color=GOLD, size_hint_y=None, height=50)
            cd.add_widget(tag)
            
            data = [
                ('Raza:', c.get('race', 'N/A')),
                ('Edad:', calc_age(c.get('birth_date'))),
                ('Partos:', c.get('num_partos', 0)),
                ('Estado:', c.get('estado', 'N/A')),
                ('Días Lact:', c.get('dias_lactancia', 0)),
                ('Pico:', f"{c.get('pico_produccion', 0)}L")
            ]
            
            if c['is_pregnant'] and c.get('expected_birth_date'):
                d = days_until(c['expected_birth_date'])
                if d is not None:
                    data.append(('Parto en:', f"{d} días ({c['expected_birth_date']})"))
            
            for lb, vl in data:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=10)
                l1 = Label(text=lb, font_size='16sp', color=MUTED, halign='left', size_hint_x=0.45)
                l1.bind(size=l1.setter('text_size'))
                l2 = Label(text=str(vl), font_size='16sp', color=TEXT, halign='right', size_hint_x=0.55)
                l2.bind(size=l2.setter('text_size'))
                row.add_widget(l1)
                row.add_widget(l2)
                cd.add_widget(row)
            
            self.content.add_widget(cd)
            
            prof = db.get_ia_profitability(cid, 30)
            pcd = ModernCard(orientation='vertical', size_hint_y=None, height=180, padding=20, spacing=8)
            pcd.add_widget(Label(text='[b]💰 RENTABILIDAD (30d)[/b]', markup=True, font_size='16sp', color=GOLD, size_hint_y=None, height=30))
            pdata = [
                ('Leche:', f"{prof['leche_total']}L"),
                ('Ingreso:', f"${prof['ingreso']}"),
                ('Costo:', f"${prof['costo_total']}"),
                ('Ganancia:', f"${prof['ganancia']}")
            ]
            for lb, vl in pdata:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=25, spacing=10)
                l1 = Label(text=lb, font_size='14sp', color=MUTED, halign='left', size_hint_x=0.5)
                l1.bind(size=l1.setter('text_size'))
                l2 = Label(text=vl, font_size='14sp', color=GREEN if 'Ganancia' in lb and prof['rentable'] else RED if 'Ganancia' in lb else TEXT, halign='right', size_hint_x=0.5)
                l2.bind(size=l2.setter('text_size'))
                row.add_widget(l1)
                row.add_widget(l2)
                pcd.add_widget(row)
            self.content.add_widget(pcd)
            
            ag = GridLayout(cols=2, spacing=10, size_hint_y=None, height=140)
            btns = [
                ('🥛 Leche', lambda x: self.reg_milk()),
                ('🐄 Parto', lambda x: self.reg_birth()),
                ('🤰 Cargar', lambda x: self.reg_ins()),
                ('💉 Vacuna', lambda x: self.reg_vacc())
            ]
            for txt, fn in btns:
                b = ModernButton(text=txt, font_size='16sp', bg_color=S2)
                b.color = TEXT
                b.bind(on_press=fn)
                ag.add_widget(b)
            self.content.add_widget(ag)
            
            ms = db.get_milk_stats(cid)
            mcd = ModernCard(orientation='vertical', size_hint_y=None, height=150, padding=20, spacing=8)
            mcd.add_widget(Label(text='[b]🥛 PRODUCCIÓN LECHE[/b]', markup=True, font_size='16sp', color=GOLD, size_hint_y=None, height=30))
            mdata = [
                ('Prom 7d:', f"{ms['promedio_7d']}L/día"),
                ('Total 7d:', f"{ms['total_7d']}L"),
                ('Prom 30d:', f"{ms['promedio_30d']}L/día"),
                ('Total 30d:', f"{ms['total_30d']}L")
            ]
            for lb, vl in mdata:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=22, spacing=10)
                l1 = Label(text=lb, font_size='13sp', color=MUTED, halign='left', size_hint_x=0.5)
                l1.bind(size=l1.setter('text_size'))
                l2 = Label(text=vl, font_size='13sp', color=TEXT, halign='right', size_hint_x=0.5)
                l2.bind(size=l2.setter('text_size'))
                row.add_widget(l1)
                row.add_widget(l2)
                mcd.add_widget(row)
            self.content.add_widget(mcd)
            
        except Exception as e:
            print(f"[ERROR] load_cattle: {e}")
    
    def reg_milk(self):
        cnt = BoxLayout(orientation='vertical', spacing=15, padding=20)
        cnt.add_widget(Label(text='Registro Leche', font_size='20sp', size_hint_y=None, height=40))
        
        cnt.add_widget(Label(text='Litros Mañana:', font_size='14sp', color=MUTED, size_hint_y=None, height=25, halign='left'))
        lm = Spinner(text='10', values=[str(i) for i in range(0, 51)], size_hint_y=None, height=60, background_color=INP, color=TEXT, font_size='18sp')
        cnt.add_widget(lm)
        
        cnt.add_widget(Label(text='Litros Tarde:', font_size='14sp', color=MUTED, size_hint_y=None, height=25, halign='left'))
        lt = Spinner(text='10', values=[str(i) for i in range(0, 51)], size_hint_y=None, height=60, background_color=INP, color=TEXT, font_size='18sp')
        cnt.add_widget(lt)
        
        pop = Popup(title='Leche', content=cnt, size_hint=(0.9, 0.7))
        
        btns = BoxLayout(size_hint_y=None, height=60, spacing=10)
        bc = ModernButton(text='Cancelar', bg_color=S2)
        bc.color = TEXT
        bc.bind(on_press=pop.dismiss)
        bs = ModernButton(text='Guardar', bg_color=GREEN)
        def save(x):
            try:
                db = App.get_running_app().db
                db.add_milk_production(self.cid, datetime.now().strftime('%Y-%m-%d'), float(lm.text), float(lt.text))
                pop.dismiss()
                self.load_cattle(self.cid)
            except: pass
        bs.bind(on_press=save)
        btns.add_widget(bc)
        btns.add_widget(bs)
        cnt.add_widget(btns)
        pop.open()
    
    def reg_birth(self):
        try:
            db = App.get_running_app().db
            db.register_birth(self.cid, datetime.now().strftime('%Y-%m-%d'))
            self.load_cattle(self.cid)
        except: pass
    
    def reg_ins(self):
        try:
            db = App.get_running_app().db
            db.add_insemination(self.cid, datetime.now().strftime('%Y-%m-%d'), 'Toro1', 1)
            self.load_cattle(self.cid)
        except: pass
    
    def reg_vacc(self):
        try:
            db = App.get_running_app().db
            today = datetime.now().strftime('%Y-%m-%d')
            prox = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
            db.add_vaccination(self.cid, 'Vacuna', today, prox, 0)
            self.load_cattle(self.cid)
        except: pass
    
    def delete(self, inst):
        try:
            db = App.get_running_app().db
            db.delete_cattle(self.cid)
            self.manager.current = 'ganado'
        except: pass

class AlertasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=[16, 10], spacing=12)
        hb = BoxLayout(size_hint_y=None, height=60, spacing=10)
        bb = ModernButton(text='← Inicio', bg_color=S2, font_size='18sp')
        bb.color = TEXT
        bb.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        t = Label(text='[b]Alertas IA[/b]', markup=True, font_size='22sp', color=GOLD)
        hb.add_widget(bb)
        hb.add_widget(t)
        self.layout.add_widget(hb)
        
        sc = ScrollView()
        self.cc = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, padding=[5, 5])
        self.cc.bind(minimum_height=self.cc.setter('height'))
        sc.add_widget(self.cc)
        self.layout.add_widget(sc)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.cc.clear_widgets()
        try:
            db = App.get_running_app().db
            alerts = db.get_ia_alerts()
            if not alerts:
                self.cc.add_widget(Label(text='Sin alertas', size_hint_y=None, height=100, font_size='18sp', color=MUTED))
                return
            
            critico = [a for a in alerts if a['type'] == 'critico']
            urgente = [a for a in alerts if a['type'] == 'urgente']
            aviso = [a for a in alerts if a['type'] == 'aviso']
            
            if critico:
                self.cc.add_widget(Label(text='[b]🚨 CRÍTICO[/b]', markup=True, font_size='18sp', color=RED, size_hint_y=None, height=35, halign='left'))
                for a in critico:
                    cd = ModernCard(orientation='vertical', size_hint_y=None, height=80, padding=15, spacing=5)
                    cd.add_widget(Label(text=a['title'], font_size='16sp', color=RED, size_hint_y=None, height=25, halign='left', valign='top'))
                    cd.add_widget(Label(text=a['desc'], font_size='14sp', color=TEXT, size_hint_y=None, height=20, halign='left', valign='top'))
                    self.cc.add_widget(cd)
            
            if urgente:
                self.cc.add_widget(Label(text='[b]⚠️ URGENTE[/b]', markup=True, font_size='18sp', color=YELLOW, size_hint_y=None, height=35, halign='left'))
                for a in urgente:
                    cd = ModernCard(orientation='vertical', size_hint_y=None, height=80, padding=15, spacing=5)
                    cd.add_widget(Label(text=a['title'], font_size='16sp', color=YELLOW, size_hint_y=None, height=25, halign='left', valign='top'))
                    cd.add_widget(Label(text=a['desc'], font_size='14sp', color=TEXT, size_hint_y=None, height=20, halign='left', valign='top'))
                    self.cc.add_widget(cd)
            
            if aviso:
                self.cc.add_widget(Label(text='[b]📋 AVISOS[/b]', markup=True, font_size='18sp', color=BLUE, size_hint_y=None, height=35, halign='left'))
                for a in aviso:
                    cd = ModernCard(orientation='vertical', size_hint_y=None, height=80, padding=15, spacing=5)
                    cd.add_widget(Label(text=a['title'], font_size='16sp', color=BLUE, size_hint_y=None, height=25, halign='left', valign='top'))
                    cd.add_widget(Label(text=a['desc'], font_size='14sp', color=TEXT, size_hint_y=None, height=20, halign='left', valign='top'))
                    self.cc.add_widget(cd)
        except Exception as e:
            print(f"[ERROR] AlertasScreen: {e}")

class IAScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=[16, 10], spacing=12)
        hb = BoxLayout(size_hint_y=None, height=60, spacing=10)
        bb = ModernButton(text='← Inicio', bg_color=S2, font_size='18sp')
        bb.color = TEXT
        bb.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        t = Label(text='[b]🤖 Análisis IA[/b]', markup=True, font_size='22sp', color=GOLD)
        hb.add_widget(bb)
        hb.add_widget(t)
        self.layout.add_widget(hb)
        
        sc = ScrollView()
        self.cc = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, padding=[5, 5])
        self.cc.bind(minimum_height=self.cc.setter('height'))
        sc.add_widget(self.cc)
        self.layout.add_widget(sc)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.cc.clear_widgets()
        try:
            db = App.get_running_app().db
            
            self.cc.add_widget(Label(text='[b]📊 ANÁLISIS POR RAZA[/b]', markup=True, font_size='18sp', color=GOLD, size_hint_y=None, height=35, halign='left'))
            races = db.get_ia_race_analysis()
            for r in races:
                cd = ModernCard(orientation='vertical', size_hint_y=None, height=150, padding=15, spacing=8)
                cd.add_widget(Label(text=f"[b]{r['race']}[/b] ({r['num_vacas']} vacas)", markup=True, font_size='18sp', color=GOLD, size_hint_y=None, height=30))
                data = [
                    ('Pico Prom:', f"{r['avg_pico']}L"),
                    ('Partos Prom:', f"{r['avg_partos']}"),
                    ('Tasa Preñez:', f"{r['tasa_prenez']}%")
                ]
                for lb, vl in data:
                    row = BoxLayout(orientation='horizontal', size_hint_y=None, height=25, spacing=10)
                    l1 = Label(text=lb, font_size='14sp', color=MUTED, halign='left', size_hint_x=0.5)
                    l1.bind(size=l1.setter('text_size'))
                    l2 = Label(text=vl, font_size='14sp', color=TEXT, halign='right', size_hint_x=0.5)
                    l2.bind(size=l2.setter('text_size'))
                    row.add_widget(l1)
                    row.add_widget(l2)
                    cd.add_widget(row)
                self.cc.add_widget(cd)
            
            s = db.get_global_stats()
            self.cc.add_widget(Label(text='[b]🎯 MÉTRICAS CLAVE[/b]', markup=True, font_size='18sp', color=GOLD, size_hint_y=None, height=35, halign='left'))
            mcd = ModernCard(orientation='vertical', size_hint_y=None, height=220, padding=15, spacing=8)
            mdata = [
                ('Total Vacas:', s['total_cattle']),
                ('Vacas Produciendo:', s['vacas_produciendo']),
                ('Leche Hoy:', f"{s['leche_hoy']}L"),
                ('Leche Semana:', f"{s['leche_total_semana']}L"),
                ('Forraje/Semana:', f"{s['forraje_semana']}kg"),
                ('Concentrado/Semana:', f"{s['concentrado_semana']}kg"),
                ('Costo Alimento/Sem:', f"${s['costo_alimento_semana']}"),
                ('% Partos/Año:', f"{s['birth_rate_annual']}%")
            ]
            for lb, vl in mdata:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=22, spacing=10)
                l1 = Label(text=lb, font_size='13sp', color=MUTED, halign='left', size_hint_x=0.6)
                l1.bind(size=l1.setter('text_size'))
                l2 = Label(text=str(vl), font_size='13sp', color=TEXT, halign='right', size_hint_x=0.4)
                l2.bind(size=l2.setter('text_size'))
                row.add_widget(l1)
                row.add_widget(l2)
                mcd.add_widget(row)
            self.cc.add_widget(mcd)
            
        except Exception as e:
            print(f"[ERROR] IAScreen: {e}")

class CattleMilkApp(App):
    def build(self):
        try:
            self.db = Database()
            sm = ScreenManager()
            sm.add_widget(HomeScreen(name='home'))
            sm.add_widget(GanadoScreen(name='ganado'))
            sm.add_widget(AgregarScreen(name='agregar'))
            sm.add_widget(DetalleScreen(name='detalle'))
            sm.add_widget(AlertasScreen(name='alertas'))
            sm.add_widget(IAScreen(name='ia'))
            return sm
        except Exception as e:
            print(f"[ERROR] build: {e}")
            return Label(text=f'Error: {e}', color=RED)

if __name__ == '__main__':
    CattleMilkApp().run()
