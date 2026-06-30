# Detecting & Locating RF Jammers — Defensive Guide

> **Scope:** how to **detect, characterize, and locate** an active RF jammer (Wi-Fi / Bluetooth-BLE / 2.4 GHz /
> RC-drone bands) using gear Cyber Controller already supports, plus an SDR. This is a **defensive / blue-team**
> guide — observing and reporting interference. It contains **no jamming instructions**.
> **Operating a jammer is illegal** (47 U.S.C. § 333 + worldwide equivalents); the lawful response to one is to
> **document and report it**, never to jam back.

## 1. Why this matters
Jamming is a denial-of-service against the RF layer: Wi-Fi drops, BLE locks/sensors stop reporting, cameras and
drone links cut out. Because it's invisible without instruments, the first job is simply **proving interference
is happening** (vs a flaky AP or congestion), then **classifying** it, then **finding the source**. Everything
here is passive observation — you are listening, not transmitting.

## 2. Two very different things people call "jamming"
Telling these apart is the whole game, because they look and are detected differently:

| | **Protocol attack** (e.g. deauth/disassoc flood, BLE-spam) | **RF noise jamming** (broadband energy) |
|---|---|---|
| What it is | Valid-but-malicious **frames** that kick clients off / drown a channel | Raw RF energy with **no valid frames** — saturates the receiver |
| How it looks | A flood of **deauthentication/disassociation** or beacon/probe frames | **Elevated noise floor**, collapsed SNR, near-total packet loss, no decodable frames |
| Detect with | A Wi-Fi/BLE sniffer that **counts frame types** (Marauder/GhostESP/ESP32, Kismet, Wireshark) | An **energy/noise** view — nRF24 channel scanner, SDR spectrum, an AP's noise-floor reading |
| Legality of source | Illegal (CFAA / unauthorized access-adjacent) | Illegal (willful interference, 47 U.S.C. § 333) |

A device like the BlueJammer-V2 spans both: its Wi-Fi mode is largely a **deauth flood** (frame-detectable),
while its nRF24-driven 2.4 GHz/BLE/RC modes are closer to **noise jamming** (energy-detectable).

## 3. Symptoms (the "am I being jammed?" checklist)
- Multiple, **different** devices lose a band **simultaneously** (not one flaky client).
- Wi-Fi clients **deauthenticate repeatedly** / can't stay associated, across SSIDs and APs.
- BLE sensors, tags, locks, or headphones **drop together** in one area.
- A drone/RC link or 2.4 GHz camera **cuts out** in a specific spot and recovers when you move away.
- The effect is **localized** — it weakens with distance/obstacles and strengthens toward a point.
- AP/router dashboards show a **rising noise floor** or plummeting SNR on the affected channel(s).

## 4. Detect it — Wi-Fi / 2.4 GHz (with Cyber Controller gear)
- **Count deauth/disassoc frames (protocol attack).** Put an ESP32 (Marauder / GhostESP / ESP32-DIV) on the
  affected channel and watch the sniffer: a steady stream of **deauth/disassociation** frames to broadcast or to
  many clients is a classic Wi-Fi "jam." Marauder's sniff modes (`sniffbeacon` / `sniffdeauth` / `sniffraw`) and
  GhostESP/ESP32-DIV capture modes surface these. In Wireshark/Kismet, filter
  `wlan.fc.type_subtype == 0x0c` (deauth) / `0x0a` (disassoc) and watch the rate.
- **Watch packet/beacon loss + RSSI (either type).** Scan APs across channels; a channel where **every** AP's
  beacons vanish or RSSI collapses while neighbors are fine points to targeted interference on that channel.
- **Energy scan 2.4 GHz (noise jamming).** An **nRF24L01+** "channel scanner" (or the scanner mode on ESP32-DIV
  / Bit-Pirate-class boards) sweeps the 126 nRF channels and shows **energy where there should be none** — a
  wide, persistent energy hump with no decodable Wi-Fi/BLE is the signature of a noise jammer.
- **Channel hopping vs fixed.** Note whether the interference is **fixed** to a channel/band or **hops** — it
  guides both classification and mitigation (e.g. moving APs to a clean channel buys time against a fixed jammer).

## 5. Detect it — Bluetooth / BLE
- Run a **BLE scan** (Marauder `blescan`, GhostESP/ESP32-DIV BLE scan) in a known-good area, then in the suspect
  area: a sharp drop in advertisements, or known beacons disappearing, indicates BLE-band interference.
- **BLE-spam vs noise:** a flood of bogus advertising packets (pairing-spam) is a *protocol* attack visible as
  excess adv frames; a silent, total BLE blackout with elevated 2.4 GHz energy is *noise* jamming (see §4 energy
  scan — BLE shares 2.4 GHz with Wi-Fi/nRF).

## 6. Detect it — broadband / unknown (SDR)
A cheap **RTL-SDR** (or HackRF/etc.) with a waterfall (SDR#, SDRangel, CubicSDR, Universal Radio Hacker) is the
most general detector:
- Park on **2.4 GHz / 5 GHz / 433–915 MHz / GNSS L1 (1575.42 MHz)** as relevant and watch the **waterfall**.
- **Noise jamming** shows as a bright, persistent, wide band of energy with no structure; **sweep jammers** show
  a diagonal sweeping line; **tone jammers** show a fixed carrier.
- GNSS/GPS jamming (relevant to drones) shows as energy around **1575.42 MHz** and a receiver that loses lock —
  detect with any GPS module's sat-count/fix status dropping to zero in a localized area.

## 7. Locate the source (direction finding)
Once you've confirmed interference, find it **passively** by measuring how signal strength changes as you move:
1. **Measure RSSI/energy** at several spots (the sniffer's RSSI, the SDR's power reading, or the nRF energy level).
2. **Gradient search:** the reading **rises** as you approach the source. Walk the gradient.
3. **Directional antenna:** a Yagi/patch (or even cupping a whip) makes the peak **directional** — take bearings
   from 2–3 positions and triangulate the intersection.
4. **Attenuate on purpose:** if the reading pegs everywhere, add attenuation (distance, your body, a small
   shield) so the peak becomes distinguishable again.
5. **Confirm physically/visually** — a small board with multiple antennas, an OLED, a battery pack. Do not touch
   or disable other people's property; involve the site owner / authorities.

## 8. What to do about it (lawfully)
- **Do not jam back.** Retaliatory jamming is the same federal crime — and adds your signal to the problem.
- **Document:** timestamps, affected bands/channels, RSSI/energy readings, captures (pcap of the deauth flood,
  SDR screenshots), and a rough location/bearings.
- **Mitigate temporarily:** move critical Wi-Fi to a clean channel/band (5 GHz if 2.4 is jammed), use wired
  links for anything critical, and physically distance assets from the source.
- **Report:** in the US, file with the **FCC Enforcement Bureau** (jamming is actively prosecuted under
  47 U.S.C. § 333); elsewhere, your national spectrum regulator. For a crime in progress affecting safety
  (e.g. drone/GPS jamming near aircraft), contact law enforcement.

## 9. Tools at a glance
| Need | Use |
|---|---|
| Count deauth/BLE-spam frames | ESP32 Marauder / GhostESP / ESP32-DIV sniffers; Wireshark; Kismet |
| 2.4 GHz energy sweep (noise) | nRF24L01+ channel scanner; ESP32-DIV / Bit-Pirate scan modes |
| Broadband / GNSS / SubGHz | RTL-SDR or HackRF + waterfall (SDR#, SDRangel, CubicSDR, URH) |
| RSSI/SNR + noise floor | Your AP/router dashboard; the sniffer's RSSI; SDR power meter |
| Direction finding | Directional antenna (Yagi/patch) + RSSI gradient + triangulation |
| GPS jamming | Any GPS/NMEA module — watch sat count / fix drop to zero locally |

## 10. Sources & further reading
- **47 U.S.C. § 333** (willful interference) and **FCC jammer-enforcement guidance** (Parts 2/15) — operating,
  marketing, or selling jammers is prohibited; report interference to the FCC Enforcement Bureau.
- Wi-Fi management-frame analysis: IEEE 802.11 deauth/disassoc subtypes; Wireshark `wlan.fc.type_subtype`; Kismet.
- 2.4 GHz energy scanning: nRF24L01+ channel-scanner technique (carrier-detect across the 126 channels).
- SDR detection: RTL-SDR project docs; SDRangel / CubicSDR / Universal Radio Hacker waterfall analysis.
- See also: [BlueJammer-V2 (BW16 controller)](bluejammer-bw16.md) and [BlueJammer-V2 (ESP32 engine)](bluejammer-esp32.md)
  — the device this defends against, documented flash-and-study-only.
- Verify current law in your jurisdiction before any RF work; statutes and tool availability change.
