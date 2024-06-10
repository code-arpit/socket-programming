from pydantic import BaseModel
import uuid
from datetime import datetime
from models import Status
from typing import Any
from pydantic import field_validator


class MessageRequestModel(BaseModel):
    conversation_id: uuid.UUID
    question: str | None = None
    question_time: datetime | None = None
    answer: str | None = None
    answer_time: datetime | None = None
    status: Status | None = Status.PENDING


class MessageResponseModel(BaseModel):
    id: uuid.UUID | None
    conversation_id: uuid.UUID | None
    question: str | None
    question_time: Any | None
    answer: str | None
    answer_time: Any | None
    status: Status | None

    @field_validator("question_time")
    def set_question_time(cls, question_time: str):
        if question_time:
            return int(datetime.fromisoformat(str(question_time)).timestamp() * 1000)

    @field_validator("answer_time")
    def set_answer_time(cls, answer_time: str):
        if answer_time:
            return int(datetime.fromisoformat(str(answer_time)).timestamp() * 1000)


class ConversationResponseModel(BaseModel):
    id: uuid.UUID | None
    user_id: uuid.UUID | None
    title: str | None
    started_on: Any | None
    is_deleted: bool | None

    @field_validator("started_on")
    def set_started_on(cls, started_on: str):
        if started_on:
            return int(datetime.fromisoformat(str(started_on)).timestamp() * 1000)


class ConversationRequestModel(BaseModel):
    user_id: uuid.UUID
    title: str
    started_on: datetime
