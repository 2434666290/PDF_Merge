import streamlit as st
from PyPDF4 import PdfFileMerger
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import io,os

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


def split_pdf(input_pdf):
    # 打开上传的 PDF 文件
    pdf_files = []
    with input_pdf as file:
        pdf = PdfReader(file)

        # 拆分每一页 PDF
        for page_number, page in enumerate(pdf.pages, start=1):
            writer = PdfWriter()
            writer.add_page(page)

            # 将拆分后的 PDF 保存到内存中
            output_pdf = io.BytesIO()
            writer.write(output_pdf)
            output_pdf.seek(0)
            pdf_files.append(output_pdf)
    return pdf_files


def main():
    st.title("PDF Merger")
    st.write("PDF_Tools created by Li")
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

    if st.button('Split PDFs for details') and uploaded_files:
        file_paths = [file for file in uploaded_files if file.name.lower().endswith(".pdf")]
        if file_paths:
            splitpdf = split_pdf(file_paths[0])  # 仅使用第一个文件进行拆分
            if splitpdf:
                st.success("PDF file split successfully!")
                # 下载拆分后的PDF文件
                for i, pdf in enumerate(splitpdf, start=1):
                    download_filename = f"page_{i}.pdf"
                    st.download_button(f"Download {download_filename}", pdf.getvalue(), file_name=download_filename)

    if st.button('Split PDFs for all') and uploaded_files:
        file_paths = [file for file in uploaded_files if file.name.lower().endswith(".pdf")]
        output_folder = "pdf_all"
        os.makedirs(output_folder, exist_ok=True)
        #output_folder = st.text_input("请在桌面创建一个文件夹：pdf_all", value=r"C:\Users\Administrator\Desktop\pdf_all")
        #st.warning("请确保桌面是否有pdf_all文件夹(或者自行修改保存路径）.")
        if file_paths:
            splitpdf = split_pdf(file_paths[0])  # 仅使用第一个文件进行拆分
            if splitpdf:
                for i, pdf in enumerate(splitpdf, start=1):
                    output_pdf = os.path.join(output_folder, f'page_{i}.pdf')
                    with open(output_pdf, 'wb') as output_file:
                        output_file.write(pdf.getvalue())
                st.success("PDF 文件拆分完成！")




if __name__ == "__main__":
    main()
