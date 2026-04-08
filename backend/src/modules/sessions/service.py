from fastapi import HTTPException, status

from modules.sessions.repository import InMemorySessionRepository, SessionRecord, session_repository
from modules.sessions.schemas import SessionCreateRequest
from modules.stages.service import stage_service


class SessionService:
    def __init__(self, repository: InMemorySessionRepository) -> None:
        self._repository = repository

    def list_sessions(self) -> list[SessionRecord]:
        return self._repository.list_sessions()

    def create_session(self, payload: SessionCreateRequest) -> SessionRecord:
        return self._repository.create_session(
            title=payload.title,
            initial_question=payload.initial_question,
            tags=payload.tags,
        )

    def get_session(self, session_id: str) -> SessionRecord:
        session = self._repository.get_session(session_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found.",
            )
        return session

    def get_workspace(self, session_id: str) -> dict[str, object]:
        session = self.get_session(session_id)
        return {
            "session": self._serialize_session(session),
            "currentStage": session.current_stage,
            "stages": stage_service.list_stage_summaries(session_id),
        }

    def _serialize_session(self, session: SessionRecord) -> dict[str, object]:
        return {
            "id": session.id,
            "title": session.title,
            "initialQuestion": session.initial_question,
            "currentStage": session.current_stage,
            "status": session.status,
            "tags": session.tags,
        }


session_service = SessionService(session_repository)
