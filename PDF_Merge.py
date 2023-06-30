import streamlit as st
from PyPDF4 import PdfFileMerger
from PIL import Image
import io

def merge_pdf_files(file_paths):
    merger = PdfFileMerger()
    for path in file_paths:
        pdf_data = path.read()
        merger.append(io.BytesIO(pdf_data))

    output = io.BytesIO()
    merger.write(output)
    merger.close()

    return output


def image_to_pdf(image):
    pdf_output = io.BytesIO()
    image.save(pdf_output, format='PDF')
    pdf_output.seek(0)

    return pdf_output


def main():
    st.title("PDF Merger")
    st.write("PDF_Merger created by Li")
    uploaded_files = st.file_uploader("Upload PDF files or images", accept_multiple_files=True)

    if st.button("Merge PDFs") and uploaded_files:
        file_paths = [file for file in uploaded_files if file.name.lower().endswith(".pdf")]

        if len(file_paths) > 1:
            merged_pdf = merge_pdf_files(file_paths)
            st.success("PDF files merged successfully!")
            st.download_button("Download merged PDF", merged_pdf.getvalue(), file_name="merged.pdf")
        else:
            st.warning("Please upload more than one PDF file for merging.")

    if st.button("Convert Images to PDF") and uploaded_files:
        file_paths = [file for file in uploaded_files if file.name.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))]

        if len(file_paths) > 0:
            pdf_files = []
            for file in file_paths:
                image_data = file.read()
                img = Image.open(io.BytesIO(image_data))
                pdf_file = image_to_pdf(img)
                pdf_files.append(pdf_file)

            merged_pdf = merge_pdf_files(pdf_files)
            st.success("Images converted to PDF successfully!")
            st.download_button("Download converted PDF", merged_pdf.getvalue(), file_name="converted.pdf")
        else:
            st.warning("Please upload at least one image file for conversion.")


if __name__ == "__main__":
    main()
