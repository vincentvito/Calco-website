#!/usr/bin/env python3
"""Generate Skeuo Calc v3 marketing images via Replicate google/nano-banana-pro.

Each spec passes the real-app screenshot as `image_input` so the on-screen
calculator UI renders correctly. References branch by theme:
- Warm (daylight scenes): images/app-screenshot-light.png
- Neon (evening scenes):  images/app-screenshot-dark.png

Usage:
    REPLICATE_API_TOKEN=r8_... python3 scripts/generate-images.py [name1 ...]

If image names are passed, only those are regenerated. Otherwise all specs run.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "images"
MODEL = "google/nano-banana-pro"
ENDPOINT = f"https://api.replicate.com/v1/models/{MODEL}/predictions"

REF_LIGHT = IMAGES_DIR / "app-screenshot-light.png"
REF_DARK = IMAGES_DIR / "app-screenshot-dark.png"

UI_REMINDER_LIGHT = (
    "Render the on-screen calculator app EXACTLY as shown in the reference: "
    "the Skeuo Calc 'Warm' theme — a peach/cream radial-gradient backdrop, a "
    "brushed-silver panel containing the calculator UI, a dark teal display "
    "with a glowing pale-green LCD digit, two pill tabs labeled 'Basic' and "
    "'Scientific' just above the display, a top row of four matte-black "
    "rounded-square memory keys (MC MR M+ M-), a row of black AC/+- /% next to "
    "a WARM ORANGE (#ff5f2c) divide key on the right, three rows of WHITE "
    "rounded-square number keys (7 8 9 / 4 5 6 / 1 2 3) each paired with a "
    "WARM ORANGE operator key (multiply, minus, plus) on the right, and a "
    "bottom row with a wide white '0', white decimal, and warm orange equals. "
    "Buttons are rounded SQUARES (not circles). The orange column is ONLY on "
    "the right; do not invent any other UI elements."
)

UI_REMINDER_DARK = (
    "Render the on-screen calculator app EXACTLY as shown in the reference: "
    "the Skeuo Calc 'Neon' theme — a deep NAVY/BLUE radial-gradient backdrop, "
    "a dark navy panel containing the calculator UI, a dark teal display with "
    "a glowing pale-green LCD digit, two pill tabs labeled 'Basic' and "
    "'Scientific', a row of dark-gray rounded-square memory keys (MC MR M+ "
    "M-), a row of dark-gray AC/+- /% next to a MINT-TEAL (#18e8c8) divide "
    "key on the right, three rows of dark-gray rounded-square number keys "
    "with vivid MINT-TEAL operator keys on the right, and a bottom row with a "
    "wide dark-gray '0', dark-gray decimal, and mint-teal equals. Buttons are "
    "rounded SQUARES (not circles). The mint column is ONLY on the right; do "
    "not invent any other UI elements."
)

IMAGES: list[dict] = [
    # ============== HERO (floating product) ==============
    {
        "name": "v3-hero-phone-light.png",
        "ref": REF_LIGHT,
        "ui": UI_REMINDER_LIGHT,
        "aspect_ratio": "3:4",
        "prompt": (
            "Hyper-realistic 3D product render of a modern iPhone 15 Pro in "
            "natural titanium finish, floating at a subtle 3/4 angled "
            "perspective (tilted ~22 degrees to the right, slightly forward), "
            "screen clearly visible, on a clean cream off-white seamless "
            "backdrop (#f5f0e6 to #fdf3df soft gradient). Soft directional "
            "studio key light from upper-left, long subtle cast shadow on the "
            "surface below, depth of field, razor-sharp focus on the device. "
            "The phone screen displays the Skeuo Calc app exactly matching "
            "the reference image (Warm theme: peach gradient bg, brushed "
            "silver panel, dark teal display, warm orange operators). "
            "Editorial Apple-style product photography, no text overlays, no "
            "people, no other objects, ultra detailed, 8k. "
            + UI_REMINDER_LIGHT
        ),
    },
    {
        "name": "v3-hero-phone-dark.png",
        "ref": REF_DARK,
        "ui": UI_REMINDER_DARK,
        "aspect_ratio": "3:4",
        "prompt": (
            "Hyper-realistic 3D product render of a modern iPhone 15 Pro in "
            "black titanium finish, floating at a subtle 3/4 angled "
            "perspective (tilted ~22 degrees to the right, slightly forward), "
            "screen clearly visible, on a deep matte navy backdrop (#060a16 "
            "fading to #0d1628) with a faint mint-teal rim light around the "
            "device, soft directional key light from upper-left, long subtle "
            "shadow below. The phone screen displays the Skeuo Calc app "
            "exactly matching the reference image (Neon theme: deep navy "
            "gradient bg, dark navy panel, dark teal display, vivid mint-teal "
            "operators). Editorial Apple-style product photography, no text "
            "overlays, no people, ultra detailed, 8k. "
            + UI_REMINDER_DARK
        ),
    },

    # ============== TACTILE — desk overhead ==============
    {
        "name": "v3-desk-overhead-day.jpg",
        "ref": REF_LIGHT,
        "ui": UI_REMINDER_LIGHT,
        "aspect_ratio": "4:3",
        "prompt": (
            "Editorial top-down overhead photograph at late-morning daylight. "
            "Surface: a beautifully clean light oak desk with subtle wood "
            "grain. Centered slightly right: a modern iPhone in natural "
            "titanium, screen up, displaying the Skeuo Calc Warm theme from "
            "the reference. Around the iPhone: a closed tan leather notebook "
            "on the left, a small white ceramic espresso cup with crema, a "
            "slim black fountain pen, a tiny green succulent in a terracotta "
            "pot. Bright soft natural daylight streaming from upper-left, "
            "clean cool-warm white balance, gentle soft shadows. Editorial "
            "product-lifestyle photography for a premium consumer tech "
            "brand, 8k, hyper detailed, no people. "
            + UI_REMINDER_LIGHT
        ),
    },
    {
        "name": "v3-desk-overhead-night.jpg",
        "ref": REF_DARK,
        "ui": UI_REMINDER_DARK,
        "aspect_ratio": "4:3",
        "prompt": (
            "Editorial top-down overhead photograph at evening. A dark "
            "walnut desk lit by a single warm brass desk lamp creating a "
            "soft pool of amber light. Centered slightly right: a modern "
            "iPhone in natural titanium, screen up, displaying the Skeuo "
            "Calc Neon theme from the reference (navy gradient, mint "
            "operators). Around it: a closed dark leather notebook, a small "
            "matte black ceramic espresso cup, a brass fountain pen, a small "
            "green succulent in a terracotta pot half in shadow. Deep "
            "shadows in unlit areas, warm tungsten color temperature, "
            "intimate cozy evening mood, editorial photography, 8k, no "
            "people. "
            + UI_REMINDER_DARK
        ),
    },

    # ============== WORKSPACE — eye-level 3/4 ==============
    {
        "name": "v3-desk-three-quarter-day.jpg",
        "ref": REF_LIGHT,
        "ui": UI_REMINDER_LIGHT,
        "aspect_ratio": "16:9",
        "prompt": (
            "Eye-level three-quarter view at clean midday daylight. A "
            "minimal walnut wood desk in a bright Scandinavian apartment "
            "with a large window in the back. In sharp foreground focus: a "
            "modern iPhone in natural titanium upright in a slim tan leather "
            "MagSafe stand, screen facing the camera, showing the Skeuo Calc "
            "Warm theme from the reference. In soft-blurred background: an "
            "open silver MacBook Pro, a small green plant in a stone pot. "
            "Bright clean daylight, fresh modern Apple aesthetic, cinematic "
            "shallow depth of field, 8k, no people. EXACTLY ONE iPhone, do "
            "NOT duplicate the device. "
            + UI_REMINDER_LIGHT
        ),
    },
    {
        "name": "v3-desk-three-quarter-night.jpg",
        "ref": REF_DARK,
        "ui": UI_REMINDER_DARK,
        "aspect_ratio": "16:9",
        "prompt": (
            "Eye-level three-quarter view at evening. CRITICAL: EXACTLY ONE "
            "single iPhone in the entire scene — do NOT duplicate, do NOT "
            "show multiple phones. A walnut wood desk in a dim apartment "
            "with a window in the back showing deep blue dusk sky. In sharp "
            "foreground focus: the ONE iPhone in natural titanium, upright "
            "in a slim tan leather MagSafe stand, screen lighting the scene "
            "slightly, showing the Skeuo Calc Neon theme from the reference "
            "(navy gradient bg, mint operators). In soft-blurred background: "
            "an open silver MacBook Pro with screen glow, a small brass desk "
            "lamp casting a warm pool of amber light, a leather notebook. "
            "Moody cozy evening, warm tungsten + cool dusk window mix, "
            "cinematic shallow depth of field, deep shadows, no people, 8k. "
            "ONE iPhone only. "
            + UI_REMINDER_DARK
        ),
    },

    # ============== HAND-HELD (tactile) ==============
    {
        "name": "v3-hand-tactile-day.jpg",
        "ref": REF_LIGHT,
        "ui": UI_REMINDER_LIGHT,
        "aspect_ratio": "4:5",
        "prompt": (
            "Close-up cinematic photograph of a person's hand holding a "
            "modern iPhone in natural titanium vertically. Thumb hovers just "
            "above the warm orange '=' key. The on-screen calculator app "
            "exactly matches the reference (Skeuo Calc Warm theme — peach "
            "gradient bg, brushed silver panel, dark teal display, vivid "
            "warm orange operators on the right column). Background: a "
            "bright, airy cafe at midday with large windows letting in clean "
            "daylight, soft window-bokeh, neutral palette. Shallow depth of "
            "field focused on the screen and thumb, no face visible, "
            "editorial product-in-hand photography, 8k, hyper detailed. "
            "Critical: rounded square buttons (NOT circles); orange only on "
            "the rightmost column; white digit keys; black memory row. "
            + UI_REMINDER_LIGHT
        ),
    },
    {
        "name": "v3-hand-tactile-night.jpg",
        "ref": REF_DARK,
        "ui": UI_REMINDER_DARK,
        "aspect_ratio": "4:5",
        "prompt": (
            "Close-up cinematic photograph at evening of a person's hand "
            "holding a modern iPhone in natural titanium vertically. Thumb "
            "hovers above the mint-teal '=' key. The on-screen calculator "
            "exactly matches the reference (Skeuo Calc Neon theme — deep "
            "navy gradient bg, dark navy panel, dark teal display, vivid "
            "mint-teal operators). Background: a dimly lit cozy cafe or bar "
            "at night, blurred glow from warm vintage Edison bulb string "
            "lights, deep amber bokeh, dark moody atmosphere. Shallow depth "
            "of field focused on the screen and thumb, no face visible, "
            "editorial product-in-hand photography, 8k. Critical UI "
            "accuracy: rounded square buttons (NOT circles), mint only on "
            "the rightmost column. "
            + UI_REMINDER_DARK
        ),
    },

    # ============== MODES — iPad showcase ==============
    {
        "name": "v3-modes-ipad-day.png",
        "ref": REF_LIGHT,
        "ui": UI_REMINDER_LIGHT,
        "aspect_ratio": "3:4",
        "prompt": (
            "Hyper-realistic 3D product render of a modern iPad Pro 11 inch "
            "in SPACE BLACK finish (matte dark grey, NOT gold or rose-gold), "
            "held in PORTRAIT orientation (vertical), tilted at a subtle 3/4 "
            "angle to the right (about 15 degrees), floating in space, soft "
            "directional key light from upper-left, gentle reflection on the "
            "back glass, long soft cast shadow below, on a clean cream "
            "off-white seamless studio backdrop with bright daylight "
            "lighting. CRITICAL: the iPad screen is completely filled by the "
            "portrait Skeuo Calc Warm theme from the reference — no black "
            "bezel visible inside the screen area, calculator extends edge "
            "to edge filling the full display. Operator keys on the right "
            "column are BRIGHT WARM ORANGE (#ff5f2c) — saturated, vivid, "
            "NOT muted brown or tan. White rounded-square number keys, "
            "matte-black memory row, dark teal display, two pill tabs "
            "'Basic'/'Scientific'. Apple editorial product photography, no "
            "people, ultra detailed, 8k. "
            + UI_REMINDER_LIGHT
        ),
    },
    {
        "name": "v3-modes-ipad-night.png",
        "ref": REF_DARK,
        "ui": UI_REMINDER_DARK,
        "aspect_ratio": "3:4",
        "prompt": (
            "Hyper-realistic 3D product render of a modern iPad Pro 11 inch "
            "in SPACE BLACK finish (matte dark grey, NOT gold), held in "
            "PORTRAIT orientation (vertical), tilted at a subtle 3/4 angle "
            "to the right (about 15 degrees), floating in space, on a deep "
            "matte navy backdrop (#060a16 to #0d1628) with a faint "
            "mint-teal rim light around the device, soft cool key light "
            "from upper-left, long subtle shadow below. CRITICAL: the iPad "
            "screen is completely filled edge-to-edge by the Skeuo Calc "
            "Neon theme from the reference (navy gradient bg, dark navy "
            "panel, dark teal display, vivid mint-teal operators) — no "
            "bezel visible inside the screen. Operator keys on the right "
            "column are BRIGHT MINT TEAL (#18e8c8) — saturated, vivid, NOT "
            "muted. Apple editorial product photography in moody evening "
            "mood, no people, ultra detailed, 8k. "
            + UI_REMINDER_DARK
        ),
    },

    # ============== ENVIRONMENT — wide studio ==============
    {
        "name": "v3-environment-wide-day.jpg",
        "ref": REF_LIGHT,
        "ui": UI_REMINDER_LIGHT,
        "aspect_ratio": "16:9",
        "prompt": (
            "Wide cinematic environmental photograph of a designer's studio "
            "at clean midday daylight. A walnut desk under a large window "
            "letting bright daylight pour in across the wood, a tall green "
            "monstera plant in a stone pot, color paint swatches fanned out "
            "on the desk, a leather sketchbook with a pen, and an open "
            "silver MacBook Pro slightly behind. EXACTLY ONE iPhone in "
            "natural titanium rests on the desk in the foreground at a "
            "slight angle, screen facing the camera, displaying the Skeuo "
            "Calc Warm theme from the reference. Cinematic depth of field "
            "with the iPhone in razor-sharp focus and the room softly "
            "blurred. Fresh clean daylight, cool-neutral white balance, no "
            "people, editorial lifestyle photography, 16:9, 8k. Only one "
            "iPhone. "
            + UI_REMINDER_LIGHT
        ),
    },
    {
        "name": "v3-environment-wide-night.jpg",
        "ref": REF_DARK,
        "ui": UI_REMINDER_DARK,
        "aspect_ratio": "16:9",
        "prompt": (
            "Wide cinematic environmental photograph of a designer's studio "
            "in the evening. A walnut desk in a dim room, a brass desk lamp "
            "casting a warm pool of amber tungsten light, a tall monstera "
            "plant in shadow, color paint swatches partially lit on the "
            "desk, a leather sketchbook, and an open silver MacBook Pro "
            "slightly behind with screen glow. Large window in the back "
            "shows deep dusk navy blue with city lights starting to twinkle. "
            "EXACTLY ONE iPhone in natural titanium rests on the desk in "
            "the foreground at a slight angle, screen facing camera, "
            "showing the Skeuo Calc Neon theme from the reference (navy "
            "gradient bg, mint operators). Cinematic depth of field with "
            "the iPhone in razor-sharp focus, intimate cozy evening, warm "
            "tungsten + cool dusk mix, no people, editorial lifestyle "
            "photography, 16:9, 8k. Only one iPhone. "
            + UI_REMINDER_DARK
        ),
    },

    # ============== TIME-AGNOSTIC ==============
    {
        "name": "v3-macro-display.jpg",
        "ref": REF_LIGHT,
        "ui": UI_REMINDER_LIGHT,
        "aspect_ratio": "16:9",
        "prompt": (
            "Extreme macro photograph of just the top portion of a modern "
            "iPhone display showing the Skeuo Calc dark teal display panel "
            "filled with the calculation '1,250 × 1.0825 = 1,353.13' "
            "rendered in glowing pale-green seven-segment-style LCD digits "
            "(slightly emissive). The panel has subtle plastic bezel "
            "reflections, deep blacks around the edge of the screen, the "
            "very tops of the white number buttons just barely visible at "
            "the bottom of the frame. Cinematic, razor-sharp focus on the "
            "digits, slight chromatic glow on the LCD numbers, no other "
            "text, editorial macro photography, 8k. The calculator app "
            "matches the reference image. "
            + UI_REMINDER_LIGHT
        ),
    },
    {
        "name": "v3-heritage-side-by-side.jpg",
        "ref": REF_LIGHT,
        "ui": UI_REMINDER_LIGHT,
        "aspect_ratio": "16:9",
        "prompt": (
            "Editorial flat-lay top-down photograph on a soft beige paper "
            "background. On the left: a vintage cream Casio MS-80 desktop "
            "calculator with grey rubber buttons, faded LCD, retro 1980s "
            "industrial design with slight wear marks. On the right: a "
            "modern iPhone in natural titanium running the Skeuo Calc Warm "
            "theme exactly as the reference image (peach gradient bg, "
            "brushed silver panel, dark teal display with glowing green LCD "
            "digit, white rounded-square number buttons, warm orange "
            "operator column, two pill tabs 'Basic'/'Scientific'). Both "
            "devices precisely horizontal and parallel, soft diffused "
            "studio light from above, very subtle shadows, warm color "
            "grading, design-magazine editorial style, 8k, no text "
            "overlays. "
            + UI_REMINDER_LIGHT
        ),
    },
]


def _palette_spec(name: str, *, bg: str, panel: str, display: str,
                  lcd: str, op_hex: str, op_word: str) -> dict:
    slug = name.lower()
    return {
        "name": f"palette-{slug}.png",
        "ref": REF_LIGHT,
        "ui": "",
        "aspect_ratio": "3:4",
        "prompt": (
            f"Hyper-realistic 3D product render of a modern iPhone 15 Pro in "
            f"natural titanium finish, held at a subtle 3/4 angle to the right "
            f"(about 20 degrees), screen clearly visible, floating on a clean "
            f"cream off-white seamless studio backdrop, soft directional key "
            f"light from upper-left, long subtle cast shadow. The phone screen "
            f"displays the Skeuo Calc app in the {name} palette. CRITICAL — the "
            f"layout exactly matches the reference image (same Basic/Scientific "
            f"tabs at top, same digital LCD display panel at the top with a "
            f"single '0' digit on the right, four rounded-square memory keys "
            f"MC MR M+ M-, a row with AC, plus-minus, percent, and the divide "
            f"key on the right, three rows of number keys 7-8-9 / 4-5-6 / 1-2-3 "
            f"each paired with an operator on the right (multiply, minus, "
            f"plus), and a bottom row with wide '0', decimal, and equals). "
            f"COLORS for this palette: the on-screen background gradient is "
            f"{bg}; the panel framing the calculator is {panel}; the display "
            f"panel itself is {display} with the LCD digit glowing in {lcd}; "
            f"the operator keys on the rightmost column (divide, multiply, "
            f"minus, plus, equals) are vivid {op_word} ({op_hex}), saturated, "
            f"NOT muted; the memory row keys and the AC/plus-minus/percent "
            f"keys are darker tinted versions of the panel. Number keys are "
            f"light rounded-square buttons. Apple editorial product "
            f"photography, no people, ultra detailed, 8k. Buttons are rounded "
            f"SQUARES (not circles). The {op_word} column is ONLY on the "
            f"right."
        ),
    }


PALETTES: list[dict] = [
    _palette_spec(
        "Tangerine",
        bg="peach/cream radial gradient (#ffd7a7 to #f6eddc)",
        panel="brushed silver-gray with subtle metallic sheen",
        display="dark teal-black (#1f3a32)",
        lcd="pale green (#a3f5c1)",
        op_hex="#ff5f2c", op_word="warm orange",
    ),
    _palette_spec(
        "Mint",
        bg="deep navy radial gradient (#0d1628 to #060a16)",
        panel="dark navy (#0e1a36)",
        display="dark teal-black (#1f3a32)",
        lcd="mint green (#7bf5d4)",
        op_hex="#18e8c8", op_word="mint teal",
    ),
    _palette_spec(
        "Crimson",
        bg="warm beige-to-rust radial gradient (#f3dcc8 to #e8b59c)",
        panel="warm cream (#f6e8d8)",
        display="dark wine (#2a0e14)",
        lcd="warm amber (#ffb56b)",
        op_hex="#e2384b", op_word="crimson red",
    ),
    _palette_spec(
        "Cobalt",
        bg="sky-to-cobalt radial gradient (#cfe1ff to #94b8ec)",
        panel="light steel blue (#d6e3f5)",
        display="deep navy (#0a1530)",
        lcd="sky blue (#7ec8ff)",
        op_hex="#2563eb", op_word="cobalt blue",
    ),
    _palette_spec(
        "Sage",
        bg="muted sage cream radial gradient (#e6ead8 to #c9d2b6)",
        panel="off-white (#f1f0e8)",
        display="dark forest green (#1a2a1f)",
        lcd="sage green (#b6e0a3)",
        op_hex="#7a9c6e", op_word="sage green",
    ),
    _palette_spec(
        "Lavender",
        bg="soft lilac radial gradient (#e8def7 to #c9b5ef)",
        panel="pale lilac (#ece2f5)",
        display="dark plum (#1f1530)",
        lcd="lavender (#d6c5ff)",
        op_hex="#a78bfa", op_word="lavender",
    ),
    _palette_spec(
        "Sunshine",
        bg="pale yellow radial gradient (#fff5cf to #f7d97a)",
        panel="cream (#fbf0d4)",
        display="dark olive (#2a2510)",
        lcd="golden yellow (#fde68a)",
        op_hex="#f4b73b", op_word="golden yellow",
    ),
    _palette_spec(
        "Slate",
        bg="cool gray radial gradient (#dde2ea to #aab3c0)",
        panel="light slate (#e2e6ec)",
        display="charcoal (#1f242c)",
        lcd="slate blue (#9bb0d6)",
        op_hex="#64748b", op_word="slate gray",
    ),
]

IMAGES.extend(PALETTES)


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
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        mime = "image/png"
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


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
    dest = IMAGES_DIR / name
    inputs = {
        "prompt": spec["prompt"],
        "aspect_ratio": spec["aspect_ratio"],
        "output_format": "jpg" if name.endswith(".jpg") else "png",
    }
    ref = spec.get("ref")
    if ref is not None:
        ref_path = Path(ref)
        if ref_path.exists():
            inputs["image_input"] = [_encode_data_uri(ref_path)]
            print(f"[{name}] feeding reference {ref_path.name}", flush=True)
        else:
            print(f"[{name}] WARNING: reference {ref_path} not found", flush=True)

    payload = {"input": inputs}
    print(f"[{name}] requesting…", flush=True)
    body = json.dumps(payload).encode("utf-8")
    pred = _request(ENDPOINT, token=token, method="POST", data=body)

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

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    _download(urls[0], dest)
    print(f"[{name}] saved ({dest.stat().st_size // 1024} KB)", flush=True)


def main() -> int:
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print("ERROR: REPLICATE_API_TOKEN env var is required", file=sys.stderr)
        return 2

    wanted = set(sys.argv[1:])
    specs = [s for s in IMAGES if not wanted or s["name"] in wanted]
    if not specs:
        print(
            f"No matching specs. Known: {[s['name'] for s in IMAGES]}",
            file=sys.stderr,
        )
        return 2

    for spec in specs:
        try:
            generate_one(token, spec)
        except Exception as e:
            print(f"[{spec['name']}] ERROR: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
