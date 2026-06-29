# OUI-Spy — Complete Hardware Guide

> **Firmware:** OUI-Spy Unified Blue · **Upstream:** [colonelpanichacks/oui-spy-unified-blue](https://github.com/colonelpanichacks/oui-spy-unified-blue) (license: not stated in README — verify in repo)
> **Chip:** ESP32-S3 (canonical board: Seeed Studio **XIAO ESP32-S3**) · **Cyber Controller profile:** `oui-spy` (esptool backend, merged single `.bin` @ `0x0`, no protocol parser, not suicide-capable)
> **This guide:** purchase → build → flash → integrate into Cyber Controller → use → troubleshoot.

## 1. Overview
OUI-Spy is a **passive, detection-only** BLE/WiFi awareness firmware for the ESP32-S3. It fingerprints
nearby radios by their **OUI** (the vendor prefix in a MAC address), MAC address, and BLE device-name
patterns, then alerts you with a piezo buzzer and NeoPixel LED. The "Unified Blue" build packs four modes
behind a boot-time selector: **Detector** (watchlist of OUIs/MACs/name patterns), **Foxhunter**
(RSSI-based proximity tracking — the buzzer cadence speeds up as you close on a target device),
**Flock-You** (detects Flock Safety cameras / Raven gunshot sensors via 42 known OUI prefixes + name/UUID
matching), and **Sky Spy** (passive drone detection via FAA Remote ID / ASTM F3411 WiFi beacons).
Cyber Controller's role is narrow but useful: it **flashes** the firmware and gives you a **raw serial
terminal** to watch its JSON output. (Upstream also ships a broader "Omni/unified" build with more engines
— UniPwn, Wardrive, Flock-WiFi/BLE — driven over BLE GATT; that is a different repo — verify if you need it.)

## 2. Legal & Safety
**Detection-only and passive.** OUI-Spy listens; it does not deauth, spoof, or transmit attacks, so it
avoids the legal exposure that active WiFi tools carry. Per the upstream disclaimer it is "intended for
security research, privacy auditing, and educational purposes," and **detecting the presence of
surveillance hardware in public is legal in most jurisdictions**. Two cautions still apply: (1) **tracking
a specific person's device** by MAC/OUI (e.g. Foxhunter proximity hunting) can implicate stalking,
wiretap, and privacy law — only track devices you own or are authorized to locate; (2) modern phones use
**MAC randomization**, so a randomized address is not a stable identity and may belong to an uninvolved
person. Respect local privacy/radio law and engagement scope. Cyber Controller does not gate any OUI-Spy
command (the profile has no protocol/danger model) — the responsibility is yours.

## 3. Hardware & Purchasing
OUI-Spy targets the **ESP32-S3**. The canonical hardware is the **Seeed Studio XIAO ESP32-S3** (dual-core
Xtensa LX7, BLE + WiFi, 8 MB flash) wired to a piezo buzzer and NeoPixel. Pick by how you want to buy it:

| Tier | Hardware | Why | Where to buy (search terms) |
|------|----------|-----|------------------------------|
| Turnkey (recommended) | **Official OUI-Spy** (assembled two-board PCB = XIAO ESP32-S3 + buzzer + NeoPixel) | Ready-to-use, no soldering, correct pinout | **Tindie**: "Oui-Spy Colonel Panic" (~US$75 assembled); also **colonelpanic.tech** |
| DIY board | **OUI-Spy bare PCBs** (pair) | Solder your own XIAO into the official PCB art | **Tindie**: "Oui-Spy pcbs only" (~US$20 the pair) |
| Wearable variants | OUI-Spy **Patch / Skull Badge / Earrings** | Same ESP32-S3 detection in a wearable form | **Tindie** store "Colonel Panic's Hack Shack" |
| Bare module (build it yourself) | **Seeed Studio XIAO ESP32-S3** + small **piezo buzzer** + **WS2812/NeoPixel** | Cheapest path; wire to the firmware's pins | **Seeed Studio** store / Amazon: "XIAO ESP32-S3" |
| Other ESP32-S3 dev boards | e.g. a generic **ESP32-S3 DevKit** (8 MB) | Works for serial-only use; no buzzer/LED unless you add them | AliExpress/Amazon: "ESP32-S3 DevKitC 8MB" |

**Notes / verify:** the Cyber Controller profile also references a **LILYGO T-Display S3** as a possible
ESP32-S3 target, but the upstream `oui-spy-unified-blue` README documents only the **XIAO ESP32-S3** pinout
— if you use a T-Display S3 or other board you must build a matching PlatformIO env and re-map pins
(verify). **Accessories:** a real **USB-C data cable** (not charge-only); the buzzer/NeoPixel are required
for the audio/visual alerts (the official board includes them). The board exposes **8 MB** flash — the
profile flashes with `dio` mode at `80 MHz`.

## 4. Building / Assembly
- **Official assembled OUI-Spy:** no assembly — just a USB-C data cable. Skip to §5.
- **Bare PCB / DIY:** solder a XIAO ESP32-S3 onto the PCB; the firmware's fixed pinout is **GPIO 3 = piezo
  buzzer**, **GPIO 21 = NeoPixel LED**, **GPIO 0 = BOOT button** (hold ~2 s to return to the mode selector).
  Wire the buzzer and NeoPixel to those pins or the alerts won't fire.
- **Drivers:** the XIAO ESP32-S3 uses **native USB** (no external UART chip), so it usually enumerates with
  no driver. Clone/dev boards may use **CH340/CH341** or **CP210x** — install that driver or no COM port
  appears.
- **Building from source (optional):** the firmware is a **PlatformIO** project (deps: NimBLE-Arduino, ESP
  Async WebServer + AsyncTCP, ArduinoJson, Adafruit NeoPixel). Build with `pio run`; the artifact lands in
  `.pio/build/seeed_xiao_esp32s3/firmware.bin`. It uses a **custom partition table** (~6 MB app + ~2 MB
  LittleFS). You only need this if you want to modify the firmware or there is no prebuilt release —
  otherwise let Cyber Controller flash the released image (§5).

## 5. Flashing & First Run (via Cyber Controller)
1. Connect the board by USB-C; open Cyber Controller → **Flash** tab.
2. **Port:** pick the board's COM/tty (click *Refresh* if missing → driver/cable issue). For the XIAO press
   **BOOT** (GPIO 0) while plugging in if it won't enter download mode.
3. **Firmware Profile:** `OUI-Spy` (profile id `oui-spy`).
4. **Board / chip:** the profile is **fixed to `esp32s3`** (single "ESP32-S3 Generic" board entry, 8 MB /
   `dio` / `80 MHz`) — there's no display variant to choose.
5. Click **Flash.** Cyber Controller (esptool backend) resolves the **latest GitHub release**, downloads
   the `.bin` asset, and writes it as a **merged single image at offset `0x0`** (`merged: true`). If the
   release **404s** — common for this project — the profile's `source_only_empty` fallback means there is
   no flashable asset; build from source (§4) or point at a release that has a `.bin`.
6. **First run:** the board boots into the **mode selector**. By default it brings up a WiFi AP for control
   (see §7); on screenless boards there's no display, so you drive it over WiFi/serial.

> Why `0x0`? The release ships an esptool **merged** image (bootloader + partitions + `boot_app0` + app
> baked into one file), so it's written at `0x0` in a single step — unlike the source build's separate
> `bootloader.bin@0x0` / `partitions.bin@0x8000` / `boot_app0.bin@0xe000` / `firmware@0x10000` layout used
> by the upstream `flash.py`.

## 6. Integrate into Cyber Controller
- **Profile:** `oui-spy` (`src/config/profiles/oui_spy.json`) — backend **esptool**, chip **esp32s3**,
  `image_model: merged-single-bin` @ `0x0`, resolver **github_release**, `on_error: source_only_empty`.
- **No protocol parser:** the profile's `protocol` is **null**, so unlike Marauder there is **no
  protocol-aware target parsing, no per-firmware command palette, and no danger-confirm**. In the
  **Devices** tab the OUI-Spy port behaves as a **raw serial terminal** at **115200 baud** (`default_baud`).
- **Control:** open the **Devices** tab → select the port → **Connect** → read the firmware's serial output
  (Sky Spy emits structured **JSON** per detected drone; other modes log detections). Send the firmware's
  own serial/keyboard inputs if/where it accepts them — there are no Cyber-Controller-injected verbs.
- **Not suicide-capable:** `supports_suicide: false` — the Flash tab will not offer a self-erase/suicide
  action for this profile.
- **Backup first:** use **Backup** in the Flash tab to dump current flash before overwriting, in case you
  want to revert.
- **Out-of-band control:** most OUI-Spy interaction happens over **WiFi**, not the serial link — see §7.

## 7. Usage (end-to-end)
1. **Flash** the firmware (§5) and power the board.
2. **Boot selector:** join the WiFi AP **SSID `oui-spy` / password `ouispy123`**, browse to
   **`192.168.4.1`**, and pick a mode. (Hold **BOOT** ~2 s any time to return here.)
3. **Detector:** configure your **watchlist** (OUIs / MAC addresses / device-name patterns) in the web
   dashboard; the buzzer + NeoPixel fire when a match advertises nearby. Mode AP:
   `snoopuntothem` / `astheysnoopuntous`.
4. **Foxhunter:** enter or live-select a target MAC, then **walk toward the loudening buzzer** — cadence
   scales inversely with RSSI (distance). Mode AP: `foxhunter` / `foxhunter`. Use only on devices you're
   authorized to locate.
5. **Flock-You:** drive/walk; it flags Flock Safety cameras / Raven sensors via 42 OUI prefixes, BLE name
   patterns (`Flock`, `Penguin`, `FS Ext Battery`, `Pigvision`), company ID `0x09C8`, and Raven UUID;
   exports JSON/CSV and supports browser-geolocation wardriving. Mode AP: `flockyou` / `flockyou123`.
6. **Sky Spy:** **no AP** — purely passive Remote-ID drone capture; watch the **serial JSON** (serial
   numbers, location, altitude, heading) in Cyber Controller's Devices terminal at 115200 baud.
7. **Stop / switch:** hold BOOT to re-enter the selector; Disconnect in Cyber Controller to free the port.

## 8. Troubleshooting
- **No COM port:** XIAO uses native USB — try another **data** cable and USB port first; for clone boards
  install **CH340/CP210x**; on Linux add your user to `dialout` and replug.
- **Won't enter download mode / "Failed to connect":** hold **BOOT** (GPIO 0) while plugging in (or during
  connect), close any serial monitor holding the port, and lower the flash baud in Settings.
- **Flash succeeds but nothing happens:** confirm the **merged release `.bin`** was used (the source build's
  separate files go to different offsets — don't mix them); re-flash if the asset was empty.
- **Release 404 / "no asset":** expected for this project — the `source_only_empty` fallback means there's
  nothing to flash; **build from source** (§4) or select a release tag that actually has a `.bin`.
- **No buzzer / LED alerts:** on DIY boards the buzzer/NeoPixel must be on **GPIO 3 / GPIO 21**; the
  official board wires these for you.
- **Can't find the WiFi AP:** the AP only appears in modes that create one (Sky Spy has none); re-enter the
  selector (`oui-spy` / `ouispy123` @ `192.168.4.1`) and pick a web-enabled mode.
- **Tracking a phone that keeps "moving"/disappearing:** **MAC randomization** — the address rotated;
  re-acquire the current MAC. Don't assume a randomized MAC is the same device over time.
- **Boot-loops / brick:** use **Erase Flash** in the Flash tab, then re-flash a known-good merged image.

## 9. Sources
- Upstream firmware: <https://github.com/colonelpanichacks/oui-spy-unified-blue> (README: modes, WiFi APs,
  hardware pinout, PlatformIO build, `flash.py`, partition layout, disclaimer).
- Meta / ecosystem repo: <https://github.com/colonelpanichacks/oui-spy> (board overview, firmware variant
  links; no formal releases on the meta repo).
- Hardware & purchasing: **colonelpanic.tech**; **Tindie** "Colonel Panic's Hack Shack" — Oui-Spy
  (assembled ~US$75), Oui-Spy pcbs only (~US$20 pair), Patch/Skull Badge/Earrings variants; XIAO ESP32-S3
  from **Seeed Studio**. Verify current prices/availability at purchase time.
- Background write-ups: Hackster.io "Oui Spy, Now and Beyond" and "Colonel Panic's OUI-SPY … Foxhunting
  Handset."
- Cyber Controller profile: `src/config/profiles/oui_spy.json` (id `oui-spy`, esptool/esp32s3, merged `.bin`
  @ `0x0`, github_release resolver, `source_only_empty`, `supports_suicide: false`, `default_baud` 115200).
- **Verify:** firmware license; LILYGO T-Display S3 support vs. XIAO-only README; broader "Omni/unified"
  BLE-GATT build (UniPwn/Wardrive/Flock-WiFi/BLE) if you need engines beyond the four-mode Unified Blue.
