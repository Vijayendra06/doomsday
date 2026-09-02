import json
import re
from typing import Literal
from urllib.parse import quote_plus, urlparse, urlunparse

import requests

from app.settings import settings

PlanKind = Literal["web_search", "youtube_search", "spotify_search"]

PLANNER_PROMPT = """Classify a browser-navigation request. Return JSON only:
{"kind":"web_search|youtube_search|spotify_search","query":"short search text"}.
Use youtube_search for requests to find a YouTube video, song, audio, or channel.
Use spotify_search for requests to find music, an artist, album, podcast, or playlist on Spotify.
Use web_search for every other website/search request. Never return a URL, command,
file path, app name, or explanation."""


# ==============================================================================
# PHASE 4: THE HANDS (Safe Web Action Destination Planner)
# ==============================================================================
def make_web_action_plan(text: str) -> dict[str, str]:
    """
    TODO (Phase 4 - Step 9):
    Classify user navigation request and return safe destination plan {kind, label, url}.
    - Explicit URL -> open_website
    - YouTube search -> youtube_search
    - Spotify search -> spotify_search
    - Other search -> web_search
    """
    trimmed = text.strip()
    direct_site = re.search(r"\b(?:open|launch|start|visit|go to)\s+(?:the\s+)?(youtube|google|gmail|github)\b", trimmed, re.IGNORECASE)
    if direct_site:
        sites = {"youtube": ("YouTube", "https://www.youtube.com"), "google": ("Google", "https://www.google.com"), "gmail": ("Gmail", "https://mail.google.com"), "github": ("GitHub", "https://github.com")}
        site = direct_site.group(1).lower()
        label, url = sites[site]
        return {"kind": "open_website", "label": label, "url": url}
    explicit = re.search(r"https?://[^\s]+", trimmed, re.IGNORECASE)
    if explicit:
        url = explicit.group(0).rstrip(".,!?)]")
        parsed = urlparse(url)
        if parsed.hostname and not parsed.username and not parsed.password:
            return {"kind": "open_website", "label": parsed.hostname, "url": url}

    classification = _model_classification(trimmed)
    kind = classification["kind"] if classification else _keyword_kind(trimmed)
    query = classification["query"] if classification else _extract_query(trimmed)
    if kind == "youtube_search":
        return {"kind": kind, "label": "YouTube", "url": f"https://www.youtube.com/results?search_query={quote_plus(query)}"}
    if kind == "spotify_search":
        return {"kind": kind, "label": "Spotify", "url": f"https://open.spotify.com/search/{quote_plus(query)}"}
    return {"kind": "web_search", "label": "Google", "url": f"https://www.google.com/search?q={quote_plus(query)}"}


def _keyword_kind(text: str) -> PlanKind:
    lowered = text.lower()
    if "youtube" in lowered:
        return "youtube_search"
    if "spotify" in lowered:
        return "spotify_search"
    return "web_search"


def _extract_query(text: str) -> str:
    query = re.sub(r"\b(please|can you|could you|open|launch|start|search|find|look up|google|play|on|in|the|website|site|web)\b", " ", text, flags=re.IGNORECASE)
    query = re.sub(r"\b(youtube|spotify)\b", " ", query, flags=re.IGNORECASE)
    return " ".join(query.split()).strip("?.!") or text


def _model_classification(text: str) -> dict[str, str] | None:
    if not settings.groq_api_key:
        return None
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            json={"model": settings.groq_chat_model, "messages": [{"role": "system", "content": PLANNER_PROMPT}, {"role": "user", "content": text}], "temperature": 0, "max_tokens": 80},
            timeout=15,
        )
        response.raise_for_status()
        result = json.loads(response.json()["choices"][0]["message"]["content"])
        if result.get("kind") in {"web_search", "youtube_search", "spotify_search"} and isinstance(result.get("query"), str):
            return {"kind": result["kind"], "query": result["query"].strip()}
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
        return None
    return None
