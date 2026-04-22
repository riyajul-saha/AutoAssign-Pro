import json
import os
import subprocess
import threading
import urllib.request
import urllib.error
import re
from PIL import ImageGrab

# OpenRouter endpoint for chat completions
API_URL = "https://openrouter.ai/api/v1/chat/completions"
# The free model we use for generation
MODEL_NAME = "arcee-ai/trinity-large-preview:free"
ENV_FILE = ".env"

def load_api_key() -> str | None:
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("OPEN_ROUTER_API="):
                    return line.strip().split("=", 1)[1]
    except:
        pass
    return None

def clean_ai_response(raw_text: str) -> str:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    if cleaned.endswith("```"):
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()

def call_openrouter(api_key: str, prompt: str) -> str:
    req_body = json.dumps({
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    req = urllib.request.Request(API_URL, data=req_body)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("HTTP-Referer", "http://localhost")
    req.add_header("X-Title", "AutoAssign Pro")
    with urllib.request.urlopen(req, timeout=120) as response:
        resp_data = json.loads(response.read().decode())
    return resp_data["choices"][0]["message"]["content"]

def solve_question(task: str, language: str, error_context: str = "") -> dict:
    api_key = load_api_key()
    if not api_key:
        return {"error": "API key missing"}

    prompt = (
        f"Solve the following assignment question in {language}: '{task}'.\n"
    )
    if error_context:
        prompt += f"The previous code failed with this error:\n{error_context}\nPlease fix the code.\n"
        
    prompt += (
        f"Return ONLY a valid JSON object with the following structure. Do not include markdown code blocks around the JSON.\n"
        f"{{\n"
        f"  \"code\": \"<the source code>\",\n"
        f"  \"dependencies\": [\"<list of command strings to install dependencies if any>\"],\n"
        f"  \"demo_input\": [\"<list of inputs to provide one by one if the program asks for user input>\"]\n"
        f"}}\n"
    )
    
    try:
        raw_text = call_openrouter(api_key, prompt)
        cleaned = clean_ai_response(raw_text)
        data = json.loads(cleaned)
        return data
    except Exception as e:
        return {"error": str(e), "raw": raw_text if 'raw_text' in locals() else ""}

def check_compiler(language: str):
    try:
        with open("languages.json", "r") as f:
            langs = json.load(f)
            
        for lang in langs.get("languages", []):
            if lang["name"].lower() == language.lower():
                check_cmd = lang.get("check_command", "")
                if not check_cmd:
                    return True, lang
                try:
                    result = subprocess.run(check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
                    if result.returncode == 0:
                        # Success
                        lang["status"] = 1
                        with open("languages.json", "w") as out:
                            json.dump(langs, out, indent=4)
                        return True, lang
                    else:
                        return False, lang
                except:
                    return False, lang
    except Exception as e:
        print("Error checking compiler:", e)
        return False, None
    return False, None
