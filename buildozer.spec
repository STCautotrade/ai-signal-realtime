[app]

title = AI SIGNAL REALTIME
package.name = aisignal
package.domain = org.stcautotrade

source.dir = .
source.include_exts = py,json,kv,png,jpg

# MAIN APP
entrypoint = main.py

version = 1.0

# ======================
# PYTHON REQUIREMENTS
# ======================
requirements = python3,kivy,requests

# ======================
# UI SETTINGS
# ======================
orientation = portrait
fullscreen = 0

# ======================
# ANDROID SETTINGS
# ======================
android.permissions = INTERNET,ACCESS_NETWORK_STATE

android.arch = arm64-v8a

android.api = 33
android.minapi = 21
android.ndk = 23b

android.accept_sdk_license = True

# ======================
# PERFORMANCE / STABILITY
# ======================
log_level = 2
warn_on_root = 0

# optional (lebih stabil di build server)
android.allow_backup = False
