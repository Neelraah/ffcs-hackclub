import json
import pandas as pd
import streamlit as st
with open("AI/Dataset/sample_datset.json", "r", encoding="utf-8") as f:
  data = json.load(f)
df = pd.DataFrame(data)
df["no_of_reviews"] = df["comments"].apply(len)
# print(df[["faculy_name", "no_of_reviews"]].head())

avg_teaching = st.slider("Average Teaching", 0, 100, 100) / 100
avg_attendance_flex = st.slider("Average Attendance Flex", 0, 100, 100) / 100
avg_supportiveness = st.slider("Average Supportiveness", 0, 100, 100) / 100
avg_marks = st.slider("Average Marks", 0, 100, 100) / 100
avg_overall = st.slider("Average Overall", 0, 100, 100) / 100
no_of_reviews = st.slider("Number of reviews", 0, 100, 100) / 100

weights = {
    "avg_teaching": avg_teaching,
    "avg_attendance_flex": avg_attendance_flex,
    "avg_supportiveness": avg_supportiveness,
    "avg_marks": avg_marks,
    "avg_overall": avg_overall,
    "no_of_reviews": no_of_reviews
}

# Convert to list
weight_values = list(weights.values())
total_weight = sum(weight_values)

# Prevent divide by zero
if total_weight == 0:
    total_weight = 1

# Normalize
weights = {k: v / total_weight for k, v in weights.items()}

df["recommendation_score"] = (
    df["avg_teaching"] * weights["avg_teaching"] +
    df["avg_attendance_flex"] * weights["avg_attendance_flex"] +
    df["avg_supportiveness"] * weights["avg_supportiveness"] +
    df["avg_marks"] * weights["avg_marks"] +
    df["avg_overall"] * weights["avg_overall"] +
    df["no_of_reviews"] * weights["no_of_reviews"]
)

recommended = df.sort_values(by="recommendation_score", ascending=False)
st.table(recommended[["faculy_name", "recommendation_score"]].head(10))