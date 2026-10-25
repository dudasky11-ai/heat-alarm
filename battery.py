# 안드로이드에서 배터리 온도·잔량·충전 여부를 읽어 옴
import os


# 안드로이드 폰에서 실행 중인지 확인 (안드로이드는 이 환경 변수를 항상 갖고 있음)
def is_android():
    return "ANDROID_ROOT" in os.environ


# 배터리 정보를 딕셔너리로 돌려줌. 안드로이드가 아니면 None
def get_battery(context=None):
    if not is_android():
        return None

    from jnius import autoclass
    Intent = autoclass("android.content.Intent")
    IntentFilter = autoclass("android.content.IntentFilter")
    BatteryManager = autoclass("android.os.BatteryManager")

    # 화면(앱)에서 부르면 액티비티를, 백그라운드 감시에서 부르면 서비스를 씀
    if context is None:
        context = autoclass("org.kivy.android.PythonActivity").mActivity

    # 안드로이드가 마지막으로 보낸 "배터리 상태 변경" 소식을 받아 옴
    intent = context.registerReceiver(None, IntentFilter(Intent.ACTION_BATTERY_CHANGED))

    temp = intent.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) / 10  # 0.1°C 단위라서 10으로 나눔
    level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, 0)
    plugged = intent.getIntExtra(BatteryManager.EXTRA_PLUGGED, 0)        # 0이면 충전기 안 꽂음

    return {"temp": temp, "level": level, "charging": plugged != 0}
