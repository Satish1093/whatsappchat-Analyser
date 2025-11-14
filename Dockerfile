# ==========================
#   Base Image
# ==========================
FROM python:3.10-slim

# ==========================
#   Install System Packages
# ==========================
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# ==========================
#   Working Directory
# ==========================
WORKDIR /app

# ==========================
#   Copy Files
# ==========================
COPY . /app

# ==========================
#   Python Dependencies
# ==========================
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ==========================
#   Expose Streamlit Port
# ==========================
EXPOSE 7860

# ==========================
#   Streamlit RUN Command
# ==========================
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
