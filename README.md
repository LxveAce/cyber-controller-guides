# Cyber Controller — Hardware Guides

In-depth, project-by-project guides for **every firmware and target** that
[Cyber Controller](https://github.com/LxveAce/cyber-controller) can flash and control. Each guide is a
complete walkthrough: **what to buy → how to build it → how to flash & run it → how to integrate it into
Cyber Controller → troubleshooting**, with a downloadable **PDF**.

> **Authorized use only.** Many of these tools transmit on regulated bands or perform offensive actions
> (deauth, evil-AP, RF). Use them only on hardware and networks you own or are explicitly authorized to
> test. Some entries are **detector-only** or **lab-only/illegal-to-operate** — each guide says which.
> Where a fact couldn't be verified it is marked `verify:` rather than asserted; never-invented purchase
> links are given as vendor + search string. See [DISCLAIMER.md](DISCLAIMER.md) for the full disclaimer
> and acceptable-use terms.

Each guide also notes the exact Cyber Controller **profile** and backend, the supported **chips/boards**,
and the upstream project. Counts and facts are grounded in the app's shipped profiles.


_📄 = download the complete-walkthrough PDF · ⚠ = lab-only / illegal-to-operate · 🛡 = detector/defensive-only_


**30 guides** across 7 categories.


## ESP32

ESP32-family firmware (flashed over USB by Cyber Controller's esptool backend).

| Project | Chips / Backend | Upstream | Guide | PDF |
|---------|-----------------|----------|-------|-----|
| **[AirTag Scanner 🛡](guides/airtag-scanner.md)** | esp32, esp32s3 | [MatthewKuKanich/ESP32-AirTag-Scanner](https://github.com/MatthewKuKanich/ESP32-AirTag-Scanner) | [guide](guides/airtag-scanner.md) | [📄](pdf/airtag-scanner.pdf) |
| **[BlueJammer-V2 - ESP32 engine ⚠](guides/bluejammer-esp32.md)** | esp32 | [EmenstaNougat/BlueJammer-V2](https://github.com/EmenstaNougat/BlueJammer-V2) | [guide](guides/bluejammer-esp32.md) | [📄](pdf/bluejammer-esp32.pdf) |
| **[Bruce](guides/bruce.md)** | esp32, esp32c5, esp32c6, esp32s3 | [BruceDevices/firmware](https://github.com/BruceDevices/firmware) | [guide](guides/bruce.md) | [📄](pdf/bruce.pdf) |
| **[Chasing Your Tail NG 🛡](guides/chasing-your-tail-ng.md)** | esp32 | [ArgeliusLabs/Chasing-Your-Tail-NG](https://github.com/ArgeliusLabs/Chasing-Your-Tail-NG) | [guide](guides/chasing-your-tail-ng.md) | [📄](pdf/chasing-your-tail-ng.pdf) |
| **[ESP32 Bit Pirate](guides/esp32-bit-pirate.md)** | esp32s3 | [geo-tp/ESP32-Bit-Pirate](https://github.com/geo-tp/ESP32-Bit-Pirate) | [guide](guides/esp32-bit-pirate.md) | [📄](pdf/esp32-bit-pirate.pdf) |
| **[ESP32 Marauder](guides/marauder.md)** | esp32, esp32c5, esp32s2, esp32s3 | [justcallmekoko/ESP32Marauder](https://github.com/justcallmekoko/ESP32Marauder) | [guide](guides/marauder.md) | [📄](pdf/marauder.pdf) |
| **[ESP32-DIV](guides/esp32-div.md)** | esp32, esp32s3 | [cifertech/ESP32-DIV](https://github.com/cifertech/ESP32-DIV) | [guide](guides/esp32-div.md) | [📄](pdf/esp32-div.pdf) |
| **[Flock-You 🛡](guides/flock-you.md)** | esp32s3 | [colonelpanichacks/flock-you](https://github.com/colonelpanichacks/flock-you) | [guide](guides/flock-you.md) | [📄](pdf/flock-you.pdf) |
| **[GhostESP](guides/ghost-esp.md)** | esp32, esp32c5, esp32c6, esp32s3 | [GhostESP-Revival/GhostESP](https://github.com/GhostESP-Revival/GhostESP) | [guide](guides/ghost-esp.md) | [📄](pdf/ghost-esp.pdf) |
| **[HaleHound](guides/halehound.md)** | esp32 | [JesseCHale/HaleHound-CYD](https://github.com/JesseCHale/HaleHound-CYD) | [guide](guides/halehound.md) | [📄](pdf/halehound.pdf) |
| **[Hydra32 (ESP32-Deauther)](guides/hydra32.md)** | esp32 | [SameerAlSahab/ESP32-Deauther](https://github.com/SameerAlSahab/ESP32-Deauther) | [guide](guides/hydra32.md) | [📄](pdf/hydra32.pdf) |
| **[MCLite (MeshCore)](guides/mclite.md)** | esp32s3 | [laserir/MCLite](https://github.com/laserir/MCLite) | [guide](guides/mclite.md) | [📄](pdf/mclite.pdf) |
| **[Meshtastic](guides/meshtastic.md)** | esp32s3 | [meshtastic/firmware](https://github.com/meshtastic/firmware) | [guide](guides/meshtastic.md) | [📄](pdf/meshtastic.pdf) |
| **[MinigotchiV3](guides/minigotchi-v3.md)** | esp32, esp32s3 | [dj1ch/minigotchi-V3](https://github.com/dj1ch/minigotchi-V3) | [guide](guides/minigotchi-v3.md) | [📄](pdf/minigotchi-v3.pdf) |
| **[OUI-Spy](guides/oui-spy.md)** | esp32s3 | [colonelpanichacks/oui-spy-unified-blue](https://github.com/colonelpanichacks/oui-spy-unified-blue) | [guide](guides/oui-spy.md) | [📄](pdf/oui-spy.pdf) |
| **[Sky-Spy 🛡](guides/sky-spy.md)** | esp32c6, esp32s3 | [colonelpanichacks/Sky-Spy](https://github.com/colonelpanichacks/Sky-Spy) | [guide](guides/sky-spy.md) | [📄](pdf/sky-spy.pdf) |
| **[T-REX](guides/t-rex.md)** | esp32s3 | [abdallahnatsheh/T-REX-FIRMWARE](https://github.com/abdallahnatsheh/T-REX-FIRMWARE) | [guide](guides/t-rex.md) | [📄](pdf/t-rex.pdf) |

## RTL8720

Realtek RTL8720DN / BW16 (AmebaD) — dual-band 2.4/5 GHz, flashed via the rtl8720 backend.

| Project | Chips / Backend | Upstream | Guide | PDF |
|---------|-----------------|----------|-------|-----|
| **[BlueJammer-V2 - BW16 controller ⚠](guides/bluejammer-bw16.md)** | rtl8720 | [EmenstaNougat/BlueJammer-V2](https://github.com/EmenstaNougat/BlueJammer-V2) | [guide](guides/bluejammer-bw16.md) | [📄](pdf/bluejammer-bw16.pdf) |
| **[BW16 Deauther (RTL8720DN)](guides/bw16-deauther.md)** | rtl8720 | [vampel/vampel.github.io](https://github.com/vampel/vampel.github.io) | [guide](guides/bw16-deauther.md) | [📄](pdf/bw16-deauther.pdf) |

## Flipper Zero

Flipper Zero custom firmware (Cyber Controller hands the package to qFlipper to install).

| Project | Chips / Backend | Upstream | Guide | PDF |
|---------|-----------------|----------|-------|-----|
| **[Flipper Zero - Momentum](guides/flipper-momentum.md)** | stm32wb55 | [Next-Flip/Momentum-Firmware](https://github.com/Next-Flip/Momentum-Firmware) | [guide](guides/flipper-momentum.md) | [📄](pdf/flipper-momentum.pdf) |
| **[Flipper Zero - Unleashed](guides/flipper-unleashed.md)** | stm32wb55 | [DarkFlippers/unleashed-firmware](https://github.com/DarkFlippers/unleashed-firmware) | [guide](guides/flipper-unleashed.md) | [📄](pdf/flipper-unleashed.pdf) |

## SBC / SD

Single-board-computer images written to a microSD/USB (removable-only writer).

| Project | Chips / Backend | Upstream | Guide | PDF |
|---------|-----------------|----------|-------|-----|
| **[Kali Linux ARM](guides/kali-arm.md)** | sd | [link](https://kali.download/arm-images/) | [guide](guides/kali-arm.md) | [📄](pdf/kali-arm.pdf) |
| **[Pwnagotchi](guides/pwnagotchi.md)** | sd | [link](https://github.com/jayofelony/pwnagotchi) | [guide](guides/pwnagotchi.md) | [📄](pdf/pwnagotchi.pdf) |
| **[RaspyJack](guides/raspyjack.md)** | sd | [link](https://github.com/7h30th3r0n3/RaspyJack) | [guide](guides/raspyjack.md) | [📄](pdf/raspyjack.pdf) |

## SBC / ADB

Device firmware installed over ADB.

| Project | Chips / Backend | Upstream | Guide | PDF |
|---------|-----------------|----------|-------|-----|
| **[RayHunter 🛡](guides/rayhunter.md)** | adb | [link](https://github.com/EFForg/rayhunter) | [guide](guides/rayhunter.md) | [📄](pdf/rayhunter.pdf) |

## Software-OS

Bootable PC/USB operating systems (Software-OS tab; SHA-256 + OpenPGP verified).

| Project | Chips / Backend | Upstream | Guide | PDF |
|---------|-----------------|----------|-------|-----|
| **[Arch Linux (USB)](guides/arch-usb.md)** | sd/usb-writer | [link](https://archlinux.org/download/) | [guide](guides/arch-usb.md) | [📄](pdf/arch-usb.pdf) |
| **[Kali Linux (USB)](guides/kali-linux-usb.md)** | sd/usb-writer | [link](https://www.kali.org/get-kali/) | [guide](guides/kali-linux-usb.md) | [📄](pdf/kali-linux-usb.pdf) |
| **[Tails OS (USB)](guides/tails-usb.md)** | sd/usb-writer | [link](https://tails.net/) | [guide](guides/tails-usb.md) | [📄](pdf/tails-usb.pdf) |

## Meta

Bring-your-own / utility profiles.

| Project | Chips / Backend | Upstream | Guide | PDF |
|---------|-----------------|----------|-------|-----|
| **[Custom / local .bin](guides/custom-local-bin.md)** | esptool | — | [guide](guides/custom-local-bin.md) | [📄](pdf/custom-local-bin.pdf) |
| **[Jammer Detection 🛡](guides/jammer-detection.md)** | — | — | [guide](guides/jammer-detection.md) | [📄](pdf/jammer-detection.pdf) |

---

Built for the Cyber Controller project by **LxveAce**. Guides are MIT-licensed; the firmwares themselves are owned by their respective upstream authors (see each guide's Sources). Vendor links/prices change — verify at purchase time.

Regenerate this index: `python tools/build_readme.py` · Rebuild PDFs: `python tools/build_pdfs.py`
