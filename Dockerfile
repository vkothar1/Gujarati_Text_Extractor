FROM python:3.12

RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-guj \
    poppler-utils  # optional for pdf handling

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "streamlitapp.py"]
