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

# ---------- 상태 초기화 ----------
if "calculated" not in st.session_state:
    st.session_state["calculated"] = False

# 특기 인스턴스를 저장할 세션 상태 초기화 (노비스, 비기너, 레이즈)
if 'novice_specialties' not in st.session_state:
    st.session_state['novice_specialties'] = []
if 'beginner_specialties' not in st.session_state:
    st.session_state['beginner_specialties'] = []
if 'raise_specialties' not in st.session_state:
    st.session_state['raise_specialties'] = []

# ---------- 종 정보 ----------
d_stat_map = {
    "도베르만": "충성심",
    "비글": "속도",
    "셰퍼드": "인내력",
    "늑대": "체력"
}
stat_order = ["인내력", "충성심", "속도", "체력"]
all_stats_for_pure_calculation = ["인내력", "충성심", "속도", "체력", "적극성"]

base_stats_initial = {"인내력": 6, "충성심": 6, "속도": 6, "체력": 6, "적극성": 3} # Default base for non-main stat
main_stat_initial = 14 # Default base for main stat

# ---------- 펫 타운 시설 데이터 (최종 확인) ----------
facility_rewards_data = {
    "관리소": [
        {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 5},
        {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 10},
        {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 1}, {"충성심": 10},
        {"충성심": 2}, {"충성심": 2}, {"적극성": 1},
        {"펫 경험치": "5%", "충성심": 5, "적극성": 1}, #19레벨
        {"펫 경험치": "5%", "충성심": 5, "적극성": 5} #20레벨
    ],
    "숙소": [
        {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 5},
        {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 10},
        {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 1}, {"체력": 10},
        {"적극성": 2}, {"적극성": 2}, {"적극성": 1},
        {"펫 경험치": "5%", "체력": 5, "적극성": 1}, #19레벨
        {"펫 경험치": "5%", "체력": 5, "적극성": 5} #20레벨
    ],
    "훈련장": [
        {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 5},
        {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 10},
        {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 1}, {"속도": 10},
        {"속도": 2}, {"속도": 2}, {"적극성": 1},
        {"펫 경험치": "5%", "속도": 5, "적극성": 1}, #19레벨
        {"펫 경험치": "5%", "속도": 5, "적극성": 5} #20레벨
    ],
    "놀이터": [
        {"체력": 1}, {"충성심": 1}, {"인내력": 1}, {"속도": 1}, {"적극성": 1},
        {"충성심": 1}, {"인내력": 1}, {"속도": 1}, {"체력": 1}, {"적극성": 3},
        {"인내력": 1}, {"속도": 1}, {"체력": 1}, {"충성심": 1}, {"적극성": 3},
        {"속도": 2}, {"체력": 2}, {"충성심": 2},
        {"펫 경험치": "5%", "인내력": 5, "적극성": 1}, #19레벨
        {"펫 경험치": "5%", "적극성": 5, "속도": 5} #20레벨 (수정 반영)
    ],
    "울타리": [
        {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 5},
        {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 10},
        {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 1}, {"인내력": 10},
        {"인내력": 2}, {"인내력": 2}, {"적극성": 1},
        {"펫 경험치": "5%", "인내력": 5, "적극성": 1}, #19레벨
        {"펫 경험치": "5%", "인내력": 5, "적극성": 5} #20레벨
    ]
}

# ---------- 특기 보상 데이터 (최종 확인) ----------
specialty_rewards_by_type_and_stage = {
    # 노비스 특기 (최대 3단계)
    "노비스 에너지": {0: {}, 1: {"체력": 1}, 2: {"체력": 2}, 3: {"체력": 3}},
    "노비스 터내서티": {0: {}, 1: {"인내력": 1}, 2: {"인내력": 2}, 3: {"인내력": 3}},
    "노비스 링크리지": {0: {}, 1: {"충성심": 1}, 2: {"충성심": 2}, 3: {"충성심": 3}},
    "노비스 래피드": {0: {}, 1: {"속도": 1}, 2: {"속도": 2}, 3: {"속도": 3}},
    "노비스 포커싱": {0: {}, 1: {"적극성": 1}, 2: {"적극성": 2}, 3: {"적극성": 3}},

    # 비기너 특기 (최대 4단계)
    "비기너 에너지": {0: {}, 1: {"체력": 1}, 2: {"체력": 2}, 3: {"체력": 3}, 4: {"체력": 5}},
    "비기너 터내서티": {0: {}, 1: {"인내력": 1}, 2: {"인내력": 2}, 3: {"인내력": 3}, 4: {"인내력": 5}},
    "비기너 링크리지": {0: {}, 1: {"충성심": 1}, 2: {"충성심": 2}, 3: {"충성심": 3}, 4: {"충성심": 5}},
    "비기너 래피드": {0: {}, 1: {"속도": 1}, 2: {"속도": 2}, 3: {"속도": 3}, 4: {"속도": 5}},
    "비기너 포커싱": {0: {}, 1: {"적극성": 1}, 2: {"적극성": 2}, 3: {"적극성": 3}, 4: {"적극성": 5}},

    # 레이즈 특기 (최대 5단계)
    "레이즈 에너지": {0: {}, 1: {"체력": 1}, 2: {"체력": 2}, 3: {"체력": 3}, 4: {"체력": 4}, 5: {"체력": 5}},
    "레이즈 터내서티": {0: {}, 1: {"인내력": 1}, 2: {"인내력": 2}, 3: {"인내력": 3}, 4: {"인내력": 4}, 5: {"인내력": 5}},
    "레이즈 링크리지": {0: {}, 1: {"충성심": 1}, 2: {"충성심": 2}, 3: {"충성심": 3}, 4: {"충성심": 4}, 5: {"충성심": 5}},
    "레이즈 래피드": {0: {}, 1: {"속도": 1}, 2: {"속도": 2}, 3: {"속도": 3}, 4: {"속도": 4}, 5: {"속도": 5}},
    "레이즈 포커싱": {0: {}, 1: {"적극성": 1}, 2: {"적극성": 2}, 3: {"적극성": 3}, 4: {"적극성": 4}, 5: {"적극성": 5}},
}

# ---------- 유틸리티 함수 ----------
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

# ---------- 입력 섹션 ----------
category = st.selectbox("\U0001F436 견종 선택", list(d_stat_map.keys()))
d_stat = d_stat_map[category] # Main stat
remaining_stats = [s for s in stat_order if s != d_stat]
a_stat_name = remaining_stats[0]
b_stat_name = remaining_stats[1]
c_stat_name = remaining_stats[2]

exclude_hp = st.checkbox("\U0001F6D1 체력 스탯 제외하고 계산하기")

st.subheader("펫 현재 정보 (펫 타운 및 특기가 포함된 스탯 입력)")
col1, col2 = st.columns(2)
level = col1.number_input("펫 레벨 (1 이상)", min_value=1, value=1, step=1)
input_stats = {}
input_stats[a_stat_name] = col1.number_input(f"{a_stat_name} 수치", min_value=0, value=base_stats_initial[a_stat_name], step=1)
input_stats[b_stat_name] = col2.number_input(f"{b_stat_name} 수치", min_value=0, value=base_stats_initial[b_stat_name], step=1)
input_stats[c_stat_name] = col1.number_input(f"{c_stat_name} 수치", min_value=0, value=base_stats_initial[c_stat_name], step=1)
input_stats[d_stat] = col2.number_input(f"{d_stat} 수치", min_value=0, value=main_stat_initial, step=1)
input_stats["적극성"] = st.number_input(f"적극성 수치", min_value=3, value=base_stats_initial["적극성"], step=1)

st.subheader("펫 타운 시설 레벨")
management_office_level = st.slider("관리소 레벨", min_value=0, max_value=20, value=0, step=1, key="mo_level")
dormitory_level = st.slider("숙소 레벨", min_value=0, max_value=20, value=0, step=1, key="dorm_level")
training_ground_level = st.slider("훈련장 레벨", min_value=0, max_value=20, value=0, step=1, key="train_level")
playground_level = st.slider("놀이터 레벨", min_value=0, max_value=20, value=0, step=1, key="play_level")
fence_level = st.slider("울타리 레벨", min_value=0, max_value=20, value=0, step=1, key="fence_level")

st.subheader("특기")

def render_specialty_section(title, category_key, specialty_options, max_stage):
    st.markdown(f"#### {title} 특기 ({category_key.split('_')[0].capitalize()})")
    
    # 세션 상태에 해당 카테고리 특기 리스트가 없으면 초기화
    if category_key not in st.session_state:
        st.session_state[category_key] = []

    col_select, col_add = st.columns([0.7, 0.3])
    with col_select:
        selected_specialty_to_add = st.selectbox(
            f"추가할 {title} 특기 선택", 
            ["선택하세요"] + specialty_options, 
            key=f"{category_key}_add_select"
        )
    with col_add:
        st.write("") # 공간 확보용
        if st.button(f"{title} 특기 추가", key=f"{category_key}_add_btn"):
            if selected_specialty_to_add != "선택하세요":
                st.session_state[category_key].append(
                    {"type": selected_specialty_to_add, "stage": 0, "id": len(st.session_state[category_key])}
                )
                # 새로운 특기 추가 후 selectbox 초기화
                st.session_state[f"{category_key}_add_select"] = "선택하세요" 
            else:
                st.warning("추가할 특기를 선택해주세요.")

    # 추가된 특기들을 렌더링
    st.markdown("---")
    if not st.session_state[category_key]:
        st.info("현재 추가된 특기가 없습니다.")
    
    # 변경된 특기 리스트를 임시 저장
    updated_specialties = []
    for i, spec in enumerate(st.session_state[category_key]):
        col_spec_name, col_spec_stage, col_spec_delete = st.columns([0.4, 0.4, 0.2])
        with col_spec_name:
            st.write(f"**{spec['type']}**")
        with col_spec_stage:
            current_stage = st.slider(
                f"{spec['type']} 단계", 
                min_value=0, max_value=max_stage, value=spec["stage"], 
                key=f"{category_key}_{spec['type']}_{spec['id']}_stage"
            )
            spec["stage"] = current_stage # 슬라이더 변경 사항 반영
        with col_spec_delete:
            st.write("") # 공간 확보용
            if st.button("삭제", key=f"{category_key}_{spec['type']}_{spec['id']}_delete"):
                # 삭제할 항목의 인덱스 대신 ID로 필터링 (고유성 유지)
                pass # 실제 삭제는 아래에서 필터링하여 수행
            else:
                updated_specialties.append(spec)
    
    # 삭제 버튼이 눌렸을 경우 실제 리스트 업데이트 (새로운 리스트로 대체)
    if len(st.session_state[category_key]) != len(updated_specialties):
        st.session_state[category_key] = updated_specialties
        st.rerun() # 상태 변경 후 재실행하여 UI 업데이트

st.markdown("---")

# 노비스 특기 (4레벨 돌파)
novice_specialty_types = [s for s in specialty_rewards_by_type_and_stage if s.startswith("노비스")]
render_specialty_section("노비스", "novice_specialties", novice_specialty_types, 3) # 노비스 특기는 최대 3단계

st.markdown("---")

# 비기너 특기 (9레벨 돌파)
beginner_specialty_types = [s for s in specialty_rewards_by_type_and_stage if s.startswith("비기너")]
render_specialty_section("비기너", "beginner_specialties", beginner_specialty_types, 4) # 비기너 특기는 최대 4단계

st.markdown("---")

# 레이즈 특기 (14레벨 돌파)
raise_specialty_types = [s for s in specialty_rewards_by_type_and_stage if s.startswith("레이즈")]
render_specialty_section("레이즈", "raise_specialties", raise_specialty_types, 5) # 레이즈 특기는 최대 5단계

st.markdown("---")

# ---------- 시뮬레이션용 상수 ----------
num_sim = 100_000
ac_vals = [0, 1, 2, 3] # 일반 스탯 증가량
ac_probs = [0.15, 0.5, 0.3, 0.05]
d_vals = [1, 2, 3, 4, 5, 6, 7] # 주 스탯 증가량
d_probs = [0.05, 0.15, 0.3, 0.2, 0.15, 0.1, 0.05]

# ---------- 버튼 ----------
if st.button("결과 계산", key="calculate_btn"):
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

    # Calculate total specialty bonuses from ALL added specialties
    total_specialty_bonuses = {stat: 0 for stat in all_stats_for_pure_calculation}
    
    all_active_specialties = (
        st.session_state['novice_specialties'] +
        st.session_state['beginner_specialties'] +
        st.session_state['raise_specialties']
    )

    for spec_instance in all_active_specialties:
        bonuses = get_specialty_bonus_for_stage(spec_instance["type"], spec_instance["stage"])
        for stat, value in bonuses.items():
            if stat in total_specialty_bonuses:
                total_specialty_bonuses[stat] += value
    
    # Calculate user's PURE stats (펫 타운 시설 스탯 및 특기 스탯 제외)
    user_pure_stats = {}
    for stat_name in all_stats_for_pure_calculation:
        initial_base = base_stats_initial[stat_name]
        if stat_name == d_stat: # 주 스탯
            initial_base = main_stat_initial
        
        user_pure_stats[stat_name] = max(
            initial_base, 
            input_stats[stat_name] - total_facility_bonuses[stat_name] - total_specialty_bonuses[stat_name]
        )
    
    user_total_pure = 0
    for stat_name in stat_order: # 적극성은 총합 계산에 포함 안됨
        if exclude_hp and stat_name == "체력":
            continue
        user_total_pure += user_pure_stats[stat_name]

    # Calculate upgrades from pet level
    upgrades = level - 1 # Level 1 means 0 upgrades, Level 2 means 1 upgrade etc.

    # Simulate random level-up stats (starting from initial base stats)
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

    for stat_name in stat_order: # 적극성은 총합 계산에 포함 안됨
        df_data["스탯"].append(stat_name)
        df_data["입력 수치 (펫 타운/특기 포함)"].append(input_stats[stat_name])
        df_data["순수 펫 스탯 (펫 타운/특기 제외)"].append(user_pure_stats[stat_name])
        df_data["펫 타운으로 인한 증가량"].append(total_facility_bonuses[stat_name])
        df_data["특기로 인한 증가량"].append(total_specialty_bonuses[stat_name])
        df_data["상위 % (순수 스탯 기준)"].append(f"{individual_percentiles[stat_name]:.2f}%")
        df_data["펫 레벨당 평균 증가량 (시설물/특기 제외)"].append(f"+{avg_increases[stat_name]:.2f}")

    # 적극성 스탯 별도 추가
    df_data["스탯"].append("적극성")
    df_data["입력 수치 (펫 타운/특기 포함)"].append(input_stats["적극성"])
    df_data["순수 펫 스탯 (펫 타운/특기 제외)"].append(user_pure_stats["적극성"])
    df_data["펫 타운으로 인한 증가량"].append(total_facility_bonuses["적극성"])
    df_data["특기로 인한 증가량"].append(total_specialty_bonuses["적극성"])
    df_data["상위 % (순수 스탯 기준)"].append("N/A") # 적극성은 시뮬레이션되지 않으므로 N/A
    df_data["펫 레벨당 평균 증가량 (시설물/특기 제외)"].append("N/A") # 적극성은 레벨업으로 증가하지 않음

    df = pd.DataFrame(df_data)
    st.table(df)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(total_sim_pure, bins=50, kde=True, ax=ax, color='skyblue')
    ax.axvline(user_total_pure, color='red', linestyle='--', label='Your Pet Pure Total Stats')
    ax.set_title(f"{'체력 제외 ' if exclude_hp else ''}총 스탯 분포 (순수 펫 스탯)")
    ax.set_xlabel("총 스탯")
    ax.legend()
    st.pyplot(fig)

    # ---
    st.markdown("---")
    # ---------- 목표 스탯 입력 ----------
    calc_goal = st.checkbox("\U0001F3AF 20레벨 목표 스탯 도달 확률 보기", key="calc_goal_checkbox")

    if calc_goal:
        st.subheader("목표 스탯 입력 (20레벨 달성 시점의 총 스탯)")
        target_stats = {}
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        target_stats[a_stat_name] = col_t1.number_input(f"{a_stat_name} 목표값", min_value=0, value=35, step=1, key=f"target_{a_stat_name}")
        target_stats[b_stat_name] = col_t2.number_input(f"{b_stat_name} 목표값", min_value=0, value=35, step=1, key=f"target_{b_stat_name}")
        target_stats[c_stat_name] = col_t3.number_input(f"{c_stat_name} 목표값", min_value=0, value=35, step=1, key=f"target_{c_stat_name}")
        target_stats[d_stat] = col_t4.number_input(f"{d_stat} 목표값 (주 스탯)", min_value=0, value=100, step=1, key=f"target_{d_stat}")
        
        # 20레벨까지 남은 업그레이드 횟수 (현재 레벨이 20보다 낮을 경우)
        remaining_upgrades_to_20 = 20 - level if level < 20 else 0

        # Simulate pure stats at level 20 (base + random level-ups up to 20)
        sim_pure_at_20 = {s: np.full(num_sim, base_stats_initial[s]) for s in stat_order}
        sim_pure_at_20[d_stat] = np.full(num_sim, main_stat_initial)

        # 현재 펫 레벨부터 20레벨까지의 추가 레벨업만 시뮬레이션
        # 펫의 현재 '순수 스탯'에서 시작하여, 남은 레벨업만 추가
        for stat_name in stat_order:
            sim_pure_at_20[stat_name] = np.full(num_sim, user_pure_stats[stat_name]) # 현재 순수 스탯에서 시작
            if remaining_upgrades_to_20 > 0:
                if stat_name == d_stat:
                    sim_pure_at_20[stat_name] += np.random.choice(d_vals, (num_sim, remaining_upgrades_to_20), p=d_probs).sum(axis=1)
                else:
                    sim_pure_at_20[stat_name] += np.random.choice(ac_vals, (num_sim, remaining_upgrades_to_20), p=ac_probs).sum(axis=1)

        # Add facility and specialty bonuses to the simulated 20-level pure stats to compare with target (which is total stat)
        sim_final_at_20 = {}
        for stat_name in stat_order: # 적극성 제외
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
