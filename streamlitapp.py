import streamlit as st
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from docx import Document
import tempfile
import os
from io import BytesIO

st.set_page_config(page_title="Multilingual Text Extractor", layout="centered")

st.title("📄 Gujarati, Hindi, and English Text Extractor")
st.markdown("Upload your document (PDF, Image, DOCX) and select the language for text extraction.")

# Language selector
language_option = st.selectbox("Select Document Language:", ["Gujarati", "Hindi", "English", "Mixed (Eng + Hin + Guj)"])
lang_map = {
    "Gujarati": "guj",
    "Hindi": "hin",
    "English": "eng",
    "Mixed (Eng + Hin + Guj)": "eng+hin+guj"
}
tesseract_lang = lang_map[language_option]

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg", "docx"])

def extract_text_from_image(img, lang):
    # Convert image to grayscale
    gray = img.convert("L")

    # Binarize to improve OCR accuracy
    bw = gray.point(lambda x: 0 if x < 128 else 255, '1')

    return pytesseract.image_to_string(bw, lang=lang)

def extract_text_from_pdf(pdf_file, lang):
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(pdf_file.read())
        tmp_pdf_path = tmp_pdf.name

    doc = fitz.open(tmp_pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        page_text = extract_text_from_image(img, lang)
        text += f"\n_________________________PAGE {page_num + 1}____________________________\n"
        text += page_text

    os.remove(tmp_pdf_path)
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return '\n'.join([p.text for p in doc.paragraphs])

if uploaded_file:
    file_type = uploaded_file.type

    with st.spinner(f"🔍 Extracting {language_option} text..."):
        if "pdf" in file_type:
            result = extract_text_from_pdf(uploaded_file, tesseract_lang)
        elif "image" in file_type:
            image = Image.open(uploaded_file)
            result = extract_text_from_image(image, tesseract_lang)
        elif "wordprocessingml" in file_type:
            result = extract_text_from_docx(uploaded_file)
        else:
            result = "❌ Unsupported file type."

    st.success("✅ Text extraction complete!")
    st.text_area(f"📝 Extracted Text ({language_option}):", value=result, height=300)
    st.download_button("⬇️ Download as TXT", result, file_name=f"{language_option.lower()}_text.txt")
