from datetime import datetime, timezone
from sqlalchemy import Column, Integer, VARCHAR, TIMESTAMP, TEXT
from model.base import Base

class ActivityLogs(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(VARCHAR(255), nullable=False)
    ref_id = Column(Integer, nullable=False)
    content = Column(TEXT, nullable=False)

    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc), nullable=False)

    def create_activity_log(self, topic, ref_id, content):
        return super().create({
            "topic": topic,
            "ref_id": ref_id,
            "content": content,
            "created_at": datetime.now(timezone.utc),
        })

    def get_activity_logs(self, topic, ref_id):
        return self.filter(filters=[("topic", "=" ,topic), ("ref_id", "=", ref_id)], alway_list=True)
