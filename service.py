# 백그라운드 감시: 앱 화면을 닫아도 30초마다 온도를 확인하고 알림을 보냄
import time

from jnius import autoclass
from plyer import notification, vibrator

from battery import get_battery
from heat import add_reading, guess_cause, judge, rise_per_minute, should_alert

CHECK_SECONDS = 30  # 확인 간격(초)

service = autoclass("org.kivy.android.PythonService").mService
old_level = "정상"
readings = []  # 최근 3분 동안의 (시각, 온도) 기록

while True:
    battery = get_battery(service)
    level, advice = judge(battery["temp"], battery["charging"])

    add_reading(readings, time.time(), battery["temp"])
    rise = rise_per_minute(readings)
    cause, solution = guess_cause(battery["temp"], battery["charging"], rise)

    if should_alert(old_level, level):
        notification.notify(
            title=f"배터리 {battery['temp']:.1f}°C [{level}]",
            message=f"{advice} (추정 원인: {cause})",
            app_name="폰 온도 알림",
        )
        if level == "위험":
            vibrator.vibrate(1)  # 1초 진동

    old_level = level
    time.sleep(CHECK_SECONDS)
