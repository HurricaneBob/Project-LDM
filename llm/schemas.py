from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class CommunicationSignals(BaseModel):
    empathy: float = 0.5
    clarity: float = 0.5
    decisiveness: float = 0.5
    aggression: float = 0.2
    supportiveness: float = 0.5
    adaptability: float = 0.5


class SemanticAnalysisResponse(BaseModel):
    communication_signals: CommunicationSignals
    leadership_style_tag: str = "Collaborative"
    conflict_escalation_risk: str = "moderate"


_SPEAKER_KEYS = {"speaking_agent", "agent_id", "agent", "speaker", "name", "persona", "persona_id"}
_TEXT_KEYS = {
    "ai_response", "dialogue_text", "response", "message", "text", "utterance",
    "content", "statement", "line", "reply", "quote", "speech", "words", "says",
    "dialogue", "spoken_text", "agent_response",
}


class DialogueLine(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")
    speaking_agent: str = Field(validation_alias=AliasChoices(*_SPEAKER_KEYS))
    ai_response: str = Field(validation_alias=AliasChoices(*_TEXT_KEYS))

    @model_validator(mode="before")
    @classmethod
    def _flexible_keys(cls, data):
        if not isinstance(data, dict):
            return data
        out = dict(data)
        if not any(k in out for k in _SPEAKER_KEYS):
            for k, v in data.items():
                if isinstance(v, str) and (
                    "agent" in k.lower() or "speaker" in k.lower() or "name" in k.lower()
                ):
                    out["speaking_agent"] = v
                    break
        if not any(k in out for k in _TEXT_KEYS):
            speaker_val = out.get("speaking_agent")
            for k, v in data.items():
                if isinstance(v, str) and v != speaker_val and len(v) > 10:
                    out["ai_response"] = v
                    break
        return out


class DialogueGenerationResponse(BaseModel):
    lines: List[DialogueLine] = Field(default_factory=list)
    narration: str = ""


class GameInitResponse(BaseModel):
    selected_scenario: str = "Scenario 1"
    situation_brief: str = ""


class ScenarioInitResponse(BaseModel):
    selected_scenario: str = ""
    situation_brief: str = ""


class ScenarioSummaryResponse(BaseModel):
    scenario_outcome_summary: str = ""


class HolisticResults(BaseModel):
    parameter_deltas_analysis: str = ""
    leadership_pattern_summary: str = ""
    hr_competency_verdict: str = ""


class HolisticSummaryResponse(BaseModel):
    holistic_results: HolisticResults


# Legacy compatibility
class CommunicationClassification(BaseModel):
    tone: str = "neutral"
    targets: List[str] = Field(default_factory=list)
    intents: List[str] = Field(default_factory=list)
    confidence: float = 0.8


class DialogueResponse(BaseModel):
    narration: str = ""
    lines: List[dict] = Field(default_factory=list)
    turn_summary: str = ""


class OpeningResponse(BaseModel):
    opening_narration: str = ""
    lines: List[dict] = Field(default_factory=list)


class MemoryExtract(BaseModel):
    memory: str


class DimensionScores(BaseModel):
    emotional_regulation: float = Field(ge=0, le=10, default=7.0)
    conflict_mediation: float = Field(ge=0, le=10, default=7.0)
    trust_building: float = Field(ge=0, le=10, default=7.0)
    adaptability: float = Field(ge=0, le=10, default=7.0)
    leadership_communication: float = Field(ge=0, le=10, default=7.0)


class FinalEvaluation(BaseModel):
    leadership_analysis: str = ""
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    cohesion_impact: str = ""
    emotional_impact: str = ""
    dimension_scores: DimensionScores = Field(default_factory=DimensionScores)
