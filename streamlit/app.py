import streamlit as st
import requests
import os
from pdf2image import convert_from_path


st.title("PDF to JSON Converter")

base_filename = "w8_ben.pdf"

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
# interact with FastAPI endpoint
backend = "http://fastapi:8000/process-pdf"

def preview_pdf(pdf_file):
    images = convert_from_path(pdf_file)
    for i, image in enumerate(images):
        st.image(image, caption=f"Page {i + 1}", use_column_width=True)

if uploaded_file is not None:
    st.write("PDF file uploaded!")

    # Create a new filename by appending the base filename
    uploaded_filename = base_filename

    if st.button("Process PDF"):
        # Save the uploaded PDF with the new filename
        with open(uploaded_filename, "wb") as f:
            f.write(uploaded_file.read())

        st.write("Processing PDF...")

        # Set the content type to "application/pdf" when sending the PDF file
        files = {"pdf_file": (uploaded_filename, open(uploaded_filename, "rb"), "application/pdf")}

        # Assuming FastAPI is running on localhost:8000, adjust the URL accordingly
        response = requests.post(backend, files=files)

        if response.status_code == 200:
            json_data = response.json()
            st.write("JSON Result:")
            st.json(json_data)
        else:
            st.error("Error processing PDF")

        if uploaded_file is not None:
            st.write(f"Uploaded PDF Preview ({uploaded_filename}):")
            preview_pdf(uploaded_filename)
