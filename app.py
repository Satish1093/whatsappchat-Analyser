# app.py.(Home + Navbar)
import nltk

# download minimal data quietly if not present
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)



import streamlit as st
from PIL import Image


# ------------------ Page Config ------------------
st.set_page_config(
    page_title="AI CHAT LAB",
    page_icon="💬",
    layout="wide"
)

# ------------------ Custom CSS ------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #e9f0ff 0%, #ffffff 100%);
}

/* Header */
.header {
    text-align: center;
    padding: 35px 0 10px 0;
}
.header h1 {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 6px;
}

/* Navbar */
.navbar {
    display: flex;
    justify-content: center;
    gap: 25px;
    padding-bottom: 20px;
}
.navbar a {
    font-weight: 600;
    font-size: 17px;
    text-decoration: none;
    color: #2a2a2a;
}
.navbar a:hover {
    color: #4a77ff;
}
</style>
""", unsafe_allow_html=True)


# ------------------ Header ------------------
st.markdown("""
<div class="header">
    <h1>💬 AI CHAT LAB</h1>
    <p>Upload, explore and extract insights from your WhatsApp chats.</p>
</div>
""", unsafe_allow_html=True)


# ------------------ Navbar (Links to Streamlit Pages) ------------------
st.markdown("""
<style>
.nav-item {
    font-size: 18px;
    font-weight: 600;
    padding: 8px 16px;
    display: inline-block;
    cursor: pointer;
}
.nav-item:hover {
    color: #4a77ff;
}
</style>
""", unsafe_allow_html=True)

cols = st.columns(4)

with cols[0]:
    if st.button("Analysis"):
        st.switch_page("pages/1_Analysis.py")

with cols[1]:
    if st.button("Heatmap"):
        st.switch_page("pages/2_Heatmap.py")

with cols[2]:
    if st.button("Sentiment"):
        st.switch_page("pages/3_Sentiment_Analysis.py")

with cols[3]:
    if st.button("About"):
        st.switch_page("pages/4_About.py")


# ------------------ Homepage Image ------------------
try:
    image = Image.open("frontend/Homepage.png")

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image(image, width="stretch")

except Exception as e:
    st.warning("⚠ Homepage image not found. Add it in: `frontend/Homepage.png`")


# ------------------ Upload Section ------------------
st.markdown("### 📂 Upload your  Chat (.txt)")

uploaded_file = st.file_uploader("Choose a export text file", type=["txt"])

if uploaded_file is not None:
    st.success("✅ File uploaded successfully! Go to **Analysis** page ➡")
