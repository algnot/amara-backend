from sqlalchemy import create_engine, and_, or_, asc, desc
from sqlalchemy.orm import declarative_base, sessionmaker
from util.encryptor import encrypt, decrypt
from util.config import get_config
from sqlalchemy import text

BaseClass = declarative_base()
ENGINE = None
SESSION_MAKER = None


def _get_bool_config(key: str, default=False):
    return get_config(key, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _get_int_config(key: str, default: int):
    value = get_config(key, str(default))
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_database_config():
    ssl_ca_path = get_config("DATABASE_SSL_CA", "")

    host = get_config("DATABASE_HOST", "localhost")
    port = get_config("DATABASE_PORT", "3306")
    user = get_config("DATABASE_USERNAME", "root")
    password = get_config("DATABASE_PASSWORD", "root")
    database = get_config("DATABASE_NAME", "tongla-hub")

    if ssl_ca_path:
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?ssl=VERIFY_IDENTITY&ssl_ca={ssl_ca_path}"
    else:
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


def get_engine():
    global ENGINE

    if ENGINE is None:
        ENGINE = create_engine(
            get_database_config(),
            echo=_get_bool_config("DATABASE_ECHO", False),
            pool_size=_get_int_config("DATABASE_POOL_SIZE", 5),
            max_overflow=_get_int_config("DATABASE_MAX_OVERFLOW", 5),
            pool_timeout=_get_int_config("DATABASE_POOL_TIMEOUT", 30),
            pool_recycle=_get_int_config("DATABASE_POOL_RECYCLE", 1800),
            pool_pre_ping=True,
            pool_use_lifo=True,
        )

    return ENGINE


def get_session_maker():
    global SESSION_MAKER

    if SESSION_MAKER is None:
        SESSION_MAKER = sessionmaker(bind=get_engine(), expire_on_commit=False)

    return SESSION_MAKER


class Base(BaseClass):
    __abstract__ = True
    __encrypted_field__ = []

    session = None
    query = None

    def __init__(self):
        super().__init__()

    def close_connection(self):
        if self.session is not None:
            self.session.close()
            self.session = None
            self.query = None

    def create_new_session(self):
        if self.session is not None:
            return

        self.session = get_session_maker()()
        self.query = self.session.query(self.__class__)

    def create(self, values=None):
        if values is None:
            values = {}

        try:
            self.create_new_session()

            for key, value in values.items():
                setattr(self, key, value)

            for field in self.__encrypted_field__:
                setattr(self, field, encrypt(getattr(self, field)))

            self.session.add(self)
            self.session.commit()
            self.session.refresh(self)

            for field in self.__encrypted_field__:
                decrypted_value = decrypt(getattr(self, field))
                setattr(self, field, decrypted_value)

            return self
        except Exception as e:
            if self.session is not None:
                self.session.rollback()
            raise e
        finally:
            self.close_connection()

    def update(self, values=None):
        if values is None:
            values = {}

        try:
            self.create_new_session()

            for key, value in values.items():
                setattr(self, key, value)

            for field in self.__encrypted_field__:
                setattr(self, field, encrypt(getattr(self, field)))

            self.session.merge(self)
            self.session.commit()

            for field in self.__encrypted_field__:
                decrypted_value = decrypt(getattr(self, field))
                setattr(self, field, decrypted_value)

            return self
        except Exception as e:
            if self.session is not None:
                self.session.rollback()
            raise e
        finally:
            self.close_connection()

    def get_by_id(self, id):
        try:
            self.create_new_session()
            record = self.session.get(self.__class__, id)

            if record is None:
                return None

            for field in self.__encrypted_field__:
                decrypted_value = decrypt(getattr(record, field))
                setattr(record, field, decrypted_value)

            return record
        finally:
            self.close_connection()

    def filter(self, filters=None, limit=999999999, order_by=None, alway_list=False):
        if filters is None:
            filters = []

        try:
            self.create_new_session()
            filter_query = []
            current_conditions = []
            or_conditions = []

            for condition in filters:
                if condition == "or":
                    if current_conditions:
                        or_conditions.append(current_conditions)
                    current_conditions = []
                elif condition == "and":
                    continue
                else:
                    field, condition_operator, value = condition
                    if condition_operator == "ilike":
                        current_conditions.append(getattr(self.__class__, field).ilike(f"%{value}%"))
                    elif condition_operator == "<=":
                        current_conditions.append(getattr(self.__class__, field) <= value)
                    elif condition_operator == ">=":
                        current_conditions.append(getattr(self.__class__, field) >= value)
                    elif condition_operator == "<":
                        current_conditions.append(getattr(self.__class__, field) < value)
                    elif condition_operator == ">":
                        current_conditions.append(getattr(self.__class__, field) > value)
                    elif condition_operator == "in":
                        current_conditions.append(getattr(self.__class__, field).in_(value))
                    elif condition_operator == "!=":
                        current_conditions.append(getattr(self.__class__, field) != value)
                    else:
                        current_conditions.append(getattr(self.__class__, field) == value)

            if current_conditions:
                or_conditions.append(current_conditions)

            if or_conditions:
                filter_query = or_(*[and_(*group) for group in or_conditions])
            else:
                filter_query = and_(*filter_query)

            if order_by:
                if isinstance(order_by, list):
                    order_criteria = []
                    for order_item in order_by:
                        if isinstance(order_item, tuple) and len(order_item) == 2:
                            field, direction = order_item
                            if direction.lower() == "desc":
                                order_criteria.append(desc(getattr(self.__class__, field)))
                            else:
                                order_criteria.append(asc(getattr(self.__class__, field)))
                        else:
                            order_criteria.append(asc(getattr(self.__class__, order_item)))
                else:
                    order_criteria = [asc(getattr(self.__class__, order_by))]
            else:
                order_criteria = []

            query = self.query.filter(filter_query)
            if order_criteria:
                query = query.order_by(*order_criteria)

            records = query.limit(limit).all()
            result_list = []

            for record in records:
                for field in self.__encrypted_field__:
                    decrypted_value = decrypt(getattr(record, field))
                    setattr(record, field, decrypted_value)
                result_list.append(record)

            if len(result_list) == 1 and not alway_list:
                return result_list[0]

            return result_list
        finally:
            self.close_connection()

    def unlink(self):
        try:
            self.create_new_session()
            self.session.delete(self)
            self.session.commit()
        except Exception as e:
            if self.session is not None:
                self.session.rollback()
            raise e
        finally:
            self.close_connection()

    def execute_raw(self, sql: str, params: dict = None, fetch: bool = False):
        session = get_session_maker()()

        try:
            result = session.execute(text(sql), params or {})

            if fetch:
                return result.mappings().all()

            session.commit()
            return result.rowcount

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def __del__(self):
        self.close_connection()

    def __enter__(self):
        return self
