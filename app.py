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

# ---------- 커스텀 CSS 스타일 적용 ----------
st.markdown(
    """
    <style>
    /* 전체 페이지 배경색 및 기본 폰트 설정 (선택 사항) */
    body {
        font-family: 'DejaVu Sans', sans-serif;
    }

    /* 각 섹션(st.expander)의 외곽선 및 패딩 */
    .streamlit-expander {
        border: 1px solid #d3d3d3; /* 연한 회색 1px 실선 테두리 */
        border-radius: 8px; /* 모서리를 둥글게 */
        padding: 15px; /* 내부 여백 */
        margin-bottom: 20px; /* 섹션 하단 여백 */
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.05); /* 은은한 그림자 효과 */
    }

    /* Expander 헤더 (제목) 스타일 */
    .streamlit-expander-header {
        font-weight: bold;
        color: #2F80ED; /* 제목 색상 */
        font-size: 1.1em; /* 제목 크기 */
        margin-bottom: 10px; /* 제목 아래 여백 */
    }

    /* 각 소제목 아래의 구분선 */
    h4 {
        border-bottom: 1px solid #e0e0e0; /* 소제목 아래 얇은 회색 선 */
        padding-bottom: 5px; /* 선과 텍스트 사이 여백 */
        margin-bottom: 15px; /* 선 아래 여백 */
    }

    /* 수평선 (st.markdown("---"))의 스타일 */
    hr {
        border-top: 1px dashed #cccccc; /* 점선으로 변경 */
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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

# --- 변경 시작: 펫 종류별 초기 스탯 및 레벨업 확률 정의 ---
initial_stats_data = {
    "일반 펫": {
        "main_stat": 14,
        "sub_stat": 6,
        "aggressiveness": 3,
        "ac_vals": [0, 1, 2, 3],
        "ac_probs": [0.15, 0.50, 0.30, 0.05],
        "d_vals": [1, 2, 3, 4, 5, 6, 7],
        "d_probs": [0.05, 0.15, 0.30, 0.20, 0.15, 0.10, 0.05]
    },
    "심연 펫": {
        "main_stat": 21, # 수정된 심연 펫 주 스탯 초기값
        "sub_stat": 7,
        "aggressiveness": 3,
        "ac_vals": [0, 1, 2, 3],
        "ac_probs": [0.135, 0.445, 0.360, 0.060],
        "d_vals": [1, 2, 3, 4, 5, 6, 7],
        "d_probs": [0.0425, 0.1275, 0.2550, 0.2300, 0.1725, 0.1150, 0.0575]
    }
}
# --- 변경 끝 ---

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

# --- 변경 시작: 시뮬레이션 로직 함수화 (다른 펫 타입 시뮬레이션을 위해) ---
def run_simulation(pet_type_key, user_pure_stats, upgrades, exclude_hp, d_stat, num_sim):
    sim_data = initial_stats_data[pet_type_key]
    
    # 펫 종류에 따른 초기 스탯 가져오기
    sim_main_stat_initial = sim_data["main_stat"]
    sim_sub_stat_initial = sim_data["sub_stat"]
    
    # 펫 종류에 따른 레벨업 확률 가져오기
    sim_ac_vals = sim_data["ac_vals"]
    sim_ac_probs = sim_data["ac_probs"]
    sim_d_vals = sim_data["d_vals"]
    sim_d_probs = sim_data["d_probs"]

    simulated_pure_stats = {s: np.full(num_sim, sim_sub_stat_initial) for s in stat_order}
    simulated_pure_stats[d_stat] = np.full(num_sim, sim_main_stat_initial)

    if upgrades > 0:
        for stat_name in stat_order:
            if stat_name == d_stat:
                simulated_pure_stats[stat_name] += np.random.choice(sim_d_vals, (num_sim, upgrades), p=sim_d_probs).sum(axis=1)
            else:
                simulated_pure_stats[stat_name] += np.random.choice(sim_ac_vals, (num_sim, upgrades), p=sim_ac_probs).sum(axis=1)

    total_sim_pure = np.zeros(num_sim)
    for stat_name in stat_order:
        if exclude_hp and stat_name == "체력":
            continue
        total_sim_pure += simulated_pure_stats[stat_name]
    
    return total_sim_pure, simulated_pure_stats
# --- 변경 끝 ---

# ---------- 입력 섹션 ----------

# 펫 현재 정보 섹션
with st.expander("\U0001F43E 펫 현재 정보 입력 (클릭하여 펼치기)", expanded=True):
    # --- 변경 시작: 펫 종류 선택 추가 ---
    pet_type = st.selectbox("펫 종류 선택", list(initial_stats_data.keys()), key="pet_type_select")
    
    # 선택된 펫 종류에 따라 초기 스탯 값 설정
    current_pet_initial_stats = initial_stats_data[pet_type]
    main_stat_initial_value = current_pet_initial_stats["main_stat"]
    sub_stat_initial_value = current_pet_initial_stats["sub_stat"]
    aggressiveness_initial_value = current_pet_initial_stats["aggressiveness"]
    # --- 변경 끝 ---

    category = st.selectbox("\U0001F436 견종 선택", list(d_stat_map.keys()), key="breed_select")
    d_stat = d_stat_map[category] # Main stat
    remaining_stats = [s for s in stat_order if s != d_stat]
    a_stat_name = remaining_stats[0]
    b_stat_name = remaining_stats[1]
    c_stat_name = remaining_stats[2]

    exclude_hp = st.checkbox("\U0001F6D1 체력 스탯 제외하고 계산하기", key="exclude_hp_checkbox")

    st.markdown("펫 스탯창에 표시되는 수치 그대로 입력해 주세요.")
    col1, col2 = st.columns(2)
    level = col1.number_input("펫 레벨 (1 이상)", min_value=1, value=1, step=1, key="pet_level_input")
    input_stats = {}
    
    # --- 변경 시작: 초기 스탯 값 동적 적용 ---
    input_stats[d_stat] = col2.number_input(f"{d_stat} 수치", min_value=0, value=main_stat_initial_value, step=1, key=f"input_{d_stat}")
    input_stats[a_stat_name] = col1.number_input(f"{a_stat_name} 수치", min_value=0, value=sub_stat_initial_value, step=1, key=f"input_{a_stat_name}")
    input_stats[b_stat_name] = col2.number_input(f"{b_stat_name} 수치", min_value=0, value=sub_stat_initial_value, step=1, key=f"input_{b_stat_name}")
    input_stats[c_stat_name] = col1.number_input(f"{c_stat_name} 수치", min_value=0, value=sub_stat_initial_value, step=1, key=f"input_{c_stat_name}")
    input_stats["적극성"] = st.number_input(f"적극성 수치", min_value=3, value=aggressiveness_initial_value, step=1, key="input_적극성")
    # --- 변경 끝 ---

# 펫 타운 시설 레벨 섹션
with st.expander("\U0001F3D9️ 펫 타운 시설 레벨 (클릭하여 펼치기)", expanded=False):
    management_office_level = st.slider("관리소 레벨", min_value=0, max_value=20, value=0, step=1, key="mo_level")
    dormitory_level = st.slider("숙소 레벨", min_value=0, max_value=20, value=0, step=1, key="dorm_level")
    training_ground_level = st.slider("훈련장 레벨", min_value=0, max_value=20, value=0, step=1, key="train_level")
    playground_level = st.slider("놀이터 레벨", min_value=0, max_value=20, value=0, step=1, key="play_level")
    fence_level = st.slider("울타리 레벨", min_value=0, max_value=20, value=0, step=1, key="fence_level")

# 특기 섹션
with st.expander("\U0001F3C1 특기 (클릭하여 펼치기)", expanded=False):
    st.markdown("---")

    def render_specialty_section(title, category_session_key, specialty_options, max_stage):
        st.markdown(f"#### {title} Specialties") # 제목 영문화
        
        if f"{category_session_key}_add_select_idx" not in st.session_state:
            st.session_state[f"{category_session_key}_add_select_idx"] = 0

        col_select, col_add = st.columns([0.7, 0.3])
        with col_select:
            selected_specialty_to_add = st.selectbox(
                f"Select Specialty to Add", # 문구 영문화
                ["Select"] + specialty_options, # 문구 영문화
                key=f"{category_session_key}_add_select",
                index=st.session_state[f"{category_session_key}_add_select_idx"]
            )
        with col_add:
            st.write("") 
            if st.button(f"Add {title} Specialty", key=f"{category_session_key}_add_btn"): # 버튼 영문화
                if selected_specialty_to_add != "Select": # 문구 영문화
                    st.session_state[category_session_key].append(
                        {"type": selected_specialty_to_add, "stage": 0, "id": pd.Timestamp.now().timestamp()}
                    )
                    st.session_state[f"{category_session_key}_add_select_idx"] = 0 
                    st.rerun() 
                else:
                    st.warning("Please select a specialty to add.") # 경고 문구 영문화

        st.markdown("---")
        if not st.session_state[category_session_key]:
            st.info("No specialties added yet.") # 문구 영문화
        
        specialties_to_keep = []
        for i, spec in enumerate(st.session_state[category_session_key]):
            instance_key = f"{category_session_key}_{spec['type']}_{spec['id']}"

            col_spec_name, col_spec_stage, col_spec_delete = st.columns([0.4, 0.4, 0.2])
            with col_spec_name:
                st.write(f"**{spec['type']}**")
            with col_spec_stage:
                current_stage = st.slider(
                    f"{spec['type']} Stage", # 문구 영문화
                    min_value=0, max_value=max_stage, value=spec["stage"], 
                    key=f"{instance_key}_stage"
                )
                spec["stage"] = current_stage 
            with col_spec_delete:
                st.write("") 
                if st.button("Delete", key=f"{instance_key}_delete"): # 버튼 영문화
                    st.session_state[category_session_key].remove(spec) 
                    st.rerun() 
                else:
                    specialties_to_keep.append(spec) 

        st.session_state[category_session_key] = specialties_to_keep

    # 노비스 특기 (4레벨 돌파)
    novice_specialty_types = [s for s in specialty_rewards_by_type_and_stage if s.startswith("노비스")]
    render_specialty_section("Novice (Level 4 Breakthrough)", "novice_specialties", novice_specialty_types, 3) # 제목 영문화

    st.markdown("---")

    # 비기너 특기 (9레벨 돌파)
    beginner_specialty_types = [s for s in specialty_rewards_by_type_and_stage if s.startswith("비기너")]
    render_specialty_section("Beginner (Level 9 Breakthrough)", "beginner_specialties", beginner_specialty_types, 4) # 제목 영문화

    st.markdown("---")

    # 레이즈 특기 (14레벨 돌파)
    raise_specialty_types = [s for s in specialty_rewards_by_type_and_stage if s.startswith("레이즈")]
    render_specialty_section("Raise (Level 14 Breakthrough)", "raise_specialties", raise_specialty_types, 5) # 제목 영문화

    st.markdown("---")

# ---------- 버튼 ----------
if st.button("Calculate Results", key="calculate_btn"): # 버튼 영문화
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
        # --- 변경 시작: 초기 스탯 값을 펫 종류에 따라 동적으로 가져오기 ---
        initial_base_for_calc = current_pet_initial_stats["sub_stat"]
        if stat_name == d_stat: # 주 스탯
            initial_base_for_calc = current_pet_initial_stats["main_stat"]
        if stat_name == "적극성": # 적극성 초기값
            initial_base_for_calc = current_pet_initial_stats["aggressiveness"]
        # --- 변경 끝 ---
        
        user_pure_stats[stat_name] = max(
            initial_base_for_calc,
            input_stats[stat_name] - total_facility_bonuses[stat_name] - total_specialty_bonuses[stat_name]
        )
    
    user_total_pure = 0
    for stat_name in stat_order: # 적극성은 총합 계산에 포함 안됨
        if exclude_hp and stat_name == "체력":
            continue
        user_total_pure += user_pure_stats[stat_name]

    upgrades = level - 1 # Level 1 means 0 upgrades, Level 2 means 1 upgrade etc.

    # --- 변경 시작: 현재 선택된 펫 타입에 대한 시뮬레이션 실행 ---
    current_pet_total_sim_pure, current_pet_simulated_pure_stats = run_simulation(
        pet_type, user_pure_stats, upgrades, exclude_hp, d_stat, num_sim
    )
    # --- 변경 끝 ---

    total_percentile = np.sum(current_pet_total_sim_pure > user_total_pure) / num_sim * 100

    individual_percentiles = {}
    for stat_name in stat_order:
        # --- 변경 시작: 현재 펫 타입의 초기 스탯을 기준으로 증가량 계산 ---
        initial_base_for_avg_calc = current_pet_initial_stats["main_stat"] if stat_name == d_stat else current_pet_initial_stats["sub_stat"]
        individual_percentiles[stat_name] = np.sum(current_pet_simulated_pure_stats[stat_name] > user_pure_stats[stat_name]) / num_sim * 100
        # --- 변경 끝 ---
    
    avg_increases = {}
    for stat_name in stat_order:
        initial_base_for_avg = current_pet_initial_stats["main_stat"] if stat_name == d_stat else current_pet_initial_stats["sub_stat"]
        avg_increases[stat_name] = (user_pure_stats[stat_name] - initial_base_for_avg) / upgrades if upgrades > 0 else 0

    st.success(f"\U0001F4CC Total Pure Stats (Excluding Town/Specialty Bonuses): {user_total_pure}") # 문구 영문화
    st.info(f"\U0001F4A1 Your pet is in the top {total_percentile:.2f}% of **{pet_type}** pets{', excluding HP' if exclude_hp else ''}.") # 문구 영문화
    st.markdown(f"### \U0001F43E Selected Breed: **{category}** / Pet Level: **{level}** / Pet Type: **{pet_type}**") # 문구 및 타입 추가 영문화

    # --- 변경 시작: 교차 비교 백분율 계산 및 표시 ---
    other_pet_type = "심연 펫" if pet_type == "일반 펫" else "일반 펫"
    
    # 다른 펫 타입의 시뮬레이션 데이터 생성
    other_pet_total_sim_pure, _ = run_simulation(
        other_pet_type, user_pure_stats, upgrades, exclude_hp, d_stat, num_sim
    )
    
    cross_percentile = np.sum(other_pet_total_sim_pure > user_total_pure) / num_sim * 100
    st.info(f"\U0001F504 Your pet is in the top {cross_percentile:.2f}% when compared to **{other_pet_type}** pets{', excluding HP' if exclude_hp else ''}.") # 문구 영문화
    st.markdown("---")
    # --- 변경 끝 ---

    # Display individual stats including facility bonuses
    df_data = {
        "Stat": [], # 헤더 영문화
        "Input Value (Incl. Town/Specialty)": [], # 헤더 영문화
        "Pure Pet Stat (Excl. Town/Specialty)": [], # 헤더 영문화
        "Bonus from Pet Town": [], # 헤더 영문화
        "Bonus from Specialty": [], # 헤더 영문화
        "Top % (Pure Stat Basis)": [], # 헤더 영문화
        "Avg. Increase per Level (Excl. Town/Specialty)": [] # 헤더 영문화
    }

    for stat_name in stat_order: # 적극성은 총합 계산에 포함 안됨
        df_data["Stat"].append(stat_name)
        df_data["Input Value (Incl. Town/Specialty)"].append(input_stats[stat_name])
        df_data["Pure Pet Stat (Excl. Town/Specialty)"].append(user_pure_stats[stat_name])
        df_data["Bonus from Pet Town"].append(total_facility_bonuses[stat_name])
        df_data["Bonus from Specialty"].append(total_specialty_bonuses[stat_name])
        df_data["Top % (Pure Stat Basis)"].append(f"{individual_percentiles[stat_name]:.2f}%")
        df_data["Avg. Increase per Level (Excl. Town/Specialty)"].append(f"+{avg_increases[stat_name]:.2f}")

    # 적극성 스탯 별도 추가
    df_data["Stat"].append("적극성")
    df_data["Input Value (Incl. Town/Specialty)"].append(input_stats["적극성"])
    df_data["Pure Pet Stat (Excl. Town/Specialty)"].append(user_pure_stats["적극성"])
    df_data["Bonus from Pet Town"].append(total_facility_bonuses["적극성"])
    df_data["Bonus from Specialty"].append(total_specialty_bonuses["적극성"])
    df_data["Top % (Pure Stat Basis)"].append("N/A")
    df_data["Avg. Increase per Level (Excl. Town/Specialty)"].append("N/A")

    df = pd.DataFrame(df_data)
    st.table(df)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(current_pet_total_sim_pure, bins=50, kde=True, ax=ax, color='skyblue')
    ax.axvline(user_total_pure, color='red', linestyle='--', label='Your Pet Pure Total Stats')
    ax.set_title(f"Overall Stat Distribution ({pet_type} - Pure Pet Stats){' (Excluding HP)' if exclude_hp else ''}") # 제목에 펫 타입 추가
    ax.set_xlabel("Total Stats")
    ax.legend()
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("Target Stats Input (Total Stats at Level 20)") # 제목 영문화
    calc_goal = st.checkbox("\U0001F3AF View Probability to Reach Level 20 Target Stats", key="calc_goal_checkbox") # 문구 영문화

    if calc_goal:
        target_stats = {}
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        target_stats[a_stat_name] = col_t1.number_input(f"{a_stat_name} Target", min_value=0, value=35, step=1, key=f"target_{a_stat_name}") # 문구 영문화
        target_stats[b_stat_name] = col_t2.number_input(f"{b_stat_name} Target", min_value=0, value=35, step=1, key=f"target_{b_stat_name}") # 문구 영문화
        target_stats[c_stat_name] = col_t3.number_input(f"{c_stat_name} Target", min_value=0, value=35, step=1, key=f"target_{c_stat_name}") # 문구 영문화
        target_stats[d_stat] = col_t4.number_input(f"{d_stat} Target (Main Stat)", min_value=0, value=100, step=1, key=f"target_{d_stat}") # 문구 영문화
        
        remaining_upgrades_to_20 = 20 - level if level < 20 else 0

        # --- 변경 시작: 목표 스탯 계산 시에도 현재 펫 타입의 초기 스탯 및 확률 적용 ---
        sim_pure_at_20_data = initial_stats_data[pet_type]
        sim_pure_at_20_main_stat_initial = sim_pure_at_20_data["main_stat"]
        sim_pure_at_20_sub_stat_initial = sim_pure_at_20_data["sub_stat"]
        sim_pure_at_20_ac_vals = sim_pure_at_20_data["ac_vals"]
        sim_pure_at_20_ac_probs = sim_pure_at_20_data["ac_probs"]
        sim_pure_at_20_d_vals = sim_pure_at_20_data["d_vals"]
        sim_pure_at_20_d_probs = sim_pure_at_20_data["d_probs"]

        sim_pure_at_20 = {s: np.full(num_sim, sim_pure_at_20_sub_stat_initial) for s in stat_order}
        sim_pure_at_20[d_stat] = np.full(num_sim, sim_pure_at_20_main_stat_initial)

        for stat_name in stat_order:
            sim_pure_at_20[stat_name] = np.full(num_sim, user_pure_stats[stat_name]) 
            if remaining_upgrades_to_20 > 0:
                if stat_name == d_stat:
                    sim_pure_at_20[stat_name] += np.random.choice(sim_pure_at_20_d_vals, (num_sim, remaining_upgrades_to_20), p=sim_pure_at_20_d_probs).sum(axis=1)
                else:
                    sim_pure_at_20[stat_name] += np.random.choice(sim_pure_at_20_ac_vals, (num_sim, remaining_upgrades_to_20), p=sim_pure_at_20_ac_probs).sum(axis=1)
        # --- 변경 끝 ---

        sim_final_at_20 = {}
        for stat_name in stat_order: 
            sim_final_at_20[stat_name] = sim_pure_at_20[stat_name] + total_facility_bonuses[stat_name] + total_specialty_bonuses[stat_name]
        
        probabilities = {}
        for stat_name in stat_order: 
            probabilities[stat_name] = np.mean(sim_final_at_20[stat_name] >= target_stats[stat_name]) * 100
        
        all_conditions = np.full(num_sim, True)
        for stat_name in stat_order: 
            all_conditions = all_conditions & (sim_final_at_20[stat_name] >= target_stats[stat_name])
        
        p_all = np.mean(all_conditions) * 100

        st.write(f"\U0001F539 Probability to reach {a_stat_name} target: **{probabilities[a_stat_name]:.2f}%**") # 문구 영문화
        st.write(f"\U0001F539 Probability to reach {b_stat_name} target: **{probabilities[b_stat_name]:.2f}%**") # 문구 영문화
        st.write(f"\U0001F539 Probability to reach {c_stat_name} target: **{probabilities[c_stat_name]:.2f}%**") # 문구 영문화
        st.write(f"\U0001F539 Probability to reach {d_stat} (Main Stat) target: **{probabilities[d_stat]:.2f}%**") # 문구 영문화
        st.success(f"\U0001F3C6 Probability to satisfy all targets simultaneously: **{p_all:.2f}%**") # 문구 영문화
