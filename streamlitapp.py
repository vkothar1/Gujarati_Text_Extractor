import streamlit as st
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from docx import Document
import tempfile
import os
import shutil
from io import BytesIO
from zipfile import ZipFile

st.set_page_config(page_title="Multilingual Text Extractor", layout="centered")

st.title("📄 Gujarati, Hindi, and English Text Extractor")
st.markdown("Upload your document (PDF, Image, DOCX), select language, and optionally split large PDFs.")

# Language selector
language_option = st.selectbox("Select Document Language:", ["Gujarati", "Hindi", "English", "Mixed (Eng + Hin + Guj)"])
lang_map = {
    "Gujarati": "guj",
    "Hindi": "hin",
    "English": "eng",
    "Mixed (Eng + Hin + Guj)": "eng+hin+guj"
}
tesseract_lang = lang_map[language_option]

# Batch size selector
batch_size = st.number_input("Pages per Batch (PDF only)", min_value=10, max_value=100, value=50, step=10)

# Optional PDF splitting
split_pdf = st.checkbox("Split large PDF into smaller files and download ZIP")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg", "docx"])

def extract_text_from_image(img, lang):
    gray = img.convert("L")
    bw = gray.point(lambda x: 0 if x < 128 else 255, '1')
    return pytesseract.image_to_string(bw, lang=lang)

def extract_text_from_pdf(pdf_file, lang, batch_size):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(pdf_file.read())
        tmp_pdf_path = tmp_pdf.name

    doc = fitz.open(tmp_pdf_path)
    total_pages = len(doc)

    output_dir = tempfile.mkdtemp()
    zip_buffer = BytesIO()
    batch_files = []

    for batch_start in range(0, total_pages, batch_size):
        batch_end = min(batch_start + batch_size, total_pages)
        batch_text = ""
        st.write(f"🔄 Processing pages {batch_start + 1} to {batch_end}...")

        for page_num in range(batch_start, batch_end):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = extract_text_from_image(img, lang)
            batch_text += f"\n_________________________PAGE {page_num + 1}____________________________\n"
            batch_text += page_text
            st.write(f"✅ Extracted text from page {page_num + 1}")

        batch_filename = f"text_batch_{batch_start + 1}_to_{batch_end}.txt"
        batch_path = os.path.join(output_dir, batch_filename)
        with open(batch_path, "w", encoding="utf-8") as f:
            f.write(batch_text)
        batch_files.append(batch_path)

    with ZipFile(zip_buffer, "w") as zipf:
        for path in batch_files:
            zipf.write(path, arcname=os.path.basename(path))

    zip_buffer.seek(0)
    shutil.rmtree(output_dir)
    os.remove(tmp_pdf_path)
    return zip_buffer

def split_pdf_into_chunks(pdf_file, batch_size):
    zip_buffer = BytesIO()
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_bytes = pdf_file.read()
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(pdf)

        split_paths = []
        for i in range(0, total_pages, batch_size):
            split_doc = fitz.open()
            for j in range(i, min(i + batch_size, total_pages)):
                split_doc.insert_pdf(pdf, from_page=j, to_page=j)
            output_path = os.path.join(tmp_dir, f"split_{i+1}_to_{min(i+batch_size, total_pages)}.pdf")
            split_doc.save(output_path)
            split_doc.close()
            split_paths.append(output_path)

        with ZipFile(zip_buffer, "w") as zipf:
            for path in split_paths:
                zipf.write(path, arcname=os.path.basename(path))

    zip_buffer.seek(0)
    return zip_buffer

def extract_text_from_docx(file):
    doc = Document(file)
    return '\n'.join([p.text for p in doc.paragraphs])

if uploaded_file:
    file_type = uploaded_file.type

    if split_pdf and "pdf" in file_type:
        with st.spinner("✂️ Splitting PDF into chunks..."):
            zip_data = split_pdf_into_chunks(uploaded_file, batch_size)
            st.download_button("⬇️ Download Split PDFs as ZIP", zip_data, file_name="split_pdfs.zip", mime="application/zip")
    else:
        with st.spinner(f"🔍 Extracting {language_option} text..."):
            if "pdf" in file_type:
                zip_data = extract_text_from_pdf(uploaded_file, tesseract_lang, batch_size)
                st.download_button("⬇️ Download Extracted Text Batches as ZIP", zip_data, file_name="text_batches.zip", mime="application/zip")
            elif "image" in file_type:
                image = Image.open(uploaded_file)
                result = extract_text_from_image(image, tesseract_lang)
                st.success("✅ Text extraction complete!")
                st.text_area(f"📝 Extracted Text ({language_option}):", value=result, height=300)
                st.download_button("⬇️ Download as TXT", result, file_name=f"{language_option.lower()}_text.txt")
            elif "wordprocessingml" in file_type:
                result = extract_text_from_docx(uploaded_file)
                st.success("✅ Text extraction complete!")
                st.text_area(f"📝 Extracted Text ({language_option}):", value=result, height=300)
                st.download_button("⬇️ Download as TXT", result, file_name=f"{language_option.lower()}_text.txt")
            else:
                st.error("❌ Unsupported file type.")
