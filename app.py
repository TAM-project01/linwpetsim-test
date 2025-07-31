import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit.components.v1 as components
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

# ---------- 세션 상태 초기화 ----------
if "calculated" not in st.session_state:
    st.session_state["calculated"] = False
if "history" not in st.session_state:
    st.session_state["history"] = []

# 종 정보
d_stat_map = {
    "도베르만": "충성심",
    "비글": "속도",
    "셰퍼드": "인내력",
    "늑대": "체력"
}
stat_order = ["인내력", "충성심", "속도", "체력"]

# ---------- 입력 기본값 세팅 (세션 상태 값 있으면 사용) ----------
category = st.session_state.get("category", list(d_stat_map.keys())[0])
d_stat = d_stat_map[category]
remaining_stats = [s for s in stat_order if s != d_stat]
a_stat, b_stat, c_stat = remaining_stats

level = st.session_state.get("level", 2)
a = st.session_state.get("a", 6)
b = st.session_state.get("b", 6)
c = st.session_state.get("c", 6)
d = st.session_state.get("d", 14)
exclude_hp = st.session_state.get("exclude_hp", False)

# ---------- 입력 UI ----------
category = st.selectbox("\U0001F436 견종 선택", list(d_stat_map.keys()), index=list(d_stat_map.keys()).index(category))
d_stat = d_stat_map[category]
remaining_stats = [s for s in stat_order if s != d_stat]
a_stat, b_stat, c_stat = remaining_stats

exclude_hp = st.checkbox("\U0001F6D1 체력 스탯 제외하고 계산하기", value=exclude_hp)

col1, col2 = st.columns(2)
level = col1.number_input("레벨 (2 이상)", min_value=2, value=level, step=1)
a = col1.number_input(f"{a_stat} 수치", min_value=0, value=a, step=1)
b = col2.number_input(f"{b_stat} 수치", min_value=0, value=b, step=1)
c = col1.number_input(f"{c_stat} 수치", min_value=0, value=c, step=1)
d = col2.number_input(f"{d_stat} 수치", min_value=0, value=d, step=1)

# ---------- 시뮬레이션용 상수 ----------
num_sim = 100_000
ac_vals = [0, 1, 2, 3]
ac_probs = [0.15, 0.5, 0.3, 0.05]
d_vals = [1, 2, 3, 4, 5, 6, 7]
d_probs = [0.05, 0.15, 0.3, 0.2, 0.15, 0.1, 0.05]

# ---------- 결과 계산 버튼 ----------
if st.button("결과 계산"):
    st.session_state["calculated"] = True
    # 현재 입력값도 세션에 저장 (화면 유지용)
    st.session_state["category"] = category
    st.session_state["level"] = level
    st.session_state["a"] = a
    st.session_state["b"] = b
    st.session_state["c"] = c
    st.session_state["d"] = d
    st.session_state["exclude_hp"] = exclude_hp

# ---------- 결과 표시 ----------
if st.session_state["calculated"]:
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

    # ---------- 목표 스탯 입력 ----------
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

    # ---------- 저장 기록 불러오기 및 저장하기 ----------
    # 화면에 기록 목록 보여주기용
    history = st.session_state["history"]

    # 저장 버튼
    if st.button("💾 현재 결과 저장하기"):
        # 현재 결과 JSON 객체 생성
        result_obj = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category": category,
            "level": level,
            "total": user_total,
            "detail": {
                a_stat: a,
                b_stat: b,
                c_stat: c,
                d_stat: d,
            },
            "a_stat": a_stat,
            "b_stat": b_stat,
            "c_stat": c_stat,
            "d_stat": d_stat,
            "exclude_hp": exclude_hp
        }

        # 중복 검사
        is_dup = False
        for h in history:
            if (h["category"] == result_obj["category"] and
                h["level"] == result_obj["level"] and
                h["total"] == result_obj["total"] and
                h["detail"] == result_obj["detail"]):
                is_dup = True
                break

        if is_dup:
            st.warning("이미 같은 기록이 저장되어 있습니다.")
        else:
            history.insert(0, result_obj)  # 최신이 위로
            if len(history) > 20:
                history.pop()  # 최대 20개만 저장
            st.success("기록이 저장되었습니다.")
            # 저장 후에도 입력값 세션 상태 유지
            st.session_state["category"] = category
            st.session_state["level"] = level
            st.session_state["a"] = a
            st.session_state["b"] = b
            st.session_state["c"] = c
            st.session_state["d"] = d
            st.session_state["exclude_hp"] = exclude_hp
            st.experimental_rerun()

    # 저장된 기록 보여주기
    st.markdown("### 💾 저장된 기록 목록")
    if len(history) == 0:
        st.write("저장된 기록이 없습니다.")
    else:
        for i, rec in enumerate(history):
            label = f"{rec['category']} | Lv.{rec['level']} | 총합: {rec['total']} ({rec['time']})"
            if st.button(f"불러오기: {label}", key=f"load_{i}"):
                # 불러오기 버튼 눌렀을 때 세션 상태에 불러온 기록 세팅 후 다시 계산 실행
                st.session_state["category"] = rec["category"]
                st.session_state["level"] = rec["level"]
                st.session_state["a_stat"] = rec.get("a_stat", a_stat)
                st.session_state["b_stat"] = rec.get("b_stat", b_stat)
                st.session_state["c_stat"] = rec.get("c_stat", c_stat)
                st.session_state["d_stat"] = rec.get("d_stat", d_stat)
                st.session_state["a"] = rec["detail"][rec.get("a_stat", a_stat)]
                st.session_state["b"] = rec["detail"][rec.get("b_stat", b_stat)]
                st.session_state["c"] = rec["detail"][rec.get("c_stat", c_stat)]
                st.session_state["d"] = rec["detail"][rec.get("d_stat", d_stat)]
                st.session_state["exclude_hp"] = rec.get("exclude_hp", False)
                st.session_state["calculated"] = True
                st.experimental_rerun()
