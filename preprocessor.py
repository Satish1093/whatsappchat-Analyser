# preprocessor.py
def preprocess(text):
    """
    Minimal cleaning: remove BOM / narrow spaces and trim.
    Return a plain string (not DataFrame).
    """
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("\u202f", " ")
    text = text.replace("\ufeff", "")
    return text.strip()
