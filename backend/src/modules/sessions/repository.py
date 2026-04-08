from copy import deepcopy
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class SessionRecord:
    title: str
    initial_question: str
    tags: list[str]
    id: str = field(default_factory=lambda: f"ses_{uuid4().hex[:12]}")
    current_stage: str = "problem_definition"
    status: str = "active"


class InMemorySessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}

    def list_sessions(self) -> list[SessionRecord]:
        return [deepcopy(item) for item in self._sessions.values()]

    def create_session(self, *, title: str, initial_question: str, tags: list[str]) -> SessionRecord:
        record = SessionRecord(
            title=title,
            initial_question=initial_question,
            tags=list(tags),
        )
        self._sessions[record.id] = record
        return deepcopy(record)

    def get_session(self, session_id: str) -> SessionRecord | None:
        record = self._sessions.get(session_id)
        if record is None:
            return None
        return deepcopy(record)

    def reset(self) -> None:
        self._sessions.clear()


session_repository = InMemorySessionRepository()
