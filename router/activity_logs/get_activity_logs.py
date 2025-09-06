from flask import Blueprint, jsonify

from model.activity_logs import ActivityLogs
from util.request import handle_error, handle_access_token

get_activity_logs_app = Blueprint("get_activity_logs", __name__)

@get_activity_logs_app.route("/<string:topic>/<string:ref_id>", methods=["GET"])
@handle_access_token(permission=["read-activity-logs-data"])
@handle_error
def get_user_by_id(topic, ref_id):
    activity_logs = ActivityLogs().get_activity_logs(topic, ref_id)

    datas = []
    for activity in activity_logs:
        datas.append({
            "content": activity.content,
            "created_at": activity.created_at,
        })

    return jsonify({
        "datas": datas
    })