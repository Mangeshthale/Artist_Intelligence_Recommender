import json
from typing import List, Dict, Any
from groq import Groq
from src.schemas import ArtistIntelligenceRecord, HirerRecommendation, UpdatedRecommendation

class FollowupUpdater:
    def __init__(self, groq_client: Groq, model: str = "openai/gpt-oss-120b"):
        self.client = groq_client
        self.model = model

    def _compress_artist_record(self, artist: ArtistIntelligenceRecord) -> Dict[str, Any]:
        return {
            "artist_id": artist.artist_id,
            "category": artist.category,
            "demonstrated_capabilities": artist.demonstrated_capabilities,
            "category_dimensions": artist.category_dimensions,
            "evidence_signals": [
                f"{e.source_file}: {e.demonstrated_signal}" 
                for e in artist.evidence[:4]
            ]
        }

    def process_update(
        self,
        initial_recommendation: HirerRecommendation,
        followup_text: str,
        artists: List[ArtistIntelligenceRecord]
    ) -> UpdatedRecommendation:
        compressed_artists = [self._compress_artist_record(a) for a in artists]

        prompt = f"""
A hirer has provided follow-up information for brief '{initial_recommendation.brief_id}'.
Re-rank the individual artists using this new context and explain what changed and why.

Initial Brief ID: {initial_recommendation.brief_id}
Initial Top Ranking: {[a.artist_id for a in initial_recommendation.top_artists]}
Follow-up Context:
\"\"\"{followup_text}\"\"\"

Artists Intelligence:
{json.dumps(compressed_artists, indent=2)}

Output strict JSON matching this schema:
{{
  "brief_id": "{initial_recommendation.brief_id}",
  "follow_up_context": "{followup_text.strip()}",
  "previous_ranking": {[a.artist_id for a in initial_recommendation.top_artists]},
  "updated_ranking": [
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
  "ranking_change_explanation": "Clear explanation of what shifted, why candidate A overtook candidate B or remained stable based on newly resolved constraints."
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
        return UpdatedRecommendation(**data)