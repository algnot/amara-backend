from sqlalchemy import Column, ForeignKey, Integer

from model.base import Base


class UserToPermission(Base):
    __tablename__ = "user_to_permission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    permission_id = Column(Integer, ForeignKey("permission.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
