# MELODY_GENERATOR System Specification
## Automated Album-Wide Melody Generation Engine

**Version:** 1.0  
**Date:** December 7, 2025  
**Status:** ACTIVE — Batch Processing Mode  

---

# SYSTEM OVERVIEW

The MELODY_GENERATOR is an automated system for generating MAMS-compliant melodies for all Trio Tunes. It processes each tune sequentially, creating four melody versions (A, B, C, D) that pass full MAMS validation.

---

# FUNCTION DEFINITION

```
MELODY_GENERATOR(tune_number, tune_name, key, bpm, time_sig, style, tagline, tip)

PARAMETERS:
    tune_number : int        — Album sequence number (1-15)
    tune_name   : string     — Title of the tune
    key         : string     — Key signature
    bpm         : int        — Tempo in beats per minute
    time_sig    : string     — Time signature (4/4, 3/4, 5/4, 7/8, 12/8, Free)
    style       : string     — Style category
    tagline     : string     — Uniqueness description
    tip         : string     — Playing tip for guitarists

RETURNS:
    {
        tune_number: int,
        tune_name: string,
        status: "PASS" | "FAIL",
        versions: {A: status, B: status, C: status, D: status},
        motifs_used: [string],
        transformations: [string],
        gce_scores: {A: int, B: int, C: int, D: int},
        validator_report: string
    }
```

---

# PROCESSING PIPELINE

## Step 1: Directory Creation

```
/Trio Tunes/TuneXX_<Tune_Name>/
├── LeadSheet/
│   ├── A/
│   │   ├── <Tune_Name>_A_Lyrical.musicxml
│   │   └── <Tune_Name>_A_Lyrical.pdf
│   ├── B/
│   │   ├── <Tune_Name>_B_Modern.musicxml
│   │   └── <Tune_Name>_B_Modern.pdf
│   ├── C/
│   │   ├── <Tune_Name>_C_Counterpoint.musicxml
│   │   └── <Tune_Name>_C_Counterpoint.pdf
│   └── D/
│       ├── <Tune_Name>_D_Hybrid.musicxml
│       └── <Tune_Name>_D_Hybrid.pdf
└── Source/
    └── LeadSheet.md
```

## Step 2: Style-Aware DNA Selection

| Style Category | Primary DNA | Secondary DNA | Motif Priority |
|:---------------|:------------|:--------------|:---------------|
| Blues | Blues (BL-1 to BL-6) | Bebop | M1, M2, M4 |
| Wayne Shorter | Modern Intervallic | Expressive | M3, M5, M6 |
| Scofield Funk | Blues + Modern | Rhythmic R-4 | M2, M3 |
| Bossa Nova | Lyrical | Brazilian rhythm | M1, M5, M6 |
| Scofield Ballad | Expressive | Space R-6 | M1, M6, M7 |
| Pat Metheny | Triad-Pair | Optimistic arc | M5, M3 |
| Experimental | Modern Angular | Space + Texture | M3, M7 |
| Post-Bop | Shorter + Bebop | Non-functional | M3, M4, M5 |
| Blues Shuffle | Blues Heavy | R-1 swing | M2, M4 |
| Odd Meter | Modern + Additive | R-4, R-7 | M3, M5 |
| ECM Ballad | Space + Sustain | R-6 | M1, M6, M7 |
| Bebop/Etude | Bebop Full | R-1, R-6 | M4 dominant |
| Fusion | Triad-Pair + Rhythm | R-2, R-4 | M3, M5 |
| Closing Ballad | Lyrical + Resolution | R-6 | M1, M6 |

## Step 3: Version Generation Logic

### Version A — Lyrical
```
DNA_PROFILE_A:
    motifs = [M1, M2, M6]
    intervals = [m6, P5, m3↔M3]
    rhythm = [R-1, R-6]
    expressive = [Hall, Green, Frisell]
    phrase_shape = [Arc, Plateau]
```

### Version B — Modern
```
DNA_PROFILE_B:
    motifs = [M3, M5]
    intervals = [P4, M7, #11]
    rhythm = [R-2, R-4]
    triad_pairs = [TP-1, TP-3, TP-5]
    expressive = [Rosenwinkel, Metheny, Law]
    phrase_shape = [Jagged, Wave]
```

### Version C — Counterpoint
```
DNA_PROFILE_C:
    motifs = [M1, M6, M7]
    intervals = [m6, P4, M7]
    rhythm = [R-3, R-6]
    expressive = [Wyble, Monder, Halvorson]
    phrase_shape = [Plateau, Contrary]
    counterpoint_rules = [70% contrary, 20% oblique, 10% parallel]
    
    NOTATION_RULE (MANDATORY):
    ┌─────────────────────────────────────────────────────────┐
    │  VERSION C MUST USE SINGLE STAFF WITH TWO VOICES        │
    │                                                         │
    │  Voice 1 (stems UP)   = Top voice / Melody              │
    │  Voice 2 (stems DOWN) = Bottom voice / Counterpoint     │
    │                                                         │
    │  NEVER use two staves — this is ONE guitar, not two!    │
    │  Use MusicXML <backup> element to layer voices.         │
    └─────────────────────────────────────────────────────────┘
```

### Version D — Hybrid
```
DNA_PROFILE_D:
    motifs = [M1, M2, M3, M4, M5, M6]  // All available
    intervals = [All signatures]
    rhythm = [Full palette]
    all_dna_layers = [Blues, Bebop, Modern, Expressive]
    phrase_shape = [Arc→Jagged→Plateau→Resolution]
    transformations = [Maximum variety]
```

## Step 4: MAMS Validation

Each generated version must pass:
1. Motif Check (≥2 motifs or 1 motif + transform)
2. Interval DNA Check (≥2 signatures)
3. Rhythmic DNA Check (≥1 cell appropriate to version)
4. Triad-Pair DNA Check (if modern/modal)
5. Blues/Bebop DNA Check (if applicable)
6. Expressive DNA Check (version-appropriate)
7. Transformation Check (≥1 transform)
8. Contour Archetype Check
9. Playability Check (D3-G5)
10. Album Coherence Check
11. GCE Score Check (≥45/50)

## Step 5: Regeneration Protocol

```
IF validation_fails:
    identify_failures()
    apply_corrections()
    regenerate_melody()
    revalidate()
    REPEAT until PASS or max_attempts (3)
```

---

# TUNE REGISTRY

## Parsed from Album_Table_of_Contents.md

| # | Title | Key | BPM | Time | Style | Status |
|:-:|:------|:----|:----|:-----|:------|:-------|
| 1 | Blue Cycle | Bb | 120 | 4/4 | Blues (Cycle) | ✓ COMPLETE |
| 2 | Orbit | F | 160 | 3/4 | Wayne Shorter (Avant) | PENDING |
| 3 | Rust & Chrome | E | 95 | 4/4 | Scofield Funk | PENDING |
| 4 | Sao Paulo Rain | D | 130 | 4/4 | Bossa Nova | PENDING |
| 5 | The Mirror | Ab | 60 | 4/4 | Scofield Ballad | PENDING |
| 6 | Bright Size Life 2 | D | 145 | 4/4 | Pat Metheny | PENDING |
| 7 | Monk's Dream | C | 110 | 4/4 | Experimental | PENDING |
| 8 | Nefertiti's Shadow | Eb | 180 | 4/4 | Wayne Shorter (Post-Bop) | PENDING |
| 9 | Greezy | G | 100 | 12/8 | Blues (Shuffle) | PENDING |
| 10 | Hexagon | B | 135 | 5/4 | Original (Odd Meter) | PENDING |
| 11 | Crystal Silence | A | 80 | 4/4 | ECM Ballad | PENDING |
| 12 | Angular Motion | Gb | 200 | 4/4 | Bebop/Etude | PENDING |
| 13 | The Void | Free | Free | Free | Experimental | PENDING |
| 14 | Solar Flare | C# | 150 | 7/8 | Fusion/Original | PENDING |
| 15 | Final Departure | Db | 70 | 4/4 | Closing Ballad | PENDING |

---

# BATCH EXECUTION PROTOCOL

```
FOR tune_number = 1 TO 15:
    
    1. LOAD tune metadata from registry
    
    2. SELECT DNA profile based on style:
       - Map style to DNA weights
       - Select primary motifs
       - Configure expressive profile
    
    3. CREATE directory structure
    
    4. GENERATE melodies:
       FOR version IN [A, B, C, D]:
           melody = generate_melody(tune, version_profile)
           validation = run_mams_validator(melody)
           
           WHILE validation.status == FAIL:
               melody = regenerate_with_fixes(melody, validation.failures)
               validation = run_mams_validator(melody)
           
           SAVE melody to appropriate directory
    
    5. CREATE LeadSheet.md with full documentation
    
    6. LOG results to completion tracker
    
    7. CLEAR ephemeral memory (preserve files)
    
    8. PROCEED to next tune

END FOR

CREATE Album_Melody_Completion_Log.md
```

---

# ALBUM COHERENCE TRACKING

## Motif Usage Across Album

The system maintains a running registry of motif usage to ensure album-wide coherence:

```
ALBUM_MOTIF_REGISTRY = {
    M1: [tunes using M1],
    M2: [tunes using M2],
    M3: [tunes using M3],
    M4: [tunes using M4],
    M5: [tunes using M5],
    M6: [tunes using M6],
    M7: [tunes using M7]
}
```

## Coherence Rules

1. **M1 (The Question):** Should appear in tunes 1, 4, 5, 11, 15 (lyrical tunes)
2. **M2 (Blues Cry):** Should appear in tunes 1, 3, 9 (blues-influenced)
3. **M3 (Angular Cell):** Should appear in tunes 2, 7, 8, 10, 12, 13, 14 (modern/angular)
4. **M4 (Bebop Seed):** Should appear in tunes 1, 8, 9, 12 (bebop passages)
5. **M5 (Floating Fourth):** Should appear in tunes 2, 6, 10, 14 (modal/quartal)
6. **M6 (The Resolution):** Should appear in all tunes at cadence points
7. **M7 (Textural Ghost):** Should appear in tunes 5, 7, 11, 13 (textural)

---

# OUTPUT FORMAT

## LeadSheet.md Template

Each generated LeadSheet.md follows this structure:

```markdown
# TUNE #XX: "[TUNE_NAME]" — COMPLETE LEAD SHEET
## MAMS-Validated Melodic Set

**Tune:** [Name]
**Key:** [Key]
**Tempo:** [BPM] BPM
**Time:** [Time Signature]
**Style:** [Style]
**Tagline:** "[Tagline]"
**Playing Tip:** [Tip]

---

# HARMONY REFERENCE
[Chord progression table]

---

# VERSION A: LYRICAL MELODY
[Full notation, tablature, validator report]

---

# VERSION B: MODERN TRIAD-PAIR MELODY
[Full notation, tablature, validator report]

---

# VERSION C: COUNTERPOINT
[Two-voice notation, tablature, validator report]

---

# VERSION D: FINAL HYBRID
[Full notation, tablature, validator report]

---

# MOTIF USAGE SUMMARY
# DNA COMPLIANCE SUMMARY
# PERFORMANCE NOTES
# FILE LOCATIONS

**STATUS: COMPLETE**
```

---

# MEMORY MANAGEMENT

To prevent memory overflow during batch processing:

1. Process one tune at a time
2. Write all outputs to disk immediately
3. Clear working memory after each tune
4. Maintain only the Album Motif Registry across tunes
5. Final summary generated from file scan, not memory

---

**SYSTEM STATUS: READY FOR BATCH EXECUTION**


