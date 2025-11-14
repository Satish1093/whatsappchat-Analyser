# pages/1_Analysis.py

import nltk
nltk.data.path.append(r"C:\Users\Arjun\PycharmProjects\whatsappchat\nltk_data")

import re
import streamlit as st
import pandas as pd
from helper import analyze_text, summarize_text, export_report_pdf
from wordcloud import WordCloud
from collections import Counter
import emoji
from urlextract import URLExtract
from pathlib import Path

st.title("📊 Chat Analysis")

# -------------------- UPLOAD --------------------
uploaded = st.file_uploader("📂 Upload  Chat (.txt)", type=["txt"])

if not uploaded:
    st.info("Upload a exported .txt file (Menu → Export chat → Without media).")
    st.stop()

raw = uploaded.read().decode("utf-8", errors="ignore")

with st.spinner("Analyzing chat..."):
    report = analyze_text(raw)

if "error" in report:
    st.error(report["error"])
    st.stop()

df_full = report["messages_df"].copy()

# -------------------- USER FILTER --------------------
user_list = sorted(df_full["user"].dropna().unique().tolist())
user_list.insert(0, "Overall")

selected_user = st.sidebar.selectbox("Select user", user_list)

df = df_full if selected_user == "Overall" else df_full[df_full["user"] == selected_user]

# -------------------- QUICK STATS --------------------
st.header(f"Overview — {selected_user}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Messages", df.shape[0])

col2.metric(
    "Total Words",
    sum(len(str(m).split()) for m in df["message"])
)

col3.metric(
    "Media Shared",
    df["message"].astype(str).str.contains("Media omitted", case=False).sum()
)

extractor = URLExtract()
col4.metric(
    "Links Shared",
    sum(len(extractor.find_urls(str(m))) for m in df["message"])
)

st.divider()

# -------------------- DAILY TIMELINE --------------------
if df["datetime"].notna().any():
    st.subheader("📅 Daily Timeline")
    daily = df.groupby(df["datetime"].dt.date).size().reset_index(name="messages")
    daily = daily.rename(columns={"datetime": "date"})
    st.line_chart(daily.set_index("date"))

# -------------------- MONTHLY TIMELINE --------------------
st.subheader("📆 Monthly Timeline")

df = df.copy()
df.loc[:, "month_name"] = df["datetime"].dt.month_name()

monthly = df["month_name"].value_counts().reset_index()
monthly.columns = ["month", "messages"]

st.bar_chart(monthly.set_index("month"))

st.divider()

# -------------------- TOP SENDERS --------------------
if selected_user == "Overall":
    st.subheader("🏆 Top Senders")
    st.table(pd.DataFrame(report["top_senders"], columns=["User", "Messages"]).head(20))

st.divider()

# -------------------- WORDCLOUD --------------------
st.subheader("🌥 Word Cloud")

text_blob = " ".join(df["message"].astype(str).tolist()).strip()

if text_blob:
    try:
        wc = WordCloud(width=900, height=450, background_color="white").generate(text_blob)
        st.image(wc.to_array(), width="stretch")
    except Exception:
        st.warning("WordCloud could not be generated.")
else:
    st.warning("No text available for WordCloud.")

st.divider()

# -------------------- MOST COMMON WORDS --------------------
st.subheader("🔤 Most Common Words")

words = []
for msg in df["message"].astype(str):
    words.extend(re.findall(r"\b[a-zA-Z]{2,}\b", msg.lower()))

common = Counter(words).most_common(25)
st.table(common)

st.divider()

# -------------------- EMOJI ANALYSIS --------------------
st.subheader("😀 Emoji Analysis")

emojis = []
for msg in df["message"].astype(str):
    emojis.extend([c for c in msg if c in emoji.EMOJI_DATA])

emoji_counts = Counter(emojis).most_common(30)
st.table(emoji_counts)

st.divider()

# -------------------- SUMMARY + PDF --------------------
st.subheader("📝 Quick Actions")

c1, c2 = st.columns(2)

with c1:
    summary_len = st.slider("Summary length (sentences)", 2, 10, 4)

    if st.button("Generate Summary"):
        text_blob = " ".join(df["message"].astype(str).tolist())
        summary = summarize_text(text_blob, max_sentences=summary_len)
        report["summary"] = summary
        st.success("Summary generated!")
        st.write(summary)

with c2:
    if st.button("Export PDF Report"):
        if "summary" not in report:
            report["summary"] = summarize_text(" ".join(df["message"].astype(str).tolist()), max_sentences=4)

        pdf_path = export_report_pdf(report, selected_user)

        with open(pdf_path, "rb") as f:
            data = f.read()

        st.download_button(
            "📥 Download PDF",
            data=data,
            file_name=f"whatsapp_report_{selected_user}.pdf",
            mime="application/pdf"
        )

        Path(pdf_path).unlink(missing_ok=True)
