#!/bin/bash

# Script de verificación del sistema para Gestión Ganadera
# Verifica que todas las dependencias estén instaladas correctamente

echo "=============================================="
echo "  Verificador de Sistema"
echo "  Gestión Ganadera"
echo "=============================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 instalado"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NO encontrado"
        ((ERRORS++))
        return 1
    fi
}

check_python_module() {
    if python3 -c "import $1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} Módulo Python $1 instalado"
        return 0
    else
        echo -e "${RED}✗${NC} Módulo Python $1 NO encontrado"
        ((ERRORS++))
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Archivo $1 existe"
        return 0
    else
        echo -e "${RED}✗${NC} Archivo $1 NO encontrado"
        ((ERRORS++))
        return 1
    fi
}

# Verificar comandos del sistema
echo "Verificando comandos del sistema..."
check_command python3
check_command pip3
check_command git
check_command java
check_command adb

echo ""
echo "Verificando versión de Python..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo "Python $PYTHON_VERSION"
if (( $(echo "$PYTHON_VERSION >= 3.8" | bc -l) )); then
    echo -e "${GREEN}✓${NC} Versión de Python adecuada (>= 3.8)"
else
    echo -e "${RED}✗${NC} Versión de Python muy antigua (necesitas >= 3.8)"
    ((ERRORS++))
fi

echo ""
echo "Verificando Java..."
if [ -z "$JAVA_HOME" ]; then
    echo -e "${YELLOW}⚠${NC} Variable JAVA_HOME no está configurada"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓${NC} JAVA_HOME = $JAVA_HOME"
fi

java -version 2>&1 | head -n 1

echo ""
echo "Verificando entorno virtual..."
if [ -d "$HOME/cattle_env" ]; then
    echo -e "${GREEN}✓${NC} Entorno virtual existe en ~/cattle_env"
    
    # Activar y verificar módulos
    source ~/cattle_env/bin/activate
    
    echo ""
    echo "Verificando módulos Python en el entorno virtual..."
    check_python_module kivy
    check_python_module buildozer
    check_python_module cython
    check_python_module PIL
    
    # Verificar versión de Kivy
    KIVY_VERSION=$(python3 -c "import kivy; print(kivy.__version__)" 2>/dev/null)
    if [ ! -z "$KIVY_VERSION" ]; then
        echo "Kivy versión: $KIVY_VERSION"
    fi
    
else
    echo -e "${RED}✗${NC} Entorno virtual NO encontrado en ~/cattle_env"
    echo "Ejecuta: python3 -m venv ~/cattle_env"
    ((ERRORS++))
fi

echo ""
echo "Verificando archivos del proyecto..."
PROJECT_DIR="$HOME/cattle_manager"
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${GREEN}✓${NC} Directorio del proyecto existe"
    cd "$PROJECT_DIR"
    
    check_file "main.py"
    check_file "buildozer.spec"
    check_file "README.md"
    
    # Verificar tamaño del archivo main.py
    if [ -f "main.py" ]; then
        SIZE=$(wc -l < main.py)
        echo "main.py tiene $SIZE líneas"
        if [ $SIZE -gt 100 ]; then
            echo -e "${GREEN}✓${NC} main.py parece completo"
        else
            echo -e "${YELLOW}⚠${NC} main.py parece incompleto"
            ((WARNINGS++))
        fi
    fi
else
    echo -e "${RED}✗${NC} Directorio del proyecto NO encontrado en $PROJECT_DIR"
    ((ERRORS++))
fi

echo ""
echo "Verificando espacio en disco..."
AVAILABLE=$(df -h ~ | awk 'NR==2 {print $4}')
echo "Espacio disponible en home: $AVAILABLE"
AVAILABLE_GB=$(df -BG ~ | awk 'NR==2 {print $4}' | sed 's/G//')
if [ $AVAILABLE_GB -lt 10 ]; then
    echo -e "${YELLOW}⚠${NC} Poco espacio en disco. Se recomiendan al menos 10GB"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓${NC} Espacio en disco suficiente"
fi

echo ""
echo "Verificando conexión a internet..."
if ping -c 1 google.com &> /dev/null; then
    echo -e "${GREEN}✓${NC} Conexión a internet OK"
else
    echo -e "${YELLOW}⚠${NC} No hay conexión a internet (necesaria para compilar)"
    ((WARNINGS++))
fi

echo ""
echo "Verificando dispositivos Android..."
if command -v adb &> /dev/null; then
    DEVICES=$(adb devices | grep -v "List" | grep "device" | wc -l)
    if [ $DEVICES -gt 0 ]; then
        echo -e "${GREEN}✓${NC} $DEVICES dispositivo(s) Android conectado(s)"
        adb devices
    else
        echo -e "${YELLOW}⚠${NC} No hay dispositivos Android conectados"
        echo "Esto es normal si aún no vas a instalar el APK"
    fi
else
    echo -e "${YELLOW}⚠${NC} ADB no está instalado"
fi

# Resumen
echo ""
echo "=============================================="
echo "  RESUMEN"
echo "=============================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ Todo está perfecto!${NC}"
    echo ""
    echo "Puedes proceder a:"
    echo "1. Probar en PC: cd ~/cattle_manager && python3 main.py"
    echo "2. Compilar APK: cd ~/cattle_manager && buildozer android debug"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Sistema funcional con $WARNINGS advertencia(s)${NC}"
    echo ""
    echo "Puedes continuar, pero revisa las advertencias arriba"
else
    echo -e "${RED}✗ Hay $ERRORS error(es) que necesitas corregir${NC}"
    echo ""
    echo "Soluciones sugeridas:"
    echo "1. Ejecuta el script de instalación: ./install.sh"
    echo "2. Activa el entorno virtual: source ~/cattle_env/bin/activate"
    echo "3. Instala dependencias manualmente: pip install -r requirements.txt"
fi

echo ""
echo "=============================================="

exit $ERRORS
