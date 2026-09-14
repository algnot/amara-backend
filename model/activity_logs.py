from datetime import UTC, datetime

from sqlalchemy import TEXT, TIMESTAMP, VARCHAR, Column, Integer

from model.base import Base


class ActivityLogs(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(VARCHAR(255), nullable=False)
    ref_id = Column(Integer, nullable=False)
    content = Column(TEXT, nullable=False)

    created_at = Column(TIMESTAMP, default=datetime.now(UTC), nullable=False)

    def create_activity_log(self, topic, ref_id, content):
        find_duplicate_log = self.filter(filters=[("topic", "=" ,topic), ("ref_id", "=", ref_id)], order_by=[("id", "desc")], limit=1, alway_list=True)

        if len(find_duplicate_log) > 0 and content == find_duplicate_log[0].content:
            return

        return super().create({
            "topic": topic,
            "ref_id": ref_id,
            "content": content,
            "created_at": datetime.now(UTC),
        })

    def get_activity_logs(self, topic, ref_id):
        return self.filter(filters=[("topic", "=" ,topic), ("ref_id", "=", ref_id)], alway_list=True)
