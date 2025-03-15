import requests
import tempfile
import os

from flask import Blueprint, request, send_file, jsonify
from util.pdf import merge_pdfs, cleanup_files, fill_content_pdf
from util.request import handle_error, validate_request
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

file_path = os.path.dirname(os.path.abspath(__file__))

INCH = 72.0
PAGE_HEIGHT = 8.27 * INCH
PAGE_WIDTH = 11.69 * INCH
NUMBER_FONT_PATH = f"{file_path}/../../static/font/helvethaica.ttf"
FONT_PATH = f"{file_path}/../../static/font/kodchiang.ttf"

pdfmetrics.registerFont(TTFont("Helvethaica", NUMBER_FONT_PATH))
pdfmetrics.registerFont(TTFont("Kodchiang", FONT_PATH))

fill_pdf_app = Blueprint("fill_pdf", __name__)


@fill_pdf_app.route("/fill", methods=["POST"])
@validate_request(["url", "params", "lang"])
@handle_error
def fill_pdf():
    global overlay_path
    payload = request.get_json()
    url = payload["url"]
    fill_data = payload.get("params", {})

    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to download PDF"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(response.content)
        temp_pdf_path = temp_pdf.name

    output_pdf_path = f"{temp_pdf_path}_filled.pdf"

    try:
        overlay_path = fill_name(fill_data.get("number"),
                                 fill_data.get("name"),
                                 fill_data.get("course_name"),
                                 fill_data.get("certificate_date"),
                                 fill_data.get("date"),
                                 payload.get("lang"))

        merge_pdfs(temp_pdf_path, overlay_path, output_pdf_path)
        return send_file(output_pdf_path, as_attachment=True, download_name="filled_form.pdf",
                         mimetype="application/pdf")
    finally:
        cleanup_files([temp_pdf_path, output_pdf_path, overlay_path])


def fill_name(number, name, course_name, certificate_date, date, lang):
    overlay_pdf_path = "/tmp/overlay.pdf"
    c = canvas.Canvas(overlay_pdf_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # number position
    text_width = c.stringWidth(number, "Helvethaica", 19)
    fill_content_pdf(c=c,
                     x_position=((PAGE_WIDTH - text_width) / 2) + (250 if lang == "th" else 240),
                     y_position=PAGE_HEIGHT - 75,
                     content=number,
                     color=(75/255, 123/255, 207/255),
                     font="Helvethaica",
                     font_size=19)

    text_width = c.stringWidth(name, "Helvethaica", 34)
    fill_content_pdf(c=c,
                     x_position=(PAGE_WIDTH - text_width) / 2,
                     y_position=((PAGE_HEIGHT - 35) / 2) - (20 if lang == "th" else 12),
                     content=name,
                     color=(201/255, 158/255, 80/255),
                     font="Helvethaica",
                     font_size=34)

    text_width = c.stringWidth(course_name, "Helvethaica", 28)
    fill_content_pdf(c=c,
                     x_position=(PAGE_WIDTH - text_width) / 2,
                     y_position=((PAGE_HEIGHT - 29) / 2) - (85 if lang == "th" else 80),
                     content=course_name,
                     color=(201 / 255, 158 / 255, 80 / 255),
                     font="Helvethaica",
                     font_size=28)

    text_width = c.stringWidth(certificate_date, "Helvethaica", 22)
    fill_content_pdf(c=c,
                     x_position=(PAGE_WIDTH - text_width) / 2,
                     y_position=((PAGE_HEIGHT - 23) / 2) - (120 if lang == "th" else 115),
                     content=certificate_date,
                     color=(201 / 255, 158 / 255, 80 / 255),
                     font="Helvethaica",
                     font_size=22)

    text_width = c.stringWidth(date, "Helvethaica", 22)
    fill_content_pdf(c=c,
                     x_position=(PAGE_WIDTH - text_width) / 2,
                     y_position=((PAGE_HEIGHT - 22) / 2) - (155 if lang == "th" else 150),
                     content=date,
                     color=(201 / 255, 158 / 255, 80 / 255),
                     font="Helvethaica",
                     font_size=22)

    c.save()
    return overlay_pdf_path
