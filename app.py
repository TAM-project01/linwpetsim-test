import streamlit as st
import json
import os
from datetime import datetime

SAVE_DIR = "saved_results"
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------- 시뮬레이션 함수 예시 ----------
def run_simulation(stat_name, level):
    import random
    total = random.randint(100, 200)
    return {
        "name": stat_name,
        "level": level,
        "total": total,
        "details": {"HP": random.randint(10, 20), "MP": random.randint(10, 20)},
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ---------- 저장 함수 ----------
def save_result(data):
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{data['name']}.json"
    with open(os.path.join(SAVE_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- 저장된 목록 불러오기 ----------
def load_saved_files():
    files = sorted(os.listdir(SAVE_DIR), reverse=True)
    result = []
    for f in files:
        try:
            with open(os.path.join(SAVE_DIR, f), encoding="utf-8") as file:
                data = json.load(file)
                result.append((f, data))
        except:
            continue
    return result

# ---------- 시뮬레이션 실행 ----------
st.title("🐾 펫 스탯 시뮬레이터")

stat_name = st.text_input("시뮬레이션 이름", value="내 스탯")
level = st.number_input("레벨", min_value=1, max_value=20, value=10)

if st.button("🧪 시뮬레이션 실행"):
    result = run_simulation(stat_name, level)
    st.session_state["last_result"] = result
    save_result(result)
    st.success("시뮬레이션 완료 및 저장됨!")

# ---------- 결과 표시 ----------
if "last_result" in st.session_state:
    st.subheader("📋 최근 결과")
    st.json(st.session_state["last_result"])

# ---------- 저장된 결과 목록에서 선택 ----------
st.subheader("💾 저장된 시뮬레이션 불러오기")
saved = load_saved_files()

for filename, data in saved:
    label = f"{data.get('name', '무명')} ({data.get('time', '')}) - 총합: {data.get('total', '?')}"
    if st.button(label, key=filename):
        st.session_state["last_result"] = data
        st.success(f"{data.get('name')} 결과를 불러왔습니다.")
