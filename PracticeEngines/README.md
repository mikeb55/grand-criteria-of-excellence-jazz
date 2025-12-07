# Practice Engines Overview
## Modular Practice Material Generation for Trio Tunes

**Version:** 1.0  
**Date:** December 7, 2025  
**Status:** ACTIVE  

---

# INTRODUCTION

This directory contains three modular practice engines designed to generate high-quality, MAMS-compliant practice material for every tune in the Trio Tunes album.

All engines are fully integrated with:
- `/MAMS/MAMS.md` — Master Album Motif System
- `/MAMS/MAMS_Validator.md` — Quality control validation
- Melodic Style Engine — All 16 influence profiles
- Tune harmonic data from each `LeadSheet.md`
- Album ordering from `Album_Table_of_Contents.md`

---

# THE THREE ENGINES

## 1. Triad Pair Soloist Engine

**File:** `Triad_Pair_Soloist_Engine.md`

**Purpose:** Generate triad-pair–based improvisation material.

**Outputs:**
- Triad-pair maps for every chord
- Example licks demonstrating each pair
- 1–2 chorus triad-pair solos
- Hybrid solos mixing triad pairs + MAMS motifs

**Best For:**
- Learning triad-pair vocabulary
- Modern jazz improvisation
- Metheny/Rosenwinkel-style playing

---

## 2. Counterpoint Companion Generator

**File:** `Counterpoint_Companion_Generator.md`

**Purpose:** Create second-voice counterpoint lines that weave around existing melodies.

**Outputs:**
- 1–2 chorus counterpoint lines
- Wyble-style double-stop implied voices
- Second guitar lines

**Best For:**
- Developing two-voice independence
- Wyble/Monder/Halvorson textures
- Trio texture enrichment
- Hand independence on guitar

---

## 3. Guitar Etude Generator

**File:** `Guitar_Etude_Generator.md`

**Purpose:** Create fully composed, playable etudes based on MAMS DNA.

**Outputs:**
- 1–3 chorus etudes per tune
- Focus-specific practice (triad pairs, bebop, blues, angular, etc.)
- Idiomatic guitar fingerings
- Practice notes and guidance

**Best For:**
- Technical development
- Style mastery
- Deep tune internalization
- Performance preparation

---

# COMMON FEATURES

All three engines share these characteristics:

## MAMS Integration

```
Every output includes:
- Motif usage (M1–M7)
- Interval DNA (P4, M7, m6, #11, etc.)
- Rhythmic DNA (R-1 to R-7)
- Expressive DNA (influence profiles)
- Transformation tracking
```

## Validation

```
Every output is validated against MAMS_Validator.md:
- Motif presence check
- DNA compliance check
- Playability check (D3–G5)
- GCE score calculation
- Regeneration until PASS
```

## Output Formats

```
All engines produce:
- MusicXML files (for notation software)
- PDF files (engraved scores)
- Markdown documentation
```

## Guitar-Specific

```
All outputs consider:
- Guitar range (D3–G5)
- Idiomatic fingerings
- Position planning
- String set optimization
- Articulation markings
```

---

# USAGE WORKFLOW

## Step 1: Choose Your Engine

| Goal | Engine |
|:-----|:-------|
| Learn triad-pair vocabulary | Triad Pair Soloist |
| Develop two-voice independence | Counterpoint Companion |
| Practice specific techniques | Guitar Etude Generator |

## Step 2: Select Parameters

Each engine accepts tune-specific parameters:
- Tune number (1–15)
- Tune name
- Focus/texture/difficulty settings
- Length/density preferences

## Step 3: Generate

Run the engine with your parameters. The system will:
1. Load tune data from LeadSheet.md
2. Apply MAMS DNA based on settings
3. Generate musical content
4. Validate against MAMS_Validator.md
5. Regenerate if needed until PASS
6. Output MusicXML + PDF + documentation

## Step 4: Practice

Use the generated materials to:
- Learn new vocabulary
- Internalize tune language
- Develop technical facility
- Prepare for performance

---

# DIRECTORY STRUCTURE

## Engine Files

```
/PracticeEngines/
├── README.md                           # This file
├── Triad_Pair_Soloist_Engine.md        # Engine 1
├── Counterpoint_Companion_Generator.md # Engine 2
└── Guitar_Etude_Generator.md           # Engine 3
```

## Generated Output Location

```
/Trio Tunes/TuneXX_<Name>/Practice/
├── TriadPairs/
│   ├── TriadPair_Map.md
│   ├── TriadPair_Examples.xml + .pdf
│   ├── TriadPair_Solo_A.xml + .pdf
│   └── TriadPair_Solo_B.xml + .pdf
├── Counterpoint/
│   ├── Counterpoint_Line_1.xml + .pdf
│   ├── Counterpoint_Line_2.xml + .pdf
│   └── Notes.md
└── Etudes/
    ├── Etude_Focus_<Name>.xml + .pdf
    └── Practice_Notes.md
```

---

# INTEGRATION MAP

```
┌─────────────────────────────────────────────────────────────┐
│                    MAMS.md (Master DNA)                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│  Triad Pair     │ │ Counterpoint│ │  Guitar Etude   │
│  Soloist Engine │ │  Companion  │ │   Generator     │
└────────┬────────┘ └──────┬──────┘ └────────┬────────┘
         │                 │                  │
         └────────────────┬┴──────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   MAMS_Validator.md   │
              │  (Quality Control)    │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  MusicXML + PDF Output │
              │  (Practice Materials)  │
              └───────────────────────┘
```

---

# QUICK START EXAMPLES

## Generate Triad-Pair Material for Blue Cycle

```
TRIAD_PAIR_SOLOIST_ENGINE(
    tune_number = 1,
    tune_name = "Blue Cycle",
    section = "full chorus",
    difficulty = "intermediate",
    density = "medium"
)
```

## Generate Counterpoint for The Mirror

```
COUNTERPOINT_COMPANION_GENERATOR(
    tune_number = 5,
    tune_name = "The Mirror",
    source_melody = "A",
    texture = "equal voice",
    angularity = "medium"
)
```

## Generate Blues Etude for Greezy

```
GUITAR_ETUDE_GENERATOR(
    tune_number = 9,
    tune_name = "Greezy",
    focus = "blues",
    length = "2 choruses",
    register = "mid-neck"
)
```

---

# BENEFITS

## For Improvisation
- Builds vocabulary systematically
- Connects theory to fretboard
- Develops modern jazz language

## For Composition
- Reinforces album DNA
- Develops motif-based thinking
- Strengthens voice-leading awareness

## For Technique
- Guitar-specific fingerings
- Position fluency
- Articulation development

## For Performance
- Deep tune internalization
- Stylistic authenticity
- Confidence through preparation

---

# SUPPORT FILES

These files are required for full engine operation:

```
/MAMS/MAMS.md                              # Core DNA definitions
/MAMS/MAMS_Validator.md                    # Validation rules
/Trio Tunes/MD/Album_Table_of_Contents.md  # Tune metadata
/Trio Tunes/TuneXX_<Name>/Source/LeadSheet.md  # Chord progressions
/Bebop Language/Bebop_Language_Project_V3_Master.md  # Bebop DNA
/Composition Rules/GCE_Melodic_Development_Rules.md  # GCE rules
```

---

**Use these tools to develop improvisation vocabulary, compositional fluency, and deep mastery of the Trio Tunes album language.**

---

*Practice Engines v1.0 — Fully MAMS Integrated*


