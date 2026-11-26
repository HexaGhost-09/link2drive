#!/usr/bin/env python3
"""Download HTTP(S) URLs or BitTorrent magnets with aria2c, then upload to Drive."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path.cwd()
DOWNLOADS = ROOT / "downloads"
UPLOADS = ROOT / "upload"
SCOPES = ["https://www.googleapis.com/auth/drive"]


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing GitHub Actions secret: {name}")
    return value


def read_inputs() -> list[str]:
    input_file = Path(os.environ.get("INPUT_FILE", "input.txt"))
    if not input_file.exists():
        raise SystemExit("No input file was supplied.")
    values = []
    for line in input_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("magnet:?"):
            values.append(line)
        elif urlparse(line).scheme in ("http", "https") and urlparse(line).netloc:
            values.append(line)
        else:
            raise SystemExit("Input contains an unsupported URL. Use HTTP(S) or magnet links.")
    if not values:
        raise SystemExit("No download links found.")
    return values


def download(url: str, index: int) -> None:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    cmd = [
        "aria2c", "--dir", str(DOWNLOADS),
        "--continue=true", "--max-tries=5", "--retry-wait=5",
        "--connect-timeout=30", "--timeout=60",
        "--summary-interval=10", "--console-log-level=notice",
        "--file-allocation=none", "--seed-time=0",
    ]
    if url.startswith("magnet:?"):
        cmd += ["--bt-max-peers=80", "--follow-torrent=mem"]
    else:
        cmd += [
            "--max-connection-per-server=16", "--split=16",
            "--min-split-size=1M", "--content-disposition-default-utf8=true",
            "--auto-file-renaming=true",
        ]
    # Pass the URL as an argv item; never interpolate it into a shell command.
    print(f"\n[{index}] Starting download ({'torrent' if url.startswith('magnet:?') else 'HTTP(S)'})")
    subprocess.run(cmd + [url], check=True)


def drive_service():
    creds = Credentials(
        token=None,
        refresh_token=required("GDRIVE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=required("GDRIVE_CLIENT_ID"),
        client_secret=required("GDRIVE_CLIENT_SECRET"),
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def find_or_create_folder(service, name: str, parent_id: str) -> str:
    safe = name.replace("'", "\\'")
    query = (
        "mimeType='application/vnd.google-apps.folder' and trashed=false "
        f"and name='{safe}' and '{parent_id}' in parents"
    )
    found = service.files().list(
        q=query, spaces="drive", fields="files(id,name)", pageSize=100
    ).execute().get("files", [])
    if found:
        return found[0]["id"]
    body = {"name": name, "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id]}
    return service.files().create(body=body, fields="id").execute()["id"]


def upload_file(service, path: Path, parent_id: str, share: bool) -> None:
    metadata = {"name": path.name, "parents": [parent_id]}
    media = MediaFileUpload(str(path), chunksize=8 * 1024 * 1024, resumable=True)
    request = service.files().create(
        body=metadata, media_body=media,
        fields="id,name,size,webViewLink"
    )
    response = None
    while response is None:
        status, response = request.next_chunk(num_retries=5)
        if status:
            print(f"Uploading {path.name}: {status.progress() * 100:.1f}%")
    print(f"Uploaded: {response.get('name')} ({response.get('size', '?')} bytes)")
    if share:
        service.permissions().create(
            fileId=response["id"],
            body={"type": "anyone", "role": "reader"},
            fields="id",
        ).execute()
    link = response.get("webViewLink")
    if link:
        with open(os.environ.get("GITHUB_STEP_SUMMARY", "/dev/null"), "a", encoding="utf-8") as out:
            out.write(f"- [{response.get('name')}]({link})\n")


def main() -> None:
    urls = read_inputs()
    for index, url in enumerate(urls, 1):
        download(url, index)

    files = [p for p in DOWNLOADS.rglob("*") if p.is_file()]
    if not files:
        raise SystemExit("aria2c completed but no files were downloaded.")

    if os.environ.get("ZIP_MODE", "false").lower() == "true":
        UPLOADS.mkdir(parents=True, exist_ok=True)
        archive = UPLOADS / "Downloads.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
            for path in files:
                zf.write(path, path.relative_to(DOWNLOADS))
        files = [archive]

    service = drive_service()
    parent = os.environ.get("GDRIVE_FOLDER_ID", "").strip() or "root"
    target = find_or_create_folder(service, "Downloads", parent)
    share = os.environ.get("SHARE_LINKS", "false").lower() == "true"

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as out:
            out.write("\n## Google Drive uploads\n")
    for path in files:
        upload_file(service, path, target, share)
    print(f"\nFinished: {len(files)} file(s) uploaded to Google Drive/Downloads.")


if __name__ == "__main__":
    main()
