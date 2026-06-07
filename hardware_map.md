# Arturia KeyLab MKII - Hardware Map (Standard MCU Modus)

**Zusammenfassung der Ports:**
* **Keys Port:** Sendet Klaviatur, Pads und Mod-Wheel.
* **DAW Port:** Sendet alle Steuerelemente (Transport, Mixer, Navigation).

---

## 1. Performance Sektion (Ganz Links)
*Senden auf dem Keys Port.*

| Element | Typ | Data1 (ID) | Bemerkung |
| :--- | :--- | :--- | :--- |
| Pitch Bend Rad | Pitch Bend | 80 | Kanal 1 |
| Mod Wheel | CC | 1 | Kanal 1 |
| Octave - / + | Intern | - | Ändert interne Hardware-Logik |
| Chord Button | Intern | - | Ändert interne Hardware-Logik |
| Transpose | Intern | - | Ändert interne Hardware-Logik |

---

## 2. Pad Sektion (Linke Mitte)

**2.1 Spezielle Pad-Buttons**
| Button | Typ | Bemerkung |
| :--- | :--- | :--- |
| Pad | SysEx | Hardware-Modus |
| Chord Memory | SysEx | Hardware-Modus |
| Chord Transpose | SysEx | Hardware-Modus |

**2.2 Die 16 Performance Pads (4x4 Grid)**
*Senden auf dem Keys Port, MIDI-Kanal 10. Senden "Note On" (Anschlag) und "Poly Aftertouch" (Druckveränderung).*

| Spalte 1 | Note | Spalte 2 | Note | Spalte 3 | Note | Spalte 4 | Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Pad 1** | 36 | **Pad 2** | 37 | **Pad 3** | 38 | **Pad 4** | 39 |
| **Pad 5** | 40 | **Pad 6** | 41 | **Pad 7** | 42 | **Pad 8** | 43 |
| **Pad 9** | 44 | **Pad 10** | 45 | **Pad 11** | 46 | **Pad 12** | 47 |
| **Pad 13** | 48 | **Pad 14** | 49 | **Pad 15** | 50 | **Pad 16** | 51 |

---

## 3. Transport Sektion (Mitte Unten)
*Senden auf dem DAW Port (Note On, Kanal 1).*

| Beschriftung | Typ | Data1 (Note) |
| :--- | :--- | :--- |
| Rewind (<<) | Note On | 91 |
| Fast Fwd (>>) | Note On | 92 |
| Stop | Note On | 93 |
| Play | Note On | 94 |
| Record | Note On | 95 |
| Loop | Note On | 86 |

---

## 4. DAW Commands (Mitte Oben)
*Senden auf dem DAW Port (Note On, Kanal 1).*

| Beschriftung | Typ | Data1 (Note) |
| :--- | :--- | :--- |
| **Reihe 1: Track Controls** | | |
| Record | Note On | 0 |
| Solo | Note On | 8 |
| Mute | Note On | 16 |
| Read | Note On | 74 |
| Write | Note On | 75 |
| **Reihe 2: Global Controls**| | |
| Save | Note On | 80 |
| In | Note On | 87 |
| Out | Note On | 88 |
| Metro | Note On | 89 |
| Undo | Note On | 81 |

---

## 5. Navigation & Modes (Mitte Rechts)
| Beschriftung | Port | Typ | Data1 | Bemerkung |
| :--- | :--- | :--- | :--- | :--- |
| Jog Wheel (Drehen) | DAW | CC | 60 | Endlosregler (Rechts=1, Links=65) |
| Jog Wheel (Klick) | DAW | Note On | 84 | |
| Bank Left (<) | DAW | Note On | 98 | |
| Bank Right (>) | DAW | Note On | 99 | |
| Category / Preset | - | Intern | - | Hardware-Modus |
| Analog Lab / DAW / USER| - | SysEx | - | Hardware-Modus |

---

## 6. Mixer Sektion (Rechts)
*Senden auf dem DAW Port.*

**Die Modus-Knöpfe (Links neben den Fadern):**

| Normal | Note |
| :--- | :--- |
| Part 2 / Previous | 48 |
| Part 1 / Next | 49 |
| Wenn Live/Bank gedrückt | Note |
| :--- | :--- |
| Part 2 / Previous | 46 |
| Part 1 / Next | 47 |
*Live / Bank: `Intern` (Hardware-Modus-Umschaltung)*

**Die 9 Fader (Lautstärke):**
*Senden weiche Übergänge via Pitch Bend. Bei Berührung senden sie eine Note.*
| Fader | Pitch Bend Kanal | Touch-Sensor (Note On) |
| :--- | :--- | :--- |
| **Fader 1** | Kanal 01 (0xE0) | 104 |
| **Fader 2** | Kanal 02 (0xE1) | 105 |
| **Fader 3** | Kanal 03 (0xE2) | 106 |
| **Fader 4** | Kanal 04 (0xE3) | 107 |
| **Fader 5** | Kanal 05 (0xE4) | 108 |
| **Fader 6** | Kanal 06 (0xE5) | 109 |
| **Fader 7** | Kanal 07 (0xE6) | 110 |
| **Fader 8** | Kanal 08 (0xE7) | 111 |
| **Fader 9 (Master)**| Kanal 09 (0xE8) | 112 |

**Die 9 Encoder (Pan/Sends):**
*Endlosregler (CC). Senden Wert `1` beim Drehen nach rechts, `65` beim Drehen nach links.*
| Enc 1 | Enc 2 | Enc 3 | Enc 4 | Enc 5 | Enc 6 | Enc 7 | Enc 8 | Enc 9 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| CC 16 | CC 17 | CC 18 | CC 19 | CC 20 | CC 21 | CC 22 | CC 23 | CC 24 |

**Die 9 Track Buttons (Select/Mute/Solo):**
*Senden als Note On (gedrückt = 127, losgelassen = 0).*
| Btn 1 | Btn 2 | Btn 3 | Btn 4 | Btn 5 | Btn 6 | Btn 7 | Btn 8 | Btn 9 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Note 24 | Note 25 | Note 26 | Note 27 | Note 28 | Note 29 | Note 30 | Note 31 | Note 32 |

---

**7. Externe Inputs / Pedale (Rückseite)**
*Senden auf dem Keys Port (Kanal 1).*

| Anschluss | Port | Typ | Data1 (CC) | Bemerkung |
| :--- | :--- | :--- | :--- | :--- |
| Sustain Pedal | Keys | CC | 64 | Werte: 0 (Losgelassen), 127 (Gedrückt) |
| Expression Pedal| Keys | CC | 11 | Werte: 0 bis 127 (Stufenlos) |
| Aux 1 Pedal | Keys | CC | 12 | Werte: 0 bis 127 (Stufenlos) |
| Aux 2 Pedal | Keys | CC | 13 | Werte: 0 bis 127 (Stufenlos) |
| Aux 3 Pedal | Keys | CC | 14 | Werte: 0 bis 127 (Stufenlos) |

---

## 8. LED SysEx Protocol (Verified)

> **Source:** Community reverse-engineering of KeyLab MkII SysEx protocol.
> Arturia SysEx wrapper: `F0 00 20 6B 7F 42 [PAYLOAD] F7`

### 8.1 Monochrome LED Command
```
F0 00 20 6B 7F 42  02 00 10  [LEDID] [VALUE]  F7
```
- **VALUE range:** `0x00` – `0x7F` (128 steps, 0 = off, 127 = full brightness)
- **Monochrome color:** Always white

### 8.2 RGB LED Command
```
F0 00 20 6B 7F 42  02 00 16  [LEDID] [R] [G] [B] [0x7F]  F7
```
- **R / G / B range:** `0x00` – `0x1F` (32 steps per channel, NOT 0-127!)
- The trailing `0x7F` is a required terminator byte in the payload

### 8.3 Full LED ID Table

| LEDID (hex) | Button / LED        | Mono | RGB | Notes                        |
|-------------|---------------------|------|-----|------------------------------|
| 0x10        | Oct -               | ✓    |     |                              |
| 0x11        | Oct +               | ✓    |     |                              |
| 0x12        | Chord               | ✓    |     |                              |
| 0x13        | Trans               | ✓    |     |                              |
| 0x14        | MIDI                | ✓    |     |                              |
| 0x15        | Chord Transp        | ✓    |     |                              |
| 0x16        | Chord Mem           | ✓    |     |                              |
| 0x17        | Pad                 | ✓    |     |                              |
| 0x18        | Category            | ✓    |     | Default: blue                |
| 0x19        | Preset              | ✓    |     | Default: blue                |
| 0x1A        | ← (Nav Left)        | ✓    |     |                              |
| 0x1B        | → (Nav Right)       | ✓    |     |                              |
| 0x1C        | ANALOG LAB          | ✓    |     | Default: blue                |
| 0x1D        | DAW                 | ✓    |     |                              |
| 0x1E        | USER                | ✓    |     |                              |
| 0x1F        | Part 1              | ✓    |     |                              |
| 0x20        | Part 2              | ✓    |     |                              |
| 0x21        | Live                | ✓    |     |                              |
| 0x22–0x29   | Select 1–8          | ✓²   | ✓   | Track buttons (RGB)          |
| 0x2A        | Multi               | ✓²   | ✓   |                              |
| 0x60        | Solo                | ✓    |     | DAW COMMANDS / USER section  |
| 0x61        | Mute                | ✓    |     |                              |
| 0x62        | Record (Track Ctrl) | ✓    |     |                              |
| 0x63        | Read                | ✓    |     |                              |
| 0x64        | Write               | ✓    |     |                              |
| 0x65        | Save                | ✓    |     |                              |
| 0x66        | In                  | ✓    |     |                              |
| 0x67        | Out                 | ✓    |     |                              |
| 0x68        | Marker              | ✓    |     | Physically labeled "Metro"   |
| 0x69        | Undo                | ✓    |     |                              |
| 0x6A        | << (Rewind)         | ✓    |     | TRANSPORT section            |
| 0x6B        | >> (FastFwd)        | ✓    |     |                              |
| 0x6C        | STOP                | ✓    |     |                              |
| 0x6D        | Pause/Play          | ✓    |     |                              |
| 0x6E        | Record (Transport)  | ✓    |     | Default: red                 |
| 0x6F        | Loop                | ✓    |     |                              |
| 0x70–0x7F   | Pads 1–16           | ✓²   | ✓   | ² = on/off only (white)      |

> ¹ Monochrome = always white  
> ² Only on/off at full white brightness (no dimming via mono command)