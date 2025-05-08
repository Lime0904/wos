import streamlit as st
import pandas as pd
from io import StringIO

# secrets.toml에서 csv 데이터 불러오기
csv_data = st.secrets["gear_data"]["csv"]
df = pd.read_csv(StringIO(csv_data))
gear_levels = df["Level"].tolist()

# 자원 딕셔너리
resource_dict = {
    row["Level"]: {
        "Alloy": row["Alloy"],
        "Polish": row["Polish"],
        "Design": row["Design"],
        "Amber": row["Amber"]
    } for _, row in df.iterrows()
}

# 등급 한국어 매핑
level_labels = {
    "Green": "고급", "Green 1*": "고급 1성",
    "Blue": "레어", "Blue 1*": "레어 1성", "Blue 2*": "레어 2성", "Blue 3*": "레어 3성",
    "Purple": "에픽", "Purple 1*": "에픽 1성", "Purple 2*": "에픽 2성", "Purple 3*": "에픽 3성",
    "Purple T1": "에픽 T1", "Purple T1 1*": "에픽 T1 1성", "Purple T1 2*": "에픽 T1 2성", "Purple T1 3*": "에픽 T1 3성",
    "Gold": "레전드", "Gold 1*": "레전드 1성", "Gold 2*": "레전드 2성", "Gold 3*": "레전드 3성",
    "Gold T1": "레전드 T1", "Gold T1 1*": "레전드 T1 1성", "Gold T1 2*": "레전드 T1 2성", "Gold T1 3*": "레전드 T1 3성",
    "Gold T2": "레전드 T2", "Gold T2 1*": "레전드 T2 1성", "Gold T2 2*": "레전드 T2 2성", "Gold T2 3*": "레전드 T2 3성",
    "Legendary": "신화", "Legendary 1*": "신화 1성", "Legendary 2*": "신화 2성", "Legendary 3*": "신화 3성",
    "Legendary T1": "신화 T1", "Legendary T1 1*": "신화 T1 1성", "Legendary T1 2*": "신화 T1 2성", "Legendary T1 3*": "신화 T1 3성",
    "Legendary T2": "신화 T2", "Legendary T2 1*": "신화 T2 1성", "Legendary T2 2*": "신화 T2 2성", "Legendary T2 3*": "신화 T2 3성",
    "Legendary T3": "신화 T3", "Legendary T3 1*": "신화 T3 1성", "Legendary T3 2*": "신화 T3 2성", "Legendary T3 3*": "신화 T3 3성",
}

# 병종별 장비 부위 묶음
gear_groups = {
    "방패병": ["Coat", "Pants"],
    "궁병": ["Ring", "Cudgel"],
    "창병": ["Hat", "Watch"]
}

gear_parts_kor = {
    "Hat": "모자",
    "Coat": "상의",
    "Ring": "반지",
    "Watch": "시계",
    "Pants": "하의",
    "Cudgel": "지팡이"
}

st.title("Chief Gear 부족 자원 계산기")

user_inputs = {}

st.subheader("장비별 현재/목표 등급")

for troop_type, parts in gear_groups.items():
    st.markdown(f"#### {troop_type}")
    for part in parts:
        part_kor = gear_parts_kor[part]
        cols = st.columns(2)
        with cols[0]:
            cur = st.selectbox(f"{part_kor} - 현재", options=gear_levels, format_func=lambda x: level_labels.get(x, x), index=gear_levels.index("Gold"), key=f"{part}_cur")
        with cols[1]:
            tar = st.selectbox(f"{part_kor} - 목표", options=gear_levels, format_func=lambda x: level_labels.get(x, x), index=gear_levels.index("Gold"), key=f"{part}_tar")
        user_inputs[part_kor] = (cur, tar)

st.markdown("---")
st.subheader("현재 보유 자원")
res_cols = st.columns(4)
user_owned = {
    "Design": res_cols[0].number_input("설계도면", min_value=0, value=0),
    "Alloy": res_cols[1].number_input("합금", min_value=0, value=0),
    "Polish": res_cols[2].number_input("윤활제", min_value=0, value=0),
    "Amber": res_cols[3].number_input("앰버", min_value=0, value=0),
}

if st.button("부족 자원 계산"):
    total_needed = {k: 0 for k in user_owned}

    for part, (cur, tar) in user_inputs.items():
        i1 = gear_levels.index(cur)
        i2 = gear_levels.index(tar)
        if i1 >= i2:
            continue
        for level in gear_levels[i1+1:i2+1]:
            for k in total_needed:
                total_needed[k] += resource_dict.get(level, {}).get(k, 0)
    st.markdown("---")
    st.subheader("결과 요약")

    name_map = {
        "Design": "설계도면",
        "Alloy": "합금",
        "Polish": "윤활제",
        "Amber": "앰버"
    }

    result_data = []
    for k in user_owned:
        result_data.append({
            "자원": name_map.get(k, k),
            "총 필요량": total_needed[k],
            "보유량": user_owned.get(k, 0),
            "부족량": max(0, total_needed[k] - user_owned.get(k, 0))
        })

    result_df = pd.DataFrame(result_data)
    st.dataframe(result_df, use_container_width=True)