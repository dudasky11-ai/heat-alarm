# 폰 온도 알림 앱: 배터리 온도를 보여주고, 백그라운드 감시를 켜고 끔
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider

from battery import get_battery, is_android
from heat import COLORS, judge

# 1. 한글 글꼴 등록 (Kivy 기본 글꼴에는 한글이 없음)
LabelBase.register(name="Roboto", fn_regular="NanumGothic-Regular.ttf")

SERVICE_CLASS = "com.dudasky11.heatalarm.ServiceHeatwatch"  # buildozer가 만들어 주는 서비스 이름


class HeatAlarmApp(App):
    # 2. 화면 만들기: 위에서 아래로 온도, 단계, 행동 요령, 버튼
    def build(self):
        self.title = "폰 온도 알림"
        root = BoxLayout(orientation="vertical", padding=40, spacing=20)

        self.temp_label = Label(text="--.-°C", font_size="72sp", bold=True)
        self.level_label = Label(text="확인 중...", font_size="32sp")
        self.info_label = Label(text="", font_size="18sp")
        self.advice_label = Label(text="", font_size="18sp", halign="center")
        self.advice_label.bind(width=self.wrap_text)  # 긴 문장을 화면 너비에서 줄바꿈

        self.watch_button = Button(text="백그라운드 감시 켜기", font_size="20sp", size_hint_y=0.25)
        self.watch_button.bind(on_press=self.toggle_watch)
        self.watching = False

        for w in (self.temp_label, self.level_label, self.info_label, self.advice_label):
            root.add_widget(w)

        # 컴퓨터에서 실행할 때는 배터리 온도를 못 읽으니 슬라이더로 온도를 흉내 냄
        self.test_slider = None
        if not is_android():
            self.test_slider = Slider(min=20, max=55, value=30, step=0.5, size_hint_y=0.2)
            root.add_widget(Label(text="[컴퓨터 테스트용] 온도 슬라이더", font_size="16sp", size_hint_y=0.1))
            root.add_widget(self.test_slider)

        root.add_widget(self.watch_button)

        # 배경색: 단계가 바뀔 때마다 색을 바꿈
        with root.canvas.before:
            self.bg_color = Color(*COLORS["정상"])
            self.bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)

        Clock.schedule_interval(self.refresh, 2)  # 앱이 켜져 있는 동안 2초마다 새로 고침
        return root

    def wrap_text(self, label, width):
        label.text_size = (width, None)

    def update_bg(self, widget, value):
        self.bg_rect.pos = widget.pos
        self.bg_rect.size = widget.size

    # 3. 앱이 처음 켜질 때: 알림 권한 요청 (안드로이드 13 이상은 꼭 필요)
    def on_start(self):
        if is_android():
            from android.permissions import request_permissions
            request_permissions(["android.permission.POST_NOTIFICATIONS"])

    # 4. 온도를 읽어서 화면에 표시
    def refresh(self, dt):
        battery = get_battery()
        if battery is None:  # 컴퓨터 테스트
            battery = {"temp": self.test_slider.value, "level": 100, "charging": False}

        level, advice = judge(battery["temp"], battery["charging"])
        charge_text = "충전 중" if battery["charging"] else "충전 안 함"

        self.temp_label.text = f"{battery['temp']:.1f}°C"
        self.level_label.text = f"[{level}]"
        self.info_label.text = f"배터리 {battery['level']}% · {charge_text}"
        self.advice_label.text = advice
        self.bg_color.rgba = COLORS[level]

    # 5. 버튼: 백그라운드 감시(service.py) 켜기/끄기
    def toggle_watch(self, button):
        if not is_android():
            button.text = "백그라운드 감시는 폰에서만 돼요"
            return

        from jnius import autoclass
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        service = autoclass(SERVICE_CLASS)

        if self.watching:
            service.stop(activity)
            button.text = "백그라운드 감시 켜기"
        else:
            service.start(activity, "")
            button.text = "백그라운드 감시 끄기"
        self.watching = not self.watching


if __name__ == "__main__":
    HeatAlarmApp().run()
