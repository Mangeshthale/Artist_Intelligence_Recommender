# Evidence-Led Artist Intelligence & Recommendation Engine

## 1. Approach

The goal of this system is to evaluate fictional creative marketplace artists (photographers, musicians, video editors) based exclusively on demonstrated evidence rather than self-reported claims, and to match them intelligently to incomplete hirer briefs.

To achieve this within strict processing constraints, the architecture leverages:

* **Decoupled Extraction & Matching:** A two-phase pipeline where Phase 1 extracts objective evidence from media into structured JSON records, and Phase 2 evaluates hirer intent against those records using Large Language Models (LLMs).
* **Compression & Token Optimization:** A localized filtering function strips extraneous text (e.g., verbose rationales) before feeding candidate profiles into the recommendation prompt, avoiding token limit exceedances (e.g., 8000 TPM limit).
* **Defensible Uncertainty:** Instead of hallucinating missing details from damaged profiles, the system assigns strict confidence scores and flags "unknowns," enabling human operators to formulate targeted refinement questions.

## 2. Setup & Execution

### Prerequisites

* Python 3.10+
* VS Code (recommended)
* A free Groq API key (`openai/gpt-oss-120b` endpoint)

### Installation

1. Clone the repository and navigate into the project directory:

   ```bash
   git clone <repository_url>
   cd artist-intelligence-recommender
   ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your environment variables by copying the example file:

    ```bash
    cp .env.example .env
    # Open .env and add your GROQ_API_KEY
    ```

### Execution

Run the main pipeline script. The script incorporates built-in rate-limiting delays to respect free-tier API caps:

 ```bash
python main.py
```

## 3. Media Selection Strategy

Blindly processing every frame of a video or second of audio is computationally expensive and slow. This pipeline employs a Selective Media Inspection strategy:

**Video Processing:** Uses OpenCV to sample distributed keyframes across the video duration instead of continuous frame decoding. This captures pacing, color grading shifts, and montage narrative without the heavy overhead.

**Audio Processing:** Utilizes mutagen to extract structural metadata (bitrate, sample rate, channels, duration). High-fidelity capabilities are inferred from technical metadata (e.g., 705.6 kbps WAV vs. compressed MP3) combined with filename heuristics, avoiding complex audio ML dependencies.

**Image Processing:** Images are downscaled to 512x512 thumbnails and encoded in Base64 using Pillow to conserve context windows when evaluated.

## 4. Implemented Choices

**Model Selection:** Utilized Groq's openai/gpt-oss-120b for heavy reasoning, conversational intent mapping, and JSON formatting reliability.

**Pydantic Schemas:** Used strictly enforced Pydantic models for JSON generation to ensure consistent output formatting, leveraging Optional fields and default values to prevent pipeline crashes when the LLM encounters missing data (e.g., damaged profiles).

**Directory Traversal Logic:** Implemented a robust traversal mechanism to accurately isolate individual artist folders (e.g., M01_Meera_Arjun) while ignoring categorization wrappers or nested media folders.

## 5. Evaluation

The system was evaluated against the synthetic dataset based on its ability to handle ambiguity:

**Artist Profiles:** Successfully distinguished between file naming conventions and actual metadata, correctly identifying the absence of claimed capabilities in damaged text files. Confidence scores accurately reflect the sparsity of evidence (often dropping to ~0.35 when only file names are present).

**Hirer Briefs:** The recommendation engine accurately matched constraints (e.g., acoustic setup vs. electronic) and dynamically adjusted rankings when follow-up context explicitly changed the event type (from background music to a 45-minute headline set).

## 6. Limitations

**Metadata Reliance:** For corrupted files, the system heavily relies on filename semantics and technical metadata. If an artist inaccurately names a file, the system may extract false positive dimensions.

**Nuanced Pacing Extraction:** While video keyframing captures broad color and scene shifts, it cannot effectively evaluate continuous narrative flow or precise audio-to-video beat synchronization, relying on LLM inferences from sparse keypoints.

**Visual Content Blindspots:** Due to API modality limits, image files are occasionally evaluated based on filenames rather than deep pixel-level aesthetic analysis, which reduces confidence in nuanced style matching (e.g., "clean premium look").
