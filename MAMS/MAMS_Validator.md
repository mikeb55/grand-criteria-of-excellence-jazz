# MAMS Validator Engine v1.0
## Quality-Control Framework for Trio Tunes Melodic Generation

**Version:** 1.0  
**Date:** December 7, 2025  
**Status:** ACTIVE — Global Enforcement  

---

> **ACTIVATION STATUS: ENABLED**  
> All melodic outputs for Trio Tunes are subject to mandatory MAMS validation.  
> No melody may be finalized until achieving **FULL PASS** on all criteria.

---

# PURPOSE

This module ensures that all melodic outputs adhere to the unified album DNA specified in:
- `/MAMS/MAMS.md` (Master Album Motif System)
- Melodic Style Engine (All Influences)
- GCE Jazz Composition Rules

Every melody (Version A, B, C, or D), counterpoint line, etude, or motif-based composition must pass the following validation checks before finalization.

---

# VALIDATION PIPELINE

```
INPUT: Generated Melody

    ↓
┌─────────────────────────────────┐
│  1. MOTIF CHECK                 │ → FAIL = Regenerate
├─────────────────────────────────┤
│  2. INTERVAL DNA CHECK          │ → FAIL = Regenerate
├─────────────────────────────────┤
│  3. RHYTHMIC DNA CHECK          │ → FAIL = Regenerate
├─────────────────────────────────┤
│  4. TRIAD-PAIR DNA CHECK        │ → FAIL = Regenerate (if applicable)
├─────────────────────────────────┤
│  5. BLUES & BEBOP DNA CHECK     │ → FAIL = Regenerate (if applicable)
├─────────────────────────────────┤
│  6. EXPRESSIVE DNA CHECK        │ → FAIL = Regenerate
├─────────────────────────────────┤
│  7. TRANSFORMATION CHECK        │ → FAIL = Regenerate
├─────────────────────────────────┤
│  8. CONTOUR ARCHETYPE CHECK     │ → FAIL = Regenerate
├─────────────────────────────────┤
│  9. PLAYABILITY CHECK           │ → FAIL = Regenerate
├─────────────────────────────────┤
│ 10. ALBUM COHERENCE CHECK       │ → FAIL = Regenerate
├─────────────────────────────────┤
│ 11. GCE SCORE CHECK             │ → FAIL if < 45/50
└─────────────────────────────────┘
    ↓
ALL PASS = OUTPUT APPROVED
```

---

# 1. MOTIF CHECK (MANDATORY)

## Requirement
A melody is **valid only if** it contains:
- **Minimum 2 occurrences** of any core MAMS motif (M1–M7), **OR**
- **1 motif used + at least 1 motif transformation**

## Core Motif Library

| ID | Name | Interval Signature | Detection Pattern |
|:--:|:-----|:-------------------|:------------------|
| **M1** | **The Question** | P4↑ → M2↑ → m3↓ | [+5, +2, -3] semitones |
| **M2** | **Blues Cry** | m3↑bend → P5↑ → m6↓ | [+3↑, +7, -8] with blue inflection |
| **M3** | **Angular Cell** | M7↑ → m2↓ → P4↑ | [+11, -1, +5] |
| **M4** | **Bebop Seed** | 1-2-3-5 + enclosure | [+2, +2, +4] + chromatic approach |
| **M5** | **Floating Fourth** | P4 → P4 → P4 | [+5, +5, +5] or [-5, -5, -5] |
| **M6** | **The Resolution** | M7↓ → m3↑ | [-11, +3] |
| **M7** | **Textural Ghost** | Wide + REST + Wide | [variable, REST, variable] |

## Validation Logic

```
MOTIF_CHECK(melody):
    motif_count = 0
    transformation_count = 0
    
    FOR each motif M1-M7:
        IF detect_motif(melody, motif):
            motif_count += 1
        IF detect_transformation(melody, motif):
            transformation_count += 1
    
    IF motif_count >= 2:
        RETURN PASS
    ELSE IF motif_count >= 1 AND transformation_count >= 1:
        RETURN PASS
    ELSE:
        RETURN FAIL("Insufficient motif usage: found {motif_count} motifs, {transformation_count} transformations")
```

## Transformation Detection

Validator must detect:
| Transform | Symbol | Detection Method |
|:----------|:------:|:-----------------|
| Transposition | T | Same intervals, different pitch center |
| Inversion | I | Mirrored interval directions |
| Retrograde | R | Reversed note order |
| Augmentation | A | Doubled rhythmic values |
| Diminution | D | Halved rhythmic values |
| Fragmentation | F | Subset of motif (≥50% of original) |
| Sequence | S | Exact interval pattern at new pitch |
| Rhythmic Displacement | RD | Same pitches, shifted beat placement |
| Octave Displacement | OD | Notes moved by octave(s) |

---

# 2. INTERVAL DNA CHECK (MANDATORY)

## Requirement
The melody must contain **at least 2** of the following interval signatures:

| Interval | Semitones | Character | Context |
|:---------|:---------:|:----------|:--------|
| **P4** | 5 | Open, modal | Quartal melodies, open voicings |
| **M7 leap** | 11 | Wide, yearning | Climax points, modern lines |
| **m6** | 8 | Melancholic | Ballads, descending lines |
| **#11** | 6 | Lydian, floating | Lydian passages, tension |
| **Interval contraction** | — | After wide leap | Balance principle |
| **Ant Law set (2–6–♭3–#4)** | [2,9,3,6] | Angular, modern | Contemporary passages |
| **Blues b3→3** | 3→4 | Blue note resolution | Lyrical/roots tunes |

## Validation Logic

```
INTERVAL_CHECK(melody):
    found_intervals = []
    
    FOR each interval in melody:
        IF interval IN [P4, M7, m6, TT/#11]:
            found_intervals.append(interval)
        IF wide_leap_followed_by_step(interval, next_interval):
            found_intervals.append("contraction")
        IF detect_ant_law_set(melody_segment):
            found_intervals.append("Ant Law")
        IF detect_blues_bend(interval):
            found_intervals.append("blues")
    
    IF len(unique(found_intervals)) >= 2:
        RETURN PASS
    ELSE:
        RETURN FAIL("Insufficient interval DNA: found only {found_intervals}")
```

---

# 3. RHYTHMIC DNA CHECK (MANDATORY)

## Requirement
Melody must contain **at least 1** of the following:

| Rhythm Type | Description | Applicable Versions |
|:------------|:------------|:--------------------|
| **Behind-beat swing** | Notes placed late in swing feel | A, C |
| **3:4 or 5:4 metric cell** | Polyrhythmic grouping | B, D |
| **Rhythmic fragmentation** | Broken motifs, stabs | B, D |
| **Long-tone lyrical arc** | Sustained notes, breath shapes | A |
| **3+3+2 grouping** | Additive rhythm | B, C |
| **Metric modulation** | Tempo illusion | B, D |
| **Space as music** | Deliberate rests | A, D |

## Validation Logic

```
RHYTHMIC_CHECK(melody, version):
    rhythmic_features = analyze_rhythm(melody)
    
    IF version == "A":
        required = ["swing", "long-tone", "space"]
    ELSE IF version == "B":
        required = ["polyrhythm", "fragmentation", "additive"]
    ELSE IF version == "C":
        required = ["swing", "continuous_8ths", "additive"]
    ELSE IF version == "D":
        required = ["displacement", "polyrhythm", "space"]
    
    IF any(feature IN rhythmic_features FOR feature IN required):
        RETURN PASS
    ELSE:
        RETURN FAIL("Missing rhythmic DNA for version {version}")
```

---

# 4. TRIAD-PAIR DNA CHECK (CONTEXT-DEPENDENT)

## Applicability
**Required for:** Modern, modal, or post-bop tunes (Version B primarily)

## Requirement
Melody must use at least:
- **1 triad-pair cell**, OR
- **1 transformation of a triad-pair cell**, OR
- **Tonality Vault behavior** (stable triad + colour triad)

## Valid Triad-Pair Relationships

| ID | Pair Type | Interval | Sound |
|:--:|:----------|:---------|:------|
| TP-1 | Major + Major (M2 apart) | Whole step | Lydian |
| TP-2 | Major + Minor (m3 apart) | Minor 3rd | Dorian |
| TP-3 | Major + Augmented | Various | Altered |
| TP-4 | Minor + Minor (M2 apart) | Whole step | Dark modal |
| TP-5 | Tritone pairs | TT | Maximum tension |

## Validation Logic

```
TRIAD_PAIR_CHECK(melody, style):
    IF style NOT IN ["modern", "modal", "post-bop", "angular"]:
        RETURN SKIP  # Not applicable
    
    triad_cells = detect_triad_pairs(melody)
    
    IF len(triad_cells) >= 1:
        RETURN PASS
    ELSE:
        RETURN FAIL("Modern style requires triad-pair DNA")
```

---

# 5. BLUES & BEBOP DNA CHECK (CONTEXT-DEPENDENT)

## Applicability
**Blues DNA Required:** Lyrical tunes, roots-influenced, blues forms  
**Bebop DNA Required:** Functional ii-V-I passages, uptempo swing

## Blues DNA Elements

| ID | Element | Detection |
|:--:|:--------|:----------|
| BL-1 | Blue note inflection | b3, b5, b7 bends/grace notes |
| BL-2 | Call & Response | 2-bar phrase pairs |
| BL-3 | Double-stop 3rds/6ths | Parallel harmony |
| BL-4 | Minor pentatonic foundation | 1-b3-4-5-b7 |
| BL-5 | Chromatic enclosure (blues) | Approach tones |
| BL-6 | Shuffle feel | Triplet groove |

## Bebop DNA Elements

| ID | Element | Detection |
|:--:|:--------|:----------|
| BB-1 | Bebop scale usage | Added passing tones |
| BB-2 | Enclosure patterns | Chromatic + diatonic surrounding |
| BB-3 | Chord-tone targeting | 3rd/7th on strong beats |
| BB-4 | 1-2-3-5 cell | Universal bebop block |
| BB-5 | Diminished approaches | Dim7 resolving down half-step |
| BB-6 | Double-time passages | 16ths over swing |
| BB-7 | Guide tone lines | 3rd→7th voice leading |

## Validation Logic

```
BLUES_BEBOP_CHECK(melody, harmony, style):
    IF style IN ["blues", "lyrical", "roots", "soul-jazz"]:
        blues_elements = detect_blues_dna(melody)
        IF len(blues_elements) < 2:
            RETURN FAIL("Blues style requires Blues DNA")
    
    IF contains_ii_V_I(harmony):
        bebop_elements = detect_bebop_dna(melody)
        IF len(bebop_elements) < 2:
            RETURN FAIL("ii-V-I passages require Bebop DNA")
    
    RETURN PASS
```

---

# 6. EXPRESSIVE DNA CHECK (MANDATORY)

## Requirement
Generated melody must align with **at least one** expressive family based on version type.

## Version A — Lyrical Expressive Family

| Influence | Required Character |
|:----------|:-------------------|
| **Jim Hall** | Space as compositional element, incomplete resolutions |
| **Bill Frisell** | Ambient sustain, volume swells, horizontal expansion |
| **Pat Metheny** | Wide intervals resolving to singing phrases, optimism |
| **Grant Green** | Clean single notes, straightforward blues roots |

**Detection:** Long tones, deliberate rests, singing contour, restraint

## Version B — Modern Expressive Family

| Influence | Required Character |
|:----------|:-------------------|
| **Wayne Shorter** | Asymmetric phrases, harmonic poetry, enigma |
| **Kurt Rosenwinkel** | Multi-octave legato, vocal-like continuity |
| **Ant Law** | Wide intervals, unusual groupings, intervallic innovation |
| **Mary Halvorson** | Unexpected bends, deliberately awkward phrasing |

**Detection:** Angular intervals, continuous flow, unpredictable contour

## Version C — Bebop Expressive Family

| Influence | Required Character |
|:----------|:-------------------|
| **Charlie Parker** | Lightning vocabulary, endless invention |
| **Sonny Stitt** | Clean bebop execution, flowing 8th streams |
| **George Benson** | Fluid virtuosity, seamless runs |
| **Steve Khan** | Harmonic sophistication, rhythmic awareness |

**Detection:** Continuous 8ths, enclosures, chord-tone targeting, bebop scales

## Version D — Counterpoint/Hybrid Expressive Family

| Influence | Required Character |
|:----------|:-------------------|
| **Jimmy Wyble** | Two-voice independence, contrary motion |
| **Ben Monder** | Harmonic density, layered textures |
| **Bill Frisell** | Blurred boundaries, textural ambiguity |
| **Mary Halvorson** | Fractured counterpoint, angular disruption |

**Detection:** Voice independence, contrary motion >50%, textural spacing

## Validation Logic

```
EXPRESSIVE_CHECK(melody, version):
    IF version == "A":
        required_traits = ["space", "singing_contour", "restraint"]
        influences = ["Hall", "Frisell", "Metheny", "Green"]
    ELSE IF version == "B":
        required_traits = ["angular", "continuous", "unpredictable"]
        influences = ["Shorter", "Rosenwinkel", "Law", "Halvorson"]
    ELSE IF version == "C":
        required_traits = ["8th_flow", "enclosure", "targeting"]
        influences = ["Parker", "Stitt", "Benson", "Khan"]
    ELSE IF version == "D":
        required_traits = ["independence", "contrary_motion", "texture"]
        influences = ["Wyble", "Monder", "Frisell", "Halvorson"]
    
    detected_traits = analyze_expressive(melody)
    
    IF count_matches(detected_traits, required_traits) >= 2:
        RETURN PASS
    ELSE:
        RETURN FAIL("Melody lacks expressive DNA for version {version}")
```

---

# 7. TRANSFORMATION CHECK (MANDATORY)

## Requirement
At least **one transformation** must be applied to at least **one motif**.

## Valid Transformations

| Transform | Symbol | Validation Criteria |
|:----------|:------:|:--------------------|
| **Inversion** | I | Interval directions mirrored |
| **Retrograde** | R | Note order reversed |
| **Augmentation** | A | Durations doubled (±10% tolerance) |
| **Diminution** | D | Durations halved (±10% tolerance) |
| **Transposition** | T | Pitch shifted, intervals preserved |
| **Sequence** | S | Pattern repeated at new pitch level |
| **Polyrhythmic displacement** | PD | Grouping shifted across beat |
| **Microtonal variant** | MV | Pitch bent/adjusted microtonally |
| **Octave displacement** | OD | Notes moved by ±12 semitones |
| **Fragmentation** | F | ≥50% of motif used |

## Validation Logic

```
TRANSFORMATION_CHECK(melody):
    transformations_found = []
    
    FOR each motif M1-M7:
        IF detect_inversion(melody, motif):
            transformations_found.append("I")
        IF detect_retrograde(melody, motif):
            transformations_found.append("R")
        IF detect_augmentation(melody, motif):
            transformations_found.append("A")
        IF detect_diminution(melody, motif):
            transformations_found.append("D")
        IF detect_transposition(melody, motif):
            transformations_found.append("T")
        IF detect_sequence(melody, motif):
            transformations_found.append("S")
        IF detect_fragmentation(melody, motif):
            transformations_found.append("F")
        IF detect_octave_displacement(melody, motif):
            transformations_found.append("OD")
    
    IF len(transformations_found) >= 1:
        RETURN PASS
    ELSE:
        RETURN FAIL("No motif transformations detected")
```

---

# 8. CONTOUR ARCHETYPE CHECK (MANDATORY)

## Requirement
Each major phrase must conform to a **recognized phrase-shape archetype**.

## Valid Phrase Shapes

| Shape | Contour | Character | Applicable Sections |
|:------|:--------|:----------|:--------------------|
| **Arc** | ↗↘ | Complete statement | Theme melodies |
| **Rising** | ↗↗ | Building tension | Pre-climax |
| **Falling** | ↘↘ | Resolution | Post-climax, endings |
| **Wave** | ↗↘↗↘ | Development | Extended passages |
| **Plateau** | ↗→ | Sustained tension | Pedal points |
| **Valley** | ↘↗ | Recovery | After tension |
| **Jagged** | ↗↘↗↘↗ | Angular | Experimental |
| **Horizontal** | → | Static | Vamps, grooves |

## Validation Logic

```
CONTOUR_CHECK(melody):
    phrases = segment_into_phrases(melody)
    
    FOR each phrase:
        contour = analyze_contour(phrase)
        IF contour NOT IN valid_archetypes:
            RETURN FAIL("Phrase {n} has unrecognized contour")
    
    RETURN PASS
```

---

# 9. PLAYABILITY CHECK (MANDATORY)

## Guitar Range Constraint

```
VALID RANGE: D3 (2nd fret, D string) to G5 (20th fret, E string)
MIDI: 50 to 79
```

## Version C Counterpoint: Single-Staff Rule (MANDATORY)

```
┌─────────────────────────────────────────────────────────────────┐
│  VERSION C (COUNTERPOINT) NOTATION RULE                         │
│                                                                 │
│  ✓ CORRECT: Single staff with two voices                       │
│     - Voice 1 (stems UP)   = Top voice / Melody                 │
│     - Voice 2 (stems DOWN) = Bottom voice / Counterpoint        │
│     - Use MusicXML <backup> to layer voices on same staff       │
│                                                                 │
│  ✗ WRONG: Two separate staves (implies two instruments)         │
│     - Never use <staves>2</staves> for guitar counterpoint      │
│                                                                 │
│  This is ONE guitar, not two!                                   │
└─────────────────────────────────────────────────────────────────┘

COUNTERPOINT_NOTATION_CHECK(version, musicxml):
    IF version == "C":
        stave_count = count_staves(musicxml)
        IF stave_count > 1:
            RETURN FAIL("Version C must use single staff with 2 voices")
        
        voice_count = count_unique_voices(musicxml)
        IF voice_count < 2:
            RETURN FAIL("Version C counterpoint requires 2 voices")
        
        stem_directions = check_stem_directions(musicxml)
        IF NOT (voice_1_stems_up AND voice_2_stems_down):
            RETURN FAIL("Voice 1 must have stems up, Voice 2 stems down")
    
    RETURN PASS
```

## Playability Rules

| Rule | Validation |
|:-----|:-----------|
| **Range** | All notes within D3–G5 |
| **Fret Span** | Maximum 5 frets per position |
| **String Skip** | Maximum 2 strings skipped |
| **Position Shift** | Smooth shifts, no sudden jumps >5 frets |
| **Articulation** | Idiomatic (hammer-ons, pull-offs, slides feasible) |
| **Fingering** | Logical left-hand shapes |
| **Counterpoint Spacing** | Max 10th between voices (Version C) |

## Validation Logic

```
PLAYABILITY_CHECK(melody):
    # Range check
    FOR each note:
        IF note < D3 OR note > G5:
            RETURN FAIL("Note {note} out of guitar range")
    
    # Interval check
    FOR each interval:
        IF interval > 12 AND not_guitaristically_feasible(interval):
            RETURN FAIL("Interval {interval} not guitaristic")
    
    # Position coherence
    positions = calculate_positions(melody)
    FOR each shift in positions:
        IF shift > 5 frets AND no_logical_path(shift):
            RETURN FAIL("Position shift too extreme")
    
    RETURN PASS
```

---

# 10. ALBUM COHERENCE CHECK (MANDATORY)

## Requirement
New melody must maintain continuity with existing tunes by:

| Coherence Aspect | Validation |
|:-----------------|:-----------|
| **Motif reuse** | Uses motifs established in previous tunes |
| **Interval DNA** | References same interval signatures |
| **Rhythmic identity** | Maintains consistent rhythmic vocabulary |
| **Expressive character** | Doesn't contradict established profiles |
| **Transformation consistency** | Similar transformation palette |

## Album Motif Registry

Validator maintains a registry of motif usage across all tunes:

```
ALBUM_COHERENCE_CHECK(melody, tune_number):
    # Load existing motif usage
    registry = load_motif_registry()
    
    # Check for motif reuse
    current_motifs = extract_motifs(melody)
    
    IF tune_number > 1:
        shared_motifs = intersection(current_motifs, registry.all_motifs)
        IF len(shared_motifs) == 0:
            RETURN WARNING("No motif connection to previous tunes")
    
    # Check expressive consistency
    IF contradicts_album_character(melody):
        RETURN FAIL("Melody contradicts established album character")
    
    # Update registry
    registry.add(tune_number, current_motifs)
    
    RETURN PASS
```

---

# 11. GCE SCORE CHECK (MANDATORY)

## Requirement
Melody must achieve **minimum 45/50** on GCE evaluation.

## GCE Criteria

| Criterion | Max Score | Validation Focus |
|:----------|:---------:|:-----------------|
| Melody Clarity | 5 | Phrase-shape archetypes |
| Harmony Logic | 5 | Triad-pair DNA |
| Voice Leading | 5 | Interval DNA, guide tones |
| Counterpoint | 5 | Independence (Version D) |
| Triad Colour | 5 | Triad-pair usage |
| Guitaristic Writing | 5 | Playability check |
| Structure | 5 | Motif + transformation |
| Emotional Narrative | 5 | Expressive DNA |
| Originality | 5 | Transformation variety |
| Technique Unity | 5 | Album coherence |

## Validation Logic

```
GCE_CHECK(melody, harmony, version):
    scores = {}
    scores["clarity"] = evaluate_clarity(melody)
    scores["harmony"] = evaluate_harmony(melody, harmony)
    scores["voice_leading"] = evaluate_voice_leading(melody)
    scores["counterpoint"] = evaluate_counterpoint(melody, version)
    scores["triad_colour"] = evaluate_triad_usage(melody)
    scores["guitaristic"] = evaluate_playability(melody)
    scores["structure"] = evaluate_structure(melody)
    scores["narrative"] = evaluate_expression(melody)
    scores["originality"] = evaluate_originality(melody)
    scores["unity"] = evaluate_coherence(melody)
    
    total = sum(scores.values())
    
    IF total >= 45:
        RETURN PASS(total)
    ELSE:
        RETURN FAIL("GCE score {total}/50 below threshold (45)")
```

---

# VALIDATION OUTPUT FORMAT

## On Every Melody Generation

```
═══════════════════════════════════════════════════════════════
                    MAMS VALIDATOR REPORT
═══════════════════════════════════════════════════════════════
Tune: [Tune Name]
Version: [A/B/C/D]
Generated: [Timestamp]
───────────────────────────────────────────────────────────────

CHECK                          STATUS    DETAILS
───────────────────────────────────────────────────────────────
1.  Motif Check                [PASS]    M1 x2, M4 x1
2.  Interval DNA Check         [PASS]    P4, M7, m6 detected
3.  Rhythmic DNA Check         [PASS]    Swing 8ths, space
4.  Triad-Pair DNA Check       [SKIP]    Not applicable (blues)
5.  Blues/Bebop DNA Check      [PASS]    BL-1, BL-4, BB-3
6.  Expressive DNA Check       [PASS]    Hall, Green profiles
7.  Transformation Check       [PASS]    T, S, RD applied
8.  Contour Archetype Check    [PASS]    Arc, Wave shapes
9.  Playability Check          [PASS]    Range D3-G5 OK
10. Album Coherence Check      [PASS]    M1 links to Tune 1
11. GCE Score Check            [PASS]    48/50

───────────────────────────────────────────────────────────────
OVERALL RESULT:                ██ PASS ██
───────────────────────────────────────────────────────────────
Motifs Used: M1, M4
Transformations: Transposition (T), Sequence (S), Rhythmic Displacement (RD)
Expressive Profile: Jim Hall (space), Grant Green (directness)
GCE Score: 48/50
═══════════════════════════════════════════════════════════════
```

## On Validation Failure

```
═══════════════════════════════════════════════════════════════
                    MAMS VALIDATOR REPORT
═══════════════════════════════════════════════════════════════
Tune: [Tune Name]
Version: [A/B/C/D]
Generated: [Timestamp]
───────────────────────────────────────────────────────────────

CHECK                          STATUS    DETAILS
───────────────────────────────────────────────────────────────
1.  Motif Check                [FAIL]    Only 1 motif, no transforms
2.  Interval DNA Check         [PASS]    P4, m6 detected
3.  Rhythmic DNA Check         [PASS]    Swing 8ths
4.  Triad-Pair DNA Check       [SKIP]    Not applicable
5.  Blues/Bebop DNA Check      [FAIL]    Missing blues DNA
6.  Expressive DNA Check       [PASS]    Hall profile
7.  Transformation Check       [FAIL]    No transformations
8.  Contour Archetype Check    [PASS]    Arc shape
9.  Playability Check          [PASS]    Range OK
10. Album Coherence Check      [WARN]    No motif link
11. GCE Score Check            [FAIL]    38/50

───────────────────────────────────────────────────────────────
OVERALL RESULT:                ██ FAIL ██
───────────────────────────────────────────────────────────────

VIOLATIONS:
• Motif Check: Add M2 (Blues Cry) in bars 5-6
• Blues DNA: Add BL-1 (blue note) in bar 3, BL-4 in bar 9
• Transformation: Apply Sequence (S) to M1 in bar 5
• GCE Score: Improve structure and triad colour

ACTION: Regenerating melody with fixes applied...
═══════════════════════════════════════════════════════════════
```

---

# AUTOMATIC REGENERATION PROTOCOL

When validation fails:

```
REGENERATE_PROTOCOL(melody, failures):
    
    FOR each failure:
        IF failure.type == "MOTIF":
            melody = inject_motif(melody, get_missing_motif())
        
        IF failure.type == "INTERVAL":
            melody = adjust_intervals(melody, required_intervals)
        
        IF failure.type == "RHYTHM":
            melody = adjust_rhythm(melody, required_rhythm)
        
        IF failure.type == "TRIAD_PAIR":
            melody = inject_triad_pair(melody, harmony)
        
        IF failure.type == "BLUES_BEBOP":
            melody = inject_blues_bebop(melody, style)
        
        IF failure.type == "EXPRESSIVE":
            melody = reshape_expression(melody, version)
        
        IF failure.type == "TRANSFORM":
            melody = apply_transformation(melody, random_transform)
        
        IF failure.type == "CONTOUR":
            melody = reshape_contour(melody, target_archetype)
        
        IF failure.type == "PLAYABILITY":
            melody = adjust_range(melody, D3, G5)
        
        IF failure.type == "COHERENCE":
            melody = inject_album_motif(melody, registry)
        
        IF failure.type == "GCE":
            melody = optimize_gce(melody, weak_criteria)
    
    # Re-validate
    RETURN validate(melody)
```

---

# GLOBAL ENFORCEMENT RULES

## Always Active

1. **Load MAMS.md** alongside Melodic Style Engine for every melodic request
2. **Run full validation** before outputting any melody
3. **Enforce album motif consistency** across all tunes
4. **Enforce guitaristic playability** (D3–G5)
5. **Enforce minimum GCE score** (45/50)
6. **Treat motif usage as mandatory**, not optional
7. **Never finalize** a melody that fails any check

## Version-Specific Enforcement

| Version | Primary Checks | Secondary Checks |
|:--------|:---------------|:-----------------|
| **A (Lyrical)** | Expressive (Hall/Frisell), Blues DNA, Space | Motif, Interval |
| **B (Modern)** | Triad-Pair DNA, Angular intervals, Transforms | Motif, Rhythmic |
| **C (Bebop)** | Bebop DNA, Continuous 8ths, Enclosures | Motif, Interval |
| **D (Counterpoint)** | Voice independence, Contrary motion | Motif, Expressive |

---

# FILE DEPENDENCIES

## Required Files (Auto-Load)

```
/MAMS/MAMS.md                  # Master motif system
/Trio Tunes/MD/*.md            # Tune lead sheets
/Composition Rules/GCE_*.md    # GCE evaluation rules
/Bebop Language/*.md           # Bebop engine definitions
```

## Output Integration

All validated melodies must include:
- MAMS Validator Report
- Motifs used (with bar locations)
- Transformations applied
- DNA layers active
- GCE score breakdown

---

**VALIDATOR STATUS: ACTIVE**

*All melodic generation for Trio Tunes is now subject to MAMS validation.*

---

# CHANGELOG

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.0 | December 7, 2025 | Initial release — full validation pipeline |

---

**END OF MAMS VALIDATOR SPECIFICATION**


