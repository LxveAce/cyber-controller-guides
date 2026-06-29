# Flipper Zero — Momentum — Complete Hardware Guide

> **Firmware:** Momentum (Flipper Zero custom firmware) · **Upstream:** [Next-Flip/Momentum-Firmware](https://github.com/Next-Flip/Momentum-Firmware) (GPL-3.0)
> **Target hardware:** Flipper Zero · **Chip:** STM32WB55 (Cortex-M4 app core + Cortex-M0+ radio core) · **Cyber Controller profile:** `flipper-momentum` (**qflipper** backend, `merged-single-bin` package, installed by **qFlipper** — *not* serial/esptool-flashed)
> **This guide:** purchase → set up → install firmware (via qFlipper) → integrate into Cyber Controller → use → troubleshoot.

## 1. Overview
Momentum is a feature-rich custom firmware for the **Flipper Zero**, built on top of the official firmware and
incorporating work from the Unleashed project ("Feature-rich, stable and customizable"). It keeps every stock
capability — **SubGHz** (315/433/868/915 MHz read/emulate/analyze), **NFC** (13.56 MHz), **125 kHz RFID**,
**Infrared**, **GPIO/UART**, **iButton/1-Wire**, and **BadUSB/BadBT** — and adds the **Momentum App** (a
settings/configuration tool), **Asset Packs** (swappable animations/icons/font themes without recompiling),
**Bad-Keyboard** (enhanced USB/BT HID attacks with device spoofing), **BLE Spam**, **FindMy Flipper**,
**NFC Maker** (Type 4 / NTAG4xx), extended SubGHz frequency support with GPS **SubDriving**, a redesigned UI
(8 main-menu styles, custom keybinds), RGB-backlight support, security options (Lock on Boot, reset on false
PINs), and **JavaScript scripting**. Unlike the ESP32 firmwares Cyber Controller flashes over serial, the
Flipper Zero is **not** written with esptool — Cyber Controller's `flipper-momentum` profile downloads the
release package and hands it to a **locally installed qFlipper app** to install over USB DFU.

## 2. Legal & Safety
**Authorized use only.** The Flipper's transmitters are real radios. **SubGHz transmit** (replaying/sending
remotes, gates, sensors) is **restricted by law and by region** — and **NFC/RFID cloning** of cards/fobs you
do not own is illegal in most jurisdictions. Out of the box the **send function is disabled** until the device
is updated and a **region** is set; the firmware then only transmits on frequencies allowed for civilian use in
that region (e.g. the EU 868 band is restricted to ~868.150–868.550 MHz). Custom firmware like Momentum can
**extend or lift these region locks** (it adds bands such as 281–361 / 378–481 / 749–962 MHz) — **doing so does
not make transmission legal**; you remain responsible for complying with local RF, telecom, and computer-misuse
law (US: FCC/CFAA; EU/others similar). Use only on your own hardware/credentials or under an explicit, written
engagement scope. Cyber Controller treats transmit/clone/spam actions as dangerous and (unless warnings are
disabled) confirms before sending.

## 3. Hardware & Purchasing
Momentum runs on **one device: the Flipper Zero** (there are no board variants — `boards` in the profile is a
single entry). Buy the genuine device; clones and "pre-loaded" units are common and risky.

| What | Detail / spec | Where to buy (search terms) |
|------|---------------|------------------------------|
| **Flipper Zero (device)** | STM32WB55RG MCU; ≈US$169 retail (**verify current price**) | **Official:** [shop.flipperzero.one](https://shop.flipperzero.one/) · reseller list at [flipperzero.one/how-to-buy](https://flipperzero.one/how-to-buy) |
| EU / UK buyers | VAT-inclusive, fast EU shipping (~€190, **verify**) | **Lab401** — search "**Lab401 Flipper Zero**" ([lab401.com/products/flipper-zero](https://lab401.com/products/flipper-zero)) |
| Japan buyers | Sole authorized channel, MIC type-approved (~¥27,800, **verify**) | **Joom** — search "**Flipper Devices Official Store Joom**" |
| Avoid | Marketplace "deals" / clones / sellers offering "modded" or "unlocked" units | Buy only from the official store or a vendor listed on the official **how-to-buy** page |

**Hardware reference (stock Flipper Zero):**
- **MCU:** STM32WB55RG — ARM Cortex-M4 @ 64 MHz (apps) + Cortex-M0+ @ 32 MHz (radio).
- **SubGHz:** CC1101 transceiver, **20 dBm** max TX; bands **315 / 433 / 868 / 915 MHz**; RX across 300–348, 387–464, 779–928 MHz.
- **NFC:** ST25R3916 @ **13.56 MHz**. **RFID:** **125 kHz** (AM/OOK). **IR:** RX 950 nm, TX 940 nm / 300 mW.
- **GPIO:** **13 user I/O pins** on the 2.54 mm header (UART/SPI/I²C/3V3/5V). **iButton:** 1-Wire.
- **Connectivity:** USB-C (USB 2.0, 12 Mbps), **BLE 5.4** (4 dBm). **Power:** 2100 mAh (up to 28 days idle).
- **Storage:** microSD up to 256 GB (FAT32) — all firmware *data* (saved keys, dumps, apps) lives here.

**Accessories:** a quality **USB-C data cable** (not charge-only — qFlipper needs data), a **microSD card**
(FAT32; required for Momentum apps, asset packs, and saved captures), and optional **GPIO add-ons** (e.g. a
WiFi Dev Board / ESP32 module for WiFi work — that ESP runs separate firmware; see the Marauder guide).

## 4. Building / Assembly
There is **nothing to build or solder** — the Flipper Zero ships fully assembled. Setup is:
- **Insert a microSD card** (FAT32) before installing Momentum. Apps, asset packs, and saved data live on the
  SD, so reflashing firmware does **not** erase your data.
- **Install qFlipper on your computer** (Windows/macOS/Linux) from the official Flipper downloads page — Cyber
  Controller relies on this locally installed app to perform the install (**verify** you have a current qFlipper).
- **Drivers:** Windows installs the Flipper's USB CDC/DFU driver automatically with qFlipper; on Linux add the
  udev rules (or run qFlipper as packaged) so the device is accessible without root.
- **No board/variant choice:** unlike the ESP32 profiles there is one chip (`stm32wb55`) and one package, so
  there is no "which screen/board" decision to get wrong.

## 5. Flashing & First Run (via Cyber Controller — qFlipper install flow)
Cyber Controller does **not** esptool-flash the Flipper. The `flipper-momentum` profile uses the **qflipper
backend**: it resolves the latest GitHub release, downloads the firmware **package**, then launches your
**locally installed qFlipper** app to install it over USB DFU.

1. **Prereqs:** qFlipper installed locally; a microSD inserted in the Flipper; connect the Flipper by **USB-C
   data cable**.
2. Open Cyber Controller → **Flash** tab → **Firmware Profile:** `Flipper Momentum`. (There is no COM-port or
   chip-detect step here — the device is handled by qFlipper, not a serial flasher.)
3. Cyber Controller's **`github_release`** resolver queries `Next-Flip/Momentum-Firmware` for the **latest**
   release and downloads the **qFlipper package** asset (matching `.tgz` / `.tar.gz` / `.zip`).
4. Click **Install**. Cyber Controller **hands the downloaded package to the locally installed qFlipper app**,
   which puts the Flipper into DFU and writes the merged firmware to the STM32WB55. Close any **Web Updater /
   Flipper Lab** browser tab first — only one installer may talk to the Flipper at a time.
5. **First run:** the Flipper reboots into Momentum (new boot animation / menu). Before any SubGHz transmit,
   set/confirm your **Region** (the firmware gates TX by region). Your SD data is preserved.

> **Manual fallback (matches qFlipper's own flow):** if you ever install outside Cyber Controller, open qFlipper
> → connect the Flipper → **Install from file** → select the downloaded **`.tgz`**. (The `.zip` archive instead
> goes to `SD/update/<firmware-folder>` and is run from the Flipper's on-device file menu.)

## 6. Integrate into Cyber Controller
- **Profile:** `flipper-momentum` — **backend `qflipper`**, protocol `flipper`, `image_model: merged-single-bin`,
  `app_offset: 0x0`, resolver `github_release` (asset suffixes `.tgz` / `.tar.gz` / `.zip`), `core_id: momentum`,
  repo `Next-Flip/Momentum-Firmware`. This is fundamentally different from the esptool profiles: **no multi-file
  offsets, no chip auto-detect, no serial write** — the install is delegated to the external qFlipper app.
- **Install role vs. control role:** the profile's primary job is **firmware delivery** (download release →
  launch qFlipper to install). The Flipper's day-to-day operation happens on its **own on-device UI**. Over
  USB-C the Flipper also exposes a CLI on a serial CDC port; **verify** in your build whether Cyber Controller's
  `flipper` protocol parser drives that CLI for live control, or whether the profile is install-only.
- **No suicide/erase:** `supports_suicide: false` — the destructive erase/"suicide" action available to ESP32
  profiles is **not** offered here, and Dead Man's Switch wiping does not apply to this profile.
- **Updating:** re-run the Flash tab to pull the newest Momentum release (the resolver always targets
  `releases/latest`); SD-card data persists across updates.

## 7. Usage (end-to-end)
*(Authorized targets only; SubGHz/NFC/RFID transmit is region- and law-restricted.)*

1. **Install/update Momentum** via the Flash tab (Section 5); confirm the device boots into Momentum and a
   **Region** is set before transmitting.
2. **SubGHz:** *Read* an authorized remote/sensor, *Save* it, and *Send* (replay) only on permitted frequencies;
   **SubDriving** logs GPS coordinates with captures (pair a compatible GPS module on GPIO).
3. **NFC / 125 kHz RFID:** *Read* → *Save* → *Emulate* your own cards/fobs; **NFC Maker** writes Type 4 / NTAG4xx
   tags.
4. **Infrared:** use the **Universal Remote** or learn/replay IR codes for your own devices.
5. **BadUSB / Bad-Keyboard:** run **Ducky-style** HID payloads from the SD over USB or Bluetooth, with device
   spoofing (lab/authorized hosts only).
6. **BLE Spam / FindMy:** broadcast BLE advertisements for testing (these are intentionally disruptive —
   authorized environments only).
7. **GPIO/UART:** drive add-on modules (e.g. an ESP32 WiFi board) from the GPIO header; that companion board
   runs its own firmware.
8. **Customize:** install **Asset Packs** (themes/animations), tweak menu style/keybinds, and run **JavaScript**
   scripts from the SD via the Momentum App.

## 8. Troubleshooting
- **qFlipper doesn't see the Flipper / install can't start:** use a **data** USB-C cable (not charge-only); close
  any **Web Updater / Flipper Lab** browser tab (only one installer at a time); on Windows let qFlipper finish
  driver install; on Linux apply the udev rules. Cyber Controller can only delegate to qFlipper if qFlipper
  itself can connect.
- **Install/download fails in Cyber Controller:** confirm network access to GitHub (the `github_release` resolver
  must reach `api.github.com`) and that a `.tgz`/`.zip` asset exists on the latest release.
- **Stuck in DFU / blue screen after install:** reconnect and let **qFlipper recover/repair the firmware**
  (re-run the install); a bad cable mid-write is the usual cause. There is **no erase/suicide** for this profile.
- **SubGHz won't transmit:** the **region** isn't set or the frequency isn't allowed in your region — set the
  region and use a permitted band (TX is disabled out of the box by design).
- **Apps/asset packs missing or won't load:** check the **microSD** is FAT32 and seated; the app/asset-pack
  version must match the installed Momentum release — re-install matching assets.
- **Bricked / boot-loop:** recover with qFlipper; as a last resort reinstall from the **`.tgz`** package, or
  reflash **official firmware** then re-apply Momentum.

## 9. Sources
- Upstream firmware: <https://github.com/Next-Flip/Momentum-Firmware> (README, releases, wiki) and
  <https://momentum-fw.dev> (features, **Web Updater**, releases).
- Install methods (Web Updater / Flipper Lab / **qFlipper `.tgz`** / `.zip`): Momentum **Installation** wiki —
  <https://momentum-fw.dev/wiki/Installation>.
- Hardware specs: Flipper Zero docs — <https://docs.flipper.net/zero/development/hardware/tech-specs>.
- SubGHz regional TX restrictions: <https://docs.flipper.net/zero/sub-ghz/frequencies>.
- Purchasing: official store <https://shop.flipperzero.one/> and reseller list <https://flipperzero.one/how-to-buy>;
  EU via **Lab401** (<https://lab401.com/products/flipper-zero>); Japan via **Joom** (official store).
- Cyber Controller profile: `src/config/profiles/flipper_momentum.json` (backend `qflipper`, chip `stm32wb55`,
  `merged-single-bin`, `github_release` resolver, `supports_suicide: false`).
- **Verify** current price, qFlipper version, and the exact latest Momentum release/asset names at install time;
  vendor links and prices change.
