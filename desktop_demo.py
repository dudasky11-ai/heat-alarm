#! python3.13
# 스마트폰 과열방지앱: 안드로이드 배터리 온도를 읽어 발열 단계와 원인을 알려주는 앱 (Kivy)
# 컴퓨터에서 실행하면 슬라이더로 온도를 흉내 내서 시연할 수 있음 (pip install kivy 필요)
import os

try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.core.text import LabelBase
    from kivy.core.window import Window
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.slider import Slider
except ImportError:  # Kivy가 없으면 창이 바로 닫히지 않게 안내하고 기다림
    print("Kivy가 설치되어 있지 않아요. 명령 프롬프트에서 pip install kivy 를 실행하세요.")
    input("Enter를 누르면 닫힙니다.")
    raise SystemExit


# 1. 온도와 충전 여부로 단계와 행동 요령을 정함
def judge(temp, charging):
    if temp >= 45:
        level = "위험"
        advice = "폰 사용을 멈추고 서늘한 곳에 두세요."
    elif temp >= 40:
        level = "주의"
        advice = "게임이나 영상을 잠시 멈추세요."
    elif temp >= 35:
        level = "따뜻함"
        advice = "햇빛이나 이불 위는 피하세요."
    else:
        level = "정상"
        advice = "괜찮아요."

    if charging and temp >= 40:
        advice = "충전기를 먼저 빼세요. " + advice

    return level, advice


# 2. 온도 기록에 새 온도를 넣고, 1분 동안 오른 온도를 돌려줌 (기록이 모자라면 None)
def one_minute_rise(temps, temp, count):
    temps.append(temp)
    if len(temps) > count:
        temps.pop(0)  # 가장 오래된 기록 지우기

    if len(temps) < count:
        return None
    return temps[-1] - temps[0]  # 지금 온도 - 1분 전 온도


# 3. 충전 여부와 1분 동안 오른 온도로 발열 원인을 추정
def guess_cause(temp, charging, rise):
    if temp < 35:
        return "없음", "지금은 괜찮아요."
    if rise is None:
        return "분석 중", "1분 뒤에 알려드릴게요."

    if charging and rise >= 1:
        return "충전하면서 사용", "충전 중에는 게임·영상을 멈추세요."
    if charging:
        return "충전 발열", "고속충전을 끄고 케이스를 벗긴 채 충전하세요."
    if rise >= 1:
        return "무거운 작업 (게임·촬영)", "앱을 끄고 화면 밝기를 낮추세요."
    return "주변 환경", "햇빛·이불 위를 피하고 케이스를 벗겨 보세요."


# 4. 단계별 글자 색 (빨강, 초록, 파랑, 투명도)
COLORS = {
    "정상": (0.3, 0.9, 0.4, 1),
    "따뜻함": (1.0, 0.85, 0.2, 1),
    "주의": (1.0, 0.55, 0.1, 1),
    "위험": (1.0, 0.2, 0.2, 1),
}


# 5. 안드로이드 폰인지 확인하고, 폰이면 배터리 정보를 딕셔너리로 돌려줌
def is_android():
    return "ANDROID_ROOT" in os.environ


def get_battery():
    if not is_android():
        return None

    from jnius import autoclass  # 안드로이드(자바) 기능을 파이썬에서 부르는 도구
    activity = autoclass("org.kivy.android.PythonActivity").mActivity
    Intent = autoclass("android.content.Intent")
    IntentFilter = autoclass("android.content.IntentFilter")
    info = activity.registerReceiver(None, IntentFilter(Intent.ACTION_BATTERY_CHANGED))

    return {
        "temp": info.getIntExtra("temperature", 0) / 10,  # 0.1°C 단위라서 10으로 나눔
        "level": info.getIntExtra("level", 0),            # 배터리 잔량(%)
        "charging": info.getIntExtra("plugged", 0) != 0,  # 0이 아니면 충전기 꽂힘
    }


# 6. 앱 화면
# 한글 글꼴 등록: 앱에 넣은 나눔고딕, 없으면 윈도우의 맑은 고딕
for font in ["NanumGothic-Regular.ttf", "C:/Windows/Fonts/malgun.ttf"]:
    if os.path.exists(font):
        LabelBase.register(name="Roboto", fn_regular=font)
        break


class HeatAlarmApp(App):
    def build(self):
        self.title = "스마트폰 과열방지앱"
        self.temps = []  # 최근 1분 동안의 온도 기록

        box = BoxLayout(orientation="vertical", padding=40)
        self.temp_label = Label(font_size="72sp")
        self.level_label = Label(font_size="36sp")
        self.info_label = Label(font_size="18sp", halign="center", text_size=(Window.width - 80, None))
        box.add_widget(self.temp_label)
        box.add_widget(self.level_label)
        box.add_widget(self.info_label)

        # 폰은 10초마다, 컴퓨터(시연용)는 1초마다 새로 고침
        if is_android():
            self.interval = 10
        else:
            self.interval = 1
            self.slider = Slider(min=20, max=55, value=30)  # 온도를 흉내 내는 슬라이더
            box.add_widget(self.slider)

        self.count = 60 // self.interval + 1  # 1분 동안 쌓이는 기록 개수
        Clock.schedule_interval(self.refresh, self.interval)
        return box

    def on_start(self):
        self.refresh(0)

    # 7. 온도를 읽어서 판정하고 화면에 표시
    def refresh(self, dt):
        battery = get_battery()
        if battery is None:  # 컴퓨터일 때
            battery = {"temp": self.slider.value, "level": 100, "charging": False}

        temp = battery["temp"]
        charging = battery["charging"]
        level, advice = judge(temp, charging)
        rise = one_minute_rise(self.temps, temp, self.count)
        cause, solution = guess_cause(temp, charging, rise)

        self.temp_label.text = f"{temp:.1f}°C"
        self.level_label.text = level
        self.level_label.color = COLORS[level]
        self.info_label.text = f"배터리 {battery['level']}%\n{advice}\n\n추정 원인: {cause}\n해결책: {solution}"


HeatAlarmApp().run()
