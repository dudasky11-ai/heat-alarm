# 폰 온도 알림 앱 화면
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider

from heat import COLORS, guess_cause, judge, one_minute_rise
from phone import get_battery, is_android, start_watch

# 한글 글꼴 등록 (Kivy 기본 글꼴에는 한글이 없음)
LabelBase.register(name="Roboto", fn_regular="NanumGothic-Regular.ttf")


class HeatAlarmApp(App):
    # 1. 화면 만들기: 온도, 단계, 설명을 위에서 아래로 쌓음
    def build(self):
        self.title = "폰 온도 알림"
        self.temps = []  # 최근 1분 동안의 온도 기록

        box = BoxLayout(orientation="vertical", padding=40)
        self.temp_label = Label(font_size="72sp")
        self.level_label = Label(font_size="36sp")
        self.info_label = Label(font_size="18sp", halign="center", text_size=(Window.width - 80, None))
        box.add_widget(self.temp_label)
        box.add_widget(self.level_label)
        box.add_widget(self.info_label)

        # 컴퓨터에서는 배터리 온도를 못 읽으니 슬라이더로 온도를 흉내 냄
        if not is_android():
            self.slider = Slider(min=20, max=55, value=30)
            box.add_widget(self.slider)

        Clock.schedule_interval(self.refresh, 10)  # 10초마다 refresh 실행
        return box

    # 2. 앱이 켜지면: 바로 한 번 표시하고, 폰이면 백그라운드 감시 시작
    def on_start(self):
        self.refresh(0)
        if is_android():
            start_watch()

    # 3. 온도를 읽어서 판정하고 화면에 표시
    def refresh(self, dt):
        battery = get_battery()
        if battery is None:  # 컴퓨터일 때
            battery = {"temp": self.slider.value, "level": 100, "charging": False}

        temp = battery["temp"]
        charging = battery["charging"]
        level, advice = judge(temp, charging)
        rise = one_minute_rise(self.temps, temp, 7)  # 10초마다 7개 = 1분
        cause, solution = guess_cause(temp, charging, rise)

        self.temp_label.text = f"{temp:.1f}°C"
        self.level_label.text = level
        self.level_label.color = COLORS[level]
        self.info_label.text = f"배터리 {battery['level']}%\n{advice}\n\n추정 원인: {cause}\n해결책: {solution}"


HeatAlarmApp().run()
