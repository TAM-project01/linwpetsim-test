import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# ---------- Initial Setup ----------
# Set font family to 'DejaVu Sans' for English text to prevent font breaking
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False # This is for displaying minus signs correctly

st.set_page_config(page_title="Pet Stat Simulator", layout="centered")
st.title("\U0001F4CA Pet Stat Simulator")
st.markdown("""
Enter your pet's level and stats to calculate its percentile rank.
Calculations include **Endurance, Loyalty, Speed, and HP**, along with the **Main Stat**.

**Please enter pet stats exactly as they appear in your pet's stat window**, including any bonuses from Pet Town or Specialties.

The simulator will then deduct Pet Town and Specialty bonuses to calculate **Pure Pet Stats** for comparison.
""")

# ---------- Custom CSS Styles ----------
st.markdown(
    """
    <style>
    /* Overall page background and default font (optional) */
    body {
        font-family: 'DejaVu Sans', sans-serif;
    }

    /* Borders and padding for each section (st.expander) */
    .streamlit-expander {
        border: 1px solid #d3d3d3; /* Light gray 1px solid border */
        border-radius: 8px; /* Rounded corners */
        padding: 15px; /* Inner padding */
        margin-bottom: 20px; /* Bottom margin for sections */
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.05); /* Subtle shadow effect */
    }

    /* Expander header (title) style */
    .streamlit-expander-header {
        font-weight: bold;
        color: #2F80ED; /* Title color */
        font-size: 1.1em; /* Title font size */
        margin-bottom: 10px; /* Bottom margin below title */
    }

    /* Separator line below each sub-heading */
    h4 {
        border-bottom: 1px solid #e0e0e0; /* Thin gray line below sub-heading */
        padding-bottom: 5px; /* Padding between text and line */
        margin-bottom: 15px; /* Margin below the line */
    }

    /* Style for horizontal rules (st.markdown("---")) */
    hr {
        border-top: 1px dashed #cccccc; /* Changed to dashed line */
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- State Initialization ----------
if "calculated" not in st.session_state:
    st.session_state["calculated"] = False

# Initialize session state for specialties
if 'novice_specialties' not in st.session_state:
    st.session_state['novice_specialties'] = []
if 'beginner_specialties' not in st.session_state:
    st.session_state['beginner_specialties'] = []
if 'raise_specialties' not in st.session_state:
    st.session_state['raise_specialties'] = []

# ---------- Breed Information ----------
d_stat_map = {
    "Doberman": "Loyalty",
    "Beagle": "Speed",
    "Shepherd": "Endurance",
    "Wolf": "HP" # Assuming '체력' maps to 'HP' for clarity
}
stat_order = ["Endurance", "Loyalty", "Speed", "HP"] # Changed to English
all_stats_for_pure_calculation = ["Endurance", "Loyalty", "Speed", "HP", "Aggressiveness"] # Changed to English

# --- Defined Initial Stats and Level-up Probabilities by Pet Type ---
initial_stats_data = {
    "Normal Pet": {
        "main_stat": 14,
        "sub_stat": 6,
        "aggressiveness": 3,
        "ac_vals": [0, 1, 2, 3],
        "ac_probs": [0.15, 0.50, 0.30, 0.05],
        "d_vals": [1, 2, 3, 4, 5, 6, 7],
        "d_probs": [0.05, 0.15, 0.30, 0.20, 0.15, 0.10, 0.05]
    },
    "Abyssal Pet": { # Changed to English
        "main_stat": 21,
        "sub_stat": 7,
        "aggressiveness": 3,
        "ac_vals": [0, 1, 2, 3],
        "ac_probs": [0.135, 0.445, 0.360, 0.060],
        "d_vals": [1, 2, 3, 4, 5, 6, 7],
        "d_probs": [0.0425, 0.1275, 0.2550, 0.2300, 0.1725, 0.1150, 0.0575]
    }
}

# ---------- Pet Town Facility Data (Finalized) ----------
facility_rewards_data = {
    "Management Office": [ # Changed to English
        {"Loyalty": 1}, {"Loyalty": 1}, {"Loyalty": 1}, {"Loyalty": 1}, {"Loyalty": 5},
        {"Loyalty": 1}, {"Loyalty": 1}, {"Loyalty": 1}, {"Loyalty": 1}, {"Loyalty": 10},
        {"Loyalty": 1}, {"Loyalty": 1}, {"Loyalty": 1}, {"Loyalty": 1}, {"Loyalty": 10},
        {"Loyalty": 2}, {"Loyalty": 2}, {"Aggressiveness": 1},
        {"Pet EXP": "5%", "Loyalty": 5, "Aggressiveness": 1}, #19레벨
        {"Pet EXP": "5%", "Loyalty": 5, "Aggressiveness": 5} #20레벨
    ],
    "Dormitory": [ # Changed to English
        {"HP": 1}, {"HP": 1}, {"HP": 1}, {"HP": 1}, {"HP": 5},
        {"HP": 1}, {"HP": 1}, {"HP": 1}, {"HP": 1}, {"HP": 10},
        {"HP": 1}, {"HP": 1}, {"HP": 1}, {"HP": 1}, {"HP": 10},
        {"Aggressiveness": 2}, {"Aggressiveness": 2}, {"Aggressiveness": 1},
        {"Pet EXP": "5%", "HP": 5, "Aggressiveness": 1}, #19레벨
        {"Pet EXP": "5%", "HP": 5, "Aggressiveness": 5} #20레벨
    ],
    "Training Ground": [ # Changed to English
        {"Speed": 1}, {"Speed": 1}, {"Speed": 1}, {"Speed": 1}, {"Speed": 5},
        {"Speed": 1}, {"Speed": 1}, {"Speed": 1}, {"Speed": 1}, {"Speed": 10},
        {"Speed": 1}, {"Speed": 1}, {"Speed": 1}, {"Speed": 1}, {"Speed": 10},
        {"Speed": 2}, {"Speed": 2}, {"Aggressiveness": 1},
        {"Pet EXP": "5%", "Speed": 5, "Aggressiveness": 1}, #19레벨
        {"Pet EXP": "5%", "Speed": 5, "Aggressiveness": 5} #20레벨
    ],
    "Playground": [ # Changed to English
        {"HP": 1}, {"Loyalty": 1}, {"Endurance": 1}, {"Speed": 1}, {"Aggressiveness": 1},
        {"Loyalty": 1}, {"Endurance": 1}, {"Speed": 1}, {"HP": 1}, {"Aggressiveness": 3},
        {"Endurance": 1}, {"Speed": 1}, {"HP": 1}, {"Loyalty": 1}, {"Aggressiveness": 3},
        {"Speed": 2}, {"HP": 2}, {"Loyalty": 2},
        {"Pet EXP": "5%", "Endurance": 5, "Aggressiveness": 1}, #19레벨
        {"Pet EXP": "5%", "Aggressiveness": 5, "Speed": 5} #20레벨
    ],
    "Fence": [ # Changed to English
        {"Endurance": 1}, {"Endurance": 1}, {"Endurance": 1}, {"Endurance": 1}, {"Endurance": 5},
        {"Endurance": 1}, {"Endurance": 1}, {"Endurance": 1}, {"Endurance": 1}, {"Endurance": 10},
        {"Endurance": 1}, {"Endurance": 1}, {"Endurance": 1}, {"Endurance": 1}, {"Endurance": 10},
        {"Endurance": 2}, {"Endurance": 2}, {"Aggressiveness": 1},
        {"Pet EXP": "5%", "Endurance": 5, "Aggressiveness": 1}, #19레벨
        {"Pet EXP": "5%", "Endurance": 5, "Aggressiveness": 5} #20레벨
    ]
}

# ---------- Specialty Reward Data (Finalized) ----------
specialty_rewards_by_type_and_stage = {
    # Novice Specialties (max 3 stages)
    "Novice Energy": {0: {}, 1: {"HP": 1}, 2: {"HP": 2}, 3: {"HP": 3}},
    "Novice Tenacity": {0: {}, 1: {"Endurance": 1}, 2: {"Endurance": 2}, 3: {"Endurance": 3}},
    "Novice Linkage": {0: {}, 1: {"Loyalty": 1}, 2: {"Loyalty": 2}, 3: {"Loyalty": 3}},
    "Novice Rapid": {0: {}, 1: {"Speed": 1}, 2: {"Speed": 2}, 3: {"Speed": 3}},
    "Novice Focusing": {0: {}, 1: {"Aggressiveness": 1}, 2: {"Aggressiveness": 2}, 3: {"Aggressiveness": 3}},

    # Beginner Specialties (max 4 stages)
    "Beginner Energy": {0: {}, 1: {"HP": 1}, 2: {"HP": 2}, 3: {"HP": 3}, 4: {"HP": 5}},
    "Beginner Tenacity": {0: {}, 1: {"Endurance": 1}, 2: {"Endurance": 2}, 3: {"Endurance": 3}, 4: {"Endurance": 5}},
    "Beginner Linkage": {0: {}, 1: {"Loyalty": 1}, 2: {"Loyalty": 2}, 3: {"Loyalty": 3}, 4: {"Loyalty": 5}},
    "Beginner Rapid": {0: {}, 1: {"Speed": 1}, 2: {"Speed": 2}, 3: {"Speed": 3}, 4: {"Speed": 5}},
    "Beginner Focusing": {0: {}, 1: {"Aggressiveness": 1}, 2: {"Aggressiveness": 2}, 3: {"Aggressiveness": 3}, 4: {"Aggressiveness": 5}},

    # Raise Specialties (max 5 stages)
    "Raise Energy": {0: {}, 1: {"HP": 1}, 2: {"HP": 2}, 3: {"HP": 3}, 4: {"HP": 4}, 5: {"HP": 5}},
    "Raise Tenacity": {0: {}, 1: {"Endurance": 1}, 2: {"Endurance": 2}, 3: {"Endurance": 3}, 4: {"Endurance": 4}, 5: {"Endurance": 5}},
    "Raise Linkage": {0: {}, 1: {"Loyalty": 1}, 2: {"Loyalty": 2}, 3: {"Loyalty": 3}, 4: {"Loyalty": 4}, 5: {"Loyalty": 5}},
    "Raise Rapid": {0: {}, 1: {"Speed": 1}, 2: {"Speed": 2}, 3: {"Speed": 3}, 4: {"Speed": 4}, 5: {"Speed": 5}},
    "Raise Focusing": {0: {}, 1: {"Aggressiveness": 1}, 2: {"Aggressiveness": 2}, 3: {"Aggressiveness": 3}, 4: {"Aggressiveness": 4}, 5: {"Aggressiveness": 5}},
}

# ---------- Utility Functions ----------
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

# --- Simulation Logic Function ---
def run_simulation(pet_type_key, upgrades, exclude_hp, d_stat, num_sim):
    sim_data = initial_stats_data[pet_type_key]
    
    # Get initial stats for this pet type
    sim_main_stat_initial = sim_data["main_stat"]
    sim_sub_stat_initial = sim_data["sub_stat"]
    
    # Get level-up probabilities for this pet type
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
        if exclude_hp and stat_name == "HP": # Changed to English
            continue
        total_sim_pure += simulated_pure_stats[stat_name]
    
    return total_sim_pure, simulated_pure_stats

# ---------- Input Section ----------

# Pet Current Info Section
with st.expander("\U0001F43E Enter Pet Current Information", expanded=True): # Changed to English
    # --- Pet Type Selection ---
    pet_type = st.selectbox("Select Pet Type", list(initial_stats_data.keys()), key="pet_type_select") # Changed to English
    
    # Set initial stat values based on selected pet type
    current_pet_initial_stats = initial_stats_data[pet_type]
    main_stat_initial_value = current_pet_initial_stats["main_stat"]
    sub_stat_initial_value = current_pet_initial_stats["sub_stat"]
    aggressiveness_initial_value = current_pet_initial_stats["aggressiveness"]

    category = st.selectbox("\U0001F436 Select Breed", list(d_stat_map.keys()), key="breed_select") # Changed to English
    d_stat = d_stat_map[category] # Main stat
    remaining_stats = [s for s in stat_order if s != d_stat]
    a_stat_name = remaining_stats[0]
    b_stat_name = remaining_stats[1]
    c_stat_name = remaining_stats[2]

    exclude_hp = st.checkbox("\U0001F6D1 Calculate Excluding HP Stat", key="exclude_hp_checkbox") # Changed to English

    st.markdown("Please enter the values exactly as displayed in your pet's stat window.") # Changed to English
    col1, col2 = st.columns(2)
    level = col1.number_input("Pet Level (1 or higher)", min_value=1, value=1, step=1, key="pet_level_input") # Changed to English
    input_stats = {}
    
    # --- Dynamic Initial Stat Values for Input Fields ---
    input_stats[d_stat] = col2.number_input(f"{d_stat} Value", min_value=0, value=main_stat_initial_value, step=1, key=f"input_{d_stat}") # Changed to English
    input_stats[a_stat_name] = col1.number_input(f"{a_stat_name} Value", min_value=0, value=sub_stat_initial_value, step=1, key=f"input_{a_stat_name}") # Changed to English
    input_stats[b_stat_name] = col2.number_input(f"{b_stat_name} Value", min_value=0, value=sub_stat_initial_value, step=1, key=f"input_{b_stat_name}") # Changed to English
    input_stats[c_stat_name] = col1.number_input(f"{c_stat_name} Value", min_value=0, value=sub_stat_initial_value, step=1, key=f"input_{c_stat_name}") # Changed to English
    input_stats["Aggressiveness"] = st.number_input(f"Aggressiveness Value", min_value=3, value=aggressiveness_initial_value, step=1, key="input_Aggressiveness") # Changed to English

# Pet Town Facility Levels Section
with st.expander("\U0001F3D9️ Pet Town Facility Levels", expanded=False): # Changed to English
    management_office_level = st.slider("Management Office Level", min_value=0, max_value=20, value=0, step=1, key="mo_level") # Changed to English
    dormitory_level = st.slider("Dormitory Level", min_value=0, max_value=20, value=0, step=1, key="dorm_level") # Changed to English
    training_ground_level = st.slider("Training Ground Level", min_value=0, max_value=20, value=0, step=1, key="train_level") # Changed to English
    playground_level = st.slider("Playground Level", min_value=0, max_value=20, value=0, step=1, key="play_level") # Changed to English
    fence_level = st.slider("Fence Level", min_value=0, max_value=20, value=0, step=1, key="fence_level") # Changed to English

# Specialties Section
with st.expander("\U0001F3C1 Specialties", expanded=False): # Changed to English
    st.markdown("---")

    def render_specialty_section(title, category_session_key, specialty_options, max_stage):
        st.markdown(f"#### {title} Specialties") # Title in English
        
        if f"{category_session_key}_add_select_idx" not in st.session_state:
            st.session_state[f"{category_session_key}_add_select_idx"] = 0

        col_select, col_add = st.columns([0.7, 0.3])
        with col_select:
            selected_specialty_to_add = st.selectbox(
                f"Select Specialty to Add", # Text in English
                ["Select"] + specialty_options, # Text in English
                key=f"{category_session_key}_add_select",
                index=st.session_state[f"{category_session_key}_add_select_idx"]
            )
        with col_add:
            st.write("") 
            if st.button(f"Add {title} Specialty", key=f"{category_session_key}_add_btn"): # Button in English
                if selected_specialty_to_add != "Select": # Text in English
                    st.session_state[category_session_key].append(
                        {"type": selected_specialty_to_add, "stage": 0, "id": pd.Timestamp.now().timestamp()}
                    )
                    st.session_state[f"{category_session_key}_add_select_idx"] = 0 
                    st.rerun() 
                else:
                    st.warning("Please select a specialty to add.") # Warning in English

        st.markdown("---")
        if not st.session_state[category_session_key]:
            st.info("No specialties added yet.") # Text in English
        
        specialties_to_keep = []
        for i, spec in enumerate(st.session_state[category_session_key]):
            instance_key = f"{category_session_key}_{spec['type']}_{spec['id']}"

            col_spec_name, col_spec_stage, col_spec_delete = st.columns([0.4, 0.4, 0.2])
            with col_spec_name:
                st.write(f"**{spec['type']}**")
            with col_spec_stage:
                current_stage = st.slider(
                    f"{spec['type']} Stage", # Text in English
                    min_value=0, max_value=max_stage, value=spec["stage"], 
                    key=f"{instance_key}_stage"
                )
                spec["stage"] = current_stage 
            with col_spec_delete:
                st.write("") 
                if st.button("Delete", key=f"{instance_key}_delete"): # Button in English
                    st.session_state[category_session_key].remove(spec) 
                    st.rerun() 
                else:
                    specialties_to_keep.append(spec) 

        st.session_state[category_session_key] = specialties_to_keep

    # Novice Specialties (Level 4 Breakthrough)
    novice_specialty_types = [s for s in specialty_rewards_by_type_and_stage if s.startswith("Novice")] # Changed to English
    render_specialty_section("Novice (Level 4 Breakthrough)", "novice_specialties", novice_specialty_types, 3) 

    st.markdown("---")

    # Beginner Specialties (Level 9 Breakthrough)
    beginner_specialty_types = [s for s in specialty_rewards_by_type_and_stage if s.startswith("Beginner")] # Changed to English
    render_specialty_section("Beginner (Level 9 Breakthrough)", "beginner_specialties", beginner_specialty_types, 4) 

    st.markdown("---")

    # Raise Specialties (Level 14 Breakthrough)
    raise_specialty_types = [s for s in specialty_rewards_by_type_and_stage if s.startswith("Raise")] # Changed to English
    render_specialty_section("Raise (Level 14 Breakthrough)", "raise_specialties", raise_specialty_types, 5) 

    st.markdown("---") 

# ---------- Button ----------
if st.button("Calculate Results", key="calculate_btn"): # Button in English
    st.session_state["calculated"] = True

# ---------- Display Results ----------
if st.session_state["calculated"]:
    # Calculate total facility bonuses
    total_facility_bonuses = {stat: 0 for stat in all_stats_for_pure_calculation}
    
    facility_levels_map = {
        "Management Office": management_office_level,
        "Dormitory": dormitory_level,
        "Training Ground": training_ground_level,
        "Playground": playground_level,
        "Fence": fence_level
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
    
    # Calculate user's PURE stats (excluding Pet Town & Specialty bonuses)
    user_pure_stats = {}
    for stat_name in all_stats_for_pure_calculation:
        # Get initial base stat for calculation based on current pet type
        initial_base_for_calc = current_pet_initial_stats["sub_stat"]
        if stat_name == d_stat: # Main stat
            initial_base_for_calc = current_pet_initial_stats["main_stat"]
        if stat_name == "Aggressiveness": # Aggressiveness initial value
            initial_base_for_calc = current_pet_initial_stats["aggressiveness"]
        
        user_pure_stats[stat_name] = max(
            initial_base_for_calc, 
            input_stats[stat_name] - total_facility_bonuses[stat_name] - total_specialty_bonuses[stat_name]
        )
    
    user_total_pure = 0
    for stat_name in stat_order: # Aggressiveness is not included in total stat calculation
        if exclude_hp and stat_name == "HP": # Changed to English
            continue
        user_total_pure += user_pure_stats[stat_name]

    upgrades = level - 1 # Level 1 means 0 upgrades, Level 2 means 1 upgrade etc.

    # Run simulation for the currently selected pet type
    current_pet_total_sim_pure, current_pet_simulated_pure_stats = run_simulation(
        pet_type, upgrades, exclude_hp, d_stat, num_sim=100_000 # num_sim is defined inside the function for consistency
    )

    total_percentile = np.sum(current_pet_total_sim_pure > user_total_pure) / 100_000 * 100 # Use num_sim as defined for the simulation
    
    individual_percentiles = {}
    for stat_name in stat_order:
        individual_percentiles[stat_name] = np.sum(current_pet_simulated_pure_stats[stat_name] > user_pure_stats[stat_name]) / 100_000 * 100 # Use num_sim
    
    avg_increases = {}
    for stat_name in stat_order:
        initial_base_for_avg = current_pet_initial_stats["main_stat"] if stat_name == d_stat else current_pet_initial_stats["sub_stat"]
        avg_increases[stat_name] = (user_pure_stats[stat_name] - initial_base_for_avg) / upgrades if upgrades > 0 else 0

    st.success(f"\U0001F4CC Total Pure Stats (Excluding Town/Specialty Bonuses): {user_total_pure}") # Changed to English
    st.info(f"\U0001F4A1 Your pet is in the top {total_percentile:.2f}% of **{pet_type}** pets{', excluding HP' if exclude_hp else ''}.") # Changed to English

    # --- Cross-Comparison Percentile ---
    other_pet_type = "Abyssal Pet" if pet_type == "Normal Pet" else "Normal Pet" # Changed to English
    
    # Run simulation for the OTHER pet type
    other_pet_total_sim_pure, _ = run_simulation(
        other_pet_type, upgrades, exclude_hp, d_stat, num_sim=100_000 # Use num_sim
    )
    
    cross_percentile = np.sum(other_pet_total_sim_pure > user_total_pure) / 100_000 * 100 # Use num_sim
    st.info(f"\U0001F504 Your pet is in the top {cross_percentile:.2f}% when compared to **{other_pet_type}** pets{', excluding HP' if exclude_hp else ''}.") # Changed to English
    st.markdown("---")

    # Display individual stats including facility bonuses
    df_data = {
        "Stat": [],
        "Input Value (Incl. Town/Specialty)": [],
        "Pure Pet Stat (Excl. Town/Specialty)": [],
        "Bonus from Pet Town": [],
        "Bonus from Specialty": [],
        "Top % (Pure Stat Basis)": [],
        "Avg. Increase per Level (Excl. Town/Specialty)": []
    }

    for stat_name in stat_order: # Aggressiveness is not included in total stat calculation
        df_data["Stat"].append(stat_name)
        df_data["Input Value (Incl. Town/Specialty)"].append(input_stats[stat_name])
        df_data["Pure Pet Stat (Excl. Town/Specialty)"].append(user_pure_stats[stat_name])
        df_data["Bonus from Pet Town"].append(total_facility_bonuses[stat_name])
        df_data["Bonus from Specialty"].append(total_specialty_bonuses[stat_name])
        df_data["Top % (Pure Stat Basis)"].append(f"{individual_percentiles[stat_name]:.2f}%")
        df_data["Avg. Increase per Level (Excl. Town/Specialty)"].append(f"+{avg_increases[stat_name]:.2f}")

    # Add Aggressiveness stat separately
    df_data["Stat"].append("Aggressiveness") # Changed to English
    df_data["Input Value (Incl. Town/Specialty)"].append(input_stats["Aggressiveness"]) # Changed to English
    df_data["Pure Pet Stat (Excl. Town/Specialty)"].append(user_pure_stats["Aggressiveness"]) # Changed to English
    df_data["Bonus from Pet Town"].append(total_facility_bonuses["Aggressiveness"]) # Changed to English
    df_data["Bonus from Specialty"].append(total_specialty_bonuses["Aggressiveness"]) # Changed to English
    df_data["Top % (Pure Stat Basis)"].append("N/A")
    df_data["Avg. Increase per Level (Excl. Town/Specialty)"].append("N/A")

    df = pd.DataFrame(df_data)
    st.table(df)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(current_pet_total_sim_pure, bins=50, kde=True, ax=ax, color='skyblue')
    ax.axvline(user_total_pure, color='red', linestyle='--', label='Your Pet Pure Total Stats')
    ax.set_title(f"Overall Stat Distribution ({pet_type} - Pure Pet Stats){' (Excluding HP)' if exclude_hp else ''}") # Title includes pet type
    ax.set_xlabel("Total Stats") # Changed to English
    ax.legend()
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("Target Stats Input (Total Stats at Level 20)") # Changed to English
    calc_goal = st.checkbox("\U0001F3AF View Probability to Reach Level 20 Target Stats", key="calc_goal_checkbox") # Changed to English

    if calc_goal:
        target_stats = {}
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        target_stats[a_stat_name] = col_t1.number_input(f"{a_stat_name} Target", min_value=0, value=35, step=1, key=f"target_{a_stat_name}") # Changed to English
        target_stats[b_stat_name] = col_t2.number_input(f"{b_stat_name} Target", min_value=0, value=35, step=1, key=f"target_{b_stat_name}") # Changed to English
        target_stats[c_stat_name] = col_t3.number_input(f"{c_stat_name} Target", min_value=0, value=35, step=1, key=f"target_{c_stat_name}") # Changed to English
        target_stats[d_stat] = col_t4.number_input(f"{d_stat} Target (Main Stat)", min_value=0, value=100, step=1, key=f"target_{d_stat}") # Changed to English
        
        remaining_upgrades_to_20 = 20 - level if level < 20 else 0

        # Run simulation for target stats based on current pet type
        sim_at_20_data = initial_stats_data[pet_type]
        sim_at_20_main_stat_initial = sim_at_20_data["main_stat"]
        sim_at_20_sub_stat_initial = sim_at_20_data["sub_stat"]
        sim_at_20_ac_vals = sim_at_20_data["ac_vals"]
        sim_at_20_ac_probs = sim_at_20_data["ac_probs"]
        sim_at_20_d_vals = sim_at_20_data["d_vals"]
        sim_at_20_d_probs = sim_at_20_data["d_probs"]

        sim_pure_at_20 = {s: np.full(num_sim, sim_at_20_sub_stat_initial) for s in stat_order}
        sim_pure_at_20[d_stat] = np.full(num_sim, sim_at_20_main_stat_initial)

        for stat_name in stat_order:
            # Start from user's pure stats for the remaining upgrades
            sim_pure_at_20[stat_name] = np.full(num_sim, user_pure_stats[stat_name]) 
            if remaining_upgrades_to_20 > 0:
                if stat_name == d_stat:
                    sim_pure_at_20[stat_name] += np.random.choice(sim_at_20_d_vals, (num_sim, remaining_upgrades_to_20), p=sim_at_20_d_probs).sum(axis=1)
                else:
                    sim_pure_at_20[stat_name] += np.random.choice(sim_at_20_ac_vals, (num_sim, remaining_upgrades_to_20), p=sim_at_20_ac_probs).sum(axis=1)

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

        st.write(f"\U0001F539 Probability to reach {a_stat_name} target: **{probabilities[a_stat_name]:.2f}%**") # Changed to English
        st.write(f"\U0001F539 Probability to reach {b_stat_name} target: **{probabilities[b_stat_name]:.2f}%**") # Changed to English
        st.write(f"\U0001F539 Probability to reach {c_stat_name} target: **{probabilities[c_stat_name]:.2f}%**") # Changed to English
        st.write(f"\U0001F539 Probability to reach {d_stat} (Main Stat) target: **{probabilities[d_stat]:.2f}%**") # Changed to English
        st.success(f"\U0001F3C6 Probability to satisfy all targets simultaneously: **{p_all:.2f}%**") # Changed to English
