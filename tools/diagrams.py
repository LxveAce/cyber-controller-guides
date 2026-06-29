#!/usr/bin/env python3
"""Generate clean, print-friendly pin-layout / connection diagrams (PNG) for the guides.

Pure-Pillow (no system deps beyond a TrueType font), high-resolution, black-on-white so they print
well and embed in the PDFs (xhtml2pdf renders PNG). Two diagram kinds:

  * **Flashing-connection** diagrams (one per backend) — how to physically connect the device to flash
    it (USB data cable, BOOT/EN for ESP32, UART for RTL8720, qFlipper, SD writer, ADB).
  * **Module-wiring** diagrams — board ↔ external-module pin-to-pin wiring (nRF24, CC1101, LoRa, OLED…),
    driven by `data/wiring.json`.

Run:  python tools/diagrams.py        (regenerates everything into assets/)
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WIRING = ROOT / "data" / "wiring.json"

SCALE = 2  # supersample for crisp text, downscaled at save
W, H = 1100, 620
BG = (255, 255, 255)
INK = (20, 24, 28)
MUTED = (110, 120, 130)
ACCENT = (0, 150, 90)
WIRE = (40, 90, 170)
BOXBG = (244, 247, 250)
HEADBG = (0, 150, 90)


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for cand in (f"C:/Windows/Fonts/{name}", f"/usr/share/fonts/truetype/dejavu/{name}"):
        try:
            return ImageFont.truetype(cand, size * SCALE)
        except Exception:
            continue
    try:
        return ImageFont.truetype("arial.ttf", size * SCALE)
    except Exception:
        return ImageFont.load_default()


F_TITLE = _font("arialbd.ttf", 22)
F_HEAD = _font("arialbd.ttf", 15)
F_PIN = _font("consola.ttf", 13)
F_LBL = _font("arial.ttf", 12)
F_NOTE = _font("arial.ttf", 12)


class Box:
    def __init__(self, draw, title, pins, x, y, w):
        self.d, self.title, self.pins = draw, title, pins
        self.x, self.y, self.w = x, y, w
        self.head_h = 30 * SCALE
        self.row_h = 26 * SCALE
        self.h = self.head_h + max(1, len(pins)) * self.row_h + 10 * SCALE
        self._pin_y = {}

    def draw_box(self):
        d = self.d
        x, y, w, h = self.x, self.y, self.w, self.h
        d.rounded_rectangle([x, y, x + w, y + h], radius=10 * SCALE, fill=BOXBG, outline=INK, width=2 * SCALE)
        d.rounded_rectangle([x, y, x + w, y + self.head_h], radius=10 * SCALE, fill=HEADBG)
        d.rectangle([x, y + self.head_h - 12 * SCALE, x + w, y + self.head_h], fill=HEADBG)
        tw = d.textlength(self.title, font=F_HEAD)
        d.text((x + (w - tw) / 2, y + 6 * SCALE), self.title, font=F_HEAD, fill=(255, 255, 255))
        cy = y + self.head_h + 6 * SCALE
        for p in self.pins:
            d.text((x + 12 * SCALE, cy), p, font=F_PIN, fill=INK)
            self._pin_y[p] = cy + 8 * SCALE
            cy += self.row_h

    def anchor(self, pin, side):
        y = self._pin_y.get(pin, self.y + self.h / 2)
        return (self.x + self.w if side == "right" else self.x, y)


def _draw(path: Path, title: str, boxes_spec: list, links: list, footnote: str = ""):
    # Size the canvas to the content (title + lowest box + footnote) so simple diagrams aren't mostly
    # whitespace — better for printing/embedding.
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    bottoms = []
    for spec in boxes_spec:
        b = Box(tmp, spec["title"], spec["pins"], spec["x"] * SCALE, spec["y"] * SCALE, spec["w"] * SCALE)
        bottoms.append(b.y + b.h)
    # word-wrap the footnote to the canvas width
    foot_lines = []
    if footnote:
        words, cur = footnote.split(), ""
        maxw = (W - 60) * SCALE
        for w in words:
            t = (cur + " " + w).strip()
            if tmp.textlength(t, font=F_NOTE) <= maxw:
                cur = t
            else:
                foot_lines.append(cur); cur = w
        if cur:
            foot_lines.append(cur)
    content_h = (max(bottoms) / SCALE if bottoms else 300) + (16 + 16 * len(foot_lines) if foot_lines else 24)
    h_px = int(max(260, content_h))

    img = Image.new("RGB", (W * SCALE, h_px * SCALE), BG)
    d = ImageDraw.Draw(img)
    d.text((30 * SCALE, 22 * SCALE), title, font=F_TITLE, fill=INK)
    d.line([(30 * SCALE, 58 * SCALE), ((W - 30) * SCALE, 58 * SCALE)], fill=ACCENT, width=3 * SCALE)

    boxes = {}
    for spec in boxes_spec:
        b = Box(d, spec["title"], spec["pins"], spec["x"] * SCALE, spec["y"] * SCALE, spec["w"] * SCALE)
        boxes[spec["id"]] = b
    for b in boxes.values():
        b.draw_box()

    for ln in links:
        (an, ap), (bn, bp) = ln["a"], ln["b"]
        ax, ay = boxes[an].anchor(ap, "right")
        bx, by = boxes[bn].anchor(bp, "left")
        midx = (ax + bx) / 2
        d.line([(ax, ay), (midx, ay), (midx, by), (bx, by)], fill=WIRE, width=3 * SCALE)
        for px, py in ((ax, ay), (bx, by)):
            d.ellipse([px - 4 * SCALE, py - 4 * SCALE, px + 4 * SCALE, py + 4 * SCALE], fill=WIRE)
        lbl = ln.get("label", "")
        if lbl:
            lw = d.textlength(lbl, font=F_LBL)
            ly = min(ay, by) - 16 * SCALE
            d.rectangle([midx - lw / 2 - 4 * SCALE, ly, midx + lw / 2 + 4 * SCALE, ly + 16 * SCALE], fill=BG)
            d.text((midx - lw / 2, ly), lbl, font=F_LBL, fill=WIRE)

    if foot_lines:
        fy = (h_px - 14 - 16 * len(foot_lines)) * SCALE
        for line in foot_lines:
            d.text((30 * SCALE, fy), line, font=F_NOTE, fill=MUTED)
            fy += 16 * SCALE

    img = img.resize((W, h_px), Image.LANCZOS)
    ASSETS.mkdir(exist_ok=True)
    img.save(path)
    return path.name


# ── Flashing-connection diagrams (one per backend) ───────────────────

def flashing_diagrams():
    out = []
    # esptool over native USB (S2/S3/C-series) — no buttons usually needed
    out.append(_draw(ASSETS / "connect-esptool-usb.png",
        "Flashing connection — ESP32 (native USB)",
        [{"id": "pc", "title": "Computer", "pins": ["Cyber Controller", "USB-A / USB-C port"], "x": 90, "y": 200, "w": 320},
         {"id": "dev", "title": "ESP32-S3 / C-series board", "pins": ["USB-C (native USB)", "EN  (reset)", "BOOT / IO0", "3V3 · GND"], "x": 690, "y": 150, "w": 320}],
        [{"a": ("pc", "USB-A / USB-C port"), "b": ("dev", "USB-C (native USB)"), "label": "USB data cable"}],
        "Use a DATA USB cable (not charge-only). S3/C-series usually enter download mode automatically; "
        "if 'Failed to connect', hold BOOT, tap EN, release BOOT, then flash."))

    # esptool classic ESP32 with BOOT/EN
    out.append(_draw(ASSETS / "connect-esptool-boot.png",
        "Flashing connection — classic ESP32 (BOOT/EN)",
        [{"id": "pc", "title": "Computer", "pins": ["Cyber Controller", "USB port"], "x": 90, "y": 210, "w": 300},
         {"id": "dev", "title": "ESP32 DevKit (WROOM)", "pins": ["micro-USB (CP210x/CH340)", "EN  = reset", "BOOT/IO0 = download", "5V/3V3 · GND"], "x": 690, "y": 160, "w": 320}],
        [{"a": ("pc", "USB port"), "b": ("dev", "micro-USB (CP210x/CH340)"), "label": "USB data cable"}],
        "Install the CP210x or CH340 driver first. To force download mode: hold BOOT, tap EN, release BOOT."))

    # rtl8720 / BW16 over UART (AmebaD)
    out.append(_draw(ASSETS / "connect-rtl8720.png",
        "Flashing connection — BW16 / RTL8720DN (UART)",
        [{"id": "pc", "title": "USB-TTL adapter", "pins": ["3V3", "GND", "TX", "RX"], "x": 90, "y": 180, "w": 280},
         {"id": "dev", "title": "BW16 (RTL8720DN)", "pins": ["3V3", "GND", "RX  (LOG_RX)", "TX  (LOG_TX)", "CEN→GND = download"], "x": 700, "y": 150, "w": 320}],
        [{"a": ("pc", "3V3"), "b": ("dev", "3V3"), "label": "3V3"},
         {"a": ("pc", "GND"), "b": ("dev", "GND"), "label": "GND"},
         {"a": ("pc", "TX"), "b": ("dev", "RX  (LOG_RX)"), "label": "TX→RX"},
         {"a": ("pc", "RX"), "b": ("dev", "TX  (LOG_TX)"), "label": "RX→TX"}],
        "Use a 3.3V USB-TTL adapter (NEVER 5V). Enter download mode per the board (e.g. pull CEN/EN low / "
        "hold the download key) before Cyber Controller drives the AmebaD ImageTool. Some BW16 dev boards have native USB."))

    # qFlipper (Flipper Zero)
    out.append(_draw(ASSETS / "connect-qflipper.png",
        "Flashing connection — Flipper Zero (qFlipper)",
        [{"id": "pc", "title": "Computer", "pins": ["Cyber Controller", "downloads the package", "→ launches qFlipper"], "x": 80, "y": 190, "w": 360},
         {"id": "dev", "title": "Flipper Zero", "pins": ["USB-C", "DFU on boot (if needed)"], "x": 720, "y": 210, "w": 300}],
        [{"a": ("pc", "→ launches qFlipper"), "b": ("dev", "USB-C"), "label": "USB-C (qFlipper installs)"}],
        "Cyber Controller does NOT serial-flash the Flipper — it hands the firmware package to a locally "
        "installed qFlipper app, which installs it over USB. Install qFlipper first."))

    # SD-card image
    out.append(_draw(ASSETS / "connect-sd.png",
        "Writing the image — Raspberry Pi / SBC (microSD)",
        [{"id": "pc", "title": "Computer + card reader", "pins": ["Cyber Controller", "removable-only writer", "USB SD reader"], "x": 80, "y": 200, "w": 360},
         {"id": "dev", "title": "microSD card", "pins": ["FAT/ext image written", "→ insert into the Pi", "→ first boot"], "x": 720, "y": 200, "w": 320}],
        [{"a": ("pc", "USB SD reader"), "b": ("dev", "FAT/ext image written"), "label": "write .img (whole card erased)"}],
        "Cyber Controller writes only to a confirmed REMOVABLE device (the whole card is erased). Then move "
        "the microSD to the Pi and power on."))

    # ADB (RayHunter / Orbic)
    out.append(_draw(ASSETS / "connect-adb.png",
        "Installing — Android/modem device (ADB)",
        [{"id": "pc", "title": "Computer (adb)", "pins": ["Cyber Controller", "ADB backend", "adb forward :8080"], "x": 80, "y": 195, "w": 340},
         {"id": "dev", "title": "Orbic / modem", "pins": ["USB (ADB enabled)", "dashboard @ :8080"], "x": 720, "y": 205, "w": 320}],
        [{"a": ("pc", "adb forward :8080"), "b": ("dev", "USB (ADB enabled)"), "label": "USB + ADB"}],
        "Requires ADB access on the device. Cyber Controller installs over ADB and reaches the web "
        "dashboard at http://localhost:8080 via adb forward."))
    return out


# ── Module-wiring diagrams (from data/wiring.json) ───────────────────

def wiring_diagrams():
    if not WIRING.exists():
        return []
    out = []
    specs = json.loads(WIRING.read_text(encoding="utf-8"))
    for slug, spec in specs.items():
        boxes = spec["boxes"]
        # auto-place boxes left/right if x/y not given
        for i, b in enumerate(boxes):
            b.setdefault("w", 300)
            b.setdefault("x", 90 if i == 0 else 700)
            b.setdefault("y", 150)
        out.append(_draw(ASSETS / f"wiring-{slug}.png", spec["title"], boxes, spec["links"],
                         spec.get("note", "")))
    return out


def main() -> int:
    names = flashing_diagrams() + wiring_diagrams()
    print(f"generated {len(names)} diagrams into {ASSETS}:")
    for n in names:
        print("  ", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
