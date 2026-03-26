# 🐄 Gestión Ganadera - Sistema de Manejo de Ganado

Sistema completo de gestión ganadera con Python, Kivy y Buildozer para dispositivos móviles Android.

## 📋 Características

### ✅ Gestión de Ganado
- ✅ Registro completo de vacas (arete, nombre, edad, peso, foto)
- ✅ Categorización (Vaca, Vaquilla, Becerra, Novillo, Toro)
- ✅ Estado reproductivo (preñada/no preñada)
- ✅ Seguimiento de preñez y fechas de parto
- ✅ Historial de partos
- ✅ Búsqueda rápida por arete o nombre
- ✅ Edición y eliminación de registros

### 💉 Sistema de Vacunación
- ✅ Registro de vacunaciones con fechas
- ✅ Configuración personalizada por vaca
- ✅ Alertas de vacunaciones próximas
- ✅ Historial completo de vacunaciones

### 📅 Agenda Inteligente
- ✅ Partos próximos (30 días)
- ✅ Alertas de secado (2 meses antes del parto)
- ✅ Recordatorios de vacunación
- ✅ Vista organizada por tipo de evento

### 📊 Estadísticas
- ✅ Total de vacas en el hato
- ✅ Vacas por categoría
- ✅ Vacas preñadas vs no preñadas
- ✅ Próximas a parir
- ✅ Partos anuales
- ✅ Promedio de producción

### 💬 Registro Rápido (Chat)
- ✅ Comandos de texto simple
- ✅ "vacuné vaca 123" - Registra vacunación
- ✅ "secé vaca 456" - Marca como secada
- ✅ "parió vaca 789" - Registra parto
- ✅ "cargué vaca 101" - Marca como preñada
- ✅ Historial de actividades recientes

### 📷 Funcionalidades Adicionales
- ✅ Captura de fotos por vaca
- ✅ Notas personalizadas
- ✅ Base de datos SQLite local
- ✅ Interfaz intuitiva y responsive
- ✅ Modo offline completo

## 🚀 Instalación en Kali Linux

### Paso 1: Instalar dependencias del sistema

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y pip
sudo apt install -y python3 python3-pip python3-venv

# Instalar dependencias de Buildozer
sudo apt install -y \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    libsqlite3-dev \
    python3-dev \
    build-essential \
    ccache

# Instalar Cython
pip3 install --user cython==0.29.36
```

### Paso 2: Configurar el entorno de Python

```bash
# Crear entorno virtual
cd ~
python3 -m venv cattle_env

# Activar entorno virtual
source ~/cattle_env/bin/activate

# Actualizar pip
pip install --upgrade pip setuptools wheel

# Instalar Kivy
pip install kivy[base]==2.3.0

# Instalar Buildozer
pip install buildozer
```

### Paso 3: Instalar Android SDK y NDK

```bash
# Crear directorio para Android
mkdir -p ~/.buildozer/android/platform

# Buildozer descargará automáticamente el SDK y NDK en la primera compilación
# O puedes descargarlos manualmente:

# SDK Command Line Tools
cd ~/.buildozer/android/platform
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip -d android-sdk
rm commandlinetools-linux-9477386_latest.zip

# Configurar variables de entorno (agregar a ~/.bashrc)
echo 'export ANDROID_HOME=$HOME/.buildozer/android/platform/android-sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools' >> ~/.bashrc
source ~/.bashrc
```

### Paso 4: Descargar y preparar el proyecto

```bash
# Copiar el proyecto a tu directorio
# (Asegúrate de copiar main.py y buildozer.spec)
mkdir -p ~/cattle_manager
cd ~/cattle_manager

# Copiar los archivos main.py y buildozer.spec aquí

# Activar el entorno virtual si no está activo
source ~/cattle_env/bin/activate
```

### Paso 5: Probar localmente (opcional)

```bash
# Activar entorno virtual
source ~/cattle_env/bin/activate

# Ejecutar la app en tu PC
cd ~/cattle_manager
python3 main.py

# Presiona Ctrl+C para salir
```

## 📱 Compilar APK para Android

### Primera compilación (puede tardar 1-2 horas)

```bash
# Activar entorno virtual
source ~/cattle_env/bin/activate

# Ir al directorio del proyecto
cd ~/cattle_manager

# Inicializar buildozer (primera vez)
buildozer init

# Compilar APK en modo debug
buildozer android debug

# El APK estará en: bin/cattle_manager-1.0-arm64-v8a-debug.apk
```

### Compilaciones posteriores (más rápidas)

```bash
# Limpiar compilación anterior (opcional)
buildozer android clean

# Compilar
buildozer android debug

# Para compilar en modo release (APK optimizado)
buildozer android release
```

### Solución de problemas comunes

#### Error: "Java not found"
```bash
sudo apt install openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

#### Error: "Android SDK not found"
```bash
# Buildozer descargará el SDK automáticamente
# Si falla, verifica tu conexión a internet
```

#### Error: "Cython compilation failed"
```bash
pip install --upgrade cython==0.29.36
```

#### Error de permisos
```bash
# NO ejecutar buildozer como root
# Si hay problemas de permisos:
sudo chown -R $USER:$USER ~/.buildozer
```

#### Limpiar y empezar de nuevo
```bash
cd ~/cattle_manager
rm -rf .buildozer
buildozer android clean
buildozer android debug
```

## 📲 Instalar APK en Android

### Método 1: Cable USB

```bash
# Habilitar "Depuración USB" en tu teléfono Android
# Conectar teléfono por USB

# Instalar herramientas ADB
sudo apt install android-tools-adb

# Verificar conexión
adb devices

# Instalar APK
adb install -r bin/cattle_manager-1.0-arm64-v8a-debug.apk
```

### Método 2: Transferencia de archivo

1. Copia el APK a tu teléfono usando USB, Bluetooth o email
2. En el teléfono, ve a Configuración → Seguridad
3. Habilita "Orígenes desconocidos" o "Instalar apps desconocidas"
4. Usa un explorador de archivos y toca el APK
5. Confirma la instalación

## 📖 Uso de la Aplicación

### Pantalla Principal (Dashboard)
- Muestra estadísticas generales del ganado
- Acceso rápido a todas las funciones
- Ver totales, categorías y alertas

### Ver Ganado
- Lista completa de todas las vacas
- Búsqueda por número de arete o nombre
- Toca cualquier vaca para ver detalles

### Agregar Vaca
- Campos obligatorios: Número de arete
- Opcionales: Nombre, fecha nacimiento, peso, foto
- Categoría: Vaca, Vaquilla, Becerra, etc.
- Estado reproductivo: Preñada/No preñada
- Si está preñada: Fecha de carga y parto esperado

### Detalle de Vaca
- Información completa
- Edad calculada automáticamente
- Días para parir (si está preñada)
- Días desde último parto
- Botones rápidos:
  - 💉 Registrar vacunación
  - 🐄 Registrar parto
  - 🚫 Secar vaca
  - 🤰 Marcar como preñada

### Agenda
- Eventos de los próximos 30 días
- Partos esperados
- Fechas de secado (60 días antes del parto)
- Vacunaciones pendientes
- Toca un evento para ver la vaca

### Registro Rápido (Chat)
- Comandos simples para registro veloz
- Ejemplos:
  - `vacuné vaca 123` o `vacune 123`
  - `secé vaca 456` o `seque 456`
  - `parió vaca 789` o `pario 789`
  - `cargué vaca 101` o `cargue 101`
- Historial de actividades recientes

## 🔧 Personalización

### Configurar Vacunación por Vaca

Cada vaca puede tener su propio esquema de vacunación:
- Frecuencia personalizada (cada X días)
- Momento específico (antes/después del parto)
- Múltiples tipos de vacunas

(Esta funcionalidad se expande en futuras versiones)

### Colores e Iconos

Edita `main.py` para cambiar colores:
```python
# Línea ~280 aprox - botón Ver Ganado
background_color=(0.2, 0.6, 0.8, 1)  # RGBA

# Experimenta con diferentes valores entre 0 y 1
```

## 📁 Estructura de la Base de Datos

La app usa SQLite con las siguientes tablas:

### `cattle` - Información de vacas
- id, tag_number, name, birth_date, weight
- category, photo_path, notes
- is_pregnant, pregnancy_date, expected_birth_date
- last_birth_date, created_at

### `vaccination_config` - Configuración de vacunas
- id, cattle_id, vaccine_name
- frequency_days, timing_type, timing_value

### `vaccination_history` - Historial de vacunaciones
- id, cattle_id, vaccine_name
- vaccination_date, next_vaccination_date, notes

### `events` - Eventos importantes
- id, cattle_id, event_type
- event_date, notes

### `activity_log` - Registro de actividades
- id, cattle_id, activity_type
- description, activity_date

### Ubicación de la base de datos:
- **Android**: `/storage/emulated/0/cattle_manager.db`
- **PC**: `~/cattle_manager.db`

## 🔄 Backup y Restauración

### Hacer backup (Android)
```bash
# Conectar teléfono por USB
adb pull /storage/emulated/0/cattle_manager.db ./backup.db
```

### Restaurar backup (Android)
```bash
adb push ./backup.db /storage/emulated/0/cattle_manager.db
```

## 🆕 Próximas Mejoras

- [ ] Gráficas de producción
- [ ] Exportar reportes a PDF/Excel
- [ ] Sincronización en la nube
- [ ] Modo multi-usuario
- [ ] Recordatorios push
- [ ] Códigos QR para aretes
- [ ] Integración con cámara mejorada
- [ ] Reportes financieros
- [ ] Genealogía del ganado

## 📞 Soporte

Para agregar funcionalidades o reportar problemas, documenta:
1. Versión de la app
2. Modelo de teléfono Android
3. Descripción del problema
4. Pasos para reproducirlo

## 📝 Licencia

Proyecto de código abierto para uso personal y comercial.

## 👨‍💻 Desarrollo

Desarrollado con:
- Python 3.10+
- Kivy 2.3.0
- SQLite3
- Buildozer

---

**¡Disfruta gestionando tu ganado de forma profesional! 🐮📱**
