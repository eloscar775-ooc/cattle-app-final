# 🚀 GUÍA RÁPIDA DE INICIO

## Para usuarios con prisa

### Instalación en 3 comandos (Kali Linux):

```bash
# 1. Dar permisos al script
chmod +x install.sh

# 2. Ejecutar instalación automática
./install.sh

# 3. ¡Listo! Sigue las instrucciones en pantalla
```

---

## ¿Qué hace cada comando?

### Probar en tu PC (sin compilar):
```bash
source ~/cattle_env/bin/activate
cd ~/cattle_manager
python3 main.py
```

### Compilar APK para Android:
```bash
source ~/cattle_env/bin/activate
cd ~/cattle_manager
buildozer android debug
```

### Instalar en teléfono Android:
```bash
# Conecta tu teléfono con USB y habilita "Depuración USB"
adb install -r bin/cattle_manager-1.0-arm64-v8a-debug.apk
```

---

## Tiempos estimados:

- **Instalación de dependencias**: 10-15 minutos
- **Primera compilación de APK**: 1-2 horas (se descarga SDK de Android)
- **Compilaciones posteriores**: 5-10 minutos
- **Prueba en PC**: Instantáneo

---

## Solución rápida de problemas:

### "Command not found" al ejecutar buildozer
```bash
source ~/cattle_env/bin/activate
```

### Error de Java
```bash
sudo apt install openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

### Limpiar y empezar de nuevo la compilación
```bash
cd ~/cattle_manager
rm -rf .buildozer
buildozer android clean
buildozer android debug
```

### El APK no se instala en Android
1. Ve a Configuración → Seguridad
2. Habilita "Orígenes desconocidos"
3. Intenta instalar de nuevo

---

## Comandos útiles:

```bash
# Ver logs en tiempo real durante compilación
buildozer android debug 2>&1 | tee build.log

# Compilar solo para ARM64 (más rápido)
# Edita buildozer.spec y cambia:
# android.archs = arm64-v8a

# Ver dispositivos Android conectados
adb devices

# Ver logs de la app en Android
adb logcat | grep python
```

---

## Estructura del proyecto:

```
cattle_manager/
├── main.py              # Código principal de la app
├── buildozer.spec       # Configuración de compilación
├── requirements.txt     # Dependencias de Python
├── install.sh          # Script de instalación
├── README.md           # Documentación completa
├── QUICKSTART.md       # Esta guía
└── bin/                # APKs compilados (se crea automáticamente)
```

---

## Características principales de la app:

✅ **Dashboard** - Estadísticas del ganado en tiempo real
✅ **Lista de ganado** - Ver, buscar y organizar vacas
✅ **Detalles** - Información completa de cada vaca
✅ **Agregar/Editar** - Formularios completos con fotos
✅ **Agenda** - Eventos próximos (partos, vacunaciones, secado)
✅ **Registro rápido** - Comandos tipo chat para acciones rápidas
✅ **Offline** - Funciona sin internet
✅ **Base de datos** - SQLite local en el teléfono

---

## Comandos del chat de registro rápido:

- `vacuné vaca 123` → Registra vacunación
- `secé vaca 456` → Marca vaca como secada
- `parió vaca 789` → Registra parto
- `cargué vaca 101` → Marca como preñada

---

**¿Necesitas más ayuda?** Lee el README.md completo.

**¿Encontraste un bug?** Documenta qué pasó, qué esperabas, y cómo reproducirlo.

---

🐄 ¡Disfruta tu nueva app de gestión ganadera! 📱
