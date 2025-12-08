# Orchestral Engine (Small Orchestra Edition) v1.0

A small-orchestra generative system using open triads from the Open Triad Engine v1.0.

## Overview

The Orchestral Engine generates playable orchestral music for a small ensemble using open-triad voicings, contrapuntal writing, functional and modal harmonic movement, and adaptive voice-leading (VL-SM).

## Instruments

| Instrument | Range (MIDI) | Range (Concert) | Section |
|------------|--------------|-----------------|---------|
| Flute | 60-96 | C4-C7 | Winds |
| Clarinet in Bb | 50-93 | D3-A6 | Winds |
| Flugelhorn/Trumpet | 54-86 | F#3-D6 | Brass |
| Violin I | 55-100 | G3-E7 | Strings |
| Violin II | 55-86 | G3-D6 | Strings |
| Viola | 48-81 | C3-A5 | Strings |
| Cello | 36-76 | C2-E5 | Strings |
| Double Bass | 28-60 | E1-C4 | Strings |
| Piano | 21-108 | A0-C8 | Keyboard |
| Percussion | - | Variable | Percussion |

## Features

- **Texture Modes**: Homophonic, Contrapuntal, Hybrid, Harmonic Field, Ostinato, Orchestral Pads
- **Orchestration Profiles**: Bright, Warm, Dark, Transparent
- **Register Profiles**: High, Mid, Low, Mixed
- **VL-SM Integration**: Functional, Modal, Intervallic, Cinematic modes
- **Density Control**: Sparse, Medium, Dense
- **Export Formats**: JSON, MusicXML, HTML/PDF

## Quick Start

```python
from orchestral_engine import OrchestralEngine

# Create engine
engine = OrchestralEngine(
    key="C",
    scale="major",
    texture_mode="homophonic",
    orchestration_profile="warm"
)

# Generate 8 bars
texture = engine.generate_homophonic(bars=8)

# Export to MusicXML
score = engine.to_score(texture, title="My Orchestra")
engine.export(texture, "output/orchestra")
```

## Texture Modes

### Homophonic
Block chord textures with open-triad expansions across all instruments.

### Contrapuntal
Independent melodic lines in 3-6 parts with voice independence.

### Hybrid
Melody + inner motion + sustained pads + bass.

### Harmonic Field
Rotating modal/open-triad loops creating atmospheric textures.

### Ostinato
Rhythmic patterns in cello/bass with sustained pads.

## Orchestration Profiles

| Profile | Character | Emphasized Instruments |
|---------|-----------|------------------------|
| Bright | Light, airy | Flute, Violin I, Violin II, Flugelhorn |
| Warm | Rich, full | Clarinet, Viola, Cello, Violin II |
| Dark | Heavy, deep | Clarinet, Viola, Cello, Bass |
| Transparent | Clear, sparse | Flute, Violin I, Piano |

## Voice-Leading Modes (VL-SM)

### Functional Mode
- APVL (common-tone retention)
- TRAM (tension-release alternation)
- Smooth outer voices

### Modal Mode
- SISM spacing
- Intervallic freedom
- Color-tone emphasis

### Cinematic Mode
- Atmospheric spacing
- Building/releasing tension
- Orchestral color variation

## API Reference

### OrchestralEngine

```python
OrchestralEngine(
    key="C",
    scale="major",
    progression=None,
    texture_mode="homophonic",
    density="medium",
    motion_type="modal",
    orchestration_profile="warm",
    register_profile="mixed",
    rhythmic_style="straight",
    tempo=80,
    time_signature=(4, 4),
    seed=None
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
| `generate_ostinato(bars)` | Ostinato texture |
| `to_score(texture, title)` | Convert to score |
| `to_json(score)` | Export to JSON |
| `to_musicxml(score)` | Export to MusicXML |
| `export(texture, path)` | Export all formats |
| `get_diagnostics(texture)` | Get diagnostic info |

## Test Suite

Run the automated test suite:

```bash
cd OpenTriadEngine
python -m orchestral_engine.tests.run_test_suite
```

This runs 10 comprehensive tests covering all texture modes, VL-SM modes, orchestration profiles, and register profiles.

## Requirements

- Python 3.8+
- Open Triad Engine v1.0 (parent module)

## License

MIT License

## Version History

- v1.0.0 - Initial release
  - 10 instruments supported
  - 6 texture modes
  - 4 orchestration profiles
  - 4 VL-SM modes
  - Full MusicXML export
  - Test suite (10 tests)

