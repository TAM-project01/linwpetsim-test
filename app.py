import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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

if "calculated" not in st.session_state:
    st.session_state["calculated"] = False

# ---------- 종 정보 ----------
d_stat_map = {
    "도베르만": "충성심",
    "비글": "속도",
    "셰퍼드": "인내력",
    "늑대": "체력"
}
stat_order = ["인내력", "충성심", "속도", "체력"]

category = st.selectbox("\U0001F436 견종 선택", list(d_stat_map.keys()))
d_stat = d_stat_map[category]
remaining_stats = [s for s in stat_order if s != d_stat]
a_stat, b_stat, c_stat = remaining_stats

exclude_hp = st.checkbox("\U0001F6D1 체력 스탯 제외하고 계산하기")

col1, col2 = st.columns(2)
level = col1.number_input("레벨 (2 이상)", min_value=2, value=2, step=1)

# 시설 단계 선택 사이드바
with st.sidebar:
    st.header("시설 단계 선택")
    manage_office_lvl = st.slider("관리소 단계", 0, 20, 0)
    lodging_lvl = st.slider("숙소 단계", 0, 20, 0)
    training_lvl = st.slider("훈련장 단계", 0, 20, 0)
    playground_lvl = st.slider("놀이터 단계", 0, 20, 0)
    fence_lvl = st.slider("울타리 단계", 0, 20, 0)

# 입력된 총 스탯 (시설 포함)
a_input = col1.number_input(f"{a_stat} 수치 (시설 포함)", min_value=0, value=6, step=1)
b_input = col2.number_input(f"{b_stat} 수치 (시설 포함)", min_value=0, value=6, step=1)
c_input = col1.number_input(f"{c_stat} 수치 (시설 포함)", min_value=0, value=6, step=1)
d_input = col2.number_input(f"{d_stat} 수치 (시설 포함)", min_value=0, value=14, step=1)

# ---------- 시설별 누적 펫 스탯 보너스 정의 ----------
# 각 시설의 단계별 누적 보너스 (펫 스탯만)
# 구조: {단계: {스탯명: 보너스값, ...}, ...}

manage_office_bonus = {
    1: {"충성심": 1},
    2: {"충성심": 1},
    3: {"충성심": 1},
    4: {"충성심": 1},
    5: {"충성심": 5},
    6: {"충성심": 1},
    7: {"충성심": 1},
    8: {"충성심": 1},
    9: {"충성심": 1},
    10: {"충성심": 10},
    11: {"충성심": 1},
    12: {"충성심": 1},
    13: {"충성심": 1},
    14: {"충성심": 1},
    15: {"충성심": 10},
    16: {"충성심": 2, "적극성": 2, "속도": 2},
    17: {"충성심": 2, "적극성": 2, "속도": 2},
    18: {"적극성": 1},
    19: {"펫 경험치 보너스": 5, "충성심": 5, "체력": 5, "속도": 5, "적극성": 1},
    20: {"펫 경험치 보너스": 5, "충성심": 5, "체력": 0, "속도": 0, "적극성": 5},  # 체력, 속도 0으로 변경
}

lodging_bonus = {
    1: {"체력": 1},
    2: {"체력": 1},
    3: {"체력": 1},
    4: {"체력": 1},
    5: {"체력": 5},
    6: {"체력": 1},
    7: {"체력": 1},
    8: {"체력": 1},
    9: {"체력": 1},
    10: {"체력": 10},
    11: {"체력": 1},
    12: {"체력": 1},
    13: {"체력": 1},
    14: {"체력": 1},
    15: {"체력": 10},
    16: {"적극성": 2},
    17: {"적극성": 2},
    18: {"적극성": 1},
    19: {"펫 경험치 보너스": 5, "적극성": 1, "체력": 5},
    20: {"펫 경험치 보너스": 5, "적극성": 5, "체력": 5},
}

training_bonus = {
    1: {"속도": 1},
    2: {"속도": 1},
    3: {"속도": 1},
    4: {"속도": 1},
    5: {"속도": 5},
    6: {"속도": 1},
    7: {"속도": 1},
    8: {"속도": 1},
    9: {"속도": 1},
    10: {"속도": 10},
    11: {"속도": 1},
    12: {"속도": 1},
    13: {"속도": 1},
    14: {"속도": 1},
    15: {"속도": 10},
    16: {"속도": 2},
    17: {"속도": 2},
    18: {"적극성": 1, "속도": 0},  # 18단계 속도 0으로 대체
    19: {"펫 경험치 보너스": 5, "적극성": 1, "속도": 5},  # 속도 +5 추가
    20: {"펫 경험치 보너스": 5, "적극성": 5, "속도": 5},
}

playground_bonus = {
    1: {"체력": 1},
    2: {"충성심": 1},
    3: {"인내력": 1},
    4: {"속도": 1},
    5: {"적극성": 1},
    6: {"충성심": 1},
    7: {"인내력": 1},
    8: {"속도": 1},
    9: {"체력": 1},
    10: {"적극성": 3},
    11: {"인내력": 1},
    12: {"속도": 1},
    13: {"체력": 1},
    14: {"충성심": 1},
    15: {"적극성": 3},
    16: {"속도": 2},
    17: {"체력": 2},  # 17단계 체력 2로 변경
    18: {"충성심": 2},
    19: {"펫 경험치 보너스": 5, "인내력": 5, "적극성": 1},
    20: {"펫 경험치 보너스": 5, "인내력": 5, "속도": 5, "적극성": 5},  # 20단계 인내력5, 속도5 추가
}

fence_bonus = {
    1: {"인내력": 1},
    2: {"인내력": 1},
    3: {"인내력": 1},
    4: {"인내력": 1},
    5: {"인내력": 5},
    6: {"인내력": 1},
    7: {"인내력": 1},
    8: {"인내력": 1},
    9: {"인내력": 1},
    10: {"인내력": 10},
    11: {"인내력": 1},
    12: {"인내력": 1},
    13: {"인내력": 1},
    14: {"인내력": 1},
    15: {"인내력": 10},
    16: {"인내력": 2},
    17: {"인내력": 2},
    18: {"적극성": 1},
    19: {"펫 경험치 보너스": 5, "인내력": 5, "적극성": 1},
    20: {"펫 경험치 보너스": 5, "인내력": 5, "적극성": 5},
}

# 단계별 누적 보너스 계산 함수
def calc_cumulative_bonus(level, bonus_dict):
    result = {}
    for lvl in range(1, level + 1):
        if lvl in bonus_dict:
            for stat, val in bonus_dict[lvl].items():
                result[stat] = result.get(stat, 0) + val
    return result

# 모든 시설 누적 펫 스탯 보너스 합산
facility_bonus_total = {}
for facility, lvl, bonus_dict in [
    ("관리소", manage_office_lvl, manage_office_bonus),
    ("숙소", lodging_lvl, lodging_bonus),
    ("훈련장", training_lvl, training_bonus),
    ("놀이터", playground_lvl, playground_bonus),
    ("울타리", fence_lvl, fence_bonus),
]:
    bns = calc_cumulative_bonus(lvl, bonus_dict)
    for stat, val in bns.items():
        if stat in ["인내력", "충성심", "속도", "체력"]:
            facility_bonus_total[stat] = facility_bonus_total.get(stat, 0) + val

# 사용자 입력값에서 시설 보너스 차감하여 순수 펫 스탯 계산 (음수 방지)
def safe_subtract(user_val, bonus):
    res = user_val - bonus
    return res if res >= 0 else 0

a_pure = safe_subtract(a_input, facility_bonus_total.get(a_stat, 0))
b_pure = safe_subtract(b_input, facility_bonus_total.get(b_stat, 0))
c_pure = safe_subtract(c_input, facility_bonus_total.get(c_stat, 0))
d_pure = safe_subtract(d_input, facility_bonus_total.get(d_stat, 0))

# ---------- 시뮬레이션 상수 ----------
num_sim = 100_000
ac_vals = [0, 1, 2, 3]
ac_probs = [0.15, 0.5, 0.3, 0.05]
d_vals = [1, 2, 3, 4, 5, 6, 7]
d_probs = [0.05, 0.15, 0.3, 0.2, 0.15, 0.1, 0.05]

if st.button("결과 계산"):
    st.session_state["calculated"] = True

if st.session_state["calculated"]:
    upgrades = level - 1
    a_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    b_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    c_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    d_sim = 14 + np.random.choice(d_vals, (num_sim, upgrades), p=d_probs).sum(axis=1)

    user_total = 0
    total_sim = np.zeros(num_sim)

    for stat_name, user_val, sim_val in zip([a_stat, b_stat, c_stat, d_stat], [a_pure, b_pure, c_pure, d_pure], [a_sim, b_sim, c_sim, d_sim]):
        if exclude_hp and stat_name == "체력":
            continue
        user_total += user_val
        total_sim += sim_val

    total_percentile = np.sum(total_sim > user_total) / num_sim * 100

    a_percentile = np.sum(a_sim > a_pure) / num_sim * 100
    b_percentile = np.sum(b_sim > b_pure) / num_sim * 100
    c_percentile = np.sum(c_sim > c_pure) / num_sim * 100
    d_percentile = np.sum(d_sim > d_pure) / num_sim * 100

    inc_a = (a_pure - 6) / upgrades
    inc_b = (b_pure - 6) / upgrades
    inc_c = (c_pure - 6) / upgrades
    inc_d = (d_pure - 14) / upgrades

    st.success(f"\U0001F4CC 총합 (시설 보너스 제외): {user_total}")
    st.info(f"\U0001F4A1 {'체력 제외 시 ' if exclude_hp else ''}상위 약 {total_percentile:.2f}% 에 해당합니다.")
    st.markdown(f"### \U0001F43E 선택한 견종: **{category}** / 레벨: **{level}**")

    df = pd.DataFrame({
        "스탯": [a_stat, b_stat, c_stat, d_stat],
        "순수 펫 스탯": [a_pure, b_pure, c_pure, d_pure],
        "시설 보너스": [
            facility_bonus_total.get(a_stat, 0),
            facility_bonus_total.get(b_stat, 0),
            facility_bonus_total.get(c_stat, 0),
            facility_bonus_total.get(d_stat, 0),
        ],
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

    # 목표 스탯 도달 확률
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
            a_20 = a_pure + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            b_20 = b_pure + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            c_20 = c_pure + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            d_20 = d_pure + np.random.choice(d_vals, (num_sim, remaining), p=d_probs).sum(axis=1)

            p_a = np.mean(a_20 >= target_a) * 100
            p_b = np.mean(b_20 >= target_b) * 100
            p_c = np.mean(c_20 >= target_c) * 100
            p_d = np.mean(d_20 >= target_d) * 100
            p_all = np.mean((a_20 >= target_a) &
