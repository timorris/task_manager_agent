import os
import re
import json
from pathlib import Path
from typing import List, Optional

import requests


def load_env_file(filepath: str = ".env") -> None:
    """
    Minimal .env loader to avoid external dependencies.
    Reads lines of the form KEY=VALUE and sets them in os.environ if not already set.
    Lines beginning with '#' are treated as comments. Empty lines are ignored.
    """
    env_path = Path(filepath)
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        # Trim optional surrounding quotes for value
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_todoist_api_key() -> Optional[str]:
    load_env_file()  # Non-intrusive: only sets values if not present in env
    return os.getenv("TODOIST_API_KEY")


def parse_tasks_from_text(text: str) -> List[str]:
    """
    A small, deterministic parser that:
    - Tries to capture the portion after 'to ' if present (common phrasing like 'add a new task to ...').
    - Splits by ', and', ' and ', ',', handling common natural phrasing.
    - Trims trailing punctuation and whitespace.
    """
    if not text:
        return []

    # Focus on text after the first ' to ' if present
    lower = text.lower()
    idx = lower.find(" to ")
    segment = text[idx + 4 :] if idx != -1 else text

    # Normalize separators: turn ' and ' into comma for simple splitting
    segment = re.sub(r"\s+and\s+", ",", segment, flags=re.IGNORECASE)
    parts = [p.strip(" .") for p in segment.split(",")]

    # Remove empty parts and keep original casing as much as possible
    tasks = [p for p in parts if p]
    return tasks


def add_task_todoist(api_key: str, content: str) -> requests.Response:
    """
    Creates a Todoist task via REST API.
    Returns the Response object. Raises for HTTP errors.
    """
    url = "https://api.todoist.com/rest/v2/tasks"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Request-Id": os.urandom(16).hex(),
    }
    payload = {"content": content}
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
    # Raise an error if status is not 2xx to surface issues clearly
    resp.raise_for_status()
    return resp


def main() -> None:
    # Original user intent string
    user_prompt = "add a new task to buy dinner for tonight, and dog food for the week."

    api_key = get_todoist_api_key()
    if not api_key:
        print(
            "ERROR: TODOIST_API_KEY is not set. Please set it in your environment or in a .env file."
        )
        return

    tasks = parse_tasks_from_text(user_prompt)
    if not tasks:
        print("No tasks detected from input. Nothing to add.")
        return

    created = []
    errors = []

    for task in tasks:
        try:
            resp = add_task_todoist(api_key, task)
            created.append(task)
        except requests.HTTPError as http_err:
            # Include more detail for debugging, but not overwhelming
            errors.append(f"{task} -> HTTP {resp.status_code if 'resp' in locals() else '??'}: {http_err}")
        except Exception as ex:
            errors.append(f"{task} -> {type(ex).__name__}: {ex}")

    if created:
        print("Successfully added tasks:")
        for t in created:
            print(f"- {t}")
    if errors:
        print("\nSome tasks could not be added:")
        for e in errors:
            print(f"- {e}")


if __name__ == "__main__":
    main()
