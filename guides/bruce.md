# Bruce — Complete Hardware Guide

> **Firmware:** Bruce · **Upstream:** [BruceDevices/firmware](https://github.com/BruceDevices/firmware) (formerly [pr3y/Bruce](https://github.com/pr3y/Bruce), AGPL-3.0)
> **Chips:** ESP32, ESP32-S3, ESP32-C5, ESP32-C6 · **Cyber Controller profile:** `bruce` (esptool backend, merged single-bin flashed @ `0x0`, no suicide)
> **This guide:** purchase → build → flash → integrate into Cyber Controller → use → troubleshoot.

## 1. Overview
Bruce is a "predatory"/multi-tool ESP32 pentest firmware built for red-team work — it bundles most offensive
radios into one menu-driven device UI: **WiFi** (scan, AP, deauth, beacon/probe spam, evil portal, wardrive),
**BLE** (scan, spam, HID keyboard, BadBLE Ducky), **RF / SubGHz 433 MHz** (scan, spectrum, replay, jam — via
a CC1101 module), **IR** (TV-B-Gone, capture/replay), **RFID/NFC** (read/clone/emulate — via a PN532),
**BadUSB** (Ducky HID from LittleFS or SD), **FM radio**, **NRF24** (jammer/Mousejack), plus iButton, GPS, and
a small JavaScript interpreter for scripts. Unlike serial-CLI firmwares, Bruce is primarily driven from the
device's own screen + buttons/keyboard. Cyber Controller flashes the correct per-board image, opens a serial
session through the **Devices** tab, and folds Bruce's output into the shared target pool for cross-device work.

## 2. Legal & Safety
**Authorized testing only.** WiFi deauth/beacon spam, BLE spam, SubGHz replay/jam, NRF24 jamming, and IR/FM
transmit are **illegal against devices, networks, vehicles, or people you do not own or have written
permission to test** in most jurisdictions (US: CFAA/FCC Part 15; EU and others similar). RF/SubGHz replay of
garage/gate/car remotes and FM/traffic-announcement hijack are specifically regulated. Cyber Controller flags
these as dangerous and (unless you disable warnings) confirms before sending. Passive scanning/sniffing may
still be regulated where you live — check local law. Use only on lab gear or under an explicit engagement scope.

## 3. Hardware & Purchasing
Bruce ships pre-compiled images for **49+ board variants**; the profile exposes the common ones. Pick by how
you'll use it — note that **SubGHz/RF, NFC, and some IR features need an external module** (built into a few
boards, add-on on the rest):

| Tier | Board (chip) | Why | Where to buy (search terms) |
|------|--------------|-----|------------------------------|
| Best all-in-one | **LilyGo T-Embed CC1101** (ESP32-S3, 16MB) | CC1101 **built in** → SubGHz out of the box; encoder UI, battery | **LilyGo** store / AliExpress: "LilyGo T-Embed CC1101" |
| Pocket keyboard | **M5Cardputer** (ESP32-S3, 8MB) | Full keyboard + screen, the flagship Bruce device for BadUSB/scripts | **M5Stack** store / Amazon: "M5Cardputer" |
| Tiny EDC | **M5StickC Plus2** (ESP32, 4MB) | Cheap, pocketable, huge community; add modules via Grove | **M5Stack** store / Amazon: "M5StickC Plus2" |
| Big-screen handheld | **LilyGo T-Deck / T-Deck Plus** (ESP32-S3, 16MB) | QWERTY + trackball + large display | **LilyGo** store: "LilyGo T-Deck" |
| Stealth dongle | **LilyGo T-Dongle-S3** (ESP32-S3, 16MB) | USB-stick form factor, good for BadUSB | **LilyGo** store: "LilyGo T-Dongle-S3" |
| Cheap + screen | **CYD "Cheap Yellow Display" CYD-2432S028** (ESP32, 4MB, ILI9341) | ~US$10–15 starter; touch UI | AliExpress/Amazon: "ESP32-2432S028R CYD 2.8" |
| M5 Core family | **M5Core2 / CoreS3 / Core Basic** | Larger screen, stackable M5 modules | **M5Stack** store: "M5Core2", "M5CoreS3" |
| Bare / serial | Any **ESP32-WROOM DevKit** (ESP32, 4MB) | Cheapest; no screen → operate features that don't need UI | AliExpress/Amazon: "ESP32 DevKit V1" |
| Newer radios | **ESP32-C5 / ESP32-C6 DevKitC** | C5 adds 5 GHz; C6 newer Wi-Fi 6 silicon | Espressif/Waveshare: "ESP32-C5-DevKitC-1", "ESP32-C6-DevKitC-1" |

**External modules (the part most people miss):**
- **CC1101** (433/315/868/915 MHz) → required for **all SubGHz/RF**. Built into T-Embed CC1101 and the "RF
  Reaper" build; an add-on (SPI wiring) on Cardputer/StickC/CYD.
- **PN532** (or PN532Killer) → required for **13.56 MHz NFC + 125 kHz RFID** read/clone/emulate.
- **NRF24L01** → for the **jammer / Mousejack / 2.4 GHz spectrum** features.
- **IR LED + receiver** → many boards have a weak built-in IR LED; an external high-power LED greatly extends range.
- Get modules from AliExpress/Amazon: "CC1101 433MHz module", "PN532 NFC module", "NRF24L01+PA+LNA".

**Accessories:** a quality **USB-C/micro-USB data cable** (not charge-only), a **microSD** (FAT32) for BadUSB
payloads / RF & NFC dumps / captures, and an optional **GPS module** (NMEA) for wardriving. Buy preloaded/
known-good hardware from resellers like **M5Shark** if you'd rather not flash yourself. **Avoid** clone ESP32s
with the wrong flash size — verify 4 MB+ (S3 boards are 8–16 MB).

## 4. Building / Assembly
- **Pre-built boards (M5 Cardputer/StickC/Core, LilyGo T-Embed/T-Deck/T-Dongle, CYD):** no assembly — just a
  data cable. The T-Embed CC1101 is the only one with SubGHz ready to go.
- **Adding modules (DIY):** wire CC1101 / PN532 / NRF24 to the board's SPI/I²C pins per the upstream wiki's
  wiring diagrams ([§9](#9-sources)); on M5StickC use a Grove/HAT breakout. Pin maps differ per board — *verify:
  exact pinout for your board on wiki.bruce.computer before soldering.*
- **Drivers:** install the USB-serial driver for your board's chip — **CP210x** (M5Stack, most DevKits),
  **CH340** (cheap clones/CYD variants), or native USB (S3/C5/C6, no driver). Without it, no COM port appears.
- **Per-board gotchas:** CYD comes in display variants — Bruce ships a **`LITE_VERSION`** of the CYD build for
  launcher compatibility, and the screen stays blank if you flash the wrong variant. Cardputer vs Cardputer
  ADV are different builds. ESP32-C5/C6 are newer ports — *verify current C6 board builds exist for your exact
  board in the latest release ([§9](#9-sources)).*

## 5. Flashing & First Run (via Cyber Controller)

![Flashing connection diagram](../assets/connect-esptool-usb.png)

*How to connect the board to flash it via Cyber Controller (native-USB ESP32).*

1. Connect the board by USB; open Cyber Controller → **Flash** tab.
2. **Port:** pick the board's COM/tty (click *Refresh* if missing → driver issue).
3. **Firmware Profile:** `Bruce`.
4. **Board / variant:** choose your exact board (e.g. *M5Cardputer*, *T-Embed CC1101*, *CYD-2432S028*,
   *M5StickC Plus2*). Cyber Controller resolves the matching `Bruce-<env>.bin` asset from the latest GitHub
   release and derives the chip family from the env name. If two assets match, prefer the **standalone** build
   over any labelled **`[LAUNCHER loader]`** (those are multi-boot loader images, not the full firmware).
5. Click **Flash**. Bruce is a **merged single-bin** written at offset **`0x0`** (no separate bootloader/
   partition files), so flashing is one write. First boot shows the Bruce menu on screen (radios across the
   top, categories down the list) or a serial banner on screenless boards.

*If "Failed to connect":* put the board in download mode first — **Cardputer:** hold **G0** while powering on,
then release; **StickC Plus2:** hold the **center (M5) button** and tap **RST**; **T-Embed CC1101:** hold the
**encoder center** and tap **RST** (button is beside the ESP32-S3 chip). Generic DevKits: hold **BOOT** during
connect.

## 6. Integrate into Cyber Controller
- **Profile:** `bruce` (esptool backend). **Merged single-bin:** one `Bruce-<env>.bin` at `app_offset 0x0`,
  `support_files: null` — there is no multi-file offset map (this is the key difference from Marauder).
- **Resolver:** `github_release` against `BruceDevices/firmware` *releases/latest*; assets match
  `^Bruce-(LAUNCHER_)?(.+)\.bin$` and the chip is mapped from the env-name fragment (e.g. `cardputer`/`-s3` →
  esp32s3, `-c5` → esp32c5, `-c6` → esp32c6). Default variant strategy is **prefer-non-launcher**.
- **Control:** open the **Devices** tab → select the port → set **Firmware = Bruce** (Pro mode; Simple mode
  auto-uses it) → **Connect** at **115200** baud. The protocol-aware `bruce` parser reads device output, the
  persistent terminal colorizes per device, and discovered APs/clients/targets populate the **Targets** pool.
- **Cross-Comm:** scans feed `target.added` events; auto-routing rules can fire a follow-up command on another
  connected device (e.g. a Marauder).
- **No suicide:** this profile is **`supports_suicide: false`** — there is no self-erase/Dead Man's Switch
  destruct for Bruce (unlike Marauder). Use **Erase Flash** in the Flash tab if you need to wipe it.
- **Backup first:** use **Backup** in the Flash tab to dump current flash before overwriting.

## 7. Usage (end-to-end)
Bruce is **menu-driven on the device** — Cyber Controller handles flashing, the serial terminal, logging, and
cross-device coordination, while you drive the radios from the on-screen menu (D-pad/encoder/keyboard).
1. **Navigate:** from the home menu pick a category — **WiFi**, **BLE**, **RF**, **RFID**, **IR**, **FM**,
   **Others** (NRF24/iButton/GPS), or **Scripts** (JS).
2. **WiFi:** *Scan* APs → they appear in Cyber Controller **Targets**; choose *Evil Portal*, *Beacon Spam*, or
   *Deauth* against an **authorized** target. With SD inserted, captures/handshakes are logged.
3. **RF / SubGHz:** (needs CC1101) *Scan/Read* a 433 MHz signal → *Save* → *Replay/Transmit* only on gear you own.
4. **NFC/RFID:** (needs PN532) *Read* a tag → *Save/Clone* → *Emulate* (Chameleon-style).
5. **BadUSB:** put a Ducky script on SD/LittleFS → run it on a connected host (authorized).
6. **IR / FM:** TV-B-Gone, capture/replay IR, or FM broadcast/spectrum.
7. **Stop / disconnect:** exit the running mode on-device; **Disconnect** in Cyber Controller to free the port.

## 8. Troubleshooting
- **No COM port:** install CP210x/CH340 driver; try another (data) cable; on Linux run
  `sudo setfacl -m u::rw /dev/ttyACM0` (or add your user to `dialout`) and replug.
- **Flash fails / "Failed to connect":** enter download mode for your board (see [§5](#5-flashing--first-run-via-cyber-controller)),
  lower the flash baud in Settings, and close any serial monitor holding the port.
- **Blank screen after flash:** wrong board variant (esp. CYD display variants / Cardputer vs ADV) — re-flash
  selecting the exact board; for CYD try the `LITE_VERSION` build.
- **SubGHz/NFC menu present but "no module"/nothing happens:** the CC1101 / PN532 isn't wired or detected —
  recheck SPI/I²C pins against the wiki pinout; confirm the board actually has the module (only T-Embed CC1101
  / RF Reaper ship CC1101 built in).
- **Boot-loops / brick:** **Erase Flash** then re-flash; verify the board is genuinely 4 MB+ (S3 8–16 MB).
- **Verify failed:** re-run flash with verify on; a bad cable or clone flash chip is the usual cause.
- **C5/C6 board not listed or won't boot:** these are newer ports — *verify a current release asset exists for
  your exact board ([§9](#9-sources));* pick the closest matching env.

## 9. Sources
- Upstream: <https://github.com/BruceDevices/firmware> (README, releases, wiki) — formerly <https://github.com/pr3y/Bruce>.
- Docs/wiki: <https://wiki.bruce.computer/> (How-to-Install, wiring diagrams, features) and the GitHub
  [Installing wiki](https://github.com/BruceDevices/firmware/wiki/Installing).
- Web flasher (alternative to Cyber Controller): <https://bruce.computer/flasher>; M5 devices also via **M5Burner**/**M5Launcher** (search "Bruce").
- Cyber Controller profile: `src/config/profiles/bruce.json` (boards, chips, merged `0x0` image, resolver/regex).
- Hardware: M5Stack (Cardputer, StickC Plus2, Core2/CoreS3), LilyGo (T-Embed CC1101, T-Deck, T-Dongle-S3), CYD
  (ESP32-2432S028), Espressif/Waveshare (C5/C6 DevKitC); modules CC1101 / PN532 / NRF24L01 from AliExpress/Amazon.
- Verify current board availability, release assets, prices, and module pinouts at purchase/flash time; vendor links and builds change.
