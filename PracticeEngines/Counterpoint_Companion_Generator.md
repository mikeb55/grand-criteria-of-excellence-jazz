# Counterpoint Companion Generator
## A Generator for Creating Second-Voice Lines Around Trio Tune Melodies

**Version:** 1.0  
**Date:** December 7, 2025  
**Status:** ACTIVE  

---

# PURPOSE

To create:
- 1–2 chorus counterpoint lines
- Either "second guitar" or "Wyble double-stop implied voices"
- Lines that weave around any Trio Tune melody
- MusicXML + PDF outputs

---

# INPUTS

| Parameter | Type | Options | Description |
|:----------|:-----|:--------|:------------|
| `tune_number` | int | 1–15 | Album sequence number |
| `tune_name` | string | — | Title of the tune |
| `source_melody` | string | "A", "B", "C", "D" | Which melody version to accompany |
| `texture` | string | "equal voice", "supportive", "bass-counterline" | Role of the new line |
| `angularity` | string | "low", "medium", "high" | How angular/chromatic |

---

# BEHAVIOUR

## Step 1: Load Source Melody

```
LOAD /Trio Tunes/TuneXX_<Name>/Source/LeadSheet.md
EXTRACT melody_version(source_melody)
EXTRACT chord_progression
EXTRACT key_signature
EXTRACT tempo
EXTRACT time_signature

PARSE melody into:
    - note_sequence[]
    - rhythm_sequence[]
    - phrase_boundaries[]
```

---

## Step 2: Apply MAMS Counterpoint DNA

### 2.1 Motion Type Selection

| Texture | Primary Motion | Secondary | Avoid |
|:--------|:---------------|:----------|:------|
| Equal Voice | 60% Contrary | 30% Oblique | Parallel 5ths/8ves |
| Supportive | 50% Oblique | 40% Parallel 3rds/6ths | Wide contrary leaps |
| Bass-Counterline | 70% Contrary | 20% Oblique | Parallel motion |

### 2.2 Interval Relationships

**Allowed Intervals (Vertical):**
| Interval | Usage | Character |
|:---------|:------|:----------|
| Unison/8ve | Phrase endings | Resolution |
| m3/M3 | Common | Warm |
| P4 | Common | Open |
| P5 | Common | Stable |
| m6/M6 | Frequent | Rich |
| m7/M7 | Occasional | Tension |
| m2/M2 | Passing | Dissonance |
| Tritone | Climax points | Maximum tension |

### 2.3 Divergence → Convergence Pattern

```
CONTOUR_RULE:
    - Start phrases with voices close (3rd/6th)
    - Diverge through contrary motion (expand to 8ve+)
    - Converge at phrase end (return to 3rd/6th or unison)
    
MONDER_ARC:
    - Gradual expansion over 4–8 bars
    - Climax at widest point
    - Resolution through convergence
```

---

## Step 3: Apply Style-Specific Rules

### 3.1 Wyble Mode (Double-Stop Implied Voices)

When texture = "equal voice" or explicitly requested:

```
WYBLE_RULES:
    - Two voices on single guitar staff
    - Top voice: Melody (from source)
    - Bottom voice: Counter-melody (generated)
    - Voice range: Maximum 10th apart (playable)
    - Fingering: Consider string sets
    - Independence: Rhythmic offset between voices
```

**Wyble Voice-Leading:**
- Smooth bass motion (stepwise preferred)
- Bass provides harmonic foundation
- Top voice melodically independent
- Cross at climax points for color

### 3.2 Monder Mode (Cinematic Arcs)

When angularity = "medium" or "high":

```
MONDER_RULES:
    - Wide spacing allowed (up to 2 octaves)
    - Cluster voicings at tension points
    - Gradual builds (long crescendo shapes)
    - Harmonic density increases toward climax
    - Orchestral thinking (voices as instruments)
```

### 3.3 Halvorson Mode (Angular Disruption)

When angularity = "high":

```
HALVORSON_RULES:
    - Microtonal "melt" in counterpoint voice
    - Unexpected pitch bends (notated as grace notes)
    - Deliberately awkward intervals (m9, aug4)
    - Off-center rhythmic placement
    - Sudden dynamic shifts
```

---

## Step 4: Apply Rhythmic DNA

### Independence Rules

| Texture | Counterpoint Rhythm |
|:--------|:--------------------|
| Equal Voice | Independent (different rhythm than melody) |
| Supportive | Complementary (fills melody gaps) |
| Bass-Counterline | Walking or pedal (steady quarter/half notes) |

### Rhythmic Techniques

```
INDEPENDENCE_DEVICES:
    - Off-grid syncopation (8th note displacement)
    - Polyrhythm (3:4 or 5:4 against melody)
    - Hemiola (3 against 2)
    - Staggered entrances (canon-like)
    - Rhythmic augmentation/diminution
```

### Angularity-Based Rhythm

| Angularity | Rhythmic Character |
|:-----------|:-------------------|
| Low | Smooth, flowing, minimal syncopation |
| Medium | Moderate syncopation, some polyrhythm |
| High | Heavy syncopation, polyrhythm, fragmentation |

---

## Step 5: Guitar Idiomatic Constraints

### CRITICAL: Single-Staff Notation Rule

> **ALL Version C (Counterpoint) lead sheets MUST use ONE STAFF with two voices.**
> Never output counterpoint as two separate staves — that implies two instruments.

```
SINGLE_STAFF_RULE (MANDATORY):
    ┌─────────────────────────────────────────────────┐
    │  ONE STAFF for guitar two-voice counterpoint    │
    │                                                 │
    │  Voice 1 (stems UP)   = Top voice / Melody      │
    │  Voice 2 (stems DOWN) = Bottom voice / Bass     │
    │                                                 │
    │  Use <backup> in MusicXML to layer voices       │
    │  on the same staff, NOT <staves>2</staves>      │
    └─────────────────────────────────────────────────┘
```

### MusicXML Voice Implementation

```xml
<!-- CORRECT: Single staff, two voices -->
<note>
    <pitch>...</pitch>
    <voice>1</voice>
    <stem>up</stem>
</note>
<backup><duration>16</duration></backup>
<note>
    <pitch>...</pitch>
    <voice>2</voice>
    <stem>down</stem>
</note>

<!-- WRONG: Two staves (implies two instruments) -->
<attributes>
    <staves>2</staves>  <!-- DO NOT USE -->
</attributes>
```

### Playability Rules

```
GUITAR_CONSTRAINTS:
    Range: D3 (MIDI 50) to G5 (MIDI 79)
    
    FOR ALL COUNTERPOINT (Version C):
        - ALWAYS single staff with Voice 1 (up) and Voice 2 (down)
        - Max interval between voices: 10th (playable stretch)
        - Consider string assignment:
            * Top voice: Strings 1-3
            * Bottom voice: Strings 4-6
        - Avoid impossible left-hand stretches (>5 frets)
        - Plan position shifts logically
        - Both voices must be playable simultaneously on ONE guitar
    
    IF generating separate "Second Guitar" part (rare):
        - Use separate file, not separate staff
        - Full range available
        - Independent fingering
```

### Fingering Optimization

```
FINGERING_LOGIC:
    1. Identify position changes
    2. Minimize shifts during fast passages
    3. Use open strings when appropriate
    4. Plan for sustain (let ring where indicated)
    5. Mark suggested fingerings in output
```

---

## Step 6: Validate

Run MAMS_Validator.md counterpoint checks:

```
COUNTERPOINT_VALIDATION:
[ ] Motion balance (contrary ≥50% for equal voice)
[ ] Interval usage (no parallel 5ths/8ves unless intentional)
[ ] Divergence-convergence pattern present
[ ] Rhythmic independence achieved
[ ] Playability verified (Wyble or separate)
[ ] Range compliance (D3–G5)
[ ] Expressive DNA match (Wyble/Monder/Halvorson)
[ ] Album coherence maintained
```

**If FAIL:** Regenerate with corrections until PASS.

---

# OUTPUTS

## Directory Structure

```
/Trio Tunes/TuneXX_<Name>/Practice/Counterpoint/
├── Counterpoint_Line_1.musicxml
├── Counterpoint_Line_1.pdf
├── Counterpoint_Line_2.musicxml (optional)
├── Counterpoint_Line_2.pdf (optional)
└── Notes.md
```

## File Descriptions

| File | Content |
|:-----|:--------|
| `Counterpoint_Line_1.*` | Primary counterpoint (1 chorus) |
| `Counterpoint_Line_2.*` | Alternate version (optional) |
| `Notes.md` | Voice relationship analysis |

## Notes.md Structure

```markdown
# Counterpoint Notes for [Tune Name]

## Source Melody
- Version: [A/B/C/D]
- Character: [Lyrical/Angular/etc.]

## Counterpoint Settings
- Texture: [equal voice/supportive/bass-counterline]
- Angularity: [low/medium/high]

## Voice Relationship Analysis
- Motion breakdown: X% contrary, Y% oblique, Z% parallel
- Key moments: [bar numbers with descriptions]
- Divergence peak: Bar [X] (interval: [X])
- Convergence: Bars [X, Y, Z]

## Performance Notes
- Wyble fingerings: [if applicable]
- Register considerations
- Dynamic suggestions

## MAMS Compliance
- Expressive DNA: [Wyble/Monder/Halvorson]
- Validation: PASS
```

---

# EXAMPLE INVOCATION

```
COUNTERPOINT_COMPANION_GENERATOR(
    tune_number = 5,
    tune_name = "The Mirror",
    source_melody = "A",
    texture = "equal voice",
    angularity = "medium"
)

OUTPUT:
- Counterpoint_Line_1: Wyble-style two-voice texture
- Motion: 58% contrary, 32% oblique, 10% parallel
- Expressive DNA: Monder cinematic arc
- Peak divergence: Bar 9 (M10)
- Validation: PASS (48/50 GCE)
```

---

# INTEGRATION DEPENDENCIES

## Required Files

```
/MAMS/MAMS.md                           # Counterpoint DNA definitions
/MAMS/MAMS_Validator.md                 # Validation rules
/Trio Tunes/TuneXX_<Name>/Source/LeadSheet.md  # Source melodies
```

## Style References

- Jimmy Wyble two-voice independence
- Ben Monder harmonic density
- Mary Halvorson angular disruption
- GCE Melodic Development Rules (Contemporary Counterpoint)

---

**ENGINE STATUS: READY**

*Counterpoint Companion Generator v1.0 — MAMS Integrated*


