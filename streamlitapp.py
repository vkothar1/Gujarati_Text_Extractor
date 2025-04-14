import streamlit as st
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from docx import Document
import tempfile
import os
from io import BytesIO

# Page config
st.set_page_config(page_title="Indian Language Text Extractor", layout="centered")

# App title and description
st.title("📄 Indian Language Text Extractor")
st.markdown("Upload your document (PDF, Image, DOCX), and this app will extract **Gujarati or Hindi** text using OCR.")

# Language selector
lang_choice = st.selectbox(
    "Select language for OCR:",
    options=["Gujarati", "Hindi"],
    index=0
)

# Map Streamlit label to Tesseract language codes
lang_map = {
    "Gujarati": "guj",
    "Hindi": "hin"
}
selected_lang = lang_map[lang_choice]

# File uploader
uploaded_file = st.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg", "docx"])

# OCR for image
def extract_text_from_image(img, lang='guj'):
    return pytesseract.image_to_string(img, lang=f'eng+{lang}')

# PDF handler (extract text directly or fallback to OCR)
def extract_text_from_pdf(pdf_file):
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(pdf_file.read())
        tmp_pdf_path = tmp_pdf.name

    doc = fitz.open(tmp_pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text("text")

        if not page_text.strip():
            pix = page.get_pixmap()
            img = Image.open(BytesIO(pix.tobytes()))
            page_text = extract_text_from_image(img, lang=selected_lang)

        text += page_text
        text += f"\n_________________________PAGE {page_num + 1}____________________________\n"

    os.remove(tmp_pdf_path)
    return text

# DOCX handler
def extract_text_from_docx(file):
    doc = Document(file)
    return '\n'.join([p.text for p in doc.paragraphs])

# Main logic
if uploaded_file:
    file_type = uploaded_file.type

    with st.spinner("🔍 Extracting text..."):
        if "pdf" in file_type:
            result = extract_text_from_pdf(uploaded_file)
        elif "image" in file_type:
            image = Image.open(uploaded_file)
            result = extract_text_from_image(image, lang=selected_lang)
        elif "wordprocessingml" in file_type:
            result = extract_text_from_docx(uploaded_file)
        else:
            result = "❌ Unsupported file type."

    st.success("✅ Text extraction complete!")
    st.text_area(f"📝 Extracted {lang_choice} Text:", value=result, height=300)
    st.download_button("⬇️ Download as TXT", result, file_name=f"{lang_choice.lower()}_text.txt")
