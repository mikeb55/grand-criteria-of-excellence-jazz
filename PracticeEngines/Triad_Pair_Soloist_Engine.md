# Triad Pair Soloist Engine
## A Modular System for Generating Triad-Pair–Based Improvisation Material

**Version:** 1.0  
**Date:** December 7, 2025  
**Status:** ACTIVE  

---

# PURPOSE

To generate:
- A triad-pair map for every chord
- Short licks demonstrating each pair
- 1–2 chorus triad-pair solos
- Hybrid solos mixing triad pairs + MAMS motifs
- Fully engraved MusicXML + PDFs

---

# INPUTS

| Parameter | Type | Options | Description |
|:----------|:-----|:--------|:------------|
| `tune_number` | int | 1–15 | Album sequence number |
| `tune_name` | string | — | Title of the tune |
| `section` | string | "A" / "B" / "full chorus" | Section to generate for |
| `difficulty` | string | "basic", "intermediate", "advanced" | Complexity level |
| `density` | string | "sparse", "medium", "dense" | Note density |

---

# BEHAVIOUR

## Step 1: Load Tune Data
```
LOAD /Trio Tunes/TuneXX_<Name>/Source/LeadSheet.md
EXTRACT chord_progression
EXTRACT key_signature
EXTRACT tempo
EXTRACT time_signature
```

## Step 2: Generate Triad-Pair Map

For each chord in the progression:

### 2.1 Choose Identity Triad (Tonality Vault Logic)
| Chord Quality | Identity Triad | Rationale |
|:--------------|:---------------|:----------|
| Maj7 | Root Major | Defines major quality |
| Dom7 | Root Major | Dominant foundation |
| Min7 | bIII Major | Relative major sound |
| Min7b5 | bIII Major | Locrian brightness |
| Dim7 | Any of 4 roots | Symmetric options |
| Maj7#11 | Root Major | Lydian base |
| Alt7 | bII Major | Tritone substitution |

### 2.2 Choose Colour Triad
| Chord Quality | Colour Triad | Interval Relationship |
|:--------------|:-------------|:----------------------|
| Maj7 | II Major | Lydian extensions |
| Dom7 | bVII Major | Mixolydian tensions |
| Min7 | IV Major | Dorian color |
| Min7b5 | bVI Major | Locrian #2 color |
| Dim7 | Half-step related | Symmetric motion |
| Maj7#11 | II Major | Full Lydian |
| Alt7 | Root Aug | Altered tensions |

### 2.3 Generate Triad-Pair Cells
For each chord, generate 2–3 cells:

```
CELL_TYPES:
    - Ascending pair: Identity → Colour
    - Descending pair: Colour → Identity  
    - Alternating: I-C-I-C (8th notes)
    - Pivot: Shared note between triads
```

### 2.4 Map Cells to MAMS Interval DNA

Ensure cells contain:
- **P4:** Quartal implications
- **M7:** Wide leaps for drama
- **m6:** Melancholic descents
- **#11:** Lydian brightness
- **2–6–♭3–#4:** Ant Law angular set
- **Blues b3→3:** Blue note crossover

---

## Step 3: Construct Outputs

### 3.1 Triad Pair Map (Markdown Table)
```markdown
| Bar | Chord | Identity Triad | Colour Triad | Cell 1 | Cell 2 | MAMS DNA |
|:---:|:------|:---------------|:-------------|:-------|:-------|:---------|
| 1 | Cmaj7 | C Major | D Major | C-E-G-D | D-F#-A-C | P4, M7 |
| 2 | Am7 | C Major | F Major | C-E-G-F | F-A-C-E | m6 |
...
```

### 3.2 Example Phrases (8 bars)
Generate 8-bar example phrases demonstrating:
- Basic triad-pair motion
- Rhythmic variation
- Connection between pairs
- Resolution points

### 3.3 Triad-Pair Solo A (1 chorus)
Pure triad-pair improvisation:
- Use only triad-pair cells
- Apply rhythmic DNA (R-1 to R-7)
- Vary density per difficulty setting

### 3.4 Triad-Pair Solo B (Hybrid)
Mix triad pairs with MAMS motifs:
- Integrate M1–M7 motifs
- Use triad pairs as connective tissue
- Apply transformations (T, I, S, F)

---

## Step 4: Apply MAMS DNA

### Rhythmic DNA Application
| Difficulty | Primary Rhythm | Secondary |
|:-----------|:---------------|:----------|
| Basic | R-1 (Swing 8ths) | R-6 (Space) |
| Intermediate | R-2 (Even 16ths) | R-4 (3+3+2) |
| Advanced | R-4, R-5, R-7 | R-3 (Displacement) |

### Expressive DNA Application
| Density | Expressive Profile |
|:--------|:-------------------|
| Sparse | Hall, Frisell (space) |
| Medium | Metheny, Rosenwinkel (flow) |
| Dense | Scofield, Law (angular) |

### Guitar Range Enforcement
```
VALID_RANGE: D3 (MIDI 50) to G5 (MIDI 79)
All generated content must fall within this range.
Adjust octaves as needed for playability.
```

---

## Step 5: Validate

Run MAMS_Validator.md checks:

```
VALIDATION_CHECKLIST:
[ ] Motif presence (if hybrid)
[ ] Interval DNA (≥2 signatures)
[ ] Rhythmic DNA (appropriate to difficulty)
[ ] Triad-Pair DNA (TP-1 to TP-5 active)
[ ] Expressive DNA (matches density)
[ ] Playability (D3–G5 range)
[ ] Album Coherence (consistent with tune character)
```

**If FAIL:** Regenerate with corrections until PASS.

---

# OUTPUTS

## Directory Structure
```
/Trio Tunes/TuneXX_<Name>/Practice/TriadPairs/
├── TriadPair_Map.md
├── TriadPair_Examples.musicxml
├── TriadPair_Examples.pdf
├── TriadPair_Solo_A.musicxml
├── TriadPair_Solo_A.pdf
├── TriadPair_Solo_B.musicxml
└── TriadPair_Solo_B.pdf
```

## File Descriptions

| File | Content |
|:-----|:--------|
| `TriadPair_Map.md` | Markdown table with all triad-pair relationships |
| `TriadPair_Examples.*` | 8-bar demonstration phrases |
| `TriadPair_Solo_A.*` | 1 chorus pure triad-pair solo |
| `TriadPair_Solo_B.*` | 1 chorus hybrid (triads + MAMS) |

---

# EXAMPLE INVOCATION

```
TRIAD_PAIR_SOLOIST_ENGINE(
    tune_number = 1,
    tune_name = "Blue Cycle",
    section = "full chorus",
    difficulty = "intermediate",
    density = "medium"
)

OUTPUT:
- TriadPair_Map.md: 12 bars mapped
- TriadPair_Examples: 8 bars, MIDI + PDF
- TriadPair_Solo_A: 12-bar triad-pair solo
- TriadPair_Solo_B: 12-bar hybrid with M2, M4, M5
- Validation: PASS (47/50 GCE)
```

---

# INTEGRATION DEPENDENCIES

## Required Files
```
/MAMS/MAMS.md                           # Motif + DNA definitions
/MAMS/MAMS_Validator.md                 # Validation rules
/Trio Tunes/MD/Album_Table_of_Contents.md   # Tune metadata
/Trio Tunes/TuneXX_<Name>/Source/LeadSheet.md  # Chord progressions
```

## Engine References
- Melodic Style Engine (all influences)
- Bebop Language Project V3
- GCE Melodic Development Rules

---

**ENGINE STATUS: READY**

*Triad Pair Soloist Engine v1.0 — MAMS Integrated*


