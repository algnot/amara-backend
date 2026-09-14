from datetime import datetime

from flask import Blueprint, jsonify, request

from model.certificate import Certificate
from model.course import Course
from model.permission import Permission
from model.saleperson import SalePerson
from model.student import Student
from model.users import User
from util.date import format_thai_date
from util.encryptor import encrypt
from util.request import handle_access_token, handle_error

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
        "filter": ["student_id", "firstname_th", "lastname_th", "firstname_en", "lastname_en"],
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


def uses_encrypted_contains_search(model_class, search_fields, filter_operator):
    if filter_operator not in ("ilike", "like"):
        return False

    encrypted_fields = set(getattr(model_class, "__encrypted_field__", []))
    return any(field in encrypted_fields for field in search_fields)


def record_matches_search(record, search_key, search_fields, filter_operator):
    if filter_operator in ("ilike", "like"):
        search_lower = search_key.lower()
        for field in search_fields:
            value = getattr(record, field, None)
            if value is not None and search_lower in str(value).lower():
                return True
        return False

    for field in search_fields:
        if getattr(record, field, None) == search_key:
            return True
    return False


def build_sql_filters(model_config, offset, search_key):
    filter_list = []
    if offset:
        filter_list.append((model_config["offset"], "<=", int(offset)))

    if not search_key:
        filter_list.extend(model_config["additional_filter"])
        return filter_list

    if offset:
        filter_list.append("and")

    search_value = encrypt(search_key) if model_config["need_encrypt"] else search_key
    filters_base = model_config["filter"]
    for index, value in enumerate(filters_base):
        filter_list.append((value, model_config["filter_operator"], search_value))
        if index < len(filters_base) - 1:
            filter_list.append("or")

    filter_list.extend(model_config["additional_filter"])
    return filter_list


def fetch_records_with_encrypted_search(model_config, offset, search_key, limit, order_by_list):
    filter_list = []
    if offset:
        filter_list.append((model_config["offset"], "<=", int(offset)))
    filter_list.extend(model_config["additional_filter"])

    records = model_config["model"]().filter(
        filters=filter_list,
        order_by=order_by_list,
        alway_list=True,
    )
    if not isinstance(records, list):
        records = [records]

    search_fields = model_config["filter"]
    filter_operator = model_config["filter_operator"]
    matched_records = [
        record
        for record in records
        if record_matches_search(record, search_key, search_fields, filter_operator)
    ]
    return matched_records[: limit + 1]

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

    if model not in mapper:
        raise Exception("model is not in mapper")

    if len(mapper[model]["permission"]) > 0 and not any(p in user_permissions for p in mapper[model]["permission"]):
        raise Exception("users do not have permission")

    model_config = mapper[model]
    order_by_list = []
    order_by_list.extend(model_config["additional_order"])
    order_by_list.append((model_config["offset"], "desc"))

    if search_key and uses_encrypted_contains_search(
        model_config["model"],
        model_config["filter"],
        model_config["filter_operator"],
    ):
        datas = fetch_records_with_encrypted_search(
            model_config,
            offset,
            search_key,
            limit,
            order_by_list,
        )
    else:
        filter_list = build_sql_filters(model_config, offset, search_key)
        datas = model_config["model"]().filter(filters=filter_list, limit=limit + 1, order_by=order_by_list)
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