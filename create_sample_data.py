#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar datos de ejemplo a la base de datos
Útil para probar la aplicación sin tener que ingresar datos manualmente
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

# Ruta de la base de datos
db_path = os.path.join(os.path.expanduser('~'), 'cattle_manager.db')

def create_sample_data():
    """Crear datos de ejemplo"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Limpiar datos existentes (opcional)
    print("¿Deseas limpiar la base de datos existente? (s/n): ", end='')
    response = input().strip().lower()
    if response == 's':
        cursor.execute('DELETE FROM cattle')
        cursor.execute('DELETE FROM vaccination_history')
        cursor.execute('DELETE FROM events')
        cursor.execute('DELETE FROM activity_log')
        cursor.execute('DELETE FROM vaccination_config')
        print("✓ Base de datos limpiada")
    
    print("\nAgregando datos de ejemplo...")
    
    # Lista de nombres de ejemplo
    nombres = [
        'Manchita', 'Bonita', 'Lechera', 'Estrella', 'Princesa',
        'Margarita', 'Luna', 'Rosa', 'Negrita', 'Blanca',
        'Café', 'Canela', 'Miel', 'Dulce', 'Linda'
    ]
    
    categorias = ['Vaca', 'Vaquilla', 'Becerra']
    vacunas = ['Brucelosis', 'Rabia', 'Aftosa', 'IBR', 'Clostridiosis']
    
    # Crear 15 vacas de ejemplo
    cattle_ids = []
    for i in range(1, 16):
        tag_number = f"{100 + i}"
        name = nombres[i-1] if i <= len(nombres) else f"Vaca {i}"
        
        # Fecha de nacimiento aleatoria (1-8 años atrás)
        years_old = random.randint(1, 8)
        birth_date = (datetime.now() - timedelta(days=years_old*365 + random.randint(0, 364))).strftime('%Y-%m-%d')
        
        # Peso aleatorio según categoría
        category = random.choice(categorias)
        if category == 'Becerra':
            weight = random.randint(150, 250)
        elif category == 'Vaquilla':
            weight = random.randint(300, 450)
        else:
            weight = random.randint(450, 650)
        
        # Estado de preñez (60% preñadas)
        is_pregnant = 1 if random.random() < 0.6 else 0
        pregnancy_date = None
        expected_birth_date = None
        last_birth_date = None
        
        if is_pregnant:
            # Fecha de carga entre 1-8 meses atrás
            pregnancy_days_ago = random.randint(30, 240)
            pregnancy_date = (datetime.now() - timedelta(days=pregnancy_days_ago)).strftime('%Y-%m-%d')
            
            # Fecha de parto esperado (283 días de gestación)
            expected_birth_date = (datetime.strptime(pregnancy_date, '%Y-%m-%d') + timedelta(days=283)).strftime('%Y-%m-%d')
        
        # Último parto (si no está preñada o tiene historial)
        if not is_pregnant or random.random() < 0.5:
            last_birth_days_ago = random.randint(60, 730)
            last_birth_date = (datetime.now() - timedelta(days=last_birth_days_ago)).strftime('%Y-%m-%d')
        
        notes = f"Vaca de ejemplo para pruebas del sistema"
        
        cursor.execute('''
            INSERT INTO cattle (tag_number, name, birth_date, weight, category,
                                is_pregnant, pregnancy_date, expected_birth_date,
                                last_birth_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tag_number, name, birth_date, weight, category, is_pregnant,
              pregnancy_date, expected_birth_date, last_birth_date, notes))
        
        cattle_id = cursor.lastrowid
        cattle_ids.append(cattle_id)
        print(f"✓ Agregada: {tag_number} - {name} ({category})")
        
        # Agregar vacunaciones aleatorias
        num_vaccinations = random.randint(1, 3)
        for _ in range(num_vaccinations):
            vaccine = random.choice(vacunas)
            days_ago = random.randint(30, 180)
            vacc_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            next_date = (datetime.now() + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO vaccination_history (cattle_id, vaccine_name, vaccination_date,
                                                 next_vaccination_date, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (cattle_id, vaccine, vacc_date, next_date, 'Vacunación de ejemplo'))
        
        # Agregar algunos eventos
        if last_birth_date:
            cursor.execute('''
                INSERT INTO events (cattle_id, event_type, event_date, notes)
                VALUES (?, ?, ?, ?)
            ''', (cattle_id, 'birth', last_birth_date, 'Parto registrado'))
        
        # Log de actividad
        cursor.execute('''
            INSERT INTO activity_log (cattle_id, activity_type, description)
            VALUES (?, ?, ?)
        ''', (cattle_id, 'registration', f'Vaca {tag_number} agregada al sistema'))
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ {len(cattle_ids)} vacas de ejemplo agregadas exitosamente!")
    print(f"✓ Base de datos: {db_path}")
    print("\nPuedes abrir la aplicación ahora y ver los datos de ejemplo.")
    print("Ejecuta: python3 main.py")

if __name__ == '__main__':
    print("============================================")
    print("  Generador de Datos de Ejemplo")
    print("  Gestión Ganadera")
    print("============================================\n")
    
    if os.path.exists(db_path):
        print(f"Base de datos encontrada: {db_path}")
    else:
        print(f"Se creará nueva base de datos: {db_path}")
    
    create_sample_data()
