# KeyLab mkII — Plugin Slot Configuration
# ============================================================
# USER-EDITABLE FILE — keine Logik, nur Daten.
#
# Weist jedem Track Button (1–8) ein Plugin und eine LED-Farbe
# zu — getrennt nach Focus-Kontext (Mixer vs. Channel Rack).
#
# FARB-FORMAT: (R, G, B) — Arturia RGB-LED-Bereich: 0–31 pro Kanal.
#
# Slot-Nummerierung: 0 = Track Button 1, ..., 7 = Track Button 8
# ============================================================

# ---------------------------------------------------------------------------
#  Mixer Focus — Track Buttons 1–8
#  Typische Nutzung: Insert-Effekte, EQs, Kompressoren, Reverbs
# ---------------------------------------------------------------------------
MIXER_SLOTS = {
    0: {
        "name":  "Fruity Parametric EQ 2",
        "color": (8, 0, 27),     # #2F00AC — violett/indigo
    },
    1: {
        "name":  "Pro-Q 3",
        "color": (31, 24, 0),    # gelb
    },
    2: {
        "name":  "TAL Reverb 4 Plugin",
        "color": (0, 12, 31),    # blau
    },
    3: {
        "name":  "Snap Heap",
        "color": (28, 28, 28),   # weiß
    },
    4: {
        "name":  "RC-20 Retro Color",
        "color": (28, 24, 14),   # beige / hellgelb
    },
    5: {
        "name":  "Little Radiator",
        "color": (0, 10, 0),     # dunkelgrün
    },
    6: {
        "name":  "TP Sonitex STX-1260",
        "color": (28, 28, 28),   # weiß
    },
    7: {
        "name":  "Ozone Imager",
        "color": (0, 12, 31),    # blau
    },
}

# ---------------------------------------------------------------------------
#  Channel Rack Focus — Track Buttons 1–8
#  Typische Nutzung: Synths, Sampler, Drum Machines
# ---------------------------------------------------------------------------
CHANNEL_SLOTS = {
    0: {
        "name":  "Omnisphere",
        "color": (0, 12, 31),    # blau
    },
    1: {
        "name":  "Vital",
        "color": (28, 0, 22),    # magenta
    },
    2: {
        "name":  "Odin2",
        "color": (12, 22, 31),   # hellblau / ice blue
    },
    3: {
        "name":  "Kontakt 7",
        "color": (15, 15, 16),   # grau
    },
    4: {
        "name":  "FLEX",
        "color": (8, 0, 27),     # #2F00AC — violett/indigo
    },
    5: {
        "name":  "Labs",
        "color": (28, 28, 28),   # weiß
    },
    6: {
        "name":  "Addictive Drums 2",
        "color": (28, 24, 14),   # beige / hellgelb
    },
    7: {
        "name":  "Fruity Slicer",
        "color": (11, 13, 15),   # #5B667C — slate blau-grau
    },
}
