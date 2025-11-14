# helper.py — FINAL STABLE VERSION WITH SAFE PDF WRITER & EMOJI SUPPORT

import re
import os
import io
import tempfile
import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import emoji
from urlextract import URLExtract
from preprocessor import preprocess
from textblob import TextBlob

# NLTK safe import
import nltk
# NOTE: adjust this path if your nltk_data is located elsewhere
nltk.data.path.append(r"C:\Users\Arjun\PycharmProjects\whatsappchat\nltk_data")
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords


# --------------------------------------------------------
#                MAIN ANALYSIS FUNCTION
# --------------------------------------------------------
def analyze_text(raw):
    """
    Parse WhatsApp export text and return analytics dictionary.
    """
    text = preprocess(raw)

    # Pattern: 12/31/20, 11:59 PM - Name: message
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}\s*[APMapm]{2})\s*-\s*([^:]+):\s*(.*)$'
    messages = []

    for line in text.splitlines():
        line = line.strip()
        match = re.match(pattern, line)
        if match:
            date_str, time_str, user, msg = match.groups()
            messages.append([date_str, time_str, user.strip(), msg])
        else:
            # continuation of previous message
            if messages:
                messages[-1][3] += " " + line

    if not messages:
        return {"error": "Chat format not recognized. Upload original WhatsApp export (.txt)."}

    df = pd.DataFrame(messages, columns=["date", "time", "user", "message"])

    # Convert to datetime (best-effort)
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"], errors="coerce")

    # Derived columns
    df["only_date"] = df["datetime"].dt.date
    df["month"]     = df["datetime"].dt.month_name()
    df["day_name"]  = df["datetime"].dt.day_name()
    df["year"]      = df["datetime"].dt.year
    df["hour"]      = df["datetime"].dt.hour

    # Basic metrics
    total_messages = len(df)
    total_words = sum(len(str(m).split()) for m in df["message"])

    extractor = URLExtract()
    links_shared = sum(len(extractor.find_urls(str(m))) for m in df["message"])

    media_shared = df[df["message"].str.contains("<Media omitted>", na=False)].shape[0]

    # Timelines
    monthly_timeline = df.groupby([df["year"], df["month"]]).size().reset_index(name="count")
    daily_timeline   = df.groupby("only_date").size().reset_index(name="count")

    # Busiest
    most_busy_day   = df["day_name"].value_counts().reset_index().rename(columns={"index": "day", "day_name": "count"})
    most_busy_month = df["month"].value_counts().reset_index().rename(columns={"index": "month", "month": "count"})
    most_busy_users = df["user"].value_counts().reset_index().rename(columns={"index": "user", "user": "messages"})

    # Emoji analysis
    all_emojis = []
    for msg in df["message"].astype(str):
        all_emojis.extend([c for c in msg if c in emoji.EMOJI_DATA])
    emoji_analysis = Counter(all_emojis).most_common(50)

    # Wordcloud image (bytes)
    text_blob = " ".join(df["message"].astype(str).tolist())
    wc = WordCloud(width=800, height=400, background_color="white").generate(text_blob)
    buf = io.BytesIO()
    wc.to_image().save(buf, format="PNG")
    buf.seek(0)
    wordcloud_bytes = buf.getvalue()

    # Common words
    words = []
    for msg in df["message"].astype(str):
        for w in re.findall(r"[a-zA-Z]{2,}", msg.lower()):
            words.append(w)
    common_words = Counter(words).most_common(100)

    # Sentiment (TextBlob)
    def sentiment_score(s):
        try:
            return TextBlob(s).sentiment.polarity
        except:
            return 0.0
    df["sentiment"] = df["message"].astype(str).apply(sentiment_score)

    overview = {
        "total_messages": total_messages,
        "total_words": total_words,
        "media_shared": media_shared,
        "links_shared": links_shared,
        "first_message": str(df["datetime"].dropna().iloc[0]) if df["datetime"].notna().any() else None,
        "last_message": str(df["datetime"].dropna().iloc[-1]) if df["datetime"].notna().any() else None
    }

    return {
        "messages_df": df,
        "overview": overview,
        "top_senders": list(most_busy_users.itertuples(index=False, name=None)),
        "emoji_analysis": emoji_analysis,
        "most_common_words": common_words,
        "wordcloud_image_bytes": wordcloud_bytes,
        "monthly_timeline": monthly_timeline.to_dict(orient="records"),
        "daily_timeline": daily_timeline.to_dict(orient="records"),
        "most_busy_day": most_busy_day.to_dict(orient="records"),
        "most_busy_month": most_busy_month.to_dict(orient="records"),
        "most_busy_users": most_busy_users.to_dict(orient="records"),
        "sentiment_series": df[["datetime", "sentiment"]].dropna().to_dict(orient="records")
    }


# --------------------------------------------------------
#                SUMMARIZER
# --------------------------------------------------------
def summarize_text(text, max_sentences=4):
    """
    Simple extractive summarizer (sentence scoring by frequency).
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    sentences = sent_tokenize(text)
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    stop_words = set(stopwords.words("english"))
    freq = {}
    for word in word_tokenize(text.lower()):
        if word.isalpha() and word not in stop_words:
            freq[word] = freq.get(word, 0) + 1

    scored = []
    for sent in sentences:
        score = sum(freq.get(w, 0) for w in word_tokenize(sent.lower()))
        scored.append((sent, score))

    top = sorted(scored, key=lambda x: x[1], reverse=True)[:max_sentences]
    selected = [s for s in sentences if s in dict(top)]
    return " ".join(selected)


# --------------------------------------------------------
#       SAFE TEXT WRITER (avoids multi_cell Unicode crash)
# --------------------------------------------------------
def _safe_write(pdf, text, font_name="Noto", font_size=12, emoji_mode=False, max_width_mm=180):
    """
    Write text safely into the PDF using manual wrapping.
    - pdf: FPDF instance
    - text: string to write
    - font_name: registered font name to use
    - font_size: integer font size
    - emoji_mode: if True, writes lines using Emoji font and uses cell()
    - max_width_mm: approximate printable width in mm (default A4 inner width)
    """
    # Set font
    pdf.set_font(font_name, "", font_size)

    # Normalize text
    if text is None:
        text = ""

    # If emoji mode: write each line with cell (no wrapping) to avoid width calc problems
    if emoji_mode:
        lines = str(text).splitlines() or [str(text)]
        for ln in lines:
            # use cell to print single line (safer for emojis)
            pdf.cell(0, font_size * 0.6 + 2, ln, ln=True)
        return

    # Manual wrap for non-emoji text
    words = str(text).split()
    if not words:
        pdf.cell(0, font_size * 0.6 + 2, "", ln=True)
        return

    current_line = ""
    for w in words:
        test_line = (current_line + " " + w).strip() if current_line else w
        # get_string_width returns mm for current font/size
        if pdf.get_string_width(test_line) > max_width_mm:
            # flush current_line
            pdf.cell(0, font_size * 0.6 + 2, current_line, ln=True)
            current_line = w
        else:
            current_line = test_line

    if current_line:
        pdf.cell(0, font_size * 0.6 + 2, current_line, ln=True)


# --------------------------------------------------------
#                PDF EXPORT (UNICODE + EMOJI SAFE)
# --------------------------------------------------------
def export_report_pdf(report, selected_user="Overall", output_path=None):
    """
    Export a report to a PDF file with Unicode + emoji support.
    Requires these files in ./fonts/:
      - NotoSans-Regular.ttf
      - NotoEmoji-Regular.ttf
    """
    from fpdf import FPDF

    # create temporary output path if not provided
    if output_path is None:
        fd, out_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        output_path = out_path

    pdf = FPDF(format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=15)

    # font files expected
    sans_path = os.path.join("fonts", "NotoSans-Regular.ttf")
    emoji_path = os.path.join("fonts", "NotoEmoji-Regular.ttf")

    if not os.path.exists(sans_path):
        raise FileNotFoundError("Missing font file: fonts/NotoSans-Regular.ttf")
    if not os.path.exists(emoji_path):
        raise FileNotFoundError("Missing font file: fonts/NotoEmoji-Regular.ttf")

    # register fonts
    pdf.add_font("Noto", "", sans_path, uni=True)
    pdf.add_font("Emoji", "", emoji_path, uni=True)

    # Title
    pdf.set_font("Noto", "", 16)
    pdf.cell(0, 10, f"WhatsApp Analysis — {selected_user}", ln=True, align="C")
    pdf.ln(4)

    # Overview
    ov = report.get("overview", {})
    _safe_write(pdf, f"Total Messages: {ov.get('total_messages','-')}", font_name="Noto", font_size=12)
    _safe_write(pdf, f"Total Words: {ov.get('total_words','-')}", font_name="Noto", font_size=12)
    _safe_write(pdf, f"Media Shared: {ov.get('media_shared','-')}", font_name="Noto", font_size=12)
    _safe_write(pdf, f"Links Shared: {ov.get('links_shared','-')}", font_name="Noto", font_size=12)
    pdf.ln(2)

    # Top senders
    _safe_write(pdf, "Top Senders:", font_name="Noto", font_size=14)
    for user, cnt in report.get("top_senders", [])[:10]:
        _safe_write(pdf, f"- {user}: {cnt}", font_name="Noto", font_size=11)
    pdf.ln(2)

    # Top words
    _safe_write(pdf, "Top Words:", font_name="Noto", font_size=14)
    for w, c in report.get("most_common_words", [])[:15]:
        _safe_write(pdf, f"- {w}: {c}", font_name="Noto", font_size=11)
    pdf.ln(2)

    # Emoji usage (use emoji font and safe cell printing)
    _safe_write(pdf, "Emoji Usage:", font_name="Noto", font_size=14)
    for e, c in report.get("emoji_analysis", [])[:30]:
        # combine short label with count; write with emoji font to render glyphs
        _safe_write(pdf, f"{e}  ×{c}", font_name="Emoji", font_size=12, emoji_mode=True)

    pdf.ln(4)

    # Summary (if present)
    if "summary" in report and report["summary"]:
        _safe_write(pdf, "Auto Summary:", font_name="Noto", font_size=14)
        _safe_write(pdf, report["summary"], font_name="Noto", font_size=11)

    pdf.ln(4)

    # Wordcloud image (if present)
    wc_bytes = report.get("wordcloud_image_bytes") or report.get("wordcloud")
    if wc_bytes:
        fd_img, img_path = tempfile.mkstemp(suffix=".png")
        os.close(fd_img)
        with open(img_path, "wb") as f:
            f.write(wc_bytes)
        # Put image full width minus margins
        pdf.image(img_path, x=15, w=180)
        try:
            os.remove(img_path)
        except Exception:
            pass

    # finalize
    pdf.output(output_path)
    return output_path
