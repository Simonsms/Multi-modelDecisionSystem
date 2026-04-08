from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StageRunStartRequest(BaseModel):
    triggered_by: str = Field(alias="triggeredBy")
    context_patch: dict[str, object] = Field(default_factory=dict, alias="contextPatch")

    model_config = ConfigDict(populate_by_name=True)


class StageRunItem(BaseModel):
    id: str
    session_id: str = Field(alias="sessionId")
    stage: str
    status: str
    triggered_by: str = Field(alias="triggeredBy")
    result_snapshot: dict[str, object] = Field(alias="resultSnapshot")
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)


class StageSummaryItem(BaseModel):
    stage: str
    status: str
    latest_run_id: str | None = Field(alias="latestRunId")

    model_config = ConfigDict(populate_by_name=True)


class StageListResponse(BaseModel):
    items: list[StageSummaryItem]
