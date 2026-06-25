## Functional Requirements
- Ingest uploaded documents (predominantly PDFs) and extract structured data via LLM calls routed through AWS Bedrock.
- Accept a small set of user-entered decisions in the desktop UI that, together with the extracted data, drive narrative generation.
- Generate a narrative draft from the extracted data and user decisions using LLM calls whose prompt content and behavior are loaded from plain text prompt files and JSON config files (no code change required to update behavior).
- Provide an in-app review/edit surface for the user to revise the generated narrative before export.
- Export the finalized narrative as a Microsoft Word document produced from a pre-written template (python-docx).
- Allow the application owner (a non-developer) to update what the app displays, how it processes data, and what it sends to the LLM by editing JSON config and prompt text files only.
- Operate as a downloadable desktop application (not a web service) that other psychologists can install and run locally, with end users only paying API fees.

## Non-Functional Requirements
- All processing that involves student/psychological records must keep data confined to the user's local machine plus the chosen LLM API; no undocumented third-party storage of clinical content.
- Configuration-driven extensibility: the owner must be able to modify prompts, data extraction logic, UI labels, and templates by editing JSON/text files, without code changes or recompilation.
- Maintainable as a phased build starting with the core extraction → narrative → export pipeline before feature expansion.
- Reliability of the extraction + narrative quality should match the existing Claude-based workflow that "reliably pulls the data … and writes a high-quality narrative" — that workflow is the quality bar.
- Distribution model is free for end users; the application must be straightforward to install and run on a school psychologist's computer.
- A developer must be able to follow a detailed pre-written blueprint (architecture, data flow, feature specs, developer notes) to build the system, with feedback channel for design input.

## Constraints
- Tech stack (required): Python, Qt via PySide6, desktop application framework.
- Tech stack (required): LLM access via AWS Bedrock (boto3 acceptable).
- Tech stack (required for data and output): PDF processing libraries and python-docx for Word generation.
- Must respect the owner's existing blueprint (architecture, data flow, feature specifications, developer notes) rather than redesign from scratch.
- All application behavior — UI content, data processing rules, prompts sent to the LLM — must be driven by JSON config files and plain text prompt files.
- Existing assets that must integrate with the build: the owner's AI prompts, supporting text files, the pre-written Word template, and the tested Claude extraction approach.
- Project will be phased; the first phase is the core pipeline (PDF → extraction → narrative → review → Word export).
- The owner is a non-developer collaborator, so the codebase must be readable enough that future content/behavior changes happen via config edits, not code edits.
- Collaboration style is iterative; the developer is expected to flag implementation alternatives when they see a better approach, but not to override the blueprint unilaterally.

## Success Criteria
- A school psychologist can install the packaged desktop app, configure their AWS Bedrock credentials, and complete a full report (upload PDFs → enter decisions → review narrative → export Word) without running any code.
- Uploading the same PDF set the owner has validated in Claude produces extracted data and a narrative of comparable quality to the existing Claude-based workflow.
- Changing the LLM prompt that controls data extraction requires only editing a text/prompt file and restarting the app — no Python code changes.
- The exported `.docx` opens cleanly in Microsoft Word and is populated from the pre-written template with the reviewed narrative content in the correct location.
- End users can use the application without ever paying anything beyond their own AWS Bedrock API usage fees; the app itself is free.
- The owner can update the JSON config files to change UI display, processing flow, or LLM payloads without engaging a developer.

## Out of Scope (initial)
- Built-in billing, subscription, or license management for end users (the app is given away for free; users pay only their own API fees).
- A web-hosted or SaaS version of the tool — this is a downloadable desktop application only.
- A custom LLM training or fine-tuning pipeline; the system calls existing models via AWS Bedrock.
- Non-PDF input formats (scanned images, handwriting OCR, audio, etc.) unless later added — the job specifies "mostly PDFs."
- Automatic generation of the prompts, template, or blueprint itself — these are authored and owned by the school psychologist.
- End-user analytics, telemetry, account management, or cloud sync of clinical data.
- Mobile, tablet, or cross-platform GUI variants beyond the PySide6 desktop target.
- Any feature beyond the core extraction → narrative → review → Word export pipeline in phase 1; later-phase features (advanced editing, batch processing, multi-template support, etc.) are deferred.