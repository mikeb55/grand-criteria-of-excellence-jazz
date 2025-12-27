# Quartal Engine Integration

## Overview

The Quartal Engine has been integrated into the GCE-Jazz project, allowing you to generate quartal harmony (chords built in 4ths) for 3-chorus solos.

## Location

The Quartal Engine is located at:
```
C:\Users\mike\Documents\Cursor AI Projects\gml-workspace\quartal-engine
```

## Python Integration

Two Python modules have been created to interface with the Node.js Quartal Engine:

1. **`quartal_engine_wrapper.py`** - Low-level wrapper for the Quartal Engine CLI
2. **`quartal_3chorus_generator.py`** - High-level generator for 3-chorus quartal solos

## Quick Start

### Basic Usage

```python
from quartal_engine_wrapper import QuartalEngine

# Initialize the engine
engine = QuartalEngine()

# Generate quartal harmony
xml_path = engine.generate(
    root="D",
    scale="dorian",
    bars=8,
    stack_type="3-note",  # or "4-note"
    duration="quarter"    # "half", "quarter", "eighth", "sixteenth"
)
```

### 3-Chorus Solo Generation

```python
from quartal_3chorus_generator import Quartal3ChorusGenerator

# Initialize generator
generator = Quartal3ChorusGenerator()

# Generate standard 3-chorus solo
results = generator.generate_solo(
    root="D",
    scale="dorian",
    bars_per_chorus=8,
    style="standard"  # or "intense", "lyrical", "progressive"
)

# Access results
print(f"Chorus 1: {results['chorus1']['file']}")
print(f"Chorus 2: {results['chorus2']['file']}")
print(f"Chorus 3: {results['chorus3']['file']}")
```

## Chorus Styles

### Standard (Default)
- **Chorus 1**: Half notes, 3-note quartals (establishment)
- **Chorus 2**: Quarter notes, 3-note quartals (development)
- **Chorus 3**: Eighth notes, 3-note quartals (climax)

### Intense
- **Chorus 1**: Quarter notes, 3-note quartals
- **Chorus 2**: Eighth notes, 3-note quartals
- **Chorus 3**: Sixteenth notes, 3-note quartals

### Lyrical
- **Chorus 1**: Half notes, 3-note quartals
- **Chorus 2**: Half notes, 4-note quartals (richer)
- **Chorus 3**: Quarter notes, 3-note quartals

### Progressive
- **Chorus 1**: Half notes, 3-note quartals
- **Chorus 2**: Quarter notes, 4-note quartals (add richness)
- **Chorus 3**: Eighth notes, 3-note quartals

## Multi-Scale Progressions

Generate different scales/modes for each chorus:

```python
results = generator.generate_multiscale_solo(
    segments=[
        ("D", "dorian", 8),    # Chorus 1
        ("D", "minor", 8),     # Chorus 2
        ("D", "dorian", 8)     # Chorus 3
    ],
    style="progressive"
)
```

## Integration with 3-Chorus Solo Workflow

The quartal material can be integrated into your existing 3-chorus solo generation:

1. **Generate quartal foundation** using `Quartal3ChorusGenerator`
2. **Extract top voice** (melody line) from each chorus
3. **Combine with other material** (bebop lines, triad pairs, etc.)
4. **Apply DTE evaluation** for any double-time sections
5. **Export final MusicXML** following the MusicXML Quality Gate

## Example: Complete 3-Chorus Quartal Solo

```python
from quartal_3chorus_generator import Quartal3ChorusGenerator

generator = Quartal3ChorusGenerator()

# Generate for a specific tune
solo = generator.generate_for_tune(
    tune_name="Angular Motion",
    root="Gb",
    scale="major",
    form_bars=16,
    style="standard",
    tempo=200
)

# Results include all 3 choruses
for chorus_key, data in solo['choruses'].items():
    print(f"{chorus_key}: {data['file']}")
    print(f"  Description: {data['description']}")
```

## Output Files

Generated MusicXML files are saved to:
```
C:\Users\mike\Documents\Cursor AI Projects\gml-workspace\quartal-engine\output\generated\
```

Files are automatically named with descriptive information:
- Format: `{root}-{scale}-quartal-{stackType}-{bars}bars-{timestamp}.musicxml`
- Example: `D-dorian-quartal-3note-8bars-1234567890.musicxml`

## Using the Generated Material

The generated MusicXML files contain:
- **Voice 1** (top voice) = Melody line (use this for solo material)
- **Voices 2-4** = Quartal harmony support

You can:
1. Open files in Sibelius, Finale, Guitar Pro 8, MuseScore, or Cubase
2. Extract the top voice as a melody line
3. Use the quartal harmony as chord voicings
4. Combine with other solo material

## Requirements

- Node.js (for the Quartal Engine)
- Python 3.x (for the Python wrapper)
- The `gml-workspace` repository must be cloned

## Testing

Run the test script to verify integration:

```bash
python Scripts/test_quartal_integration.py
```

## Notes

- The Quartal Engine generates **chord voicings**, not arpeggios
- All notes in a quartal stack play **simultaneously**
- The top voice (Voice 1) is designed to serve as a melody line
- Quartal harmony creates a modern, open sound perfect for jazz and fusion

## Integration with MusicXML Quality Gate

When generating 3-chorus quartal solos:
- Ensure material meets the 8/10 excellence threshold
- Use DTE-ARC framework for evaluation if double-time is present
- Follow the 3-chorus structure rules (establish → develop → peak)
- Apply proper naming conventions: `Vx.x - <Tune Name> - Quartal - <Style>.musicxml`

## Support

For issues or questions:
- Check the Quartal Engine documentation: `gml-workspace/quartal-engine/Quartal_Engine_Dummies_Guide.md`
- Review the Quartal Engine specs: `gml-workspace/quartal-engine/specs/`




