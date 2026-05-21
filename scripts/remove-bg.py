#!/usr/bin/env python3
"""Strip backgrounds from the two hero PNGs in-place using Replicate.

Usage:
    REPLICATE_API_TOKEN=r8_... python3 scripts/remove-bg.py [name1 name2 ...]

Defaults to the two hero phones if no names are passed. Overwrites the source files.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "images"
MODEL = "851-labs/background-remover"
# Versioned predictions endpoint — the /models/{owner}/{name}/predictions shortcut
# 404s for many bg-removal models, so use /v1/predictions with a version hash.
MODEL_VERSION = "a029dff38972b5fda4ec5d75d7d1cd25aeff621d2cf4946a41055d7db66b80bc"
ENDPOINT = "https://api.replicate.com/v1/predictions"
DEFAULT_TARGETS = ["hero-phone-angled-light.png", "hero-phone-angled-dark.png"]


def _request(url, *, token, method="GET", data=None):
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "wait=30",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} from {url}: {body}") from e


def _download(url, dest):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=180) as resp, dest.open("wb") as f:
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            f.write(chunk)


def _encode_data_uri(path: Path) -> str:
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _flatten(output):
    if isinstance(output, str):
        return [output]
    if isinstance(output, list):
        out = []
        for x in output:
            out.extend(_flatten(x))
        return out
    if isinstance(output, dict):
        for k in ("url", "image", "output"):
            if k in output:
                return _flatten(output[k])
    return []


def run_one(token: str, name: str) -> None:
    src = IMAGES_DIR / name
    if not src.exists():
        print(f"[{name}] not found at {src}", file=sys.stderr)
        return

    print(f"[{name}] encoding {src.stat().st_size // 1024} KB...", flush=True)
    payload = {
        "version": MODEL_VERSION,
        "input": {"image": _encode_data_uri(src), "format": "png"},
    }
    body = json.dumps(payload).encode("utf-8")

    print(f"[{name}] submitting to {MODEL}", flush=True)
    pred = _request(ENDPOINT, token=token, method="POST", data=body)

    get_url = pred.get("urls", {}).get("get")
    status = pred.get("status")
    deadline = time.time() + 240
    while status not in ("succeeded", "failed", "canceled"):
        if time.time() > deadline:
            raise RuntimeError(f"[{name}] timed out")
        time.sleep(2)
        pred = _request(get_url, token=token)
        status = pred.get("status")
        print(f"[{name}] status={status}", flush=True)

    if status != "succeeded":
        raise RuntimeError(f"[{name}] failed: {pred.get('error') or pred}")

    urls = _flatten(pred.get("output"))
    if not urls:
        raise RuntimeError(f"[{name}] no output URLs: {pred}")

    backup = src.with_suffix(src.suffix + ".bak")
    if not backup.exists():
        backup.write_bytes(src.read_bytes())
        print(f"[{name}] backup → {backup.name}", flush=True)

    _download(urls[0], src)
    print(
        f"[{name}] overwrote with transparent PNG ({src.stat().st_size // 1024} KB)",
        flush=True,
    )


def main() -> int:
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print("ERROR: REPLICATE_API_TOKEN env var is required", file=sys.stderr)
        return 2

    names = sys.argv[1:] or DEFAULT_TARGETS
    for name in names:
        try:
            run_one(token, name)
        except Exception as e:
            print(f"[{name}] ERROR: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
