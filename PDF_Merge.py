import streamlit as st
from PyPDF4 import PdfFileMerger
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import io
import os
import zipfile
import base64

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
    st.title("PDF Tools")
    st.write("PDF_Tools created by Li")
    uploaded_files = st.file_uploader("上传pdf文件或者图片", accept_multiple_files=True)
    choose = st.sidebar.selectbox('选择你需要的功能', ['PDF合并', '图片转化成PDF', 'PDF拆分(一张一张)', 'PDF拆分(zip打包)'])

    if choose == 'PDF合并' and uploaded_files:
        if st.button('PDF合并'):
            file_paths = [file for file in uploaded_files if file.name.lower().endswith(".pdf")]

            if len(file_paths) > 1:
                merged_pdf = merge_pdf_files(file_paths)
                st.success("PDF文件合并成功!")
                pdf_bytes = merged_pdf.getvalue()
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="merged.pdf">Download merged.pdf</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning("请上传多个PDF文件合并.")

    if choose == '图片转化成PDF' and uploaded_files:
        if st.button('图片转化PDF'):
            file_paths = [file for file in uploaded_files if file.name.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))]

            if len(file_paths) > 0:
                pdf_files = []
                for file in file_paths:
                    image_data = file.read()
                    img = Image.open(io.BytesIO(image_data))
                    pdf_file = image_to_pdf(img)
                    pdf_files.append(pdf_file)

                merged_pdf = merge_pdf_files(pdf_files)
                st.success("图片转化成PDF成功!")
                pdf_bytes = merged_pdf.getvalue()
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="converted.pdf">Download converted.pdf</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning("请上传至少一张图.")

    if choose == 'PDF拆分(一张一张)' and uploaded_files:
        if st.button('PDF拆分'):
            file_paths = [file for file in uploaded_files if file.name.lower().endswith(".pdf")]
            if file_paths:
                splitpdf = split_pdf(file_paths[0])  # 仅使用第一个文件进行拆分
                if splitpdf:
                    st.success("PDF文件拆分成功!")
                    # 下载拆分后的PDF文件
                    for i, pdf in enumerate(splitpdf, start=1):
                        download_filename = f"page_{i}.pdf"
                        pdf_bytes = pdf.getvalue()
                        b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{download_filename}">Download{download_filename}</a>'
                        st.markdown(href, unsafe_allow_html=True)

    if choose == 'PDF拆分(zip打包)' and uploaded_files:
        if st.button('PDF拆分'):
            file_paths = [file for file in uploaded_files if file.name.lower().endswith(".pdf")]
            if file_paths:
                output_folder = "pdf_all"  # 在当前工作目录创建名为 "pdf_all" 的文件夹
                os.makedirs(output_folder, exist_ok=True)

                for file_path in file_paths:
                    splitpdf = split_pdf(file_path)  # 拆分 PDF 文件
                    if splitpdf:
                        for i, pdf in enumerate(splitpdf, start=1):
                            output_pdf = os.path.join(output_folder, f'page_{i}.pdf')
                            with open(output_pdf, 'wb') as output_file:
                                output_file.write(pdf.getvalue())

                # 将所有文件打包为 ZIP 文件
                zip_file_name = "pdf_all.zip"
                with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
                    for folder_name, subfolders, filenames in os.walk(output_folder):
                        for filename in filenames:
                            file_path = os.path.join(folder_name, filename)
                            zip_file.write(file_path, arcname=os.path.relpath(file_path, output_folder))

                # 读取 ZIP 文件内容并进行 base64 编码
                with open(zip_file_name, 'rb') as file:
                    zip_data = file.read()
                    zip_data_b64 = base64.b64encode(zip_data).decode()

                # 生成下载链接
                download_link = f'<a href="data:application/zip;base64,{zip_data_b64}" download="{zip_file_name}">下载全部拆分文件</a>'
                st.markdown(download_link, unsafe_allow_html=True)

                # 删除拆分后的文件和 ZIP 文件
                for folder_name, subfolders, filenames in os.walk(output_folder):
                    for filename in filenames:
                        file_path = os.path.join(folder_name, filename)
                        os.remove(file_path)
                os.remove(zip_file_name)

if __name__ == "__main__":
    main()
