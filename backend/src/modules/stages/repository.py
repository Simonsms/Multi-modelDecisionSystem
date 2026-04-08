from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import uuid4

STAGE_ORDER = [
    "problem_definition",
    "research_analysis",
    "option_comparison",
    "decision_recommendation",
]


@dataclass
class StageRunRecord:
    session_id: str
    stage: str
    triggered_by: str
    result_snapshot: dict[str, object]
    id: str = field(default_factory=lambda: f"sr_{uuid4().hex[:12]}")
    status: str = "completed"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class InMemoryStageRepository:
    def __init__(self) -> None:
        self._stage_runs: dict[str, StageRunRecord] = {}

    def create_stage_run(
        self,
        *,
        session_id: str,
        stage: str,
        triggered_by: str,
        result_snapshot: dict[str, object],
    ) -> StageRunRecord:
        record = StageRunRecord(
            session_id=session_id,
            stage=stage,
            triggered_by=triggered_by,
            result_snapshot=deepcopy(result_snapshot),
        )
        self._stage_runs[record.id] = record
        return deepcopy(record)

    def get_stage_run(self, stage_run_id: str) -> StageRunRecord | None:
        record = self._stage_runs.get(stage_run_id)
        if record is None:
            return None
        return deepcopy(record)

    def list_stage_runs(self, session_id: str) -> list[StageRunRecord]:
        return [
            deepcopy(record)
            for record in self._stage_runs.values()
            if record.session_id == session_id
        ]

    def get_latest_stage_run(self, session_id: str, stage: str) -> StageRunRecord | None:
        matched = [
            record
            for record in self._stage_runs.values()
            if record.session_id == session_id and record.stage == stage
        ]
        if not matched:
            return None
        latest = max(matched, key=lambda item: item.created_at)
        return deepcopy(latest)

    def reset(self) -> None:
        self._stage_runs.clear()


stage_repository = InMemoryStageRepository()
