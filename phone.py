# 폰(안드로이드)과 연결하는 부분
# 안드로이드가 정해 둔 이름과 방법을 그대로 불러다 쓰는 코드라서, 이 파일만 모아 둠
import os


# 1. 안드로이드 폰에서 실행 중인지 확인 (안드로이드는 이 값을 항상 갖고 있음)
def is_android():
    return "ANDROID_ROOT" in os.environ


# 2. 배터리 정보를 딕셔너리로 돌려줌. 폰이 아니면 None
def get_battery(in_service=False):
    if not is_android():
        return None

    from jnius import autoclass  # 안드로이드(자바) 기능을 파이썬에서 부르는 도구

    if in_service:  # 백그라운드 감시에서 부를 때
        context = autoclass("org.kivy.android.PythonService").mService
    else:           # 앱 화면에서 부를 때
        context = autoclass("org.kivy.android.PythonActivity").mActivity

    Intent = autoclass("android.content.Intent")
    IntentFilter = autoclass("android.content.IntentFilter")
    info = context.registerReceiver(None, IntentFilter(Intent.ACTION_BATTERY_CHANGED))

    return {
        "temp": info.getIntExtra("temperature", 0) / 10,  # 0.1°C 단위라서 10으로 나눔
        "level": info.getIntExtra("level", 0),            # 배터리 잔량(%)
        "charging": info.getIntExtra("plugged", 0) != 0,  # 0이 아니면 충전기 꽂힘
    }


# 3. 알림 권한을 묻고 백그라운드 감시(service.py)를 시작
def start_watch():
    from android.permissions import request_permissions
    from jnius import autoclass

    request_permissions(["android.permission.POST_NOTIFICATIONS"])
    activity = autoclass("org.kivy.android.PythonActivity").mActivity
    service = autoclass("com.dudasky11.heatalarm.ServiceHeatwatch")
    service.start(activity, "")
