import json
from typing import List, Dict, Any
from groq import Groq
from src.schemas import ArtistIntelligenceRecord, HirerRecommendation

class HirerMatcher:
    def __init__(self, groq_client: Groq, model: str = "openai/gpt-oss-120b"):
        self.client = groq_client
        self.model = model

    def _compress_artist_record(self, artist: ArtistIntelligenceRecord) -> Dict[str, Any]:
        """Strips verbose rationale and limits citations to stay well below TPM limits."""
        return {
            "artist_id": artist.artist_id,
            "category": artist.category,
            "claimed_capabilities": artist.claimed_capabilities,
            "demonstrated_capabilities": artist.demonstrated_capabilities,
            "category_dimensions": artist.category_dimensions,
            "evidence_signals": [
                f"{e.source_file} ({e.identifier_or_timestamp}): {e.demonstrated_signal}" 
                for e in artist.evidence[:4]
            ],
            "overall_confidence": artist.overall_confidence
        }

    def match_brief(self, brief_id: str, brief_text: str, artists: List[ArtistIntelligenceRecord]) -> HirerRecommendation:
        # Compress all artist records to reduce prompt token footprint
        compressed_artists = [self._compress_artist_record(a) for a in artists]

        prompt = f"""
You are matching an incomplete creative marketplace hirer brief against evidence-backed individual artist records.

Hirer Brief ({brief_id}):
\"\"\"{brief_text}\"\"\"

Artist Intelligence Records:
{json.dumps(compressed_artists, indent=2)}

TASK:
1. Interpret intent: Identify explicit constraints, reasonable assumptions, contradictions, and critical unknowns.
2. Select top 2 ranked individual artists based strictly on DEMONSTRATED capabilities matching the brief.
3. Detail reasons, trade-offs, relevant demonstrated signals, and irrelevant signals for each.
4. Formulate exactly up to 2 high-leverage refinement questions explaining how answers materially alter rankings.

Output strict JSON matching this schema:
{{
  "brief_id": "{brief_id}",
  "interpreted_intent": {{
    "explicit_constraints": ["..."],
    "reasonable_assumptions": ["..."],
    "contradictions": ["..."],
    "critical_unknowns": ["..."]
  }},
  "top_artists": [
    {{
      "rank": 1,
      "artist_id": "EXACT_ARTIST_ID_HERE",
      "match_score": 0.0 to 1.0,
      "reasons": ["..."],
      "trade_offs": ["..."],
      "relevant_demonstrated_signals": ["..."],
      "irrelevant_or_unsupported_signals": ["..."]
    }},
    {{
      "rank": 2,
      "artist_id": "EXACT_ARTIST_ID_HERE",
      "match_score": 0.0 to 1.0,
      "reasons": ["..."],
      "trade_offs": ["..."],
      "relevant_demonstrated_signals": ["..."],
      "irrelevant_or_unsupported_signals": ["..."]
    }}
  ],
  "key_assumptions": ["..."],
  "uncertainty_assessment": "...",
  "refinement_questions": [
    {{
      "question": "...",
      "potential_answers_impact": {{
        "if_answer_A": "Impact on rank 1 vs 2",
        "if_answer_B": "Impact on rank 1 vs 2"
      }}
    }}
  ]
}}
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You output strictly valid JSON with no markdown backticks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)
        return HirerRecommendation(**data)