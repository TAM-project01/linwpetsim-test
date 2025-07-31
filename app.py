import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_title="펫 시뮬레이터", layout="wide")

st.title("🐾 펫 스탯 시뮬레이터")
st.markdown("개별 시뮬 결과를 저장하고 나중에 불러올 수 있습니다.")

# ---------- 시뮬레이션 입력 ----------
name = st.text_input("견종 이름", value="무명")
level = st.number_input("레벨", min_value=1, max_value=20, value=1)
main_stat = st.number_input("주 스탯", min_value=0, value=20)
sub_stats = {
    "힘": st.number_input("부스탯 - 힘", min_value=0, value=7),
    "지능": st.number_input("부스탯 - 지능", min_value=0, value=7),
    "체력": st.number_input("부스탯 - 체력", min_value=0, value=7),
}

if st.button("🎲 시뮬레이션 실행"):
    total = main_stat + sum(sub_stats.values())
    result = {
        "name": name,
        "level": level,
        "main_stat": main_stat,
        "sub_stats": sub_stats,
        "total": total,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detail": {
            "주스탯": main_stat,
            "부스탯": sub_stats,
        }
    }
    st.session_state["result_json"] = json.dumps(result, ensure_ascii=False)
    st.success("✅ 시뮬레이션 결과가 생성되었습니다!")

# ---------- 시뮬 결과 JSON 보여주기 ----------
if "result_json" in st.session_state:
    st.text_area("🔍 결과 JSON", st.session_state["result_json"], height=200)

# ---------- 저장/불러오기 기능 ----------
result_json = st.session_state.get("result_json")
if result_json is None:
    result_json = "{}"

# JS 문자열로 안전하게 escape
js_result_str = json.dumps(result_json)

# JavaScript 코드 삽입
js_code = f"""
<script>
const result = JSON.parse({js_result_str});

function saveResult() {{
    if (!result || Object.keys(result).length === 0) {{
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
    let container = document.getElementById('history_buttons');
    if (!container) return;

    if (history.length === 0) {{
        container.innerHTML = '저장된 기록이 없습니다.';
        return;
    }}

    let html = '';
    for (let i = 0; i < history.length; i++) {{
        let r = history[i];
        html += `<button onclick="loadHistoryItem(${i})" style="margin:2px;">${{r.name || '무명'}} (${{r.time}}) 총합: ${{r.total}}</button><br/>`;
    }}
    container.innerHTML = html;
}}

function loadHistoryItem(idx) {{
    let history = JSON.parse(localStorage.getItem('petSimHistory') || '[]');
    if (history.length > idx) {{
        let item = history[idx];
        const textarea = window.parent.document.querySelector('textarea');
        if (textarea) {{
            textarea.value = JSON.stringify(item, null, 2);
            textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
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

st.components.v1.html(js_code, height=400)
