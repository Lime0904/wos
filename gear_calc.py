import streamlit as st
import pandas as pd
from io import StringIO

# Load CSV data
gear_df = pd.read_csv("data/gear_data.csv")
gear_levels = gear_df["Level"].tolist()

# Load package data
packages_df = pd.read_csv("data/packages.csv")

# Resource dictionary from gear data
resource_dict = {
    row["Level"]: {
        "Alloy": row["Alloy"],
        "Polish": row["Polish"],
        "Design": row["Design"],
        "Amber": row["Amber"]
    } for _, row in gear_df.iterrows()
}

# Group gear parts by unit type
gear_groups = {
    "Infantry": ["Coat", "Pants"],
    "Marksman": ["Ring", "Cudgel"],
    "Lancer": ["Hat", "Watch"]
}

gear_parts_eng = {
    "Hat": "Hat",
    "Coat": "Coat",
    "Ring": "Ring",
    "Watch": "Watch",
    "Pants": "Pants",
    "Cudgel": "Cudgel"
}

st.title("Chief Gear Resource Calculator")

user_inputs = {}
st.subheader("Current / Target Level for Each Gear")

for unit_type, parts in gear_groups.items():
    st.markdown(f"#### {unit_type}")
    for part in parts:
        part_label = gear_parts_eng[part]
        cols = st.columns(2)
        with cols[0]:
            cur = st.selectbox(
                f"{part_label} - Current",
                options=gear_levels,
                index=gear_levels.index("Gold"),
                key=f"{part}_cur"
            )
        with cols[1]:
            tar = st.selectbox(
                f"{part_label} - Target",
                options=gear_levels,
                index=gear_levels.index("Gold"),
                key=f"{part}_tar"
            )
        user_inputs[part_label] = (cur, tar)

st.markdown("---")
st.subheader("Your Resource Inventory")
res_cols = st.columns(4)
user_owned = {
    "Design": res_cols[0].number_input("Design Plans", min_value=0, value=0),
    "Alloy": res_cols[1].number_input("Alloy", min_value=0, value=0),
    "Polish": res_cols[2].number_input("Polishing Solution", min_value=0, value=0),
    "Amber": res_cols[3].number_input("Lunar Amber", min_value=0, value=0),
}

st.markdown("---")
st.subheader("Package Purchase Input")
package_counts = {}
package_cols = st.columns(5)
price_list = ["$5", "$10", "$20", "$50", "$100"]
for i, price in enumerate(price_list):
    with package_cols[i]:
        count = st.number_input(f"{price}", min_value=0, value=0, step=1, key=f"pkg_{price}")
        package_counts[price] = count

# Calculate total resource from packages
package_resources = {"Design": 0, "Alloy": 0, "Polish": 0, "Amber": 0, "Plans": 0, "DesignPlans": 0}
for price, count in package_counts.items():
    df = packages_df[packages_df["Package"] == price]
    for _, row in df.iterrows():
        res = row["Resource"]
        if res not in package_resources:
            package_resources[res] = 0
        package_resources[res] += row["Amount"] * count

# Merge package resource with user input
total_owned = {
    k: user_owned.get(k, 0) + package_resources.get(k, 0)
    for k in user_owned
}

if st.button("Calculate Deficit"):
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
    st.subheader("Resource Summary")

    result_data = []
    for k in user_owned:
        result_data.append({
            "Resource": k,
            "Required": total_needed[k],
            "Owned": total_owned.get(k, 0),
            "Deficit": max(0, total_needed[k] - total_owned.get(k, 0))
        })

    result_df = pd.DataFrame(result_data)
    st.dataframe(result_df, use_container_width=True)
