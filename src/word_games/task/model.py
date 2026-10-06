import uuid
from datetime import datetime

from pydantic import BaseModel


class TaskNaturalIdentifier(BaseModel):
    hrid: str
    assignee_public_id: uuid.UUID
    creator_public_id: uuid.UUID

    @property
    def task_name(self) -> str:
        return self.hrid.split("-")[0]


class TaskResults(TaskNaturalIdentifier):
    score: int
    max_score: int
    solved_at: datetime
    response: dict
