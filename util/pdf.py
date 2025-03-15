import os
from PyPDF2 import PdfReader, PdfWriter

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
NUMBER_FONT_PATH = os.path.join(BASE_DIR, "../static/font/helvethaica.ttf")
FONT_PATH = os.path.join(BASE_DIR, "../static/font/kodchiang.ttf")

def fill_content_pdf(c, x_position, y_position, content, color, font, font_size):
    c.setFillColorRGB(*color)
    c.setFont(font, font_size)
    c.drawString(x_position, y_position, content)

def merge_pdfs(original_pdf_path, overlay_pdf_path, output_pdf_path):
    original_pdf = PdfReader(original_pdf_path)
    overlay_pdf = PdfReader(overlay_pdf_path)
    pdf_writer = PdfWriter()

    for page_num in range(len(original_pdf.pages)):
        original_page = original_pdf.pages[page_num]
        overlay_page = overlay_pdf.pages[0]
        original_page.merge_page(overlay_page)
        pdf_writer.add_page(original_page)

    with open(output_pdf_path, "wb") as output_pdf:
        pdf_writer.write(output_pdf)


def cleanup_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
