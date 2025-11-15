import os
import json
import zipfile
import requests
from io import BytesIO


GITHUB_API_RELEASES = "https://api.github.com/repos/WaleonGames/ZastepstwaUI20/releases/latest"


def load_local_version(version_path):
    """Wczytuje wersję z pliku version.json."""
    try:
        with open(version_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("version", "0.0.0")
    except:
        return "0.0.0"
    
    
def fetch_latest_release():
    """Pobiera dane o najnowszym Release z GitHuba."""
    try:
        r = requests.get(GITHUB_API_RELEASES, timeout=5)
        data = r.json()

        return {
            "version": data.get("tag_name", "0.0.0"),
            "name": data.get("name", ""),
            "body": data.get("body", ""),
            "zip_url": data["assets"][0]["browser_download_url"]
            if data.get("assets") else None
        }

    except Exception as e:
        return {"error": str(e)}


def download_zip(url):
    """Pobiera ZIP aktualizacji z GitHuba."""
    try:
        r = requests.get(url, timeout=10)
        return BytesIO(r.content)
    except Exception as e:
        return None


def install_zip(zip_bytes, target_folder):
    """Rozpakowuje ZIP do głównego folderu projektu."""
    try:
        with zipfile.ZipFile(zip_bytes, "r") as z:
            z.extractall(target_folder)
        return True
    except Exception as e:
        return False
