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

# ---------- 시설별 펫 스탯 보너스 테이블 (0~20 단계 누적용) ----------
# 단계별 누적 합산을 위해 리스트 안 값들은 단계별 추가 보너스

facility_bonus_pet_stats = {
    "관리소": [
        {"충성심":1}, {"충성심":1}, {"충성심":1}, {"충성심":1}, {"충성심":5},
        {"충성심":1}, {"충성심":1}, {"충성심":1}, {"충성심":1}, {"충성심":10},
        {"충성심":1}, {"충성심":1}, {"충성심":1}, {"충성심":1}, {"충성심":10},
        {"충성심":2, "적극성":2, "속도":2}, {"충성심":2, "적극성":2, "속도":2}, {"적극성":1}, 
        {"펫 경험치 보너스":5, "충성심":5, "체력":5, "속도":5, "적극성":1}, 
        {"펫 경험치 보너스":5, "충성심":5, "적극성":5}
    ],
    "숙소": [
        {}, # 0단계 (0레벨) 보너스 없음
        {"체력":1}, {"체력":1}, {"체력":1}, {"체력":1}, {"체력":5},
        {"체력":1}, {"체력":1}, {"체력":1}, {"체력":1}, {"체력":10},
        {"체력":1}, {"체력":1}, {"체력":1}, {"체력":1}, {"체력":10},
        {"적극성":2}, {"적극성":2}, {"적극성":1},
        {"펫 경험치 보너스":5, "적극성":1, "체력":5}, 
        {"펫 경험치 보너스":5, "적극성":5, "체력":5}
    ],
    "훈련장": [
        {}, # 0단계
        {"속도":1}, {"속도":1}, {"속도":1}, {"속도":1}, {"속도":5},
        {"속도":1}, {"속도":1}, {"속도":1}, {"속도":1}, {"속도":10},
        {"속도":1}, {"속도":1}, {"속도":1}, {"속도":1}, {"속도":10},
        {"속도":2}, {"속도":2}, {"적극성":1}, 
        {"펫 경험치 보너스":5, "적극성":1, "속도":5}, 
        {"펫 경험치 보너스":5, "적극성":5, "속도":5}
    ],
    "놀이터": [
        {}, # 0단계
        {"체력":1}, {"충성심":1}, {"인내력":1}, {"속도":1}, {"적극성":1},
        {"충성심":1}, {"속도":1}, {"체력":1}, {"적극성":1}, {"적극성":3},
        {"인내력":1}, {"속도":1}, {"체력":1}, {"충성심":1}, {"적극성":3},
        {"속도":2}, {"적극성":1}, {"체력":2}, 
        {"펫 경험치 보너스":5, "인내력":5, "적극성":1}, 
        {"펫 경험치 보너스":5, "인내력":5, "속도":5, "적극성":5}
    ],
    "울타리": [
        {}, # 0단계
        {"인내력":1}, {"인내력":1}, {"인내력":1}, {"인내력":1}, {"인내력":5},
        {"인내력":1}, {"인내력":1}, {"인내력":1}, {"인내력":10},
        {"인내력":1}, {"인내력":1}, {"인내력":1}, {"인내력":1}, {"인내력":10},
        {"인내력":2}, {"인내력":2}, {"적극성":1},
        {"펫 경험치 보너스":5, "인내력":5, "적극성":5},
        {"펫 경험치 보너스":5, "인내력":5, "적극성":5}
    ],
}

# 펫 스탯 4종만 관리 (인내력, 충성심, 속도, 체력)
# 적극성, 펫 경험치 보너스 등은 따로 표시 가능하니 우선 시뮬레이션에서는 제외

def calc_cumulative_bonus(facility, level):
    """facility: str, level: int (0~20)
    해당 시설의 1~level단계까지 누적된 펫 스탯 보너스를 반환 (dict)"""
    bonus = {"인내력":0, "충성심":0, "속도":0, "체력":0}
    if level == 0:
        return bonus
    for i in range(level):
        step_bonus = facility_bonus_pet_stats[facility][i]
        for stat in bonus.keys():
            bonus[stat] += step_bonus.get(stat, 0)
    return bonus

# ---------- 입력 ----------
category = st.selectbox("\U0001F436 견종 선택", list(d_stat_map.keys()))
d_stat = d_stat_map[category]
remaining_stats = [s for s in stat_order if s != d_stat]
a_stat, b_stat, c_stat = remaining_stats

exclude_hp = st.checkbox("\U0001F6D1 체력 스탯 제외하고 계산하기")

col1, col2 = st.columns(2)
level = col1.number_input("레벨 (2 이상)", min_value=2, value=2, step=1)

a = col1.number_input(f"{a_stat} 수치", min_value=0, value=6, step=1)
b = col2.number_input(f"{b_stat} 수치", min_value=0, value=6, step=1)
c = col1.number_input(f"{c_stat} 수치", min_value=0, value=6, step=1)
d = col2.number_input(f"{d_stat} 수치", min_value=0, value=14, step=1)

st.markdown("---")
st.markdown("### 시설 단계 선택 (0~20)")

col1, col2, col3, col4, col5 = st.columns(5)
level_gm = col1.slider("관리소", min_value=0, max_value=20, value=0)
level_inn = col2.slider("숙소", min_value=0, max_value=20, value=0)
level_training = col3.slider("훈련장", min_value=0, max_value=20, value=0)
level_playground = col4.slider("놀이터", min_value=0, max_value=20, value=0)
level_fence = col5.slider("울타리", min_value=0, max_value=20, value=0)

# ---------- 시설 보너스 누적 계산 ----------
bonus_gm = calc_cumulative_bonus("관리소", level_gm)
bonus_inn = calc_cumulative_bonus("숙소", level_inn)
bonus_training = calc_cumulative_bonus("훈련장", level_training)
bonus_playground = calc_cumulative_bonus("놀이터", level_playground)
bonus_fence = calc_cumulative_bonus("울타리", level_fence)

total_bonus = {"인내력":0, "충성심":0, "속도":0, "체력":0}
for stat in total_bonus.keys():
    total_bonus[stat] = bonus_gm[stat] + bonus_inn[stat] + bonus_training[stat] + bonus_playground[stat] + bonus_fence[stat]

# ---------- 시설 보너스 제외한 순수 펫 스탯 계산 ----------
pure_a = a - total_bonus.get(a_stat, 0)
pure_b = b - total_bonus.get(b_stat, 0)
pure_c = c - total_bonus.get(c_stat, 0)
pure_d = d - total_bonus.get(d_stat, 0)

# 음수 방지
pure_a = max(pure_a, 0)
pure_b = max(pure_b, 0)
pure_c = max(pure_c, 0)
pure_d = max(pure_d, 0)

# ---------- 시뮬레이션 상수 ----------
num_sim = 100_000
ac_vals = [0, 1, 2, 3]
ac_probs = [0.15, 0.5, 0.3, 0.05]
d_vals = [1, 2, 3, 4, 5, 6, 7]
d_probs = [0.05, 0.15, 0.3, 0.2, 0.15, 0.1, 0.05]

# ---------- 결과 계산 버튼 ----------
if st.button("결과 계산"):
    st.session_state["calculated"] = True

# ---------- 결과 표시 ----------
if st.session_state["calculated"]:
    upgrades = level - 1

    # 시뮬레이션은 순수 스탯 기준으로 수행
    a_sim = pure_a + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    b_sim = pure_b + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    c_sim = pure_c + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    d_sim = pure_d + np.random.choice(d_vals, (num_sim, upgrades), p=d_probs).sum(axis=1)

    # 사용자가 입력한 순수 펫 스탯 총합과 시뮬레이션 비교
    user_total_pure = pure_a + pure_b + pure_c + pure_d
    total_sim = a_sim + b_sim + c_sim + d_sim

    total_percentile = np.sum(total_sim > user_total_pure) / num_sim * 100

    a_percentile = np.sum(a_sim > pure_a) / num_sim * 100
    b_percentile = np.sum(b_sim > pure_b) / num_sim * 100
    c_percentile = np.sum(c_sim > pure_c) / num_sim * 100
    d_percentile = np.sum(d_sim > pure_d) / num_sim * 100

    inc_a = (pure_a - 6) / upgrades
    inc_b = (pure_b - 6) / upgrades
    inc_c = (pure_c - 6) / upgrades
    inc_d = (pure_d - 14) / upgrades

    st.success(f"\U0001F4CC 시설 제외 펫 순수 스탯 총합: {user_total_pure}")
    st.info(f"\U0001F4A1 {'체력 제외 시 ' if exclude_hp else ''}상위 약 {total_percentile:.2f}% 에 해당합니다.")
    st.markdown(f"### \U0001F43E 선택한 견종: **{category}** / 레벨: **{level}**")
    st.markdown(f"### \U0001F3D7 시설 단계")
    st.write(f"관리소: {level_gm}, 숙소: {level_inn}, 훈련장: {level_training}, 놀이터: {level_playground}, 울타리: {level_fence}")

    # 결과표에 시설 제외 순수 펫 스탯 보여주기
    df = pd.DataFrame({
        "스탯": [a_stat, b_stat, c_stat, d_stat],
        "현재 수치": [a, b, c, d],
        "시설 보너스": [
            total_bonus.get(a_stat, 0),
            total_bonus.get(b_stat, 0),
            total_bonus.get(c_stat, 0),
            total_bonus.get(d_stat, 0),
        ],
        "순수 펫 스탯": [pure_a, pure_b, pure_c, pure_d],
        "상위 %": [f"{a_percentile:.2f}%", f"{b_percentile:.2f}%", f"{c_percentile:.2f}%", f"{d_percentile:.2f}%"],
        "Lv당 평균 증가량": [f"+{inc_a:.2f}", f"+{inc_b:.2f}", f"+{inc_c:.2f}", f"+{inc_d:.2f}"]
    })
    st.table(df)

    # 시뮬레이션 총합 분포 그래프
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(total_sim, bins=50, kde=True, ax=ax, color='skyblue')
    ax.axvline(user_total_pure, color='red', linestyle='--', label='Your Pure Total Stat')
    ax.set_title(f"{'Excl. HP ' if exclude_hp else ''}Stat Total Distribution (Pure Stats)")
    ax.set_xlabel("Total Stat (Pure)")
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
            a_20 = pure_a + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            b_20 = pure_b + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            c_20 = pure_c + np.random.choice(ac_vals, (num_sim, remaining), p=ac_probs).sum(axis=1)
            d_20 = pure_d + np.random.choice(d_vals, (num_sim, remaining), p=d_probs).sum(axis=1)

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
