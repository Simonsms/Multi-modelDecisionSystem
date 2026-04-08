from fastapi import APIRouter

from app.deps import make_response
from modules.stages.schemas import StageListResponse, StageRunItem, StageRunStartRequest, StageSummaryItem
from modules.stages.service import stage_service

router = APIRouter(tags=["stages"])


@router.get("/sessions/{session_id}/stages")
def list_stages(session_id: str) -> dict[str, object]:
    items = [
        StageSummaryItem.model_validate(item).model_dump(by_alias=True)
        for item in stage_service.list_stage_summaries(session_id)
    ]
    return make_response(StageListResponse(items=items).model_dump(by_alias=True))


@router.get("/sessions/{session_id}/stages/{stage}")
def get_stage_detail(session_id: str, stage: str) -> dict[str, object]:
    return make_response(stage_service.get_stage_detail(session_id, stage))


@router.post("/sessions/{session_id}/stages/{stage}/start")
def start_stage(session_id: str, stage: str, payload: StageRunStartRequest) -> dict[str, object]:
    stage_run = stage_service.start_stage(session_id, stage, payload)
    serialized = StageRunItem.model_validate(stage_run, from_attributes=True).model_dump(by_alias=True)
    return make_response(serialized)


@router.get("/stage-runs/{stage_run_id}")
def get_stage_run(stage_run_id: str) -> dict[str, object]:
    stage_run = stage_service.get_stage_run(stage_run_id)
    serialized = StageRunItem.model_validate(stage_run, from_attributes=True).model_dump(by_alias=True)
    return make_response(serialized)
