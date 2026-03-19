
import pandas as pd

def load(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()

def hitters():
    lines = load("debug_artifacts/hitter.txt")
    res = []
    for i,l in enumerate(lines):
        if l=="타율":
            try:
                name=lines[i-2]
                team=lines[i-1]
                avg=float(lines[i+1])
                ops_idx=lines.index("OPS", i)
                ops=float(lines[ops_idx+1])
                res.append([name,team,avg,ops])
            except: pass
    pd.DataFrame(res,columns=["player","team","avg","ops"]).to_csv("data/players_stats.csv",index=False)

def pitchers():
    lines = load("debug_artifacts/pitcher.txt")
    res=[]
    for i,l in enumerate(lines):
        if l=="평균자책":
            try:
                name=lines[i-2]
                team=lines[i-1]
                era=float(lines[i+1])
                res.append([name,team,era])
            except: pass
    pd.DataFrame(res,columns=["player","team","era"]).to_csv("data/pitcher_stats.csv",index=False)

def schedule():
    lines = load("debug_artifacts/schedule.txt")
    res=[]
    for i,l in enumerate(lines):
        if l=="경기 시간":
            try:
                time=lines[i+1]
                away=lines[i+5]
                home=lines[i+6]
                res.append([time,away,home])
            except: pass
    pd.DataFrame(res,columns=["time","away","home"]).to_csv("data/schedule.csv",index=False)

if __name__=="__main__":
    import os
    os.makedirs("data",exist_ok=True)
    hitters()
    pitchers()
    schedule()
