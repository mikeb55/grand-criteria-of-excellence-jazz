# Open Triad Engine v1.0
## Complete Instruction Manual

---

# Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Quick Start](#3-quick-start)
4. [Core Concepts](#4-core-concepts)
5. [Creating Triads](#5-creating-triads)
6. [Open Voicing Transformations](#6-open-voicing-transformations)
7. [Inversions](#7-inversions)
8. [Scale Mapping](#8-scale-mapping)
9. [Voice Leading](#9-voice-leading)
10. [Shape Bundles & Patterns](#10-shape-bundles--patterns)
11. [Special Engines](#11-special-engines)
12. [Export Functions](#12-export-functions)
13. [Integration with Other Generators](#13-integration-with-other-generators)
14. [Complete API Reference](#14-complete-api-reference)
15. [Troubleshooting](#15-troubleshooting)

---

# 1. Introduction

The **Open Triad Engine** is a modular generative engine that:

- Converts closed triads into open triads (drop-2, drop-3, super-open)
- Cycles through inversions intelligently
- Performs adaptive voice-leading with 4 specialized modes
- Maps shapes across scales and progressions
- Outputs melodic, harmonic, chord-melody, counterpoint, and orchestration material

**Designed for Integration**: The engine is a standalone module that can be called by other generators like EtudeGen, MAMS, TriadPair Engine, Counterpoint Companion, and Quartet Engine.

---

# 2. Installation

## 2.1 Location

The engine is installed at:
```
C:\Users\mike\Documents\Cursor AI Projects\GCE-Jazz\OpenTriadEngine\
```

## 2.2 Requirements

The engine uses only Python standard library - no external dependencies required.

For testing (optional):
```bash
pip install pytest pytest-cov
```

## 2.3 Verify Installation

```python
cd OpenTriadEngine
python -c "from open_triad_engine import OpenTriadEngine; print('Engine loaded successfully!')"
```

---

# 3. Quick Start

## 3.1 Basic Import

```python
from open_triad_engine import OpenTriadEngine, create_engine, Note, Triad
```

## 3.2 Create an Engine

```python
# Method 1: Default configuration
engine = OpenTriadEngine()

# Method 2: With custom configuration
engine = create_engine(
    mode='melodic',
    priority='smooth',
    triad_type='major'
)
```

## 3.3 Your First Open Triads

```python
engine = OpenTriadEngine()

# Generate open triads for C major scale
result = engine.generate_scale_triads('C', 'ionian')

# Print the results
for triad in result.data:
    voices = [str(v) for v in triad.voices]
    print(f"{triad.symbol}: {voices}")
```

**Output:**
```
C: ['C4', 'E4', 'G5']
Dm: ['D4', 'F4', 'A5']
Em: ['E4', 'G4', 'B5']
F: ['F4', 'A4', 'C6']
G: ['G4', 'B4', 'D6']
Am: ['A4', 'C5', 'E6']
Bdim: ['B4', 'D5', 'F6']
```

---

# 4. Core Concepts

## 4.1 What is an Open Triad?

A **closed triad** has all three notes within one octave:
- C major closed: C4 - E4 - G4 (spans 7 semitones)

An **open triad** spreads the notes across a wider range:
- C major open (drop-2): C4 - E4 - G5 (spans 19 semitones)

## 4.2 Why Open Triads?

| Benefit | Description |
|---------|-------------|
| **Clarity** | Each voice is more distinct |
| **Range** | Better for ensemble writing |
| **Voice Leading** | Smoother connections between chords |
| **Modern Sound** | Used extensively in jazz and contemporary music |

## 4.3 The Note Class

```python
from open_triad_engine import Note

# Create a note
note = Note('C', 4)  # Middle C

# Properties
print(note.name)        # 'C'
print(note.octave)      # 4
print(note.midi_number) # 60
print(note.pitch_class) # 0

# Transpose
g4 = note.transpose(7)  # G4 (up a fifth)
print(g4)  # 'G4'
```

## 4.4 The Triad Class

```python
from open_triad_engine import Triad, Note, TriadType

# Create a triad
triad = Triad(
    root=Note('C', 4),
    triad_type=TriadType.MAJOR
)

# Properties
print(triad.symbol)      # 'C'
print(triad.voices)      # [Note C4, Note E4, Note G4]
print(triad.bass_note)   # C4
print(triad.top_note)    # G4
print(triad.is_open)     # False (closed position)
```

---

# 5. Creating Triads

## 5.1 Using the Engine

```python
engine = OpenTriadEngine()

# Create individual triads
c_major = engine.create_triad('C', 'major', 4)
d_minor = engine.create_triad('D', 'minor', 4)
f_sharp_dim = engine.create_triad('F#', 'dim', 4)
g_aug = engine.create_triad('G', 'aug', 4)
a_sus4 = engine.create_triad('A', 'sus4', 4)
```

## 5.2 Triad Types

| Type | Symbol | Intervals | Example |
|------|--------|-----------|---------|
| Major | `'major'` | R, M3, P5 | C-E-G |
| Minor | `'minor'` | R, m3, P5 | C-Eb-G |
| Diminished | `'dim'` | R, m3, d5 | C-Eb-Gb |
| Augmented | `'aug'` | R, M3, A5 | C-E-G# |
| Sus2 | `'sus2'` | R, M2, P5 | C-D-G |
| Sus4 | `'sus4'` | R, P4, P5 | C-F-G |

## 5.3 From Chord Symbols

```python
from open_triad_engine import Triad

# Parse chord symbols directly
c_major = Triad.from_symbol('C')
d_minor = Triad.from_symbol('Dm')
f_sharp_dim = Triad.from_symbol('F#dim')
bb_aug = Triad.from_symbol('Bbaug')
```

---

# 6. Open Voicing Transformations

## 6.1 Drop-2 Voicing

Takes the second voice from the top and drops it down an octave.

```python
engine = OpenTriadEngine()

# Create closed triad
closed = engine.create_triad('C', 'major', 4)
print(f"Closed: {[str(v) for v in closed.voices]}")
# Closed: ['C4', 'E4', 'G4']

# Convert to drop-2
drop2 = engine.to_open_voicing(closed, 'drop2')
print(f"Drop-2: {[str(v) for v in drop2.voices]}")
# Drop-2: ['E3', 'C4', 'G4']
```

## 6.2 Drop-3 Voicing

Takes the third voice from the top (bass) and drops it down an octave.

```python
drop3 = engine.to_open_voicing(closed, 'drop3')
print(f"Drop-3: {[str(v) for v in drop3.voices]}")
# Drop-3: ['C3', 'E4', 'G4']
```

## 6.3 Super-Open Voicing

Maximum spread - raises top voice and lowers bottom voice.

```python
super_open = engine.to_open_voicing(closed, 'super_open')
print(f"Super-Open: {[str(v) for v in super_open.voices]}")
# Super-Open: ['C3', 'E4', 'G5']
```

## 6.4 Comparison

| Voicing | Notes | Outer Interval |
|---------|-------|----------------|
| Closed | C4-E4-G4 | 7 semitones |
| Drop-2 | E3-C4-G4 | 15 semitones |
| Drop-3 | C3-E4-G4 | 19 semitones |
| Super-Open | C3-E4-G5 | 31 semitones |

---

# 7. Inversions

## 7.1 Get All Inversions

```python
engine = OpenTriadEngine()
triad = engine.create_triad('C', 'major', 4)

inversions = engine.get_all_inversions(triad)

print("Root position:", [str(v) for v in inversions['open_root'].voices])
print("1st inversion:", [str(v) for v in inversions['open_first'].voices])
print("2nd inversion:", [str(v) for v in inversions['open_second'].voices])
```

**Output:**
```
Root position: ['C4', 'E4', 'G5']
1st inversion: ['E3', 'G4', 'C5']
2nd inversion: ['G3', 'C4', 'E5']
```

## 7.2 Inversion Cycling

The engine supports directional inversion cycling for melodic patterns:

```python
from open_triad_engine.transformations import InversionEngine

triad = engine.create_triad('D', 'minor', 4)

# Ascending cycle: 1st → 2nd → root
ascending = InversionEngine.cycle_inversions(triad, ascending=True)

# Descending cycle: root → 2nd → 1st
descending = InversionEngine.cycle_inversions(triad, ascending=False)
```

---

# 8. Scale Mapping

## 8.1 Generate Triads for a Scale

```python
engine = OpenTriadEngine()

# C Ionian (Major)
c_major = engine.generate_scale_triads('C', 'ionian')

# D Dorian
d_dorian = engine.generate_scale_triads('D', 'dorian')

# F Lydian
f_lydian = engine.generate_scale_triads('F', 'lydian')

# A Melodic Minor
a_mel_minor = engine.generate_scale_triads('A', 'melodic_minor')
```

## 8.2 Available Scales (50+)

### Diatonic Modes
- `ionian`, `dorian`, `phrygian`, `lydian`, `mixolydian`, `aeolian`, `locrian`

### Melodic Minor Modes
- `melodic_minor`, `dorian_b2`, `lydian_augmented`, `lydian_dominant`
- `mixolydian_b6`, `locrian_nat2`, `altered`

### Harmonic Minor Modes
- `harmonic_minor`, `phrygian_dominant`, `lydian_sharp2`

### Symmetric Scales
- `whole_tone`, `half_whole`, `whole_half`, `augmented`

### Pentatonic & Blues
- `major_pentatonic`, `minor_pentatonic`, `blues`

### Bebop Scales
- `bebop_dominant`, `bebop_major`, `bebop_minor`

### Exotic Scales
- `hirajoshi`, `hungarian_minor`, `persian`, `double_harmonic`

## 8.3 List All Scales

```python
# All scales
all_scales = engine.list_scales()

# By category
diatonic = engine.list_scales(category='diatonic')
melodic_minor = engine.list_scales(category='melodic_minor')
symmetric = engine.list_scales(category='symmetric')

# Get scale details
altered = engine.get_scale('altered')
print(f"Altered scale intervals: {altered.intervals}")
# [0, 1, 3, 4, 6, 8, 10]
```

---

# 9. Voice Leading

## 9.1 The Voice-Leading Smart Module (VL-SM)

The engine includes 4 voice-leading modes:

| Mode | Best For |
|------|----------|
| **Functional** | Traditional harmony, ii-V-I progressions |
| **Modal** | Modern jazz, intervallic freedom |
| **Counterpoint** | Independent melodic lines |
| **Orchestration** | Ensemble writing with register constraints |

## 9.2 Basic Voice Leading

```python
engine = OpenTriadEngine()

# Create source and target triads
source = engine.create_triad('C', 'major', 4)
source = engine.to_open_voicing(source, 'drop2')

target = engine.create_triad('G', 'major', 4)

# Voice lead between them
result = engine.voice_lead(source, target, mode='functional')

print(f"Source: {source.symbol} {[str(v) for v in source.voices]}")
print(f"Target: {result.target.symbol} {[str(v) for v in result.target.voices]}")
print(f"Score: {result.score}")
print(f"Narrative: {result.narrative}")
```

## 9.3 Voice Lead a Progression

```python
# ii-V-I in C
result = engine.voice_lead_progression(['Dm', 'G', 'C'])

print("Voice-led progression:")
for triad in result.data['triads']:
    print(f"  {triad.symbol}: {[str(v) for v in triad.voices]}")

print("\nVoice leading analysis:")
for vl in result.data['voice_leading']:
    print(f"  {vl.source.symbol} → {vl.target.symbol}")
    for motion in vl.motions:
        print(f"    {motion.voice_name}: {motion.from_note} → {motion.to_note} ({motion.motion_type})")
```

## 9.4 Functional Mode Features

- **APVL (Axis-Preserving Voice Leading)**: Maintains common tones as pivot points
- **TRAM (Tension/Release Alternating Motion)**: Alternates between tense and relaxed motion
- **Parallel 5th/8ve avoidance**: Optional classical voice-leading rules

```python
engine = create_engine(
    mode='harmonic',
    priority='smooth',
    allow_parallel_fifths=False,
    allow_parallel_octaves=False,
    prefer_contrary_motion=True
)
```

## 9.5 Modal Mode Features

- **SISM (Sum-Interval Stability Mapping)**: Measures voicing color
- **Intervallic freedom**: Allows wider leaps for modern sound

```python
result = engine.voice_lead(source, target, mode='modal')
```

## 9.6 Counterpoint Mode Features

- Independent melodic lines
- Contrary/oblique motion preferred
- Prevents voice crossing

```python
result = engine.voice_lead(source, target, mode='counterpoint')
```

## 9.7 Orchestration Mode Features

- Assigns voices to instruments
- Enforces register constraints
- Optimizes for timbral clarity

```python
engine = create_engine(
    mode='orchestration',
    instruments={
        'top': 'violin',
        'middle': 'viola',
        'bottom': 'cello'
    }
)
```

---

# 10. Shape Bundles & Patterns

## 10.1 Shape Bundles

A shape bundle contains all open inversions for a chord:

```python
result = engine.generate_scale_triads('G', 'ionian')
bundles = engine.get_shape_bundles(result.data)

for bundle in bundles[:3]:  # First 3 chords
    print(f"\n{bundle.root_triad.symbol}:")
    for name, shape in bundle.get_all_shapes().items():
        print(f"  {name}: {[str(v) for v in shape.voices]}")
    print(f"  Contour: {bundle.root_contour.type.value}")
```

## 10.2 Melodic Patterns

Generate practice patterns from a triad:

```python
triad = engine.create_triad('C', 'major', 4)
patterns = engine.generate_patterns(triad)

for pattern in patterns[:5]:
    notes = [str(n) for n in pattern.notes]
    print(f"{pattern.pattern_type}: {notes}")
```

**Output:**
```
arpeggio_up: ['C4', 'E4', 'G4']
arpeggio_down: ['G4', 'E4', 'C4']
arpeggio_up_down: ['C4', 'E4', 'G4', 'E4', 'C4']
rotation_1-3-2: ['C4', 'G4', 'E4']
wave: ['C4', 'G4', 'E4', 'C5', 'G4', 'E4']
```

## 10.3 Pattern Types

| Pattern | Description |
|---------|-------------|
| `arpeggio_up` | Low to high |
| `arpeggio_down` | High to low |
| `arpeggio_up_down` | Up then down |
| `arpeggio_down_up` | Down then up |
| `rotation_1-3-2` | Root, 5th, 3rd |
| `rotation_3-1-2` | 5th, root, 3rd |
| `wave` | Alternating extremes |
| `pendulum` | Low-high-low-mid pattern |
| `skip_2` | Intervallic skips |

---

# 11. Special Engines

## 11.1 ii-V-I Engine

Generates optimally voice-led ii-V-I progressions:

```python
# Major ii-V-I in C
result = engine.generate_two_five_one('C')
print(f"ii:  {result.ii.symbol} {[str(v) for v in result.ii.voices]}")
print(f"V:   {result.V.symbol} {[str(v) for v in result.V.voices]}")
print(f"I:   {result.I.symbol} {[str(v) for v in result.I.voices]}")

# Minor ii-V-i in A
result_minor = engine.generate_two_five_one('A', minor=True)
```

**Example Output:**
```
ii:  Dm ['D4', 'F4', 'A5']
V:   G ['B3', 'D4', 'G5']
I:   C ['C4', 'E4', 'G5']
```

## 11.2 Chord-Melody Engine

Creates chord-melody voicings with melody on top:

```python
# Create a melody
melody = [
    Note('E', 5), Note('D', 5), Note('C', 5), Note('D', 5),
    Note('E', 5), Note('E', 5), Note('E', 5)
]

# Harmonize it
voicings = engine.create_chord_melody(melody)

for v in voicings:
    print(f"Melody: {v.melody_note}, Chord: {v.triad.symbol}")
    print(f"  Full voicing: {[str(n) for n in v.full_voicing]}")
```

## 11.3 Triad-Pair Engine

For jazz improvisation using triad pairs:

```python
# Klemons pair (whole step apart)
pair = engine.create_triad_pair('C', 'klemons')
print(f"Pair: {pair.triad1.symbol} + {pair.triad2.symbol}")
print(f"Combined pitch classes: {pair.combined_pitch_classes}")
```

**Output:**
```
Pair: C + D
Combined pitch classes: {0, 2, 4, 6, 7, 9}
```

## 11.4 Counterpoint Companion

Generates three independent voice lines:

```python
triads = [
    engine.create_triad('C', 'major'),
    engine.create_triad('Am', 'minor'),
    engine.create_triad('F', 'major'),
    engine.create_triad('G', 'major'),
]

result = engine.generate_counterpoint(triads)

print("Soprano:", [str(n) for n in result.soprano.notes])
print("Alto:   ", [str(n) for n in result.alto.notes])
print("Bass:   ", [str(n) for n in result.bass.notes])
```

## 11.5 Orchestration Mapper

Assigns voices to instruments:

```python
triads = engine.generate_scale_triads('D', 'dorian').data
orchestrations = engine.orchestrate(triads)

for orch in orchestrations[:3]:
    print(f"\n{orch.triad.symbol}:")
    for pos, instrument in orch.assignments.items():
        info = orch.register_info[pos]
        print(f"  {pos}: {instrument} ({info['note']})")
```

---

# 12. Export Functions

## 12.1 Export to MusicXML

For notation software (Sibelius, Finale, MuseScore):

```python
triads = engine.generate_scale_triads('C', 'ionian').data
path = engine.export_musicxml(
    triads, 
    'c_major_open_triads.xml',
    title='C Major Open Triads'
)
print(f"Saved to: {path}")
```

## 12.2 Export to JSON

For data interchange:

```python
path = engine.export_json(triads, 'triads.json')
```

## 12.3 Export to Guitar TAB

```python
path = engine.export_tab(triads, 'triads_tab.txt')
```

**Example TAB output:**
```
====================================================
OPEN TRIAD TABLATURE
====================================================

    C       Dm      Em      F       G  
e|-------|-------|-------|-------|-------|
B|-12----|-------|-------|-------|-------|
G|-------|-------|-------|-------|-------|
D|--9----|--10---|--12---|--14---|--16---|
A|-------|-------|-------|-------|-------|
E|--8----|--10---|--12---|--13---|--15---|
```

## 12.4 Export HTML Etude

Print-ready practice sheet:

```python
path = engine.export_etude(
    title='C Major Open Triad Study',
    key='C Major',
    triads=triads,
    filename='c_major_etude.html',
    include_patterns=True
)
```

---

# 13. Integration with Other Generators

## 13.1 Quick Functions

For easy integration with external generators:

```python
from open_triad_engine.engine import (
    quick_open_triads,
    quick_voice_lead,
    quick_two_five_one
)

# One-liner: Open triads for a scale
triads = quick_open_triads('G', 'dorian')

# One-liner: Voice lead a progression
voiced = quick_voice_lead(['Am7', 'D7', 'Gmaj7', 'Cmaj7'])

# One-liner: ii-V-I
two_five_one = quick_two_five_one('Bb')
```

## 13.2 Engine Interface

The main interface for integration:

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

---

# 14. Complete API Reference

## 14.1 EngineConfig Options

| Option | Type | Values | Default |
|--------|------|--------|---------|
| `triad_type` | str | major, minor, dim, aug, sus, sus2, sus4 | 'major' |
| `source` | str | diatonic, chromatic, progression, user_defined, tonality_vault | 'diatonic' |
| `string_set` | str | '6-4', '5-3', '4-2', 'auto' | 'auto' |
| `mode` | str | melodic, harmonic, chord_melody, counterpoint, orchestration | 'melodic' |
| `priority` | str | smooth, intervallic, mixed | 'smooth' |
| `scale_map` | List[str] | Scale names | ['ionian'] |
| `register_limits` | Dict | {'low': int, 'high': int} | {'low': 36, 'high': 84} |
| `allow_parallel_fifths` | bool | True/False | False |
| `allow_parallel_octaves` | bool | True/False | False |
| `prefer_contrary_motion` | bool | True/False | True |
| `max_voice_leap` | int | Semitones | 12 |
| `instruments` | Dict | Voice → instrument mapping | violin/viola/cello |

## 14.2 Note Class

```python
Note(name: str, octave: int = 4)

Properties:
  .name          # 'C', 'F#', 'Bb'
  .octave        # 0-9
  .pitch_class   # 0-11
  .midi_number   # 0-127
  .frequency     # Hz

Methods:
  .transpose(semitones) -> Note
  .interval_to(other) -> int
  
Class Methods:
  Note.from_midi(midi_number) -> Note
  Note.from_string('C4') -> Note
```

## 14.3 Triad Class

```python
Triad(root: Note, triad_type: TriadType, inversion: Inversion = ROOT)

Properties:
  .root          # Root Note
  .triad_type    # TriadType enum
  .inversion     # Inversion enum
  .voicing_type  # VoicingType enum
  .voices        # List[Note]
  .symbol        # 'C', 'Dm', 'F#dim'
  .bass_note     # Lowest Note
  .top_note      # Highest Note
  .is_open       # bool
  .intervals     # List[int]
  .contour       # str

Methods:
  .transpose(semitones) -> Triad
  .copy() -> Triad
  .to_dict() -> Dict

Class Methods:
  Triad.from_symbol('Dm') -> Triad
```

---

# 15. Troubleshooting

## 15.1 Import Errors

**Problem**: `ModuleNotFoundError: No module named 'open_triad_engine'`

**Solution**: Make sure you're in the correct directory:
```python
import sys
sys.path.insert(0, 'C:/Users/mike/Documents/Cursor AI Projects/GCE-Jazz/OpenTriadEngine')
from open_triad_engine import OpenTriadEngine
```

## 15.2 Invalid Triad Type

**Problem**: `Warning: Invalid triad_type 'maj7', falling back to 'major'`

**Solution**: The engine handles triads (3 notes), not 7th chords. Use:
- `'major'`, `'minor'`, `'dim'`, `'aug'`, `'sus2'`, `'sus4'`

## 15.3 Note Out of Range

**Problem**: Orchestration shows ⚠ warning

**Solution**: Adjust register limits or let the engine auto-select inversions:
```python
engine = create_engine(
    register_limits={'low': 48, 'high': 96}  # Adjust range
)
```

## 15.4 Running Tests

```bash
cd OpenTriadEngine
pytest tests/ -v
```

---

# Appendix A: Example Progressions

## Jazz Standards

```python
# Autumn Leaves
autumn_leaves = ['Am7', 'D7', 'Gmaj7', 'Cmaj7', 'F#m7b5', 'B7', 'Em']

# All The Things You Are
attya = ['Fm7', 'Bbm7', 'Eb7', 'Abmaj7', 'Dbmaj7', 'G7', 'Cmaj7']

# Giant Steps
giant_steps = ['Bmaj7', 'D7', 'Gmaj7', 'Bb7', 'Ebmaj7', 'Am7', 'D7', 'Gmaj7']
```

## Modal Progressions

```python
# So What (D Dorian)
so_what = engine.generate_scale_triads('D', 'dorian')

# Maiden Voyage (D Mixolydian)
maiden = engine.generate_scale_triads('D', 'mixolydian')
```

---

# Appendix B: Keyboard Shortcuts

When using the demo:

| Action | Command |
|--------|---------|
| Run demo | `python examples/demo_all_modes.py` |
| Run tests | `pytest tests/ -v` |
| Quick triads | `quick_open_triads('C', 'ionian')` |
| Quick ii-V-I | `quick_two_five_one('Bb')` |

---

**Open Triad Engine v1.0** — Part of the GCE-Jazz Project

*Manual Version 1.0 — Generated 2024*

