# 온도 판정 규칙 (화면과 백그라운드 감시가 함께 씀)


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


# 2. 온도 기록에 새 온도를 넣고, 1분 동안 오른 온도를 돌려줌
#    count: 1분 동안 쌓이는 기록 개수 (기록이 모자라면 None)
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
