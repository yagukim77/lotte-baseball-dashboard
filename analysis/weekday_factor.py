from datetime import datetime


WEEKDAY_FACTORS = {
    "Monday": 1.00,
    "Tuesday": 1.01,
    "Wednesday": 1.00,
    "Thursday": 1.01,
    "Friday": 1.02,
    "Saturday": 1.03,
    "Sunday": 0.99,
}


def get_weekday_factor(date_str: str) -> float:
    try:
        dt = datetime.strptime(str(date_str), "%Y-%m-%d")
        key = dt.strftime("%A")
        return WEEKDAY_FACTORS.get(key, 1.0)
    except Exception:
        return 1.0
