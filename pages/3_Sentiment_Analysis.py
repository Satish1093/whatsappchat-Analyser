# pages/3_Sentiment_Analysis.py

import streamlit as st
import pandas as pd
from helper import analyze_text

st.title("💟 Sentiment Analysis")

# -------------------- Upload Section --------------------
uploaded = st.file_uploader("📂 Upload  chat (.txt)", type=["txt"])
if not uploaded:
    st.info("Upload exported chat (.txt) to analyze sentiment.")
    st.stop()

raw = uploaded.read().decode("utf-8", errors="ignore")

with st.spinner("Analyzing chat for sentiment..."):
    report = analyze_text(raw)

if "error" in report:
    st.error(report["error"])
    st.stop()

df = report["messages_df"].copy()

# -------------------- Check if sentiment exists --------------------
if "sentiment" not in df.columns:
    st.warning("⚠ Sentiment scores missing — analysis unavailable.")
    st.stop()

# Replace NaN sentiment values
df["sentiment"] = df["sentiment"].fillna(0)

# -------------------- Average sentiment --------------------
st.subheader("💬 Overall Chat Sentiment")

avg_sent = df["sentiment"].mean()
sent_label = (
    "😊 Positive" if avg_sent > 0.1 else
    "😐 Neutral" if -0.1 <= avg_sent <= 0.1 else
    "😡 Negative"
)

st.metric("Average Polarity", f"{avg_sent:.3f}", help="Ranges from -1 (negative) to +1 (positive)")
st.write(f"Overall sentiment: **{sent_label}**")

st.divider()

# -------------------- Sentiment Over Time --------------------
if df["datetime"].notna().any():
    st.subheader("📈 Sentiment Over Time")

    df_plot = (
        df.dropna(subset=["datetime"])
          .set_index("datetime")
          .resample("D")["sentiment"]
          .mean()
          .fillna(0)
    )

    st.line_chart(df_plot)

else:
    st.warning("⚠ Datetime parsing failed — sentiment timeline unavailable.")
