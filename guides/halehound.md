# HaleHound — Complete Hardware Guide

> **Firmware:** HaleHound (CYD edition) · **Upstream:** [JesseCHale/HaleHound-CYD](https://github.com/JesseCHale/HaleHound-CYD) (license: verify in repo)
> **Chips:** ESP32 (classic ESP32-WROOM-32 on every supported CYD board) · **Cyber Controller profile:** `halehound` (esptool backend, single **merged** image flashed at offset `0x0`, not suicide-capable)
> **This guide:** purchase → build → flash → integrate into Cyber Controller → use → troubleshoot.

## 1. Overview
HaleHound is a multi-protocol offensive-security/recon firmware built specifically for the **CYD ("Cheap
Yellow Display") ESP32 boards** — a ~US$10 ESP32-WROOM-32 dev board with a bonded SPI touchscreen and a
microSD slot. Out of the box (on the ESP32 alone) it does WiFi work — packet monitor, beacon spam,
deauther, probe sniffer / Evil-Twin, captive-portal credential harvesting, EAPOL/PMKID capture, station
scanning, and BLE scanning/spoofing/tracker-hunting. Its distinguishing feature is **external radio
expansion**: solder on a **CC1101** (SubGHz 300–928 MHz capture/replay/brute), an **NRF24L01+PA+LNA**
(2.4 GHz sniff/flood/MouseJack/spectrum), a **PN532** (NFC/RFID scan/read/clone/emulate MIFARE & NTAG),
and an optional **GPS** (wardriving / camera detection), turning the CYD into a Flipper-class multi-band
tool. The whole UI is touch-driven and auto-scales between the 240×320 (2.8") and 320×480 (3.5") panels.

In Cyber Controller the profile id is **`halehound`**: it flashes the merged release image over USB and
drives the device's serial monitor from the **Devices** tab. Because HaleHound is primarily an on-screen,
touch-operated tool, the serial side is mainly its **Serial Monitor / UART passthrough** (boot banner,
logs, debug) rather than a full scriptable CLI like Marauder.

## 2. Legal & Safety
**Authorized testing only.** HaleHound transmits across several regulated bands — 2.4 GHz WiFi/BLE
deauth/flood, 2.4 GHz NRF24 jamming/MouseJack, and SubGHz (315/433/868/915 MHz) replay/brute/disruption.
**WiFi deauthentication and any RF jamming/flooding against networks, devices, or people you do not own or
lack written permission to test is illegal in most jurisdictions** (US: CFAA + FCC rules that flatly
prohibit jammers; EU and others similar). SubGHz replay against vehicles/gates/garage doors and NFC card
cloning are likewise unlawful without authorization. The firmware itself gates every offensive module
behind an on-device liability acceptance prompt (decline → defensive/passive "Blue Team" modules only);
treat that prompt as a real legal boundary, not a formality. Passive scanning/sniffing and the jam-
detection modules may still be regulated where you live — check local law. Cyber Controller does not
remove any of this responsibility from you.

## 3. Hardware & Purchasing
HaleHound runs only on CYD-family ESP32 boards (all use the **classic ESP32**, 4 MB flash). Pick the panel
size first, then decide which radios to add.

| Tier | Board | Cyber Controller `board_id` | Why | Where to buy (search terms) |
|------|-------|------------------------------|-----|------------------------------|
| Default / best-tested | **ESP32-2432S028R CYD 2.8"** (ILI9341, XPT2046 resistive touch) | `esp32-cyd` | Cheapest, most documented, fully tested upstream | AliExpress/Amazon: **"ESP32-2432S028R CYD 2.8"** |
| Bigger screen | **QDtech E32R35T CYD 3.5"** (ST7796 320×480) | `E32R35T` | Larger UI, more room for radios | AliExpress: **"ESP32 CYD 3.5 E32R35T"** / "ESP32-3248S035" (verify: exact SKU matches E32R35T, ST7796 panel) |
| Alt 2.8" | **QDtech E32R28T CYD 2.8"** | `E32R28T` | QDtech variant of the 2.8" | AliExpress: **"ESP32 CYD E32R28T 2.8"** (verify: variant ID before buying) |
| Pre-wired hat | **NM-RF-Hat** (2.8" CYD + RF carrier) | `NM-RF-Hat` | Carrier board that pre-routes the external radios | verify: current source/vendor for "NM-RF-Hat" CYD hat |
| Pre-built kit | **CYD + HaleHound in a case** | (flash as `esp32-cyd`) | No soldering; some shops sell assembled units | Search **"ESP32 HaleHound 2.8 touchscreen"** (e.g. STSCollective lists a cased build) — verify what radios are actually fitted |

**External radio modules (optional, soldered to the CYD breakout pins):**

| Module | Buy (search terms) | Adds |
|--------|--------------------|------|
| **CC1101** SubGHz (HW-863, or **E07-433M20S** PA version for more TX power) | "CC1101 433MHz module", "E07-433M20S" | 300–928 MHz capture / replay / brute / spectrum / .sub |
| **NRF24L01+PA+LNA** | "NRF24L01+PA+LNA" | 2.4 GHz sniff, flood, MouseJack, spectrum |
| **PN532 V3** (Elechouse, **SPI** mode) | "PN532 NFC V3 Elechouse" | NFC/RFID scan/read/clone/emulate (MIFARE, NTAG) |
| **GPS** (GT-U7 or NEO-6M) | "GT-U7 GPS module", "NEO-6M GPS" | Wardriving / GPS-tagged logging |
| **5V→3.3V buck/LDO** (AMS1117-3.3 module or MP2307 mini-buck) | "AMS1117 3.3V module", "MP2307 mini buck" | **Required** if you fit PA radios (see §4) |

**Accessories:** a real **data** USB cable (CYD uses **micro-USB** + a **CH340** USB-serial chip — many
cheap cables are charge-only); a **microSD** card formatted **FAT32** for captures/loot/OTA; thin silicone
hookup wire; and a soldering iron for the radio pins. **Do not invent product URLs** — buy from AliExpress
/ Amazon / the module makers and confirm the board ID and 4 MB flash before purchase.

## 4. Building / Assembly
- **Bare CYD (WiFi/BLE only):** no assembly — just plug in a data cable. Every WiFi and BLE-via-ESP32
  feature works with zero soldering.
- **Adding radios:** the CYD exposes a few breakout headers (often labelled **CN1 / P3 / extension
  pads**). HaleHound uses the ESP32 **VSPI** bus shared across CC1101 / NRF24 / PN532, with separate chip-
  select / control pins per module. Wiring **from the upstream README** (verify against the README's
  Radio-Test screen, which draws the diagrams on-device):
  - **CC1101 (SubGHz):** VCC→3.3V, GND→GND, SCK→GPIO18, MOSI→GPIO23, MISO→GPIO19, CS→**GPIO27** (GPIO21 on
    E32R35T), GDO0(TX)→GPIO22, GDO2(RX)→GPIO35. *Upstream note: CiferTech's original firmware had CC1101
    TX/RX swapped; HaleHound corrects this.*
  - **NRF24L01+PA+LNA:** VCC→3.3V, GND→GND, SCK→GPIO18, MOSI→GPIO23, MISO→GPIO19, CSN→**GPIO4** (GPIO26 on
    E32R28T/E32R35T), CE→GPIO16, IRQ→GPIO17. Solder a **10 µF cap** across the module's VCC/GND if it
    randomly resets.
  - **PN532 (NFC, SPI mode):** VCC→3.3V (CN1), GND→GND (CN1), SCK→GPIO18, MOSI→GPIO23, MISO→GPIO19,
    SS→GPIO17. Set the module **DIP switches to SPI** (CH1=OFF, CH2=ON).
  - **GPS:** VCC→VIN(5V), GND→GND, module TX→**GPIO1**; 9600 baud (firmware auto-scans / handles serial).
- **Critical power rule:** **the PA radios (NRF24+PA+LNA, E07 CC1101) draw more current than the CYD's
  onboard 3.3 V regulator can supply.** Power them from a **separate 5V→3.3V buck/LDO**: tap 5 V from USB
  VBUS *before* the CYD regulator and feed the module VCC from the independent 3.3 V output (common ground).
  Sharing the CYD 3.3 V rail causes brownouts, random resets, and failed radio init.
- **Drivers:** install the **CH340** USB-serial driver (Windows: CH341SER; macOS: CH341SER_MAC; Linux:
  in-kernel 5.x+). Without it no COM/tty port appears and Cyber Controller can't see the board.
- **Per-board gotchas:** the 3.5" **E32R35T** uses an **ST7796** controller (vs ILI9341 on the 2.8"
  boards) and moves CC1101/NRF24 chip-selects — flash the matching `board_id` or you get a blank/garbled
  screen and dead radios. Touch is **resistive (XPT2046)** on all variants and may need calibration.

## 5. Flashing & First Run (via Cyber Controller)

![Flashing connection diagram](../assets/connect-esptool-boot.png)

*How to connect the board to flash it (classic ESP32 — BOOT/EN download mode).*

1. Connect the CYD by USB; open Cyber Controller → **Flash** tab.
2. **Port:** pick the board's COM/tty (click *Refresh* if missing → almost always a CH340 driver issue).
3. **Firmware Profile:** `HaleHound`.
4. **Board / variant:** choose the exact CYD you own — **ESP32 CYD 2.8" (`esp32-cyd`)**, **E32R35T 3.5"**,
   **E32R28T 2.8"**, or **NM-RF-Hat**. The variant picks the right display driver and pin map; the wrong
   choice = blank screen and non-functional radios.
5. Click **Flash.** HaleHound is a **single merged image** (`image_model: merged-single-bin`): Cyber
   Controller resolves the latest GitHub release `.bin` for the classic ESP32, prefers the **FULL/merged**
   asset, and esptool writes it in one pass at offset **`0x0`** (bootloader + partitions + app are all
   inside that one file — no separate boot/partition offsets). First boot shows the HaleHound touch UI,
   then the on-device **liability/VALHALLA disclaimer** before offensive modules unlock.

*(Upstream also offers a browser web-flasher at flash.halehound.com; Cyber Controller does the same job
over esptool and adds backup + the serial terminal, so prefer the Flash tab here.)*

## 6. Integrate into Cyber Controller
- **Profile:** `halehound` — backend **esptool**, chip **esp32**, `image_model: merged-single-bin`,
  `app_offset: 0x0`, `support_files: null`, `supports_suicide: false`. Release assets are matched by the
  `github_release` resolver (`.bin`, prefer the **FULL** fragment) from
  `github.com/JesseCHale/HaleHound-CYD/releases/latest`.
- **Boards exposed:** `esp32-cyd`, `E32R35T`, `E32R28T`, `NM-RF-Hat` (all chip `esp32`, 4 MB, DIO @ 80 MHz,
  external modules CC1101 / NRF24L01 / PN532 declared in the profile).
- **Control:** open the **Devices** tab → select the port → set **Firmware = HaleHound** → **Connect** at
  **115200 baud** (`default_baud`). HaleHound is operated from its **touchscreen**, so the serial side is
  the device's **Serial Monitor / UART passthrough**: use Cyber Controller's terminal to read the boot
  banner, logs, GPS/NMEA, and debug output, and to confirm the link is alive — not as a full remote CLI
  (it does not expose a Marauder-style scriptable command set). Treat the terminal as monitoring/diagnostic.
- **Backup first:** use **Backup** in the Flash tab to dump the current 4 MB flash before overwriting, so
  you can restore the prior firmware.
- **Cross-Comm:** because HaleHound's serial output is not a structured target protocol, do not expect it
  to auto-populate the shared **Targets** pool the way Marauder does (verify: current build's serial output
  format). Dead Man's Switch / suicide is **not** supported for this profile (`supports_suicide: false`).

## 7. Usage (end-to-end)
1. **Flash & accept disclaimer:** boot, calibrate touch if prompted, accept the VALHALLA liability prompt
   to unlock offensive modules (or decline for passive/Blue-Team only).
2. **Insert microSD (FAT32):** captures and loot land under `/sd/...` (e.g. `/sd/eapol/`, `/sd/wardriving/`,
   `/sd/subghz/`, `/sd/loot/`); OTA images go in `/sd/firmware/`.
3. **WiFi (no extra hardware):** WiFi menu → Scanner / Packet Monitor / Deauther / Probe-Sniffer→Evil-Twin
   / Captive Portal (credential harvest) / EAPOL-PMKID capture — **authorized targets only.**
4. **SubGHz (CC1101):** record + replay, brute (Princeton/CAME/Nice-FLO/PT2262), spectrum analyzer, or
   browse/transmit Flipper **`.sub`** files from SD.
5. **2.4 GHz (NRF24):** channel scanner, spectrum analyzer, promiscuous sniffer, MouseJack keystroke
   injection (lab gear you own).
6. **NFC/RFID (PN532):** scan → read MIFARE sectors → clone UID → emulate; NTAG213/215/216 read/dump/write.
7. **GPS / wardrive:** with a GPS module, log GPS-tagged APs to SD (lawful, owner-authorized).
8. **Monitor over Cyber Controller:** keep the **Devices** terminal open at 115200 to watch logs/NMEA
   while operating from the screen. Disconnect in Cyber Controller to free the port.

## 8. Troubleshooting
- **No COM port:** install the **CH340** driver (CH341SER); try another **data** micro-USB cable; on Linux
  add your user to `dialout` and replug.
- **Blank / garbled screen after flash:** wrong board variant — re-flash selecting the exact CYD
  (`esp32-cyd` vs `E32R35T` vs `E32R28T` vs `NM-RF-Hat`); the 3.5" ST7796 panel especially needs `E32R35T`.
- **Display upside-down / touch offset:** Settings → Rotation; Tools → Touch Calibrate (auto-calibrates on
  first boot).
- **Flash fails / "Failed to connect":** hold **BOOT** while plugging in (or during connect), lower the
  flash baud in Settings, and close any serial monitor (including the Devices terminal) holding the port.
- **Radios won't init / random resets:** you're browning out the shared 3.3 V rail — move PA modules to a
  **separate 5V→3.3V buck**, add the **10 µF cap** across the NRF24 VCC/GND, and re-check the per-board CS
  pins (CC1101 CS = GPIO27/GPIO21; NRF24 CSN = GPIO4/GPIO26).
- **PN532 not detected:** set the module DIP switches to **SPI** (CH1=OFF, CH2=ON) and verify VCC/GND on
  CN1; confirm SS=GPIO17.
- **GPS conflicts with USB serial:** expected — firmware releases the UART during GPS use; if you need both,
  read GPS on-screen rather than over Cyber Controller's terminal.
- **Boot-loop / brick:** **Erase Flash** then re-flash the merged image; verify the board is genuinely 4 MB.
- **Build-from-source fails (PlatformIO):** use **Python 3.10–3.13** (3.14 needs a `platform.py` patch);
  targets are `esp32-cyd`, `esp32-e32r35t`, `esp32-e32r28t`, `esp32-cyd-hat`.

## 9. Sources
- Upstream firmware: <https://github.com/JesseCHale/HaleHound-CYD> (README — boards, menu tree, wiring
  pinouts, power requirement, build targets, SD layout, known issues) and the
  [releases](https://github.com/JesseCHale/HaleHound-CYD/releases) page.
- Cyber Controller profile: `src/config/profiles/halehound.json` (boards `esp32-cyd` / `E32R35T` /
  `E32R28T` / `NM-RF-Hat`, chip `esp32`, esptool backend, merged single image @ `0x0`, `default_baud`
  115200, `supports_suicide: false`, GitHub-release resolver).
- CYD hardware reference: Random Nerd Tutorials & Mischianti ESP32-2432S028R pinout pages; module makers
  (CC1101 / NRF24L01+PA+LNA / PN532 V3 / NEO-6M / GT-U7).
- Pre-built option: STSCollective "ESP32 HaleHound" listing (verify fitted radios before buying).
- **verify at purchase/flash time:** current upstream version (profile text references v3.5.5 but the repo
  ships newer releases — Cyber Controller always pulls the latest), repo license, exact AliExpress SKUs for
  the QDtech E32R35T/E32R28T and NM-RF-Hat, and the on-device Radio-Test wiring diagrams for your board.
