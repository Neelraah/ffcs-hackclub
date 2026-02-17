import json
import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

def compute_sentiment(comment_list):
    if not comment_list:
        return 0
    scores = [
        sia.polarity_scores(comment["review"])["compound"]
        for comment in comment_list
    ]
    return sum(scores) / len(scores)

st.subheader("Top Recommended Professors")
st.write("Based on your preference weights and rating confidence.")

@st.cache_data
def load_data():
    with open("AI/Dataset/sample_datset.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)

@st.cache_resource
def load_sentiment_model():
    nltk.download("vader_lexicon")
    return SentimentIntensityAnalyzer()

sia = load_sentiment_model()

df = load_data()

# Build course dictionary automatically
course_dict = {}

for courses in df["courses"]:
    for course in courses:
        course_dict[course["code"]] = course["title"]

course_options = sorted(course_dict.items(), key=lambda x: x[1])

selected_course = st.selectbox(
    "Select Course",
    ["All Courses"] + [f"{code} - {title}" for code, title in course_options]
)

if selected_course != "All Courses":
    selected_code = selected_course.split(" - ")[0]

    df = df[df["courses"].apply(
        lambda course_list: any(course["code"] == selected_code for course in course_list)
    )]

st.write("Max teaching score:", df["avg_teaching"].max())

# Derived features
df["no_of_reviews"] = df["comments"].apply(len)
max_reviews = df["no_of_reviews"].max()
df["confidence"] = df["no_of_reviews"] / max_reviews if max_reviews != 0 else 0
df["sentiment_score"] = df["comments"].apply(compute_sentiment)
df["sentiment_score"] = (df["sentiment_score"] + 1) / 2


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
sentiment_weight = st.slider("Student Sentiment Importance", 0, 100, 50) / 100

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

df["sentiment_factor"] = 1 + sentiment_weight * (df["sentiment_score"] - 0.5)
df["recommendation_score"] *= df["sentiment_factor"]


recommended = df.sort_values(by="recommendation_score", ascending=False)

st.table(
    recommended[["faculy_name", "recommendation_score", "confidence"]]
    .head(10)
)
