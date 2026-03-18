import pandas as pd


def build_live_win_history(current_prob: float, status_text: str):
    innings = ["1회", "2회", "3회", "4회", "5회", "6회", "7회", "8회", "9회"]
    base = 0.5
    history = []
    for i, inning in enumerate(innings, start=1):
        factor = i / 9
        value = base + (current_prob - base) * factor
        history.append({"inning": inning, "win_prob": round(value, 3)})
    if "종료" in str(status_text):
        history[-1]["win_prob"] = round(current_prob, 3)
    return pd.DataFrame(history)
