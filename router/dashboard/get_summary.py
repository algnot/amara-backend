from flask import Blueprint, jsonify
from model.base import Base
from util.request import handle_error, handle_access_token

get_summary_app = Blueprint("get_summary", __name__)

@get_summary_app.route("/summary", methods=["GET"])
@handle_access_token(permission=["read-dashboard-data"])
@handle_error
def get_summary():
    total_students = Base().execute_raw(
        "SELECT COUNT(id) as total FROM student",
        fetch=True
    )[0]["total"]

    total_certificate = Base().execute_raw(
        "SELECT COUNT(id) as total FROM certificate WHERE batch != :batch",
        {"batch": 'draft'},
        fetch=True,
    )[0]["total"]

    total_draft_certificate = Base().execute_raw(
        "SELECT COUNT(id) as total FROM certificate WHERE batch = :batch",
        {"batch": 'draft'},
        fetch=True,
    )[0]["total"]

    total_certificate_in_month = Base().execute_raw(
        """
        SELECT COUNT(id) as total
        FROM certificate
        WHERE batch != :batch
        AND YEAR(given_date) = YEAR(CURRENT_DATE())
        AND MONTH(given_date) = MONTH(CURRENT_DATE())
        """,
        {"batch": "draft"},
        fetch=True
    )[0]["total"]

    return jsonify({
        "total_students": total_students,
        "total_certificate": total_certificate,
        "total_draft_certificate": total_draft_certificate,
        "total_certificate_in_month": total_certificate_in_month,
    })
