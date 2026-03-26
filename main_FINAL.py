#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐄 CATTLE MANAGER PRO - Sistema Profesional de Gestión Ganadera
VERSIÓN FINAL - Cajas grandes + % Partos/Año
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
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import get_color_from_hex, platform
import sqlite3
import re

# === PALETA DE COLORES PROFESIONAL ===
BG = get_color_from_hex('#0a0e27')
CARD = get_color_from_hex('#1a1f3a')
PRIMARY = get_color_from_hex('#4c9aff')
SUCCESS = get_color_from_hex('#36b37e')
WARNING = get_color_from_hex('#ffab00')
DANGER = get_color_from_hex('#ff5630')
INFO = get_color_from_hex('#00b8d9')
PURPLE = get_color_from_hex('#6554c0')
PINK = get_color_from_hex('#ff79c6')
TEXT = get_color_from_hex('#e6edf3')
TEXT_DIM = get_color_from_hex('#8c92a0')

Window.clearcolor = BG


# === COMPONENTES PERSONALIZADOS ===

class RoundedButton(Button):
    """Botón con bordes redondeados"""
    def __init__(self, bg_color=PRIMARY, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = TEXT
        self.bold = True
        self.bg_color = bg_color
        
        with self.canvas.before:
            self.rect_color = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class StyledCard(BoxLayout):
    """Tarjeta con fondo redondeado"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*CARD)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# === BASE DE DATOS ===

class Database:
    """Gestión completa de la base de datos SQLite"""
    
    def __init__(self):
        # CORRECCIÓN PARA ANDROID
        try:
            if platform == 'android':
                from android.storage import app_storage_path
                storage_path = app_storage_path()
                self.db_path = os.path.join(storage_path, 'cattle_manager.db')
                print(f"[ANDROID] Base de datos en: {self.db_path}")
            else:
                self.db_path = os.path.expanduser('~/cattle_manager.db')
                print(f"[DESKTOP] Base de datos en: {self.db_path}")
        except Exception as e:
            print(f"[ERROR] Detectando plataforma: {e}")
            self.db_path = os.path.expanduser('~/cattle_manager.db')
        
        try:
            self.init_database()
            print("[OK] Base de datos inicializada")
        except Exception as e:
            print(f"[ERROR] Inicializando DB: {e}")
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializar todas las tablas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cattle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_number TEXT UNIQUE NOT NULL,
                name TEXT,
                birth_date TEXT,
                weight REAL,
                category TEXT,
                is_pregnant INTEGER DEFAULT 0,
                pregnancy_date TEXT,
                expected_birth_date TEXT,
                last_birth_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vaccination_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cattle_id INTEGER,
                vaccine_name TEXT,
                vaccination_date TEXT,
                next_vaccination_date TEXT,
                notes TEXT,
                FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cattle_id INTEGER,
                event_type TEXT,
                event_date TEXT,
                notes TEXT,
                FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cattle_id INTEGER,
                activity_type TEXT,
                description TEXT,
                activity_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cattle_id) REFERENCES cattle (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_cattle(self, data):
        """Agregar una vaca"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO cattle (tag_number, name, birth_date, weight, category,
                                    is_pregnant, pregnancy_date, expected_birth_date,
                                    last_birth_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data.get('tag_number'), data.get('name'), data.get('birth_date'),
                  data.get('weight'), data.get('category'), data.get('is_pregnant', 0),
                  data.get('pregnancy_date'), data.get('expected_birth_date'),
                  data.get('last_birth_date'), data.get('notes')))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def update_cattle(self, cattle_id, data):
        """Actualizar datos de una vaca"""
        conn = self.get_connection()
        cursor = conn.cursor()
        fields = []
        values = []
        for key, value in data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                values.append(value)
        values.append(cattle_id)
        query = f"UPDATE cattle SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    
    def get_all_cattle(self):
        """Obtener todas las vacas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cattle ORDER BY tag_number')
        columns = [desc[0] for desc in cursor.description]
        cattle_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return cattle_list
    
    def get_cattle_by_id(self, cattle_id):
        """Obtener una vaca por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cattle WHERE id = ?', (cattle_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        conn.close()
        return dict(zip(columns, row)) if row else None
    
    def search_cattle(self, query):
        """Buscar vacas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE tag_number LIKE ? OR name LIKE ?
            ORDER BY tag_number
        ''', (search_term, search_term))
        columns = [desc[0] for desc in cursor.description]
        cattle_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return cattle_list
    
    def delete_cattle(self, cattle_id):
        """Eliminar una vaca"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cattle WHERE id = ?', (cattle_id,))
        conn.commit()
        conn.close()
    
    def add_vaccination(self, cattle_id, vaccine_name, vaccination_date, next_date, notes=''):
        """Agregar vacunación"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vaccination_history (cattle_id, vaccine_name, vaccination_date,
                                             next_vaccination_date, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (cattle_id, vaccine_name, vaccination_date, next_date, notes))
        conn.commit()
        conn.close()
    
    def get_vaccinations(self, cattle_id):
        """Obtener vacunaciones"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM vaccination_history 
            WHERE cattle_id = ?
            ORDER BY vaccination_date DESC
        ''', (cattle_id,))
        columns = [desc[0] for desc in cursor.description]
        vaccinations = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return vaccinations
    
    def add_event(self, cattle_id, event_type, event_date, notes=''):
        """Agregar evento"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (cattle_id, event_type, event_date, notes)
            VALUES (?, ?, ?, ?)
        ''', (cattle_id, event_type, event_date, notes))
        conn.commit()
        conn.close()
    
    def get_events(self, cattle_id):
        """Obtener eventos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM events 
            WHERE cattle_id = ?
            ORDER BY event_date DESC
        ''', (cattle_id,))
        columns = [desc[0] for desc in cursor.description]
        events = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return events
    
    def add_activity_log(self, cattle_id, activity_type, description):
        """Agregar log de actividad"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activity_log (cattle_id, activity_type, description)
            VALUES (?, ?, ?)
        ''', (cattle_id, activity_type, description))
        conn.commit()
        conn.close()
    
    def get_activity_log(self, limit=50):
        """Obtener log de actividades"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT al.*, c.tag_number, c.name
            FROM activity_log al
            JOIN cattle c ON al.cattle_id = c.id
            ORDER BY al.activity_date DESC
            LIMIT ?
        ''', (limit,))
        columns = [desc[0] for desc in cursor.description]
        activities = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return activities
    
    def get_statistics(self):
        """Obtener estadísticas generales"""
        conn = self.get_connection()
        cursor = conn.cursor()
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM cattle')
        stats['total_cattle'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT category, COUNT(*) FROM cattle GROUP BY category')
        stats['by_category'] = dict(cursor.fetchall())
        
        cursor.execute('SELECT COUNT(*) FROM cattle WHERE is_pregnant = 1')
        stats['pregnant'] = cursor.fetchone()[0]
        
        today = datetime.now().strftime('%Y-%m-%d')
        future_60 = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date BETWEEN ? AND ?
        ''', (today, future_60))
        stats['near_birth_60'] = cursor.fetchone()[0]
        
        future_90 = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date BETWEEN ? AND ?
        ''', (future_60, future_90))
        stats['to_dry'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM cattle WHERE is_pregnant = 0')
        stats['not_pregnant'] = cursor.fetchone()[0]
        
        past_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM cattle 
            WHERE last_birth_date >= ?
        ''', (past_30,))
        stats['recent_births'] = cursor.fetchone()[0]
        
        year_start = f"{datetime.now().year}-01-01"
        cursor.execute('''
            SELECT COUNT(*) FROM events 
            WHERE event_type = 'birth' 
            AND event_date >= ?
        ''', (year_start,))
        stats['births_this_year'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(weight) FROM cattle WHERE weight IS NOT NULL')
        avg_weight = cursor.fetchone()[0]
        stats['avg_weight'] = round(avg_weight, 1) if avg_weight else 0
        
        future_30 = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(DISTINCT cattle_id) FROM vaccination_history
            WHERE next_vaccination_date BETWEEN ? AND ?
        ''', (today, future_30))
        stats['need_vaccine'] = cursor.fetchone()[0]
        
        # NUEVO: Calcular % de partos anuales (últimos 2 años)
        two_years_ago = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM cattle')
        total_cows = cursor.fetchone()[0]
        cursor.execute('''
            SELECT COUNT(*) FROM events 
            WHERE event_type = 'birth' 
            AND event_date >= ?
        ''', (two_years_ago,))
        births_2y = cursor.fetchone()[0]
        
        if total_cows > 0:
            births_per_cow = births_2y / total_cows
            stats['birth_rate_annual'] = round((births_per_cow / 2) * 100, 1)
        else:
            stats['birth_rate_annual'] = 0
        
        conn.close()
        return stats
    
    def get_agenda_items(self):
        """Obtener items de la agenda"""
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        agenda = {
            'to_dry': [],
            'near_birth': [],
            'need_vaccine': [],
            'recent_births': [],
            'overdue': []
        }
        
        future_60 = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        future_90 = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date BETWEEN ? AND ?
            ORDER BY expected_birth_date
        ''', (future_60, future_90))
        columns = [desc[0] for desc in cursor.description]
        agenda['to_dry'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date BETWEEN ? AND ?
            ORDER BY expected_birth_date
        ''', (today, future_60))
        agenda['near_birth'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date < ?
            ORDER BY expected_birth_date
        ''', (today,))
        agenda['overdue'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        past_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE last_birth_date >= ?
            ORDER BY last_birth_date DESC
        ''', (past_30,))
        agenda['recent_births'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        future_30 = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT c.*, vh.vaccine_name, vh.next_vaccination_date
            FROM cattle c
            JOIN vaccination_history vh ON c.id = vh.cattle_id
            WHERE vh.next_vaccination_date BETWEEN ? AND ?
            ORDER BY vh.next_vaccination_date
        ''', (today, future_30))
        columns_vacc = [desc[0] for desc in cursor.description]
        agenda['need_vaccine'] = [dict(zip(columns_vacc, row)) for row in cursor.fetchall()]
        
        conn.close()
        return agenda


# === FUNCIONES AUXILIARES ===

def calculate_age(birth_date):
    """Calcular edad en formato Xa Ym"""
    if not birth_date:
        return "N/A"
    try:
        birth = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.now()
        years = today.year - birth.year
        months = today.month - birth.month
        if months < 0:
            years -= 1
            months += 12
        return f"{years}a {months}m"
    except:
        return "N/A"


def calculate_days_to_birth(expected_date):
    """Calcular días hasta el parto"""
    if not expected_date:
        return None
    try:
        expected = datetime.strptime(expected_date, '%Y-%m-%d')
        today = datetime.now()
        delta = (expected - today).days
        return delta
    except:
        return None


def calculate_days_since(date_str):
    """Calcular días desde una fecha"""
    if not date_str:
        return None
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now()
        delta = (today - date).days
        return delta
    except:
        return None


# === PANTALLAS ===

class HomeScreen(Screen):
    """Pantalla principal con estadísticas"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(
            text='[b]🐄 Gestión Ganadera PRO[/b]',
            markup=True,
            font_size='24sp',
            color=TEXT,
            size_hint_y=0.1
        )
        self.layout.add_widget(header)
        
        # Stats cards
        scroll = ScrollView(size_hint_y=0.5)
        self.stats_container = GridLayout(cols=2, spacing=8, size_hint_y=None, padding=5)
        self.stats_container.bind(minimum_height=self.stats_container.setter('height'))
        scroll.add_widget(self.stats_container)
        self.layout.add_widget(scroll)
        
        # Botones de navegación
        buttons_grid = GridLayout(cols=2, spacing=8, size_hint_y=0.4)
        
        btn_list = RoundedButton(text='📋 Ver Ganado', font_size='16sp', bg_color=PRIMARY)
        btn_list.bind(on_press=lambda x: setattr(self.manager, 'current', 'cattle_list'))
        
        btn_add = RoundedButton(text='➕ Agregar', font_size='16sp', bg_color=SUCCESS)
        btn_add.bind(on_press=lambda x: setattr(self.manager, 'current', 'add_cattle'))
        
        btn_agenda = RoundedButton(text='📅 Agenda', font_size='16sp', bg_color=WARNING)
        btn_agenda.bind(on_press=lambda x: setattr(self.manager, 'current', 'agenda'))
        
        btn_chat = RoundedButton(text='⚡ Rápido', font_size='16sp', bg_color=PURPLE)
        btn_chat.bind(on_press=lambda x: setattr(self.manager, 'current', 'quick_log'))
        
        buttons_grid.add_widget(btn_list)
        buttons_grid.add_widget(btn_add)
        buttons_grid.add_widget(btn_agenda)
        buttons_grid.add_widget(btn_chat)
        
        self.layout.add_widget(buttons_grid)
        self.add_widget(self.layout)
    
    def on_enter(self):
        """Al entrar a la pantalla"""
        try:
            self.update_stats()
        except Exception as e:
            print(f"[ERROR] HomeScreen.update_stats: {e}")
    
    def create_stat_card(self, icon, title, value, subtitle=''):
        """Crear tarjeta de estadística"""
        card = StyledCard(orientation='horizontal', size_hint_y=None, height=70, padding=10, spacing=8)
        
        icon_label = Label(text=icon, font_size='28sp', size_hint_x=0.25, color=TEXT)
        
        content = BoxLayout(orientation='vertical')
        
        title_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
        title_label = Label(
            text=f'[color={title_color}]{title}[/color]',
            markup=True,
            font_size='11sp',
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        value_label = Label(
            text=f'[b]{value}[/b]',
            markup=True,
            font_size='20sp',
            halign='left',
            color=TEXT
        )
        value_label.bind(size=value_label.setter('text_size'))
        
        content.add_widget(title_label)
        content.add_widget(value_label)
        
        if subtitle:
            sub_label = Label(
                text=f'[color={title_color}]{subtitle}[/color]',
                markup=True,
                font_size='9sp',
                halign='left'
            )
            sub_label.bind(size=sub_label.setter('text_size'))
            content.add_widget(sub_label)
        
        card.add_widget(icon_label)
        card.add_widget(content)
        
        return card
    
    def update_stats(self):
        """Actualizar estadísticas"""
        self.stats_container.clear_widgets()
        
        try:
            db = App.get_running_app().db
            stats = db.get_statistics()
            
            self.stats_container.add_widget(self.create_stat_card('🐮', 'Total Vacas', stats.get('total_cattle', 0)))
            self.stats_container.add_widget(self.create_stat_card('🤰', 'Preñadas', stats.get('pregnant', 0), f"{stats.get('not_pregnant', 0)} sin cargar"))
            self.stats_container.add_widget(self.create_stat_card('⚠️', 'Próximas 60d', stats.get('near_birth_60', 0), 'A parir'))
            self.stats_container.add_widget(self.create_stat_card('🚫', 'Para Secar', stats.get('to_dry', 0), '60-90 días'))
            self.stats_container.add_widget(self.create_stat_card('👶', 'Partos 30d', stats.get('recent_births', 0), 'Recientes'))
            self.stats_container.add_widget(self.create_stat_card('📊', f'Año {datetime.now().year}', stats.get('births_this_year', 0), 'Partos'))
            # NUEVA TARJETA: % Partos/Año
            self.stats_container.add_widget(self.create_stat_card('📈', '% Partos/Año', f"{stats.get('birth_rate_annual', 0)}%", '2 años'))
            self.stats_container.add_widget(self.create_stat_card('⚖️', 'Peso Prom', f"{stats.get('avg_weight', 0)} kg"))
        except Exception as e:
            print(f"[ERROR] update_stats: {e}")


class CattleListScreen(Screen):
    """Pantalla de lista de ganado"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=0.1, spacing=5)
        btn_back = RoundedButton(text='← Inicio', size_hint_x=0.3, bg_color=CARD)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        
        # CAJA DE BÚSQUEDA MÁS GRANDE
        self.search_input = TextInput(
            hint_text='Buscar por arete o nombre...',
            multiline=False,
            size_hint_x=0.7,
            height=70,  # ← MÁS GRANDE
            background_color=CARD,
            foreground_color=TEXT,
            cursor_color=PRIMARY,
            hint_text_color=TEXT_DIM,
            padding=[15, 20],  # ← MÁS PADDING
            font_size='18sp'  # ← FUENTE MÁS GRANDE
        )
        self.search_input.bind(text=self.on_search)
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(self.search_input)
        self.layout.add_widget(top_bar)
        
        # Lista de ganado
        self.scroll = ScrollView(size_hint_y=0.9)
        self.cattle_container = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=5)
        self.cattle_container.bind(minimum_height=self.cattle_container.setter('height'))
        self.scroll.add_widget(self.cattle_container)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        """Al entrar a la pantalla"""
        self.load_cattle_list()
    
    def load_cattle_list(self, search_query=''):
        """Cargar lista de ganado"""
        self.cattle_container.clear_widgets()
        
        try:
            db = App.get_running_app().db
            cattle_list = db.search_cattle(search_query) if search_query else db.get_all_cattle()
            
            if not cattle_list:
                no_data = Label(
                    text='No hay vacas registradas',
                    size_hint_y=None,
                    height=70,
                    color=TEXT_DIM,
                    font_size='16sp'
                )
                self.cattle_container.add_widget(no_data)
                return
            
            for cattle in cattle_list:
                card = self.create_cattle_card(cattle)
                self.cattle_container.add_widget(card)
        except Exception as e:
            print(f"[ERROR] load_cattle_list: {e}")
    
    def create_cattle_card(self, cattle):
        """Crear tarjeta de vaca"""
        card = StyledCard(orientation='vertical', size_hint_y=None, height=120, padding=15, spacing=8)
        
        # Header con número y nombre
        header = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        
        tag_label = Label(
            text=f"[b]{cattle['tag_number']}[/b]",
            markup=True,
            font_size='22sp',
            color=PRIMARY,
            size_hint_x=0.4,
            halign='left'
        )
        tag_label.bind(size=tag_label.setter('text_size'))
        
        name_label = Label(
            text=cattle.get('name', 'Sin nombre'),
            font_size='18sp',
            color=TEXT,
            size_hint_x=0.6,
            halign='left'
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        header.add_widget(tag_label)
        header.add_widget(name_label)
        
        # Info
        info = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        
        if cattle['is_pregnant']:
            days_to_birth = calculate_days_to_birth(cattle.get('expected_birth_date'))
            if days_to_birth is not None:
                if days_to_birth < 0:
                    status_text = f"🚨 Vencida ({abs(days_to_birth)}d)"
                    status_color = DANGER
                elif days_to_birth <= 60:
                    status_text = f"⚠️ Faltan {days_to_birth} días para parir (283 días gestación)"
                    status_color = WARNING
                else:
                    status_text = f"🤰 Preñada - {days_to_birth}d"
                    status_color = SUCCESS
            else:
                status_text = "🤰 Preñada"
                status_color = SUCCESS
        else:
            status_text = "Sin cargar"
            status_color = TEXT_DIM
        
        status_hex = ''.join([f'{int(c*255):02x}' for c in status_color[:3]])
        status_label = Label(
            text=f"[color={status_hex}]{status_text}[/color]",
            markup=True,
            font_size='14sp',
            halign='left'
        )
        status_label.bind(size=status_label.setter('text_size'))
        
        info.add_widget(status_label)
        
        # Botón
        btn_detail = RoundedButton(
            text='Ver Detalles 🔍',
            size_hint_y=0.3,
            bg_color=PRIMARY,
            font_size='16sp'
        )
        btn_detail.bind(on_press=lambda x, cid=cattle['id']: self.view_detail(cid))
        
        card.add_widget(header)
        card.add_widget(info)
        card.add_widget(btn_detail)
        
        return card
    
    def view_detail(self, cattle_id):
        """Ver detalle de vaca"""
        detail_screen = self.manager.get_screen('cattle_detail')
        detail_screen.load_cattle(cattle_id)
        self.manager.current = 'cattle_detail'
    
    def on_search(self, instance, value):
        """Al escribir en búsqueda"""
        self.load_cattle_list(value)


class AddCattleScreen(Screen):
    """Pantalla para agregar ganado"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=0.08, spacing=5)
        btn_back = RoundedButton(text='← Atrás', size_hint_x=0.5, bg_color=CARD)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'cattle_list'))
        
        title_label = Label(
            text='[b]➕ Agregar Vaca[/b]',
            markup=True,
            size_hint_x=0.5,
            color=TEXT,
            font_size='18sp'
        )
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title_label)
        self.layout.add_widget(top_bar)
        
        # Formulario
        scroll = ScrollView(size_hint_y=0.82)
        form = GridLayout(cols=1, spacing=15, size_hint_y=None, padding=10)
        form.bind(minimum_height=form.setter('height'))
        
        # TODAS LAS CAJAS DE TEXTO MÁS GRANDES (height=70)
        
        form.add_widget(Label(
            text='🏷️ Número de Arete *',
            size_hint_y=None,
            height=35,
            color=TEXT,
            font_size='16sp',
            halign='left'
        ))
        self.tag_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=70,  # ← MÁS GRANDE
            background_color=CARD,
            foreground_color=TEXT,
            cursor_color=PRIMARY,
            padding=[15, 20],  # ← MÁS PADDING
            font_size='18sp'  # ← FUENTE MÁS GRANDE
        )
        form.add_widget(self.tag_input)
        
        form.add_widget(Label(
            text='📛 Nombre (opcional)',
            size_hint_y=None,
            height=35,
            color=TEXT,
            font_size='16sp',
            halign='left'
        ))
        self.name_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=70,  # ← MÁS GRANDE
            background_color=CARD,
            foreground_color=TEXT,
            cursor_color=PRIMARY,
            padding=[15, 20],
            font_size='18sp'
        )
        form.add_widget(self.name_input)
        
        form.add_widget(Label(
            text='📅 Fecha Nacimiento (AAAA-MM-DD)',
            size_hint_y=None,
            height=35,
            color=TEXT,
            font_size='16sp',
            halign='left'
        ))
        self.birth_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=70,  # ← MÁS GRANDE
            hint_text='2020-01-15',
            background_color=CARD,
            foreground_color=TEXT,
            hint_text_color=TEXT_DIM,
            cursor_color=PRIMARY,
            padding=[15, 20],
            font_size='18sp'
        )
        form.add_widget(self.birth_input)
        
        form.add_widget(Label(
            text='⚖️ Peso (kg)',
            size_hint_y=None,
            height=35,
            color=TEXT,
            font_size='16sp',
            halign='left'
        ))
        self.weight_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=70,  # ← MÁS GRANDE
            hint_text='540',
            input_filter='float',
            background_color=CARD,
            foreground_color=TEXT,
            hint_text_color=TEXT_DIM,
            cursor_color=PRIMARY,
            padding=[15, 20],
            font_size='18sp'
        )
        form.add_widget(self.weight_input)
        
        form.add_widget(Label(
            text='📂 Categoría',
            size_hint_y=None,
            height=35,
            color=TEXT,
            font_size='16sp',
            halign='left'
        ))
        self.category_spinner = Spinner(
            text='Seleccionar',
            values=('Vaca', 'Vaquilla', 'Becerra', 'Otro'),
            size_hint_y=None,
            height=70,  # ← MÁS GRANDE
            background_color=CARD,
            color=TEXT,
            font_size='18sp'
        )
        form.add_widget(self.category_spinner)
        
        # ¿Está preñada?
        form.add_widget(Label(
            text='🤰 ¿Está preñada?',
            size_hint_y=None,
            height=35,
            color=TEXT,
            font_size='16sp',
            halign='left'
        ))
        
        pregnant_box = BoxLayout(size_hint_y=None, height=70, spacing=10)
        self.pregnant_yes = RoundedButton(text='Sí', bg_color=CARD)
        self.pregnant_no = RoundedButton(text='No', bg_color=PRIMARY)
        self.pregnant_yes.bind(on_press=self.toggle_pregnant_yes)
        self.pregnant_no.bind(on_press=self.toggle_pregnant_no)
        pregnant_box.add_widget(self.pregnant_yes)
        pregnant_box.add_widget(self.pregnant_no)
        form.add_widget(pregnant_box)
        
        self.is_pregnant = False
        
        # Campos de embarazo (ocultos inicialmente)
        self.pregnancy_fields = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=[0, 10])
        self.pregnancy_fields.bind(minimum_height=self.pregnancy_fields.setter('height'))
        
        self.pregnancy_fields.add_widget(Label(
            text='📅 Fecha Carga (AAAA-MM-DD)',
            size_hint_y=None,
            height=35,
            color=TEXT,
            font_size='16sp',
            halign='left'
        ))
        self.pregnancy_date_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=70,  # ← MÁS GRANDE
            hint_text='2024-06-01',
            background_color=CARD,
            foreground_color=TEXT,
            hint_text_color=TEXT_DIM,
            cursor_color=PRIMARY,
            padding=[15, 20],
            font_size='18sp'
        )
        self.pregnancy_date_input.bind(text=self.calculate_expected_birth)
        self.pregnancy_fields.add_widget(self.pregnancy_date_input)
        
        self.pregnancy_fields.add_widget(Label(
            text='👶 Fecha Parto Esperado',
            size_hint_y=None,
            height=35,
            color=TEXT,
            font_size='16sp',
            halign='left'
        ))
        self.expected_birth_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=70,  # ← MÁS GRANDE
            background_color=CARD,
            foreground_color=TEXT,
            cursor_color=PRIMARY,
            padding=[15, 20],
            font_size='18sp',
            disabled=True
        )
        self.pregnancy_fields.add_widget(self.expected_birth_input)
        
        form.add_widget(self.pregnancy_fields)
        self.pregnancy_fields.opacity = 0
        self.pregnancy_fields.disabled = True
        
        # Último parto
        form.add_widget(Label(
            text='🐄 Último Parto (AAAA-MM-DD)',
            size_hint_y=None,
            height=35,
            color=TEXT,
            font_size='16sp',
            halign='left'
        ))
        self.last_birth_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=70,  # ← MÁS GRANDE
            hint_text='2024-01-15',
            background_color=CARD,
            foreground_color=TEXT,
            hint_text_color=TEXT_DIM,
            cursor_color=PRIMARY,
            padding=[15, 20],
            font_size='18sp'
        )
        form.add_widget(self.last_birth_input)
        
        # Notas
        form.add_widget(Label(
            text='📝 Notas',
            size_hint_y=None,
            height=35,
            color=TEXT,
            font_size='16sp',
            halign='left'
        ))
        self.notes_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=120,  # ← ÁREA DE TEXTO MÁS GRANDE
            background_color=CARD,
            foreground_color=TEXT,
            cursor_color=PRIMARY,
            padding=[15, 15],
            font_size='16sp'
        )
        form.add_widget(self.notes_input)
        
        scroll.add_widget(form)
        self.layout.add_widget(scroll)
        
        # Botón guardar
        btn_save = RoundedButton(
            text='💾 Guardar Vaca',
            size_hint_y=0.1,
            bg_color=SUCCESS,
            font_size='18sp'
        )
        btn_save.bind(on_press=self.save_cattle)
        self.layout.add_widget(btn_save)
        
        self.add_widget(self.layout)
    
    def toggle_pregnant_yes(self, instance):
        """Marcar como preñada"""
        self.is_pregnant = True
        self.pregnant_yes.bg_color = PRIMARY
        self.pregnant_no.bg_color = CARD
        self.pregnancy_fields.opacity = 1
        self.pregnancy_fields.disabled = False
    
    def toggle_pregnant_no(self, instance):
        """Marcar como no preñada"""
        self.is_pregnant = False
        self.pregnant_yes.bg_color = CARD
        self.pregnant_no.bg_color = PRIMARY
        self.pregnancy_fields.opacity = 0
        self.pregnancy_fields.disabled = True
    
    def calculate_expected_birth(self, instance, value):
        """Calcular fecha esperada de parto (283 días)"""
        if not value:
            return
        try:
            pregnancy_date = datetime.strptime(value, '%Y-%m-%d')
            expected_birth = pregnancy_date + timedelta(days=283)
            self.expected_birth_input.text = expected_birth.strftime('%Y-%m-%d')
        except:
            self.expected_birth_input.text = ''
    
    def save_cattle(self, instance):
        """Guardar vaca"""
        if not self.tag_input.text.strip():
            return
        
        data = {
            'tag_number': self.tag_input.text.strip(),
            'name': self.name_input.text.strip(),
            'birth_date': self.birth_input.text.strip() or None,
            'weight': float(self.weight_input.text) if self.weight_input.text else None,
            'category': self.category_spinner.text if self.category_spinner.text != 'Seleccionar' else None,
            'is_pregnant': 1 if self.is_pregnant else 0,
            'pregnancy_date': self.pregnancy_date_input.text.strip() if self.is_pregnant else None,
            'expected_birth_date': self.expected_birth_input.text.strip() if self.is_pregnant else None,
            'last_birth_date': self.last_birth_input.text.strip() or None,
            'notes': self.notes_input.text.strip() or None
        }
        
        try:
            db = App.get_running_app().db
            cattle_id = db.add_cattle(data)
            
            if cattle_id:
                # Limpiar campos
                self.tag_input.text = ''
                self.name_input.text = ''
                self.birth_input.text = ''
                self.weight_input.text = ''
                self.category_spinner.text = 'Seleccionar'
                self.pregnancy_date_input.text = ''
                self.expected_birth_input.text = ''
                self.last_birth_input.text = ''
                self.notes_input.text = ''
                
                self.toggle_pregnant_no(None)
                
                # Volver a lista
                self.manager.current = 'cattle_list'
        except Exception as e:
            print(f"[ERROR] save_cattle: {e}")


class CattleDetailScreen(Screen):
    """Pantalla de detalle de vaca"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cattle_id = None
        
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=0.08, spacing=5)
        btn_back = RoundedButton(text='← Lista', bg_color=CARD)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'cattle_list'))
        
        self.title_label = Label(
            text='[b]Detalle Vaca[/b]',
            markup=True,
            color=TEXT,
            font_size='18sp'
        )
        
        btn_delete = RoundedButton(text='🗑️ Eliminar', bg_color=DANGER, size_hint_x=0.4)
        btn_delete.bind(on_press=self.confirm_delete)
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(self.title_label)
        top_bar.add_widget(btn_delete)
        
        self.layout.add_widget(top_bar)
        
        # Contenido scrollable
        self.scroll = ScrollView(size_hint_y=0.92)
        self.content = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, padding=10)
        self.content.bind(minimum_height=self.content.setter('height'))
        
        self.scroll.add_widget(self.content)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)
    
    def load_cattle(self, cattle_id):
        """Cargar datos de la vaca"""
        self.cattle_id = cattle_id
        self.content.clear_widgets()
        
        try:
            db = App.get_running_app().db
            cattle_data = db.get_cattle_by_id(cattle_id)
            
            if not cattle_data:
                return
            
            # Tarjeta de información
            info_card = StyledCard(orientation='vertical', size_hint_y=None, height=250, padding=15, spacing=10)
            
            title = Label(
                text=f"[b]🐮 {cattle_data['tag_number']}[/b]\n{cattle_data.get('name', 'Sin nombre')}",
                markup=True,
                size_hint_y=0.25,
                font_size='24sp',
                color=PRIMARY
            )
            
            # Información
            info_text = f"""Categoría: {cattle_data.get('category', 'N/A')}
Edad: {calculate_age(cattle_data.get('birth_date'))}
Peso: {cattle_data.get('weight', 'N/A')} kg
Estado: {'🤰 PREÑADA' if cattle_data['is_pregnant'] else 'Sin cargar'}"""
            
            if cattle_data['is_pregnant'] and cattle_data.get('expected_birth_date'):
                days_to_birth = calculate_days_to_birth(cattle_data['expected_birth_date'])
                if days_to_birth is not None:
                    info_text += f"\nDías para parir: {days_to_birth}"
                    info_text += f"\nParto esperado: {cattle_data['expected_birth_date']}"
            
            if cattle_data.get('last_birth_date'):
                days_since = calculate_days_since(cattle_data['last_birth_date'])
                info_text += f"\nÚltimo parto: {cattle_data['last_birth_date']} ({days_since}d)"
            
            info_label = Label(
                text=info_text,
                size_hint_y=0.5,
                font_size='16sp',
                color=TEXT,
                halign='left'
            )
            info_label.bind(size=info_label.setter('text_size'))
            
            if cattle_data.get('notes'):
                notes_label = Label(
                    text=f"Notas: {cattle_data['notes']}",
                    size_hint_y=0.25,
                    font_size='14sp',
                    color=TEXT_DIM,
                    halign='left'
                )
                notes_label.bind(size=notes_label.setter('text_size'))
                info_card.add_widget(title)
                info_card.add_widget(info_label)
                info_card.add_widget(notes_label)
            else:
                info_card.add_widget(title)
                info_card.add_widget(info_label)
            
            self.content.add_widget(info_card)
            
            # Botones de acción
            actions_grid = GridLayout(cols=2, spacing=8, size_hint_y=None, height=180)
            
            btn_vaccinate = RoundedButton(text='💉 Vacunar', bg_color=PRIMARY, font_size='16sp')
            btn_vaccinate.bind(on_press=self.add_vaccination)
            
            btn_birth = RoundedButton(text='🐄 Registrar Parto', bg_color=SUCCESS, font_size='16sp')
            btn_birth.bind(on_press=self.register_birth)
            
            btn_dry = RoundedButton(text='🚫 Secar', bg_color=WARNING, font_size='16sp')
            btn_dry.bind(on_press=self.dry_cow)
            
            btn_pregnant = RoundedButton(text='🤰 Cargar', bg_color=PINK, font_size='16sp')
            btn_pregnant.bind(on_press=self.mark_pregnant)
            
            actions_grid.add_widget(btn_vaccinate)
            actions_grid.add_widget(btn_birth)
            actions_grid.add_widget(btn_dry)
            actions_grid.add_widget(btn_pregnant)
            
            self.content.add_widget(actions_grid)
            
            # Historial de vacunación
            vaccinations = db.get_vaccinations(cattle_id)
            
            if vaccinations:
                vacc_title = Label(
                    text='[b]HISTORIAL DE VACUNACIÓN[/b]',
                    markup=True,
                    size_hint_y=None,
                    height=35,
                    font_size='16sp',
                    color=INFO
                )
                self.content.add_widget(vacc_title)
                
                for vacc in vaccinations:
                    vacc_card = StyledCard(orientation='vertical', size_hint_y=None, height=80, padding=10, spacing=5)
                    
                    vacc_name = Label(
                        text=f"[b]{vacc['vaccine_name']}[/b] - {vacc['vaccination_date']}",
                        markup=True,
                        font_size='16sp',
                        color=TEXT,
                        halign='left'
                    )
                    vacc_name.bind(size=vacc_name.setter('text_size'))
                    
                    dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
                    vacc_next = Label(
                        text=f"[color={dim_color}]Próxima: {vacc.get('next_vaccination_date', 'N/A')}[/color]",
                        markup=True,
                        font_size='14sp',
                        halign='left'
                    )
                    vacc_next.bind(size=vacc_next.setter('text_size'))
                    
                    vacc_card.add_widget(vacc_name)
                    vacc_card.add_widget(vacc_next)
                    
                    self.content.add_widget(vacc_card)
        
        except Exception as e:
            print(f"[ERROR] load_cattle: {e}")
    
    def add_vaccination(self, instance):
        """Agregar vacunación"""
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        content.add_widget(Label(text='💉 Nueva Vacunación', font_size='18sp', size_hint_y=None, height=35))
        
        content.add_widget(Label(text='Nombre de la vacuna:', size_hint_y=None, height=30, halign='left'))
        vaccine_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=70,
            background_color=CARD,
            foreground_color=TEXT,
            font_size='18sp',
            padding=[15, 20]
        )
        content.add_widget(vaccine_input)
        
        content.add_widget(Label(text='Fecha (AAAA-MM-DD):', size_hint_y=None, height=30, halign='left'))
        date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=70,
            background_color=CARD,
            foreground_color=TEXT,
            font_size='18sp',
            padding=[15, 20]
        )
        content.add_widget(date_input)
        
        content.add_widget(Label(text='Días hasta próxima:', size_hint_y=None, height=30, halign='left'))
        interval_input = TextInput(
            text='180',
            multiline=False,
            size_hint_y=None,
            height=70,
            background_color=CARD,
            foreground_color=TEXT,
            input_filter='int',
            font_size='18sp',
            padding=[15, 20]
        )
        content.add_widget(interval_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        popup = Popup(title='Vacunación', content=content, size_hint=(0.9, 0.8))
        
        btn_save = RoundedButton(text='Guardar', bg_color=SUCCESS)
        def save_vacc(x):
            if vaccine_input.text and date_input.text:
                try:
                    vacc_date = datetime.strptime(date_input.text, '%Y-%m-%d')
                    interval = int(interval_input.text) if interval_input.text else 180
                    next_date = vacc_date + timedelta(days=interval)
                    
                    db = App.get_running_app().db
                    db.add_vaccination(
                        self.cattle_id,
                        vaccine_input.text,
                        date_input.text,
                        next_date.strftime('%Y-%m-%d'),
                        ''
                    )
                    db.add_activity_log(self.cattle_id, 'vaccination', f"Vacuna: {vaccine_input.text}")
                    
                    popup.dismiss()
                    self.load_cattle(self.cattle_id)
                except:
                    pass
        
        btn_save.bind(on_press=save_vacc)
        btn_cancel = RoundedButton(text='Cancelar', bg_color=CARD)
        btn_cancel.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_save)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def register_birth(self, instance):
        """Registrar parto"""
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        content.add_widget(Label(text='👶 Registrar Parto', font_size='18sp', size_hint_y=None, height=35))
        
        content.add_widget(Label(text='Fecha (AAAA-MM-DD):', size_hint_y=None, height=30, halign='left'))
        date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=70,
            background_color=CARD,
            foreground_color=TEXT,
            font_size='18sp',
            padding=[15, 20]
        )
        content.add_widget(date_input)
        
        content.add_widget(Label(text='Notas:', size_hint_y=None, height=30, halign='left'))
        notes_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=100,
            background_color=CARD,
            foreground_color=TEXT,
            font_size='16sp',
            padding=[15, 15]
        )
        content.add_widget(notes_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        popup = Popup(title='Parto', content=content, size_hint=(0.9, 0.7))
        
        btn_save = RoundedButton(text='Guardar', bg_color=SUCCESS)
        def save_birth(x):
            if date_input.text:
                try:
                    db = App.get_running_app().db
                    db.update_cattle(self.cattle_id, {
                        'is_pregnant': 0,
                        'last_birth_date': date_input.text,
                        'pregnancy_date': None,
                        'expected_birth_date': None
                    })
                    db.add_event(self.cattle_id, 'birth', date_input.text, notes_input.text)
                    db.add_activity_log(self.cattle_id, 'birth', 'Parto registrado')
                    
                    popup.dismiss()
                    self.load_cattle(self.cattle_id)
                except:
                    pass
        
        btn_save.bind(on_press=save_birth)
        btn_cancel = RoundedButton(text='Cancelar', bg_color=CARD)
        btn_cancel.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_save)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def dry_cow(self, instance):
        """Secar vaca"""
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        content.add_widget(Label(text='🚫 Secar Vaca', font_size='18sp', size_hint_y=None, height=35))
        
        content.add_widget(Label(text='Fecha (AAAA-MM-DD):', size_hint_y=None, height=30, halign='left'))
        date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=70,
            background_color=CARD,
            foreground_color=TEXT,
            font_size='18sp',
            padding=[15, 20]
        )
        content.add_widget(date_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        popup = Popup(title='Secado', content=content, size_hint=(0.9, 0.5))
        
        btn_save = RoundedButton(text='Guardar', bg_color=WARNING)
        def save_dry(x):
            if date_input.text:
                try:
                    db = App.get_running_app().db
                    db.add_event(self.cattle_id, 'drying', date_input.text, 'Vaca secada')
                    db.add_activity_log(self.cattle_id, 'drying', 'Vaca secada')
                    
                    popup.dismiss()
                    self.load_cattle(self.cattle_id)
                except:
                    pass
        
        btn_save.bind(on_press=save_dry)
        btn_cancel = RoundedButton(text='Cancelar', bg_color=CARD)
        btn_cancel.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_save)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def mark_pregnant(self, instance):
        """Marcar como preñada"""
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        content.add_widget(Label(text='🤰 Cargar Vaca', font_size='18sp', size_hint_y=None, height=35))
        
        content.add_widget(Label(text='Fecha carga (AAAA-MM-DD):', size_hint_y=None, height=30, halign='left'))
        preg_date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=70,
            background_color=CARD,
            foreground_color=TEXT,
            font_size='18sp',
            padding=[15, 20]
        )
        content.add_widget(preg_date_input)
        
        content.add_widget(Label(text='Parto esperado:', size_hint_y=None, height=30, halign='left'))
        expected_label = Label(
            text='',
            size_hint_y=None,
            height=35,
            font_size='18sp',
            color=SUCCESS
        )
        content.add_widget(expected_label)
        
        def update_expected(instance, value):
            if value:
                try:
                    preg_date = datetime.strptime(value, '%Y-%m-%d')
                    expected = preg_date + timedelta(days=283)
                    expected_label.text = expected.strftime('%Y-%m-%d')
                except:
                    expected_label.text = ''
        
        preg_date_input.bind(text=update_expected)
        update_expected(None, preg_date_input.text)
        
        btn_layout = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        popup = Popup(title='Cargar', content=content, size_hint=(0.9, 0.6))
        
        btn_save = RoundedButton(text='Guardar', bg_color=PINK)
        def save_pregnant(x):
            if preg_date_input.text and expected_label.text:
                try:
                    db = App.get_running_app().db
                    db.update_cattle(self.cattle_id, {
                        'is_pregnant': 1,
                        'pregnancy_date': preg_date_input.text,
                        'expected_birth_date': expected_label.text
                    })
                    db.add_activity_log(self.cattle_id, 'pregnancy', f'Preñada - Parto: {expected_label.text}')
                    
                    popup.dismiss()
                    self.load_cattle(self.cattle_id)
                except:
                    pass
        
        btn_save.bind(on_press=save_pregnant)
        btn_cancel = RoundedButton(text='Cancelar', bg_color=CARD)
        btn_cancel.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_save)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def confirm_delete(self, instance):
        """Confirmar eliminación"""
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        content.add_widget(Label(
            text='¿Estás seguro de eliminar esta vaca?\n\nEsta acción NO se puede deshacer.',
            font_size='16sp',
            color=DANGER
        ))
        
        btn_layout = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        popup = Popup(title='Confirmar', content=content, size_hint=(0.9, 0.4))
        
        btn_yes = RoundedButton(text='Sí, eliminar', bg_color=DANGER)
        def do_delete(x):
            try:
                db = App.get_running_app().db
                db.delete_cattle(self.cattle_id)
                popup.dismiss()
                self.manager.current = 'cattle_list'
            except:
                pass
        
        btn_yes.bind(on_press=do_delete)
        btn_no = RoundedButton(text='No, cancelar', bg_color=CARD)
        btn_no.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(btn_no)
        btn_layout.add_widget(btn_yes)
        content.add_widget(btn_layout)
        
        popup.open()


class AgendaScreen(Screen):
    """Pantalla de agenda (60 días)"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=0.08, spacing=5)
        btn_back = RoundedButton(text='← Inicio', bg_color=CARD)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        
        title = Label(
            text='[b]📅 Agenda (60 días)[/b]',
            markup=True,
            color=TEXT,
            font_size='18sp'
        )
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        
        self.layout.add_widget(top_bar)
        
        # Eventos
        self.scroll = ScrollView(size_hint_y=0.92)
        self.events_container = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, padding=10)
        self.events_container.bind(minimum_height=self.events_container.setter('height'))
        
        self.scroll.add_widget(self.events_container)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        """Al entrar a la pantalla"""
        self.load_events()
    
    def load_events(self):
        """Cargar eventos"""
        self.events_container.clear_widgets()
        
        try:
            db = App.get_running_app().db
            agenda = db.get_agenda_items()
            
            # Vencidas (crítico)
            if agenda['overdue']:
                self.events_container.add_widget(Label(
                    text='[b]🚨 VENCIDAS - CRÍTICO[/b]',
                    markup=True,
                    size_hint_y=None,
                    height=35,
                    font_size='16sp',
                    color=DANGER
                ))
                
                for cattle in agenda['overdue']:
                    days_overdue = abs(calculate_days_to_birth(cattle['expected_birth_date']))
                    card = self.create_event_card(
                        cattle,
                        f"🚨 {cattle['tag_number']} - Vencida",
                        f"Parto: {cattle['expected_birth_date']} ({days_overdue}d)",
                        DANGER
                    )
                    self.events_container.add_widget(card)
            
            # Para secar (60-90 días)
            if agenda['to_dry']:
                self.events_container.add_widget(Label(
                    text='[b]🚫 PARA SECAR (60-90 días)[/b]',
                    markup=True,
                    size_hint_y=None,
                    height=35,
                    font_size='16sp',
                    color=WARNING
                ))
                
                for cattle in agenda['to_dry']:
                    days_to_birth = calculate_days_to_birth(cattle['expected_birth_date'])
                    card = self.create_event_card(
                        cattle,
                        f"🚫 {cattle['tag_number']} - {cattle.get('name', 'Sin nombre')}",
                        f"Parto: {cattle['expected_birth_date']} ({days_to_birth}d)",
                        WARNING
                    )
                    self.events_container.add_widget(card)
            
            # Próximas a parir (0-60 días)
            if agenda['near_birth']:
                self.events_container.add_widget(Label(
                    text='[b]⚠️ PRÓXIMAS A PARIR (0-60 días)[/b]',
                    markup=True,
                    size_hint_y=None,
                    height=35,
                    font_size='16sp',
                    color=WARNING
                ))
                
                for cattle in agenda['near_birth']:
                    days_to_birth = calculate_days_to_birth(cattle['expected_birth_date'])
                    card = self.create_event_card(
                        cattle,
                        f"⚠️ {cattle['tag_number']} - {cattle.get('name', 'Sin nombre')}",
                        f"Parto: {cattle['expected_birth_date']} ({days_to_birth}d)",
                        WARNING
                    )
                    self.events_container.add_widget(card)
            
            # Partos recientes (30 días)
            if agenda['recent_births']:
                self.events_container.add_widget(Label(
                    text='[b]👶 PARTOS RECIENTES (30 días)[/b]',
                    markup=True,
                    size_hint_y=None,
                    height=35,
                    font_size='16sp',
                    color=SUCCESS
                ))
                
                for cattle in agenda['recent_births']:
                    days_since = calculate_days_since(cattle['last_birth_date'])
                    card = self.create_event_card(
                        cattle,
                        f"👶 {cattle['tag_number']} - {cattle.get('name', 'Sin nombre')}",
                        f"Parto: {cattle['last_birth_date']} ({days_since}d atrás)",
                        SUCCESS
                    )
                    self.events_container.add_widget(card)
            
            # Vacunas próximas
            if agenda['need_vaccine']:
                self.events_container.add_widget(Label(
                    text='[b]💉 VACUNACIONES PRÓXIMAS (30 días)[/b]',
                    markup=True,
                    size_hint_y=None,
                    height=35,
                    font_size='16sp',
                    color=INFO
                ))
                
                for cattle in agenda['need_vaccine']:
                    card = self.create_event_card(
                        cattle,
                        f"💉 {cattle['tag_number']} - {cattle.get('vaccine_name', 'Vacuna')}",
                        f"Próxima: {cattle.get('next_vaccination_date', 'N/A')}",
                        INFO
                    )
                    self.events_container.add_widget(card)
            
            # Sin eventos
            if not any(agenda.values()):
                self.events_container.add_widget(Label(
                    text='No hay eventos próximos',
                    size_hint_y=None,
                    height=70,
                    font_size='16sp',
                    color=TEXT_DIM
                ))
        
        except Exception as e:
            print(f"[ERROR] load_events: {e}")
    
    def create_event_card(self, cattle, title, subtitle, color):
        """Crear tarjeta de evento"""
        card = StyledCard(orientation='vertical', size_hint_y=None, height=80, padding=10, spacing=5)
        
        title_label = Label(
            text=f"[b]{title}[/b]",
            markup=True,
            font_size='16sp',
            color=color,
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
        subtitle_label = Label(
            text=f"[color={dim_color}]{subtitle}[/color]",
            markup=True,
            font_size='14sp',
            halign='left'
        )
        subtitle_label.bind(size=subtitle_label.setter('text_size'))
        
        card.add_widget(title_label)
        card.add_widget(subtitle_label)
        
        return card


class QuickLogScreen(Screen):
    """Pantalla de registro rápido"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=0.08, spacing=5)
        btn_back = RoundedButton(text='← Inicio', bg_color=CARD)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        
        title = Label(
            text='[b]⚡ Registro Rápido[/b]',
            markup=True,
            color=TEXT,
            font_size='18sp'
        )
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        
        self.layout.add_widget(top_bar)
        
        # Instrucciones
        dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
        instructions = Label(
            text=f'[color={dim_color}]Comandos: "vacuné 123", "secé 456", "parió 789", "cargué 101"[/color]',
            markup=True,
            size_hint_y=0.08,
            font_size='14sp'
        )
        self.layout.add_widget(instructions)
        
        # Log de actividades
        self.scroll = ScrollView(size_hint_y=0.72)
        self.log_container = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, padding=10)
        self.log_container.bind(minimum_height=self.log_container.setter('height'))
        
        self.scroll.add_widget(self.log_container)
        self.layout.add_widget(self.scroll)
        
        # Input
        input_box = BoxLayout(size_hint_y=0.12, spacing=5)
        
        # CAJA DE COMANDO MÁS GRANDE
        self.quick_input = TextInput(
            hint_text='Ej: vacuné 123',
            multiline=False,
            size_hint_x=0.7,
            height=70,  # ← MÁS GRANDE
            background_color=CARD,
            foreground_color=TEXT,
            hint_text_color=TEXT_DIM,
            cursor_color=PRIMARY,
            padding=[15, 20],  # ← MÁS PADDING
            font_size='18sp'  # ← FUENTE MÁS GRANDE
        )
        self.quick_input.bind(on_text_validate=self.process_command)
        
        btn_send = RoundedButton(text='Enviar', size_hint_x=0.3, bg_color=SUCCESS, font_size='16sp')
        btn_send.bind(on_press=self.process_command)
        
        input_box.add_widget(self.quick_input)
        input_box.add_widget(btn_send)
        
        self.layout.add_widget(input_box)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        """Al entrar a la pantalla"""
        self.load_activity_log()
    
    def load_activity_log(self):
        """Cargar log de actividades"""
        self.log_container.clear_widgets()
        
        try:
            db = App.get_running_app().db
            activities = db.get_activity_log(20)
            
            if not activities:
                dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
                self.log_container.add_widget(Label(
                    text=f'[color={dim_color}]Sin actividades recientes[/color]',
                    markup=True,
                    size_hint_y=None,
                    height=70,
                    font_size='16sp'
                ))
                return
            
            for activity in activities:
                activity_card = StyledCard(orientation='vertical', size_hint_y=None, height=70, padding=10, spacing=5)
                
                dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
                time_label = Label(
                    text=f"[color={dim_color}][{activity['activity_date'][:16]}][/color]",
                    markup=True,
                    font_size='12sp',
                    size_hint_y=0.3
                )
                
                desc_label = Label(
                    text=f"{activity['tag_number']} - {activity['description']}",
                    color=TEXT,
                    font_size='16sp',
                    size_hint_y=0.7
                )
                
                activity_card.add_widget(time_label)
                activity_card.add_widget(desc_label)
                
                self.log_container.add_widget(activity_card)
        
        except Exception as e:
            print(f"[ERROR] load_activity_log: {e}")
    
    def process_command(self, instance):
        """Procesar comando"""
        command = self.quick_input.text.strip().lower()
        
        if not command:
            return
        
        try:
            db = App.get_running_app().db
            
            # Extraer número de arete
            arete_match = re.search(r'(\d+)', command)
            if not arete_match:
                self.show_message('❌ No se encontró número de arete')
                return
            
            arete = arete_match.group(1)
            cattle_list = db.search_cattle(arete)
            if not cattle_list:
                self.show_message(f'❌ Vaca {arete} no encontrada')
                return
            
            cattle = cattle_list[0]
            cattle_id = cattle['id']
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Procesar comando
            if 'vacun' in command:
                db.add_vaccination(cattle_id, 'Vacuna general', today, today, 'Registro rápido')
                db.add_activity_log(cattle_id, 'vaccination', 'Vacunación registrada')
                self.show_message(f'✅ Vacunación registrada → {arete}')
            
            elif 'sec' in command:
                db.add_event(cattle_id, 'drying', today, 'Secado')
                db.add_activity_log(cattle_id, 'drying', 'Vaca secada')
                self.show_message(f'✅ Secado registrado → {arete}')
            
            elif 'pari' in command or 'naci' in command:
                db.update_cattle(cattle_id, {
                    'is_pregnant': 0,
                    'last_birth_date': today,
                    'pregnancy_date': None,
                    'expected_birth_date': None
                })
                db.add_event(cattle_id, 'birth', today, 'Parto')
                db.add_activity_log(cattle_id, 'birth', 'Parto registrado')
                self.show_message(f'✅ Parto registrado → {arete}')
            
            elif 'carg' in command or 'preñ' in command:
                expected_date = (datetime.now() + timedelta(days=283)).strftime('%Y-%m-%d')
                db.update_cattle(cattle_id, {
                    'is_pregnant': 1,
                    'pregnancy_date': today,
                    'expected_birth_date': expected_date
                })
                db.add_activity_log(cattle_id, 'pregnancy', f'Preñada (parto: {expected_date})')
                self.show_message(f'✅ Vaca cargada → {arete}')
            
            else:
                self.show_message('❌ Comando no reconocido')
                return
            
            self.quick_input.text = ''
            self.load_activity_log()
        
        except Exception as e:
            print(f"[ERROR] process_command: {e}")
            self.show_message(f'❌ Error: {str(e)}')
    
    def show_message(self, message):
        """Mostrar mensaje de resultado"""
        msg_card = StyledCard(orientation='horizontal', size_hint_y=None, height=70, padding=10)
        
        if '✅' in message:
            color = SUCCESS
        else:
            color = DANGER
        
        msg_label = Label(
            text=f'[b]{message}[/b]',
            markup=True,
            color=color,
            font_size='16sp'
        )
        msg_card.add_widget(msg_label)
        self.log_container.add_widget(msg_card, index=0)


# === APLICACIÓN PRINCIPAL ===

class CattleManagerApp(App):
    """Aplicación principal"""
    
    def build(self):
        try:
            print("[INFO] Iniciando aplicación...")
            self.db = Database()
            sm = ScreenManager()
            sm.add_widget(HomeScreen(name='home'))
            sm.add_widget(CattleListScreen(name='cattle_list'))
            sm.add_widget(AddCattleScreen(name='add_cattle'))
            sm.add_widget(CattleDetailScreen(name='cattle_detail'))
            sm.add_widget(AgendaScreen(name='agenda'))
            sm.add_widget(QuickLogScreen(name='quick_log'))
            print("[INFO] Aplicación iniciada correctamente")
            return sm
        except Exception as e:
            print(f"[FATAL ERROR] build: {e}")
            error_layout = BoxLayout(orientation='vertical', padding=20)
            error_layout.add_widget(Label(
                text=f'[b]Error Fatal:[/b]\n{str(e)}',
                markup=True,
                color=DANGER
            ))
            return error_layout


if __name__ == '__main__':
    try:
        print("[INFO] Lanzando CattleManagerApp...")
        CattleManagerApp().run()
    except Exception as e:
        print(f"[FATAL] Error al lanzar: {e}")
