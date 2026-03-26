#!/bin/bash

# Script de instalación automática para Gestión Ganadera
# Para Kali Linux / Debian / Ubuntu

set -e  # Salir si hay error

echo "=============================================="
echo "  Instalador de Gestión Ganadera"
echo "  Sistema de Manejo de Ganado"
echo "=============================================="
echo ""

# Verificar que no sea root
if [ "$EUID" -eq 0 ]; then 
    echo "❌ ERROR: No ejecutes este script como root"
    echo "   Ejecuta: bash install.sh"
    exit 1
fi

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin color

# Función para imprimir con color
print_green() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_yellow() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_red() {
    echo -e "${RED}✗ $1${NC}"
}

# Verificar conexión a internet
echo "Verificando conexión a internet..."
if ping -c 1 google.com &> /dev/null; then
    print_green "Conexión a internet OK"
else
    print_red "No hay conexión a internet. Verifica tu conexión."
    exit 1
fi

# Actualizar sistema
echo ""
echo "Paso 1/7: Actualizando sistema..."
sudo apt update
print_green "Sistema actualizado"

# Instalar dependencias del sistema
echo ""
echo "Paso 2/7: Instalando dependencias del sistema..."
echo "Esto puede tardar varios minutos..."

sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
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
    ccache \
    android-tools-adb

print_green "Dependencias instaladas"

# Configurar Java
echo ""
echo "Paso 3/7: Configurando Java..."
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
print_green "Java configurado"

# Crear entorno virtual
echo ""
echo "Paso 4/7: Creando entorno virtual de Python..."
python3 -m venv ~/cattle_env
source ~/cattle_env/bin/activate

# Actualizar pip
pip install --upgrade pip setuptools wheel

# Instalar Cython
pip install cython==0.29.36
print_green "Cython instalado"

# Instalar Kivy
echo ""
echo "Paso 5/7: Instalando Kivy..."
echo "Esto puede tardar un momento..."
pip install "kivy[base]==2.3.0"
print_green "Kivy instalado"

# Instalar Buildozer
echo ""
echo "Paso 6/7: Instalando Buildozer..."
pip install buildozer
print_green "Buildozer instalado"

# Crear directorio del proyecto
echo ""
echo "Paso 7/7: Preparando proyecto..."
PROJECT_DIR="$HOME/cattle_manager"

if [ -d "$PROJECT_DIR" ]; then
    print_yellow "El directorio $PROJECT_DIR ya existe"
    read -p "¿Deseas sobrescribirlo? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf "$PROJECT_DIR"
        mkdir -p "$PROJECT_DIR"
    fi
else
    mkdir -p "$PROJECT_DIR"
fi

# Verificar que los archivos estén en el directorio actual
if [ -f "main.py" ] && [ -f "buildozer.spec" ]; then
    cp main.py "$PROJECT_DIR/"
    cp buildozer.spec "$PROJECT_DIR/"
    cp README.md "$PROJECT_DIR/" 2>/dev/null || true
    print_green "Archivos copiados a $PROJECT_DIR"
else
    print_yellow "Asegúrate de copiar main.py y buildozer.spec a $PROJECT_DIR"
fi

# Instrucciones finales
echo ""
echo "=============================================="
echo "  ✓ INSTALACIÓN COMPLETADA"
echo "=============================================="
echo ""
echo "📋 Siguiente pasos:"
echo ""
echo "1. Activa el entorno virtual:"
echo "   ${GREEN}source ~/cattle_env/bin/activate${NC}"
echo ""
echo "2. Ve al directorio del proyecto:"
echo "   ${GREEN}cd ~/cattle_manager${NC}"
echo ""
echo "3. Para probar en tu PC:"
echo "   ${GREEN}python3 main.py${NC}"
echo ""
echo "4. Para compilar APK (primera vez, tarda 1-2 horas):"
echo "   ${GREEN}buildozer android debug${NC}"
echo ""
echo "5. El APK estará en:"
echo "   ${GREEN}~/cattle_manager/bin/cattle_manager-1.0-arm64-v8a-debug.apk${NC}"
echo ""
echo "6. Para instalar en Android con USB:"
echo "   ${GREEN}adb install -r bin/cattle_manager-1.0-arm64-v8a-debug.apk${NC}"
echo ""
echo "=============================================="
echo ""
echo "📖 Lee el README.md para más información"
echo ""
echo "⚠️  IMPORTANTE: La primera compilación puede tardar 1-2 horas"
echo "    y descargará ~2GB de datos (Android SDK y NDK)"
echo ""
echo "¿Problemas? Verifica:"
echo "  • Conexión a internet estable"
echo "  • Espacio en disco (mínimo 10GB libres)"
echo "  • No ejecutar buildozer como root"
echo ""

# Preguntar si desea compilar ahora
read -p "¿Deseas compilar el APK ahora? (esto tardará 1-2 horas) (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo ""
    echo "Iniciando compilación..."
    echo "Presiona Ctrl+C si deseas cancelar"
    sleep 3
    
    cd "$PROJECT_DIR"
    source ~/cattle_env/bin/activate
    buildozer android debug
    
    if [ $? -eq 0 ]; then
        echo ""
        print_green "¡APK compilado exitosamente!"
        echo "Ubicación: $PROJECT_DIR/bin/"
        ls -lh "$PROJECT_DIR/bin/"*.apk
    else
        print_red "Error al compilar. Revisa los logs arriba."
    fi
else
    echo ""
    print_yellow "Puedes compilar después con: cd ~/cattle_manager && buildozer android debug"
fi

echo ""
print_green "¡Instalación completada! 🐄📱"
