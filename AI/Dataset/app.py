import json
import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

st.subheader("Top Recommended Professors")
st.write("Based on your preference weights and rating confidence.")

@st.cache_data
def load_data():
    with open("AI/Dataset/sample_datset.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)

df = load_data()

# Derived features
df["no_of_reviews"] = df["comments"].apply(len)
df["confidence"] = df["no_of_reviews"] / df["no_of_reviews"].max()

# Scale rating columns
scaler = MinMaxScaler()
columns_to_scale = [
    "avg_teaching",
    "avg_attendance_flex",
    "avg_supportiveness",
    "avg_marks",
    "avg_overall"
]

df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])

# Sliders
avg_teaching = st.slider("Average Teaching", 0, 100, 100) / 100
avg_attendance_flex = st.slider("Average Attendance Flex", 0, 100, 100) / 100
avg_supportiveness = st.slider("Average Supportiveness", 0, 100, 100) / 100
avg_marks = st.slider("Average Marks", 0, 100, 100) / 100
avg_overall = st.slider("Average Overall", 0, 100, 100) / 100

weights = {
    "avg_teaching": avg_teaching,
    "avg_attendance_flex": avg_attendance_flex,
    "avg_supportiveness": avg_supportiveness,
    "avg_marks": avg_marks,
    "avg_overall": avg_overall
}

# Normalize weights
total_weight = sum(weights.values())
if total_weight == 0:
    total_weight = 1

weights = {k: v / total_weight for k, v in weights.items()}

# Score calculation
df["recommendation_score"] = (
    df["avg_teaching"] * weights["avg_teaching"] +
    df["avg_attendance_flex"] * weights["avg_attendance_flex"] +
    df["avg_supportiveness"] * weights["avg_supportiveness"] +
    df["avg_marks"] * weights["avg_marks"] +
    df["avg_overall"] * weights["avg_overall"]
)

# Confidence boost
df["recommendation_score"] *= (0.7 + 0.3 * df["confidence"])

recommended = df.sort_values(by="recommendation_score", ascending=False)

st.table(
    recommended[["faculy_name", "recommendation_score", "confidence"]]
    .head(10)
)
