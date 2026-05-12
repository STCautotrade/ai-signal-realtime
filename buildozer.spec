[app]

title = AI SIGNAL REALTIME

package.name = aisignal
package.domain = org.stcautotrade

source.dir = .
source.include_exts = py,json,kv,png,jpg

# main file (ini lebih benar daripada source.main)
entrypoint = main.py

version = 1.0

requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

# ======================
# ANDROID SETTINGS
# ======================

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
