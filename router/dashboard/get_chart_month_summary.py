from flask import Blueprint, jsonify, request
from model.base import Base
from util.request import handle_error, handle_access_token
from datetime import datetime

get_chart_month_summary_app = Blueprint("get_chart_month_summary", __name__)

@get_chart_month_summary_app.route("/chart-month-summary", methods=["GET"])
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
            YEAR(given_date) AS year,
            MONTH(given_date) AS month,
            COUNT(id) AS total
        FROM certificate
        WHERE batch != :batch
        AND given_date >= :start_date
        AND given_date < :end_date
        GROUP BY YEAR(given_date), MONTH(given_date)
        ORDER BY year, month
        """,
        {
            "batch": "draft",
            "start_date": start_date,
            "end_date": end_date
        },
        fetch=True
    )

    month_map = {
        1: "ม.ค.",
        2: "ก.พ.",
        3: "มี.ค.",
        4: "เม.ย.",
        5: "พ.ค.",
        6: "มิ.ย.",
        7: "ก.ค.",
        8: "ส.ค.",
        9: "ก.ย.",
        10: "ต.ค.",
        11: "พ.ย.",
        12: "ธ.ค."
    }

    data_map = {
        (row["year"], row["month"]): row["total"]
        for row in result
    }

    chart_data = []
    current = start_date

    while current < end_date:
        y = current.year
        m = current.month

        chart_data.append({
            "key": f"{month_map[m]} {y}",
            "value": data_map.get((y, m), 0)
        })

        if m == 12:
            current = datetime(y + 1, 1, 1)
        else:
            current = datetime(y, m + 1, 1)

    return jsonify(chart_data)
