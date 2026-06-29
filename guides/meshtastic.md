# Meshtastic — Complete Hardware Guide

> **Firmware:** Meshtastic · **Upstream:** [meshtastic/firmware](https://github.com/meshtastic/firmware) (GPL-3.0)
> **Chips:** ESP32-S3 (this profile's default board) · also ESP32, ESP32-C3, ESP32-C6 in the same release family — nRF52840 and RP2040 boards exist but use a UF2 bootloader, not esptool · **Cyber Controller profile:** `meshtastic` (esptool backend, merged single-bin @ `0x0`, no suicide)
> **This guide:** purchase → build → flash → integrate into Cyber Controller → use → troubleshoot.

## 1. Overview
Meshtastic is an open-source firmware that turns inexpensive **LoRa** boards into a long-range, low-power
**mesh network** for **text messaging, GPS/position sharing, and telemetry — with no cellular, WiFi, or
internet required**. Nodes relay each other's packets, so a handful of devices can cover kilometres of
terrain; traffic on a channel is end-to-end encrypted with a pre-shared key (AES). It is a *communications*
firmware, not an offensive-security tool. Cyber Controller's role is the **flashing** step: it fetches the
correct per-board image and writes it over USB. Day-to-day operation (region, channels, messaging) happens
through the official Meshtastic **phone app, web client, or Python CLI** — see §6–7.

## 2. Legal & Safety
**Two hard rules before anything else:**

1. **Attach the LoRa antenna before powering the board on.** Upstream is explicit: *"Never power on the
   radio without attaching an antenna as doing so could damage the radio chip!"* Transmitting into an
   open/unmatched port can destroy the SX126x/LR11xx radio. This applies on first boot and every flash.
2. **Set the correct `lora.region` (it is mandatory and lawful operation depends on it).** Until a region
   is set, the node displays a warning and **will not transmit any packets**. Each region defines the
   licence-free ISM band, max power, and **duty-cycle** limits for your jurisdiction — e.g. **US** 902–928
   MHz, **EU_868** 869.4–869.65 MHz (duty-cycle limited), **EU_433**, **ANZ** 915–928 MHz, plus CN, JP,
   KR, TW, IN, RU, and many others (full list in §7 / cite §9).

**Lawful framing:** Meshtastic runs on licence-free ISM bands, but you must pick **the region you are
physically in**, use **a board built for that band** (a 915 MHz board cannot legally operate on 868), and
**respect the band/power/duty-cycle rules**. Do not set a foreign region to access a band you are not
permitted to use. In most places this is unlicensed operation; some bands (e.g. EU 868) enforce strict
duty-cycle — Meshtastic honours these once the region is correct.

## 3. Hardware & Purchasing
Meshtastic runs on many LoRa boards. The Cyber Controller `meshtastic` profile targets **ESP32-S3 /
Heltec-class** boards; pick by how you'll deploy:

| Tier | Board | MCU / radio | Why | Where to buy (search terms) |
|------|-------|-------------|-----|------------------------------|
| **Best starter (this profile default)** | **Heltec WiFi LoRa 32 V3** (also V4) | ESP32-S3 + SX1262, 0.96" OLED | ~US$20, OLED, battery + (V4) solar/GNSS headers, u.FL LoRa | **heltec.org**, **Rokland**, Amazon/AliExpress: "Heltec LoRa 32 V3 SX1262" |
| GPS / battery node | **LilyGo T-Beam** (v1.1 / T-Beam Supreme) | ESP32(-S3) + SX1262 + GPS, 18650 holder | Built-in GPS + battery, classic field node | **LilyGo** store, Rokland, AliExpress: "LilyGo T-Beam Meshtastic" |
| Low-power handheld | **LilyGo T-Echo** | nRF52840 + SX1262 + e-ink + GPS | Very low power, e-ink, GPS — *UF2 flash, not this esptool profile* | LilyGo / Rokland: "LilyGo T-Echo" |
| Keyboard + screen | **LilyGo T-Deck** | ESP32-S3 + SX1262, QWERTY + LCD | Standalone messaging without a phone | LilyGo / Rokland: "LilyGo T-Deck Meshtastic" |
| Solar / base station | **RAK WisBlock Starter Kit** (RAK4631 core, RAK19007 base) | nRF52840 + SX1262 | Modular, lowest power, best for solar — *UF2 flash, not this profile* | **RAKwireless** store, Rokland: "RAK WisBlock Meshtastic 4631" |
| Pocket tracker | **Seeed SenseCAP T1000-E** | nRF52840 + LR1110 | Card-sized, IP65, GPS — *UF2 flash, not this profile* | **Seeed Studio**, Rokland: "SenseCAP T1000-E" |
| Compact ESP32-S3 | **Station G2 / Nano G2 Ultra** (B&Q) | ESP32-S3 + SX1262 | Polished enclosure, optional GPS | B&Q Consulting / Rokland: "Station G2 Meshtastic" |

**Accessories (essential):** a **band-matched LoRa antenna** with the right connector (most boards use
**u.FL/IPEX** pigtail to SMA) — buy the **915 MHz** antenna for US/ANZi or **868 MHz** for EU; a **data**
USB-C cable (not charge-only); a **18650 / LiPo** for portable nodes; optional **GPS module** and **solar
panel** on boards with those headers. **Verify the board's band variant matches your region before buying.**

> ESP32-S3 / ESP32 / C3 / C6 boards flash with this `esptool` profile. **nRF52840 and RP2040 boards
> (T-Echo, RAK, T1000-E, Mesh Node T114) install via a UF2 drag-and-drop bootloader and are *not* served by
> the `meshtastic` esptool profile** — flash those with the Meshtastic Web Flasher instead (verify: §9).

## 4. Building / Assembly
- **Attach the antenna first** (see §2) — then connect battery, then USB. Never key up bare.
- **Pre-built boards (Heltec V3, T-Beam, T-Deck, Station G2):** no assembly — antenna + data cable only.
- **Battery / solar:** plug a LiPo/18650 into the board's battery connector (observe polarity — Heltec uses
  an SH1.25 JST); V4-class and RAK/Seeed boards expose solar/GNSS headers for off-grid nodes.
- **Drivers (ESP32 only):** install the USB-serial driver for your board's bridge — **CP210x** (most
  Heltec/ESP32 DevKits) or **CH340/CH9102** (some clones). Native-USB ESP32-S3 boards may enumerate without
  a driver. Without the right driver, no COM port appears.
- **Per-board gotchas:** confirm the exact variant (e.g. **Heltec V3 vs V2** vs **V4**) — picking the wrong
  variant flashes the wrong pin map and the OLED/LoRa won't work. nRF52/RP2040 boards have **no serial
  bootloader** — they mount as a USB drive for UF2 files (not this profile).

## 5. Flashing & First Run (via Cyber Controller)
1. **Attach the antenna**, then connect the board by USB; open Cyber Controller → **Flash** tab.
2. **Port:** pick the board's COM/tty (click *Refresh* if missing → driver issue, see §4).
3. **Firmware Profile:** `Meshtastic`.
4. **Board / variant:** choose your exact board (default is **`heltec-v3`**). Variants are listed
   **by chip** — e.g. ESP32-S3: `heltec-v3`, `tbeam-s3-core`, `t-deck`, `t-watch-s3`, `station-g2`,
   `tlora-t3s3-v1`, `m5stack-cores3`, `seeed-xiao-s3`, and more; ESP32: `tbeam`, `tlora-v2-1-1_6`,
   `heltec-v2_1`, `rak11200`, `nano-g1`, etc. Pick the one printed on your board.
5. Click **Flash**. Cyber Controller auto-detects the chip, resolves the latest GitHub release, downloads
   the per-chip `firmware-<chip>-<version>.zip`, extracts the **merged single image
   `firmware-<board>-<version>.bin`**, and writes it at **offset `0x0`** (8 MB flash, `dio` @ 80 MHz for
   Heltec V3). If a flash fails, hold **BOOT** while connecting to force download mode (see §8).
6. **First boot:** the OLED shows the Meshtastic splash and a **"region not set"** message — that's
   expected. The radio stays silent until you set the region (next step, §7).

## 6. Integrate into Cyber Controller
- **Profile:** `meshtastic` — **backend `esptool`**, `image_model: merged-single-bin`, `app_offset: 0x0`,
  resolver `github_release` against `meshtastic/firmware` (latest release). Variants are resolved
  **by chip** from the release zips (`firmware-(esp32|esp32s2|esp32s3|esp32c3|esp32c6)-<ver>.zip`); default
  variant prefers **`heltec-v3`**. **`supports_suicide: false`** (no self-destruct for this profile).
- **No serial command protocol:** the profile's `protocol` is **`null`** — unlike Marauder, Cyber
  Controller does **not** parse a Meshtastic serial command set or auto-populate a target pool. The
  Devices tab can open the raw serial port, but **normal control is the Meshtastic app/web/CLI** (below).
- **Backup first:** use **Backup** in the Flash tab to dump current flash before overwriting; **Erase
  Flash** is available if you need a clean install (this wipes node config — export it first via the app).
- **Control plane (post-flash):** connect to the node with one of the official clients —
  - **Android / iOS app** → pairs over **Bluetooth** (also USB on Android).
  - **Web Client** (`client.meshtastic.org`, or the node's `meshtastic.local`) → over **WiFi/USB**.
  - **Python CLI** `meshtastic` → over **serial/USB** (or TCP/BLE) for scripting and bulk config.

## 7. Usage (end-to-end)
1. **Flash** (Cyber Controller, §5) with the antenna attached.
2. **Pair:** open the **Meshtastic phone app** and connect to the node over Bluetooth (or use the Web
   Client / CLI over USB).
3. **Set region (mandatory):** Settings → **LoRa → Region** → choose your country/band (**US**, **EU_868**,
   **EU_433**, **ANZ**, **CN**, **JP**, **KR**, **TW**, **IN**, **RU**, … or **LORA_24** for 2.4 GHz). The
   node now starts transmitting. *All nodes that must talk to each other need the **same Region and Modem
   Preset**.*
4. **Pick a modem preset:** default **LONG_FAST** (good range/speed balance); options run from
   **SHORT_TURBO** (fastest, shortest range) to **VERY_LONG_SLOW** (max range, low throughput).
5. **Channels:** the **primary channel** carries your mesh; it's keyed by a **PSK**. Share the channel QR/
   URL with others to put them on the same encrypted channel. Add secondary channels as needed.
6. **Message / track:** send text to the channel or a node, view other nodes on the map (GPS-equipped
   boards report position), and read telemetry (battery, environment) — all from the app/web/CLI.
7. **CLI examples (verify exact flags in §9 docs):** `meshtastic --set lora.region US`,
   `meshtastic --info`, `meshtastic --sendtext "hello mesh"`.

## 8. Troubleshooting
- **No COM port:** install the **CP210x**/**CH340/CH9102** driver; use a **data** cable; on Linux add your
  user to `dialout` and replug.
- **Flash fails / "Failed to connect":** hold **BOOT** while plugging in (or during connect) to enter
  download mode, lower the flash baud in Settings, and close any serial monitor/app holding the port.
- **OLED blank or garbled after flash:** wrong **variant** — re-flash selecting the exact board (e.g. V3 vs
  V2 vs V4).
- **"Region not set" / node won't transmit:** set **LoRa → Region** in the app (§7) — this is required by
  design, not a bug.
- **Nodes don't see each other:** mismatched **Region** or **Modem Preset**, different **channel/PSK**, or
  **no antenna** on one node. Confirm all three match and antennas are attached.
- **Poor range / radio damaged:** check the antenna is the **right band** and was attached **before** every
  power-on; an unmatched/missing antenna degrades or destroys the radio.
- **nRF52/RP2040 board won't flash here:** those use a **UF2 bootloader**, not esptool — use the Meshtastic
  Web Flasher (double-tap reset to mount the drive, drop the UF2). Not served by this profile.
- **Boot-loop / brick:** **Erase Flash** then re-flash; verify genuine flash size (Heltec V3 = 8 MB).

## 9. Sources
- Upstream: <https://github.com/meshtastic/firmware> (GPL-3.0; releases, per-chip firmware zips).
- Docs: <https://meshtastic.org> — Getting Started & antenna warning
  (<https://meshtastic.org/docs/getting-started/>), ESP32 flashing & CLI script
  (<https://meshtastic.org/docs/getting-started/flashing-firmware/esp32/>), LoRa region/preset/channels
  (<https://meshtastic.org/docs/configuration/radio/lora/>), supported hardware
  (<https://meshtastic.org/docs/hardware/devices/>), client apps (<https://meshtastic.org/docs/software/>).
- Cyber Controller profile: `src/config/profiles/meshtastic.json` (chip/board list, esptool backend,
  merged-single-bin @ `0x0`, `github_release` resolver, `protocol: null`, `supports_suicide: false`).
- Hardware/purchasing: heltec.org, LilyGo, RAKwireless, Seeed Studio, B&Q Consulting; resellers Rokland,
  Amazon, AliExpress. **Verify board band variant, current availability, and prices at purchase time;
  vendor links change.**
- **Verify before relying on exact syntax:** esptool offsets/erase steps for your specific board, current
  region frequency tables, and `meshtastic` CLI flags — confirm against the upstream docs above.
