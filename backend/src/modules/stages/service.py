from fastapi import HTTPException, status

from modules.sessions.repository import session_repository
from modules.stages.repository import STAGE_ORDER, StageRunRecord, stage_repository
from modules.stages.schemas import StageRunStartRequest
from orchestration.stage_orchestrator import stage_orchestrator


class StageService:
    def list_stage_summaries(self, session_id: str) -> list[dict[str, object]]:
        self._assert_session_exists(session_id)
        items: list[dict[str, object]] = []
        for stage in STAGE_ORDER:
            latest = stage_repository.get_latest_stage_run(session_id, stage)
            items.append(
                {
                    "stage": stage,
                    "status": latest.status if latest else "pending",
                    "latestRunId": latest.id if latest else None,
                }
            )
        return items

    def get_stage_detail(self, session_id: str, stage: str) -> dict[str, object]:
        self._assert_session_exists(session_id)
        self._assert_stage_supported(stage)
        latest = stage_repository.get_latest_stage_run(session_id, stage)
        return {
            "stage": stage,
            "status": latest.status if latest else "pending",
            "latestRun": self._serialize_stage_run(latest) if latest else None,
        }

    def start_stage(self, session_id: str, stage: str, payload: StageRunStartRequest) -> StageRunRecord:
        self._assert_session_exists(session_id)
        self._assert_stage_supported(stage)
        return stage_orchestrator.start_stage(session_id, stage, payload)

    def get_stage_run(self, stage_run_id: str) -> StageRunRecord:
        stage_run = stage_repository.get_stage_run(stage_run_id)
        if stage_run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stage run {stage_run_id} not found.",
            )
        return stage_run

    def _assert_session_exists(self, session_id: str) -> None:
        if session_repository.get_session(session_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found.",
            )

    def _assert_stage_supported(self, stage: str) -> None:
        if stage not in STAGE_ORDER:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stage {stage} not found.",
            )

    def _serialize_stage_run(self, stage_run: StageRunRecord) -> dict[str, object]:
        return {
            "id": stage_run.id,
            "sessionId": stage_run.session_id,
            "stage": stage_run.stage,
            "status": stage_run.status,
            "triggeredBy": stage_run.triggered_by,
            "resultSnapshot": stage_run.result_snapshot,
            "createdAt": stage_run.created_at.isoformat(),
        }


stage_service = StageService()
