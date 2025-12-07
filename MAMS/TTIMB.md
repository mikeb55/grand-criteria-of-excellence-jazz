# TRIO TUNES IMPROVISATION METHOD BUILDER (TTIMB)
## Complete System for Generating an Album-Wide Improvisation Method Book

**Version:** 1.0  
**Date:** December 7, 2025  
**Status:** ACTIVE  

---

# SYSTEM OVERVIEW

TTIMB is a complete system to generate an entire improvisation method book for all 15 Trio Tunes using:
- MAMS (Master Album Motif System)
- Melodic Style Engine
- MAMS Validator
- Practice Engines (Triad Pair, Counterpoint, Etude)

---

# REQUIRED RESOURCES (AUTO-LOAD)

```
/MAMS/MAMS.md                                    # Master motif system
/MAMS/MAMS_Validator.md                          # Validation rules
/MAMS/MELODY_GENERATOR.md                        # Batch melody generator
/PracticeEngines/Triad_Pair_Soloist_Engine.md   # Triad pair materials
/PracticeEngines/Counterpoint_Companion_Generator.md  # Counterpoint lines
/PracticeEngines/Guitar_Etude_Generator.md       # MAMS-based etudes
/Trio Tunes/MD/Album_Table_of_Contents.md        # Tune registry
```

These MUST remain loaded for all subsequent steps.

---

# DIRECTORY STRUCTURE

```
/Trio Tunes/MethodBook/
├── Book.md                 # Master method book document
├── TTIMB_A4.pdf           # Final formatted PDF
├── TTIMB.zip              # Complete archive
├── Chapters/
│   ├── Tune01_Blue_Cycle.md
│   ├── Tune02_Orbit.md
│   └── ... (all 15 tunes)
├── Assets/
│   └── (images, diagrams)
├── XML/
│   └── (consolidated MusicXML)
└── PDF/
    └── (consolidated PDFs)
```

---

# FUNCTION DEFINITION: TTIMB_BUILD_TUNE()

```
TTIMB_BUILD_TUNE(tune_number, tune_name, key, bpm, time_sig, style, tagline, tip)

PARAMETERS:
    tune_number : int        — Album sequence number (1-15)
    tune_name   : string     — Title of the tune
    key         : string     — Key signature
    bpm         : int        — Tempo in beats per minute
    time_sig    : string     — Time signature
    style       : string     — Style category
    tagline     : string     — Uniqueness description
    tip         : string     — Playing tip for guitarists

RETURNS:
    { tune_number, tune_name, status: "PASS" }
```

---

# TTIMB_BUILD_TUNE() BEHAVIOUR

## (A) Generate Lead Sheet Melody Set

Call MELODY_GENERATOR to create:
- Version A (Lyrical)
- Version B (Modern)
- Version C (Counterpoint) — SINGLE STAFF, two voices
- Version D (Hybrid)

Each must be:
- MusicXML format
- Engraved PDF
- Validated with MAMS_Validator

**Save in:** `/Trio Tunes/TuneXX_<Name>/LeadSheet/`

---

## (B) Generate Triad Pair Soloist Materials

Call Triad_Pair_Soloist_Engine to produce:
- TriadPair_Map.md
- TriadPair_Examples.xml + .pdf
- TriadPair_Solo_A.xml + .pdf
- TriadPair_Solo_B.xml + .pdf

All validated via MAMS_Validator.

**Save in:** `/Trio Tunes/TuneXX_<Name>/Practice/TriadPairs/`

---

## (C) Generate Counterpoint Companion Materials

Call Counterpoint_Companion_Generator to produce:
- Counterpoint_Line_1.xml + .pdf
- Counterpoint_Line_2.xml + .pdf (optional)
- Notes.md

Validated via MAMS_Validator.

**Save in:** `/Trio Tunes/TuneXX_<Name>/Practice/Counterpoint/`

---

## (D) Generate Etude Materials

Call Guitar_Etude_Generator to produce:
- 1 chorus lyrical etude
- 1 chorus modern intervallic etude
- 1 chorus blues/bebop etude
- Optional: 1–2 multi-chorus advanced etudes

All with MusicXML + PDFs.

**Save in:** `/Trio Tunes/TuneXX_<Name>/Practice/Etudes/`

---

## (E) Generate Phrase Pack

Produce:
- 16–32 MAMS-driven phrases
- Each labelled with motif ID (M1–M7), interval DNA, rhythmic DNA

Output as:
- PhrasePack.md
- PhrasePack.xml
- PhrasePack.pdf

**Save in:** `/Trio Tunes/TuneXX_<Name>/Practice/Phrases/`

---

## (F) Motif Density Analysis

Analyze:
- A, B, C, D lead sheet melodies
- Triad pair solos
- Counterpoint lines
- Etudes

Produce:
- MotifDensityReport.md
- charts/visual summaries (ASCII acceptable)

**Save in:** `/Trio Tunes/TuneXX_<Name>/Analysis/`

---

## (G) Practice Plan

Generate:
- Daily practice plan
- Weekly practice plan
- "How to learn this tune" page
- "Improvisation study checklist"

**Save as:** `/Trio Tunes/TuneXX_<Name>/Practice/PracticePlan.md`

---

## (H) Produce Tune Chapter for Method Book

Create: `/Trio Tunes/MethodBook/Chapters/TuneXX_<Name>.md`

Include:
- Overview
- Lead sheet previews (ASCII or markdown-rendered)
- Summary of motifs used
- Triad-pair map summary
- Etude summaries
- Counterpoint guide
- Practice plan
- Phrase pack highlights
- Motif density summary

This file becomes one chapter of the final method book.

---

# ITERATION PROTOCOL

```
FOR tune_number = 1 TO 15:
    
    1. LOAD tune metadata from Album_Table_of_Contents.md
    
    2. CALL TTIMB_BUILD_TUNE(tune_number, ...)
    
    3. SAVE all outputs to tune directory
    
    4. CREATE chapter file in /MethodBook/Chapters/
    
    5. CLEAR ephemeral memory (NOT files)
    
    6. PROCEED to next tune

END FOR
```

This ensures memory-safe processing.

---

# FINAL BOOK ASSEMBLY

After all 15 tunes are processed:

## 1. Create Book.md

Master file containing:
- Title page
- Table of Contents
- Introduction to MAMS
- Overview of Melodic Style Engine
- Overview of Trio Tunes concept
- One chapter per tune (import TuneXX files)
- Closing notes & study strategies

## 2. Create A4 PDF

Save as: `/Trio Tunes/MethodBook/TTIMB_A4.pdf`

## 3. Create ZIP Archive

Zip the entire MethodBook/ directory:

Save as: `/Trio Tunes/MethodBook/TTIMB.zip`

---

# TUNE REGISTRY

| # | Title | Key | BPM | Time | Style |
|:-:|:------|:----|:----|:-----|:------|
| 1 | Blue Cycle | Bb | 120 | 4/4 | Blues (Cycle) |
| 2 | Orbit | F | 160 | 3/4 | Wayne Shorter (Avant) |
| 3 | Rust & Chrome | E | 95 | 4/4 | Scofield Funk |
| 4 | Sao Paulo Rain | D | 130 | 4/4 | Bossa Nova |
| 5 | The Mirror | Ab | 60 | 4/4 | Scofield Ballad |
| 6 | Bright Size Life 2 | D | 145 | 4/4 | Pat Metheny |
| 7 | Monk's Dream | C | 110 | 4/4 | Experimental |
| 8 | Nefertiti's Shadow | Eb | 180 | 4/4 | Wayne Shorter (Post-Bop) |
| 9 | Greezy | G | 100 | 12/8 | Blues (Shuffle) |
| 10 | Hexagon | B | 135 | 5/4 | Original (Odd Meter) |
| 11 | Crystal Silence | A | 80 | 4/4 | ECM Ballad |
| 12 | Angular Motion | Gb | 200 | 4/4 | Bebop/Etude |
| 13 | The Void | Free | Free | Free | Experimental |
| 14 | Solar Flare | C# | 150 | 7/8 | Fusion/Original |
| 15 | Final Departure | Db | 70 | 4/4 | Closing Ballad |

---

# COMPLETION CONFIRMATION

After building the complete method book and all tune chapters, respond:

> **"TTIMB complete — full Trio Tunes Improvisation Method Book generated successfully."**

---

**SYSTEM STATUS: INSTALLED AND READY**

*TTIMB v1.0 — Integrated with MAMS + Practice Engines*

