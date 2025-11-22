# Bebop-Language Project V3.0 — Master Specification

**Version:** 3.0  
**Date:** November 22, 2025  
**Status:** FINAL

---

# 1. PURPOSE

This document defines the **Bebop-Language Project V3.0** architecture for Rapid Composer, Sibelius, and Sonuscore *The Score*. It integrates modern jazz language into a generative and notation-based workflow.

**Core Influences:**
- **Bebop:** Parker, Stitt, Barry Harris
- **Modern Guitar:** Metheny, Scofield, Rosenwinkel, Martino
- **Avant/Modal:** Coltrane, Shorter, Ornette
- **Orchestral:** Maria Schneider

---

# 2. THE FOUR ENGINE ARCHITECTURE (Rapid Composer Live Mode)

## Engine A — Bebop Engine
*Focus: The classic language.*
- **Target Gravity:** 3rd, 5th, 7th, 9th resolution points.
- **Scales:** Bebop Major, Bebop Dominant, 6th-Diminished.
- **Ornamentation:** Approach tones, Double Enclosures (Sheryl Bailey/Django).
- **Logic:** "Up-Scale, Down-Chord" (Barry Harris).

## Engine B — Avant Engine
*Focus: Post-bop and structural disruption.*
- **Cells:** 1-2-3-5 (Coltrane), 4th stacks (McCoy Tyner).
- **Harmony:** Hexatonics, Triad Superimposition.
- **Rhythm:** 3+3+2 cross-rhythms, over-the-barline phrasing.

## Engine C — Orchestral Jazz Engine
*Focus: Texture and Color.*
- **Palette:** Lydian, Lydian b7, Pastel Triad Pairs.
- **Orchestration:** Woodwind dovetailing, String arcs.
- **Rhythm:** Polyrhythmic overlays (3:2, 5:4).

## Engine D — Guitar Modernism Engine
*Focus: The modern guitar lineage.*
- **Metheny:** Wide melodic intervals + Pentatonics.
- **Scofield:** Chromatic displacement + Blues.
- **Rosenwinkel:** Vocal-like multi-octave lines.
- **Martino:** Minor conversion logic.

---

# 3. GLOBAL TRANSFORMATIONS

## F2 — Polychord Generator
Generates complex upper structures over bass roots:
1. **Minor + Diminished** (Martino)
2. **Major + Major** (Lydian)
3. **Major + Minor** (Dorian Hex)
4. **Major + Augmented** (Altered Hex)

## F3 — Polyrhythm Engine
Applies rhythmic templates:
- 3-over-2
- 5-over-4
- Nested 2-over-3-over-4

---

# 4. ENSEMBLE DEFINITION

**Small Jazz Orchestra (11 Instruments):**

| # | Instrument | MIDI | Role |
|---|------------|------|------|
| 1 | Flute | 73 | Color / Melody |
| 2 | Clarinet in Bb | 71 | Counterpoint |
| 3 | Flugelhorn | 56 | Lead |
| 4 | Violin I | 40 | High Pad / Line |
| 5 | Violin II | 40 | High Pad / Line |
| 6 | Viola | 41 | Mid Texture |
| 7 | Cello | 42 | Low Texture |
| 8 | Electric Guitar | 27 | Comping / Solo |
| 9 | Piano | 0 | Harmony / Comping |
| 10| Double Bass | 32 | Foundation |
| 11| Light Percussion | 118 | Texture |

---

# 5. FILE MANIFEST

The generated ZIP bundle contains:

1. `V3_RC_Presets_Full.json`: JSON definitions for Engines A-D.
2. `rc_liveset.json`: Rapid Composer Live Set structure.
3. `rc_transformations.json`: Polychord/Polyrhythm logic.
4. `the_score_playbackmap.json`: Integration map for Sonuscore.
5. `the_score_playbackmap.txt`: Human-readable map.
6. `small_jazz_orchestra_template.musicxml`: Sibelius-ready score template.
7. `Bebop_Language_Project_V3_Master.md`: This specification.
8. `README.md`: Setup instructions.



