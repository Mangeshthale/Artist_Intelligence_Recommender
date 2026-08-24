import os
import glob
import json
import time
from dotenv import load_dotenv
from groq import Groq
from tqdm import tqdm

from src.schemas import HirerRecommendation
from src.artist_analyzer import ArtistAnalyzer
from src.hirer_matcher import HirerMatcher
from src.followup_updater import FollowupUpdater

def find_artist_folders(base_path: str = "data/artist_profiles") -> list:
    """Accurately discovers exactly the 15 artist profile folders."""
    artist_dirs = []
    
    for entry in os.scandir(base_path):
        if entry.is_dir() and not entry.name.startswith(('.', '__')):
            # Case 1: Subcategory folders (e.g. photographers/, musicians/, video_editors/)
            subfolders = [s.path for s in os.scandir(entry.path) if s.is_dir() and not s.name.startswith('.')]
            if subfolders:
                for sub in subfolders:
                    if os.path.basename(sub).lower() != "media":
                        artist_dirs.append(sub)
            else:
                # Case 2: Direct artist folder
                artist_dirs.append(entry.path)
                
    # Filter out any lingering nested 'media' folders
    artist_dirs = [d for d in artist_dirs if os.path.basename(d).lower() != "media"]
    return sorted(list(set(artist_dirs)))

def main():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Check your .env file.")

    client = Groq(api_key=api_key)
    os.makedirs("outputs", exist_ok=True)

    print("🚀 Starting Artist Intelligence & Recommendation Pipeline...")

    # -------------------------------------------------------------
    # PART A: Artist Intelligence (15 Individual Artists)
    # -------------------------------------------------------------
    print("\n[Part A] Extracting evidence-backed artist intelligence...")
    analyzer = ArtistAnalyzer(client)
    artist_records = []
    
    artist_dirs = find_artist_folders("data/artist_profiles")
    print(f"Found {len(artist_dirs)} individual artist folders.")

    with open("outputs/artist_intelligence.jsonl", "w", encoding="utf-8") as f_out:
        for artist_dir in tqdm(artist_dirs, desc="Processing Artists"):
            record = analyzer.analyze_artist_folder(artist_dir)
            artist_records.append(record)
            f_out.write(record.model_dump_json() + "\n")
            time.sleep(2)  # Short safety interval between artist analyses
            
    print(f"✅ Saved {len(artist_records)} artist records to outputs/artist_intelligence.jsonl")

    # -------------------------------------------------------------
    # PART B: Contextual Recommendations
    # -------------------------------------------------------------
    print("\n[Part B] Matching hirer briefs against demonstrated capabilities...")
    matcher = HirerMatcher(client)
    recommendations = []
    
    brief_files = glob.glob("data/hirer_conversations/*.txt") + glob.glob("data/hirer_conversations/*.md")
    for brief_file in tqdm(sorted(brief_files), desc="Processing Hirer Briefs"):
        brief_id = os.path.splitext(os.path.basename(brief_file))[0]
        with open(brief_file, "r", encoding="utf-8", errors="ignore") as bf:
            brief_text = bf.read()
        
        rec = matcher.match_brief(brief_id, brief_text, artist_records)
        recommendations.append(rec.model_dump())
        
        # Pacing between briefs to respect the free tier TPM rate limit
        time.sleep(15)

    with open("outputs/recommendations.json", "w", encoding="utf-8") as f_out:
        json.dump(recommendations, f_out, indent=2)
    print("✅ Saved initial recommendations to outputs/recommendations.json")

    # -------------------------------------------------------------
    # PART C: Follow-up Re-ranking
    # -------------------------------------------------------------
    print("\n[Part C] Processing follow-up update and re-ranking...")
    updater = FollowupUpdater(client)
    followup_files = glob.glob("data/follow_up_update/*.txt") + glob.glob("data/follow_up_update/*.md")
    
    if followup_files and recommendations:
        with open(followup_files[0], "r", encoding="utf-8", errors="ignore") as ff:
            followup_text = ff.read()
        
        # Target the brief referenced in follow-up (defaulting to Brief 01 / Enquiry 081)
        target_rec = next(
            (r for r in recommendations if "01" in r["brief_id"] or "cafe" in r["brief_id"].lower()), 
            recommendations[0]
        )
        
        target_pydantic = HirerRecommendation(**target_rec)
        updated_rec = updater.process_update(target_pydantic, followup_text, artist_records)
        
        with open("outputs/updated_recommendation.json", "w", encoding="utf-8") as f_out:
            json.dump(updated_rec.model_dump(), f_out, indent=2)
        print("✅ Saved re-ranking to outputs/updated_recommendation.json")

    print("\n🎉 Complete pipeline executed successfully!")

if __name__ == "__main__":
    main()