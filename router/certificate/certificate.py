from flask import Blueprint
from router.certificate.request_certificate import request_certificate_app


certificate_app = Blueprint("certificate", __name__, url_prefix="/certificate")

certificate_app.register_blueprint(request_certificate_app)

