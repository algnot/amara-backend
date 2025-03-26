import csv
from flask import Blueprint, Response
from io import StringIO
from model.saleperson import SalePerson
from util.request import handle_error, handle_access_token

export_sale_person_app = Blueprint("export_sale_person", __name__)

@export_sale_person_app.route("/sale-person", methods=["GET"])
@handle_access_token
@handle_error
def export_sale_person():
    all_sale_person = SalePerson().filter()

    if not isinstance(all_sale_person, list):
        all_sale_person = [all_sale_person]

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["sale_person_id", "ชื่อ", "นามสกุล", "รหัสผู้ขาย"])

    for sale_person in all_sale_person:
        writer.writerow([sale_person.id, sale_person.firstname, sale_person.lastname, sale_person.reference_code])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students.csv"},
    )
