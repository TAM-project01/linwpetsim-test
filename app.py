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

# ---------- 상태 저장 ----------
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

# ---------- 시설별 단계별 누적 펫 스탯 데이터 ----------
# 0레벨은 모두 0 (효과 없음)
facility_stat_data = {
    "관리소": {
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
        20: {"펫 경험치 보너스": 5, "충성심": 5, "체력": 5, "적극성": 5},
    },
    "숙소": {
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
    },
    "훈련장": {
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
        18: {"적극성": 1},
        19: {"펫 경험치 보너스": 5, "적극성": 1, "속도": 5},
        20: {"펫 경험치 보너스": 5, "적극성": 5, "속도": 5},
    },
    "놀이터": {
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
        17: {"체력": 2},
        18: {"충성심": 2},
        19: {"펫 경험치 보너스": 5, "인내력": 5, "적극성": 1},
        20: {"펫 경험치 보너스": 5, "인내력": 5, "속도": 5},
    },
    "울타리": {
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
    },
}

# ---------- 기능 함수 ----------
def get_cumulative_facility_stats(facility, level):
    """facility: str, level: int, return dict 누적 스탯 합산"""
    cum_stats = {}
    for lvl in range(1, level + 1):
        stats = facility_stat_data.get(facility, {}).get(lvl, {})
        for stat, val in stats.items():
            cum_stats[stat] = cum_stats.get(stat, 0) + val
    return cum_stats

def aggregate_all_facilities_stats(levels):
    """
    levels: dict of facility:str -> level:int
    return: dict of stat -> total bonus
    """
    total_stats = {}
    for fac, lvl in levels.items():
        fac_stats = get_cumulative_facility_stats(fac, lvl)
        for stat, val in fac_stats.items():
            total_stats[stat] = total_stats.get(stat, 0) + val
    return total_stats

# ---------- 입력 ----------

# 시설별 레벨 입력 (0~20)
st.sidebar.header("시설 레벨 설정 (0~20)")
facility_levels = {}
for fac in ["관리소", "숙소", "훈련장", "놀이터", "울타리"]:
    facility_levels[fac] = st.sidebar.slider(f"{fac} 단계", min_value=0, max_value=20, value=0, step=1)

# 누적된 시설 스탯 계산
facility_stats = aggregate_all_facilities_stats(facility_levels)

st.sidebar.markdown("----")
st.sidebar.write("### 시설 누적 보너스 스탯")
if len(facility_stats) == 0:
    st.sidebar.write("0레벨 상태입니다.")
else:
    for k, v in facility_stats.items():
        if "보너스" in k:  # 펫 경험치 보너스 등 별도 표시
            st.sidebar.write(f"{k}: +{v}%")
        else:
            st.sidebar.write(f"{k}: +{v}")

# 종, 주스탯, 입력값
category = st.selectbox("\U0001F436 견종 선택", list(d_stat_map.keys()))
d_stat = d_stat_map[category]
remaining_stats = [s for s in stat_order if s != d_stat]
a_stat, b_stat, c_stat = remaining_stats

exclude_hp = st.checkbox("\U0001F6D1 체력 스탯 제외하고 계산하기")

col1, col2 = st.columns(2)
level = col1.number_input("레벨 (2 이상)", min_value=2, value=2, step=1)
# 시설 스탯 차감 후 실제 입력값 계산용 함수
def adjust_stat_input(stat_name, base_val):
    """시설에서 차감된 스탯만큼 빼고 0 미만 방지"""
    val = base_val - facility_stats.get(stat_name, 0)
    if val < 0:
        val = 0
    return val

a_raw = col1.number_input(f"{a_stat} 수치 (시설 보너스 제외)", min_value=0, value=6, step=1)
b_raw = col2.number_input(f"{b_stat} 수치 (시설 보너스 제외)", min_value=0, value=6, step=1)
c_raw = col1.number_input(f"{c_stat} 수치 (시설 보너스 제외)", min_value=0, value=6, step=1)
d_raw = col2.number_input(f"{d_stat} 수치 (시설 보너스 제외)", min_value=0, value=14, step=1)

a = adjust_stat_input(a_stat, a_raw)
b = adjust_stat_input(b_stat, b_raw)
c = adjust_stat_input(c_stat, c_raw)
d = adjust_stat_input(d_stat, d_raw)

# ---------- 시뮬레이션용 상수 ----------
num_sim = 100_000
ac_vals = [0, 1, 2, 3]
ac_probs = [0.15, 0.5, 0.3, 0.05]
d_vals = [1, 2, 3, 4, 5, 6, 7]
d_probs = [0.05, 0.15, 0.3, 0.2, 0.15, 0.1, 0.05]

# ---------- 버튼 ----------
if st.button("결과 계산"):
    st.session_state["calculated"] = True

# ---------- 결과 표시 ----------
if st.session_state["calculated"]:
    upgrades = level - 1
    a_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    b_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    c_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    d_sim = 14 + np.random.choice(d_vals, (num_sim, upgrades), p=d_probs).sum(axis=1)

    user_total = 0
    total_sim = np.zeros(num_sim)

    # 총합 계산 시 시설 보너스 포함: 입력값 + 시설 보너스
    for stat_name, user_val, sim_val in zip(
        [a_stat, b_stat, c_stat, d_stat],
        [a + facility_stats.get(a_stat, 0),
         b + facility_stats.get(b_stat, 0),
         c + facility_stats.get(c_stat, 0),
         d + facility_stats.get(d_stat, 0)],
        [a_sim, b_sim, c_sim, d_sim],
    ):
        if exclude_hp and stat_name == "체력":
            continue
        user_total += user_val
        total_sim += sim_val

    total_percentile = np.sum(total_sim > user_total) / num_sim * 100

    # 개별 스탯 백분위 (입력값 + 시설 보너스)
    a_percentile = np.sum(a_sim > (a + facility_stats.get(a_stat, 0))) / num_sim * 100
    b_percentile = np.sum(b_sim > (b + facility_stats.get(b_stat, 0))) / num_sim * 100
    c_percentile = np.sum(c_sim > (c + facility_stats.get(c_stat, 0))) / num_sim * 100
    d_percentile = np.sum(d_sim > (d + facility_stats.get(d_stat, 0))) / num_sim * 100

    inc_a = (a + facility_stats.get(a_stat, 0) - 6) / upgrades
    inc_b = (b + facility_stats.get(b_stat, 0) - 6) / upgrades
    inc_c = (c + facility_stats.get(c_stat, 0) - 6) / upgrades
    inc_d = (d + facility_stats.get(d_stat, 0) - 14) / upgrades

    st.success(f"\U0001F4CC 총합: {user_total}")
    st.info(f"\U0001F4A1 {'체력 제외 시 ' if exclude_hp else ''}상위 약 {total_percentile:.2f}% 에 해당합니다.")
    st.markdown(f"### \U0001F43E 선택한 견종: **{category}** / 레벨: **{level}**")

    df = pd.DataFrame({
        "스탯": [a_stat, b_stat, c_stat, d_stat],
        "현재 수치 (시설 보너스 제외)": [a_raw, b_raw, c_raw, d_raw],
        "시설 보너스": [facility_stats.get(a_stat, 0), facility_stats.get(b_stat, 0),
                      facility_stats.get(c_stat, 0), facility_stats.get(d_stat, 0)],
        "합산 수치": [a + facility_stats.get(a_stat, 0),
                  b + facility_stats.get(b_stat, 0),
                  c + facility_stats.get(c_stat, 0),
                  d + facility_stats.get(d_stat, 0)],
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
            a_20 = a + facility_stats.get(a_stat, 0) + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            b_20 = b + facility_stats.get(b_stat, 0) + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            c_20 = c + facility_stats.get(c_stat, 0) + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            d_20 = d + facility_stats.get(d_stat, 0) + np.random.choice(d_vals, (num_sim, remaining), p=d_probs).sum(axis=1)

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
