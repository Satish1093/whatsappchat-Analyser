# pages/2_Heatmap.py

import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from helper import analyze_text
import pandas as pd

st.title("📈 Activity Heatmap")

# -------------------- UPLOAD --------------------
uploaded = st.file_uploader("📂 Upload  chat (.txt)", type=["txt"])

if not uploaded:
    st.info("Upload exported chat (.txt) to generate heatmap.")
    st.stop()

raw = uploaded.read().decode("utf-8", errors="ignore")

with st.spinner("Processing chat..."):
    report = analyze_text(raw)

if "error" in report:
    st.error(report["error"])
    st.stop()

df = report["messages_df"].copy()

# -------------------- CHECK DATETIME --------------------
if not df["datetime"].notna().any():
    st.warning("⚠ Datetime could not be extracted. Heatmap unavailable for this chat.")
    st.stop()

# Ensure required columns exist
df["day_name"] = df["datetime"].dt.day_name()
df["hour"] = df["datetime"].dt.hour

# -------------------- HEATMAP DATA --------------------
heat = (
    df.pivot_table(
        index="day_name",
        columns="hour",
        values="message",
        aggfunc="count",
        fill_value=0
    )
)

# Reorder weekdays consistently
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heat = heat.reindex(weekday_order)

st.subheader("🗓 Weekly Activity Heatmap")

# -------------------- PLOT --------------------
fig, ax = plt.subplots(figsize=(14, 5))

sns.heatmap(
    heat,
    cmap="PuBuGn",
    linewidths=0.5,
    linecolor="white",
    cbar_kws={"label": "Message Count"},
    ax=ax
)

ax.set_xlabel("Hour of Day (0–23)")
ax.set_ylabel("Day of Week")

st.pyplot(fig)

st.success("Heatmap generated successfully!")
