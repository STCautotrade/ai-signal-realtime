[app]

title = AI SIGNAL REALTIME
package.name = aisignal
package.domain = org.stcautotrade

source.dir = .
source.include_exts = py,json,kv,png,jpg

# MAIN FILE
source.main = main.py

version = 1.0

requirements = python3,kivy,requests,urllib3,certifi

orientation = portrait
fullscreen = 0

# ======================
# ANDROID SETTINGS
# ======================

android.permissions = INTERNET

android.arch = arm64-v8a

android.api = 33
android.minapi = 21
android.ndk = 25b

android.accept_sdk_license = True

# ======================
# BUILD SETTINGS
# ======================

[buildozer]

log_level = 2
warn_on_root = 0
