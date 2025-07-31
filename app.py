import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# ---------- 초기 설정 ----------
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="펫 스탯 시뮬레이터", layout="centered")
st.title("\U0001F4CA펫 스탯 시뮬레이터")
st.markdown("""
레벨과 스탯 수치를 입력하면, 당신의 총합이 상위 몇 %인지 계산합니다.
주 스탯을 포함한 **인내력, 충성심, 속도, 체력** 기준입니다.

**펫 스탯은 펫 타운 및 특기로 증가된 스탯을 포함하여 입력**해 주세요.

**펫 스탯창에 표시되는 수치 그대로 입력하면 됩니다**

펫 타운 시설 레벨과 각 특기 단계를 입력하면, 시뮬레이터에서 해당 증가분을 제외한 **순수 펫 스탯**을 기준으로 계산합니다.
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
# 적극성은 stat_order에 없으므로, 별도로 관리
all_stats_for_pure_calculation = ["인내력", "충성심", "속도", "체력", "적극성"] 

base_stats_initial = {"인내력": 6, "충성심": 6, "속도": 6, "체력": 6, "적극성": 3} # Default base for non-main stat
main_stat_initial = 14 # Default base for main stat

# ---------- 펫 타운 시설 데이터 ----------
facility_rewards_data = {
    "관리소": [
        {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 5},
        {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 10},
        {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 10},
        {"충성심": 2}, {"충성심": 2}, {"적극성": 1},
        {"펫 경험치": "5%", "충성심": 5, "적극성": 1},
        {"펫 경험치": "5%", "충성심": 5, "적극성": 5}
    ],
    "숙소": [
        {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 5},
        {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 10},
        {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 10},
        {"적극성": 2}, {"적극성": 2}, {"적극성": 1},
        {"펫 경험치": "5%", "체력": 5, "적극성": 1},
        {"펫 경험치": "5%", "체력": 5, "적극성": 5}
    ],
    "훈련장": [
        {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 5},
        {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 10},
        {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 10},
        {"속도": 2}, {"속도": 2}, {"적극성": 1},
        {"펫 경험치": "5%", "속도": 5, "적극성": 1},
        {"펫 경험치": "5%", "속도": 5, "적극성": 5}
    ],
    "놀이터": [
        {"체력": 1}, {"충성심": 1}, {"인내력": 1}, {"속도": 1}, {"적극성": 1},
        {"충성심": 1}, {"인내력": 1}, {"속도": 1}, {"체력": 1}, {"적극성": 3},
        {"인내력": 1}, {"속도": 1}, {"체력": 1}, {"충성심": 1}, {"적극성": 3},
        {"속도": 2}, {"체력": 2}, {"충성심": 2},
        {"펫 경험치": "5%", "인내력": 5, "적극성": 1},
        {"펫 경험치": "5%", "인내력": 5, "속도": 5} # 놀이터 20레벨은 속도+5임, 적극성+5 아님
    ],
    "울타리": [
        {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 5},
        {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 10},
        {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 10},
        {"인내력": 2}, {"인내력": 2}, {"적극성": 1},
        {"펫 경험치": "5%", "인내력": 5, "적극성": 1},
        {"펫 경험치": "5%", "인내력": 5, "적극성": 5}
    ]
}

# ---------- 특기 보상 데이터 ----------
specialty_rewards_by_type_and_stage = {
    "노비스 에너지": {0: {}, 1: {"체력": 1}, 2: {"체력": 2}, 3: {"체력": 3}},
    "노비스 터내서티": {0: {}, 1: {"인내력": 1}, 2: {"인내력": 2}, 3: {"인내력": 3}},
    "노비스 링크리지": {0: {}, 1: {"충성심": 1}, 2: {"충성심": 2}, 3: {"충성심": 3}},
    "노비스 래피드": {0: {}, 1: {"속도": 1}, 2: {"속도": 2}, 3: {"속도": 3}},

    "노비스 포커싱": {0: {}, 1: {"적극성": 1}, 2: {"적극성": 2}, 3: {"적극성": 3}},

    "비기너 에너지": {0: {}, 1: {"체력": 1}, 2: {"체력": 2}, 3: {"체력": 3}, 4: {"체력": 5}},
    "비기너 터내서티": {0: {}, 1: {"인내력": 1}, 2: {"인내력": 2}, 3: {"인내력": 3}, 4: {"인내력": 5}},
    "비기너 링크리지": {0: {}, 1: {"충성심": 1}, 2: {"충성심": 2}, 3: {"충성심": 3}, 4: {"충성심": 5}},
    "비기너 래피드": {0: {}, 1: {"속도": 1}, 2: {"속도": 3}, 3: {"속도": 5}, 4: {"속도": 5}},

    "비기너 포커싱": {0: {}, 1: {"적극성": 1}, 2: {"적극성": 2}, 3: {"적극성": 3}, 4: {"적극성": 4}},

    "레이즈 에너지": {0: {}, 1: {"체력": 1}, 2: {"체력": 2}, 3: {"체력": 3}, 4: {"체력": 4}, 5: {"체력": 5}},
    "레이즈 터내서티": {0: {}, 1: {"인내력": 1}, 2: {"인내력": 2}, 3: {"인내력": 3}, 4: {"인내력": 4}, 5: {"인내력": 5}},
    "레이즈 링크리지": {0: {}, 1: {"충성심": 1}, 2: {"충성심": 2}, 3: {"충성심": 3}, 4: {"충성심": 4}, 5: {"충성심": 5}},
    "레이즈 래피드": {0: {}, 1: {"속도": 1}, 2: {"속도": 2}, 3: {"속도": 3}, 4: {"속도": 4}, 5: {"속도": 5}},

    "레이즈 포커싱": {0: {}, 1: {"적극성": 1}, 2: {"적극성": 2}, 3: {"적극성": 3}, 4: {"적극성": 4}, 5: {"적극성": 5}},
}

def calculate_accumulated_facility_stats(facility_name, level):
    stats_to_sum = {stat: 0 for stat in all_stats_for_pure_calculation}
    if facility_name in facility_rewards_data:
        for i in range(min(level, len(facility_rewards_data[facility_name]))):
            rewards_at_level = facility_rewards_data[facility_name][i]
            for stat, value in rewards_at_level.items():
                if stat in stats_to_sum:
                    stats_to_sum[stat] += value
    return stats_to_sum

def get_specialty_bonus_for_stage(specialty_type, stage):
    stats_to_add = {stat: 0 for stat in all_stats_for_pure_calculation}
    if specialty_type in specialty_rewards_by_type_and_stage:
        if stage in specialty_rewards_by_type_and_stage[specialty_type]:
            rewards_at_stage = specialty_rewards_by_type_and_stage[specialty_type][stage]
            for stat, value in rewards_at_stage.items():
                if stat in stats_to_add:
                    stats_to_add[stat] += value
    return stats_to_add

# ---------- 입력 ----------
category = st.selectbox("\U0001F436 견종 선택", list(d_stat_map.keys()))
d_stat = d_stat_map[category] # Main stat
remaining_stats = [s for s in stat_order if s != d_stat]
# 각 스탯을 변수에 정확하게 할당
a_stat_name = remaining_stats[0]
b_stat_name = remaining_stats[1]
c_stat_name = remaining_stats[2]

exclude_hp = st.checkbox("\U0001F6D1 체력 스탯 제외하고 계산하기")

st.subheader("펫 현재 정보 (펫 타운 및 특기가 포함된 스탯 입력)")
col1, col2 = st.columns(2)
level = col1.number_input("펫 레벨 (1 이상)", min_value=1, value=1, step=1)
# 사용자가 입력하는 스탯은 시설물 스탯을 포함한 값
input_stats = {}
input_stats[a_stat_name] = col1.number_input(f"{a_stat_name} 수치", min_value=0, value=base_stats_initial[a_stat_name], step=1)
input_stats[b_stat_name] = col2.number_input(f"{b_stat_name} 수치", min_value=0, value=base_stats_initial[b_stat_name], step=1)
input_stats[c_stat_name] = col1.number_input(f"{c_stat_name} 수치", min_value=0, value=base_stats_initial[c_stat_name], step=1)
input_stats[d_stat] = col2.number_input(f"{d_stat} 수치", min_value=0, value=main_stat_initial, step=1)

# 적극성 스탯 입력 필드 추가
input_stats["적극성"] = st.number_input(
    f"적극성 수치 (고정값 + 펫 타운 + 특기 포함)",
    min_value=0,
    value=base_stats_initial["적극성"],
    step=1
)


st.subheader("펫 타운 시설 레벨")
# Slider for facility levels
management_office_level = st.slider("관리소 레벨", min_value=0, max_value=20, value=0, step=1)
dormitory_level = st.slider("숙소 레벨", min_value=0, max_value=20, value=0, step=1)
training_ground_level = st.slider("훈련장 레벨", min_value=0, max_value=20, value=0, step=1)
playground_level = st.slider("놀이터 레벨", min_value=0, max_value=20, value=0, step=1)
fence_level = st.slider("울타리 레벨", min_value=0, max_value=20, value=0, step=1)

st.subheader("특기")

# Specialty sliders for Novice
col_novice1, col_novice2 = st.columns(2)
novice_energy_stage = col_novice1.slider("노비스 에너지 단계 (4레벨 돌파)", min_value=0, max_value=3, value=0, step=1)
novice_tenacity_stage = col_novice2.slider("노비스 터내서티 단계 (4레벨 돌파)", min_value=0, max_value=3, value=0, step=1)
novice_linkage_stage = col_novice1.slider("노비스 링크리지 단계 (4레벨 돌파)", min_value=0, max_value=3, value=0, step=1)
novice_rapid_stage = col_novice2.slider("노비스 래피드 단계 (4레벨 돌파)", min_value=0, max_value=3, value=0, step=1)
novice_focusing_stage = st.slider("노비스 포커싱 단계 (4레벨 돌파)", min_value=0, max_value=3, value=0, step=1)

st.markdown("---")

# Specialty sliders for Beginner
col_beginner1, col_beginner2 = st.columns(2)
beginner_energy_stage = col_beginner1.slider("비기너 에너지 단계 (9레벨 돌파)", min_value=0, max_value=4, value=0, step=1)
beginner_tenacity_stage = col_beginner2.slider("비기너 터내서티 단계 (9레벨 돌파)", min_value=0, max_value=4, value=0, step=1)
beginner_linkage_stage = col_beginner1.slider("비기너 링크리지 단계 (9레벨 돌파)", min_value=0, max_value=4, value=0, step=1)
beginner_rapid_stage = col_beginner2.slider("비기너 래피드 단계 (9레벨 돌파)", min_value=0, max_value=4, value=0, step=1)
beginner_focusing_stage = st.slider("비기너 포커싱 단계 (9레벨 돌파)", min_value=0, max_value=4, value=0, step=1)

st.markdown("---")

# Specialty sliders for Raise
col_raise1, col_raise2 = st.columns(2)
raise_energy_stage = col_raise1.slider("레이즈 에너지 단계 (14레벨 돌파)", min_value=0, max_value=5, value=0, step=1)
raise_tenacity_stage = col_raise2.slider("레이즈 터내서티 단계 (14레벨 돌파)", min_value=0, max_value=5, value=0, step=1)
raise_linkage_stage = col_raise1.slider("레이즈 링크리지 단계 (14레벨 돌파)", min_value=0, max_value=5, value=0, step=1)
raise_rapid_stage = col_raise2.slider("레이즈 래피드 단계 (14레벨 돌파)", min_value=0, max_value=5, value=0, step=1)
raise_focusing_stage = st.slider("레이즈 포커싱 단계 (14레벨 돌파)", min_value=0, max_value=5, value=0, step=1)

# ---------- 시뮬레이션용 상수 ----------
num_sim = 100_000
ac_vals = [0, 1, 2, 3] # 일반 스탯 증가량
ac_probs = [0.15, 0.5, 0.3, 0.05]
d_vals = [1, 2, 3, 4, 5, 6, 7] # 주 스탯 증가량
d_probs = [0.05, 0.15, 0.3, 0.2, 0.15, 0.1, 0.05]

# ---------- 버튼 ----------
if st.button("결과 계산"):
    st.session_state["calculated"] = True

# ---------- 결과 표시 ----------
if st.session_state["calculated"]:
    # Calculate total facility bonuses
    total_facility_bonuses = {stat: 0 for stat in all_stats_for_pure_calculation}
    
    facility_levels_map = {
        "관리소": management_office_level,
        "숙소": dormitory_level,
        "훈련장": training_ground_level,
        "놀이터": playground_level,
        "울타리": fence_level
    }

    for facility_name, current_level in facility_levels_map.items():
        bonuses = calculate_accumulated_facility_stats(facility_name, current_level)
        for stat, value in bonuses.items():
            if stat in total_facility_bonuses:
                total_facility_bonuses[stat] += value

    # Calculate total specialty bonuses
    total_specialty_bonuses = {stat: 0 for stat in all_stats_for_pure_calculation}
    
    specialty_inputs = {
        "노비스 에너지": novice_energy_stage,
        "노비스 터내서티": novice_tenacity_stage,
        "노비스 링크리지": novice_linkage_stage,
        "노비스 래피드": novice_rapid_stage,
        "노비스 포커싱": novice_focusing_stage,
        "비기너 에너지": beginner_energy_stage,
        "비기너 터내서티": beginner_tenacity_stage,
        "비기너 링크리지": beginner_linkage_stage,
        "비기너 래피드": beginner_rapid_stage,
        "비기너 포커싱": beginner_focusing_stage,
        "레이즈 에너지": raise_energy_stage,
        "레이즈 터내서티": raise_tenacity_stage,
        "레이즈 링크리지": raise_linkage_stage,
        "레이즈 래피드": raise_rapid_stage,
        "레이즈 포커싱": raise_focusing_stage
    }

    for specialty_type, stage in specialty_inputs.items():
        bonuses = get_specialty_bonus_for_stage(specialty_type, stage)
        for stat, value in bonuses.items():
            if stat in total_specialty_bonuses:
                total_specialty_bonuses[stat] += value

    # Calculate user's PURE stats (펫 타운 시설 스탯 및 특기 스탯 제외)
    user_pure_stats = {}
    for stat_name in all_stats_for_pure_calculation:
        if stat_name in stat_order: # 인내력, 충성심, 속도, 체력
            # 주 스탯과 나머지 스탯을 구분하여 기본값 설정
            initial_base = main_stat_initial if stat_name == d_stat else base_stats_initial[stat_name]
            user_pure_stats[stat_name] = max(initial_base, input_stats[stat_name] - total_facility_bonuses[stat_name] - total_specialty_bonuses[stat_name])
        else: # 적극성
            user_pure_stats[stat_name] = max(base_stats_initial[stat_name], input_stats[stat_name] - total_facility_bonuses[stat_name] - total_specialty_bonuses[stat_name])

    
    user_total_pure = 0
    for stat_name in stat_order: # 적극성은 총합 계산에 포함 안됨
        if exclude_hp and stat_name == "체력":
            continue
        user_total_pure += user_pure_stats[stat_name]

    # Calculate upgrades from pet level
    upgrades = level - 1 # Level 1 means 0 upgrades, Level 2 means 1 upgrade etc.

    # Simulate random level-up stats (starting from initial base stats)
    # 각 스탯별 시뮬레이션 결과 저장용 딕셔너리
    simulated_pure_stats = {s: np.full(num_sim, base_stats_initial[s]) for s in stat_order}
    simulated_pure_stats[d_stat] = np.full(num_sim, main_stat_initial)

    if upgrades > 0:
        for stat_name in stat_order:
            if stat_name == d_stat:
                simulated_pure_stats[stat_name] += np.random.choice(d_vals, (num_sim, upgrades), p=d_probs).sum(axis=1)
            else:
                simulated_pure_stats[stat_name] += np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)

    # Calculate total simulated PURE stats for percentile comparison
    total_sim_pure = np.zeros(num_sim)
    for stat_name in stat_order: # 적극성은 총합 계산에 포함 안됨
        if exclude_hp and stat_name == "체력":
            continue
        total_sim_pure += simulated_pure_stats[stat_name]

    total_percentile = np.sum(total_sim_pure > user_total_pure) / num_sim * 100

    # Individual stat percentiles (for user's PURE stats vs simulated PURE stats)
    individual_percentiles = {}
    for stat_name in stat_order:
        individual_percentiles[stat_name] = np.sum(simulated_pure_stats[stat_name] > user_pure_stats[stat_name]) / num_sim * 100
    
    # Calculate average increase per level (based on user's PURE stats)
    avg_increases = {}
    for stat_name in stat_order:
        initial_base = main_stat_initial if stat_name == d_stat else base_stats_initial[stat_name]
        avg_increases[stat_name] = (user_pure_stats[stat_name] - initial_base) / upgrades if upgrades > 0 else 0

    st.success(f"\U0001F4CC 총합 (펫 타운 및 특기 제외 순수 스탯): {user_total_pure}")
    st.info(f"\U0001F4A1 {'체력 제외 시 ' if exclude_hp else ''}상위 약 {total_percentile:.2f}% 에 해당합니다.")
    st.markdown(f"### \U0001F43E 선택한 견종: **{category}** / 펫 레벨: **{level}**")

    # Display individual stats including facility bonuses
    df_data = {
        "스탯": [],
        "입력 수치 (펫 타운/특기 포함)": [],
        "순수 펫 스탯 (펫 타운/특기 제외)": [],
        "펫 타운으로 인한 증가량": [],
        "특기로 인한 증가량": [],
        "상위 % (순수 스탯 기준)": [],
        "펫 레벨당 평균 증가량 (시설물/특기 제외)": []
    }

    # Populate df_data for main stats
    for stat_name in stat_order:
        df_data["스탯"].append(stat_name)
        df_data["입력 수치 (펫 타운/특기 포함)"].append(input_stats[stat_name])
        df_data["순수 펫 스탯 (펫 타운/특기 제외)"].append(user_pure_stats[stat_name])
        df_data["펫 타운으로 인한 증가량"].append(total_facility_bonuses[stat_name])
        df_data["특기로 인한 증가량"].append(total_specialty_bonuses[stat_name])
        df_data["상위 % (순수 스탯 기준)"].append(f"{individual_percentiles[stat_name]:.2f}%")
        df_data["펫 레벨당 평균 증가량 (시설물/특기 제외)"].append(f"+{avg_increases[stat_name]:.2f}")

    # Add Activeness separately
    df_data["스탯"].append("적극성")
    df_data["입력 수치 (펫 타운/특기 포함)"].append(input_stats["적극성"])
    df_data["순수 펫 스탯 (펫 타운/특기 제외)"].append(user_pure_stats["적극성"])
    df_data["펫 타운으로 인한 증가량"].append(total_facility_bonuses["적극성"])
    df_data["특기로 인한 증가량"].append(total_specialty_bonuses["적극성"])
    df_data["상위 % (순수 스탯 기준)"].append("N/A")
    df_data["펫 레벨당 평균 증가량 (시설물/특기 제외)"].append("N/A")

    df = pd.DataFrame(df_data)
    st.table(df)


    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(total_sim_pure, bins=50, kde=True, ax=ax, color='skyblue')
    ax.axvline(user_total_pure, color='red', linestyle='--', label='Your Pet pure Total Stats')
    ax.set_title(f"{'Exclude HP ' if exclude_hp else ''}Total Stats Distribution (Pet Pure Stats)")
    ax.set_xlabel("Total Stats")
    ax.legend()
    st.pyplot(fig)

    # ---
    st.markdown("---")
    # ---------- 목표 스탯 입력 ----------
    calc_goal = st.checkbox("\U0001F3AF 20레벨 목표 스탯 도달 확률 보기")

    if calc_goal:
        st.subheader("목표 스탯 입력 (20레벨 달성 시점의 총 스탯)")
        # 목표 스탯 입력 필드도 딕셔너리로 관리
        target_stats = {}
        col1, col2, col3, col4 = st.columns(4)
        target_stats[a_stat_name] = col1.number_input(f"{a_stat_name} 목표값", min_value=0, value=35, step=1)
        target_stats[b_stat_name] = col2.number_input(f"{b_stat_name} 목표값", min_value=0, value=35, step=1)
        target_stats[c_stat_name] = col3.number_input(f"{c_stat_name} 목표값", min_value=0, value=35, step=1)
        target_stats[d_stat] = col4.number_input(f"{d_stat} 목표값 (주 스탯)", min_value=0, value=100, step=1)
        # 적극성 목표값 입력은 유지하되, 확률 계산에서는 제외
        _ = st.number_input(f"적극성 목표값 (확률 계산에 포함되지 않음)", min_value=0, value=3, step=1)


        remaining_upgrades = 20 - level
        if remaining_upgrades >= 0: # Can reach 20 or already at 20+
            # Simulate pure stats at level 20 (base + random level-ups up to 20)
            sim_pure_at_20 = {s: np.full(num_sim, base_stats_initial[s]) for s in stat_order}
            sim_pure_at_20[d_stat] = np.full(num_sim, main_stat_initial)

            if 19 > 0: 
                for stat_name in stat_order:
                    if stat_name == d_stat:
                        sim_pure_at_20[stat_name] += np.random.choice(d_vals, (num_sim, 19), p=d_probs).sum(axis=1)
                    else:
                        sim_pure_at_20[stat_name] += np.random.choice(ac_vals, (num_sim, 19), p=ac_probs).sum(axis=1)

            # Add facility and specialty bonuses to the simulated 20-level pure stats to compare with target (which is total stat)
            sim_final_at_20 = {}
            for stat_name in stat_order:
                sim_final_at_20[stat_name] = sim_pure_at_20[stat_name] + total_facility_bonuses[stat_name] + total_specialty_bonuses[stat_name]
            
            # 확률 계산
            probabilities = {}
            for stat_name in stat_order: # 적극성 제외
                probabilities[stat_name] = np.mean(sim_final_at_20[stat_name] >= target_stats[stat_name]) * 100
            
            # 모든 목표 동시 만족 확률 (적극성 제외)
            all_conditions = np.full(num_sim, True)
            for stat_name in stat_order: # 적극성 제외
                all_conditions = all_conditions & (sim_final_at_20[stat_name] >= target_stats[stat_name])
            
            p_all = np.mean(all_conditions) * 100


            st.write(f"\U0001F539 {a_stat_name} 목표 도달 확률: **{probabilities[a_stat_name]:.2f}%**")
            st.write(f"\U0001F539 {b_stat_name} 목표 도달 확률: **{probabilities[b_stat_name]:.2f}%**")
            st.write(f"\U0001F539 {c_stat_name} 목표 도달 확률: **{probabilities[c_stat_name]:.2f}%**")
            st.write(f"\U0001F539 {d_stat} (주 스탯) 목표 도달 확률: **{probabilities[d_stat]:.2f}%**")
            st.success(f"\U0001F3C6 모든 목표를 동시에 만족할 확률: **{p_all:.2f}%**")
        else:
            st.warning("펫 레벨이 이미 20을 초과했습니다. 20레벨 목표 시뮬레이션은 생략됩니다.")
