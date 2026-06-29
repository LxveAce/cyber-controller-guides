# T-REX — Complete Hardware Guide

> **Firmware:** T-REX · **Upstream:** [abdallahnatsheh/T-REX-FIRMWARE](https://github.com/abdallahnatsheh/T-REX-FIRMWARE) (AGPL-3.0)
> **Chip:** ESP32-S3 · **Hardware:** LilyGo **T-Deck** / **T-Deck Plus** · **Cyber Controller profile:** `t-rex` (esptool backend, merged single `.bin` @ `0x0`, default baud 115200)
> **This guide:** purchase → build → flash → integrate into Cyber Controller → use → troubleshoot.

## 1. Overview
T-REX turns the LilyGo **T-Deck** (and **T-Deck Plus**) into a pocket pentest terminal: an ESP32-S3
handheld with a physical QWERTY keyboard, trackball, and 2.8" display driving an on-device command-line
interface. It is **not** a serial-only firmware — the operator works directly on the device with a blinking
cursor, command history, tab-autocomplete, and on-device man pages (§9).

Feature set (per upstream, §9): WiFi scan / connect / monitor mode / **deauth**, **Evil Twin AP** with
adaptive deauth + captive portal, hidden-SSID reveal, WPA2 handshake capture with on-device cracking, MAC
spoofing, WPS detection, **beacon flood** injection, and a passive **WiFi IDS** (`wguard`) that watches for
deauth floods/evil twins/karma. Network recon adds ARP host discovery, parallel TCP port scanning, ICMP
ping, banner grabbing, and OS fingerprinting. Bluetooth/BLE covers scanning with RSSI, **GATT enumeration**
(`bi`), a passive advertisement sniffer with PCAP export, a tracker-detector (`tm` — AirTag/Tile/SmartTag
signatures), Fast Pair attacks, and BLE HID. USB gadget modes include mass storage (`um`), USB keyboard/mouse
(`uk`), **BadUSB** (`ux`, DuckyScript v1), and a mouse jiggler (`jg`). T-Deck Plus additionally has GPS.

Cyber Controller's role is the **toolchain side**: it flashes the correct per-board `.bin` and gives you a
serial terminal/console to the device. The offensive operation itself is driven from the T-Deck's own
keyboard and CLI.

## 2. Legal & Safety
**Authorized testing only.** Deauthentication, Evil Twin / captive-portal AP, beacon flood, BLE spam/Fast
Pair, and **BadUSB** keystroke injection are **restricted** techniques — using them against networks,
devices, or people you do not own or lack **written** permission to test is illegal in most jurisdictions
(US: CFAA/FCC; EU and others similar). Passive scanning, sniffing, and IDS may still be regulated where you
live — check local law. BadUSB (`ux`) executes arbitrary keystrokes on whatever host you plug into; treat it
like a loaded tool. Cyber Controller flags restricted firmware as dangerous and (unless you disable warnings)
confirms before issuing risky operations. Use only on your own lab gear or under an explicit engagement scope.

## 3. Hardware & Purchasing
T-REX runs **only** on the two LilyGo boards below (both ESP32-S3, 16 MB flash, 8 MB PSRAM). Pick by whether
you need GPS and a ready-to-carry unit:

| Board | Chip / memory | Display + input | Extras | Best for | Where to buy (search terms) |
|-------|---------------|-----------------|--------|----------|------------------------------|
| **LilyGo T-Deck** | ESP32-S3FN16R8, 16 MB flash / 8 MB PSRAM | 2.8" **ST7789** 320×240 (no touch) + QWERTY keyboard (I²C) + trackball | LoRa SX1262 (option), USB-C, microSD; **bring-your-own LiPo**, no case | Cheapest entry, bench/lab use | **LilyGo store**: "T-Deck" (lilygo.cc/products/t-deck); AliExpress: "LILYGO T-Deck ESP32-S3" |
| **LilyGo T-Deck Plus** | ESP32-S3FN16R8, 16 MB flash / 8 MB PSRAM | same display + QWERTY keyboard + trackball | **GPS** (u-blox MIA-M10Q — *verify exact GNSS model on your revision*), LoRa SX1262, **2000 mAh battery + enclosure** included | Field/wardriving, carry-ready | **LilyGo store**: "T-Deck Plus" (lilygo.cc/products/t-deck-plus-1); AliExpress: "LILYGO T-Deck Plus GPS" |

**T-Deck vs T-Deck Plus (the difference that matters for flashing):** the Plus adds a **GPS module**, a
**battery**, and a **case**; the base T-Deck is more of a dev kit (you supply the LiPo, LoRa is an optional
add-on). On the Plus the Grove pins are reserved for GPS. Because GPS support differs, **T-REX ships a
separate firmware binary per board** — you must flash the one that matches your hardware (§5).

**Indicative pricing (verify at purchase — vendor links/prices change, §9):** T-Deck ≈ US$43+, T-Deck Plus
≈ US$70.

**Accessories:** a quality **USB-C data cable** (not charge-only — native USB on the S3 needs data lines),
a **microSD** (FAT32) for capture/PCAP/handshake logging and BadUSB payloads, and for the base T-Deck a
**3.7 V LiPo** if you want it portable. Buy direct from **LilyGo** or the **LILYGO official AliExpress
store** to avoid clones with the wrong flash size — verify **16 MB flash / 8 MB PSRAM**.

## 4. Building / Assembly
You do **not** need to compile to use T-REX — flash the prebuilt release binary via Cyber Controller (§5).
Build from source only if you want to modify it.

- **Pre-built boards:** both T-Deck variants ship assembled. The base T-Deck may need a LiPo connected for
  untethered use; the Plus comes with battery + case. No soldering for stock use.
- **Drivers:** the ESP32-S3 uses **native USB** (USB-CDC), so on Windows 10/11, modern Linux, and macOS a
  COM/tty port usually appears with no driver install. If no port shows, see §8.
- **Build from source (optional):** install **VS Code + PlatformIO**, then
  `git clone https://github.com/abdallahnatsheh/T-REX-FIRMWARE`, open the folder, select the PlatformIO
  environment **`env:T-Deck`** or **`env:T-Deck-Plus`** to match your board, and click **Upload**.
  Dependencies (LovyanGFX, NimBLE-Arduino, RadioLib, TinyGPS++, ArduinoJson, TouchLib, etc.) install
  automatically via `lib_deps`. License is **AGPL-3.0** (derivatives must be shared alike).

## 5. Flashing & First Run (via Cyber Controller)
1. Connect the T-Deck by USB-C; open Cyber Controller → **Flash** tab.
2. **Port:** pick the board's COM/tty (click *Refresh* if missing → see §8). The ESP32-S3 enumerates as a
   native USB serial device.
3. **Firmware Profile:** `t-rex`.
4. **Board / variant:** select **T-Deck** *or* **T-Deck Plus** to match your hardware. This choice picks the
   correct release asset — `T-Rex-...-TDeck.bin` vs `T-Rex-...-TDeck-Plus.bin` (the Plus build includes GPS).
   Flashing the wrong one leaves GPS non-functional or features mismatched.
5. Click **Flash.** Cyber Controller targets the **ESP32-S3**, fetches the latest GitHub release, and writes
   the **single merged `.bin` at offset `0x0`** (flash mode `qio`, freq `80 MHz`, baud 115200). No separate
   bootloader/partition files are needed — it is a web-flasher-class single image.
6. **First boot:** the T-REX CLI appears on the display with a prompt. Recommended setup commands (run on the
   T-Deck keyboard): `sdf init` (create SD directory structure if a card is present), `tz` (timezone),
   `psv` (power save), and optionally `lock new` (set a SHA-256 PIN lock). Type `man <cmd>` or `help` for
   on-device documentation.

> **Note (per profile, §9):** the `0x0` merged-bin layout is the documented upstream esptool target
> (`esptool --chip esp32s3 --port <PORT> write_flash 0x0 <T-Rex...bin>`). If a future release changes the
> image model, **verify** the offset against the release notes before manual flashing — Cyber Controller
> tracks this in the profile.

## 6. Integrate into Cyber Controller
- **Profile:** `t-rex` (file `src/config/profiles/trex.json`, id `trex`). Backend **esptool**; resolver
  **github_release** (latest) matching a `.bin` asset; chip fixed to **esp32s3**; image **merged single bin
  @ `0x0`**; default baud **115200**. Two boards are defined (T-Deck, T-Deck Plus), both ESP32-S3 / 16 MB /
  `qio` / `80m`.
- **Control:** open the **Devices** tab → select the port → set **Firmware = T-REX** → **Connect.** Because
  the profile's `protocol` is **null**, Cyber Controller treats T-REX as a **raw serial CLI terminal**: you
  see and type its on-device commands directly, but there is **no protocol-aware parser**, so scan results
  are **not** auto-imported into the shared Targets pool — targeting is managed on the T-Deck itself.
- **Command set:** drive it through the persistent terminal using T-REX's own verbs, e.g. `scanwifi`/`sw`,
  `connectwifi`/`cw`, `beaconflood`/`bf`, `wguard`/`wg`, `bleinfo`/`bi`, `trackme`/`tm`, `fastpair`/`fp`,
  `usbkbd`/`uk`, `usbexec`/`ux` (BadUSB). The T-Deck keyboard works in parallel with the terminal.
- **Suicide / Dead Man's Switch:** **not supported** for this profile (`supports_suicide: false`).
- **Backup first:** use **Backup** in the Flash tab to dump the current flash before overwriting (e.g. if the
  board currently runs Meshtastic or stock firmware).

## 7. Usage (end-to-end)
1. **Connect & verify:** Devices tab → Connect → type `help` (or watch the display); confirm the prompt
   responds. On the Plus, GPS fix status is reported once it locks.
2. **WiFi scan:** `scanwifi` (`sw`) lists nearby APs; page with `l`/`a`, rescan with `u`, quit with `q`.
3. **Recon a host:** join a network with `connectwifi` (`cw`), then run ARP discovery / TCP port scan /
   banner grab from the network menu to enumerate hosts and services.
4. **Authorized offensive ops (scope required):** Evil Twin + captive portal, deauth, or `beaconflood`
   against **your own** lab SSIDs; capture WPA2 handshakes and crack on-device. Cyber Controller confirms
   restricted actions first.
5. **BLE work:** `bleinfo` (`bi`) to enumerate a device's GATT tree; the passive BLE ad sniffer exports
   **PCAP to SD** for Wireshark; `trackme` (`tm`) for passive tracker surveillance.
6. **USB attacks/utilities:** `usbexec` (`ux`) runs a DuckyScript v1 payload from SD (BadUSB); `usbkbd`
   (`uk`) turns the device into a USB HID keyboard/mouse; `um` exposes the SD as a USB drive.
7. **Logging & exit:** results/PCAPs/handshakes write to microSD; stop the active operation on-device, then
   **Disconnect** in Cyber Controller to free the port.

## 8. Troubleshooting
- **No COM/tty port:** use a **data** USB-C cable (not charge-only); try another port; on Linux add your user
  to `dialout` and replug. The S3 uses native USB-CDC — the port disappears while the device reboots.
- **Flash fails / "Failed to connect":** force **download mode** — **hold the trackball button down, plug in
  USB, then start the flash** (this is T-REX's documented recovery for the ESP32-S3). Lower the flash baud in
  Settings and close any serial monitor holding the port.
- **GPS not working on T-Deck Plus:** confirm you flashed the **`-TDeck-Plus`** binary (select *T-Deck Plus*
  in the Flash tab), and allow time outdoors for first fix.
- **Wrong board features / blank-ish behavior:** re-flash selecting the exact board variant; a base-T-Deck
  binary on a Plus (or vice-versa) mismatches GPS/peripherals.
- **SD warnings:** a yellow lock-screen indicator flags a missing SD; per upstream, recovery may require
  removing the SD and rebooting. Run `sdf init` to (re)create the directory structure.
- **Boot-loop / bad flash:** **Erase Flash** in the Flash tab, then re-flash the latest release; verify the
  board is genuinely **16 MB** flash (clones may report wrong sizes).
- **Forgot PIN lock:** the lock uses a SHA-256 hash; recovery generally means re-flashing — *verify* current
  upstream guidance before assuming data is recoverable.

## 9. Sources
- Upstream firmware: <https://github.com/abdallahnatsheh/T-REX-FIRMWARE> (README, feature list, build via
  PlatformIO `env:T-Deck`/`env:T-Deck-Plus`, AGPL-3.0) and its **Releases** page (per-board `.bin`,
  `esptool ... write_flash 0x0`, trackball download-mode).
- Hardware: LilyGo T-Deck wiki <https://wiki.lilygo.cc/products/t-deck-series/t-deck/> (ESP32-S3FN16R8,
  16 MB/8 MB, 2.8" ST7789 320×240, I²C keyboard + trackball, SX1262 LoRa, GNSS on Plus, 2000 mAh, USB-C,
  microSD) and store pages <https://lilygo.cc/products/t-deck> / <https://lilygo.cc/products/t-deck-plus-1>.
- Pricing / T-Deck vs Plus differences: Liliputing and CNX-Software T-Deck Plus coverage (≈US$43 base /
  ≈US$70 Plus; Plus adds GPS, battery, case). **Verify current prices and exact GNSS model at purchase** —
  vendor links and revisions change.
- Cyber Controller profile: `src/config/profiles/trex.json` (id `trex`, esptool, esp32s3, merged `.bin`
  @ `0x0`, baud 115200, boards T-Deck / T-Deck Plus, `protocol: null`, `supports_suicide: false`).
