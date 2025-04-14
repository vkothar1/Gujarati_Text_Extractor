import streamlit as st
from PIL import Image
import pytesseract
import fitz  # PyMuPDF for PDF text extraction
from docx import Document
import tempfile
import os

st.set_page_config(page_title="Gujarati Text Extractor", layout="centered")

st.title("📄 Gujarati Text Extractor")
st.markdown("Upload your document (PDF, Image, DOCX), and this app will extract Gujarati text for you.")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg", "docx"])

def extract_text_from_image(img):
    return pytesseract.image_to_string(img, lang='eng+guj')

def extract_text_from_pdf(pdf_file):
    text = ""
    
    # Create a temporary file to save the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(pdf_file.read())
        tmp_pdf_path = tmp_pdf.name

    # Open the PDF using PyMuPDF
    doc = fitz.open(tmp_pdf_path)
    
    # Loop through all pages in the PDF and extract text
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Load each page
        text += page.get_text("text")  # Extract text from the page
        text += f"\n_________________________PAGE {page_num + 1}____________________________\n"
    
    os.remove(tmp_pdf_path)  # Clean up temporary file
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return '\n'.join([p.text for p in doc.paragraphs])

if uploaded_file:
    file_type = uploaded_file.type

    with st.spinner("🔍 Extracting text..."):
        if "pdf" in file_type:
            result = extract_text_from_pdf(uploaded_file)
        elif "image" in file_type:
            image = Image.open(uploaded_file)
            result = extract_text_from_image(image)
        elif "wordprocessingml" in file_type:
            result = extract_text_from_docx(uploaded_file)
        else:
            result = "❌ Unsupported file type."

    st.success("✅ Text extraction complete!")
    st.text_area("📝 Extracted Gujarati Text:", value=result, height=300)
    st.download_button("⬇️ Download as TXT", result, file_name="gujarati_text.txt")
