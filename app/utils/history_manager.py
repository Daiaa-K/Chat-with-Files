import os
import json
from config.settings import settings
from utils.logger import logger

# History directory
HISTORY_DIR =settings.HISTORY_DIR
os.makedirs(HISTORY_DIR, exist_ok=True)

# Maximum number of sessions to keep
MAX_SESSIONS = 10


def _get_history_file(session_id: str) -> str:
    """Return path to session history file."""
    return os.path.join(HISTORY_DIR, f"{session_id}.json")


def save_history(session_id: str, question: str, answer: str):
    """
    Append a new Q/A turn to the session history file.
    If sessions exceed MAX_SESSIONS, delete oldest.
    """
    history_file = _get_history_file(session_id)
    record = []

    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                record = json.load(f)
                logger.info(f"Loaded existing history for session {session_id}, {len(record)//2} turns.")
        except Exception:
            record = []
            logger.info("starting new session history due to error loading existing file.")

    # Append new Q/A
    record.append({"role": "human", "content": question})
    record.append({"role": "ai", "content": answer})

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved history for session {session_id}, total {len(record)//2} turns.")   

    # Enforce session limit
    _enforce_session_limit()


def load_history(session_id: str):
    """
    Load a session's history as a list of dicts.
    Returns [] if no history exists.
    """
    history_file = _get_history_file(session_id)
    if not os.path.exists(history_file):
        return []

    try:
        with open(history_file, "r", encoding="utf-8") as f:
            logger.info(f"Loaded history for session {session_id}")
            return json.load(f)
    except Exception:
        return []


def delete_history(session_id: str):
    """
    Delete a session's history file.
    """
    history_file = _get_history_file(session_id)
    if os.path.exists(history_file):
        os.remove(history_file)
        logger.info(f"Deleted history for session {session_id}.")


def _enforce_session_limit():
    """
    Keep only the last MAX_SESSIONS history files.
    Deletes oldest by file modified time.
    """
    files = [os.path.join(HISTORY_DIR, f) for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    if len(files) <= MAX_SESSIONS:
        return

    # Sort by modification time (oldest first)
    files.sort(key=os.path.getmtime)

    # Delete oldest until limit is satisfied
    for f in files[:-MAX_SESSIONS]:
        os.remove(f)
        logger.info(f"Deleted old history file: {f}")
