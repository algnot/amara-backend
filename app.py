import sentry_sdk
from flask import Flask, jsonify
from flask_cors import CORS
from router.auth.auth import auth_app
from router.certificate.certificate import certificate_app
from router.course.course import course_app
from router.data.data import data_app
from router.export.export import export_app
from router.permission.permission import permission_app
from router.sale_person.sale_person import sale_person_app
from router.student.student import student_app
from router.user.user import user_app
from util.config import get_config

sentry_url = get_config("SENTRY_URL", "")

if sentry_url != "":
    sentry_sdk.init(
        dsn=sentry_url,
        send_default_pii=True,
        traces_sample_rate=1.0,
        profile_session_sample_rate=1.0,
        profile_lifecycle="trace",
        environment=get_config("APP_ENV", "development"),
    )

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_app)
app.register_blueprint(sale_person_app)
app.register_blueprint(data_app)
app.register_blueprint(student_app)
app.register_blueprint(course_app)
app.register_blueprint(certificate_app)
app.register_blueprint(export_app)
app.register_blueprint(permission_app)
app.register_blueprint(user_app)

@app.route("/_hc", methods=["GET"])
def _hc():
    return jsonify({"status": "server is running"})


if __name__ == "__main__":
    app.run(threaded=True)
