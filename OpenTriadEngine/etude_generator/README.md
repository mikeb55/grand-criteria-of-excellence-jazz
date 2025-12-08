# Etude Generator Add-on for Open Triad Engine v1.0

A generator that produces playable guitar etudes using the Open Triad Engine.

## Features

- **7 Structural Etude Templates**
  - Scalar Open-Triad Etude
  - Inversion Cycle Etude
  - Intervallic Etude
  - Position-Locked Etude
  - String-Set Etude
  - ii-V-I Etude
  - Chord-Melody Mini-Etude

- **Voice-Leading Integration**
  - APVL (Axis-Preserving Voice Leading)
  - TRAM (Tension/Release Alternating Motion)
  - SISM (Sum-Interval Stability Mapping)

- **Multiple Output Formats**
  - JSON (complete data)
  - MusicXML (notation)
  - Guitar TAB
  - HTML/PDF (print-ready)

## Quick Start

```python
from etude_generator import generate_etude, quick_etude

# Quick etude with defaults
etude = quick_etude(key='C', etude_type='melodic')
etude.print_summary()

# Export to all formats
etude.export_all('my_etude')
```

## Configuration Options

| Option | Values | Default |
|--------|--------|---------|
| `key` | C, D, E, F, G, A, B (with #/b) | 'C' |
| `scale` | ionian, dorian, phrygian, lydian, mixolydian, aeolian, locrian, melodic_minor, altered, etc. | 'ionian' |
| `etude_type` | melodic, harmonic, intervallic, chord_melody, position, string_set, ii_v_i, inversion_cycle, scalar | 'melodic' |
| `difficulty` | beginner, intermediate, advanced | 'intermediate' |
| `string_set` | "6-4", "5-3", "4-2", "auto" | 'auto' |
| `mode` | functional, modal, intervallic | 'functional' |
| `rhythmic_style` | straight, syncopated, triplet, polyrhythmic, swing | 'straight' |
| `tempo` | 40-180 BPM | 100 |
| `length` | 1-32 bars | 8 |

## Etude Types

### 1. Scalar Open-Triad Etude
Runs through all scale degrees with open triad voicings.
```python
etude = generate_etude(key='G', scale='ionian', etude_type='scalar')
```

### 2. Inversion Cycle Etude
Cycles through all three inversions: root → 1st → 2nd.
```python
etude = generate_etude(key='D', etude_type='inversion_cycle')
```

### 3. Intervallic Etude
Wide-interval lines using triad pairs for modern sound.
```python
etude = generate_etude(key='A', scale='lydian', etude_type='intervallic')
```

### 4. Position-Locked Etude
All notes stay within one fretboard position.
```python
etude = generate_etude(key='C', etude_type='position', position=5)
```

### 5. String-Set Etude
All voicings use a specific string grouping.
```python
etude = generate_etude(key='E', etude_type='string_set', string_set='5-3')
```

### 6. ii-V-I Etude
Functional voice-leading with APVL + TRAM.
```python
etude = generate_etude(key='Bb', etude_type='ii_v_i', mode='functional')
```

### 7. Chord-Melody Mini-Etude
Melody on top with open triad support underneath.
```python
etude = generate_etude(key='F', etude_type='chord_melody', string_set='4-2')
```

## Export Formats

```python
# Export individually
etude.export_json('my_etude.json')
etude.export_tab('my_etude.tab.txt')
etude.export_musicxml('my_etude.musicxml')
etude.export_pdf('my_etude.html')

# Export all at once
etude.export_all('my_etude')  # Creates .json, .tab.txt, .musicxml, .html
```

## Difficulty Levels

| Difficulty | Max Tempo | Max Bars | Allowed Rhythms |
|------------|-----------|----------|-----------------|
| Beginner | 80 BPM | 8 | straight |
| Intermediate | 120 BPM | 16 | straight, syncopated, triplet |
| Advanced | 180 BPM | 32 | all |

## Integration with Open Triad Engine

The Etude Generator uses these Open Triad Engine modules:

- **Transformations**: closed→open conversion, inversions
- **Voice-Leading (VL-SM)**: functional, modal, intervallic modes
- **Patterns**: arpeggios, rotations, skips, waves
- **Special Engines**: ii-V-I, chord-melody, triad-pair

## Running the Demo

```bash
cd OpenTriadEngine/etude_generator/examples
python demo_etudes.py
```

This generates 4 demonstration etudes:
1. D Dorian Modal Melodic Etude
2. G Lydian Intervallic Triad-Pair Etude
3. Bb ii-V-I Functional Voice-Leading Etude
4. C Major Chord-Melody Miniature

## Running Tests

```bash
cd OpenTriadEngine/etude_generator
pytest tests/ -v
```

## File Structure

```
etude_generator/
├── __init__.py          # Package exports
├── inputs.py            # EtudeConfig, validation
├── harmonic.py          # HarmonicGenerator using OTE
├── patterns.py          # PatternStitcher
├── rhythm.py            # RhythmGenerator
├── templates.py         # 7 etude templates
├── output.py            # Export formats
├── generator.py         # Main EtudeGenerator
├── tests/
│   └── test_etude_generator.py
├── examples/
│   ├── demo_etudes.py
│   └── output/          # Generated demo files
└── README.md
```

## API Reference

### EtudeGenerator

```python
class EtudeGenerator:
    def __init__(self, config: EtudeConfig)
    def generate(self) -> GeneratedEtude
    
    @classmethod
    def quick_generate(cls, key, scale, etude_type, difficulty, length) -> GeneratedEtude
```

### GeneratedEtude

```python
class GeneratedEtude:
    config: EtudeConfig
    phrases: List[EtudePhrase]
    harmonic_material: HarmonicMaterial
    
    # Properties
    title: str
    description: str
    total_bars: int
    total_notes: int
    
    # Methods
    def export_json(filename) -> str
    def export_tab(filename) -> str
    def export_musicxml(filename) -> str
    def export_pdf(filename) -> str
    def export_all(base_filename) -> Dict[str, str]
    def print_summary()
    def to_dict() -> Dict
```

### Convenience Functions

```python
def generate_etude(**kwargs) -> GeneratedEtude
def quick_etude(key, etude_type, difficulty) -> GeneratedEtude
def list_etude_types() -> List[str]
def list_templates() -> Dict[str, str]
```

---

**Etude Generator v1.0** — Add-on for Open Triad Engine

