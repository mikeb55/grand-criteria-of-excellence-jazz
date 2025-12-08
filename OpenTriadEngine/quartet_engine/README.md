# Quartet Engine (Open Triad Edition) v1.0

A four-voice generative system for string quartet writing using the harmonic logic of the Open Triad Engine v1.0.

## Overview

The Quartet Engine generates playable string quartet music using open-triad voicings, contrapuntal voice behavior, functional and modal harmonic movement, and adaptive voice-leading (VL-SM).

## Features

- **Open-Triad Voicing Distribution**: Distributes open triads across Violin I, II, Viola, and Cello
- **Multiple Texture Modes**: Homophonic, contrapuntal, hybrid, harmonic field, rhythmic cells
- **VL-SM Integration**: Functional, modal, intervallic, and counterpoint voice-leading modes
- **Pattern Generation**: Inversion cycles, triad pairs, staggered entrances, hockets
- **Register Profiles**: Standard, high-lift (brighter), dark-low (heavier)
- **Rhythm Engine**: Unified, staggered, ostinato, polyrhythm, syncopation
- **Export Formats**: JSON, MusicXML (4 staves), HTML, PDF-ready output

## Installation

```bash
cd OpenTriadEngine
pip install -e .
```

## Quick Start

```python
from quartet_engine import QuartetEngine

# Create engine
engine = QuartetEngine(
    key="C",
    scale="major",
    quartet_mode="homophonic"
)

# Generate 8 bars
texture = engine.generate_homophonic(bars=8)

# Export to MusicXML
score = engine.to_score(texture, title="My Quartet")
xml = engine.to_musicxml(score)
```

## Texture Modes

### Homophonic
All instruments align harmonically using open-triad stacks.

```python
texture = engine.generate_homophonic(bars=8)
```

### Contrapuntal
Independent voices with triad-weighted harmonic targets.

```python
texture = engine.generate_contrapuntal(bars=8)
```

### Hybrid
Melody + harmony + inner counterlines.

```python
texture = engine.generate_hybrid(bars=8, melody_instrument=InstrumentType.VIOLIN_I)
```

### Harmonic Field
Rotating triads creating atmospheric textures.

```python
texture = engine.generate_harmonic_field(bars=8)
```

### Rhythmic Cells
Ostinatos, syncopation, and rhythmic interplay.

```python
texture = engine.generate_rhythmic_cells(bars=8)
```

## Voice-Leading Modes

### Functional Mode
- Common-tone retention (APVL)
- Tension-Release Alternating Motion (TRAM)
- Smooth outer voices

### Modal Mode
- Intervallic freedom
- Sum-Interval Stability Mapping (SISM)
- Color-tone emphasis

### Counterpoint Mode
- Independent melodic lines
- Contrary/oblique motion preferred
- Voice crossing prevention

## Instrument Ranges

| Instrument | Range | Sweet Spot |
|------------|-------|------------|
| Violin I   | G3-E6 | C4-C6     |
| Violin II  | G3-D6 | G3-G5     |
| Viola      | C3-A5 | C3-C5     |
| Cello      | C2-E5 | C2-G4     |

## Pattern Types

```python
from quartet_engine import PatternType

# Inversion cycles
pattern = engine.pattern_gen.generate_inversion_sweep(bars=8)

# Triad pairs
pattern = engine.pattern_gen.generate_triad_pair_gesture(
    bars=6,
    pair=((5, "major"), (7, "major"))  # F and G major
)

# Staggered entrances
pattern = engine.pattern_gen.generate_staggered_entrance(bars=8, offset_beats=1.0)

# Hocket
pattern = engine.pattern_gen.generate_hocket(bars=8)
```

## Export Formats

### JSON
```python
json_data = engine.to_json(score)
```

### MusicXML
```python
xml_string = engine.to_musicxml(score)
engine.output.save_musicxml(score, "output.musicxml")
```

### HTML (for PDF)
```python
engine.output.save_html(score, "output.html")
```

### All Formats
```python
files = engine.export(texture, "output/quartet", title="My Quartet")
# Returns: {"json": "...", "musicxml": "...", "html": "..."}
```

## Demo Methods

```python
# C major homophonic
texture = engine.demo_homophonic_c_major(bars=8)

# G major ii-V-I
texture = engine.demo_functional_ii_v_i(bars=4)

# D Dorian modal
texture = engine.demo_modal_dorian(bars=6)

# A minor counterpoint
texture = engine.demo_contrapuntal_a_minor(bars=4)
```

## Test Suite

Run the automated test suite:

```bash
cd OpenTriadEngine
python -m quartet_engine.tests.run_test_suite
```

This generates 10 comprehensive tests with JSON and MusicXML output.

## Integration with CEO Module

The Quartet Engine is designed to integrate with the Combined Engine Orchestrator (CEO):

```python
from ceo_module import CEO

ceo = CEO()
result = ceo.execute("Generate an 8-bar homophonic quartet in C major")
```

## API Reference

### QuartetEngine

```python
QuartetEngine(
    key="C",           # Musical key
    scale="major",     # Scale type
    progression=None,  # Optional chord progression
    quartet_mode="homophonic",  # Writing mode
    texture_density="medium",   # Texture density
    motion_type="modal",        # Harmonic motion
    register_profile="standard", # Register profile
    rhythmic_style="straight",   # Rhythmic style
    tempo=80,          # BPM
    time_signature=(4, 4),  # Time signature
    seed=None          # Random seed
)
```

### Key Methods

| Method | Description |
|--------|-------------|
| `generate(bars, mode)` | Generate texture |
| `generate_homophonic(bars)` | Homophonic texture |
| `generate_contrapuntal(bars)` | Contrapuntal texture |
| `generate_hybrid(bars)` | Hybrid texture |
| `generate_harmonic_field(bars)` | Harmonic field |
| `generate_rhythmic_cells(bars)` | Rhythmic cells |
| `generate_pattern(bars, type)` | Generate pattern |
| `generate_counterpoint(bars)` | Four-voice counterpoint |
| `to_score(texture, title)` | Convert to score |
| `to_json(score)` | Export to JSON |
| `to_musicxml(score)` | Export to MusicXML |
| `export(texture, path)` | Export all formats |

## Requirements

- Python 3.8+
- Open Triad Engine v1.0 (parent module)

## License

MIT License

## Version History

- v1.0.0 - Initial release
  - Open-triad voicing distribution
  - 5 texture modes
  - VL-SM integration
  - Pattern generation
  - MusicXML export
  - Test suite (10 tests)

