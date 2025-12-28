# Barry Engine

**Barry** is an abstract, rule-based jazz engine built on **General Musical Language (GML)**, inspired by Barry Harris-style concepts of movement, bebop language, and clear criteria of excellence.

## Purpose

Barry serves as the "musical brain" that:
- Analyzes GML phrases, progressions, and sections
- Scores them against explicit jazz criteria
- Suggests improvements (or generates alternatives) that are more idiomatic, better voiced, and structurally clearer

Barry is **instrument-agnostic**: it does not know about fretboards or DAWs directly; other tools call Barry and then handle instrument or UI details.

## Core Concepts

### 1. Movement-Based Harmony and Voice-Leading
- Prefers **stepwise** or small-interval motion between successive chord tones
- Emphasizes **guide tones** (3rds, 7ths, tensions like 9, 11, 13) and their smooth resolution
- Recognizes standard movement patterns: ii–V–I chains, turnarounds, diminished passing chords
- Penalizes large, unmotivated leaps

### 2. Idiomatic Bebop Language
- Favors **8th-note-based** lines with clear chord-tone targeting
- Uses **approach tones and enclosures** resolving into chord tones on strong beats
- Prefers chromaticism that can be explained (enclosures, approach tones, scales)
- Rewards **downbeat chord tones** on important harmonic beats

### 3. Grand Criteria of Excellence
- **Tension-release arcs**: Phrases build and release tension in recognizable waves
- **Motivic development**: Reuse and variation of ideas (sequence, inversion, displacement)
- **Form and architecture**: Respects encoded forms (AABA, ABAC, blues, etc.)
- **Idiomaticity**: Rewards lines that resemble real jazz practice
- **Playability**: Models range and density constraints (abstract)

## Location

BarryEngine is located at the **top level** of the `grand-criteria-of-excellence-jazz` repository, alongside other core modules:
- `BarryEngine/` - This module (jazz analysis and improvement engine)
- `Bebop Language/` - Bebop language specifications
- `Composition Rules/` - Composition rules and guidelines
- `Jazz Guitar/` - Jazz guitar-specific material
- `OpenTriadEngine/` - Open triad generation engine

## Installation

```bash
# BarryEngine is part of the GCE-Jazz project
# No separate installation needed - import directly from the top level
```
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
read_file

## Quick Start

### Basic Analysis

```python
from barry_engine import (
    GMLPhrase, GMLProgression, BarryEngine,
    note_from_midi, phrase_from_pitches
)

# Create a phrase
notes = [
    note_from_midi(60, duration=0.5, onset=0.0),  # C4
    note_from_midi(62, duration=0.5, onset=0.5),  # D4
    note_from_midi(64, duration=0.5, onset=1.0),  # E4
]
phrase = GMLPhrase(notes=notes, key="C")

# Create a progression
progression = GMLProgression(
    chords=["Cm7", "F7", "BbMaj7"],
    key="C"
)

# Analyze
engine = BarryEngine()
result = engine.analyze_phrase(phrase, progression)

print(f"Overall score: {result.overall:.2f}")
print(f"Movement score: {result.movement.overall:.2f}")
print(f"Bebop score: {result.bebop.overall:.2f}")
for tag in result.tags:
    print(f"  - {tag}")
```

### Transformation

```python
from barry_engine import improve_line_movement, add_bebop_enclosures

# Improve movement
result = improve_line_movement(phrase, progression)
print("Changes made:")
for change in result.changes_made:
    print(f"  - {change}")

# Add bebop enclosures
result = add_bebop_enclosures(phrase, progression)
```

### Section Analysis

```python
from barry_engine import GMLSection, GMLForm, PhraseRole

# Create a section with multiple phrases
section = GMLSection(
    phrases=[phrase1, phrase2, phrase3],
    label="A",
    form=GMLForm.AABA
)

# Analyze section
result = engine.analyze_section(section)
print(f"GCE score: {result.gce.overall:.2f}")
print(f"Tension-release: {result.gce.tension_release:.2f}")
print(f"Motivic development: {result.gce.motivic_development:.2f}")
```

## API Reference

### Analysis Functions

#### `score_phrase_movement(phrase, progression=None) -> MovementScore`
Scores a phrase for movement-based harmony and voice-leading.

**Returns:**
- `stepwise_ratio`: Ratio of stepwise motions
- `guide_tone_score`: Quality of guide tone resolution
- `voice_leading_score`: Smoothness of voice-leading
- `progression_score`: Recognition of standard patterns
- `leap_penalty`: Penalty for large unmotivated leaps
- `overall`: Overall movement score
- `issues`: List of issue descriptions

#### `score_phrase_bebop_idiom(phrase, harmony=None) -> BebopScore`
Scores a phrase for bebop language idiomaticity.

**Returns:**
- `eighth_note_ratio`: Ratio of 8th-note durations
- `chord_tone_targeting`: Quality of chord tone targeting on downbeats
- `approach_tone_usage`: Quality of approach tone usage
- `enclosure_usage`: Quality of enclosure patterns
- `chromatic_explanation`: How well chromaticism is explained
- `overall`: Overall bebop score
- `issues`: List of issue descriptions

#### `score_section_form_alignment(section, form=None) -> GCEScore`
Scores a section for Grand Criteria of Excellence.

**Returns:**
- `tension_release`: Quality of tension-release arcs
- `motivic_development`: Quality of motivic development
- `form_alignment`: Alignment with form structure
- `idiomaticity`: Idiomatic jazz language usage
- `playability`: Abstract playability score
- `overall`: Overall GCE score
- `issues`: List of issue descriptions

### Transformation Functions

#### `improve_line_movement(phrase, harmony=None) -> TransformationResult`
Enhances stepwise motion and voice-leading in a phrase.

#### `add_bebop_enclosures(phrase, harmony=None) -> TransformationResult`
Adds bebop enclosures to chord tones in a phrase.

#### `strengthen_cadence(phrase, cadence_context=None) -> TransformationResult`
Improves cadential resolution in a phrase.

### Orchestration Functions

#### `evaluate_phrase_bundle(phrases, context=None) -> List[AnalysisResult]`
Evaluates multiple phrase candidates and returns analysis for each.

#### `suggest_best_candidate_line(candidates, context=None) -> Tuple[GMLPhrase, AnalysisResult]`
Suggests the best candidate line from multiple options based on overall score.

## GML Data Structures

### `GMLNote`
Represents a single note:
- `pitch_class`: 0-11 (0=C, 1=C#, etc.)
- `octave`: Octave number (middle C = 4)
- `duration`: Duration in beats
- `onset`: Start time in beats
- `harmonic_context`: Optional chord symbol

### `GMLPhrase`
Represents a musical phrase:
- `notes`: List of GMLNote objects
- `bar_start`, `bar_end`: Bar numbers
- `role`: PhraseRole (OPENING, CONTINUATION, CADENTIAL, etc.)
- `harmonic_progression`: Optional list of chord symbols
- `key`: Key signature

### `GMLProgression`
Represents a chord progression:
- `chords`: List of chord symbols
- `functions`: Optional list of HarmonicFunction
- `key`: Key signature
- `bars_per_chord`: Optional list of bar counts per chord

### `GMLSection`
Represents a section of a composition:
- `phrases`: List of GMLPhrase objects
- `label`: Section label (e.g., "A", "B")
- `form`: GMLForm (AABA, ABAC, BLUES_12, etc.)
- `key`: Key signature

## Design Principles

1. **Stateless and Deterministic**: Same GML input → same result
2. **Instrument-Agnostic**: Works with abstract GML, not instrument-specific details
3. **Rule-Based**: Explicit jazz criteria, not machine learning
4. **Modular**: Small, clear functions that can be composed
5. **Explainable**: Returns scores with issue descriptions and tags

## Integration

Barry is designed to be called by other tools:
- Fretboard projectors can convert Barry's GML output to tablature
- DAWs can convert to MIDI or notation
- Other engines can use Barry's scores to guide generation

## Examples

See `examples/` directory for more detailed examples.

## License

Part of the GCE-Jazz project.

