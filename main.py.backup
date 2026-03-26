#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐄 CATTLE MANAGER PRO - Sistema Profesional de Gestión Ganadera
Versión Completa con Todas las Funcionalidades
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
from kivy.utils import get_color_from_hex
import sqlite3
import re

# === PALETA DE COLORES PROFESIONAL ===
BG = get_color_from_hex('#0a0e27')          # Fondo principal
CARD = get_color_from_hex('#1a1f3a')        # Tarjetas
PRIMARY = get_color_from_hex('#4c9aff')     # Azul principal
SUCCESS = get_color_from_hex('#36b37e')     # Verde éxito
WARNING = get_color_from_hex('#ffab00')     # Amarillo advertencia
DANGER = get_color_from_hex('#ff5630')      # Rojo peligro
INFO = get_color_from_hex('#00b8d9')        # Azul info
PURPLE = get_color_from_hex('#6554c0')      # Morado
PINK = get_color_from_hex('#ff79c6')        # Rosa
TEXT = get_color_from_hex('#e6edf3')        # Texto principal
TEXT_DIM = get_color_from_hex('#8c92a0')    # Texto secundario

Window.clearcolor = BG


# === COMPONENTES PERSONALIZADOS ===

class RoundedButton(Button):
    """Botón con bordes redondeados y colores personalizados"""
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
    """Tarjeta con fondo y bordes redondeados"""
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
        self.db_path = os.path.join(os.path.expanduser('~'), 'cattle_manager.db')
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializar todas las tablas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla principal de ganado
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
        
        # Historial de vacunación
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
        
        # Eventos (partos, secados, etc)
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
        
        # Log de actividades
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
        """Registrar vacunación"""
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
        """Obtener historial de vacunación"""
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
        """Registrar evento"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (cattle_id, event_type, event_date, notes)
            VALUES (?, ?, ?, ?)
        ''', (cattle_id, event_type, event_date, notes))
        conn.commit()
        conn.close()
    
    def get_events(self, cattle_id):
        """Obtener eventos de una vaca"""
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
        
        # Para secar (60-90 días)
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date BETWEEN ? AND ?
            ORDER BY expected_birth_date
        ''', (future_60, future_90))
        columns = [desc[0] for desc in cursor.description]
        agenda['to_dry'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Próximas a parir (0-60 días)
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date BETWEEN ? AND ?
            ORDER BY expected_birth_date
        ''', (today, future_60))
        agenda['near_birth'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Partos atrasados
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE is_pregnant = 1 
            AND expected_birth_date < ?
            ORDER BY expected_birth_date
        ''', (today,))
        agenda['overdue'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Partos recientes
        past_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT * FROM cattle 
            WHERE last_birth_date >= ?
            ORDER BY last_birth_date DESC
        ''', (past_30,))
        agenda['recent_births'] = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Vacunaciones próximas
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


# === PANTALLAS DE LA APLICACIÓN ===

class HomeScreen(Screen):
    """Pantalla principal con dashboard"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        title = Label(
            text='[b]🐄 Gestión Ganadera PRO[/b]',
            markup=True,
            font_size='26sp',
            color=TEXT
        )
        header.add_widget(title)
        self.layout.add_widget(header)
        
        # Stats container
        scroll = ScrollView(size_hint_y=0.5)
        self.stats_container = GridLayout(cols=2, spacing=10, size_hint_y=None, padding=5)
        self.stats_container.bind(minimum_height=self.stats_container.setter('height'))
        scroll.add_widget(self.stats_container)
        self.layout.add_widget(scroll)
        
        # Botones principales
        buttons_grid = GridLayout(cols=2, spacing=10, size_hint_y=0.4)
        
        btn_list = RoundedButton(text='📋 Ver Ganado', font_size='18sp', bg_color=PRIMARY)
        btn_list.bind(on_press=lambda x: setattr(self.manager, 'current', 'cattle_list'))
        
        btn_add = RoundedButton(text='➕ Agregar Vaca', font_size='18sp', bg_color=SUCCESS)
        btn_add.bind(on_press=lambda x: setattr(self.manager, 'current', 'add_cattle'))
        
        btn_agenda = RoundedButton(text='📅 Agenda', font_size='18sp', bg_color=WARNING)
        btn_agenda.bind(on_press=lambda x: setattr(self.manager, 'current', 'agenda'))
        
        btn_chat = RoundedButton(text='⚡ Registro Rápido', font_size='18sp', bg_color=PURPLE)
        btn_chat.bind(on_press=lambda x: setattr(self.manager, 'current', 'quick_log'))
        
        buttons_grid.add_widget(btn_list)
        buttons_grid.add_widget(btn_add)
        buttons_grid.add_widget(btn_agenda)
        buttons_grid.add_widget(btn_chat)
        
        self.layout.add_widget(buttons_grid)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.update_stats()
    
    def create_stat_card(self, icon, title, value, subtitle=''):
        """Crear tarjeta de estadística"""
        card = StyledCard(orientation='horizontal', size_hint_y=None, height=90, padding=15, spacing=10)
        
        icon_label = Label(text=icon, font_size='36sp', size_hint_x=0.25, color=TEXT)
        
        content = BoxLayout(orientation='vertical', spacing=2)
        
        # Título con color de texto secundario
        title_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
        title_label = Label(
            text=f'[color={title_color}]{title}[/color]',
            markup=True,
            font_size='13sp',
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        value_label = Label(
            text=f'[b][size=28]{value}[/size][/b]',
            markup=True,
            halign='left',
            valign='middle',
            color=TEXT
        )
        value_label.bind(size=value_label.setter('text_size'))
        
        content.add_widget(title_label)
        content.add_widget(value_label)
        
        if subtitle:
            subtitle_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
            subtitle_label = Label(
                text=f'[color={subtitle_color}][size=11]{subtitle}[/size][/color]',
                markup=True,
                halign='left',
                valign='middle'
            )
            subtitle_label.bind(size=subtitle_label.setter('text_size'))
            content.add_widget(subtitle_label)
        
        card.add_widget(icon_label)
        card.add_widget(content)
        
        return card
    
    def update_stats(self):
        """Actualizar estadísticas"""
        self.stats_container.clear_widgets()
        
        db = App.get_running_app().db
        stats = db.get_statistics()
        
        self.stats_container.add_widget(self.create_stat_card('🐮', 'Total Vacas', stats.get('total_cattle', 0)))
        self.stats_container.add_widget(self.create_stat_card('🤰', 'Preñadas', stats.get('pregnant', 0), f"{stats.get('not_pregnant', 0)} sin cargar"))
        self.stats_container.add_widget(self.create_stat_card('⚠️', 'Próximas 60d', stats.get('near_birth_60', 0), 'A parir'))
        self.stats_container.add_widget(self.create_stat_card('🚫', 'Para Secar', stats.get('to_dry', 0), '60-90 días'))
        self.stats_container.add_widget(self.create_stat_card('👶', 'Partos 30d', stats.get('recent_births', 0), 'Recientes'))
        self.stats_container.add_widget(self.create_stat_card('📊', f'Año {datetime.now().year}', stats.get('births_this_year', 0), 'Partos'))
        self.stats_container.add_widget(self.create_stat_card('💉', 'Vacunas 30d', stats.get('need_vaccine', 0), 'Próximas'))
        self.stats_container.add_widget(self.create_stat_card('⚖️', f'{stats.get("avg_weight", 0)} kg', 'Peso Promedio'))


class CattleListScreen(Screen):
    """Pantalla de lista de ganado"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Barra superior
        top_bar = BoxLayout(size_hint_y=0.1, spacing=10)
        
        btn_back = RoundedButton(text='← Inicio', size_hint_x=0.25, bg_color=CARD)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        
        self.search_input = TextInput(
            hint_text='Buscar por arete o nombre...',
            multiline=False,
            size_hint_x=0.75,
            background_color=CARD,
            foreground_color=TEXT,
            cursor_color=PRIMARY,
            hint_text_color=TEXT_DIM,
            padding=[15, 15]
        )
        self.search_input.bind(text=self.on_search)
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(self.search_input)
        self.layout.add_widget(top_bar)
        
        # Lista
        self.scroll = ScrollView(size_hint_y=0.9)
        self.cattle_container = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=5)
        self.cattle_container.bind(minimum_height=self.cattle_container.setter('height'))
        self.scroll.add_widget(self.cattle_container)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_cattle_list()
    
    def load_cattle_list(self, search_query=''):
        """Cargar lista de ganado"""
        self.cattle_container.clear_widgets()
        
        db = App.get_running_app().db
        cattle_list = db.search_cattle(search_query) if search_query else db.get_all_cattle()
        
        if not cattle_list:
            no_data = Label(
                text='No hay vacas registradas' if not search_query else 'No se encontraron resultados',
                size_hint_y=None,
                height=50,
                color=TEXT_DIM
            )
            self.cattle_container.add_widget(no_data)
            return
        
        for cattle in cattle_list:
            self.cattle_container.add_widget(self.create_cattle_card(cattle))
    
    def create_cattle_card(self, cattle):
        """Crear tarjeta de vaca"""
        card = StyledCard(orientation='vertical', size_hint_y=None, height=140, padding=15, spacing=8)
        
        # Header
        header = BoxLayout(size_hint_y=0.35, spacing=10)
        
        status_icon = '🤰' if cattle.get('is_pregnant') else '❌'
        icon_label = Label(text=status_icon, font_size='36sp', size_hint_x=0.15)
        
        info = BoxLayout(orientation='vertical', size_hint_x=0.85)
        
        title_label = Label(
            text=f"[b][size=20]{cattle['tag_number']}[/size][/b]  {cattle.get('name', 'Sin nombre')}",
            markup=True,
            halign='left',
            color=TEXT
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        age = self.calculate_age(cattle.get('birth_date'))
        dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
        category_label = Label(
            text=f"[color={dim_color}]{cattle.get('category', 'N/A')} • {age}[/color]",
            markup=True,
            halign='left',
            font_size='13sp'
        )
        category_label.bind(size=category_label.setter('text_size'))
        
        info.add_widget(title_label)
        info.add_widget(category_label)
        
        header.add_widget(icon_label)
        header.add_widget(info)
        card.add_widget(header)
        
        # Detalles
        details = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=3)
        
        if cattle.get('is_pregnant'):
            days_to_birth = self.calculate_days_to_birth(cattle.get('expected_birth_date'))
            if days_to_birth:
                if days_to_birth > 0:
                    detail_text = f"⏱️ Faltan [b]{days_to_birth}[/b] días para parir (283 días gestación)"
                    if days_to_birth <= 60:
                        warn_color = ''.join([f'{int(c*255):02x}' for c in WARNING[:3]])
                        detail_text = f"[color={warn_color}]{detail_text}[/color]"
                else:
                    danger_color = ''.join([f'{int(c*255):02x}' for c in DANGER[:3]])
                    detail_text = f"[color={danger_color}]⚠️ Ya pasó la fecha[/color]"
            else:
                dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
                detail_text = f"[color={dim_color}]Sin fecha de parto[/color]"
        else:
            days_since = self.calculate_days_since(cattle.get('last_birth_date'))
            dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
            if days_since:
                detail_text = f"[color={dim_color}]Último parto hace {days_since} días[/color]"
            else:
                detail_text = f"[color={dim_color}]Sin partos registrados[/color]"
        
        detail_label = Label(
            text=detail_text,
            markup=True,
            halign='left',
            font_size='12sp'
        )
        detail_label.bind(size=detail_label.setter('text_size'))
        details.add_widget(detail_label)
        
        card.add_widget(details)
        
        # Botón
        btn_view = RoundedButton(
            text='Ver Detalles →',
            size_hint_y=0.25,
            bg_color=PRIMARY
        )
        btn_view.bind(on_press=lambda x: self.view_cattle_detail(cattle['id']))
        card.add_widget(btn_view)
        
        return card
    
    def calculate_age(self, birth_date):
        """Calcular edad"""
        if not birth_date:
            return 'Edad desconocida'
        try:
            birth = datetime.strptime(birth_date, '%Y-%m-%d')
            today = datetime.now()
            years = today.year - birth.year
            months = today.month - birth.month
            if months < 0:
                years -= 1
                months += 12
            if years > 0:
                return f"{years}a {months}m"
            else:
                return f"{months} meses"
        except:
            return 'N/A'
    
    def calculate_days_to_birth(self, expected_date):
        """Calcular días para el parto"""
        if not expected_date:
            return None
        try:
            expected = datetime.strptime(expected_date, '%Y-%m-%d')
            today = datetime.now()
            return (expected - today).days
        except:
            return None
    
    def calculate_days_since(self, date):
        """Calcular días desde una fecha"""
        if not date:
            return None
        try:
            past = datetime.strptime(date, '%Y-%m-%d')
            today = datetime.now()
            return (today - past).days
        except:
            return None
    
    def view_cattle_detail(self, cattle_id):
        """Ver detalle de vaca"""
        detail_screen = self.manager.get_screen('cattle_detail')
        detail_screen.load_cattle(cattle_id)
        self.manager.current = 'cattle_detail'
    
    def on_search(self, instance, value):
        """Búsqueda en tiempo real"""
        self.load_cattle_list(value)


class AddCattleScreen(Screen):
    """Pantalla para agregar vaca"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cattle_id = None
        
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Barra superior
        top_bar = BoxLayout(size_hint_y=0.08, spacing=10)
        btn_back = RoundedButton(text='← Atrás', size_hint_x=0.3, bg_color=CARD)
        btn_back.bind(on_press=self.go_back)
        self.title_label = Label(text='[b]Agregar Vaca[/b]', markup=True, size_hint_x=0.7, color=TEXT)
        top_bar.add_widget(btn_back)
        top_bar.add_widget(self.title_label)
        self.layout.add_widget(top_bar)
        
        # Formulario
        scroll = ScrollView(size_hint_y=0.84)
        form = GridLayout(cols=1, spacing=12, size_hint_y=None, padding=10)
        form.bind(minimum_height=form.setter('height'))
        
        self.tag_input = self.create_input(form, '🏷️ Número de Arete *')
        self.name_input = self.create_input(form, '📛 Nombre (opcional)')
        self.birth_date_input = self.create_input(form, '🎂 Fecha Nacimiento (AAAA-MM-DD)')
        self.weight_input = self.create_input(form, '⚖️ Peso (kg)')
        
        # Categoría
        form.add_widget(Label(text='📂 Categoría', size_hint_y=None, height=30, color=TEXT))
        self.category_spinner = Spinner(
            text='Seleccionar',
            values=['Vaca', 'Vaquilla', 'Becerra', 'Novillo', 'Toro'],
            size_hint_y=None,
            height=45,
            background_color=CARD,
            color=TEXT
        )
        form.add_widget(self.category_spinner)
        
        # Estado de preñez
        form.add_widget(Label(text='🤰 ¿Está preñada?', size_hint_y=None, height=30, color=TEXT))
        self.pregnant_spinner = Spinner(
            text='No',
            values=['No', 'Sí'],
            size_hint_y=None,
            height=45,
            background_color=CARD,
            color=TEXT
        )
        self.pregnant_spinner.bind(text=self.on_pregnant_change)
        form.add_widget(self.pregnant_spinner)
        
        # Campos de preñez
        self.pregnancy_container = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None)
        self.pregnancy_container.height = 0
        self.pregnancy_container.opacity = 0
        
        self.pregnancy_date_input = self.create_input(self.pregnancy_container, '📅 Fecha de Carga')
        self.expected_birth_input = self.create_input(self.pregnancy_container, '👶 Parto Esperado (auto 283 días)')
        
        form.add_widget(self.pregnancy_container)
        
        self.last_birth_input = self.create_input(form, '🐄 Último Parto (AAAA-MM-DD)')
        
        # Notas
        form.add_widget(Label(text='📝 Notas', size_hint_y=None, height=30, color=TEXT))
        self.notes_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=100,
            background_color=CARD,
            foreground_color=TEXT
        )
        form.add_widget(self.notes_input)
        
        scroll.add_widget(form)
        self.layout.add_widget(scroll)
        
        # Botón guardar
        btn_save = RoundedButton(
            text='💾 Guardar',
            size_hint_y=0.08,
            font_size='18sp',
            bg_color=SUCCESS
        )
        btn_save.bind(on_press=self.save_cattle)
        self.layout.add_widget(btn_save)
        
        self.add_widget(self.layout)
    
    def create_input(self, container, label_text):
        """Crear campo de texto"""
        container.add_widget(Label(text=label_text, size_hint_y=None, height=30, color=TEXT))
        text_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=CARD,
            foreground_color=TEXT,
            cursor_color=PRIMARY,
            padding=[15, 12]
        )
        container.add_widget(text_input)
        return text_input
    
    def on_pregnant_change(self, spinner, text):
        """Mostrar/ocultar campos de preñez"""
        if text == 'Sí':
            self.pregnancy_container.height = 170
            self.pregnancy_container.opacity = 1
            if not self.pregnancy_date_input.text:
                self.pregnancy_date_input.text = datetime.now().strftime('%Y-%m-%d')
            if self.pregnancy_date_input.text:
                try:
                    preg_date = datetime.strptime(self.pregnancy_date_input.text, '%Y-%m-%d')
                    expected = preg_date + timedelta(days=283)
                    self.expected_birth_input.text = expected.strftime('%Y-%m-%d')
                except:
                    pass
        else:
            self.pregnancy_container.height = 0
            self.pregnancy_container.opacity = 0
    
    def save_cattle(self, instance):
        """Guardar vaca"""
        if not self.tag_input.text.strip():
            self.show_popup('❌ Error', 'El número de arete es obligatorio')
            return
        
        data = {
            'tag_number': self.tag_input.text.strip(),
            'name': self.name_input.text.strip(),
            'birth_date': self.birth_date_input.text.strip() or None,
            'weight': float(self.weight_input.text) if self.weight_input.text else None,
            'category': self.category_spinner.text if self.category_spinner.text != 'Seleccionar' else None,
            'is_pregnant': 1 if self.pregnant_spinner.text == 'Sí' else 0,
            'pregnancy_date': self.pregnancy_date_input.text.strip() or None,
            'expected_birth_date': self.expected_birth_input.text.strip() or None,
            'last_birth_date': self.last_birth_input.text.strip() or None,
            'notes': self.notes_input.text.strip()
        }
        
        db = App.get_running_app().db
        
        try:
            if self.cattle_id:
                db.update_cattle(self.cattle_id, data)
                message = '✅ Vaca actualizada'
            else:
                cattle_id = db.add_cattle(data)
                if cattle_id:
                    message = '✅ Vaca agregada'
                    db.add_activity_log(cattle_id, 'registration', f'Vaca {data["tag_number"]} agregada')
                else:
                    self.show_popup('❌ Error', 'El arete ya existe')
                    return
            
            self.show_popup('✅ Éxito', message, callback=self.go_back)
        except Exception as e:
            self.show_popup('❌ Error', f'Error: {str(e)}')
    
    def show_popup(self, title, message, callback=None):
        """Mostrar popup"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        content.add_widget(Label(text=message, color=TEXT))
        
        btn_ok = RoundedButton(text='OK', size_hint_y=None, height=50, bg_color=PRIMARY)
        content.add_widget(btn_ok)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.35),
            background_color=CARD
        )
        btn_ok.bind(on_press=popup.dismiss)
        
        if callback:
            popup.bind(on_dismiss=lambda x: callback(None))
        
        popup.open()
    
    def go_back(self, instance):
        """Volver atrás"""
        self.clear_form()
        self.manager.current = 'cattle_list'
    
    def clear_form(self):
        """Limpiar formulario"""
        self.cattle_id = None
        self.tag_input.text = ''
        self.name_input.text = ''
        self.birth_date_input.text = ''
        self.weight_input.text = ''
        self.category_spinner.text = 'Seleccionar'
        self.pregnant_spinner.text = 'No'
        self.pregnancy_date_input.text = ''
        self.expected_birth_input.text = ''
        self.last_birth_input.text = ''
        self.notes_input.text = ''


class CattleDetailScreen(Screen):
    """Pantalla de detalle de vaca"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cattle_id = None
        self.cattle_data = None
        
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Barra superior
        top_bar = BoxLayout(size_hint_y=0.08, spacing=5)
        btn_back = RoundedButton(text='← Lista', size_hint_x=0.5, bg_color=CARD)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'cattle_list'))
        
        btn_delete = RoundedButton(text='🗑 Eliminar', size_hint_x=0.5, bg_color=DANGER)
        btn_delete.bind(on_press=self.confirm_delete)
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(btn_delete)
        
        self.layout.add_widget(top_bar)
        
        # Contenido scrollable
        self.scroll = ScrollView(size_hint_y=0.92)
        self.content = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=10)
        self.content.bind(minimum_height=self.content.setter('height'))
        
        self.scroll.add_widget(self.content)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)
    
    def load_cattle(self, cattle_id):
        """Cargar datos de la vaca"""
        self.cattle_id = cattle_id
        self.content.clear_widgets()
        
        db = App.get_running_app().db
        self.cattle_data = db.get_cattle_by_id(cattle_id)
        
        if not self.cattle_data:
            self.content.add_widget(Label(text='Error: Vaca no encontrada', color=TEXT))
            return
        
        # Card de información
        info_card = StyledCard(orientation='vertical', size_hint_y=None, height=300, padding=15, spacing=8)
        
        title = Label(
            text=f"[b][size=24]🐮 {self.cattle_data['tag_number']}[/size][/b]\n{self.cattle_data.get('name', 'Sin nombre')}",
            markup=True,
            size_hint_y=0.25,
            color=TEXT
        )
        info_card.add_widget(title)
        
        info_text = f"""[b]Categoría:[/b] {self.cattle_data.get('category', 'N/A')}
[b]Edad:[/b] {self.calculate_age(self.cattle_data.get('birth_date'))}
[b]Peso:[/b] {self.cattle_data.get('weight', 'N/A')} kg
[b]Estado:[/b] {'🤰 PREÑADA' if self.cattle_data.get('is_pregnant') else '❌ NO PREÑADA'}
"""
        
        if self.cattle_data.get('is_pregnant'):
            days = self.calculate_days_to_birth(self.cattle_data.get('expected_birth_date'))
            info_text += f"\n[b]Días para parir:[/b] {days if days else 'N/A'}"
            info_text += f"\n[b]Parto esperado:[/b] {self.cattle_data.get('expected_birth_date', 'N/A')}"
        
        if self.cattle_data.get('last_birth_date'):
            days_since = self.calculate_days_since(self.cattle_data.get('last_birth_date'))
            info_text += f"\n[b]Último parto:[/b] {self.cattle_data.get('last_birth_date')}"
            info_text += f"\n[b]Días desde parto:[/b] {days_since if days_since else 'N/A'}"
        
        info_label = Label(
            text=info_text,
            markup=True,
            size_hint_y=0.75,
            color=TEXT
        )
        info_card.add_widget(info_label)
        
        self.content.add_widget(info_card)
        
        # Botones de acción
        actions_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=120)
        
        btn_vaccinate = RoundedButton(text='💉 Vacunar', bg_color=PRIMARY)
        btn_vaccinate.bind(on_press=self.add_vaccination)
        
        btn_birth = RoundedButton(text='🐄 Parto', bg_color=SUCCESS)
        btn_birth.bind(on_press=self.register_birth)
        
        btn_dry = RoundedButton(text='🚫 Secar', bg_color=WARNING)
        btn_dry.bind(on_press=self.dry_cow)
        
        btn_pregnant = RoundedButton(text='🤰 Cargar', bg_color=PINK)
        btn_pregnant.bind(on_press=self.mark_pregnant)
        
        actions_grid.add_widget(btn_vaccinate)
        actions_grid.add_widget(btn_birth)
        actions_grid.add_widget(btn_dry)
        actions_grid.add_widget(btn_pregnant)
        
        self.content.add_widget(actions_grid)
        
        # Historial de vacunación
        self.content.add_widget(Label(
            text='[b]HISTORIAL DE VACUNACIÓN[/b]',
            markup=True,
            size_hint_y=None,
            height=40,
            color=TEXT
        ))
        
        vaccinations = db.get_vaccinations(cattle_id)
        if vaccinations:
            for vacc in vaccinations[:5]:
                vacc_card = StyledCard(orientation='horizontal', size_hint_y=None, height=50, padding=10)
                vacc_label = Label(
                    text=f"{vacc['vaccine_name']} - {vacc['vaccination_date']}",
                    color=TEXT
                )
                vacc_card.add_widget(vacc_label)
                self.content.add_widget(vacc_card)
        else:
            dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
            self.content.add_widget(Label(
                text=f'[color={dim_color}]Sin vacunaciones[/color]',
                markup=True,
                size_hint_y=None,
                height=30
            ))
    
    def calculate_age(self, birth_date):
        """Calcular edad"""
        if not birth_date:
            return 'N/A'
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
            return 'N/A'
    
    def calculate_days_to_birth(self, expected_date):
        """Calcular días para parto"""
        if not expected_date:
            return None
        try:
            expected = datetime.strptime(expected_date, '%Y-%m-%d')
            return (expected - datetime.now()).days
        except:
            return None
    
    def calculate_days_since(self, date):
        """Calcular días desde fecha"""
        if not date:
            return None
        try:
            past = datetime.strptime(date, '%Y-%m-%d')
            return (datetime.now() - past).days
        except:
            return None
    
    def confirm_delete(self, instance):
        """Confirmar eliminación"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        content.add_widget(Label(text='¿Eliminar esta vaca?', color=TEXT))
        
        buttons = BoxLayout(spacing=10, size_hint_y=None, height=50)
        btn_yes = RoundedButton(text='Sí', bg_color=DANGER)
        btn_no = RoundedButton(text='No', bg_color=CARD)
        
        buttons.add_widget(btn_yes)
        buttons.add_widget(btn_no)
        content.add_widget(buttons)
        
        popup = Popup(title='Confirmar', content=content, size_hint=(0.8, 0.4), background_color=CARD)
        
        btn_yes.bind(on_press=lambda x: self.delete_cattle(popup))
        btn_no.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def delete_cattle(self, popup):
        """Eliminar vaca"""
        db = App.get_running_app().db
        db.delete_cattle(self.cattle_id)
        popup.dismiss()
        self.manager.current = 'cattle_list'
    
    def add_vaccination(self, instance):
        """Popup de vacunación"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        content.add_widget(Label(text='Nombre de la Vacuna:', size_hint_y=None, height=30, color=TEXT))
        vaccine_input = TextInput(
            hint_text='Ej: Brucelosis, Rabia, Aftosa...',
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=CARD,
            foreground_color=TEXT
        )
        content.add_widget(vaccine_input)
        
        content.add_widget(Label(text='Fecha:', size_hint_y=None, height=30, color=TEXT))
        date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=CARD,
            foreground_color=TEXT
        )
        content.add_widget(date_input)
        
        content.add_widget(Label(text='Próxima (días):', size_hint_y=None, height=30, color=TEXT))
        next_days_input = TextInput(
            text='30',
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=CARD,
            foreground_color=TEXT
        )
        content.add_widget(next_days_input)
        
        content.add_widget(Label(text='Notas:', size_hint_y=None, height=30, color=TEXT))
        notes_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=80,
            background_color=CARD,
            foreground_color=TEXT
        )
        content.add_widget(notes_input)
        
        buttons = BoxLayout(spacing=10, size_hint_y=None, height=50)
        btn_save = RoundedButton(text='💾 Guardar', bg_color=SUCCESS)
        btn_cancel = RoundedButton(text='❌ Cancelar', bg_color=DANGER)
        
        buttons.add_widget(btn_save)
        buttons.add_widget(btn_cancel)
        content.add_widget(buttons)
        
        popup = Popup(
            title='💉 Registrar Vacunación',
            content=content,
            size_hint=(0.9, 0.8),
            background_color=CARD
        )
        
        def save_vaccination(btn):
            if not vaccine_input.text.strip():
                return
            
            try:
                days = int(next_days_input.text)
            except:
                days = 30
            
            vacc_date = date_input.text.strip()
            next_date = (datetime.strptime(vacc_date, '%Y-%m-%d') + timedelta(days=days)).strftime('%Y-%m-%d')
            
            db = App.get_running_app().db
            db.add_vaccination(
                self.cattle_id,
                vaccine_input.text.strip(),
                vacc_date,
                next_date,
                notes_input.text.strip()
            )
            db.add_activity_log(
                self.cattle_id,
                'vaccination',
                f'Vacuna: {vaccine_input.text.strip()}'
            )
            
            popup.dismiss()
            self.load_cattle(self.cattle_id)
        
        btn_save.bind(on_press=save_vaccination)
        btn_cancel.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def register_birth(self, instance):
        """Popup de parto"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        content.add_widget(Label(
            text='¿Registrar el parto?\nEsto la marcará como NO PREÑADA',
            color=TEXT,
            size_hint_y=None,
            height=60
        ))
        
        content.add_widget(Label(text='Fecha:', size_hint_y=None, height=30, color=TEXT))
        date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=CARD,
            foreground_color=TEXT
        )
        content.add_widget(date_input)
        
        content.add_widget(Label(text='Notas:', size_hint_y=None, height=30, color=TEXT))
        notes_input = TextInput(
            hint_text='Ej: Becerro macho, parto normal...',
            multiline=True,
            size_hint_y=None,
            height=80,
            background_color=CARD,
            foreground_color=TEXT
        )
        content.add_widget(notes_input)
        
        buttons = BoxLayout(spacing=10, size_hint_y=None, height=50)
        btn_confirm = RoundedButton(text='✅ Confirmar', bg_color=SUCCESS)
        btn_cancel = RoundedButton(text='❌ Cancelar', bg_color=DANGER)
        
        buttons.add_widget(btn_confirm)
        buttons.add_widget(btn_cancel)
        content.add_widget(buttons)
        
        popup = Popup(
            title='🐄 Registrar Parto',
            content=content,
            size_hint=(0.9, 0.65),
            background_color=CARD
        )
        
        def confirm_birth(btn):
            db = App.get_running_app().db
            birth_date = date_input.text.strip()
            
            db.update_cattle(self.cattle_id, {
                'is_pregnant': 0,
                'last_birth_date': birth_date,
                'pregnancy_date': None,
                'expected_birth_date': None
            })
            db.add_event(self.cattle_id, 'birth', birth_date, notes_input.text.strip())
            db.add_activity_log(self.cattle_id, 'birth', f'Parto: {notes_input.text.strip()}')
            
            popup.dismiss()
            self.load_cattle(self.cattle_id)
        
        btn_confirm.bind(on_press=confirm_birth)
        btn_cancel.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def dry_cow(self, instance):
        """Popup de secado"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        content.add_widget(Label(
            text='¿Secar esta vaca?',
            color=TEXT,
            size_hint_y=None,
            height=40
        ))
        
        content.add_widget(Label(text='Fecha:', size_hint_y=None, height=30, color=TEXT))
        date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=CARD,
            foreground_color=TEXT
        )
        content.add_widget(date_input)
        
        content.add_widget(Label(text='Notas:', size_hint_y=None, height=30, color=TEXT))
        notes_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=80,
            background_color=CARD,
            foreground_color=TEXT
        )
        content.add_widget(notes_input)
        
        buttons = BoxLayout(spacing=10, size_hint_y=None, height=50)
        btn_confirm = RoundedButton(text='✅ Secar', bg_color=WARNING)
        btn_cancel = RoundedButton(text='❌ Cancelar', bg_color=DANGER)
        
        buttons.add_widget(btn_confirm)
        buttons.add_widget(btn_cancel)
        content.add_widget(buttons)
        
        popup = Popup(
            title='🚫 Secar Vaca',
            content=content,
            size_hint=(0.9, 0.6),
            background_color=CARD
        )
        
        def confirm_dry(btn):
            db = App.get_running_app().db
            dry_date = date_input.text.strip()
            
            db.add_event(self.cattle_id, 'drying', dry_date, notes_input.text.strip())
            db.add_activity_log(self.cattle_id, 'drying', f'Secado: {notes_input.text.strip()}')
            
            popup.dismiss()
            self.load_cattle(self.cattle_id)
        
        btn_confirm.bind(on_press=confirm_dry)
        btn_cancel.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def mark_pregnant(self, instance):
        """Popup marcar preñada"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        content.add_widget(Label(
            text='Marcar como PREÑADA',
            color=TEXT,
            size_hint_y=None,
            height=40,
            font_size='16sp',
            bold=True
        ))
        
        content.add_widget(Label(text='Fecha de Carga:', size_hint_y=None, height=30, color=TEXT))
        preg_date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=CARD,
            foreground_color=TEXT
        )
        content.add_widget(preg_date_input)
        
        content.add_widget(Label(
            text='Fecha de Parto Esperado:',
            size_hint_y=None,
            height=30,
            color=TEXT
        ))
        
        expected_date = (datetime.now() + timedelta(days=283)).strftime('%Y-%m-%d')
        expected_input = TextInput(
            text=expected_date,
            multiline=False,
            size_hint_y=None,
            height=45,
            background_color=CARD,
            foreground_color=TEXT
        )
        content.add_widget(expected_input)
        
        dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
        content.add_widget(Label(
            text=f'[color={dim_color}]Se calculan 283 días automáticamente[/color]',
            markup=True,
            size_hint_y=None,
            height=25,
            font_size='11sp'
        ))
        
        content.add_widget(Label(text='Notas:', size_hint_y=None, height=30, color=TEXT))
        notes_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height=80,
            background_color=CARD,
            foreground_color=TEXT
        )
        content.add_widget(notes_input)
        
        buttons = BoxLayout(spacing=10, size_hint_y=None, height=50)
        btn_confirm = RoundedButton(text='✅ Marcar Preñada', bg_color=PINK)
        btn_cancel = RoundedButton(text='❌ Cancelar', bg_color=DANGER)
        
        buttons.add_widget(btn_confirm)
        buttons.add_widget(btn_cancel)
        content.add_widget(buttons)
        
        popup = Popup(
            title='🤰 Marcar Preñada',
            content=content,
            size_hint=(0.9, 0.75),
            background_color=CARD
        )
        
        def auto_calculate(instance, value):
            """Auto-calcular fecha de parto"""
            try:
                preg_date = datetime.strptime(value, '%Y-%m-%d')
                expected = (preg_date + timedelta(days=283)).strftime('%Y-%m-%d')
                expected_input.text = expected
            except:
                pass
        
        preg_date_input.bind(text=auto_calculate)
        
        def confirm_pregnant(btn):
            db = App.get_running_app().db
            preg_date = preg_date_input.text.strip()
            expected_date = expected_input.text.strip()
            
            db.update_cattle(self.cattle_id, {
                'is_pregnant': 1,
                'pregnancy_date': preg_date,
                'expected_birth_date': expected_date
            })
            db.add_activity_log(
                self.cattle_id,
                'pregnancy',
                f'Marcada preñada. Parto: {expected_date}. {notes_input.text.strip()}'
            )
            
            popup.dismiss()
            self.load_cattle(self.cattle_id)
        
        btn_confirm.bind(on_press=confirm_pregnant)
        btn_cancel.bind(on_press=popup.dismiss)
        
        popup.open()


class AgendaScreen(Screen):
    """Pantalla de agenda"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Header
        top_bar = BoxLayout(size_hint_y=0.08, spacing=5)
        btn_back = RoundedButton(text='← Inicio', size_hint_x=0.5, bg_color=CARD)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        
        title = Label(text='[b]📅 Agenda (60 días)[/b]', markup=True, size_hint_x=0.5, color=TEXT)
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        
        self.layout.add_widget(top_bar)
        
        # Eventos
        self.scroll = ScrollView(size_hint_y=0.92)
        self.events_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=10)
        self.events_container.bind(minimum_height=self.events_container.setter('height'))
        
        self.scroll.add_widget(self.events_container)
        self.layout.add_widget(self.scroll)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_events()
    
    def load_events(self):
        """Cargar eventos"""
        self.events_container.clear_widgets()
        
        db = App.get_running_app().db
        agenda = db.get_agenda_items()
        
        # Partos atrasados (CRÍTICO)
        if agenda['overdue']:
            danger_color = ''.join([f'{int(c*255):02x}' for c in DANGER[:3]])
            self.events_container.add_widget(Label(
                text=f'[b][color={danger_color}]🚨 PARTOS ATRASADOS[/color][/b]',
                markup=True,
                size_hint_y=None,
                height=40
            ))
            for cattle in agenda['overdue']:
                card = self.create_agenda_card(cattle, DANGER)
                self.events_container.add_widget(card)
        
        # Para secar
        if agenda['to_dry']:
            warn_color = ''.join([f'{int(c*255):02x}' for c in WARNING[:3]])
            self.events_container.add_widget(Label(
                text=f'[b][color={warn_color}]🚫 PARA SECAR (60-90 días)[/color][/b]',
                markup=True,
                size_hint_y=None,
                height=40
            ))
            for cattle in agenda['to_dry']:
                card = self.create_agenda_card(cattle, WARNING)
                self.events_container.add_widget(card)
        
        # Próximas a parir
        if agenda['near_birth']:
            warn_color = ''.join([f'{int(c*255):02x}' for c in WARNING[:3]])
            self.events_container.add_widget(Label(
                text=f'[b][color={warn_color}]⚠️ PRÓXIMAS A PARIR (0-60 días)[/color][/b]',
                markup=True,
                size_hint_y=None,
                height=40
            ))
            for cattle in agenda['near_birth']:
                card = self.create_agenda_card(cattle, WARNING)
                self.events_container.add_widget(card)
        
        # Partos recientes
        if agenda['recent_births']:
            success_color = ''.join([f'{int(c*255):02x}' for c in SUCCESS[:3]])
            self.events_container.add_widget(Label(
                text=f'[b][color={success_color}]👶 PARTOS RECIENTES (30 días)[/color][/b]',
                markup=True,
                size_hint_y=None,
                height=40
            ))
            for cattle in agenda['recent_births']:
                card = self.create_agenda_card(cattle, SUCCESS)
                self.events_container.add_widget(card)
        
        # Vacunaciones próximas
        if agenda['need_vaccine']:
            info_color = ''.join([f'{int(c*255):02x}' for c in INFO[:3]])
            self.events_container.add_widget(Label(
                text=f'[b][color={info_color}]💉 VACUNACIONES PRÓXIMAS[/color][/b]',
                markup=True,
                size_hint_y=None,
                height=40
            ))
            for cattle in agenda['need_vaccine']:
                card = self.create_vaccine_card(cattle)
                self.events_container.add_widget(card)
        
        if not any(agenda.values()):
            dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
            self.events_container.add_widget(Label(
                text=f'[color={dim_color}]No hay eventos próximos[/color]',
                markup=True,
                size_hint_y=None,
                height=50
            ))
    
    def create_agenda_card(self, cattle, color):
        """Crear tarjeta de evento"""
        card = StyledCard(orientation='horizontal', size_hint_y=None, height=70, padding=15, spacing=10)
        
        info = BoxLayout(orientation='vertical')
        
        title = Label(
            text=f"[b]{cattle['tag_number']}[/b] - {cattle.get('name', 'Sin nombre')}",
            markup=True,
            halign='left',
            color=TEXT
        )
        title.bind(size=title.setter('text_size'))
        
        if cattle.get('expected_birth_date'):
            try:
                days = (datetime.strptime(cattle['expected_birth_date'], '%Y-%m-%d') - datetime.now()).days
                dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
                detail = Label(
                    text=f"[color={dim_color}]Parto: {cattle['expected_birth_date']} ({days} días)[/color]",
                    markup=True,
                    halign='left',
                    font_size='12sp'
                )
                detail.bind(size=detail.setter('text_size'))
            except:
                detail = None
        elif cattle.get('last_birth_date'):
            dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
            detail = Label(
                text=f"[color={dim_color}]Parió: {cattle['last_birth_date']}[/color]",
                markup=True,
                halign='left',
                font_size='12sp'
            )
            detail.bind(size=detail.setter('text_size'))
        else:
            detail = None
        
        info.add_widget(title)
        if detail:
            info.add_widget(detail)
        
        card.add_widget(info)
        
        return card
    
    def create_vaccine_card(self, cattle):
        """Crear tarjeta de vacuna"""
        card = StyledCard(orientation='horizontal', size_hint_y=None, height=70, padding=15, spacing=10)
        
        info = BoxLayout(orientation='vertical')
        
        title = Label(
            text=f"[b]{cattle['tag_number']}[/b] - {cattle.get('vaccine_name', 'Vacuna')}",
            markup=True,
            halign='left',
            color=TEXT
        )
        title.bind(size=title.setter('text_size'))
        
        dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
        detail = Label(
            text=f"[color={dim_color}]Próxima: {cattle.get('next_vaccination_date', 'N/A')}[/color]",
            markup=True,
            halign='left',
            font_size='12sp'
        )
        detail.bind(size=detail.setter('text_size'))
        
        info.add_widget(title)
        info.add_widget(detail)
        
        card.add_widget(info)
        
        return card


class QuickLogScreen(Screen):
    """Pantalla de registro rápido"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Header
        top_bar = BoxLayout(size_hint_y=0.08, spacing=5)
        btn_back = RoundedButton(text='← Inicio', size_hint_x=0.5, bg_color=CARD)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        
        title = Label(text='[b]⚡ Registro Rápido[/b]', markup=True, size_hint_x=0.5, color=TEXT)
        
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        
        self.layout.add_widget(top_bar)
        
        # Instrucciones
        dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
        instructions = Label(
            text=f'[color={dim_color}]Comandos: "vacuné 123", "secé 456", "parió 789", "cargué 101"[/color]',
            markup=True,
            size_hint_y=0.08,
            font_size='12sp'
        )
        self.layout.add_widget(instructions)
        
        # Log de actividades
        self.scroll = ScrollView(size_hint_y=0.7)
        self.log_container = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, padding=10)
        self.log_container.bind(minimum_height=self.log_container.setter('height'))
        
        self.scroll.add_widget(self.log_container)
        self.layout.add_widget(self.scroll)
        
        # Input
        input_box = BoxLayout(size_hint_y=0.1, spacing=5)
        
        self.quick_input = TextInput(
            hint_text='Escribe comando...',
            multiline=False,
            size_hint_x=0.75,
            background_color=CARD,
            foreground_color=TEXT,
            hint_text_color=TEXT_DIM
        )
        self.quick_input.bind(on_text_validate=self.process_command)
        
        btn_send = RoundedButton(text='Enviar', size_hint_x=0.25, bg_color=SUCCESS)
        btn_send.bind(on_press=self.process_command)
        
        input_box.add_widget(self.quick_input)
        input_box.add_widget(btn_send)
        
        self.layout.add_widget(input_box)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_activity_log()
    
    def load_activity_log(self):
        """Cargar log de actividades"""
        self.log_container.clear_widgets()
        
        db = App.get_running_app().db
        activities = db.get_activity_log(20)
        
        if not activities:
            dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
            self.log_container.add_widget(Label(
                text=f'[color={dim_color}]Sin actividades[/color]',
                markup=True,
                size_hint_y=None,
                height=50
            ))
            return
        
        for activity in activities:
            activity_card = StyledCard(orientation='vertical', size_hint_y=None, height=60, padding=10, spacing=5)
            
            dim_color = ''.join([f'{int(c*255):02x}' for c in TEXT_DIM[:3]])
            time_label = Label(
                text=f"[color={dim_color}][{activity['activity_date'][:16]}][/color]",
                markup=True,
                font_size='10sp',
                size_hint_y=0.3
            )
            
            desc_label = Label(
                text=f"{activity['tag_number']} - {activity['description']}",
                color=TEXT,
                size_hint_y=0.7
            )
            
            activity_card.add_widget(time_label)
            activity_card.add_widget(desc_label)
            
            self.log_container.add_widget(activity_card)
    
    def process_command(self, instance):
        """Procesar comando"""
        command = self.quick_input.text.strip().lower()
        
        if not command:
            return
        
        db = App.get_running_app().db
        
        # Extraer número
        arete_match = re.search(r'(\d+)', command)
        if not arete_match:
            self.show_message('❌ No se encontró número')
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
            self.show_message(f'✅ Vacunación → {arete}')
        
        elif 'sec' in command:
            db.add_event(cattle_id, 'drying', today, 'Secado')
            db.add_activity_log(cattle_id, 'drying', 'Vaca secada')
            self.show_message(f'✅ Secado → {arete}')
        
        elif 'pari' in command or 'naci' in command:
            db.update_cattle(cattle_id, {
                'is_pregnant': 0,
                'last_birth_date': today,
                'pregnancy_date': None,
                'expected_birth_date': None
            })
            db.add_event(cattle_id, 'birth', today, 'Parto')
            db.add_activity_log(cattle_id, 'birth', 'Parto registrado')
            self.show_message(f'✅ Parto → {arete}')
        
        elif 'carg' in command or 'preñ' in command:
            expected_date = (datetime.now() + timedelta(days=283)).strftime('%Y-%m-%d')
            db.update_cattle(cattle_id, {
                'is_pregnant': 1,
                'pregnancy_date': today,
                'expected_birth_date': expected_date
            })
            db.add_activity_log(cattle_id, 'pregnancy', f'Preñada (parto: {expected_date})')
            self.show_message(f'✅ Cargada → {arete}')
        
        else:
            self.show_message('❌ Comando no reconocido')
            return
        
        self.quick_input.text = ''
        self.load_activity_log()
    
    def show_message(self, message):
        """Mostrar mensaje"""
        msg_card = StyledCard(orientation='horizontal', size_hint_y=None, height=50, padding=10)
        
        if '✅' in message:
            color = SUCCESS
        else:
            color = DANGER
        
        msg_label = Label(
            text=f'[b]{message}[/b]',
            markup=True,
            color=color
        )
        msg_card.add_widget(msg_label)
        self.log_container.add_widget(msg_card, index=0)


# === APLICACIÓN PRINCIPAL ===

class CattleManagerApp(App):
    """Aplicación principal"""
    
    def build(self):
        self.db = Database()
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(CattleListScreen(name='cattle_list'))
        sm.add_widget(AddCattleScreen(name='add_cattle'))
        sm.add_widget(CattleDetailScreen(name='cattle_detail'))
        sm.add_widget(AgendaScreen(name='agenda'))
        sm.add_widget(QuickLogScreen(name='quick_log'))
        return sm


if __name__ == '__main__':
    CattleManagerApp().run()
