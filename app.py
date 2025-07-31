import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
from datetime import datetime

# ---------- 초기 설정 ----------
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="스탯 시뮬레이터", layout="centered")
st.title("\U0001F4CA펫 스탯 시뮬레이터")
st.markdown("""
레벨과 스탯 수치를 입력하면, 당신의 총합이 상위 몇 %인지 계산합니다.  
주 스탯을 포함한 **인내력, 충성심, 속도, 체력** 기준이며,  
**특기로 얻은 스탯은 제외하고 입력**해 주세요.
""")

# ---------- 상태 저장 초기화 ----------
if "calculated" not in st.session_state:
    st.session_state["calculated"] = False
if "history" not in st.session_state:
    st.session_state["history"] = []  # 기록 리스트
if "current_result" not in st.session_state:
    st.session_state["current_result"] = None

# ---------- 종 정보 ----------
d_stat_map = {
    "도베르만": "충성심",
    "비글": "속도",
    "셰퍼드": "인내력",
    "늑대": "체력"
}
stat_order = ["인내력", "충성심", "속도", "체력"]

# ---------- 기록 불러오기용 선택박스 ----------
st.sidebar.header("저장된 기록 불러오기")
if st.session_state["history"]:
    selected_idx = st.sidebar.selectbox("불러올 기록 선택", options=list(range(len(st.session_state["history"]))),
                                        format_func=lambda x: f"{st.session_state['history'][x]['time']} - {st.session_state['history'][x]['category']} - 총합 {st.session_state['history'][x]['total']}")
    if st.sidebar.button("불러오기"):
        record = st.session_state["history"][selected_idx]
        # 입력값 세션 상태에 저장 (불러오기)
        st.session_state["category"] = record["category"]
        st.session_state["level"] = record["level"]
        st.session_state["a"] = record["detail"][record["a_stat"]]
        st.session_state["b"] = record["detail"][record["b_stat"]]
        st.session_state["c"] = record["detail"][record["c_stat"]]
        st.session_state["d"] = record["detail"][record["d_stat"]]
        st.session_state["calculated"] = True
        st.experimental_rerun()
else:
    st.sidebar.write("저장된 기록이 없습니다.")

# ---------- 입력 폼 초기값 설정 ----------
category = st.session_state.get("category", list(d_stat_map.keys())[0])
d_stat = d_stat_map[category]
remaining_stats = [s for s in stat_order if s != d_stat]
a_stat, b_stat, c_stat = remaining_stats

level = st.session_state.get("level", 2)
a = st.session_state.get("a", 6)
b = st.session_state.get("b", 6)
c = st.session_state.get("c", 6)
d = st.session_state.get("d", 14)

exclude_hp = st.checkbox("\U0001F6D1 체력 스탯 제외하고 계산하기")

col1, col2 = st.columns(2)
with col1:
    category = st.selectbox("\U0001F436 견종 선택", list(d_stat_map.keys()), index=list(d_stat_map.keys()).index(category))
    level = st.number_input("레벨 (2 이상)", min_value=2, value=level, step=1)
    a = st.number_input(f"{a_stat} 수치", min_value=0, value=a, step=1)
    c = st.number_input(f"{c_stat} 수치", min_value=0, value=c, step=1)
with col2:
    b = st.number_input(f"{b_stat} 수치", min_value=0, value=b, step=1)
    d = st.number_input(f"{d_stat} 수치", min_value=0, value=d, step=1)

# ---------- 시뮬레이션용 상수 ----------
num_sim = 100_000
ac_vals = [0, 1, 2, 3]
ac_probs = [0.15, 0.5, 0.3, 0.05]
d_vals = [1, 2, 3, 4, 5, 6, 7]
d_probs = [0.05, 0.15, 0.3, 0.2, 0.15, 0.1, 0.05]

# ---------- 계산 및 저장 ----------
if st.button("결과 계산"):
    upgrades = level - 1
    a_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    b_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    c_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    d_sim = 14 + np.random.choice(d_vals, (num_sim, upgrades), p=d_probs).sum(axis=1)

    user_total = 0
    total_sim = np.zeros(num_sim)
    for stat_name, user_val, sim_val in zip([a_stat, b_stat, c_stat, d_stat], [a, b, c, d], [a_sim, b_sim, c_sim, d_sim]):
        if exclude_hp and stat_name == "체력":
            continue
        user_total += user_val
        total_sim += sim_val

    total_percentile = np.sum(total_sim > user_total) / num_sim * 100
    a_percentile = np.sum(a_sim > a) / num_sim * 100
    b_percentile = np.sum(b_sim > b) / num_sim * 100
    c_percentile = np.sum(c_sim > c) / num_sim * 100
    d_percentile = np.sum(d_sim > d) / num_sim * 100

    inc_a = (a - 6) / upgrades if upgrades > 0 else 0
    inc_b = (b - 6) / upgrades if upgrades > 0 else 0
    inc_c = (c - 6) / upgrades if upgrades > 0 else 0
    inc_d = (d - 14) / upgrades if upgrades > 0 else 0

    st.success(f"\U0001F4CC 총합: {user_total}")
    st.info(f"\U0001F4A1 {'체력 제외 시 ' if exclude_hp else ''}상위 약 {total_percentile:.2f}% 에 해당합니다.")
    st.markdown(f"### \U0001F43E 선택한 견종: **{category}** / 레벨: **{level}**")

    df = pd.DataFrame({
        "스탯": [a_stat, b_stat, c_stat, d_stat],
        "현재 수치": [a, b, c, d],
        "상위 %": [f"{a_percentile:.2f}%", f"{b_percentile:.2f}%", f"{c_percentile:.2f}%", f"{d_percentile:.2f}%"],
        "Lv당 평균 증가량": [f"+{inc_a:.2f}", f"+{inc_b:.2f}", f"+{inc_c:.2f}", f"+{inc_d:.2f}"]
    })
    st.table(df)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(total_sim, bins=50, kde=True, ax=ax, color='skyblue')
    ax.axvline(user_total, color='red', linestyle='--', label='Your Total')
    ax.set_title(f"{'Excl. HP ' if exclude_hp else ''}Stat Total Distribution")
    ax.set_xlabel("Total Stat")
    ax.legend()
    st.pyplot(fig)

    # 목표 스탯 도달 확률 보기
    calc_goal = st.checkbox("\U0001F3AF 20레벨 목표 스탯 도달 확률 보기")

    if calc_goal:
        st.subheader("목표 스탯 입력")
        col1, col2, col3, col4 = st.columns(4)
        target_a = col1.number_input(f"{a_stat} 목표값", min_value=0, value=35, step=1)
        target_b = col2.number_input(f"{b_stat} 목표값", min_value=0, value=35, step=1)
        target_c = col3.number_input(f"{c_stat} 목표값", min_value=0, value=35, step=1)
        target_d = col4.number_input(f"{d_stat} 목표값 (주 스탯)", min_value=0, value=100, step=1)

        remaining = 20 - level
        if remaining > 0:
            a_20 = a + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            b_20 = b + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            c_20 = c + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            d_20 = d + np.random.choice(d_vals, (num_sim, remaining), p=d_probs).sum(axis=1)

            p_a = np.mean(a_20 >= target_a) * 100
            p_b = np.mean(b_20 >= target_b) * 100
            p_c = np.mean(c_20 >= target_c) * 100
            p_d = np.mean(d_20 >= target_d) * 100
            p_all = np.mean((a_20 >= target_a) & (b_20 >= target_b) & (c_20 >= target_c) & (d_20 >= target_d)) * 100

            st.write(f"\U0001F539 {a_stat} 목표 도달 확률: **{p_a:.2f}%**")
            st.write(f"\U0001F539 {b_stat} 목표 도달 확률: **{p_b:.2f}%**")
            st.write(f"\U0001F539 {c_stat} 목표 도달 확률: **{p_c:.2f}%**")
            st.write(f"\U0001F539 {d_stat} (주 스탯) 목표 도달 확률: **{p_d:.2f}%**")
            st.success(f"\U0001F3C6 모든 목표를 동시에 만족할 확률: **{p_all:.2f}%**")
        else:
            st.warning("이미 20레벨입니다. 목표 시뮬레이션은 생략됩니다.")

    # ---------- 현재 결과 저장 ----------
    st.session_state["current_result"] = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category,
        "level": level,
        "total": user_total,
        "detail": {
            a_stat: a,
            b_stat: b,
            c_stat: c,
            d_stat: d
        },
        "a_stat": a_stat,
        "b_stat": b_stat,
        "c_stat": c_stat,
        "d_stat": d_stat
    }

    # 기록 저장 버튼
    if st.button("현재 결과 저장하기"):
        # 중복 검사
        history = st.session_state["history"]
        current = st.session_state["current_result"]
        if any(
            (h["category"] == current["category"] and
             h["level"] == current["level"] and
             h["total"] == current["total"] and
             h["detail"] == current["detail"])
            for h in history
        ):
            st.warning("이미 같은 기록이 저장되어 있습니다.")
        else:
            history.insert(0, current)  # 최신 기록을 맨 앞에 저장
            if len(history) > 20:  # 기록 최대 20개 제한
                history.pop()
            st.success("기록이 저장되었습니다.")
        st.experimental_rerun()
else:
    st.info("먼저 '결과 계산' 버튼을 눌러 주세요.")
