# Triad Pair Solo Engine (Open Triad Edition)

An improvisation-focused generator that produces intervallic, modern jazz solo lines using triad pairs transformed into open triads.

## Overview

The Triad Pair Solo Engine integrates with **Open Triad Engine v1.0** to generate sophisticated jazz solo phrases. It supports:

- **Diatonic triad pairs** - Adjacent and non-adjacent scale-degree combinations
- **Klemonic pairs** - Stable + tension triads following Jordan Klemons' principles
- **UST (Upper Structure Triad) pairs** - For altered dominants, Lydian, melodic minor
- **Altered dominant pairs** - Derived from 7♭9, 7alt, diminished whole-tone

## Installation

```bash
# From the OpenTriadEngine directory
pip install -e .

# Or add to your Python path
import sys
sys.path.insert(0, '/path/to/OpenTriadEngine')
```

## Quick Start

```python
from triad_pair_solo_engine import TriadPairSoloEngine

# Create engine
engine = TriadPairSoloEngine(
    key="C",
    scale="dorian",
    triad_pair_type="diatonic",
    mode="intervallic",
    rhythmic_style="swing"
)

# Generate a 4-bar phrase
phrase = engine.generate_phrase(bars=4)

# Export to all formats
engine.export(phrase, "output/my_solo")
```

## Features

### Triad Pair Types

| Type | Description | Use Case |
|------|-------------|----------|
| `diatonic` | Scale-degree triads | Modal jazz, standard changes |
| `klemonic` | Stable + tension pairs | Chord-specific tension |
| `ust` | Upper structure triads | Altered dominants, modern harmony |
| `altered_dominant_pairs` | 7alt, 7♭9, 7#9 derived | Outside playing |

### Solo Modes

| Mode | Description | Voice-Leading |
|------|-------------|---------------|
| `intervallic` | Wide leaps, SISM spacing | Maximum motion |
| `functional` | APVL, TRAM | Smooth voice-leading |
| `modal` | Floating, open lines | Balanced motion |
| `hybrid` | Mixed approach | Adaptive |

### Rhythmic Styles

- `straight` - Even 8th notes
- `swing` - Jazz swing feel (default)
- `triplet` - Triplet-based phrasing
- `syncopated` - Offbeat emphasis
- `polyrhythmic` - 3/4 and 5/4 superimpositions

## API Reference

### TriadPairSoloEngine

The main interface for generating solo phrases.

```python
engine = TriadPairSoloEngine(
    key="C",              # Root key
    scale="major",        # Scale type
    progression=None,     # Optional chord progression
    triad_pair_type="diatonic",
    mode="intervallic",
    string_set="auto",    # Guitar string set
    rhythmic_style="swing",
    difficulty="intermediate",
    seed=None             # Random seed
)
```

#### Methods

**`get_triad_pairs(count, pair_type)`**
```python
pairs = engine.get_triad_pairs(count=4)
# Returns list of TriadPair objects
```

**`generate_phrase(bars, structure, triad_pairs)`**
```python
phrase = engine.generate_phrase(bars=4)
# Returns SoloPhrase object
```

**`generate_call_response(triad_pairs)`**
```python
call, response = engine.generate_call_response()
# Returns tuple of (SoloPhrase, SoloPhrase)
```

**`generate_pattern(triad_pair, pattern_type)`**
```python
from triad_pair_solo_engine.patterns import PatternType
cell = engine.generate_pattern(pair, PatternType.WAVE)
# Returns MelodicCell
```

**`analyze_voice_leading(from_pair, to_pair)`**
```python
vl = engine.analyze_voice_leading(pair1, pair2)
print(vl.narrative)
# "2 voice(s) moving stepwise; intervallic expansion"
```

**`export(phrase, output_path, formats)`**
```python
files = engine.export(phrase, "output/solo", ["json", "musicxml", "html"])
```

### TriadPair

Represents a pair of triads for intervallic soloing.

```python
from triad_pair_solo_engine import TriadPair

pair = TriadPair(
    triad_a=("C", "major"),
    triad_b=("D", "minor"),
    relationship="diatonic",
    tension_level=0.5,
    source_scale="C_major"
)

interval = pair.get_interval()  # 2 semitones (major 2nd)
```

### SoloPhrase

A complete solo phrase with notes, cells, and analysis.

```python
phrase = engine.generate_phrase(bars=4)

print(phrase.bar_count)          # 4
print(phrase.total_duration())   # Total beats
print(phrase.get_pitch_range())  # (lowest, highest)
print(phrase.notes)              # List of PatternNote
print(phrase.voice_leading_analysis)  # VL-SM results
```

### Pattern Types

```python
from triad_pair_solo_engine.patterns import PatternType

PatternType.UP_ARPEGGIO      # Ascending through both triads
PatternType.DOWN_ARPEGGIO    # Descending through both triads
PatternType.ALTERNATING      # A → B → A → B
PatternType.ROTATION_132     # 1-3-2 rotation
PatternType.ROTATION_312     # 3-1-2 rotation
PatternType.WAVE             # Directional wave pattern
PatternType.INTERVAL_SKIP    # Large intervallic leaps
PatternType.PIVOT_TONE       # Pivot note patterns
```

## Voice-Leading (VL-SM)

The engine uses the Voice-Leading Smart Module with three modes:

### Intervallic Mode
- Allows large leaps
- SISM (Sum-Interval Stability Mapping) for tension control
- Directional inversion cycling

### Functional Mode
- APVL (Axis-Preserving Voice Leading)
- TRAM (Tension/Release Alternating Motion)
- Common-tone retention

### Modal Mode
- Open, floating lines
- SISM-based spacing
- Balanced motion

## Output Formats

### JSON
```json
{
  "phrase": {
    "structure": "structured_4bar",
    "bar_count": 4,
    "rhythmic_style": "swing"
  },
  "notes": [
    {
      "pitch": 60,
      "pitch_name": "C4",
      "duration": 0.5,
      "triad_source": "A",
      "string": 3,
      "fret": 5
    }
  ],
  "triad_pairs": [...],
  "voice_leading": [...]
}
```

### MusicXML
Single melodic staff with proper key signature, time signature, and articulations.

### HTML Phrase Sheet
Beautiful, print-ready phrase sheet with:
- Key/scale metadata
- Triad pairs used
- Notation preview
- Guitar TAB
- Voice-leading analysis

## Demo Examples

Run the demo script to generate example phrases:

```bash
python examples/demo_phrases.py
```

Or programmatically:

```python
from triad_pair_solo_engine.examples.demo_phrases import generate_all_demos

demos = generate_all_demos("./output")
```

### Generated Demos

1. **Intervallic Modal** - D Dorian intervallic line with wave contour
2. **Altered Dominant** - G7alt with altered dominant triad pairs
3. **Functional ii-V-I** - C major ii-V-I with APVL + TRAM
4. **Large-Leap SISM** - Eb Lydian UST with maximum spacing

## Integration with Open Triad Engine

The Triad Pair Solo Engine calls Open Triad Engine v1.0 for:

- Triad generation and transformation
- Open-triad voicing (drop2, drop3, super_open)
- Inversion cycling (open_root, open_first, open_second)
- Voice-leading algorithms (VL-SM)
- Scale mapping

```python
# The engine internally uses:
from open_triad_engine import OpenTriadEngine

# For advanced integration:
engine = TriadPairSoloEngine(key="C", scale="dorian")
open_engine = OpenTriadEngine(...)  # Your Open Triad Engine instance

# Use Open Triad Engine's transformation
from open_triad_engine.transformations import ClosedToOpenConverter
converter = ClosedToOpenConverter()
```

## Unit Tests

Run the test suite:

```bash
cd triad_pair_solo_engine
pytest tests/ -v
```

Test coverage includes:
- Input validation
- Triad pair mapping
- Pattern generation
- Rhythmic alignment
- Voice-leading analysis
- MusicXML validity
- Full workflow integration

## Configuration Options

### SoloEngineConfig

| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `key` | str | "C" | C, C#, D, ..., B, Db, Eb, ... |
| `scale` | str | "major" | major, minor, dorian, phrygian, lydian, mixolydian, aeolian, locrian, melodic_minor, harmonic_minor, whole_tone, diminished, altered, lydian_dominant |
| `progression` | list | None | ["Dm7", "G7", "Cmaj7"] |
| `triad_pair_type` | str | "diatonic" | diatonic, klemonic, ust, altered_dominant_pairs |
| `mode` | str | "intervallic" | functional, modal, intervallic, hybrid |
| `string_set` | str | "auto" | 6-4, 5-3, 4-2, auto |
| `rhythmic_style` | str | "swing" | straight, swing, triplet, syncopated, polyrhythmic |
| `phrase_length` | int | 4 | 1-32 bars |
| `contour` | str | "wave" | ascending, descending, wave, zigzag, random_seeded |
| `difficulty` | str | "intermediate" | beginner, intermediate, advanced |
| `seed` | int | None | Any integer for reproducibility |

## Architecture

```
triad_pair_solo_engine/
├── __init__.py          # Package exports
├── inputs.py            # Configuration and validation
├── triad_pairs.py       # Triad pair selection engine
├── patterns.py          # Pattern generation
├── rhythm.py            # Rhythm engine
├── voice_leading.py     # VL-SM integration
├── phrase_assembler.py  # Phrase construction
├── output.py            # Export formatting
├── engine.py            # Main engine class
├── tests/
│   └── test_triad_pair_engine.py
├── examples/
│   └── demo_phrases.py
└── exports/             # Generated output files
```

## License

Part of the Open Triad Engine v1.0 project.

## Version

1.0.0

