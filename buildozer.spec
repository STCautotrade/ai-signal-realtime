[app]

title = AI SIGNAL REALTIME

package.name = aisignal
package.domain = org.stcautotrade

source.dir = .
source.include_exts = py,json,png,jpg,kv

# MAIN FILE
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
# ANDROID SETTINGS (FIXED)
# ======================

android.permissions = INTERNET

android.api = 33
android.minapi = 21

# FIX NDK ERROR (WAJIB)
android.ndk = 27b

# FIX ARCH WARNING (WAJIB BARU)
android.archs = arm64-v8a

# ======================
# BUILD PERFORMANCE
# ======================

android.allow_backup = True
android.logcat_filters = *:S python:D

# ======================
# BUILD OPTIONS
# ======================

[buildozer]

log_level = 2
warn_on_root = 0
