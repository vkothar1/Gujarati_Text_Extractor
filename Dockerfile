FROM python:3.12-slim

# Install Tesseract and Gujarati language data
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-guj \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Streamlit app
CMD ["streamlit", "run", "streamlitapp.py", "--server.port=8501", "--server.address=0.0.0.0"]
