import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit.components.v1 as components
import json
from datetime import datetime

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
if "result_json" not in st.session_state:
    st.session_state["result_json"] = None
if "load_json_str" not in st.session_state:
    st.session_state["load_json_str"] = ""

# 견종별 주스탯 매핑
d_stat_map = {
    "도베르만": "충성심",
    "비글": "속도",
    "셰퍼드": "인내력",
    "늑대": "체력"
}
stat_order = ["인내력", "충성심", "속도", "체력"]

# --- 사용자 입력 ---
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

# --- 시뮬레이션 상수 ---
num_sim = 100_000
ac_vals = [0,1,2,3]
ac_probs = [0.15,0.5,0.3,0.05]
d_vals = [1,2,3,4,5,6,7]
d_probs = [0.05,0.15,0.3,0.2,0.15,0.1,0.05]

if st.button("결과 계산"):
    st.session_state["calculated"] = True

# 결과 계산 및 출력
if st.session_state["calculated"]:
    upgrades = level - 1
    a_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    b_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    c_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    d_sim = 14 + np.random.choice(d_vals, (num_sim, upgrades), p=d_probs).sum(axis=1)

    user_total = 0
    total_sim = np.zeros(num_sim)
    for stat_name, user_val, sim_val in zip([a_stat,b_stat,c_stat,d_stat], [a,b,c,d], [a_sim,b_sim,c_sim,d_sim]):
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
        "스탯": [a_stat,b_stat,c_stat,d_stat],
        "현재 수치": [a,b,c,d],
        "상위 %": [f"{a_percentile:.2f}%", f"{b_percentile:.2f}%", f"{c_percentile:.2f}%", f"{d_percentile:.2f}%"],
        "Lv당 평균 증가량": [f"+{inc_a:.2f}", f"+{inc_b:.2f}", f"+{inc_c:.2f}", f"+{inc_d:.2f}"]
    })
    st.table(df)

    fig, ax = plt.subplots(figsize=(10,4))
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

    # 결과 JSON 생성
    result_obj = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": "무명",
        "category": category,
        "level": level,
        "total": user_total,
        "detail": {
            a_stat: a,
            b_stat: b,
            c_stat: c,
            d_stat: d,
        }
    }
    st.session_state["result_json"] = json.dumps(result_obj)

# ----------------- JSON 직접 입력 및 불러오기 UI -----------------
st.markdown("---")
st.subheader("저장된 기록 불러오기")

load_json_str = st.text_area("불러올 JSON 문자열을 여기에 붙여넣기 또는 저장 목록에서 선택", height=150, value=st.session_state["load_json_str"])

if st.button("불러오기"):
    try:
        load_obj = json.loads(load_json_str)
        st.session_state["calculated"] = True
        st.session_state["load_json_str"] = load_json_str
        # 입력 폼 자동 반영용
        category = load_obj.get("category", category)
        level = load_obj.get("level", level)
        detail = load_obj.get("detail", {})
        a = detail.get(a_stat, a)
        b = detail.get(b_stat, b)
        c = detail.get(c_stat, c)
        d = detail.get(d_stat, d)

        # 입력값 덮어쓰기 (세션 상태 혹은 변수 수정 필요)
        # Streamlit 구조상 입력값이 변수화되어 있으니 reload 버튼이나 전체 페이지 리렌더를 권장합니다.

        st.success("불러오기 성공! 위 입력값을 다시 확인하고 결과 계산을 눌러주세요.")
    except Exception as e:
        st.error(f"불러오기 실패: {e}")

# ----------------- 저장 목록 보여주기 & 선택 기능 (localStorage 활용) -----------------

# Streamlit에서 JS 로컬스토리지 접근은 JS 코드로 처리, 아래는 JS 코드

result_json = st.session_state.get("result_json", "null")

js_code = f"""
<script>
const result = {result_json};

function saveResult() {{
    if (!result) {{
        alert('저장할 결과가 없습니다.');
        return;
    }}
    let history = JSON.parse(localStorage.getItem('petSimHistory') || '[]');

    let isDuplicate = history.some(h =>
        h.name === result.name &&
        h.total === result.total &&
        JSON.stringify(h.detail) === JSON.stringify(result.detail)
    );
    if (isDuplicate) {{
        alert('이미 같은 기록이 있습니다.');
        return;
    }}

    history.push(result);
    history.sort((a,b) => new Date(b.time) - new Date(a.time));
    localStorage.setItem('petSimHistory', JSON.stringify(history));
    alert('저장 완료!');

    showHistory();
}}

function showHistory() {{
    let history = JSON.parse(localStorage.getItem('petSimHistory') || '[]');
    if(history.length === 0) {{
        document.getElementById('history_buttons').innerHTML = '저장된 기록이 없습니다.';
        return;
    }}
    let html = '';
    for(let i=0; i<history.length; i++) {{
        let r = history[i];
        let name_display = r.name ? r.name : '무명';
        html += '<button onclick="loadHistoryItem(' + i + ')" style="margin:2px; width:100%;">' + name_display + ' (' + r.time + ') 총합: ' + r.total + '</button><br/>';
    }}
    document.getElementById('history_buttons').innerHTML = html;
}}

function loadHistoryItem(idx) {{
    let history = JSON.parse(localStorage.getItem('petSimHistory') || '[]');
    if (history.length > idx) {{
        let item = history[idx];
        // 부모 Streamlit 앱의 텍스트박스 값을 직접 수정 불가능해서
        // 대신 alert로 JSON 보여주고 복사 권장
        alert("불러올 JSON:\n" + JSON.stringify(item, null, 2));
    }}
}}

window.onload = function() {{
    showHistory();
}};
</script>

<button onclick="saveResult()">💾 저장하기 (localStorage)</button>
<div id="history_buttons" style="margin-top:10px; font-weight:bold; max-height: 300px; overflow-y: auto;"></div>
"""

components.html(js_code, height=400)
