# ESP32 Marauder — Complete Hardware Guide

> **Firmware:** ESP32 Marauder · **Upstream:** [justcallmekoko/ESP32Marauder](https://github.com/justcallmekoko/ESP32Marauder) (GPL-3.0)
> **Chips:** ESP32, ESP32-S2, ESP32-S3, ESP32-C5 · **Cyber Controller profile:** `marauder` (esptool backend, multi-file offsets, suicide-capable)
> **This guide:** purchase → build → flash → integrate into Cyber Controller → use → troubleshoot.

## 1. Overview
ESP32 Marauder is the most widely used ESP32 WiFi/Bluetooth offensive-security firmware. It performs
WiFi scanning, packet sniffing, deauthentication, beacon/probe spam, evil-portal/evil-AP, PMKID/EAPOL
capture, and BLE scanning/spoofing, with an on-device UI on display boards and a serial CLI everywhere.
Cyber Controller flashes it, drives its serial command set, and feeds its scan output into the shared
target pool for cross-device coordination.

## 2. Legal & Safety
**Authorized testing only.** Deauthentication, beacon spam, and evil-AP transmit on the 2.4 GHz band and
are **illegal against networks/people you do not own or have written permission to test** in most
jurisdictions (US: CFAA/FCC; EU and others similar). Use only on your own lab gear or under an explicit
engagement scope. Cyber Controller labels these as dangerous commands and (unless you disable warnings)
confirms before sending. Passive scanning/sniffing may still be regulated where you live — check local law.

## 3. Hardware & Purchasing
Marauder runs on many ESP32 boards. Pick by how you'll use it:

| Tier | Board | Why | Where to buy (search terms) |
|------|-------|-----|------------------------------|
| Best all-in-one | **Official Marauder v6/v7** (ESP32-WROOM + 2.4" touch + SD + battery) | Purpose-built, on-device UI, GPS option | Search "justcallmekoko Marauder" on **Tindie**; resellers: **dbrand Killer**, **Lonely Binary** |
| Cheap + screen | **CYD "Cheap Yellow Display" ESP32-2432S028R** (2.8" ILI9341) | ~US$10–15, great starter | AliExpress/Amazon: "ESP32-2432S028R CYD 2.8" |
| Pocket | **M5StickC Plus2** / **M5Cardputer** (ESP32-S3) | Tiny, built-in screen/keyboard | **M5Stack** store / Amazon: "M5Cardputer" |
| Flipper add-on | **Flipper Zero WiFi Dev Board (ESP32-S2)** or **Multi-Board S3** | Integrates with Flipper | Flipper official store; "Flipper WiFi dev board" |
| Bare/no screen | Any **ESP32-WROOM-32 DevKit** | Cheapest, serial-only via Cyber Controller | AliExpress/Amazon: "ESP32 DevKit V1" |
| Dual-band | **Marauder Mini v3 / Waveshare ESP32-C5** | adds 5 GHz | Waveshare: "ESP32-C5 DevKitC" |

**Accessories:** a quality **USB-C/micro-USB data cable** (not charge-only), optional **microSD** (FAT32)
for capture logging, optional **GPS module** (NMEA) for wardriving, and an external antenna where the
board exposes a u.FL connector. **Avoid** ESP32 clones with the wrong flash size; verify 4MB+.

## 4. Building / Assembly
- **Pre-built boards (CYD, M5, official Marauder):** no assembly — just a data cable.
- **DevKit + screen DIY:** wire an SPI display per the upstream wiring guide; most users skip this and use
  a CYD instead.
- **Drivers:** install the USB-serial driver for your board's chip — **CP210x** (most DevKits/official),
  **CH340** (cheap clones), or native USB (S2/S3). Without it, no COM port appears.
- **Per-board gotchas:** CYD comes in display variants (2432S028 vs Guition 2.4"/3.5") — pick the matching
  variant in Cyber Controller or the screen stays blank. ESP32-C5 uses a **`0x2000`** bootloader offset
  (Cyber Controller handles this automatically).

## 5. Flashing & First Run (via Cyber Controller)
1. Connect the board by USB; open Cyber Controller → **Flash** tab.
2. **Port:** pick the board's COM/tty (click *Refresh* if missing → driver issue).
3. **Firmware Profile:** `ESP32 Marauder`.
4. **Board / variant:** choose your exact board (e.g. *CYD 2.8"*, *M5Cardputer*, *Generic ESP32*). "Auto"
   uses the chip default and may be wrong for display boards — if the screen stays blank, re-flash with
   the matching variant.
5. Click **Flash**. Cyber Controller auto-detects the chip, fetches the latest release, and writes the
   bootloader/partitions/app at the correct offsets. First boot shows the Marauder UI (on screen boards)
   or prints a banner on the serial terminal.

## 6. Integrate into Cyber Controller
- **Profile:** `marauder` (esptool, multi-file: bootloader@0x1000 / partitions@0x8000 / app@0x10000;
  the app pulls boot files from the upstream FlashFiles tree per chip).
- **Control:** open the **Devices** tab → select the port → set **Firmware = ESP32 Marauder** (Pro mode;
  Simple mode auto-uses it) → **Connect**. The protocol-aware parser understands Marauder output, so APs/
  clients populate the **Targets** pool and the persistent terminal colorizes per device.
- **Command set:** the per-firmware palette offers Marauder commands (`scanap`, `sniffraw`, `attack -t
  deauth`, `list -a`, `select -a <n>`, `stopscan`, etc.). Dangerous verbs are confirmed first.
- **Cross-Comm:** a scan on the Marauder feeds `target.added` events; auto-routing rules can fire a
  command on another connected device. **Dead Man's Switch** is supported for this profile.
- **Backup first:** use **Backup** in the Flash tab to dump the current flash before overwriting.

## 7. Usage (end-to-end)
1. **Scan:** Devices tab → `scanap` → watch APs appear in **Targets**.
2. **Select a target** in Targets → right-click → action (e.g. deauth) — or send `select -a <n>` then
   `attack -t deauth` in the terminal (authorized targets only).
3. **Capture:** `sniffraw` / PMKID modes; with a microSD the device logs `.pcap`/`.log`.
4. **Wardrive:** pair a GPS module and use the **Wardrive** tab to export WiGLE CSV (lawful, owner-authorized).
5. **Stop:** `stopscan` / stop the attack; Disconnect to free the port.

## 8. Troubleshooting
- **No COM port:** install CP210x/CH340 driver; try another (data) cable; on Linux add your user to
  `dialout` and replug.
- **Blank screen after flash:** wrong board variant — re-flash selecting the exact display board.
- **Flash fails / "Failed to connect":** hold **BOOT** while plugging in (or during connect), lower the
  flash baud in Settings, close any serial monitor holding the port.
- **Boot-loops / brick:** use **Erase Flash** then re-flash; verify the board is genuinely 4MB+.
- **C5/dual-band oddities:** ensure the C5 variant is selected (the `0x2000` bootloader offset is
  required — Cyber Controller sets it automatically).
- **Verify failed:** re-run flash with verify on; a bad cable/clone flash chip is the usual cause.

## 9. Sources
- Upstream: <https://github.com/justcallmekoko/ESP32Marauder> (README, wiki, FlashFiles, releases).
- Cyber Controller profile: `src/config/profiles/marauder.json` (boards, offsets, command protocol).
- Hardware: official Marauder (Tindie/dbrand/Lonely Binary), CYD (ESP32-2432S028R), M5Stack, Flipper store.
- Verify current board availability + prices at purchase time; vendor links change.
