#!/usr/bin/env python3
"""Generate Calco / 01 app-icon explorations via Replicate.

Dual-model: 5 icons via openai/gpt-image-2, 5 via google/nano-banana-pro.
iOS app icons are 1024x1024, opaque, square. Outputs land in ../app-icons/.

Usage:
    REPLICATE_API_TOKEN=r8_... python3 scripts/generate-icons.py [name1 ...]

If filenames are passed, only those are regenerated. Otherwise all ten run.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "app-icons"

GPT = "openai/gpt-image-2"
NANO = "google/nano-banana-pro"


def _endpoint(model: str) -> str:
    return f"https://api.replicate.com/v1/models/{model}/predictions"


def _inputs(model: str, prompt: str) -> dict:
    if model == GPT:
        return {
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "quality": "high",
            "background": "opaque",
            "output_format": "png",
            "number_of_images": 1,
        }
    # nano-banana-pro
    return {
        "prompt": prompt,
        "aspect_ratio": "1:1",
        "output_format": "png",
    }


ICONS: list[dict] = [
    {
        "name": "icon-01-brushed-key.png",
        "model": NANO,
        "prompt": (
            "Square iOS app icon, 1024x1024, fully opaque background filling "
            "the entire square edge to edge, no rounded corners, no padding. "
            "Hyper-real product macro: a single warm-orange (#ff5f2c) "
            "rounded-square calculator key with a crisp white equals (=) "
            "glyph, sitting slightly proud of a brushed silver-aluminium "
            "surface that fills the whole icon. The brushed grain runs "
            "horizontally and catches a soft directional studio light from "
            "the upper-left; a gentle contact shadow sits beneath the key. "
            "Skeuomorphic and tactile, the warmth of a 1980s Casio with the "
            "precision of a modern OS. No text other than the equals glyph. "
            "8k, photorealistic."
        ),
    },
    {
        "name": "icon-02-drenched-equals.png",
        "model": GPT,
        "prompt": (
            "Square iOS app icon, 1024x1024 pixels, fully opaque background, "
            "edge to edge, no rounded corners, no padding. The whole icon is "
            "one saturated warm-orange field (#ff5f2c) with a bold white "
            "equals (=) sign deeply letterpress-embossed into the centre, "
            "crisp inner shadows making the glyph read as pressed into the "
            "surface. Confident, industrial, minimal. Only the equals sign, "
            "no other text."
        ),
    },
    {
        "name": "icon-03-panel-corner.png",
        "model": NANO,
        "prompt": (
            "Square iOS app icon, 1024x1024, fully opaque, edge to edge, no "
            "rounded corners. Tight three-quarter macro of the corner of a "
            "brushed silver-aluminium calculator panel showing four sculpted "
            "rounded-square keys: three matte-charcoal keys and, at the "
            "lower-right, one warm-orange (#ff5f2c) key with a white equals "
            "glyph that draws the eye. Soft studio light from upper-left, "
            "fine brushed-metal grain, subtle key emboss and contact "
            "shadows. Premium skeuomorphic product render. No readable text. "
            "8k, photorealistic."
        ),
    },
    {
        "name": "icon-04-c-monogram.png",
        "model": GPT,
        "prompt": (
            "Square iOS app icon, 1024x1024 pixels, fully opaque, edge to "
            "edge, no rounded corners. A single bold geometric letter 'C' "
            "(for Calco) centered on a warm cream background (#f6eddc). The "
            "'C' is set in a heavy grotesque sans serif in walnut-ink "
            "near-black (#1a1410), the lower terminal of the 'C' tipped with "
            "a warm-orange (#ff5f2c) accent. Editorial, premium, like a "
            "Milan design-house monogram, crisp and vector-clean. Only the "
            "letter C, no other text."
        ),
    },
    {
        "name": "icon-05-lcd-glow.png",
        "model": NANO,
        "prompt": (
            "Square iOS app icon, 1024x1024, fully opaque, edge to edge, no "
            "rounded corners. Extreme macro of a calculator LCD: a dark "
            "teal-green display panel (#1f3a32) fills the icon, a single "
            "large glowing pale-green (#a3f5c1) seven-segment digit centered, "
            "faint emissive bloom around the segments, a subtle glass "
            "reflection across the top, a thin brushed-metal bezel just "
            "visible at the edges. Calm and premium, the glow of a desk "
            "calculator at dusk. No other text. 8k, photorealistic."
        ),
    },
    {
        "name": "icon-06-flat-key.png",
        "model": GPT,
        "prompt": (
            "Square iOS app icon, 1024x1024 pixels, fully opaque, edge to "
            "edge, no rounded corners. Minimal flat design: one warm-orange "
            "(#ff5f2c) rounded-square tile with a clean white equals (=) "
            "sign centered on it, the tile centered on a soft cream "
            "background (#f6eddc) with a single subtle long soft shadow to "
            "the lower-right. Calm, modern, premium, generous negative "
            "space. Only the equals glyph, no other text."
        ),
    },
    {
        "name": "icon-07-casio-cream.png",
        "model": NANO,
        "prompt": (
            "Square iOS app icon, 1024x1024, fully opaque, edge to edge, no "
            "rounded corners. A loving macro fragment of a cream 1980s "
            "desktop calculator body (warm ivory plastic, #f6eddc) with one "
            "warm-orange (#ff5f2c) rounded key bearing a white equals glyph "
            "among soft grey keys, shot slightly from above in gentle window "
            "daylight, rounded mid-century industrial-design forms, faint "
            "honest patina. Nostalgic and premium, Braun-and-Casio "
            "heritage. No readable text. 8k, photorealistic."
        ),
    },
    {
        "name": "icon-08-neon-key.png",
        "model": GPT,
        "prompt": (
            "Square iOS app icon, 1024x1024 pixels, fully opaque, edge to "
            "edge, no rounded corners. A single mint-teal (#18e8c8) "
            "rounded-square calculator key with a dark-navy equals (=) "
            "glyph, centered, glowing softly, on a deep navy radial-gradient "
            "background (#0d1628 to #060a16) — the app's Neon night theme as "
            "an icon. Cool, premium, a faint mint bloom around the key. Only "
            "the equals glyph, no other text."
        ),
    },
    {
        "name": "icon-09-floating-key.png",
        "model": NANO,
        "prompt": (
            "Square iOS app icon, 1024x1024, fully opaque, edge to edge, no "
            "rounded corners. A single warm-orange (#ff5f2c) rounded-square "
            "calculator key with a white equals glyph, floating and "
            "centered, casting a soft long drop shadow, on a smooth warm "
            "peach-to-cream radial gradient (from #ffd7a7 upper-left to "
            "#f6eddc). Glossy-matte plastic key with a subtle top highlight "
            "and skeuomorphic emboss. Clean premium product render. No text "
            "other than the glyph. 8k."
        ),
    },
    {
        "name": "icon-10-flat-calc.png",
        "model": GPT,
        "prompt": (
            "Square iOS app icon, 1024x1024 pixels, fully opaque, edge to "
            "edge, no rounded corners. A clean flat illustration of a tiny "
            "calculator centered on a warm cream background (#f6eddc): a "
            "brushed-silver body with a dark teal display strip at the top "
            "and a grid of rounded keys, the rightmost column of operator "
            "keys in warm orange (#ff5f2c). Crisp geometric vector style, "
            "soft long shadow, premium editorial product illustration. No "
            "readable numbers or text."
        ),
    },
]


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


def generate_one(token: str, spec: dict) -> None:
    name = spec["name"]
    model = spec["model"]
    dest = OUT_DIR / name
    payload = {"input": _inputs(model, spec["prompt"])}
    print(f"[{name}] {model} requesting…", flush=True)
    body = json.dumps(payload).encode("utf-8")
    pred = _request(_endpoint(model), token=token, method="POST", data=body)

    get_url = pred.get("urls", {}).get("get")
    status = pred.get("status")
    deadline = time.time() + 300
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

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _download(urls[0], dest)
    print(f"[{name}] saved ({dest.stat().st_size // 1024} KB)", flush=True)


def main() -> int:
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print("ERROR: REPLICATE_API_TOKEN env var is required", file=sys.stderr)
        return 2

    wanted = set(sys.argv[1:])
    specs = [s for s in ICONS if not wanted or s["name"] in wanted]
    if not specs:
        print(f"No matching specs. Known: {[s['name'] for s in ICONS]}",
              file=sys.stderr)
        return 2

    for spec in specs:
        try:
            generate_one(token, spec)
        except Exception as e:
            print(f"[{spec['name']}] ERROR: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
