from datetime import datetime
from flask import Blueprint, jsonify, request
from model.certificate import Certificate
from model.course import Course
from model.saleperson import SalePerson
from model.student import Student
from model.users import User
from model.permission import Permission
from util.date import format_thai_date
from util.encryptor import encrypt
from util.request import handle_error, handle_access_token

list_data_app = Blueprint("list_data_app", __name__)

mapper = {
    "sale_person": {
        "model": SalePerson,
        "offset": "id",
        "filter": ["reference_code"],
        "filter_operator": "=",
        "additional_filter": [],
        "additional_order": [],
        "permission": ["read-sale-person-data"],
        "mapper_key": ["id", "firstname", "lastname", "reference_code"],
        "mapper_value": ["id", "firstname", "lastname", "reference_code"],
        "need_encrypt": False,
    },
    "student": {
        "model": Student,
        "offset": "id",
        "filter": ["student_id"],
        "filter_operator": "ilike",
        "additional_filter": [],
        "additional_order": [],
        "permission": ["read-student-data"],
        "mapper_key": ["id", "student_id", "firstname_th", "lastname_th", "firstname_en", "lastname_en"],
        "mapper_value": ["id", "student_id", "firstname_th", "lastname_th", "firstname_en", "lastname_en"],
        "need_encrypt": False,
    },
    "user": {
        "model": User,
        "offset": "id",
        "filter": ["username", "email"],
        "filter_operator": "=",
        "additional_filter": [],
        "additional_order": [],
        "permission": [],
        "mapper_key": ["uid", "username", "email", "role", "image_url"],
        "mapper_value": ["id", "username", "email", "role.name", "image_url"],
        "need_encrypt": True,
    },
    "course": {
        "model": Course,
        "offset": "id",
        "filter": ["course_code", "name_th", "name_en"],
        "filter_operator": "ilike",
        "additional_filter": [],
        "additional_order": [],
        "permission": ["read-course-data"],
        "mapper_key": ["id", "course_code", "name_th", "name_en"],
        "mapper_value": ["id", "course_code", "name_th", "name_en"],
        "need_encrypt": False,
    },
    "certificate": {
        "model": Certificate,
        "offset": "id",
        "filter": ["certificate_number", "batch"],
        "filter_operator": "ilike",
        "additional_filter": [("archived", "=", False)],
        "additional_order": [],
        "permission": ["read-certificate-data"],
        "mapper_key": ["id", "certificate_number", "batch", "start_date", "end_date"],
        "mapper_value": ["id", "certificate_number", "batch", "start_date", "end_date"],
        "need_encrypt": False,
    },
    "permission": {
        "model": Permission,
        "offset": "id",
        "filter": ["key", "name", "description"],
        "filter_operator": "ilike",
        "additional_filter": [],
        "additional_order": [],
        "permission": [],
        "mapper_key": ["id", "key", "name", "description"],
        "mapper_value": ["id", "key", "name", "description"],
        "need_encrypt": False,
    }
}

def resolve_nested_attribute(obj, attr_path):
    attrs = attr_path.split(".")
    for attr in attrs:
        obj = getattr(obj, attr, None)
        if obj is None:
            break
    return obj

@list_data_app.route("/list", methods=["GET"])
@handle_access_token()
@handle_error
def list_data():
    user_permissions = request.permissions
    query = request.args
    model = query.get("model", "")
    limit = int(query.get("limit", 20))
    offset = query.get("offset", False)
    search_key = query.get("text", False)

    if model not in mapper.keys():
        raise Exception("model is not in mapper")

    if len(mapper[model]["permission"]) > 0 and not any(p in user_permissions for p in mapper[model]["permission"]):
        raise Exception("users do not have permission")

    filter_list = []
    if offset:
        filter_list.append((mapper[model]["offset"], "<=", int(offset)))

    if search_key:
        if offset:
            filter_list.append("and")
        if mapper[model]["need_encrypt"]:
            search_key = encrypt(search_key)

        filter_list = []
        filters_base = mapper[model]["filter"]
        for index, value in enumerate(filters_base):
            condition = (value, mapper[model]["filter_operator"], search_key)
            filter_list.append(condition)

            if index < len(filters_base) - 1:
                filter_list.append("or")

    filter_list.extend(mapper[model]["additional_filter"])

    order_by_list = []
    order_by_list.extend(mapper[model]["additional_order"])
    order_by_list.append((mapper[model]["offset"], "desc"))

    datas = mapper[model]["model"]().filter(filters=filter_list, limit=limit + 1, order_by=order_by_list)
    if not isinstance(datas, list):
        datas = [datas]
    response = []

    for data in datas[:limit]:
        to_append = {}
        for index, key in enumerate(mapper[model]["mapper_key"]):
            attr_path = mapper[model]["mapper_value"][index]
            value = resolve_nested_attribute(data, attr_path)
            if isinstance(value, datetime):
                value = format_thai_date(value)
            to_append[key] = value
        response.append(to_append)

    return jsonify({
        "datas": response,
        "next": -1 if len(response) < limit else getattr(datas[-1], mapper[model]["offset"]),
    })