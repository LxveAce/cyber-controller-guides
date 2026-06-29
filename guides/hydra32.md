# Hydra32 (ESP32-Deauther) — Complete Hardware Guide

> **Firmware:** Hydra32 / HydraESP (ESP32-Deauther) · **Upstream:** [SameerAlSahab/ESP32-Deauther](https://github.com/SameerAlSahab/ESP32-Deauther) (GPL-3.0)
> **Chip:** ESP32 (Xtensa LX6) on the **ESP32 DevKit V1** board · **Cyber Controller profile:** `hydra32` (esptool backend, multi-file offsets, pinned + SHA-256-verified release)
> **This guide:** purchase → build → flash → integrate into Cyber Controller → use → troubleshoot.

## 1. Overview
Hydra32 (the project also calls itself **HydraESP**; the pinned release is tagged **`Hydra32`** and ships the
app as `projecthydra-32.bin`) is a WiFi/Bluetooth security-research firmware for the classic dual-core
**ESP32-WROOM-32**. It is an ESP32-Deauther variant that bundles WiFi reconnaissance and 802.11
deauthentication with a browser-based control panel served from on-device SPIFFS storage. Documented
capabilities include **WiFi scanning**, **deauthentication** (up to 16 simultaneous targets), **WPA
handshake capture** (`.pcap` / `.hccapx`), **PMKID capture**, **beacon spam**, **Ghost Mode** (probe-request
SSID echo), **Evil Twin** (open clone + captive-portal password capture), **BLE spam** (Apple/Samsung/Google
proximity advertisements), and a defensive **deauth detector**. An optional SSD1306 OLED shows live status.
Cyber Controller's role is narrow and honest: it flashes the **pinned, SHA-256-verified** release images at
the correct offsets and exposes the device on the **Devices** tab — it adds no attack capability of its own.
(Feature names and version: §9.)

## 2. Legal & Safety
**Authorized testing only.** Deauthentication, beacon spam, Evil Twin, and BLE spam actively transmit on
the 2.4 GHz band and are **illegal against networks, devices, or people you do not own or have explicit
written permission to test** in most jurisdictions (US: CFAA + FCC rules against willful RF interference;
the EU and many others have equivalent statutes). Deauthentication is jamming-by-protocol: it knocks real
clients off real networks, so unauthorized use is not a grey area. Use Hydra32 **only** on your own lab gear
or under a signed engagement scope. Even passive WiFi scanning/sniffing and the captive-portal credential
capture in Evil Twin can be regulated where you live — check local law first. Cyber Controller surfaces the
firmware's lawful-use notice and treats transmit features as dangerous; the tool does not remove your
responsibility for what you transmit. Upstream states plainly: *"Use it only on networks and devices you own
or have received explicit written authorisation to test."* (§9)

## 3. Hardware & Purchasing
Hydra32 targets **one board** in the Cyber Controller profile: the **ESP32 DevKit V1** (the DOIT/"NodeMCU-32"
style 30-pin board built around the **ESP32-WROOM-32** module). Upstream notes other plain ESP32 modules
(ESP32-WROOM-32, ESP32-WROVER) are *expected* to work, but **ESP32-S2 / S3 / C3 are not supported** — this is
LX6-ESP32-only firmware. Buy the matching board:

| Part | Why this one | Where to buy (search terms) |
|------|--------------|------------------------------|
| **ESP32 DevKit V1** (ESP32-WROOM-32, 30-pin, 4 MB flash) | The profile's only board; cheap, serial-flash friendly, BOOT/EN buttons | AliExpress/Amazon: **"ESP32 DevKit V1"** or **"DOIT ESP32 DEVKIT V1"**; distributors: **Mouser / DigiKey** search "ESP32-DevKitC" / "ESP32-WROOM-32" |
| **USB data cable** (Micro-USB, *data* not charge-only) | DevKit V1 uses Micro-USB; charge-only cables show no COM port | Any electronics vendor: **"micro USB data cable"** |
| **SSD1306 OLED 128×64 I²C** *(optional)* | On-device live status/logs without the web UI | AliExpress/Amazon: **"SSD1306 0.96 OLED I2C 128x64"** |
| **Dupont jumper wires** *(optional, for OLED)* | Wire the OLED to the I²C pins | **"dupont jumper wires female-female"** |

**Board-buying notes**
- **Verify 4 MB flash.** The profile flashes a SPIFFS storage image at **`0x190000`** and assumes a 4 MB part
  (the upstream `partitions.csv` for the `devkit-v1` branch lays the storage partition there). A 2 MB clone
  will not fit the layout. If unsure, *verify:* check the WROOM-32 module marking or read flash size with
  `esptool flash_id`.
- **USB-serial chip varies by clone.** Genuine/most DOIT DevKit V1 boards use the **Silicon Labs CP2102**
  (CP210x driver); cheaper clones use a **WCH CH340**. You need the matching driver (see §4). *Verify:* read
  the chip marking next to the USB port.
- No invented part numbers or shop URLs here — search the terms above with your preferred vendor and confirm
  price/stock at purchase time (§9).

## 4. Building / Assembly
There is **nothing to solder** for the base setup — the DevKit V1 is a finished board; you only need a data
cable. Assembly/setup work is drivers, the optional OLED, and (if you don't use the pinned release) building
from source.

**USB-serial driver (required to get a COM port)**
- **CP2102 boards:** install the **Silicon Labs CP210x VCP** driver.
- **CH340 boards:** install the **WCH CH340** driver.
- Without the right driver, no COM/tty port appears and flashing cannot start (§8).

**Optional OLED wiring (SSD1306, I²C)**
- The DevKit V1's default hardware I²C pins are **GPIO21 = SDA** and **GPIO22 = SCL**, with **3V3** and **GND**
  for power. Wire OLED `VCC→3V3`, `GND→GND`, `SDA→GPIO21`, `SCL→GPIO22`.
- *Verify:* confirm the exact SDA/SCL GPIOs (and the OLED I²C address, usually `0x3C`) against the Hydra32
  source/README for your release before relying on them — upstream did not publish a fixed pinout table at the
  time of writing (§9).

**Building from source (only if not using Cyber Controller's pinned release)**
- Hydra32 is an **ESP-IDF** project (CMake-based). Standard flow: install ESP-IDF, then
  `idf.py set-target esp32` → `idf.py build` → `idf.py -p <PORT> flash`. *Verify* the exact ESP-IDF version
  in the repo before building; IDF major versions are not always interchangeable (§9).
- For normal use you do **not** build anything — Cyber Controller fetches the prebuilt, hash-pinned release.

## 5. Flashing & First Run (via Cyber Controller)

![Flashing connection diagram](../assets/connect-esptool-boot.png)

*How to connect the board to flash it (classic ESP32 — BOOT/EN download mode).*

1. Connect the DevKit V1 by Micro-USB; open Cyber Controller → **Flash** tab.
2. **Port:** pick the board's COM/tty (click *Refresh* if missing → driver/cable issue, see §8).
3. **Firmware Profile:** `Hydra32 (ESP32-Deauther)` (profile id `hydra32`).
4. **Board:** **ESP32 DevKit V1** (`esp32` chip; the profile's only board). Flash params are fixed by the
   profile: **4 MB**, flash mode **dio**, flash freq **80m**, default baud **921600**.
5. Click **Flash.** Cyber Controller resolves the pinned **`Hydra32`** release, **verifies each file's
   SHA-256**, and writes the multi-file image at the upstream offsets:
   - `bootloader.bin` → **`0x1000`**
   - `partition-table.bin` → **`0x8000`**
   - `projecthydra-32.bin` (app) → **`0x10000`**
   - `storage.bin` (SPIFFS web UI) → **`0x190000`**
   This is a **single-factory** layout — there is **no `boot_app0`** file (the profile sets
   `include_boot_app0: false`).
6. **First run:** after flashing, the ESP32 boots and starts its own management access point. From a phone or
   laptop, join the Hydra32 AP and browse to **`http://192.168.4.1`** to reach the web UI (tabs: **Scan,
   Attack, Detector, Settings, About**). The default AP credentials are reported as SSID **`hydra`** /
   password **`notforfun`** — *verify per release*, as defaults can change between versions (§9). With an OLED
   attached, status also appears on the screen.

> **Tip:** if the board won't enter download mode automatically, hold **BOOT (IO0)** while the flash starts,
> or tap **EN** then start the flash. See §8.

## 6. Integrate into Cyber Controller
- **Profile:** `hydra32` — backend **esptool**, chip **esp32**, board **ESP32 DevKit V1**. Image model is
  **multi-file-offsets** with a **pinned-release** resolver (release tag **`Hydra32`**). Every asset
  (`bootloader.bin`, `partition-table.bin`, `storage.bin`, and the `projecthydra-32.bin` app) is
  **SHA-256-pinned and verified at flash time, never vendored** — if a download's hash doesn't match, the
  flash aborts.
- **Control:** open the **Devices** tab → select the DevKit V1's port → set **Firmware = Hydra32
  (ESP32-Deauther)** → **Connect**. The serial terminal is persistent and per-device colorized.
- **Primary UI is the web panel.** Unlike CLI-first firmwares, Hydra32 is driven through its browser UI at
  `192.168.4.1`; the Devices tab is for the serial console, boot/diagnostic output, and reconnects. Use
  whichever the firmware exposes for a given action.
- **Suicide / self-erase:** the profile sets `supports_suicide: false` — there is **no** firmware
  self-destruct for Hydra32. To wipe it, use **Erase Flash** in the Flash tab.
- **Backup first:** before overwriting an existing board, use **Backup** in the Flash tab to dump current
  flash.

## 7. Usage (end-to-end)
All steps below assume **authorized targets only** (§2).
1. **Power & connect:** plug the DevKit V1 into USB or a 5 V source; join its AP and open
   **`http://192.168.4.1`**.
2. **Scan:** **Scan** tab → list nearby APs (SSID, BSSID, signal). Pick your authorized target.
3. **Attack:** **Attack** tab → choose a mode:
   - **Deauth** — disconnect clients from the selected AP (up to 16 targets).
   - **Beacon spam** — flood fake beacons to test detection/visibility.
   - **Handshake / PMKID capture** — force re-auth and capture `.pcap` / `.hccapx`, or pull a PMKID without a
     connected client.
   - **Ghost Mode** — echo probe-request SSIDs.
   - **Evil Twin** — open clone of the AP with a captive portal that prompts for the password (captured
     credentials show in the UI/OLED).
   - **BLE spam** — broadcast Apple/Samsung/Google proximity ads.
4. **Timed operations:** set an attack duration so it auto-stops (Settings/Attack controls).
5. **Detector (defensive):** **Detector** tab → puts the radio in promiscuous monitor mode and alerts when
   **>10 deauth frames from one BSSID within 1 second** are seen; results show in a live log table.
6. **Settings/About:** channel and operational options live under **Settings**; **About** shows version.
7. **Stop & disconnect:** stop the active attack in the web UI; in Cyber Controller, **Disconnect** to free
   the serial port.

## 8. Troubleshooting
- **No COM port:** install the correct USB-serial driver — **CP210x (Silicon Labs)** for CP2102 boards or
  **CH340 (WCH)** for clones; swap in a **data** USB cable (charge-only cables are the #1 cause); on Linux add
  your user to `dialout` and replug.
- **Flash fails / "Failed to connect":** hold **BOOT (IO0)** while the flash starts (or tap **EN** then
  start); close any serial monitor holding the port; lower the flash baud in Settings (esptool can fall back
  to very slow rates to prove it isn't a baud problem).
- **SHA-256 / download mismatch:** the pinned release didn't verify — retry (transient download), confirm
  network access to GitHub releases, and don't substitute hand-downloaded bins; the profile intentionally
  refuses unverified files.
- **Web UI won't load at 192.168.4.1:** confirm you joined the Hydra32 AP (not your home WiFi); some phones
  auto-switch back to a known network with internet — disable "auto-switch"/"smart network switch." *Verify*
  the AP SSID/password for your release (§9).
- **Storage/UI assets missing or blank page:** `storage.bin` (SPIFFS) didn't write — re-flash; ensure the
  board is genuinely **4 MB** (a smaller flash can't hold the `0x190000` storage partition).
- **Boot-loops / brick:** **Erase Flash** then re-flash the pinned release; verify the WROOM-32 is real
  (`esptool flash_id` to confirm 4 MB).
- **OLED blank:** check `VCC/GND/SDA(GPIO21)/SCL(GPIO22)` wiring and the I²C address; *verify* the pins/address
  against your release's source (§9).
- **Wrong chip:** this firmware is **ESP32 (LX6) only** — an ESP32-S2/S3/C3 board will not run it.

## 9. Sources
- Upstream repo (README, features, releases): <https://github.com/SameerAlSahab/ESP32-Deauther> (GPL-3.0).
- Releases / pinned `Hydra32` tag, assets, and offsets: <https://github.com/SameerAlSahab/ESP32-Deauther/releases>
  (`bootloader.bin`@`0x1000`, `partition-table.bin`@`0x8000`, `projecthydra-32.bin`@`0x10000`,
  `storage.bin`@`0x190000`; latest reported V1.1.3).
- Project site: <https://sameeralsahab.github.io/ESP32-Deauther/>.
- Cyber Controller profile: `src/config/profiles/hydra32.json` (board, chip, esptool offsets, SHA-256 pins,
  flash params, `supports_suicide: false`).
- Board specs (ESP32-WROOM-32, 4 MB, CP2102, Micro-USB, BOOT/EN): DOIT ESP32 DevKit V1 references
  (espboards.dev, Mischianti, Last Minute Engineers) and the Espressif ESP32-WROOM-32 datasheet.
- Drivers: Silicon Labs CP210x VCP; WCH CH340. Flashing/boot-mode troubleshooting: Espressif esptool docs;
  Random Nerd Tutorials ESP32 troubleshooting.
- **Verify at use time:** AP SSID/password defaults, OLED pinout/address, ESP-IDF build version, and current
  board prices/stock — these can change between firmware releases and vendors.
