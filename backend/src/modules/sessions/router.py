from fastapi import APIRouter, status

from app.deps import make_response
from modules.sessions.schemas import SessionCreateRequest, SessionItem, SessionListResponse
from modules.sessions.service import session_service

router = APIRouter(tags=["sessions"])


def _to_session_item(record: object) -> SessionItem:
    return SessionItem.model_validate(record, from_attributes=True)


@router.get("/sessions")
def list_sessions() -> dict[str, object]:
    items = [_to_session_item(record) for record in session_service.list_sessions()]
    return make_response(SessionListResponse(items=items).model_dump(by_alias=True))


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionCreateRequest) -> dict[str, object]:
    created = session_service.create_session(payload)
    return make_response(_to_session_item(created).model_dump(by_alias=True))


@router.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, object]:
    session = session_service.get_session(session_id)
    return make_response(_to_session_item(session).model_dump(by_alias=True))


@router.get("/sessions/{session_id}/workspace")
def get_workspace(session_id: str) -> dict[str, object]:
    return make_response(session_service.get_workspace(session_id))
