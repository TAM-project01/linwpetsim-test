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
if "loaded_json_str" not in st.session_state:
    st.session_state["loaded_json_str"] = ""

d_stat_map = {
    "도베르만": "충성심",
    "비글": "속도",
    "셰퍼드": "인내력",
    "늑대": "체력"
}
stat_order = ["인내력", "충성심", "속도", "체력"]
category_list = list(d_stat_map.keys())

# 이름 입력
name = st.text_input("이름 입력", value="무명")

# 불러오기용 텍스트 박스
loaded_json_str = st.text_area("불러온 기록 JSON (버튼 클릭 후 불러오기 클릭)", height=140, value=st.session_state["loaded_json_str"], key="loaded_json")

if st.button("불러오기"):
    try:
        loaded_data = json.loads(loaded_json_str)
        # 데이터 검증 - 필수 키 존재 여부 간단 확인
        required_keys = ["category", "name", "level", "detail"]
        if not all(k in loaded_data for k in required_keys):
            st.error(f"불러온 JSON에 필수 키가 없습니다: {required_keys}")
        else:
            st.session_state["loaded_json_str"] = loaded_json_str
            st.session_state["load_category"] = loaded_data.get("category", category_list[0])
            st.session_state["load_name"] = loaded_data.get("name", "무명")
            st.session_state["load_level"] = loaded_data.get("level", 2)
            st.session_state["load_detail"] = loaded_data.get("detail", {})
            st.success("기록을 성공적으로 불러왔습니다.")
    except Exception as e:
        st.error(f"불러오기 실패: 올바른 JSON 형식인지 확인하세요.\n오류: {e}")

# 불러온 데이터가 있으면 우선으로 UI 세팅
category = st.session_state.get("load_category", category_list[0])
name = st.session_state.get("load_name", name)
level = st.session_state.get("load_level", 2)
detail = st.session_state.get("load_detail", {})

category = st.selectbox("\U0001F436 견종 선택", category_list, index=category_list.index(category))
d_stat = d_stat_map[category]
remaining_stats = [s for s in stat_order if s != d_stat]
a_stat, b_stat, c_stat = remaining_stats

exclude_hp = st.checkbox("\U0001F6D1 체력 스탯 제외하고 계산하기")

col1, col2 = st.columns(2)

a = detail.get(a_stat, 6)
b = detail.get(b_stat, 6)
c = detail.get(c_stat, 6)
d = detail.get(d_stat, 14)

level = col1.number_input("레벨 (2 이상)", min_value=2, value=level, step=1)
a = col1.number_input(f"{a_stat} 수치", min_value=0, value=a, step=1)
b = col2.number_input(f"{b_stat} 수치", min_value=0, value=b, step=1)
c = col1.number_input(f"{c_stat} 수치", min_value=0, value=c, step=1)
d = col2.number_input(f"{d_stat} 수치", min_value=0, value=d, step=1)

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

    # 결과 JSON 생성 및 저장
    result_obj = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": name,
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
    st.session_state["result_json"] = json.dumps(result_obj, ensure_ascii=False)
else:
    result_obj = None

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
        html += '<button onclick="loadHistoryItem(' + i + ')" style="margin:2px;">' +
                (r.name || '무명') + ' (' + r.time + ') 총합: ' + r.total + '</button><br/>';
    }}
    document.getElementById('history_buttons').innerHTML = html;
}}

function loadHistoryItem(idx) {{
    let history = JSON.parse(localStorage.getItem('petSimHistory') || '[]');
    if (history.length > idx) {{
        let item = history[idx];
        const textarea = window.parent.document.querySelector('textarea[id="loaded_json"]');
        if (textarea) {{
            textarea.value = JSON.stringify(item, null, 2);
            textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
            alert('불러온 기록 JSON이 텍스트 박스에 복사되었습니다. 상단 "불러오기" 버튼을 눌러 적용하세요.');
        }} else {{
            alert('불러오기용 텍스트 박스를 찾을 수 없습니다.');
        }}
    }}
}}

window.onload = function() {{
    showHistory();
}};
</script>

<button onclick="saveResult()">💾 저장하기 (localStorage)</button>
<div id="history_buttons" style="margin-top:10px; font-weight:bold;"></div>
"""

components.html(js_code, height=450)
