# Arch Linux Install USB — Complete Guide

> **OS:** Arch Linux · **Upstream:** [archlinux.org](https://archlinux.org) (independent, rolling-release)
> **Type:** Installer **ISO** (`x86_64`) written whole-disk to a USB · **Cyber Controller catalog id:** `arch` (Software-OS tab; `verify_model = image_sig`)
> **This guide:** choose a USB → verify → flash via the Software-OS tab → boot the installer → install Arch to disk → troubleshoot UEFI/Secure Boot.

## 1. Overview
Arch Linux is a **minimal, rolling-release** general-purpose Linux for advanced users who want to build
their system from the ground up. Its USB image is an **installer ISO** (`x86_64`, ~**1.5GB**): it boots
into a **live installer environment** — a root shell with networking and the `archinstall` helper — from
which you **install Arch onto the machine's internal disk**. Unlike Kali Live (a portable working OS) or
Tails (an amnesic privacy OS), the Arch USB is fundamentally a **bootstrapping installer**, not a daily
"live" environment, and **not** designed for USB persistence. Cyber Controller's **Software-OS tab**
resolves the current Arch release from the official machine-readable feed, verifies its OpenPGP signature,
and writes it to a confirmed removable USB. This is the OS/USB-writer path, separate from the ESP32
firmware Flash tab.

## 2. Legal & Safety
Arch Linux is **free, lawful, general-purpose software** — nothing about it is restricted. The only real
risks are data-loss: (a) flashing the USB **erases the entire target USB**, and (b) the **installer writes
to and partitions a real disk** — during installation it is entirely possible to wipe the wrong drive.
**Back up first**, and triple-check the target disk name (`/dev/sdX`, `/dev/nvme0n1`, …) before
partitioning. The live installer environment runs as **root** with no password, so don't leave a booted
installer unattended on a sensitive machine.

## 3. Hardware & Purchasing
You need **a USB flash drive (8GB+)** and a 64-bit (`x86_64`) PC.

| Item | Recommendation | Notes (archlinux.org, §9) |
|------|----------------|---------------------------|
| USB stick | **8GB+** (the ISO is ~1.5GB) | The image easily fits 8GB; bigger is fine. **The whole stick is erased.** |
| Speed | USB 3.x | Faster installer boot and package I/O. |
| Host CPU | **x86_64** | The official ISO is x86_64 only (32-bit was dropped years ago). |
| Network | Wired or Wi-Fi | Arch installs packages **from the internet** during setup, so the target machine needs working networking. |

Any reputable USB stick works (SanDisk/Samsung/Kingston from Amazon, Best Buy, Micro Center, manufacturer
stores). **Download the ISO only from `archlinux.org/download/` or its official mirrors** — never an
unknown third-party mirror. *Verify: the download page lists official mirrors and the checksums/signature
to confirm whichever mirror you use.*

## 4. Making the bootable USB / partitioning notes
- **Raw, whole-disk write.** The Arch ISO is an isohybrid image written **block-for-block** to the entire
  USB; "the image can be directly written to a USB flash drive" with `dd`/raw writers
  (archlinux.org, §9). Its own partition table replaces anything on the stick.
- **No persistence partition.** Unlike Kali/Tails, you do **not** add persistence to the Arch stick — the
  installer is meant to be transient. Any state you want lives on the **target machine's disk** after you
  install. (The live environment is read-mostly; changes vanish on reboot.)
- **Don't extract the ISO onto a FAT32 stick** and don't "burn as files" — write the image directly, which
  is exactly what Cyber Controller's writer does.
- **Ventoy alternative:** because the Arch ISO is a transient installer, it is a **great Ventoy
  candidate** — install **Ventoy** to a USB once, then drop the `archlinux-*.iso` (and other installer
  ISOs) onto it and pick from a boot menu. That's a separate workflow from Cyber Controller's raw writer;
  handy if you juggle several installers. Search: "Ventoy multiboot USB". *Verify Ventoy + your firmware's
  Secure Boot behavior.*

## 5. Flash to USB via Cyber Controller's Software-OS tab

![Flashing connection diagram](../assets/connect-sd.png)

*Cyber Controller writes the image to a removable microSD/USB; then boot the device.*

1. Insert the USB. Open Cyber Controller → **Software-OS** tab.
2. **Operating System:** pick **Arch Linux**. Description shows `ISO`, verified via `image_sig`.
3. **Check latest:** Cyber Controller resolves the current release **live** from the official feed
   `archlinux.org/releng/releases/json/`, choosing the latest available release and building the ISO URL
   on the official mirror (`geo.mirror.pkgbuild.com`), plus the `.sig` URL and SHA-256. Offline? tick
   **"Use bundled version (offline)"** to use the pinned catalog image (offline fallback; at time of
   writing the pinned fallback is `2026.06.01` — the live check supersedes it).
4. **Target USB (removable):** select your stick (only removable drives <256GB are listed). **Refresh
   drives** if needed.
5. Click **Flash OS** → confirm the "ERASE EVERYTHING" dialog → it downloads, **verifies the OpenPGP
   signature / SHA-256** (see §6), writes the image, and **reads it back** to confirm.
6. On success: *"boot the target machine from this USB."*

**CLI equivalent:** `cyber-controller --flash-os arch [--os-image <local.iso>] [--os-target <device>]
[--offline] [--yes]`.

## 6. Integration with the Software-OS tab (integrity verification)
- **Catalog entry** (`src/config/os_catalog.json`): id `arch`, `resolver: arch`, `image_type: iso`,
  `verify_model: image_sig`, `arch_feed_url: https://archlinux.org/releng/releases/json/`,
  `arch_mirror_base: https://geo.mirror.pkgbuild.com`. The catalog's static `gpg_fingerprint` is
  **`null`** by design — Arch's signing key can rotate, so Cyber Controller takes the **`pgp_fingerprint`
  from the live release feed** for each release rather than hard-coding it.
- **Live resolve:** the `arch` resolver reads the JSON feed, picks the `latest_version` (falling back to
  the newest available release), and forms the ISO/`.sig` URLs on the official mirror. Downloads are
  HTTPS-only and restricted to an allowlist (`archlinux.org`, `geo.mirror.pkgbuild.com`,
  `*.mirror.pkgbuild.com`) with redirects re-validated (anti-SSRF).
- **Verification model — `image_sig`:** a **detached OpenPGP `.sig` over the ISO itself**. Cyber Controller
  fetches `archlinux-<ver>-x86_64.iso.sig`, runs `gpg --verify`, and accepts only a **valid signature
  matching the feed's fingerprint**; an invalid/foreign signature **refuses the write**. If `gpg` is
  absent it falls back to the published **SHA-256** (mismatch still refuses); a fully unverified image is
  written only after an explicit warning.
- **Manual verification (recommended)** per archlinux.org (§9) — the current release signing key is
  Pierre Schmitz, fingerprint `3E80 CA1A 8B89 F69C BA57 D98A 76A5 EF90 5444 9A5C` (*verify against the
  download page, as keys rotate*):
  `gpg --auto-key-locate clear,wkd --locate-external-key pierre@archlinux.org` then
  `gpg --verify archlinux-<ver>-x86_64.iso.sig archlinux-<ver>-x86_64.iso`. The page also publishes
  **SHA256** and **BLAKE2b** checksums.
- **Post-write read-back:** the backend re-reads the written bytes and re-hashes to confirm the USB matches
  the verified image.

## 7. Booting it / installing (no persistence)
**Boot the installer:** insert the stick, power on, open the firmware **boot menu** (commonly
**F12 / F10 / Esc**, or **Option** on older Intel Macs — *verify your model*), and pick the USB. The Arch
boot menu loads the live environment to a **root shell** (`root@archiso`).

There is **no persistence** here — instead you **install Arch to the internal disk**:
1. **Network:** wired auto-connects; for Wi-Fi use `iwctl` to associate (*verify the current tool*).
2. **Time/keyboard:** set keymap with `loadkeys`, confirm clock with `timedatectl`.
3. **Guided install:** run **`archinstall`** — the official menu-driven installer that handles
   partitioning, filesystem, bootloader, users, and desktop selection — or do a **manual install**
   (partition → `pacstrap` base → configure → install a bootloader). *Verify exact steps against the
   current Installation Guide on the Arch Wiki, since the process evolves.*
4. **Disk safety:** the installer **partitions and erases the target disk** — confirm you've selected the
   right drive. Then `reboot` and **remove the USB**; the machine now boots Arch from its own disk.

Any state you want kept lives on that installed disk; the USB is only the bootstrap medium and can be
re-used/re-flashed afterward.

## 8. Troubleshooting (boot / UEFI / Secure Boot)
- **USB not in the boot menu:** enable USB boot; try another port; disable **Fast Boot**. Use the one-time
  firmware **boot menu**.
- **Secure Boot:** the official Arch ISO is generally **not signed for Secure Boot** — if it won't boot,
  **disable Secure Boot** in firmware to boot the installer (you can configure Secure Boot for the
  installed system later). *Verify against the Arch Wiki for your firmware.*
- **UEFI vs Legacy/CSM:** modern Arch installs target **UEFI**; if the installer won't start, toggle
  UEFI/Legacy and retry. **Boot the installer in the same mode (UEFI) you intend to install in**, or the
  bootloader step can fail.
- **No network in the installer:** plug in Ethernet, or use `iwctl` for Wi-Fi; Arch **downloads packages
  during install**, so networking is required.
- **Installed system won't boot:** usually a **bootloader/UEFI entry** problem — re-check the ESP mount,
  bootloader install, and that firmware boots in UEFI mode. *Verify with the Arch Wiki's bootloader page.*
- **Black screen at installer boot:** edit the boot entry (press `e`/Tab) and add `nomodeset`.
  *Verify the parameter for your GPU.*
- **Flash failed / stick not removable:** the writer lists only removable drives <256GB; run the app with
  raw-disk privileges (Administrator on Windows; appropriate rights on Linux/macOS).
- **Verify failed (signature/checksum):** re-download from an official mirror — a corrupted download or a
  bad mirror is the usual cause. Don't boot an unverified installer.

## 9. Sources
- Arch download (ISO, ~1.5GB, checksums, PGP verify, mirrors): <https://archlinux.org/download/>
- Release feed (machine-readable, used to resolve latest): <https://archlinux.org/releng/releases/json/>
- Installation guide (boot, network, `archinstall`/manual install): search the **Arch Wiki** for
  "Installation guide" at <https://wiki.archlinux.org/>.
- Cyber Controller integration: `src/config/os_catalog.json` (entry `arch`), `src/core/os_catalog.py`
  (arch resolver via the JSON feed + `image_sig` verify), `src/core/backends/sd_backend.py`
  (removable-only write + read-back), `src/ui/qt/software_tab.py` (Software-OS tab).
- Verify the current Arch version and signing key/fingerprint at flash time — Arch is rolling-release, the
  ISO is rebuilt monthly, and the tab resolves the latest live.
