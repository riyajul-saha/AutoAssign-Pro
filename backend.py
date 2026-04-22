"""
============================================================
  backend.py — AutoAssign Pro Backend Module
============================================================
  Handles all non-UI logic:
    • Loading the API key from the .env file
    • Building AI prompts (Case 1: raw questions, Case 2: topic-only)
    • Calling the OpenRouter API (model: openai/gpt-oss-120b:free)
    • Cleaning markdown backticks from AI responses
    • Parsing JSON and saving to current_assignment.json
============================================================
"""

import json
import re
import os
import urllib.request
import urllib.error


# ──────────────────────────────────────────────────────────
#  Constants
# ──────────────────────────────────────────────────────────

# OpenRouter endpoint for chat completions
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# The free model we use for generation
MODEL_NAME = "openai/gpt-oss-120b:free"

# Output file where parsed assignment JSON is saved
OUTPUT_FILE = "current_assignment.json"

# Path to the environment file containing the API key
ENV_FILE = ".env"


# ──────────────────────────────────────────────────────────
#  API Key Loader
# ──────────────────────────────────────────────────────────

def load_api_key() -> str | None:
    """
    Read the OPEN_ROUTER_API key from the .env file.

    Returns:
        The API key string if found, otherwise None.
    """
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                # Look for the exact key name
                if line.strip().startswith("OPEN_ROUTER_API="):
                    return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        pass  # .env file doesn't exist
    except Exception:
        pass  # Any other read error

    return None


# ──────────────────────────────────────────────────────────
#  Prompt Builders
# ──────────────────────────────────────────────────────────

def build_prompt_from_questions(user_questions: str, num_questions: int) -> str:
    """
    Case 1 — User provided raw questions.
    Build a prompt asking the AI to structure them into JSON.

    Args:
        user_questions: Raw question text entered by the user.
        num_questions: Target number of questions to format.

    Returns:
        The formatted prompt string.
    """
    return (
        f'Here is a raw list of assignment questions: "{user_questions}". \n'
        f'First, verify that the text above actually contains valid assignment '
        f'questions or academic tasks. If the text is random gibberish, '
        f'greetings, unrelated sentences, code snippets that are not questions, '
        f'or anything that is NOT a legitimate question or set of questions, '
        f'respond with EXACTLY the single word: INVALID_INPUT\n'
        f'Otherwise, format them into a valid JSON object of (if possible) {num_questions} questions. Return ONLY the raw JSON '
        f'without any markdown or extra text. Use this exact structure:\n'
        f'{{"assignment_title": "Custom Assignment", "questions": '
        f'[{{"id": 1, "task": "..."}}]}}'
    )


def build_prompt_from_topic(topic_name: str, description: str, num_questions: int) -> str:
    """
    Case 2 — User provided only a topic (no questions).
    Build a prompt asking the AI to generate assignment questions.

    Args:
        topic_name: The assignment topic entered by the user.
        description: Specific field or details for the topic.
        num_questions: Number of questions to generate.

    Returns:
        The formatted prompt string.
    """
    prompt = f'Act as a computer science professor. Generate {num_questions} practical and most valuable programming assignment questions on the topic: "{topic_name}". Do not give very hard question, keep question easy and Mediun '
    
    if description and description.strip().lower() != "basic":
        prompt += f'Specifically, focus these questions on the specific field or concept of: "{description}". '

    prompt += (
        f'\nFirst, verify that "{topic_name}" is a legitimate academic topic, '
        f'subject, or field of study. If it is random gibberish, greetings, '
        f'unrelated nonsense, emoji-only text, or anything that is NOT a '
        f'valid topic, respond with EXACTLY the single word: INVALID_INPUT\n'
        f'Otherwise, return ONLY a raw, valid JSON object without any markdown '
        f'formatting or extra text. Use this exact structure:\n'
        f'{{"assignment_title": "{topic_name}", "questions": '
        f'[{{"id": 1, "task": "..."}}]}}'
    )
    return prompt


# ──────────────────────────────────────────────────────────
#  OpenRouter API Caller
# ──────────────────────────────────────────────────────────

def call_openrouter(api_key: str, prompt: str) -> str:
    """
    Send the prompt to the OpenRouter API and return the raw
    text content from the AI response.

    Args:
        api_key: Bearer token for OpenRouter.
        prompt:  The full prompt string to send.

    Returns:
        Raw text content from the AI's response.

    Raises:
        urllib.error.URLError: On network / HTTP errors.
        KeyError / IndexError:  If the response shape is unexpected.
    """
    # Build the JSON request body
    req_body = json.dumps({
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }).encode("utf-8")

    # Create the HTTP request with required headers
    req = urllib.request.Request(API_URL, data=req_body)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("HTTP-Referer", "http://localhost")  # Required by some OR models
    req.add_header("X-Title", "AutoAssign Pro")

    # Execute the request (45-second timeout)
    with urllib.request.urlopen(req, timeout=45) as response:
        resp_data = json.loads(response.read().decode())

    # Extract the AI's message content
    return resp_data["choices"][0]["message"]["content"]


# ──────────────────────────────────────────────────────────
#  Response Cleaner (Markdown Backtick Remover)
# ──────────────────────────────────────────────────────────

def clean_ai_response(raw_text: str) -> str:
    """
    Strip markdown code-fence backticks that the AI sometimes
    wraps around JSON output.

    Example input the AI might return:
        ```json
        {"assignment_title": "...", ...}
        ```

    This function removes the surrounding ``` markers so the
    raw JSON can be parsed safely.

    Args:
        raw_text: The raw string returned by the AI.

    Returns:
        Cleaned string with backticks removed.
    """
    cleaned = raw_text.strip()

    # Remove opening ```json or ``` block
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)

    # Remove closing ``` block
    if cleaned.endswith("```"):
        cleaned = re.sub(r"\s*```$", "", cleaned)

    return cleaned.strip()


# ──────────────────────────────────────────────────────────
#  JSON Parser & File Saver
# ──────────────────────────────────────────────────────────

def parse_and_save(raw_text: str) -> dict:
    """
    Clean the AI response, parse it as JSON, and write the
    result to current_assignment.json.

    Args:
        raw_text: Raw AI response string (may contain backticks).

    Returns:
        The parsed JSON as a Python dictionary.

    Raises:
        json.JSONDecodeError: If the cleaned text is not valid JSON.
    """
    # Step 1 — Remove any markdown backticks
    cleaned = clean_ai_response(raw_text)

    # Step 2 — Parse the cleaned string into a Python dict
    parsed_json = json.loads(cleaned)

    # Step 3 — Write to the output file with pretty formatting
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(parsed_json, f, indent=4)

    return parsed_json


# ──────────────────────────────────────────────────────────
#  High-Level Orchestrator  (called by the UI thread)
# ──────────────────────────────────────────────────────────

def generate_assignment(topic: str, questions: str, description: str = "Basic", num_questions: int = 5, log_callback=None):
    """
    Main entry point for the backend pipeline.

    Decides which prompt to use (Case 1 vs Case 2), calls the AI,
    cleans the response, and saves the JSON file.

    Args:
        topic:         The topic string (may be empty).
        questions:     The raw questions string (may be empty).
        description:   Specific field to narrow down the topic.
        num_questions: Target number of questions to generate.
        log_callback:  Optional callable(str) for real-time log messages.

    Returns:
        dict with keys:
            "success" (bool)  — whether the generation succeeded
            "message" (str)   — human-readable result / error description
            "data"    (dict)  — parsed JSON data (only if success=True)
    """
    def log(msg):
        """Helper to safely invoke the log callback."""
        if log_callback:
            log_callback(msg)

    # ── Step 1: Load the API key ─────────────────────────
    log("Initializing generation...")
    api_key = load_api_key()

    if not api_key:
        log("❌ OPEN_ROUTER_API key missing in .env file.")
        return {"success": False, "message": "API key not found in .env file.", "data": None}

    # ── Step 2: Build the correct prompt ─────────────────
    log("Preparing AI payload...")

    if questions:
        # Case 1 — User gave raw questions → ask AI to structure them
        log(f"Mode: Structuring {num_questions} raw questions (Case 1)")
        prompt = build_prompt_from_questions(questions, num_questions)
    else:
        # Case 2 — User gave only a topic → ask AI to generate questions
        desc_log = f" with focus on '{description}'" if description.lower() != "basic" else ""
        log(f"Mode: Generating {num_questions} questions for topic '{topic}'{desc_log} (Case 2)")
        prompt = build_prompt_from_topic(topic, description, num_questions)

    # ── Step 3: Call the OpenRouter API ──────────────────
    log(f"Connecting to OpenRouter ({MODEL_NAME})...")

    try:
        raw_text = call_openrouter(api_key, prompt)
    except urllib.error.URLError as e:
        error_msg = f"API connection error: {e.reason}"
        log(f"❌ {error_msg}")
        return {"success": False, "message": error_msg, "data": None}
    except Exception as e:
        error_msg = f"Unexpected API error: {str(e)}"
        log(f"❌ {error_msg}")
        return {"success": False, "message": error_msg, "data": None}

    # ── Step 4: Check for invalid input sentinel ────────
    cleaned_response = clean_ai_response(raw_text).strip()
    if cleaned_response.upper() == "INVALID_INPUT" or "INVALID_INPUT" in cleaned_response.upper().split():
        log("⚠️ AI detected the input is not a valid topic or question.")
        return {
            "success": False,
            "message": "INVALID_INPUT",
            "data": None,
        }

    # ── Step 5: Parse response & save JSON ───────────────
    log("Parsing AI response...")

    try:
        parsed_data = parse_and_save(raw_text)
    except json.JSONDecodeError:
        log("❌ AI returned invalid JSON. Could not parse.")
        return {"success": False, "message": "AI returned invalid JSON.", "data": None}

    # ── Step 6: Done! ────────────────────────────────────
    log(f"Saving to {OUTPUT_FILE}...")
    log("✅ Assignment saved successfully!")

    return {"success": True, "message": "Assignment generated.", "data": parsed_data}
