# AI Tool Usage and Verification Log

## Tools Used

* **LLM Engine:** Groq API (`gpt-oss-120b`) for structured JSON extraction and conversational intent reasoning.
* **Assistance:** AI coding assistant for boilerplate structuring, schema definition, and markdown templates.

## Generated vs. Verified Components

* **Code Architecture:** Generated base Pydantic schemas and pipeline runner; verified metadata extraction and exception handling on corrupted files manually.
* **Extraction Quality:** Verified that capability citations link directly to file paths and timestamps, filtering out any hallucinated claims.
* **Matching Logic:** Reviewed the generated top-2 recommendations to confirm ranking decisions were driven exclusively by demonstrated evidence rather than profile claims.
