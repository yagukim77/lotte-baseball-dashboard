PARK_FACTORS = {
    "사직": 1.02,
    "잠실": 0.96,
    "문학": 1.01,
    "대구": 1.06,
    "수원": 1.03,
    "광주": 1.02,
    "대전": 1.01,
    "창원": 0.99,
    "고척": 0.97,
    "울산": 1.00,
    "포항": 1.02,
    "청주": 1.01,
}


def get_park_factor(stadium: str) -> float:
    if not stadium:
        return 1.0
    return PARK_FACTORS.get(str(stadium).strip(), 1.0)
