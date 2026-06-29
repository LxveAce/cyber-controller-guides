# Kali Linux ARM (Raspberry Pi) — Complete Hardware Guide

> **Distro:** Kali Linux ARM (64-bit / arm64) · **Upstream:** [kali.org](https://www.kali.org/) (Kali Linux / OffSec — GPL + mixed FOSS licenses)
> **Target hardware:** Raspberry Pi 3 / 4 / 400 / 5 / 500 (arm64) and Pi Zero 2 W · **Cyber Controller profile:** `kali-arm` (`sd` backend — removable-only image writer, no serial protocol)
> **This guide:** purchase → build the deck → write the SD image via Cyber Controller → integrate → use → troubleshoot.

## 1. Overview
Kali Linux ARM is the full Kali penetration-testing distribution pre-built as a flashable disk image for
Raspberry Pi and other ARM single-board computers. Unlike a single-purpose firmware, it is a complete
Debian-based OS carrying Kali's toolset (Nmap, Metasploit, Aircrack-ng, Wireshark, Burp Suite, the
wireless/Nexmon stack, etc.) on a credit-card-sized board. On a Pi with a touchscreen and battery it
becomes a self-contained **cyberdeck** — the Cyber Controller cyberdeck OS. Cyber Controller's role here
is narrow but important: it downloads the official Kali ARM image and **writes it to a microSD card**
through its hardened, removable-only SD/Software-OS writer. After that, the Pi boots and runs Kali
directly — Cyber Controller does not drive it over a serial link (the profile has no protocol).

## 2. Legal & Safety
**Authorized testing only.** Kali is an offensive-security distribution: it ships tools that scan, exploit,
deauthenticate, capture handshakes, and crack credentials. Running any of these against networks, systems,
or people you do not own or have **explicit written permission** to test is illegal in most jurisdictions
(US: CFAA/Wiretap Act/FCC; EU and others similar). Use Kali only on your own lab gear or under a signed
engagement scope. Two hardware-specific cautions: (1) the SD write in §5 **erases the entire target drive**
— pick the right removable device; (2) onboard/USB WiFi monitor-mode and injection transmit on regulated
bands — passive *and* active radio use may be restricted where you live. Change the default password
immediately (§7); a Kali box on `kali/kali` is itself a liability.

## 3. Hardware & Purchasing
Cyber Controller's `kali-arm` profile fetches the **64-bit (arm64)** generic Raspberry Pi image, so target
an arm64-capable Pi. Pick by form factor:

| Tier | Board | Why | Where to buy (search terms) |
|------|-------|-----|------------------------------|
| Best cyberdeck | **Raspberry Pi 5 (4GB/8GB)** | Fastest Pi; best for the full toolset + touchscreen deck | "Raspberry Pi 5 8GB" — official resellers: **PiShop**, **Adafruit**, **CanaKit**, **The Pi Hut** |
| Reliable workhorse | **Raspberry Pi 4 (4GB/8GB)** | Mature, well-supported, cheaper than Pi 5 | "Raspberry Pi 4 Model B 4GB" — same resellers |
| All-in-one keyboard | **Raspberry Pi 400 / 500** | Pi built into a keyboard — instant portable rig | "Raspberry Pi 400 kit" / "Raspberry Pi 500" |
| Pocket / drop box | **Raspberry Pi Zero 2 W** | Tiny, low-power; great headless implant (Pi-Tail variant) | "Raspberry Pi Zero 2 W" — see verify note below |

**Display for a deck:** any HDMI monitor works, but for a true cyberdeck use a small touchscreen — e.g. the
**official Raspberry Pi Touch Display**, or a **Waveshare / SunFounder HDMI/DSI touchscreen** (search
"Raspberry Pi touchscreen 5 inch HDMI" or "Waveshare DSI touch display"). **microSD card:** the Kali docs
require **"at least 16GB capacity"** and **"Class 10 cards are highly recommended."** For the full toolset
plus updates, buy **32GB+** with an **A1/A2** application-class rating — e.g. **Samsung EVO Plus**,
**SanDisk Extreme**, or **SanDisk Ultra** (search "Samsung EVO Plus 64GB microSD A2" / "SanDisk Extreme
microSD"). **Accessories:** a quality USB-C (Pi 4/5) or micro-USB (Zero 2 W) power supply rated for the
board, a **USB microSD card reader** for writing from your PC, optional case/heatsink/fan, and — for
wireless work — a **USB WiFi adapter that supports monitor mode + injection** (verify chipset; common
recommendations: Atheros AR9271, Realtek RTL8812AU). Onboard Pi WiFi can now do monitor mode via Nexmon
(see §7).

> **verify:** Cyber Controller's profile pattern matches the **arm64** Raspberry Pi image. The **Pi Zero 2 W**
> and the **32-bit (armhf) Pi 2/3/4/400** images are published under different filenames on kali.org; if you
> target those, confirm the downloaded asset name before writing (the Zero 2 W has its own dedicated image,
> including a "Pi-Tail" build). See §9.

## 4. Building / Assembly
- **Bare Pi (3/4/5):** seat it in a case with a heatsink (Pi 4/5 run hot under load). No soldering.
- **Pi 400/500:** nothing to assemble — Pi-in-a-keyboard. Add an HDMI display and power.
- **Cyberdeck build:** mount the Pi + touchscreen (HDMI or DSI ribbon) and, optionally, a LiPo/UPS HAT and
  keyboard into an enclosure. DSI/official touch displays are plug-and-play under Kali; cheap HDMI panels
  may need a `config.txt` resolution/overscan tweak (verify per panel).
- **microSD prep (for the host PC that runs Cyber Controller):** insert the microSD into a **USB card
  reader** so it enumerates as a **removable** drive — Cyber Controller's writer refuses fixed/system disks
  and anything ≥ 256 GB by design (§6). No special USB-serial driver is needed (this is block storage, not
  a serial board).
- **Wireless add-on:** if using a USB WiFi adapter, plug it into a USB port; you'll bring up monitor mode
  in software after first boot (§7).

## 5. Write the Kali ARM image via Cyber Controller

![Flashing connection diagram](../assets/connect-sd.png)

*Cyber Controller writes the image to a removable microSD/USB; then boot the device.*

Cyber Controller writes the compressed Kali `.img.xz` straight to the microSD — no separate imager needed.
1. Insert the **microSD via a USB card reader** so it shows up as a removable drive. On Windows, run Cyber
   Controller **as Administrator** (raw disk writes need it); on Linux/macOS the write uses `dd` and will
   prompt for `sudo`.
2. Open Cyber Controller → the **SD / Software-OS** imaging flow and select the **Kali Linux ARM64** image
   profile (`kali-arm`).
3. **Scan/refresh removable drives**, then **select your microSD** from the detected list. Double-check the
   device path and size — **this operation erases the whole card.** Fixed/system disks never appear.
4. **Confirm** the destructive write (the backend will not proceed without an explicit confirmation — a
   built-in safety invariant). Cyber Controller then runs the full pipeline automatically:
   **download** the latest `kali-linux-<version>-raspberry-pi-arm64.img.xz` from `kali.download`
   (an allowlisted host) → **stream-decompress** the `.xz` (never loading the whole image into RAM) →
   **block-write** the raw `.img` to the card → **SHA-256 verify** the write by reading it back.
5. When it reports verification passed / "SD card is ready," eject the reader, move the microSD into the
   Pi, attach power (and a display if not going headless), and boot. First boot resizes the filesystem and
   may reboot once.

## 6. Integrate into Cyber Controller (SD-image)
- **Profile:** `kali-arm` — `backend: "sd"`, `protocol: null`. Because there is no serial protocol, this is
  a **one-shot imaging target**, not a live-controlled device: there's no Devices/Targets/terminal session,
  no Cross-Comm routing, and no Dead Man's Switch for it (those apply to serial firmware like Marauder).
  Integration *is* the write pipeline.
- **Backend routing:** the flash engine maps `backend: "sd"` to the SD-image handler, which calls into
  `src/core/backends/sd_backend.py`. That module's `PI_IMAGE_PROFILES["kali-arm"]` defines the source:
  `download_url = https://kali.download/arm-images/` and the asset filter
  `kali-linux.*arm64.*\.img\.xz$` (so it selects the 64-bit Raspberry Pi image).
- **Shared writer with the Software-OS tab:** the Pi SD image and the **Software-OS tab** (which writes
  desktop/USB OS ISOs like Kali installer, Tails, and Arch) use the **same hardened removable-only writer**
  in `sd_backend` — Windows raw `PhysicalDriveN` via ctypes, Linux/macOS via `dd`. Think of `kali-arm` as
  the *Raspberry Pi (SD)* sibling of the Software-OS *desktop (USB)* images, sharing one
  download → decompress → write → verify path.
- **Safety invariants (enforced before any byte is written):** target must be **removable** (never a
  fixed/system disk), must be **< 256 GB** (SD sanity ceiling), and the caller must pass **`confirmed=True`**.
  Downloads are restricted to an **HTTPS allowlist** (`kali.download` / `*.kali.download`, plus GitHub hosts
  for the other Pi profiles), with redirect re-validation and filename path-traversal checks.
- **Versioning:** there is no GitHub release for Kali ARM — images come straight from `kali.download`, and
  Cyber Controller resolves the latest matching arm64 image at write time. Prefer the latest **point
  release** (e.g. `2026.x`) unless you specifically need a weekly build.

## 7. Usage (end-to-end)
1. **First boot & login:** Kali ARM ships with **default credentials `kali` / `kali`** (the non-root default
   in place since Kali **2020.1** for pre-built ARM/VM images). Log in at the desktop or console.
2. **Lock it down immediately:** run `passwd` to change the `kali` password. For a network-exposed box,
   also regenerate SSH host keys (verify: e.g. `sudo dpkg-reconfigure openssh-server` or remove
   `/etc/ssh/ssh_host_*` then `sudo ssh-keygen -A`).
3. **Update first:** `sudo apt update && sudo apt full-upgrade -y` then reboot — Kali moves fast and the
   image may be weeks old.
4. **Headless / SSH:** to run without a monitor, pre-stage WiFi by adding a `wpa_supplicant.conf` to the
   card's **first (boot) partition** before first boot: `wpa_passphrase YOURNETWORK > wpa_supplicant.conf`
   (per the Kali docs). Then connect over SSH as `kali@<pi-ip>`. **verify:** whether the SSH service is
   enabled by default on the ARM image; if it isn't, attach a screen/keyboard once and run
   `sudo systemctl enable --now ssh`.
5. **Wireless testing:** onboard Pi WiFi can do **monitor mode + injection via Nexmon** on supported boards
   (Pi 5, Pi 4 32/64-bit, 3B, 3B+, Zero W, Zero 2 W). Since **Kali 2025.1** this is packaged — install with
   `sudo apt install -y brcmfmac-nexmon-dkms firmware-nexmon` then reboot. Otherwise use a USB WiFi adapter
   with monitor-mode support. **verify:** current Nexmon status for your exact board/kernel — older Pi 5
   images shipped *without* internal-WiFi Nexmon and required a USB adapter.
6. **Bluetooth (Pi 4 etc.):** if needed, enable it with `sudo systemctl enable --now hciuart.service` and
   `sudo systemctl enable --now bluetooth.service` (audio defaults to HDMI, not the 3.5mm jack).
7. **Run your tools** (authorized scope only): standard Kali — `nmap`, `aircrack-ng`/`airodump-ng`,
   `wireshark`, `msfconsole`, etc. On Pi 5, kernel headers for DKMS builds are named
   `linux-headers-rpi-2712` and `linux-headers-rpi-v8` (not the generic Debian names).

## 8. Troubleshooting
- **microSD not listed in Cyber Controller:** use a **USB card reader** (built-in slots may read as fixed);
  re-scan; on Windows launch **as Administrator**; confirm the card is **< 256 GB**.
- **Write fails / permission denied:** Windows needs Administrator for raw disk access; Linux/macOS needs
  the `sudo`/root `dd` prompt to succeed. Close any Explorer/Finder window holding the card.
- **Verification MISMATCH after write:** usually a flaky card or reader — re-seat, try another reader/card,
  and re-write. A failed verify means the card may be corrupt; don't boot it.
- **Pi shows no display / rainbow screen / boot loop:** re-write the image; confirm an arm64-capable model
  (Pi 3/4/400/5/500); for cheap HDMI touchscreens, set the panel resolution in `config.txt` (verify per
  panel). Try a known-good power supply — under-volting causes instability on Pi 4/5.
- **Can't SSH in headless:** verify SSH is enabled (step 4); confirm the `wpa_supplicant.conf` was placed
  on the **boot** partition and the network name/passphrase are correct; check the Pi got a DHCP lease.
- **Onboard WiFi won't go to monitor mode:** install the Nexmon packages (§7) and reboot, or fall back to a
  USB adapter with a monitor-mode-capable chipset.
- **Login rejected:** defaults are **`kali` / `kali`**; if you already changed it and forgot, re-write the
  card (no in-place recovery on a fresh image).

## 9. Sources
- Kali ARM image downloads & model list: <https://www.kali.org/get-kali/> (Get Kali → ARM / Raspberry Pi).
- Kali on ARM docs hub: <https://www.kali.org/docs/arm/> and the per-model pages
  (<https://www.kali.org/docs/arm/raspberry-pi-4/>, <https://www.kali.org/docs/arm/raspberry-pi-5/>,
  <https://www.kali.org/docs/arm/raspberry-pi-zero-2-w/>) — microSD/Class 10, `.img.xz`, `dd`/Imager,
  `wpa_supplicant.conf` headless, audio/Bluetooth notes.
- Default credentials (`kali`/`kali`, since 2020.1): <https://www.kali.org/docs/introduction/default-credentials/>.
- Nexmon onboard-WiFi monitor mode (2025.1 packaging): <https://www.kali.org/blog/raspberry-pi-wi-fi-glow-up/>.
- Cyber Controller profile: `src/config/profiles/kali_arm.json` (`id: kali-arm`, `backend: sd`,
  `protocol: null`, image host `kali.download/arm-images/`).
- Cyber Controller SD writer & safety invariants: `src/core/backends/sd_backend.py`
  (`PI_IMAGE_PROFILES["kali-arm"]`, arm64 `.img.xz` pattern, removable-only / <256 GB / `confirmed=True`,
  HTTPS allowlist) and the Software-OS tab `src/ui/qt/software_tab.py` (shared removable-only writer).
- Verify current image filenames, prices, board availability, and Nexmon status at use time — kali.org
  versions and vendor links change.
