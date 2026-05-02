from flask import Blueprint, jsonify, request
from model.base import Base
from util.request import handle_error, handle_access_token
from datetime import datetime

get_chart_course_summary_app = Blueprint("get_chart_course_summary", __name__)

@get_chart_course_summary_app.route("/chart-course-summary", methods=["GET"])
@handle_access_token(permission=["read-dashboard-data"])
@handle_error
def get_summary():
    start_month = int(request.args.get("start_month"))
    start_year = int(request.args.get("start_year"))
    end_month = int(request.args.get("end_month"))
    end_year = int(request.args.get("end_year"))

    start_date = datetime(start_year, start_month, 1)

    if end_month == 12:
        end_date = datetime(end_year + 1, 1, 1)
    else:
        end_date = datetime(end_year, end_month + 1, 1)

    result = Base().execute_raw(
        """
        SELECT 
            co.name_th AS course_name,
            COUNT(c.id) AS total
        FROM certificate c
        JOIN course co ON c.course_id = co.id
        WHERE c.batch != :batch
        AND c.given_date >= :start_date
        AND c.given_date < :end_date
        AND c.archived = 0
        GROUP BY co.id, co.name_th
        ORDER BY total DESC
        """,
        {
            "batch": "draft",
            "start_date": start_date,
            "end_date": end_date
        },
        fetch=True
    )

    course_chart_data = [
        {
            "key": row["course_name"],
            "value": row["total"]
        }
        for row in result
    ]

    return jsonify(course_chart_data)