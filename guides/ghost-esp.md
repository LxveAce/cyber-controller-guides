# GhostESP — Complete Hardware Guide

> **Firmware:** GhostESP · **Upstream:** [GhostESP-Revival/GhostESP](https://github.com/GhostESP-Revival/GhostESP) (GPL-3.0, canonical — the older [Spooks4576/Ghost_ESP](https://github.com/Spooks4576/Ghost_ESP) is deprecated)
> **Chips:** ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C5, ESP32-C6 · **Cyber Controller profile:** `ghost-esp` (esptool backend, **merged single-bin @ `0x0`**, not suicide-capable)
> **This guide:** purchase → build → flash → integrate into Cyber Controller → use → troubleshoot.

## 1. Overview
GhostESP is a lightweight, ESP-IDF-based WiFi/BLE scan-monitor-deauth firmware for ESP32-family boards. It
performs WiFi AP/STA scanning, packet sniffing, deauth/disassoc and CSA attacks, beacon spam, Karma,
handshake/PMKID capture, evil-portal, and wardriving, plus BLE scanning/spam and detection (AirTag, Flipper,
skimmer, drone). On capable boards it also exposes NFC (PN532), IR learn/replay, SubGHz (CC1101), and
802.15.4/Zigbee (C5/C6) — feature availability varies by chip and board. It has an on-device UI on display
boards and a serial CLI everywhere, plus an official web flasher and companion app. Cyber Controller flashes
it (per-board merged `.bin`), drives its serial command set, and feeds its scan output into the shared target
pool for cross-device coordination.

## 2. Legal & Safety
**Authorized testing only.** Deauth/disassoc, CSA, EAPOL-logoff, beacon spam, Karma, and evil-portal all
transmit on the 2.4 GHz band and are **illegal against networks/people you do not own or have written
permission to test** in most jurisdictions (US: CFAA/FCC; EU and others similar). GhostESP is published for
educational/ethical research only. Use it solely on your own lab gear or under an explicit engagement scope.
Cyber Controller labels these as dangerous commands and (unless you disable warnings) confirms before sending.
Passive scanning/sniffing and SubGHz/NFC/IR features may still be regulated where you live — check local law.

## 3. Hardware & Purchasing
GhostESP runs on a wide board matrix (45+ tested boards upstream). Pick by display vs. no-display and by which
radios you need; Cyber Controller resolves the matching per-board merged `.bin` from the latest release.

| Tier | Board(s) | Display | Why | Where to buy (search terms) |
|------|----------|---------|-----|------------------------------|
| Purpose-built | **GhostBoard** (Rabbit-Labs) | yes | Designed for GhostESP, on-device UI | **Lab401**: "GhostBoard"; "Rabbit-Labs GhostBoard" |
| Cheap + screen | **CYD "Cheap Yellow Display" ESP32-2432S028R** (2.8" ILI9341) | yes | ~US$10–15, great starter | AliExpress/Amazon: "ESP32-2432S028R CYD 2.8" |
| Pocket + keyboard | **M5Cardputer / Cardputer ADV** (ESP32-S3) | yes | Tiny, built-in screen + keyboard | **M5Stack** store / Amazon: "M5Cardputer" |
| LilyGo | **T-Deck, T-Display-S3 (Touch), T-Embed CC1101, S3TWatch, T-Dongle-S3/C5** | mostly yes | Adds SubGHz/IR on some models | **LilyGo** store / AliExpress: "LilyGo T-Deck", "LilyGo T-Display S3" |
| Marauder-style | **Marauder v4 / v6 / v8, JCMK DevBoard Pro** | varies | Existing Marauder hardware | **Tindie**: "justcallmekoko Marauder" |
| Bare / no screen | **ESP32-S3-DevKitC-1**, ESP32-WROOM DevKitC, generic ESP32 | no | Cheapest, serial-only via Cyber Controller | Mouser/DigiKey/AliExpress: "ESP32-S3-DevKitC-1" |
| Dual-band / 802.15.4 | **ESP32-C5-DevKitC-1** (5 GHz), **ESP32-C6-DevKitC-1** (Zigbee/Thread), Pancake C5, NM-CYD-C5 | varies | Adds 5 GHz / 802.15.4 | Espressif resellers: "ESP32-C5-DevKitC-1", "ESP32-C6-DevKitC-1" |

**Display vs. no-display:** display boards (CYD 2.8", Cardputer, T-Display-S3, GhostBoard) give a standalone
on-device menu; no-display DevKits are driven entirely over serial by Cyber Controller. **Compatibility
caveat:** the CYD **2.8" (ESP32-2432S028R)** is supported, but the **2.4" `2432S024` variant is not
compatible** — buy the 2.8". S2 boards have **no Bluetooth hardware** (WiFi-only). C5 adds 5 GHz; C5/C6 add
802.15.4/Zigbee.

**Accessories:** a quality **USB-C/micro-USB data cable** (not charge-only), optional **microSD** (FAT32) for
PCAP/log/evil-portal capture, optional **GPS module** (NMEA) for wardriving, and an external antenna where the
board exposes a u.FL connector. **Avoid** ESP32 clones with the wrong flash size — verify **4 MB+** (S3
DevKitC variant expects 8 MB; see §6).

## 4. Building / Assembly
- **Pre-built boards (GhostBoard, CYD, M5, LilyGo, Marauder):** no assembly — just a data cable.
- **DevKit-only (no screen):** nothing to wire; operate over serial via Cyber Controller. A DIY SPI display is
  possible but most users buy a CYD instead.
- **Drivers:** install the USB-serial driver for your board's chip — **CP210x** (most DevKits/official),
  **CH340/CH34x** (cheap clones), or native USB-CDC (S2/S3/C3/C6). Without it, no COM port appears.
- **Per-board gotchas:** confirm the exact CYD revision (2.8" `2432S028R`, not the 2.4" `2432S024`) or the
  screen stays blank/wrong. Boards with extra radios (T-Embed CC1101, T-Dongle-C5) only expose those features
  with the matching firmware variant. S2 = WiFi only (no BLE).

## 5. Flashing & First Run (via Cyber Controller)
1. Connect the board by USB; open Cyber Controller → **Flash** tab.
2. **Port:** pick the board's COM/tty (click *Refresh* if missing → driver issue).
3. **Firmware Profile:** `GhostESP`.
4. **Board / variant:** choose your exact board (e.g. *CYD 2432S028R*, *M5Cardputer*, *ESP32-S3-DevKitC-1*,
   *ESP32-C5-DevKitC-1*, *ESP32 Generic*). The resolver matches the board name fragment to the right release
   asset; a wrong pick on a display board leaves the screen blank.
5. Click **Flash**. Cyber Controller auto-detects the chip, fetches the latest GitHub release, extracts the
   per-board **`merged.bin`**, and writes it as a **single image at offset `0x0`** (no separate
   bootloader/partition files — the merge model bakes those in, so there is no per-chip offset juggling).
   First boot shows the GhostESP UI (on screen boards) or prints a banner on the serial terminal at
   **115200 baud**.

> If `esptool` can't sync, hold **BOOT**, plug in USB, then release (or hold **BOOT**, tap **RESET**, keep
> **BOOT** 1–2 s, release) and re-flash. See §8.

## 6. Integrate into Cyber Controller
- **Profile:** `ghost-esp` (esptool backend, `image_model: merged-single-bin`, `app_offset: 0x0`,
  `flash_mode: dio`, `flash_freq: 80m`). Flash sizes: **4 MB** for generic ESP32 / C5 / C6 / CYD, **8 MB** for
  the S3-DevKitC variant. The release resolver pulls the matching `merged.bin` per board by name fragment
  (e.g. `esp32-s3-devkitc-1`, `cardputer`, `cyd-2432s028`, `esp32-c5-devkitc-1`, `lilygo-t-display-s3`).
- **Control:** open the **Devices** tab → select the port → set **Firmware = GhostESP** (Pro mode; Simple
  mode auto-uses it) → **Connect** at 115200. The protocol-aware **`ghost_esp` parser** understands GhostESP
  output, so APs/clients/BLE devices populate the **Targets** pool and the persistent terminal colorizes per
  device.
- **Command set:** the per-firmware palette offers GhostESP commands (`scanap`, `scansta`, `blescan`,
  `attack -d`, `beaconspam`, `capture`, `startportal`, `startwd`, `stop`, etc.). Dangerous verbs are confirmed
  first.
- **Cross-Comm:** a scan on the GhostESP feeds `target.added` events; auto-routing rules can fire a command on
  another connected device. **Note:** this profile is **not suicide-capable** (`supports_suicide: false`) —
  there is no self-erase build; use the Flash tab's **Erase Flash** to wipe.
- **Backup first:** use **Backup** in the Flash tab to dump the current flash before overwriting.

## 7. Usage (end-to-end)
1. **Scan:** Devices tab → `scanap` (add `-live` to channel-hop, `-stop` to halt) → watch APs appear in
   **Targets**; `scansta` logs associated stations, `scanall` does both. `blescan` (with `-f` Flipper, `-a`
   AirTag, `-g` GATT, etc.) populates BLE devices.
2. **Select a target** in Targets → right-click → action (e.g. deauth) — or select the AP and send `attack -d`
   (deauth), `attack -c` (CSA), or `attack -e` (EAPOL-logoff) in the terminal (authorized targets only).
   *Verify the exact list/select syntax for your build — see §9.*
3. **Capture:** `capture -raw` / `-eapol` / `-probe` / `-wps` writes PCAP to microSD; `capture -stop` ends it.
4. **Evil portal:** `startportal <path|default> <AP_SSID> [PSK]` serves a captive portal (lawful, authorized
   only); keystroke logs land under `/mnt/ghostesp/evil_portal/`.
5. **Wardrive:** pair a GPS module and run `startwd` to log WiFi+GPS to CSV (lawful, owner-authorized);
   `wdstream` streams to the companion app.
6. **Stop:** `stop` halts all attacks/scans/background tasks (`stopscan` stops just the AP scan); Disconnect to
   free the port.

## 8. Troubleshooting
- **No COM port:** install CP210x/CH34x driver; try another (data) cable/port; on Linux add your user to
  `dialout` and replug. S3/C3/C6 native-USB boards may need a re-plug to enumerate.
- **Flash fails / "Failed to connect":** hold **BOOT** while plugging in (or **BOOT** + tap **RESET**), lower
  the flash baud in Settings, and close any serial monitor / web flasher holding the port.
- **Blank or wrong screen after flash:** wrong board variant — re-flash selecting the exact display board
  (confirm CYD is the **2.8" 2432S028R**, not the unsupported 2.4" `2432S024`).
- **Boot-loops / brick:** use **Erase Flash** then re-flash; verify the board is genuinely **4 MB+** (8 MB for
  the S3-DevKitC variant). A bad cable or counterfeit flash chip is the usual cause.
- **No BLE features:** ESP32-**S2** has no Bluetooth hardware — use an ESP32/S3/C3/C5/C6 board for BLE.
- **Missing extra radios (NFC/IR/SubGHz/Zigbee):** these are board/chip-specific — confirm your hardware has
  the module and that you flashed the matching variant.
- **Web-flasher (fallback) issues:** if using the upstream flasher instead of Cyber Controller, use a
  Chromium browser (WebSerial), clear cached site data or try a fresh session, and disable VPN/firewall that
  may block it.

## 9. Sources
- Upstream: <https://github.com/GhostESP-Revival/GhostESP> (README, releases, `merged.bin` assets) — canonical.
- Docs: <https://docs.ghostesp.net/> (supported hardware, CLI reference, WiFi/BLE/evil-portal, installation).
- Web flasher: <https://flasher.ghostesp.net/> and `ghostesp.net/flasher`; board list: `ghostesp.net/boards`.
- Cyber Controller profile: `src/config/profiles/ghost_esp.json` (boards, chip map, merged-bin @ `0x0`, `ghost_esp` parser).
- Hardware: GhostBoard (Lab401 / Rabbit-Labs), CYD `ESP32-2432S028R`, M5Stack (Cardputer), LilyGo (T-Deck / T-Display-S3), Espressif DevKitC (S3/C5/C6), Marauder hardware (Tindie).
- Deprecated (do not use): <https://github.com/Spooks4576/Ghost_ESP>. Verify current board availability + prices and exact command syntax at use time; vendor links and CLI flags change.
