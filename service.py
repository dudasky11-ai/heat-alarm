# 백그라운드 감시: 앱을 닫아도 30초마다 온도를 확인하고 알림을 보냄
import time

from plyer import notification, vibrator

from heat import guess_cause, judge, one_minute_rise
from phone import get_battery

old_level = "정상"  # 지난번 단계
temps = []          # 최근 1분 동안의 온도 기록

while True:
    battery = get_battery(in_service=True)
    temp = battery["temp"]
    charging = battery["charging"]
    level, advice = judge(temp, charging)
    rise = one_minute_rise(temps, temp, 3)  # 30초마다 3개 = 1분
    cause, solution = guess_cause(temp, charging, rise)

    # 주의·위험 단계로 "새로" 올라갔을 때만 알림 (같은 알림이 계속 울리지 않게)
    if level in ("주의", "위험") and level != old_level:
        notification.notify(title=f"배터리 {temp:.1f}°C {level}", message=f"{advice} 원인: {cause}")
        if level == "위험":
            vibrator.vibrate(1)  # 1초 진동

    old_level = level
    time.sleep(30)  # 30초 쉬고 다시 확인
