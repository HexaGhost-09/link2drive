#!/usr/bin/env python3
"""Upload a local file to Drime using its multipart S3 API."""
from __future__ import annotations

import mimetypes
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

TOKEN = os.environ["DRIME_TOKEN"]
BASE = "https://app.drime.cloud/api/v1"
CHUNK_SIZE = 5 * 1024 * 1024
WORKERS = 4

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {TOKEN}"})


def api(method: str, path: str, **kwargs):
    response = session.request(method, BASE + path, timeout=60, **kwargs)
    response.raise_for_status()
    if response.content:
        return response.json()
    return {}


def upload_part(url: str, part_number: int, data: bytes) -> dict:
    last_error = None
    for _ in range(3):
        try:
            response = requests.put(url, data=data, timeout=300)
            response.raise_for_status()
            etag = response.headers.get("ETag", "").strip('"')
            if not etag:
                raise ValueError("Missing ETag from upload response")
            return {"PartNumber": part_number, "ETag": etag}
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Part {part_number} failed after 3 attempts: {last_error}")


def upload_small(path: Path) -> dict:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    with path.open("rb") as file_obj:
        response = session.post(
            f"{BASE}/uploads",
            files={"file": (path.name, file_obj, mime)},
            data={"workspaceId": "0", "parentId": ""},
            timeout=300,
        )
    response.raise_for_status()
    return response.json()


def upload_large(path: Path) -> dict:
    size = path.stat().st_size
    name = path.name
    extension = path.suffix.lstrip(".").lower() or "bin"
    mime = mimetypes.guess_type(name)[0] or "application/octet-stream"

    created = api("POST", "/s3/multipart/create", json={
        "filename": name, "mime": mime, "size": size,
        "extension": extension, "workspaceId": 0,
    })
    key, upload_id = created["key"], created["uploadId"]
    part_count = (size + CHUNK_SIZE - 1) // CHUNK_SIZE

    signed = api("POST", "/s3/multipart/sign-part-urls", json={
        "key": key, "uploadId": upload_id,
        "partNumbers": list(range(1, part_count + 1)),
    })
    urls = signed["urls"]
    if len(urls) != part_count:
        raise RuntimeError(f"Drime returned {len(urls)} part URLs; expected {part_count}")

    results = []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = []
        with path.open("rb") as file_obj:
            for index, url in enumerate(urls, start=1):
                chunk = file_obj.read(CHUNK_SIZE)
                if not chunk:
                    break
                futures.append(pool.submit(upload_part, url, index, chunk))
        for future in as_completed(futures):
            results.append(future.result())
            print(f"Uploaded parts: {len(results)}/{part_count}", flush=True)

    results.sort(key=lambda item: item["PartNumber"])
    api("POST", "/s3/multipart/complete", json={
        "key": key, "uploadId": upload_id, "parts": results,
    })
    return api("POST", "/s3/entries", json={
        "filename": name, "mime": mime, "size": size,
        "extension": extension, "key": key, "workspaceId": 0,
    })


def upload(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size < CHUNK_SIZE:
        return upload_small(path)
    return upload_large(path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python drime_upload.py <file>")
    file_path = Path(sys.argv[1]).resolve()
    print(f"Uploading to Drime: {file_path.name}", flush=True)
    result = upload(file_path)
    print(f"Upload complete: {file_path.name}", flush=True)
    print(result)
