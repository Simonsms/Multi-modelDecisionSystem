from modules.stages.repository import STAGE_ORDER, StageRunRecord, stage_repository
from modules.stages.schemas import StageRunStartRequest
from orchestration.role_router import ROLE_MODEL_MAP


class StageOrchestrator:
    def start_stage(self, session_id: str, stage: str, payload: StageRunStartRequest) -> StageRunRecord:
        if stage not in STAGE_ORDER:
            raise ValueError(f"Unsupported stage: {stage}")

        result_snapshot = {
            "summary": "stub result",
            "stage": stage,
            "provider": ROLE_MODEL_MAP[stage]["primary"],
            "contextPatch": payload.context_patch,
        }
        return stage_repository.create_stage_run(
            session_id=session_id,
            stage=stage,
            triggered_by=payload.triggered_by,
            result_snapshot=result_snapshot,
        )


stage_orchestrator = StageOrchestrator()
