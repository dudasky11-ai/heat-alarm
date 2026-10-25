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


# 3. 단계별 화면 색 (빨강, 초록, 파랑, 투명도) — Kivy 색 형식
COLORS = {
    "정상": (0.20, 0.65, 0.35, 1),
    "따뜻함": (0.95, 0.70, 0.10, 1),
    "주의": (0.95, 0.45, 0.10, 1),
    "위험": (0.85, 0.15, 0.15, 1),
}
