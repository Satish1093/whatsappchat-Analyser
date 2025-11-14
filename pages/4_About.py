# pages/4_About.py
import streamlit as st

st.title("ℹ️ About this project")
st.write("""
⭐ About – AI Chat Lab: 

Welcome to AI Chat Lab’s Analyzer — an intelligent, privacy-focused tool designed to transform raw chat exports into meaningful insights using AI-powered analytics.

This project combines Natural Language Processing (NLP), Data Visualization, and Statistical Analysis to help users better understand their AI conversations.
Whether you're exploring personal chats, group discussions, study groups, or business communication, the analyzer provides deep insights instantly.

🤖 What This AI Tool Does

Using AI and NLP techniques, the analyzer extracts and visualizes:

📊 Chat Statistics

Total messages, words, and characters

Most active users & message frequency

Media and link sharing patterns

First & last message timestamps

🎨 Visual Analytics

Daily & monthly activity graphs

Hourly heatmap showing peak chat times

Wordcloud visualization

Emoji usage breakdown

🧠 AI-Powered Text Insights

Sentiment analysis (positive/neutral/negative)

Auto-generated conversation summary

Keyword extraction & common word analysis

📄 Smart PDF Export

Generates a clean, professional analysis report

Fully Unicode-compatible (supports all emojis 👍🔥😂❤️)

Uses Noto fonts for accurate rendering

🔐 Privacy First — 100% Offline

All processing happens locally on your device.
No data is uploaded or stored anywhere.
Your chats stay completely secure.

🧰 Technologies Used

Python

Streamlit

NLTK / TextBlob

Pandas / NumPy

WordCloud

Seaborn / Matplotlib

FPDF (Unicode with Noto Emoji)

🚀 Why AI Chat Lab Built This

At AI Chat Lab, our goal is to make powerful AI and data tools accessible to everyone.
AI is one of the world’s most used communication platforms — but the exported chat format is difficult to analyze manually.

This analyzer converts plain text into:

Clear patterns

Visual stories

Emotional insights

AI-generated summaries

All with just one upload.

🌟 Future Roadmap

Topic detection using LLMs

Advanced emotion classification

AI-based conversation classifier

Chat comparison between two users

Multi-language support

Smart relationship insights dashboard
""")
