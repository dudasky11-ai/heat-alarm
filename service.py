# 백그라운드 감시: 앱 화면을 닫아도 30초마다 온도를 확인하고 알림을 보냄
import time

from jnius import autoclass
from plyer import notification, vibrator

from battery import get_battery
from heat import judge, should_alert

CHECK_SECONDS = 30  # 확인 간격(초)

service = autoclass("org.kivy.android.PythonService").mService
old_level = "정상"

while True:
    battery = get_battery(service)
    level, advice = judge(battery["temp"], battery["charging"])

    if should_alert(old_level, level):
        notification.notify(
            title=f"배터리 {battery['temp']:.1f}°C [{level}]",
            message=advice,
            app_name="폰 온도 알림",
        )
        if level == "위험":
            vibrator.vibrate(1)  # 1초 진동

    old_level = level
    time.sleep(CHECK_SECONDS)
