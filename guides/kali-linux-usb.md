# Kali Linux Live USB — Complete Guide

> **OS:** Kali Linux (Live) · **Upstream:** [kali.org](https://www.kali.org) (Debian-based, Offensive Security)
> **Type:** Live `amd64` ISO written whole-disk to a USB · **Cyber Controller catalog id:** `kali` (Software-OS tab, removable-USB writer; `verify_model = checksums_sig`)
> **This guide:** choose a USB → verify → flash to USB via Cyber Controller's Software-OS tab → boot → add (encrypted) persistence → troubleshoot UEFI/Secure Boot.

## 1. Overview
Kali Linux is a Debian-based **penetration-testing / security** distribution. The **Live** `amd64`
image boots straight from a USB stick into a full Kali desktop **without installing anything or
touching the machine's internal disk** — "a full bare metal Kali install without needing to alter an
already-installed operating system" (kali.org, §9). It ships the Kali toolset (network/recon, wireless,
web, exploitation and forensics tooling). It is *not* amnesic like Tails and it is *not* an installer
like Arch — it is a portable, optionally-persistent working environment. Cyber Controller's **Software-OS
tab** downloads the current Live image from the official mirror, integrity-verifies it, and writes it to a
confirmed removable USB. This is the OS/SD-writer path; it is **separate from the firmware Flash tab**
(esptool) used for ESP32 boards.

## 2. Legal & Safety
**Authorized testing only.** Kali bundles offensive tooling (scanners, exploit frameworks, wireless
attack tools). Running these against networks, systems, or people you do not own or lack **written
permission** to test is illegal in most jurisdictions (US: CFAA; EU and others similar). Kali itself is a
lawful, freely distributed operating system — possessing and learning it is legal; *unauthorized use* is
not. Use only your own lab gear or an explicit engagement scope. Two data-safety notes: (a) flashing
**erases the entire target USB**, and (b) Kali Live by default writes nothing to the host's internal
disk, but installer/persistence steps can — double-check the target device before you write.

## 3. Hardware & Purchasing
You only need **a USB flash drive (8GB+; Kali Live with persistence wants 16GB+)** and a 64-bit
(`amd64`/x86-64) PC to boot it.

| Item | Recommendation | Notes / search terms |
|------|----------------|----------------------|
| USB stick | **8GB minimum**, 16–32GB recommended | The Live ISO is >4GB, so 8GB barely fits the OS alone; a persistence partition needs the rest (kali.org persistence docs, §9). Search: "USB 3.2 flash drive 32GB" |
| Speed | **USB 3.x** flash drive (or USB-SSD) | Live runs from the stick — disk ops "may slow due to the utilized storage media" (kali.org, §9). A fast drive transforms the experience. |
| Endurance (optional) | Small **USB-SSD** in an enclosure | If you'll use persistence heavily, an SSD outlasts cheap flash and is much faster. |
| Host PC | Any x86-64 PC <~10 yrs old | Needs a USB-bootable BIOS/UEFI. |

Buy from any reputable retailer (Amazon, Best Buy, Micro Center, manufacturer stores — SanDisk, Samsung,
Kingston). There is no special hardware to purchase; **do not** download Kali from third-party "mirrors"
you find via ads — use the official site (§9). *Verify: counterfeit/oversized fake-capacity USB sticks
exist; test capacity (e.g. `f3`/`h2testw`) on suspiciously cheap drives.*

## 4. Making the bootable USB / partitioning notes
Cyber Controller writes the Live ISO **raw (block-for-block)** to the whole USB device — this is an
"isohybrid" image, so the resulting stick is bootable on both UEFI and legacy BIOS. Key facts:

- **The whole drive is overwritten.** Any existing partitions/data on the USB are destroyed. The image's
  own partition table replaces whatever was there.
- **ISO, written directly to the device** (not "burned" as files, not copied to a FAT32 partition). Tools
  like Rufus's "DD mode", `dd`, or Cyber Controller's writer all do the same raw write.
- **Persistence is a partition you add *after* writing the image** (see §7). Plan capacity now: image
  (>4GB) + your desired persistence space ≤ USB size, so pick 16GB+ if you want meaningful persistence.
- **Ventoy alternative:** instead of a dedicated single-OS stick, you can install **Ventoy** to a USB and
  then just *copy* the Kali `.iso` onto it (multi-ISO boot menu). That is a separate workflow from
  Cyber Controller's raw writer — convenient for carrying several ISOs, but it does not set up Kali
  persistence the same way. Search: "Ventoy multiboot USB".

## 5. Flash to USB via Cyber Controller's Software-OS tab
1. Insert the USB. Open Cyber Controller → **Software-OS** tab (labeled "Write a verified bootable
   operating system to a USB stick").
2. **Operating System:** pick **Kali Linux (Live)**. The description shows it is an `ISO` verified via
   `checksums_sig`.
3. **Check latest:** click it. Cyber Controller resolves the current release **live** by parsing
   `cdimage.kali.org/current/SHA256SUMS` (the `current` path always points at the newest release) and
   reads the image filename + SHA-256 from that file. If you have no network, tick **"Use bundled version
   (offline)"** to flash the version pinned in the catalog (offline fallback; at time of writing the
   pinned fallback is `2026.2` — the live check supersedes it).
4. **Target USB (removable):** select your stick. **Only removable drives are listed** (the writer refuses
   fixed/system disks and anything ≥256GB). Click **Refresh drives** if it's missing.
5. **(Pro mode) Use local image…** optionally point at a Kali `.iso` you already downloaded instead of
   fetching it. In **Simple mode** this and the offline toggle are hidden and it always fetches the latest.
6. Click **Flash OS** → confirm the "ERASE EVERYTHING" dialog. Cyber Controller downloads (if needed),
   **verifies** (see §6), writes the image, then **reads it back and re-hashes** to confirm the write.
7. On success: *"boot the target machine from this USB."*

**CLI equivalent:** `cyber-controller --flash-os kali [--os-image <local.iso>] [--os-target <device>]
[--offline] [--yes]`. The flash refuses to run without confirmation (the whole USB is erased).

## 6. Integration with the Software-OS tab (integrity verification)
- **Catalog entry** (`src/config/os_catalog.json`): id `kali`, `resolver: kali`, `image_type: iso`,
  `verify_model: checksums_sig`, `kali_variant: live-amd64`, official GPG fingerprint
  `827C 8569 F251 8CC6 77FE CA1A ED65 462E C8D5 E4C5`.
- **Live resolve:** the `kali` resolver fetches `SHA256SUMS` from `cdimage.kali.org/current/`, finds the
  `kali-linux-<ver>-live-amd64.iso` line, and takes its filename, version, and SHA-256. All OS downloads
  are restricted to an allowlist of official hosts (`cdimage.kali.org`, `kali.download`), HTTPS-only,
  with redirects re-validated (anti-SSRF).
- **Verification model — `checksums_sig` (this is why Kali is a two-step verify):**
  1. Cyber Controller downloads `SHA256SUMS` **and** `SHA256SUMS.gpg`, then verifies the OpenPGP signature
     on the `SHA256SUMS` file against the pinned Kali key fingerprint above. *A bad/foreign signature →
     the flash is refused.*
  2. It then hashes the ISO and confirms that SHA-256 **appears in the signed `SHA256SUMS`**. Mismatch →
     refused. This chains trust: signed list → list contains image hash → image matches.
  - If `gpg` isn't installed, the signature step is skipped with a NOTE and the SHA-256 check still runs;
    you'll see a warning that you should verify the signature for full assurance. An image with **no**
    valid signature *and* no checksum is written only after an explicit UNVERIFIED warning — avoid that.
- **Manual cross-check (recommended):** import the key and verify yourself (kali.org, §9):
  `gpg --keyserver hkps://keyserver.ubuntu.com --recv-key 827C8569F2518CC677FECA1AED65462EC8D5E4C5`
  then `gpg --verify SHA256SUMS.gpg SHA256SUMS` — look for *"Good signature from 'Kali Linux Archive
  Automatic Signing Key'"* with that key ID.
- **Post-write read-back:** after writing, the backend re-reads the bytes from the USB and compares the
  SHA-256 to the image — a hardware-level confirmation the stick is good.

## 7. Booting it / persistence
**Boot:** insert the stick, power on, open the firmware **boot menu** (commonly **F12 / F10 / F9 / Esc**,
or **Option** on Intel Macs — *verify your model*), and pick the USB. At the Kali boot menu choose **Live
(amd64)**. *Default live credentials are `kali` / `kali` — verify on the current Kali Live boot screen,
as defaults have changed across releases.*

**Persistence (optional, makes the stick remember changes):**
- Requires spare space on the USB (so the **8GB minimum / 16GB+ recommended**). After writing the image,
  add a new partition in the free space, format it **ext4 and label it `persistence`**, then create a file
  `persistence.conf` on it containing the single line `/ union` (kali.org persistence docs, §9):
  `sudo mkfs.ext4 -L persistence /dev/sdX3` then `echo "/ union" | sudo tee /mnt/usb/persistence.conf`.
- At boot, pick the **"Live USB Persistence"** menu entry to load your saved changes.
- **Encrypted persistence (LUKS):** Kali documents an *"Encrypted Persistence"* variant that puts the
  persistence partition inside a LUKS container so your saved data is protected at rest — strongly
  preferred if the stick holds engagement data. Follow Kali's dedicated encrypted-persistence guide for
  the `cryptsetup luksFormat` steps (§9).
- You can keep **multiple labeled stores** (e.g. `work`, `ctf`) and choose which to load via the
  `persistence-label=` boot parameter (edit the entry with Tab/`e`).

## 8. Troubleshooting (boot / UEFI / Secure Boot)
- **USB not in the boot menu:** enable USB boot in firmware; try a different port (rear/USB-2 port);
  re-seat the stick. Some firmwares hide USB until **Fast Boot** is disabled.
- **Secure Boot:** current Kali Live is signed for Secure Boot and generally boots with it on; if it
  refuses, **disable Secure Boot** in firmware (and re-enable after). *Verify against the Kali release
  notes for your version.*
- **UEFI vs Legacy/CSM:** if it won't boot, toggle between **UEFI** and **Legacy/CSM** boot modes — the
  isohybrid image supports both, but the firmware must be pointed at the matching one.
- **Black screen / hangs at boot:** at the boot menu press `e`/Tab and add `nomodeset` (graphics driver
  fallback) to the kernel line. *Verify the exact parameter for your GPU.*
- **Boots but feels slow:** that's expected on slow flash media (kali.org, §9) — use a USB 3.x drive or
  add persistence on faster media.
- **Persistence not loading:** confirm the partition label is exactly `persistence`, the file is
  `persistence.conf` containing `/ union`, and you selected the **Persistence** boot entry.
- **Flash failed / not removable:** the writer only lists removable drives <256GB — if your stick doesn't
  appear, it may be reported as fixed; try another stick/reader. Run the app **as Administrator** (Windows)
  or with the needed privileges (Linux/macOS) for raw disk access.
- **Verify failed (checksum/signature):** re-download — a corrupted download or a tampered mirror is the
  usual cause. Never write an image that fails verification.

## 9. Sources
- Get Kali (live image): <https://www.kali.org/get-kali/>
- Kali USB docs (writing, persistence, verification index): <https://www.kali.org/docs/usb/>
- Kali USB persistence (partition + `persistence.conf`): <https://www.kali.org/docs/usb/usb-persistence/>
- Verify Kali images securely (SHA256SUMS, `.gpg`, key fingerprint): <https://www.kali.org/docs/introduction/download-images-securely/>
- Cyber Controller catalog + writer: `src/config/os_catalog.json` (entry `kali`), `src/core/os_catalog.py`
  (resolver/verify), `src/core/backends/sd_backend.py` (removable-only write + read-back),
  `src/ui/qt/software_tab.py` (Software-OS tab).
- Verify the current Live version, file name, and credentials at flash time — releases roll forward and
  the tab resolves the latest live.
