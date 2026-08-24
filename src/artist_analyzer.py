import os
import json
from groq import Groq
from src.schemas import ArtistIntelligenceRecord
from src.media_processor import MediaProcessor

class ArtistAnalyzer:
    def __init__(self, groq_client: Groq, model: str = "openai/gpt-oss-120b"):
        self.client = groq_client
        self.model = model

    def analyze_artist_folder(self, artist_folder_path: str) -> ArtistIntelligenceRecord:
        artist_id = os.path.basename(artist_folder_path)
        
        # 1. Read Profile Text
        profile_text = ""
        for f in os.listdir(artist_folder_path):
            if f.endswith(".txt") or f.endswith(".md"):
                with open(os.path.join(artist_folder_path, f), "r", encoding="utf-8", errors="ignore") as file:
                    profile_text += file.read() + "\n"

        # 2. Inspect Media Files & Gather Selective Signals
        media_inventory = []
        for root, _, files in os.walk(artist_folder_path):
            for file in files:
                ext = file.lower().split(".")[-1]
                fpath = os.path.join(root, file)
                rel_path = os.path.relpath(fpath, artist_folder_path)
                
                if ext in ["jpg", "jpeg", "png", "webp"]:
                    media_inventory.append(f"Image: {rel_path}")
                elif ext in ["mp3", "wav", "aac"]:
                    meta = MediaProcessor.extract_audio_metadata(fpath)
                    media_inventory.append(f"Audio: {rel_path} | Metadata: {meta}")
                elif ext in ["mp4", "mov", "mkv"]:
                    keyframes = MediaProcessor.sample_video_keyframes(fpath, num_samples=2)
                    media_inventory.append(f"Video: {rel_path} | Sampled at: {[k['timestamp'] for k in keyframes]}")

        # 3. LLM Extraction Prompt
        prompt = f"""
You are an expert capability auditor for a creative marketplace.
Analyze the following artist profile and media evidence.

STRICT RULES:
1. Separate 'claimed_capabilities' (what profile says) from 'demonstrated_capabilities' (what portfolio media actually proves).
2. Never infer trust signals (character, punctuality, reliability, popularity).
3. Distinguish category-specific dimensions:
   - Photographers: lighting style, studio vs field, color grading, subject focus (portraits, product, event).
   - Musicians: genre, instrumentation, tempo range, production/mixing fidelity.
   - Video Editors: pacing/rhythm, VFX/color grading, montage/narrative style, sound sync.
4. Always cite specific files or timestamps for evidence. If media is missing or damaged, mark confidence lower and list it under unknowns.

Artist ID: {artist_id}
Profile Content:
{profile_text if profile_text.strip() else '[NO PROFILE TEXT PROVIDED / DAMAGED]'}

Media Inventory & Technical Metadata:
{chr(10).join(media_inventory) if media_inventory else '[NO MEDIA FILES FOUND]'}

Output strict JSON matching this schema:
{{
  "artist_id": "{artist_id}",
  "category": "photographer" | "musician" | "video_editor",
  "claimed_capabilities": ["..."],
  "demonstrated_capabilities": ["..."],
  "category_dimensions": {{ ... }},
  "evidence": [
    {{
      "source_file": "...",
      "identifier_or_timestamp": "...",
      "demonstrated_signal": "...",
      "confidence": 0.0 to 1.0
    }}
  ],
  "unknowns_and_limitations": ["..."],
  "overall_confidence": 0.0 to 1.0,
  "confidence_rationale": "..."
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
        return ArtistIntelligenceRecord(**data)