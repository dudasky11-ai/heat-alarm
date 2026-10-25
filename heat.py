# 배터리 온도 판정 규칙 (화면과 백그라운드 감시가 함께 씀)

# 단계별 기준 온도 (°C): 이 온도 이상이면 그 단계
DANGER = 45   # 위험: 대부분의 폰이 충전을 멈추는 온도
WARNING = 40  # 주의: 충전 속도가 느려지기 시작하는 온도
WARM = 35     # 따뜻함: 제조사 권장 사용 온도의 위쪽 끝


# 1. 온도와 충전 여부로 단계와 행동 요령을 돌려줌
def judge(temp, charging):
    if temp >= DANGER:
        level = "위험"
        advice = "폰 사용을 멈추고 케이스를 벗긴 뒤 서늘한 곳에 두세요."
    elif temp >= WARNING:
        level = "주의"
        advice = "게임이나 영상을 잠시 멈추세요."
    elif temp >= WARM:
        level = "따뜻함"
        advice = "조금 뜨거워요. 직사광선이나 이불 위는 피하세요."
    else:
        level = "정상"
        advice = "괜찮아요."

    # 충전 중에 뜨거우면 충전기 분리를 먼저 권함
    if charging and temp >= WARNING:
        advice = "충전기를 먼저 분리하세요. " + advice

    return level, advice


# 2. 알림을 보낼지 결정: 주의·위험 단계로 "새로" 올라갔을 때만 (같은 알림 반복 방지)
def should_alert(old_level, new_level):
    if new_level not in ("주의", "위험"):
        return False
    return new_level != old_level


# 3-1. 측정값을 기록에 추가하고, 3분(180초)보다 오래된 기록은 지움
KEEP_SECONDS = 180


def add_reading(readings, now, temp):
    readings.append((now, temp))
    while now - readings[0][0] > KEEP_SECONDS:
        readings.pop(0)


# 3-2. 온도가 1분에 몇 °C씩 오르는지 계산
#    readings: [(측정 시각(초), 온도), ...] 오래된 것부터. 1분 이상 쌓여야 계산함
def rise_per_minute(readings):
    if len(readings) < 2:
        return None
    first_time, first_temp = readings[0]
    last_time, last_temp = readings[-1]
    minutes = (last_time - first_time) / 60
    if minutes < 1:
        return None
    return (last_temp - first_temp) / minutes


# 4. 충전 여부와 온도 상승 속도로 발열 원인을 추정하고 해결책을 돌려줌
FAST_RISE = 1.0  # 1분에 1°C 이상 오르면 "빠르게 오름"
SLOW_RISE = 0.3  # 1분에 0.3°C 미만이면 "거의 그대로"


def guess_cause(temp, charging, rise):
    if temp < WARM:
        return "없음", "지금은 괜찮아요."

    if rise is None:
        return "분석 중", "1분 정도 지켜본 뒤 원인을 알려드릴게요."

    if charging and rise >= FAST_RISE:
        return "충전하면서 사용", "충전 중에는 게임·영상을 멈추거나 충전기를 분리하세요."
    if charging:
        return "충전 발열", "고속충전을 끄고 케이스를 벗긴 채 충전하세요."
    if rise >= FAST_RISE:
        return "무거운 작업 (게임·촬영·영상 통화)", "앱을 잠시 끄고 화면 밝기와 그래픽 설정을 낮추세요."
    if rise < SLOW_RISE:
        return "주변 환경 또는 약한 신호", "햇빛·이불 위를 피하고, 신호가 약한 곳이면 Wi-Fi를 쓰세요."
    return "여러 원인이 겹침", "쓰지 않는 앱을 끄고 케이스를 벗겨 보세요."


# 5. 단계별 화면 색 (빨강, 초록, 파랑, 투명도) — Kivy 색 형식
COLORS = {
    "정상": (0.20, 0.65, 0.35, 1),
    "따뜻함": (0.95, 0.70, 0.10, 1),
    "주의": (0.95, 0.45, 0.10, 1),
    "위험": (0.85, 0.15, 0.15, 1),
}
