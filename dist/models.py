from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, VARCHAR, TIMESTAMP, ENUM, BOOLEAN

from database import Base
from enum import Enum
import uuid


class Status(str, Enum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"


class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID)
    title = Column(VARCHAR)
    started_on = Column(TIMESTAMP)
    is_deleted = Column(BOOLEAN, default=False)


class Message(Base):
    __tablename__ = "message"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID, ForeignKey("conversation.id"))
    question = Column(VARCHAR)
    question_time = Column(TIMESTAMP)
    answer = Column(VARCHAR)
    answer_time = Column(TIMESTAMP)
    status = Column(ENUM(Status), default=Status.PENDING)

    conversation = relationship("Conversation", backref="messages")
