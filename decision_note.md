# Decision Note: Artist Intelligence & Recommendation System

## 1. Decision Supported

This system supports creative marketplace operations by converting sparse, unstructured hirer requests into evidence-backed artist matches. It assists marketplace coordinators in identifying suitable artists based solely on verified capabilities rather than self-reported claims.

## 2. First-Version Scope & Non-Goals

* **In-Scope:**
  * Schema-based extraction of claimed vs. demonstrated capabilities across 15 profiles (5 photographers, 5 musicians, 5 video editors).
  * Explicit citation of source files and timestamps for observable capabilities.
  * Interpretation of incomplete briefs into constraints, assumptions, and critical unknowns.
  * Ranked top-2 recommendations per brief with trade-offs and up to 2 refinement questions.
  * Re-ranking pipeline upon arrival of new context.
* **Non-Goals (Out of Scope):**
  * Inference of subjective trust signals (reliability, punctuality, character, popularity).
  * Web scraping, real-time client deployment, or fine-tuning models.
  * Brute-force frame-by-frame video processing.

## 3. Capability Dimensions per Category

* **Photographers:** Lighting control (natural vs. studio strobes), environment (field/outdoor vs. studio), subject specialism (product, portraiture, architectural), and color grading profile.
* **Musicians:** Primary genre, instrument arrangement, structural tempo/rhythm range, and acoustic recording vs. electronic production fidelity.
* **Video Editors:** Cutting pace and rhythm, visual effects/compositing, narrative montage flow, and multi-track audio/dialogue synchronization.

## 4. Main Assumptions & Risks

* **Assumption:** Technical file metadata (bitrates, frame keypoints, resolutions) reliably indicates technical execution capability even when sample lengths are constrained.
* **Risk:** Extremely sparse or damaged profiles may produce lower-confidence matches; the system mitigates this by flagging confidence scores and explicit unknowns rather than hallucinating capabilities.
