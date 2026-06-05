from pydantic import BaseModel, Field


class Citation(BaseModel):
    pmid: str
    title: str
    journal: str = "Unknown journal"
    year: str = "n.d."
    url: str
    snippet: str
    score: float = Field(ge=0)


class AgentTraceItem(BaseModel):
    agent: str
    action: str
    detail: str


class SafetyStatus(BaseModel):
    allowed: bool
    category: str
    reason: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1200)


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    agent_trace: list[AgentTraceItem]
    safety_status: SafetyStatus
    retrieval_scores: list[float]
    confidence: str


class PubMedSearchResponse(BaseModel):
    query: str
    citations: list[Citation]


class EvalResult(BaseModel):
    scenario: str
    passed: bool
    detail: str


class EvalResponse(BaseModel):
    results: list[EvalResult]
    pass_rate: float
