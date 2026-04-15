# AI-Powered Workflow Automator

An intelligent file organization tool designed to transform unstructured visual data (screenshots and mobile photos) into a searchable, categorized asset library using Multimodal AI.

## The Solution
This tool leverages the **Google Gemini 3.1 Flash API** to "see" images and generate descriptive, context-aware filenames. It eliminates the manual overhead of organizing hundreds of generic filenames like `Screenshot_2026...` or `IMG_9421.HEIC`.

## Technical Stack
* **Language:** Python 3.14
* **AI Model:** Gemini 3.1 Flash (Multimodal)
* **Libraries:** `google-genai`, `Pillow`, `pillow-heif`, `python-dotenv`
* **Storage Integration:** Local file system / Cloud-synced directories (Dropbox/OneDrive)

## Key Features
* **Multimodal Analysis:** Identifies mechanical parts, document types, and UI elements.
* **Apple Ecosystem Support:** Native handling of `.HEIC` formats from iPhone AirDrops.
* **Security:** Environment-based configuration (Zero hardcoded API keys).
* **Resilience:** Built-in error handling for API rate limits and file duplicates.

## Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your `GEMINI_API_KEY` and `DROPBOX_PATH`.
4. Run: `python renamer.py`