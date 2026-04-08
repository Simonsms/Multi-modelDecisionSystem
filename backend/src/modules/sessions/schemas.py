from pydantic import BaseModel, ConfigDict, Field


class SessionCreateRequest(BaseModel):
    title: str
    initial_question: str = Field(alias="initialQuestion")
    tags: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class SessionItem(BaseModel):
    id: str
    title: str
    initial_question: str = Field(alias="initialQuestion")
    current_stage: str = Field(alias="currentStage")
    status: str
    tags: list[str]

    model_config = ConfigDict(populate_by_name=True)


class SessionListResponse(BaseModel):
    items: list[SessionItem]
