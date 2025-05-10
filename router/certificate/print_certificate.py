import os
import tempfile
from flask import Blueprint, send_file, request
from model.certificate import Certificate
from model.course import Course
from model.student import Student
from util.date import format_eng_date, format_thai_date_with_thai_numerals, to_thai_numerals
from util.pdf import merge_pdfs, cleanup_files, fill_content_pdf
from util.request import handle_error
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

print_certification_app = Blueprint("print_certification", __name__)

def get_pdf_mapping(version, language, certification, course, student):
    fill_data = {
        "1.0": {
            "th": [
                {
                    "x_position": "((PAGE_WIDTH - text_width) / 2) + 250",
                    "y_position": "PAGE_HEIGHT - 75",
                    "color": (75 / 255, 123 / 255, 207 / 255),
                    "font": "Helvethaica",
                    "font_size": 19,
                    "content": f"เลขที่ {to_thai_numerals(certification.certificate_number)}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 35) / 2) - 19",
                    "color": (201/255, 158/255, 80/255),
                    "font": "Helvethaica",
                    "font_size": 34,
                    "content": f"{student.firstname_th} {student.lastname_th}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width - text_width_next) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 55",
                    "color": (75 / 255, 123 / 255, 207 / 255),
                    "font": "Helvethaica",
                    "font_size": 26,
                    "content": "ได้ศึกษาสำเร็จหลักสูตรวิชา"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width + text_width_prev) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 55",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 26,
                    "content": f"{course.name_th}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 23) / 2) - 87",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 22,
                    "content": f"รุ่นที่ {to_thai_numerals(certification.batch)} ระหว่างวันที่ {format_thai_date_with_thai_numerals(certification.start_date)} ถึงวันที่ {format_thai_date_with_thai_numerals(certification.end_date)}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 22) / 2) - 117",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 22,
                    "content": f"ให้ไว้ ณ วันที่ {format_thai_date_with_thai_numerals(certification.given_date)}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 185",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 22,
                    "content": "ธนวัฒน์ ตลับทอง.................................................."
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 215",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 22,
                    "content": "ผู้บริหารโรงเรียน"
                }
            ],
            "en": [
                {
                    "x_position": "((PAGE_WIDTH - text_width) / 2) + 240",
                    "y_position": "PAGE_HEIGHT - 75",
                    "color": (75 / 255, 123 / 255, 207 / 255),
                    "font": "Helvethaica",
                    "font_size": 19,
                    "content": f"Certificate No. {certification.certificate_number}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 35) / 2) - 22",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 34,
                    "content": f"{student.firstname_en} {student.lastname_en}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width - text_width_next) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 62",
                    "color": (75 / 255, 123 / 255, 207 / 255),
                    "font": "Helvethaica",
                    "font_size": 27,
                    "content": "Completed the course of study "
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width + text_width_prev) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 62",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 27,
                    "content": f"{course.name_en}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 102",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 27,
                    "content": f"Given on {format_eng_date(certification.given_date)}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 180",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 22,
                    "content": "Tanawat Talabtong.................................................."
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 210",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 22,
                    "content": "Director of the School"
                }
            ]
        },
        "2.0": {
            "th": [
                {
                    "x_position": "((PAGE_WIDTH - text_width) / 2) + 250",
                    "y_position": "PAGE_HEIGHT - 75",
                    "color": (75 / 255, 123 / 255, 207 / 255),
                    "font": "Helvethaica",
                    "font_size": 19,
                    "content": f"เลขที่ {to_thai_numerals(certification.certificate_number)}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 35) / 2) - 27",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 34,
                    "content": f"{student.firstname_th} {student.lastname_th}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width - text_width_next) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 67",
                    "color": (75 / 255, 123 / 255, 207 / 255),
                    "font": "Helvethaica",
                    "font_size": 27,
                    "content": "ได้ศึกษาสำเร็จหลักสูตรวิชา"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width + text_width_prev) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 67",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 27,
                    "content": f"{course.name_th}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 107",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 27,
                    "content": f"ให้ไว้ ณ วันที่ {format_thai_date_with_thai_numerals(certification.given_date)}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 185",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 22,
                    "content": "ธนวัฒน์ ตลับทอง.................................................."
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 215",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 22,
                    "content": "ผู้บริหารโรงเรียน"
                }
            ],
            "en": [
                {
                    "x_position": "((PAGE_WIDTH - text_width) / 2) + 240",
                    "y_position": "PAGE_HEIGHT - 75",
                    "color": (75 / 255, 123 / 255, 207 / 255),
                    "font": "Helvethaica",
                    "font_size": 19,
                    "content": f"Certificate No. {certification.certificate_number}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 35) / 2) - 22",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 34,
                    "content": f"{student.firstname_en} {student.lastname_en}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width - text_width_next) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 62",
                    "color": (75 / 255, 123 / 255, 207 / 255),
                    "font": "Helvethaica",
                    "font_size": 27,
                    "content": "Completed the course of study "
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width + text_width_prev) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 62",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 27,
                    "content": f"{course.name_en}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 102",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 27,
                    "content": f"Given on {format_eng_date(certification.given_date)}"
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 180",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 22,
                    "content": "Tanawat Talabtong.................................................."
                },
                {
                    "x_position": "(PAGE_WIDTH - text_width) / 2",
                    "y_position": "((PAGE_HEIGHT - 29) / 2) - 210",
                    "color": (201 / 255, 158 / 255, 80 / 255),
                    "font": "Helvethaica",
                    "font_size": 22,
                    "content": "Director of the School"
                }
            ],
        }
    }

    return fill_data[version][language]

@print_certification_app.route("/print/<string:language>/<string:version>/<string:certification_number>", methods=["GET"])
@handle_error
def print_certification(language, version, certification_number):
    query = request.args
    without_layout = query.get("without_layout", "false")

    certification = Certificate().filter(filters=[("certificate_number", "=", certification_number)], limit=1)

    if not certification:
        raise Exception("ไม่พบเลขที่ใบประกาศนี้ในระบบ")

    course = Course().filter(filters=[("id", "=", certification.course_id)], limit=1)
    if not course:
        raise Exception("ไม่พบคอร์สเรียนนี้ในระบบ")

    student = Student().filter(filters=[("id", "=", certification.student_id)], limit=1)
    if not student:
        raise Exception("ไม่พบข้อมูลนักเรียนดังกล่าวในระบบ")

    mapping = get_pdf_mapping(version, language, certification, course, student)
    pdf_path = f"{file_path}/../../static/certificate/certificate-{version}-{language}-fill.pdf"

    output_pdf_path = f"{pdf_path}_filled.pdf"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_overlay:
        overlay_path = temp_overlay.name
    c = canvas.Canvas(overlay_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    try:
        for index, field in enumerate(mapping):
            text_width_prev = 0 if index == 0 else c.stringWidth(mapping[index - 1]["content"], mapping[index - 1]["font"], mapping[index - 1]["font_size"])
            text_width = c.stringWidth(mapping[index]["content"], mapping[index]["font"], mapping[index]["font_size"])
            text_width_next = 0 if index + 1 > len(mapping) - 1 else c.stringWidth(mapping[index + 1]["content"], mapping[index + 1]["font"], mapping[index + 1]["font_size"])
            print(text_width_prev, text_width, text_width_next)
            fill_content_pdf(c=c,
                             x_position=eval(mapping[index]["x_position"]),
                             y_position=eval(mapping[index]["y_position"]),
                             content=mapping[index]["content"],
                             color=mapping[index]["color"],
                             font=mapping[index]["font"],
                             font_size=mapping[index]["font_size"])

        c.save()
        if without_layout.lower() == "true":
            return send_file(overlay_path, as_attachment=False, mimetype="application/pdf",
                             download_name=f"{certification.certificate_number}-{language}-without-layout.pdf")
        else:
            merge_pdfs(pdf_path, overlay_path, output_pdf_path)
            return send_file(output_pdf_path, as_attachment=False, mimetype="application/pdf",
                             download_name=f"{certification.certificate_number}-{language}.pdf")
    finally:
        cleanup_files([output_pdf_path, overlay_path])
