# Open Triad Engine v1.0

A modular generative engine that converts closed triads into open triads, cycles inversions, performs adaptive voice-leading, maps shapes across scales or progressions, and outputs melodic/harmonic/chord-melody/counterpoint/orchestration material.

**Designed for Integration**: Installable as a standalone module but callable by other generators (EtudeGen, MAMS, TriadPair Engine, Counterpoint Companion, Quartet Engine, etc.).

## 🎹 Features

### Core Capabilities

- **Closed → Open Triad Conversion**
  - Drop-2 voicings
  - Drop-3 voicings
  - Super-open (maximum spread)

- **Inversion Engine**
  - Open root position
  - Open first inversion
  - Open second inversion
  - Directional inversion cycling

- **Scale/Key Mapping**
  - All diatonic modes
  - Melodic minor modes
  - Harmonic minor modes
  - Symmetric scales (whole-tone, diminished, augmented)
  - 50+ scales in the Tonality Vault

### Voice-Leading Smart Module (VL-SM)

Four adaptive modes with specialized algorithms:

1. **Functional Mode**
   - APVL (Axis-Preserving Voice Leading)
   - TRAM (Tension/Release Alternating Motion)
   - Common-tone retention
   - Parallel fifth/octave avoidance

2. **Modal/Modern Jazz Mode**
   - SISM (Sum-Interval Stability Mapping)
   - Intervallic freedom
   - Color-tone preservation

3. **Counterpoint Mode**
   - Independent melodic lines
   - Contrary/oblique motion preference
   - Voice crossing prevention

4. **Orchestration Mode**
   - Instrument register mapping
   - Timbral spacing optimization
   - Range constraint enforcement

### Special Use-Case Engines

- **Chord-Melody Engine**: Melody on top with open triad support
- **ii-V-I Engine**: Optimized functional progressions
- **Triad-Pair Engine**: Klemons, diatonic, and UST pairs
- **Counterpoint Companion**: Three-voice counterpoint generation
- **Orchestration Mapper**: Voice-to-instrument assignment

### Export Formats

- MusicXML (notation interchange)
- JSON (data)
- Guitar TAB
- PDF Etude Builder (HTML)

## 📦 Installation

```bash
# Clone or copy the OpenTriadEngine directory
cd OpenTriadEngine

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

## 🚀 Quick Start

### Basic Usage

```python
from open_triad_engine import OpenTriadEngine, create_engine

# Create engine with defaults
engine = OpenTriadEngine()

# Generate open triads for C major scale
result = engine.generate_scale_triads('C', 'ionian')
for triad in result.data:
    print(f"{triad.symbol}: {triad.voices}")

# Voice lead a ii-V-I progression
result = engine.voice_lead_progression(['Dm', 'G', 'C'])
for triad in result.data['triads']:
    print(f"{triad.symbol}: {triad.voices}")
```

### With Configuration

```python
from open_triad_engine import create_engine, EngineConfig

# Create engine with custom config
engine = create_engine(
    mode='chord_melody',
    priority='smooth',
    instruments={
        'top': 'violin',
        'middle': 'viola',
        'bottom': 'cello'
    }
)

# Generate ii-V-I with optimal voice leading
result = engine.generate_two_five_one('Bb')
print(f"ii: {result.ii.symbol}")
print(f"V:  {result.V.symbol}")
print(f"I:  {result.I.symbol}")
```

### Quick Functions for External Generators

```python
from open_triad_engine.engine import (
    quick_open_triads,
    quick_voice_lead,
    quick_two_five_one
)

# One-liner to get open triads
triads = quick_open_triads('G', 'dorian')

# One-liner to voice lead
voiced = quick_voice_lead(['Am', 'D', 'G', 'C'])

# One-liner for ii-V-I
two_five_one = quick_two_five_one('F')
```

## 🎼 Detailed Usage

### Creating and Transforming Triads

```python
from open_triad_engine import OpenTriadEngine

engine = OpenTriadEngine()

# Create a closed triad
triad = engine.create_triad('C', 'major', 4)

# Convert to open voicing
open_triad = engine.to_open_voicing(triad, 'drop2')

# Get all inversions
inversions = engine.get_all_inversions(triad)
# Returns: {'open_root': ..., 'open_first': ..., 'open_second': ...}
```

### Voice Leading

```python
# Voice lead between two triads
source = engine.create_triad('C', 'major')
source = engine.to_open_voicing(source, 'drop2')
target = engine.create_triad('G', 'major')

result = engine.voice_lead(source, target, mode='functional')

print(f"Score: {result.score}")
print(f"Narrative: {result.narrative}")
for motion in result.motions:
    print(f"  {motion.voice_name}: {motion.from_note} → {motion.to_note}")
```

### Chord-Melody Harmonization

```python
from open_triad_engine import Note

engine = OpenTriadEngine()

# Create a melody
melody = [Note('E', 5), Note('D', 5), Note('C', 5)]

# Harmonize with open triads (melody stays on top)
voicings = engine.create_chord_melody(melody)

for v in voicings:
    print(f"Melody: {v.melody_note}, Chord: {v.triad.symbol}")
```

### Shape Bundles for Practice

```python
result = engine.generate_scale_triads('C', 'ionian')
bundles = engine.get_shape_bundles(result.data)

for bundle in bundles:
    print(f"\n{bundle.root_triad.symbol}:")
    for name, shape in bundle.get_all_shapes().items():
        print(f"  {name}: {shape.voices}")
```

### Triad Pairs

```python
# Create Klemons-style pair (whole step apart)
pair = engine.create_triad_pair('C', 'klemons')
print(f"Triad 1: {pair.triad1.symbol}")
print(f"Triad 2: {pair.triad2.symbol}")
print(f"Combined pitches: {pair.combined_pitch_classes}")
```

### Export

```python
result = engine.generate_scale_triads('C', 'ionian')

# Export to MusicXML
path = engine.export_musicxml(result.data, 'triads.xml', title='Open Triads')

# Export to JSON
path = engine.export_json(result.data, 'triads.json')

# Export to TAB
path = engine.export_tab(result.data, 'triads.txt')

# Export complete etude
path = engine.export_etude(
    title='C Major Open Triads',
    key='C',
    triads=result.data,
    filename='etude.html'
)
```

## 📐 Architecture

```
OpenTriadEngine/
├── open_triad_engine/
│   ├── __init__.py          # Package exports
│   ├── core.py               # Note, Interval, Triad classes
│   ├── inputs.py             # EngineConfig, validation
│   ├── transformations.py    # Closed→Open, Inversions, ScaleMapper
│   ├── voice_leading.py      # VL-SM, APVL, TRAM, SISM
│   ├── output_shapes.py      # ShapeBundle, MelodicPatterns, Rhythms
│   ├── special_engines.py    # ChordMelody, ii-V-I, TriadPair, etc.
│   ├── tonality_vault.py     # Scale definitions
│   ├── exports.py            # MusicXML, PDF, TAB export
│   └── engine.py             # Main OpenTriadEngine class
├── tests/
│   ├── test_core.py
│   ├── test_transformations.py
│   ├── test_voice_leading.py
│   └── test_engine.py
├── examples/
│   └── demo_all_modes.py
└── exports/                   # Output directory
```

## 🔌 Integration API

The engine provides a clean interface for external generators:

```python
class OpenTriadEngine:
    # Core operations
    def create_triad(root, triad_type, octave) -> Triad
    def to_open_voicing(triad, voicing) -> Triad
    def get_all_inversions(triad) -> Dict[str, Triad]
    
    # Scale operations
    def generate_scale_triads(root, scale_name) -> EngineResult
    def parse_progression(chord_symbols) -> EngineResult
    
    # Voice leading
    def voice_lead(source, target, mode) -> VoiceLeadingResult
    def voice_lead_progression(symbols) -> EngineResult
    
    # Special engines
    def generate_two_five_one(key, minor) -> TwoFiveOneResult
    def create_chord_melody(melody) -> List[ChordMelodyVoicing]
    def create_triad_pair(root, pair_type) -> TriadPair
    def generate_counterpoint(triads) -> CounterpointResult
    def orchestrate(triads) -> List[OrchestrationVoicing]
    
    # Shapes and patterns
    def get_shape_bundles(triads) -> List[ShapeBundle]
    def generate_patterns(triad) -> List[MelodicPattern]
    
    # Export
    def export_musicxml(triads, filename) -> str
    def export_json(triads, filename) -> str
    def export_tab(triads, filename) -> str
    def export_etude(title, key, triads, filename) -> str
```

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_core.py -v

# Run with coverage
pytest tests/ --cov=open_triad_engine
```

## 📚 Tonality Vault Scales

The engine includes 50+ scales organized by category:

- **Diatonic**: Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian
- **Melodic Minor**: Jazz Minor, Dorian b2, Lydian Augmented, Lydian Dominant, Altered
- **Harmonic Minor**: Harmonic Minor, Phrygian Dominant, etc.
- **Symmetric**: Whole-tone, Diminished (half-whole, whole-half), Augmented
- **Pentatonic**: Major, Minor, Blues
- **Bebop**: Dominant, Major, Minor
- **Exotic**: Hirajoshi, Hungarian Minor, Persian, etc.

```python
engine = OpenTriadEngine()

# List all scales
scales = engine.list_scales()

# List by category
diatonic = engine.list_scales(category='diatonic')

# Get scale definition
scale = engine.get_scale('altered')
print(scale.intervals)  # [0, 1, 3, 4, 6, 8, 10]
```

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please read the contributing guidelines before submitting PRs.

---

**Open Triad Engine v1.0** - Part of the GCE-Jazz Project

