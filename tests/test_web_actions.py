from fastapi.testclient import TestClient

from app.main import app
from app.services.web_action_planner import make_web_action_plan

client = TestClient(app)


def test_direct_website_plan_uses_only_user_http_url() -> None:
    plan = make_web_action_plan("Please open https://example.org/products?tag=jarvis")
    assert plan == {
        "kind": "open_website",
        "label": "example.org",
        "url": "https://example.org/products?tag=jarvis",
    }


def test_youtube_plan_uses_generated_search_url(monkeypatch) -> None:
    monkeypatch.setattr("app.services.web_action_planner._model_classification", lambda _: None)
    plan = make_web_action_plan("Play lofi coding music on YouTube")
    assert plan["kind"] == "youtube_search"
    assert plan["url"] == "https://www.youtube.com/results?search_query=lofi+coding+music"


def test_open_youtube_plan_uses_youtube_homepage() -> None:
    assert make_web_action_plan("Open YouTube") == {
        "kind": "open_website",
        "label": "YouTube",
        "url": "https://www.youtube.com",
    }


def test_web_url_validation_rejects_non_web_targets() -> None:
    from app.services.web_actions import validate_web_url

    for url in ("file:///C:/secret.txt", "javascript:alert(1)", "https://user:password@example.com"):
        try:
            validate_web_url(url)
        except ValueError:
            continue
        raise AssertionError(f"Unsafe URL was accepted: {url}")


def test_chrome_executor_requests_a_new_tab(monkeypatch) -> None:
    from app.services import web_actions

    launched: list[list[str]] = []
    monkeypatch.setattr(web_actions.sys, "platform", "win32")
    monkeypatch.setattr(web_actions, "_chrome_path", lambda: r"C:\Chrome\chrome.exe")
    monkeypatch.setattr(web_actions.os.path, "isfile", lambda _: True)
    monkeypatch.setattr(web_actions.subprocess, "Popen", lambda args, **_: launched.append(args))

    web_actions.open_website("https://www.youtube.com", browser="chrome", new_tab=True)

    assert launched == [[r"C:\Chrome\chrome.exe", "--new-tab", "https://www.youtube.com"]]


def test_web_action_endpoint_returns_constrained_plan(monkeypatch) -> None:
    monkeypatch.setattr("app.services.web_action_planner._model_classification", lambda _: None)
    response = client.post("/api/web-actions/plan", json={"text": "open the official NASA website"})
    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "web_search"
    assert body["url"].startswith("https://www.google.com/search?q=")


def test_spotify_plan_uses_generated_search_url(monkeypatch) -> None:
    monkeypatch.setattr("app.services.web_action_planner._model_classification", lambda _: None)
    plan = make_web_action_plan("Play Hans Zimmer on Spotify")
    assert plan["kind"] == "spotify_search"
    assert plan["url"] == "https://open.spotify.com/search/Hans+Zimmer"


