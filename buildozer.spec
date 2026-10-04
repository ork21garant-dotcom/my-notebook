[app]
title = My Notebook
package.name = mynotebook
package.domain = org.myapp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,kivy,cryptography
orientation = portrait
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk_api = 21
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
