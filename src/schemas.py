from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class EvidenceCitation(BaseModel):
    source_file: str = Field(default="unknown")
    identifier_or_timestamp: Optional[str] = Field(default="N/A")
    demonstrated_signal: str = Field(default="unspecified")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)

class ArtistIntelligenceRecord(BaseModel):
    artist_id: str
    category: str  # "photographer", "musician", "video_editor"
    claimed_capabilities: List[str] = Field(default_factory=list)
    demonstrated_capabilities: List[str] = Field(default_factory=list)
    category_dimensions: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[EvidenceCitation] = Field(default_factory=list)
    unknowns_and_limitations: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence_rationale: str = Field(default="Extracted from available portfolio signals.")

class RankedArtist(BaseModel):
    rank: int
    artist_id: str
    match_score: float
    reasons: List[str] = Field(default_factory=list)
    trade_offs: List[str] = Field(default_factory=list)
    relevant_demonstrated_signals: List[str] = Field(default_factory=list)
    irrelevant_or_unsupported_signals: List[str] = Field(default_factory=list)

class RefinementQuestion(BaseModel):
    question: str
    potential_answers_impact: Dict[str, str] = Field(default_factory=dict)

class HirerRecommendation(BaseModel):
    brief_id: str
    interpreted_intent: Dict[str, Any] = Field(default_factory=dict)
    top_artists: List[RankedArtist] = Field(default_factory=list)
    key_assumptions: List[str] = Field(default_factory=list)
    uncertainty_assessment: str = Field(default="Moderate")
    refinement_questions: List[RefinementQuestion] = Field(default_factory=list)

class UpdatedRecommendation(BaseModel):
    brief_id: str
    follow_up_context: str
    previous_ranking: List[str] = Field(default_factory=list)
    updated_ranking: List[RankedArtist] = Field(default_factory=list)
    ranking_change_explanation: str