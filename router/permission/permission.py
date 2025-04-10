from flask import Blueprint

from router.permission.add_permission import add_permission_app
from router.permission.get_permission import get_permission_app
from router.permission.update_permission import update_permission_app

permission_app = Blueprint("permission", __name__, url_prefix="/permission")

permission_app.register_blueprint(add_permission_app)
permission_app.register_blueprint(get_permission_app)
permission_app.register_blueprint(update_permission_app)

