[app]

title = AI SIGNAL REALTIME

package.name = aisignal
package.domain = org.stcautotrade

source.dir = .
source.include_exts = py,json,png,jpg,kv

version = 1.0.0

# ======================
# REQUIREMENTS
# ======================
requirements = python3,kivy,requests,urllib3,certifi,setuptools,wheel

# ======================
# APP SETTINGS
# ======================
orientation = portrait
fullscreen = 0

# ======================
# ANDROID SETTINGS
# ======================
android.permissions = INTERNET

android.api = 33
android.minapi = 21

android.archs = arm64-v8a

android.accept_sdk_license = True
android.allow_backup = True

android.logcat_filters = *:S python:D

# ======================
# BUILD OPTIONS
# ======================
[buildozer]

log_level = 2
warn_on_root = 0
