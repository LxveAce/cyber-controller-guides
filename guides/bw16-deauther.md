# BW16 / RTL8720DN Deauther — Complete Hardware Guide

> **Firmware:** Vampire Deauther (BW16/RTL8720DN) · **Upstream lineage:** [tesa-klebeband/RTL8720dn-Deauther](https://github.com/tesa-klebeband/RTL8720dn-Deauther) (GPL-3.0) → Vampire Deauther distribution ([vampel/vampel.github.io](https://github.com/vampel/vampel.github.io))
> **Chip:** RTL8720DN (Realtek AmebaD, dual-core ARM Cortex-M33) packaged as the **BW16** module · **Cyber Controller profile:** `rtl8720` (AmebaD ImageTool backend, `bw16` protocol, SHA-256-pinned bundle)
> **This guide:** purchase → wire → flash → integrate into Cyber Controller → use → troubleshoot.

## 1. Overview
The BW16 deauther is a **dual-band** WiFi deauthentication tool built on Realtek's **RTL8720DN** — a Wi-Fi (2.4 GHz **and** 5 GHz) + Bluetooth LE 5.0 SoC. Its headline capability is the one ESP8266/ESP32 deauthers cannot match: it can **deauthenticate 5 GHz networks**, not just 2.4 GHz. The lineage starts with tesa-klebeband's *RTL8720dn-Deauther* (an ESP32-Deauther ported to the RTL8720dn to "deauthenticate on 5GHz now"); Cyber Controller ships a prebuilt **Vampire Deauther** binary bundle for the same chip (§9).

Functionally it scans nearby APs across both bands, deauthenticates a selected target (or several), and can spam randomized beacon frames. It also exposes BLE on the Realtek radio. Cyber Controller flashes the AmebaD firmware bundle, then drives the device's **`AT+` serial CLI** and feeds scan output into the shared target pool for cross-device coordination.

## 2. Legal & Safety
**Authorized testing only.** Deauthentication transmits forged management frames that knock clients off a network; doing this against networks, devices, or people you **do not own or have explicit written permission to test is illegal** in most jurisdictions (US: CFAA + FCC rules against willful RF interference; EU and others have direct equivalents). The 5 GHz capability does **not** make it more legal — it widens the blast radius to bands ESP32 gear can't touch, and 5 GHz channels include radar/DFS allocations that are especially regulated. Use only on your own lab gear or under an explicit, scoped engagement.

Cyber Controller labels deauth/beacon verbs as dangerous commands and (unless you disable warnings) confirms before sending. Beacon spam and any transmit mode are equally restricted; even passive scanning may be regulated where you live — check local law first.

## 3. Hardware & Purchasing
You need an **RTL8720DN/BW16** board and, for the bare-module variants, a **3.3 V USB-to-TTL adapter**. Pick by how the board exposes its serial port:

| Variant | What it is | Flashing path | Where to buy (search terms) |
|---|---|---|---|
| **BW16 Type-C / USB dev board** | RTL8720DN module on a carrier with onboard USB-UART + Type-C; easiest | USB cable only **if** USB is wired to the flash UART (verify — see §4) | AliExpress/eBay: **"BW16 RTL8720DN development board Type-C"** |
| **Mini BW16 (CH340)** | Compact dev board with a CH340 USB-serial bridge + GPIO headers | USB cable + CH340 driver | AliExpress: **"Mini BW16 RTL8720DN CH340"** |
| **BW16-Kit** | Module pre-soldered on a small breakout with castellated pads/headers | Usually USB-TTL adapter on LOG pins | Amazon/AliExpress: **"BW16-Kit RTL8720DN"** |
| **Bare BW16 module** | Just the castellated B&T module (cheapest, for embedding) | **Requires** external 3.3 V USB-TTL adapter wired to PA7/PA8 | AliExpress/eBay: **"BW16 RTL8720DN module"** |
| **Flipper Zero BW16 dev board** | BW16 on a Flipper GPIO carrier (the Vampire Deauther also ships a Flipper `.fap`) | Per carrier; often a USB-UART header | Search **"Flipper Zero BW16 RTL8720DN deauther board"** |

**Antenna options:** BW16 modules ship as either **onboard/PCB antenna** or **IPEX (U.FL) connector** variants. The IPEX version lets you attach a high-gain external 2.4/5 GHz dual-band antenna for range; the PCB version is self-contained. Listings often have a dropdown: *onboard antenna* vs *IPEX antenna*, and *soldered* vs *unsoldered* pins — pick deliberately (verify the exact listing before buying).

**Accessories:**
- **3.3 V USB-to-TTL adapter** (CP2102 / CH340 / FT232) for bare-module variants. **Must be 3.3 V logic — 5 V can damage the RTL8720DN.**
- A quality **data** USB cable (not charge-only) for USB dev boards.
- Optional: dual-band IPEX antenna; a couple of SPST switches + a ~2 kΩ resistor if you need a manual download-mode jig (§4).
- **Avoid** boards advertised only as "RTL8720" without the **DN** suffix if you specifically need dual-band — verify the part is **RTL8720DN**.

## 4. Building / Assembly
There's no firmware build step for Cyber Controller (it flashes a prebuilt, SHA-256-pinned bundle). Assembly is about **getting a usable flash UART**, which is the single biggest BW16 gotcha.

**The LP_UART vs LOG_UART trap.** On many BW16 carriers the onboard USB-serial chip is wired to the **LP_UART** pins (GPIOB_1 / GPIOB_2 — the "AT command" port), but firmware flashing/logging uses the **LOG_UART** pins (**PA7 = GPIOA_7 / PA8 = GPIOA_8**). If your board routes USB to LP_UART, plugging in USB alone will **not** flash. Two fixes (verify which your board needs):
- **Bridge the pins:** connect `GPIOA_8 ←→ GPIOB_1` and `GPIOA_7 ←→ GPIOB_2` so the onboard USB reaches the LOG UART during upload, **or**
- **Use an external USB-TTL adapter** wired straight to the LOG pins.

**USB-TTL wiring (bare module / LOG pins):**
| Module pin | → | USB-TTL adapter |
|---|---|---|
| **PA7 / LOG_TX** (pin 11) | → | **RX** |
| **PA8 / LOG_RX** (pin 15) | → | **TX** |
| **GND** | → | **GND** |
| **3V3 / VCC** | → | **3.3 V** |

(TX↔RX crossed, as usual. Keep it strictly 3.3 V.)

**Download (flash) mode.** Cyber Controller's `rtl8720` profile expects the board to **auto-enter download mode via DTR/RTS** (the AmebaD loader pulses CHIP_EN/PA7 through the adapter's control lines). If your adapter/board doesn't auto-toggle, enter it manually:
- **Manual jig:** an SPST switch from **CHIP_EN (pin 3)** to GND, and a second SPST switch from **PA7 (pin 11)** to GND **through a ~2 kΩ resistor**. Sequence: **hold PA7-to-GND → press & release CHIP_EN-to-GND → release PA7.**
- **Button boards:** **hold "BURN" → press "RST" → release "BURN."**
The chip then listens on the LOG UART (CLI/monitor baud **115200**; the loader itself negotiates a faster flash baud — see §5).

**Drivers:** install your adapter/board's USB-serial driver — **CP210x**, **CH340**, or **FTDI** — or no COM port appears. (Distinct from ESP tooling: this is **not** esptool/ltchiptool — it's Realtek's AmebaD ImageTool, see §5/§6.)

## 5. Flashing & First Run (via Cyber Controller)
**One-time host prerequisite (important).** The RTL8720DN is flashed with **Realtek's AmebaD ImageTool**, which is **not bundled** with Cyber Controller (GPL/licensing). Provide it once:
- Set the env var **`CYBERC_AMEBAD_TOOL`** to the tool's path, **or** drop the binary into **`tools/realtek/`**.
- **On Windows, place `cygwin1.dll` alongside it** (the tool is a Cygwin build).
Without this, the `rtl8720` profile cannot flash. (Verify the exact tool name/location in your Cyber Controller build's docs.)

**Flash steps:**
1. Wire the board for flashing (§4) and connect it by USB. Open Cyber Controller → **Flash** tab.
2. **Port:** pick the board's COM/tty (click *Refresh* if missing → driver or LP/LOG-UART wiring issue, §4/§8).
3. **Firmware Profile:** `BW16 RTL8720DN — Vampire Deauther (AmebaD)` (profile id `rtl8720`).
4. **Board:** `BW16 RTL8720DN` (`board_id: bw16-rtl8720dn`, 2 MB flash) — the only board for this profile.
5. Click **Flash**. Cyber Controller fetches the pinned **Vampire Deauther** bundle (tag `vampire`), **verifies each file's SHA-256**, pushes the RAM flashloader, then writes the AmebaD image. First boot brings up the deauther firmware on the LOG UART at **115200**.

**What actually gets written (AmebaD 3-file image).** Unlike a single ESP app binary, AmebaD uses a multi-part image because the RTL8720DN is **dual-core** (a low-power **KM0** core + a 200 MHz **KM4** core):
- `imgtool_flashloader_amebad.bin` — RAM flashloader the host runs first
- `km0_boot_all.bin` — KM0 boot image
- `km4_boot_all.bin` — KM4 boot image
- `km0_km4_image2.bin` — the combined application image

Cyber Controller treats these as one **`merged-single-bin`** payload at **app_offset `0x0`**, all SHA-256-pinned (`verify_sha256: true`). **First-flash note:** on a factory module you typically must let the tool erase the vendor firmware so the new image runs.

## 6. Integrate into Cyber Controller
- **Profile:** `rtl8720` — backend **`rtl8720`** (Realtek AmebaD ImageTool, **not** esptool), control protocol **`bw16`**, resolver **`pinned_release`** (tag `vampire`, SHA-256 verified), image model **`merged-single-bin`**, app_offset `0x0`. Monitor/CLI baud **115200**; the AmebaD loader negotiates ~**1.5 Mbaud** for the flash transfer itself.
- **Control:** **Devices** tab → select the port → set **Firmware = BW16 RTL8720DN (Vampire Deauther)** → **Connect**. The `bw16` parser understands the firmware's output, so scanned APs populate the **Targets** pool and the persistent terminal colorizes per device.
- **Command set (`AT+` CLI):** the per-firmware palette exposes the Vampire Deauther verbs — **`AT+SCAN`** (scan APs across 2.4/5 GHz), **`AT+DEAUTHIDX`** (deauth a target by its scan index), **`AT+BEACONRANDOM`** (randomized beacon spam), **`AT+STOP`** (halt the current action). Dangerous verbs (deauth/beacon) are confirmed first.
- **Cross-Comm:** a scan feeds `target.added` events; auto-routing rules can fire a command on another connected device (e.g., a 2.4 GHz ESP32 + the BW16 covering 5 GHz). **Suicide / Dead Man's Switch is NOT supported** for this profile (`supports_suicide: false`).
- **Backup first:** use **Backup** in the Flash tab to dump current flash before overwriting where supported.

## 7. Usage (end-to-end)
1. **Scan:** Devices tab → `AT+SCAN`. Both bands are swept; APs appear in **Targets** with an index.
2. **Pick a target:** note the **index** of an AP you are authorized to test.
3. **Deauth:** `AT+DEAUTHIDX <index>` (or select the target in the Targets pool → right-click → deauth). On the original tesa-klebeband firmware the on-board RGB LED flashes **blue** while frames are sent (red = ready, green = HTTP/web-UI activity) — verify whether your specific board exposes the LED.
4. **Beacon spam (optional, lab only):** `AT+BEACONRANDOM` to flood randomized SSIDs.
5. **Stop:** `AT+STOP` to halt; **Disconnect** to free the port.

**Note on the web UI:** the upstream tesa-klebeband firmware also hosts a control AP (SSID `RTL8720dn-Deauther`, password `0123456789`, default `192.168.1.1`). Cyber Controller drives the **serial `AT+` CLI**, not that web UI — treat the AP details as lineage context (verify whether the exact Vampire bundle you flashed still hosts it).

## 8. Troubleshooting
- **No COM port:** install the CP210x/CH340/FTDI driver; use a **data** cable; on Linux add your user to `dialout` and replug.
- **Port appears but flash/connect fails:** you're almost certainly on the **LP_UART** port. Bridge `GPIOA_8↔GPIOB_1` and `GPIOA_7↔GPIOB_2`, or move the adapter to the **LOG** pins **PA7/PA8** (§4).
- **"Flashloader/ImageTool not found":** set **`CYBERC_AMEBAD_TOOL`** or place the tool in `tools/realtek/`; on Windows include **`cygwin1.dll`** (§5).
- **Won't enter download mode:** your adapter isn't toggling DTR/RTS — do the **manual** sequence (hold **PA7/BURN** → tap **CHIP_EN/RST** → release **PA7/BURN**), or use an adapter that exposes DTR/RTS (§4).
- **Flash transfer stalls / corrupt:** drop to a slower baud, use a short quality cable, and confirm a clean **3.3 V** supply (USB-TTL 3.3 V rails can sag — power VCC separately if needed). Re-flash; SHA-256 verification will catch a bad download.
- **Module damaged / dead:** check you never fed **5 V** to a logic pin; RTL8720DN I/O is 3.3 V.
- **Wrong/blank behavior:** confirm the part is genuinely **RTL8720DN** (not a plain RTL8720) and that the bundle's SHA-256 verified during flash.

## 9. Sources
- **Upstream firmware lineage:** tesa-klebeband/RTL8720dn-Deauther — <https://github.com/tesa-klebeband/RTL8720dn-Deauther> (README: 5 GHz deauth, AP `RTL8720dn-Deauther`/`0123456789`/`192.168.1.1`, RGB LED meaning, LOG/LP UART bridging, AmebaD board-manager URL).
- **Vampire Deauther distribution:** <https://github.com/vampel/vampel.github.io> (prebuilt BW16 AmebaD bundle + Flipper `.fap`).
- **Cyber Controller profile:** `src/config/profiles/rtl8720.json` (backend `rtl8720`, protocol `bw16`, AT+ command set, 4-file AmebaD bundle, SHA-256 pins, baud, host-tool requirement).
- **BW16 hardware:** Realtek AmebaD Arduino docs (`ameba-doc-arduino-sdk.readthedocs-hosted.com`, BW16 typec getting-started); Hackster "Getting Started with RTL8720DN BW16" and BW16 troubleshooting guide; mikey60/BW16-RTL8720DN-Module-Arduino (pinout, PA7/PA8 LOG wiring, CHIP_EN download sequence).
- **Purchasing:** AliExpress / eBay / Amazon listings for "BW16 RTL8720DN" (Type-C, Mini CH340, BW16-Kit, bare module; onboard vs IPEX antenna). **Verify current board availability, antenna option, and prices at purchase time — vendor links and stock change.**
