from flask import Flask, jsonify
from flask_cors import CORS

from router.auth.auth import auth_app
from router.data.data import data_app
from router.pdf.pdf import pdf_app
from router.sale_person.sale_person import sale_person_app
from router.student.student import student_app

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_app)
app.register_blueprint(pdf_app)
app.register_blueprint(sale_person_app)
app.register_blueprint(data_app)
app.register_blueprint(student_app)

@app.route("/_hc", methods=["GET"])
def _hc():
    return jsonify({"status": "server is running"})


if __name__ == "__main__":
    app.run()
