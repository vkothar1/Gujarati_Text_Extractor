import streamlit as st
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from docx import Document
import tempfile
import os
from io import BytesIO
import zipfile

st.set_page_config(page_title="Multilingual Text Extractor", layout="centered")

st.title("📄 Gujarati, Hindi, and English Text Extractor")
st.markdown("Upload a single file (PDF, Image, DOCX) or a ZIP of multiple PDFs. Choose the language for OCR.")

# Language selector
language_option = st.selectbox("Select Document Language:", ["Gujarati", "Hindi", "English", "Mixed (Eng + Hin + Guj)"])
lang_map = {
    "Gujarati": "guj",
    "Hindi": "hin",
    "English": "eng",
    "Mixed (Eng + Hin + Guj)": "eng+hin+guj"
}
tesseract_lang = lang_map[language_option]

# Batch size selector for PDFs
batch_size = st.number_input("Pages per Batch (PDF only)", min_value=10, max_value=100, value=50, step=10)

uploaded_file = st.file_uploader("Upload a file (PDF, Image, DOCX, or ZIP of PDFs)", type=["pdf", "png", "jpg", "jpeg", "docx", "zip"])

def extract_text_from_image(img, lang):
    config = r'--oem 1 --psm 6'
    return pytesseract.image_to_string(img, lang=lang, config=config)

def extract_text_from_pdf(pdf_path, lang, batch_size):
    text = ""
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    for batch_start in range(0, total_pages, batch_size):
        batch_end = min(batch_start + batch_size, total_pages)
        st.write(f"🔄 Processing pages {batch_start + 1} to {batch_end}...")

        for page_num in range(batch_start, batch_end):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)  # Optimized DPI
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = extract_text_from_image(img, lang)
            text += f"\n_________________________PAGE {page_num + 1}____________________________\n"
            text += page_text
            st.write(f"✅ Extracted text from page {page_num + 1}")

    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return '\n'.join([p.text for p in doc.paragraphs])

def process_zip(zip_file, lang, batch_size):
    full_text = ""
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
            pdf_files = [f for f in os.listdir(temp_dir) if f.lower().endswith(".pdf")]
            if not pdf_files:
                return "❌ No PDFs found in ZIP."

            for pdf_name in sorted(pdf_files):
                st.write(f"📂 Processing {pdf_name}...")
                pdf_path = os.path.join(temp_dir, pdf_name)
                full_text += f"\n\n============= FILE: {pdf_name} =============\n\n"
                full_text += extract_text_from_pdf(pdf_path, lang, batch_size)
    return full_text

if uploaded_file:
    file_type = uploaded_file.type

    with st.spinner(f"🔍 Extracting {language_option} text..."):
        if uploaded_file.name.lower().endswith(".zip"):
            result = process_zip(uploaded_file, tesseract_lang, batch_size)
        elif "pdf" in file_type:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(uploaded_file.read())
                result = extract_text_from_pdf(tmp_pdf.name, tesseract_lang, batch_size)
                os.remove(tmp_pdf.name)
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
