import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class WebLaunchResult:
    url: str
    browser: str
    new_tab: bool


def validate_web_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only public HTTP and HTTPS websites are allowed.")
    return url.strip()


def _chrome_path() -> str | None:
    candidates = (
        shutil.which("chrome.exe"),
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    )
    return next((path for path in candidates if path and os.path.isfile(path)), None)


def open_website(url: str, browser: str = "default", new_tab: bool = True) -> WebLaunchResult:
    safe_url = validate_web_url(url)
    if browser == "chrome":
        if sys.platform != "win32":
            raise OSError("Chrome launching is supported on Windows only.")
        chrome = _chrome_path()
        if not chrome:
            raise FileNotFoundError("Google Chrome is not installed.")
        subprocess.Popen([chrome, "--new-tab" if new_tab else "--new-window", safe_url], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    elif browser == "default":
        os.startfile(safe_url)  # type: ignore[attr-defined]
    else:
        raise ValueError("That browser is not allowlisted.")
    return WebLaunchResult(safe_url, browser, new_tab)