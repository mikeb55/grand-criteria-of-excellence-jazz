# Guitar Etude Generator (MAMS-Based)
## A System for Creating Fully Composed, Playable Etudes

**Version:** 1.0  
**Date:** December 7, 2025  
**Status:** ACTIVE  

---

# PURPOSE

To give Mike playable, musically coherent etudes that:
- Reinforce tune language
- Drill triad pairs, motifs, intervallic motion, blues, bebop
- Integrate counterpoint and modern phrasing
- Are fully MAMS-compliant
- Output as MusicXML + PDF

---

# INPUTS

| Parameter | Type | Options | Description |
|:----------|:-----|:--------|:------------|
| `tune_number` | int | 1–15 | Album sequence number |
| `tune_name` | string | — | Title of the tune |
| `focus` | string | See Focus Types | Technical/stylistic emphasis |
| `length` | string | "1 chorus" / "2 choruses" / "3 choruses" | Etude duration |
| `register` | string | "mid-neck", "upper", "mixed" | Position preference |

## Focus Types

| Focus | Description | Primary DNA |
|:------|:------------|:------------|
| `triad pairs` | Constant triad-pair motion | TP-1 to TP-5 |
| `bebop` | Classic bebop vocabulary | BB-1 to BB-7 |
| `blues` | Blues language emphasis | BL-1 to BL-6 |
| `intervallic modern` | Wide intervals, angular | I-1 to I-5 |
| `angular` | Halvorson/Law angularity | M3, M7 |
| `counterpoint` | Two-voice independence | Wyble/Monder |
| `mixed` | All elements integrated | Full MAMS |

---

# BEHAVIOUR

## Step 1: Load Tune Data

```
LOAD /Trio Tunes/TuneXX_<Name>/Source/LeadSheet.md
EXTRACT:
    - chord_progression
    - form (number of bars)
    - key_signature
    - tempo
    - time_signature
    - style_tag
```

---

## Step 2: Select MAMS Components by Focus

### Motif Selection Matrix

| Focus | Primary Motifs | Secondary | Transformations |
|:------|:---------------|:----------|:----------------|
| Triad Pairs | M5 | M3 | F, OD |
| Bebop | M4 | M2 | S, D |
| Blues | M2 | M1, M4 | T, RD |
| Intervallic Modern | M3, M5 | M7 | I, OD |
| Angular | M3, M7 | M5 | I, F, RD |
| Counterpoint | M1, M6, M7 | M5 | T, I, HR |
| Mixed | M1-M7 | All | Full palette |

### Interval DNA Selection

| Focus | Required Intervals |
|:------|:-------------------|
| Triad Pairs | P4, M7, chord tones |
| Bebop | m3, M3, P5, m7 |
| Blues | m3↔M3, P5, b7 |
| Intervallic Modern | P4, M7, m6, #11 |
| Angular | M7, tritone, m9 |
| Counterpoint | m6, P4, varies |
| Mixed | All signatures |

### Rhythmic DNA Selection

| Focus | Primary Rhythm | Secondary |
|:------|:---------------|:----------|
| Triad Pairs | R-2 (Even) | R-4 |
| Bebop | R-1 (Swing) | R-6 |
| Blues | R-1 (Swing) | R-6, BL-6 |
| Intervallic Modern | R-2, R-4 | R-3, R-5 |
| Angular | R-3, R-5 | R-4 |
| Counterpoint | R-3, R-6 | R-5 |
| Mixed | Full palette | Context-dependent |

---

## Step 3: Generate Etude Content

### Per-Chorus Generation

For each chorus:

```
GENERATE_CHORUS(chorus_number, focus, register):
    
    1. Select motifs from focus matrix
    
    2. For each phrase (4-8 bars):
        a. Choose primary motif
        b. Apply transformation (varied per phrase)
        c. Connect to chord progression
        d. Apply rhythmic DNA
        e. Check interval DNA compliance
    
    3. Apply phrase-shape archetype:
        - Chorus 1: Arc (↗↘)
        - Chorus 2: Wave (↗↘↗↘)
        - Chorus 3: Rising → Resolution
    
    4. Integrate expressive DNA:
        - Select from influence profiles
        - Apply phrasing characteristics
        - Add articulation markings
    
    5. Ensure register compliance:
        - mid-neck: A3 to D5
        - upper: D4 to G5
        - mixed: D3 to G5 (full range)
```

### Focus-Specific Rules

#### Triad Pairs Focus
```
TRIAD_PAIR_ETUDE:
    - Identify triad pair for each chord
    - Construct lines from triad arpeggios
    - Use connecting tones from MAMS interval DNA
    - Vary ascending/descending patterns
    - Include pivot tones (shared notes)
```

#### Bebop Focus
```
BEBOP_ETUDE:
    - Apply bebop scales (added passing tones)
    - Use enclosure patterns (BB-2)
    - Target chord tones on strong beats (BB-3)
    - Include 1-2-3-5 cells (BB-4)
    - Add diminished approaches (BB-5)
    - Incorporate double-time sections (BB-6)
    - Guide tone awareness (BB-7)
```

#### Blues Focus
```
BLUES_ETUDE:
    - Foundation: Minor pentatonic (BL-4)
    - Add blue notes (BL-1): b3, b5, b7
    - Include m3↔M3 crossover
    - Call and response phrasing (BL-2)
    - Double-stop 3rds/6ths (BL-3)
    - Chromatic approaches (BL-5)
    - Shuffle feel if 12/8 (BL-6)
```

#### Intervallic Modern Focus
```
INTERVALLIC_ETUDE:
    - Prioritize wide leaps (M7, m6)
    - P4 stacks (M5 motif)
    - Ant Law set: 2–6–♭3–#4
    - Avoid stepwise motion (max 3 consecutive steps)
    - Angular contours
    - Modern expressive profiles (Rosenwinkel, Law)
```

#### Angular Focus
```
ANGULAR_ETUDE:
    - M3 (Angular Cell) dominant
    - M7 (Textural Ghost) for space
    - Wide leaps followed by direction change
    - Rhythmic displacement (R-3)
    - Halvorson influence (bent notes, awkward intervals)
    - Maximum interval contrast
```

#### Counterpoint Focus
```
COUNTERPOINT_ETUDE:
    - Two voices (Wyble style)
    - M1 (Question) in top voice
    - M6 (Resolution) at phrase ends
    - M7 (Ghost) for texture
    - Contrary motion dominant
    - Voice independence rhythmically
    - Consider fingering for double-stops
```

#### Mixed Focus
```
MIXED_ETUDE:
    - Chorus 1: Emphasize tune's native style
    - Chorus 2: Contrast with different DNA
    - Chorus 3: Synthesis of all elements
    - All motifs available
    - Full transformation palette
    - Maximum MAMS compliance
```

---

## Step 4: Apply Expressive Language

### Influence Integration

| Focus | Primary Influences | Articulation Style |
|:------|:-------------------|:-------------------|
| Triad Pairs | Metheny, Rosenwinkel | Legato, flowing |
| Bebop | Parker, Stitt, Benson | Articulate, swing |
| Blues | Green, Scofield | Slides, bends |
| Intervallic Modern | Law, Rosenwinkel | Clean, wide |
| Angular | Halvorson, Monder | Bent, textural |
| Counterpoint | Wyble, Hall | Independent, clear |
| Mixed | Full chain | Context-dependent |

### Articulation Markings

```
ARTICULATION_VOCABULARY:
    - Legato slurs (hammer-on/pull-off)
    - Staccato dots (short, separated)
    - Accent marks (>)
    - Ghost notes (parentheses)
    - Slides (/ or \)
    - Bends (↗)
    - Vibrato (~~~)
    - Let ring (l.v.)
```

---

## Step 5: Ensure Idiomatic Fingerings

### Position Planning

```
POSITION_LOGIC:
    1. Analyze note range per phrase
    2. Identify optimal position(s)
    3. Plan shift points (between phrases)
    4. Consider open strings
    5. Avoid awkward stretches
    6. Mark position numbers (I, II, V, VII, etc.)
```

### String Set Considerations

| Register | Primary Strings | Character |
|:---------|:----------------|:----------|
| Mid-neck | 2, 3, 4 | Warm, balanced |
| Upper | 1, 2, 3 | Bright, clear |
| Mixed | All | Full color palette |

### Fingering Notation

```
LEFT_HAND:
    1 = index
    2 = middle
    3 = ring
    4 = pinky
    
    Position marked as Roman numeral at start of phrase
```

---

## Step 6: Validate

Run MAMS_Validator.md checks:

```
ETUDE_VALIDATION:
[ ] Motif Check: ≥2 motifs present
[ ] Interval DNA: ≥2 signatures per chorus
[ ] Rhythmic DNA: Appropriate to focus
[ ] Focus-specific DNA: Active and prominent
[ ] Transformation Check: ≥1 per chorus
[ ] Expressive DNA: Matches focus
[ ] Playability: D3–G5, idiomatic fingerings
[ ] GCE Score: ≥45/50
[ ] Album Coherence: Consistent with tune character
```

**If FAIL:** Regenerate with corrections until PASS.

---

# OUTPUTS

## Directory Structure

```
/Trio Tunes/TuneXX_<Name>/Practice/Etudes/
├── Etude_Focus_<FocusName>.musicxml
├── Etude_Focus_<FocusName>.pdf
└── Practice_Notes.md
```

## File Descriptions

| File | Content |
|:-----|:--------|
| `Etude_Focus_<Name>.*` | Full etude (1–3 choruses) |
| `Practice_Notes.md` | Technical and musical guidance |

## Practice_Notes.md Structure

```markdown
# Practice Notes: [Tune Name] — [Focus] Etude

## Overview
- Length: [X] choruses
- Focus: [Focus type]
- Register: [mid-neck/upper/mixed]
- Difficulty: [based on focus and length]

## MAMS DNA Active
- Motifs: [list]
- Interval DNA: [list]
- Rhythmic DNA: [list]
- Expressive: [influences]

## Technical Challenges
1. [Challenge 1 with bar reference]
2. [Challenge 2 with bar reference]
...

## Practice Suggestions
1. [Suggestion 1]
2. [Suggestion 2]
...

## Position Guide
- Bars 1-4: Position [X]
- Bars 5-8: Position [Y]
...

## Articulation Key
- [Symbol]: [Meaning]
...

## MAMS Validation
- Status: PASS
- GCE Score: [X]/50
```

---

# EXAMPLE INVOCATION

```
GUITAR_ETUDE_GENERATOR(
    tune_number = 9,
    tune_name = "Greezy",
    focus = "blues",
    length = "2 choruses",
    register = "mid-neck"
)

OUTPUT:
- Etude_Focus_Blues.musicxml
- Etude_Focus_Blues.pdf
- Practice_Notes.md

Content:
- Chorus 1: M2 (Blues Cry) dominant, call & response
- Chorus 2: M4 (Bebop) integration, double-time section
- Blues DNA: BL-1, BL-2, BL-4, BL-5 active
- Shuffle feel (12/8)
- Validation: PASS (49/50 GCE)
```

---

# INTEGRATION DEPENDENCIES

## Required Files

```
/MAMS/MAMS.md                           # Full MAMS specification
/MAMS/MAMS_Validator.md                 # Validation rules
/Trio Tunes/TuneXX_<Name>/Source/LeadSheet.md  # Chord progressions
/Bebop Language/Bebop_Language_Project_V3_Master.md  # Bebop DNA
```

## Engine References

- Melodic Style Engine (all 16 influences)
- Triad Pair Soloist Engine (for triad pair focus)
- Counterpoint Companion Generator (for counterpoint focus)
- GCE Melodic Development Rules

---

**ENGINE STATUS: READY**

*Guitar Etude Generator v1.0 — MAMS Integrated*


