[app]
title = 스마트폰 과열방지앱
package.name = heatalarm
package.domain = com.dudasky11
source.dir = .
source.include_exts = py,ttf
source.exclude_dirs = .github, bin, .buildozer
version = 0.1
requirements = python3,kivy==2.3.0,plyer,pyjnius
orientation = portrait
fullscreen = 0

# 백그라운드 감시 서비스 (service.py), 화면을 닫아도 계속 실행
services = Heatwatch:service.py:foreground

android.permissions = POST_NOTIFICATIONS,FOREGROUND_SERVICE,VIBRATE,WAKE_LOCK
android.api = 33
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True
android.ndk = 25b

# 빌드 도구를 검증된 안정 버전으로 고정 (최신 개발 버전은 부품 설치가 실패함)
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 0
