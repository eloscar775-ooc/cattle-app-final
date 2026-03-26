[app]
title = CattlePRO Milk AI
package.name = cattlepro
package.domain = org.oscar775
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# REQUERIMIENTOS: Aquí es donde Kivy se instala para el APK
requirements = python3,kivy==2.3.0,pillow

orientation = portrait
fullscreen = 1

# CONFIGURACIÓN DE ANDROID (Esto corrige el error del SDK)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Para que no se detenga pidiendo permisos manuales
android.skip_update = False
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
