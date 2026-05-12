[app]

title = AI SIGNAL REALTIME

package.name = aisignal
package.domain = org.stcautotrade

source.dir = .
source.include_exts = py,json,png,jpg,kv

# MAIN FILE (INI YANG BENAR UNTUK BUILD)
entrypoint = main.py

version = 1.0.0

# ======================
# REQUIREMENTS
# ======================
requirements = python3,kivy,requests,urllib3,certifi

# ======================
# APP SETTINGS
# ======================
orientation = portrait
fullscreen = 0

# ======================
# ANDROID SETTINGS (FINAL STABLE FIX)
# ======================

android.permissions = INTERNET

android.api = 33
android.minapi = 21

# 🔥 LOCK VERSION (BIAR TIDAK AMBIL 37 LAGI)
android.sdk = 33
android.build_tools = 33.0.2
android.ndk = 25b

# ARCH STABLE (64-bit Android)
android.archs = arm64-v8a

# FIX LICENSE ERROR
android.accept_sdk_license = True

# OPTIONAL STABILITY SETTINGS
android.allow_backup = True
android.logcat_filters = *:S python:D

# ======================
# BUILD OPTIONS
# ======================
[buildozer]

log_level = 2
warn_on_root = 0
