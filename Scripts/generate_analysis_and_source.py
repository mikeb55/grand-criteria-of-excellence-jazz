"""
Generate Analysis and Source files for Orbit and Crystal Silence
================================================================

Creates:
- Analysis/ folder: Harmonic analysis, voice leading guides, form maps
- Source/ folder: Master MusicXML files, part extractions
"""

import os
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ============================================================================
# CONSTANTS
# ============================================================================

NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7,
    "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# ============================================================================
# ANALYSIS CONTENT
# ============================================================================

ORBIT_ANALYSIS = """# Orbit — Harmonic Analysis

## Overview
**Style:** Wayne Shorter (Post-1965 Avant-Garde)  
**Key:** F Major (Lydian-dominant)  
**Tempo:** 160 BPM  
**Time:** 3/4 (Waltz)  
**Form:** 16 bars, through-composed

---

## Chord Progression

```
Section A (bars 1-8):
| Fmaj7#11 | Ebmaj7#5 | Dbmaj7   | Bmaj7    |
| Bbm9     | Abmaj7   | Gbmaj7   | Emaj7    |

Section B (bars 9-16):
| Fmaj7#11 | Dbmaj7   | Amaj7    | Gmaj7    |
| Fmaj7#11 | Ebm9     | Dbmaj7   | Fmaj7    |
```

---

## Roman Numeral Analysis

| Bar | Chord | Roman | Function |
|-----|-------|-------|----------|
| 1 | Fmaj7#11 | I | Tonic (Lydian) |
| 2 | Ebmaj7#5 | bVII | Chromatic neighbor |
| 3 | Dbmaj7 | bVI | Chromatic descent |
| 4 | Bmaj7 | #IV | Tritone substitute area |
| 5 | Bbm9 | iv | Subdominant minor |
| 6 | Abmaj7 | bIII | Mediant |
| 7 | Gbmaj7 | bII | Neapolitan area |
| 8 | Emaj7 | VII | Leading tone major |
| 9 | Fmaj7#11 | I | Return home |
| 10 | Dbmaj7 | bVI | Distant color |
| 11 | Amaj7 | III | Mediant major |
| 12 | Gmaj7 | II | Supertonic major |
| 13 | Fmaj7#11 | I | Home |
| 14 | Ebm9 | bvii | Minor contrast |
| 15 | Dbmaj7 | bVI | Penultimate |
| 16 | Fmaj7 | I | Final resolution |

---

## Root Motion Analysis

### Bars 1-4: Chromatic Descent
```
F → Eb → Db → B
  ↓    ↓    ↓
 -2   -2   -2 (semitones)
```
This creates a **falling chromatic line** that destabilizes tonal center.

### Bars 5-8: Continued Descent
```
Bb → Ab → Gb → E
  ↓    ↓    ↓
 -2   -2   -3
```
The descent continues with a slightly larger drop at the end.

### Bars 9-12: Wide Intervals
```
F → Db → A → G
  ↓    ↓   ↓
 -4   -4  -2
```
Wider leaps create more tension before resolution.

---

## Scale Palette

| Chord | Scale | Color Tones |
|-------|-------|-------------|
| Fmaj7#11 | F Lydian | B (♯11) |
| Ebmaj7#5 | Eb Lydian Augmented | A (♯11), B (♯5) |
| Dbmaj7 | Db Lydian | G (♯11) |
| Bmaj7 | B Lydian | E♯/F (♯11) |
| Bbm9 | Bb Dorian | G (nat 6), C (9) |
| Abmaj7 | Ab Lydian | D (♯11) |
| Gbmaj7 | Gb Lydian | C (♯11) |
| Emaj7 | E Lydian | A♯ (♯11) |

---

## Non-Functional Characteristics

1. **No V-I cadences** — The harmony never resolves functionally
2. **Chromatic root motion** — Roots move by half-step, not by fifth
3. **Major 7th predominance** — Almost all chords are maj7 variants
4. **Lydian as default** — The ♯11 creates floating, unresolved quality
5. **Color over function** — Chords relate by sound color, not tension-release

---

## Wayne Shorter Influence

This progression emulates Shorter's approach from albums like:
- *Speak No Evil* (1964)
- *JuJu* (1964)
- *Nefertiti* (1967)

Key Shorter characteristics present:
- Through-composed form
- Modal interchange without functional resolution
- Mysterious, floating quality
- Wide dynamic range implied by sparse texture

---

## Triad Pairs for Improvisation

| Over Chord | Triad Pair | Resulting Sound |
|------------|-----------|-----------------|
| Fmaj7#11 | F + G | Full Lydian color |
| Ebmaj7#5 | Eb aug + Bb | Augmented Lydian |
| Dbmaj7 | Db + Eb | Lydian 9 + ♯11 |
| Bbm9 | Db + Ab | Minor 9 sound |

---

## Performance Notes

- **Tempo feel:** Light waltz, not heavy downbeats
- **Dynamics:** Float between p and mp
- **Phrasing:** Let phrases span across bar lines
- **Sustain:** Let notes ring their full value
- **Space:** Silence is part of the composition
"""

ORBIT_VOICE_LEADING = """# Orbit — Voice Leading Guide

## Guide Tone Lines

### Line 1: 3rds of each chord
```
Bar:  1    2    3    4    5    6    7    8
Tone: A    G    F    D#   Db   C    Bb   G#
      ↓    ↓    ↓    ↓    ↓    ↓    ↓
     -2   -2   -2   -1   -1   -2   -2 (semitones)
```

### Line 2: 7ths of each chord
```
Bar:  1    2    3    4    5    6    7    8
Tone: E    D    C    A#   Ab   G    F    D#
      ↓    ↓    ↓    ↓    ↓    ↓    ↓
     -2   -2   -2   -1   -1   -2   -2
```

---

## Common Tones Between Adjacent Chords

| Bars | Chords | Common Tones |
|------|--------|--------------|
| 1→2 | Fmaj7#11 → Ebmaj7#5 | G (9th/3rd) |
| 2→3 | Ebmaj7#5 → Dbmaj7 | Ab (♯5/5th) |
| 3→4 | Dbmaj7 → Bmaj7 | F (3rd/♯11) |
| 4→5 | Bmaj7 → Bbm9 | F (♯11/5th) |
| 5→6 | Bbm9 → Abmaj7 | Ab (b7/root), Eb (11/5) |
| 6→7 | Abmaj7 → Gbmaj7 | Eb (5th/6th) |
| 7→8 | Gbmaj7 → Emaj7 | None (distant) |

---

## Smooth Voice Leading Paths

### Upper Voice (melody range)
```
F5 → Eb5 → Db5 → B4 → Bb4 → Ab4 → Gb4 → E4
 ↘    ↘    ↘    ↘    ↘    ↘    ↘
  chromatic descent through the form
```

### Inner Voice
```
A4 → G4 → F4 → D#4 → Db4 → C4 → Bb3 → G#3
 ↘    ↘    ↘    ↘    ↘    ↘    ↘
  parallel 3rds below melody
```

---

## Chord Voicing Suggestions

### Quartal Voicings (Shorter-style)
```
Fmaj7#11:  x-x-3-4-5-5  (C-F-B-E stacked 4ths)
Ebmaj7#5:  x-6-5-4-4-x  (Eb-G-B-D)
Dbmaj7:    x-4-5-5-6-x  (Db-F-Ab-C)
```

### Drop-2 Voicings
```
Fmaj7:   1-x-2-2-1-x
Ebmaj7:  x-6-5-3-4-x
Dbmaj7:  x-4-3-1-2-x
```

---

## Contrary Motion Opportunities

| Bars | Upper Voice | Lower Voice | Motion |
|------|------------|-------------|--------|
| 1-4 | Descending | Ascending | Contrary |
| 5-8 | Descending | Stationary | Oblique |
| 9-12 | Ascending | Descending | Contrary |
| 13-16 | Descending | Ascending | Contrary |
"""

ORBIT_FORM_MAP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Orbit - Form Map</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #fff; color: #333; padding: 40px; max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; color: #1a1a2e; border-bottom: 3px solid #333; padding-bottom: 10px; }
        .form-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 30px 0; }
        .bar { background: #f5f5f5; border: 2px solid #333; border-radius: 8px; padding: 15px; text-align: center; }
        .bar-num { font-size: 0.8em; color: #666; }
        .chord { font-size: 1.2em; font-weight: bold; margin: 10px 0; }
        .scale { font-size: 0.9em; color: #555; }
        .section-a { background: #e3f2fd; }
        .section-b { background: #fff3e0; }
        .home { background: #c8e6c9; border-color: #2e7d32; }
        .legend { display: flex; justify-content: center; gap: 30px; margin: 20px 0; }
        .legend-item { display: flex; align-items: center; gap: 8px; }
        .legend-box { width: 20px; height: 20px; border: 1px solid #333; border-radius: 4px; }
        .info { background: #fafafa; padding: 20px; border: 1px solid #ddd; margin-top: 30px; }
        @media print { body { padding: 20px; } }
    </style>
</head>
<body>
    <h1>ORBIT — Form Map</h1>
    <p style="text-align: center; color: #666;">Wayne Shorter Style | F Major | 3/4 | 160 BPM</p>
    
    <div class="legend">
        <div class="legend-item"><div class="legend-box section-a"></div> Section A</div>
        <div class="legend-item"><div class="legend-box section-b"></div> Section B</div>
        <div class="legend-item"><div class="legend-box home"></div> Home (Fmaj7)</div>
    </div>
    
    <div class="form-grid">
        <div class="bar section-a home"><div class="bar-num">Bar 1</div><div class="chord">Fmaj7#11</div><div class="scale">F Lydian</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 2</div><div class="chord">Ebmaj7#5</div><div class="scale">Eb Lyd Aug</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 3</div><div class="chord">Dbmaj7</div><div class="scale">Db Lydian</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 4</div><div class="chord">Bmaj7</div><div class="scale">B Lydian</div></div>
        
        <div class="bar section-a"><div class="bar-num">Bar 5</div><div class="chord">Bbm9</div><div class="scale">Bb Dorian</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 6</div><div class="chord">Abmaj7</div><div class="scale">Ab Lydian</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 7</div><div class="chord">Gbmaj7</div><div class="scale">Gb Lydian</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 8</div><div class="chord">Emaj7</div><div class="scale">E Lydian</div></div>
        
        <div class="bar section-b home"><div class="bar-num">Bar 9</div><div class="chord">Fmaj7#11</div><div class="scale">F Lydian</div></div>
        <div class="bar section-b"><div class="bar-num">Bar 10</div><div class="chord">Dbmaj7</div><div class="scale">Db Lydian</div></div>
        <div class="bar section-b"><div class="bar-num">Bar 11</div><div class="chord">Amaj7</div><div class="scale">A Lydian</div></div>
        <div class="bar section-b"><div class="bar-num">Bar 12</div><div class="chord">Gmaj7</div><div class="scale">G Lydian</div></div>
        
        <div class="bar section-b home"><div class="bar-num">Bar 13</div><div class="chord">Fmaj7#11</div><div class="scale">F Lydian</div></div>
        <div class="bar section-b"><div class="bar-num">Bar 14</div><div class="chord">Ebm9</div><div class="scale">Eb Dorian</div></div>
        <div class="bar section-b"><div class="bar-num">Bar 15</div><div class="chord">Dbmaj7</div><div class="scale">Db Lydian</div></div>
        <div class="bar section-b home"><div class="bar-num">Bar 16</div><div class="chord">Fmaj7</div><div class="scale">F Lydian</div></div>
    </div>
    
    <div class="info">
        <h3>Root Motion Pattern</h3>
        <p><strong>Bars 1-4:</strong> F → Eb → Db → B (chromatic descent)</p>
        <p><strong>Bars 5-8:</strong> Bb → Ab → Gb → E (continued descent)</p>
        <p><strong>Bars 9-12:</strong> F → Db → A → G (wider intervals)</p>
        <p><strong>Bars 13-16:</strong> F → Eb → Db → F (return home)</p>
    </div>
</body>
</html>
"""

CRYSTAL_ANALYSIS = """# Crystal Silence — Harmonic Analysis

## Overview
**Style:** ECM Ballad (Ralph Towner / Egberto Gismonti)  
**Key:** A Major  
**Tempo:** 80 BPM  
**Time:** 4/4  
**Form:** 16 bars

---

## Chord Progression

```
Section A (bars 1-8):
| Amaj9     | F#m11     | Dmaj9     | E/A       |
| Amaj9     | C#m7      | Bm9       | Esus4  E7 |

Section B (bars 9-16):
| Fmaj7     | Gmaj7     | Amaj9     | Dmaj7     |
| Bm11      | E7sus4    | Amaj9     | Amaj9     |
```

---

## Roman Numeral Analysis

| Bar | Chord | Roman | Function |
|-----|-------|-------|----------|
| 1 | Amaj9 | I | Tonic |
| 2 | F#m11 | vi | Relative minor |
| 3 | Dmaj9 | IV | Subdominant |
| 4 | E/A | V/I | Dominant pedal |
| 5 | Amaj9 | I | Tonic |
| 6 | C#m7 | iii | Mediant |
| 7 | Bm9 | ii | Supertonic |
| 8 | Esus4 E7 | V | Dominant |
| 9 | Fmaj7 | bVI | Modal interchange (borrowed) |
| 10 | Gmaj7 | bVII | Modal interchange |
| 11 | Amaj9 | I | Return home |
| 12 | Dmaj7 | IV | Subdominant |
| 13 | Bm11 | ii | Supertonic |
| 14 | E7sus4 | V | Dominant suspension |
| 15-16 | Amaj9 | I | Final resolution |

---

## Key Harmonic Features

### 1. Open String Integration
A major allows extensive use of open strings:
- **Open A** (5th string) — Root
- **Open E** (6th/1st strings) — 5th
- **Open B** (2nd string) — 9th
- **Open D** (4th string) — 11th

### 2. Modal Interchange (Bars 9-10)
The Fmaj7 → Gmaj7 progression is borrowed from A minor/Aeolian:
- Creates "distant color" without leaving the key center
- Classic ECM harmonic move

### 3. Suspension Emphasis
Multiple sus4 and 11 chords create floating, unresolved quality:
- F#m11, Bm11, E7sus4

---

## Scale Palette

| Chord | Scale | Character |
|-------|-------|-----------|
| Amaj9 | A Lydian | Open, bright |
| F#m11 | F# Aeolian | Melancholy, suspended |
| Dmaj9 | D Lydian | Bright neighbor |
| E/A | E Mixolydian | Dominant color |
| C#m7 | C# Aeolian | Minor mediant |
| Bm9 | B Dorian | Natural 6 (G#) |
| Fmaj7 | F Lydian | Borrowed, distant |
| Gmaj7 | G Lydian | Chromatic approach |

---

## Campanella Technique Integration

### What is Campanella?
"Little bells" — notes ring into each other on different strings.

### Application to Crystal Silence

**Amaj9 arpeggio (campanella fingering):**
```
e|------------0---------|
B|--------2-------------|
G|----2-----------------|
D|--2-------------------|
A|0---------------------|
```
Each note on a different string = maximum sustain overlap.

**Open string voicings:**
```
Amaj9:   x-0-6-6-0-0  (E and B open)
F#m11:   x-0-4-6-0-0  (A pedal)
Dmaj9:   x-5-4-6-5-0  (high E open)
E/A:     x-0-2-1-0-0  (multiple opens)
```

---

## ECM Aesthetic Characteristics

1. **Space as composition** — Reverb tail is part of the music
2. **Quiet dynamics** — Never louder than mezzo-piano
3. **Open voicings** — Wide intervals between notes
4. **Melodic simplicity** — Fewer notes, more sustain
5. **Timbral focus** — Tone quality over velocity

---

## Triad Pairs for Improvisation

| Over Chord | Triad Pair | Sound |
|------------|-----------|-------|
| Amaj9 | A + B | Lydian color |
| F#m11 | F#m + A | Minor with relative major |
| Dmaj9 | D + E | Lydian 9 + #11 |
| Bm9 | D + E | Relative major color |

---

## Performance Notes

- **Tempo:** Extremely patient, breathe with the form
- **Dynamics:** pp to mp range only
- **Sustain:** Never dampen strings early
- **Reverb:** Use hall reverb generously
- **Touch:** Light, minimal attack
"""

CRYSTAL_VOICE_LEADING = """# Crystal Silence — Voice Leading Guide

## Guide Tone Lines

### Line 1: 3rds of each chord
```
Bar:  1    2    3    4    5    6    7    8
Tone: C#   A    F#   G#   C#   E    D    G#
      ↓    ↓    ↓    ↑    ↓    ↓    ↓    ↑
```

### Line 2: 7ths of each chord
```
Bar:  1    2    3    4    5    6    7    8
Tone: G#   E    C#   D    G#   B    A    D
      ↓    ↓    ↓    ↑    ↓    ↓    ↓    ↑
```

---

## Open String Pedal Points

### A Pedal (bars 1-8)
The open A string can sustain through most of Section A:
```
Amaj9: A is root ✓
F#m11: A is 3rd ✓
Dmaj9: A is 5th ✓
E/A: A is pedal bass ✓
C#m7: A is b6 (avoid or use as color)
Bm9: A is b7 ✓
Esus4: A is 11 ✓
```

### E Pedal (all bars)
Open E works almost everywhere:
```
Amaj9: E is 5th ✓
F#m11: E is b7 ✓
Dmaj9: E is 9 ✓
E/A: E is root ✓
Fmaj7: E is 7th ✓
Gmaj7: E is 6th ✓
Bm9: E is 11 ✓
```

---

## Common Tones Between Adjacent Chords

| Bars | Chords | Common Tones |
|------|--------|--------------|
| 1→2 | Amaj9 → F#m11 | A, C#, E |
| 2→3 | F#m11 → Dmaj9 | A, F# |
| 3→4 | Dmaj9 → E/A | A, E |
| 4→5 | E/A → Amaj9 | A, E |
| 5→6 | Amaj9 → C#m7 | C#, E |
| 6→7 | C#m7 → Bm9 | E |
| 7→8 | Bm9 → E7sus | B, E |
| 8→9 | E7 → Fmaj7 | None (distant!) |
| 9→10 | Fmaj7 → Gmaj7 | None (chromatic) |
| 10→11 | Gmaj7 → Amaj9 | None (whole step) |

---

## Campanella Voice Leading

### Principle: Adjacent notes on different strings

**Example over bars 1-4:**
```
String:  1    2    1    3    2    4    1    2
Note:    E    B    E    A    C#   D    G#   B
Fret:    0    0    0    2    2    0    4    0
```
All notes ring together creating harp-like texture.

---

## Smooth Voice Leading Paths

### Upper Register Path (melody)
```
C#5 → A4 → F#4 → E4 → C#5 → E5 → D5 → G#4
  ↘    ↘    ↘    ↗    ↗    ↘    ↘
```

### Drone + Melody Separation
Keep voices in distinct registers:
- **Drone:** A2-E3 range (open strings)
- **Melody:** A4-E6 range (upper positions)

---

## Voicing Suggestions

### Open Position Voicings
```
Amaj9:   x-0-6-6-0-0
F#m11:   x-0-4-6-0-0
Dmaj9:   x-5-4-6-5-0
E/A:     x-0-2-1-0-0
Bm11:    x-2-4-2-0-0
```

### High Position + Open String
```
Amaj9:   x-12-11-13-12-0  (open high E)
Dmaj7:   x-x-11-11-10-0   (open high E)
```

---

## The "Crystal" Effect

To achieve the crystalline, bell-like sound:
1. Use different strings for adjacent notes
2. Let all notes ring (no dampening)
3. Use dynamics to shape, not articulation
4. Embrace the reverb tail as part of the music
"""

CRYSTAL_FORM_MAP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Crystal Silence - Form Map</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #fff; color: #333; padding: 40px; max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; color: #1a1a2e; border-bottom: 3px solid #333; padding-bottom: 10px; }
        .form-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 30px 0; }
        .bar { background: #f5f5f5; border: 2px solid #333; border-radius: 8px; padding: 15px; text-align: center; }
        .bar-num { font-size: 0.8em; color: #666; }
        .chord { font-size: 1.2em; font-weight: bold; margin: 10px 0; }
        .scale { font-size: 0.9em; color: #555; }
        .section-a { background: #e8f5e9; }
        .section-b { background: #fce4ec; }
        .home { background: #c8e6c9; border-color: #2e7d32; }
        .borrowed { background: #fff3e0; border-color: #ef6c00; }
        .legend { display: flex; justify-content: center; gap: 20px; margin: 20px 0; flex-wrap: wrap; }
        .legend-item { display: flex; align-items: center; gap: 8px; }
        .legend-box { width: 20px; height: 20px; border: 1px solid #333; border-radius: 4px; }
        .info { background: #fafafa; padding: 20px; border: 1px solid #ddd; margin-top: 30px; }
        .open-strings { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0; }
        @media print { body { padding: 20px; } }
    </style>
</head>
<body>
    <h1>CRYSTAL SILENCE — Form Map</h1>
    <p style="text-align: center; color: #666;">ECM Ballad | A Major | 4/4 | 80 BPM</p>
    
    <div class="legend">
        <div class="legend-item"><div class="legend-box section-a"></div> Section A</div>
        <div class="legend-item"><div class="legend-box section-b"></div> Section B</div>
        <div class="legend-item"><div class="legend-box home"></div> Home (Amaj9)</div>
        <div class="legend-item"><div class="legend-box borrowed"></div> Borrowed (Modal Interchange)</div>
    </div>
    
    <div class="open-strings">
        <strong>Open Strings Available:</strong> A (5th), E (6th/1st), B (2nd), D (4th) — Use for campanella effect
    </div>
    
    <div class="form-grid">
        <div class="bar section-a home"><div class="bar-num">Bar 1</div><div class="chord">Amaj9</div><div class="scale">A Lydian</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 2</div><div class="chord">F#m11</div><div class="scale">F# Aeolian</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 3</div><div class="chord">Dmaj9</div><div class="scale">D Lydian</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 4</div><div class="chord">E/A</div><div class="scale">E Mixolydian</div></div>
        
        <div class="bar section-a home"><div class="bar-num">Bar 5</div><div class="chord">Amaj9</div><div class="scale">A Lydian</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 6</div><div class="chord">C#m7</div><div class="scale">C# Aeolian</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 7</div><div class="chord">Bm9</div><div class="scale">B Dorian</div></div>
        <div class="bar section-a"><div class="bar-num">Bar 8</div><div class="chord">Esus E7</div><div class="scale">E Mixolydian</div></div>
        
        <div class="bar section-b borrowed"><div class="bar-num">Bar 9</div><div class="chord">Fmaj7</div><div class="scale">F Lydian ♭</div></div>
        <div class="bar section-b borrowed"><div class="bar-num">Bar 10</div><div class="chord">Gmaj7</div><div class="scale">G Lydian ♭</div></div>
        <div class="bar section-b home"><div class="bar-num">Bar 11</div><div class="chord">Amaj9</div><div class="scale">A Lydian</div></div>
        <div class="bar section-b"><div class="bar-num">Bar 12</div><div class="chord">Dmaj7</div><div class="scale">D Lydian</div></div>
        
        <div class="bar section-b"><div class="bar-num">Bar 13</div><div class="chord">Bm11</div><div class="scale">B Dorian</div></div>
        <div class="bar section-b"><div class="bar-num">Bar 14</div><div class="chord">E7sus4</div><div class="scale">E Mixolydian</div></div>
        <div class="bar section-b home"><div class="bar-num">Bar 15</div><div class="chord">Amaj9</div><div class="scale">A Lydian</div></div>
        <div class="bar section-b home"><div class="bar-num">Bar 16</div><div class="chord">Amaj9</div><div class="scale">A Lydian</div></div>
    </div>
    
    <div class="info">
        <h3>Key Moments</h3>
        <p><strong>Bars 9-10:</strong> Modal interchange creates "distant color" (Fmaj7, Gmaj7 borrowed from A minor)</p>
        <p><strong>Bars 15-16:</strong> Double home chord for extended resolution / fade</p>
        <p><strong>Campanella:</strong> Use open strings throughout for bell-like sustain</p>
    </div>
</body>
</html>
"""

# ============================================================================
# SOURCE FILE GENERATION
# ============================================================================

def create_musicxml_header(title: str, key_fifths: int, time_beats: int, time_type: int, tempo: int, divisions: int = 16) -> ET.Element:
    """Create a basic MusicXML score structure."""
    root = ET.Element("score-partwise")
    root.set("version", "4.0")
    
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = title
    
    ident = ET.SubElement(root, "identification")
    creator = ET.SubElement(ident, "creator")
    creator.set("type", "composer")
    creator.text = "GCE Jazz"
    
    part_list = ET.SubElement(root, "part-list")
    score_part = ET.SubElement(part_list, "score-part")
    score_part.set("id", "P1")
    ET.SubElement(score_part, "part-name").text = "Guitar"
    
    part = ET.SubElement(root, "part")
    part.set("id", "P1")
    
    return root

def add_measure_attrs(measure: ET.Element, divisions: int, key_fifths: int, time_beats: int, time_type: int, tempo: int):
    """Add attributes and tempo to first measure."""
    attrs = ET.SubElement(measure, "attributes")
    ET.SubElement(attrs, "divisions").text = str(divisions)
    
    key = ET.SubElement(attrs, "key")
    ET.SubElement(key, "fifths").text = str(key_fifths)
    ET.SubElement(key, "mode").text = "major"
    
    time = ET.SubElement(attrs, "time")
    ET.SubElement(time, "beats").text = str(time_beats)
    ET.SubElement(time, "beat-type").text = str(time_type)
    
    clef = ET.SubElement(attrs, "clef")
    ET.SubElement(clef, "sign").text = "G"
    ET.SubElement(clef, "line").text = "2"
    ET.SubElement(clef, "clef-octave-change").text = "-1"
    
    direction = ET.SubElement(measure, "direction")
    direction.set("placement", "above")
    dir_type = ET.SubElement(direction, "direction-type")
    metro = ET.SubElement(dir_type, "metronome")
    ET.SubElement(metro, "beat-unit").text = "quarter"
    ET.SubElement(metro, "per-minute").text = str(tempo)

def add_chord_note(measure: ET.Element, step: str, alter: int, octave: int, duration: int, is_chord: bool = False):
    """Add a note to a measure."""
    note = ET.SubElement(measure, "note")
    if is_chord:
        ET.SubElement(note, "chord")
    pitch = ET.SubElement(note, "pitch")
    ET.SubElement(pitch, "step").text = step
    if alter != 0:
        ET.SubElement(pitch, "alter").text = str(alter)
    ET.SubElement(pitch, "octave").text = str(octave)
    ET.SubElement(note, "duration").text = str(duration)
    ET.SubElement(note, "type").text = "whole" if duration >= 64 else "half" if duration >= 32 else "quarter"

def generate_orbit_master():
    """Generate Orbit master source file."""
    root = create_musicxml_header("Orbit - Master Source", -1, 3, 4, 160)
    part = root.find("./part[@id='P1']")
    
    # Orbit progression with root notes
    chords = [
        ("F", 0, 3), ("Eb", -1, 3), ("Db", -1, 3), ("B", 0, 2),
        ("Bb", -1, 2), ("Ab", -1, 3), ("Gb", -1, 3), ("E", 0, 3),
        ("F", 0, 3), ("Db", -1, 3), ("A", 0, 3), ("G", 0, 3),
        ("F", 0, 3), ("Eb", -1, 3), ("Db", -1, 3), ("F", 0, 3)
    ]
    
    for i, (note, alter, octave) in enumerate(chords, 1):
        measure = ET.SubElement(part, "measure")
        measure.set("number", str(i))
        
        if i == 1:
            add_measure_attrs(measure, 16, -1, 3, 4, 160)
        
        # Root note (dotted half = whole bar in 3/4)
        add_chord_note(measure, note, alter, octave, 48)
    
    return root

def generate_crystal_master():
    """Generate Crystal Silence master source file."""
    root = create_musicxml_header("Crystal Silence - Master Source", 3, 4, 4, 80)
    part = root.find("./part[@id='P1']")
    
    # Crystal progression with root notes
    chords = [
        ("A", 0, 3), ("F", 1, 3), ("D", 0, 3), ("E", 0, 3),
        ("A", 0, 3), ("C", 1, 3), ("B", 0, 2), ("E", 0, 3),
        ("F", 0, 3), ("G", 0, 3), ("A", 0, 3), ("D", 0, 3),
        ("B", 0, 2), ("E", 0, 3), ("A", 0, 3), ("A", 0, 3)
    ]
    
    for i, (note, alter, octave) in enumerate(chords, 1):
        measure = ET.SubElement(part, "measure")
        measure.set("number", str(i))
        
        if i == 1:
            add_measure_attrs(measure, 16, 3, 4, 4, 80)
        
        # Root note (whole note)
        add_chord_note(measure, note, alter, octave, 64)
    
    return root

def write_xml(root: ET.Element, path: str):
    """Write XML to file with pretty printing."""
    xml_str = ET.tostring(root, encoding="unicode")
    parsed = minidom.parseString(xml_str)
    pretty = '<?xml version="1.0" encoding="UTF-8"?>\n' + parsed.toprettyxml(indent="  ")[23:]
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(pretty)
    print(f"[OK] Wrote: {path}")

def write_text(content: str, path: str):
    """Write text content to file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Wrote: {path}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("GENERATING ANALYSIS & SOURCE FILES")
    print("=" * 60)
    
    base_orbit = Path(r"C:\Users\mike\Documents\Cursor AI Projects\GCE-Jazz\Trio Tunes\Tune02_Orbit")
    base_crystal = Path(r"C:\Users\mike\Documents\Cursor AI Projects\GCE-Jazz\Trio Tunes\Tune11_Crystal_Silence")
    
    # =========================================================================
    # ORBIT
    # =========================================================================
    print("\n=== ORBIT ===")
    
    # Analysis folder
    analysis_orbit = base_orbit / "Analysis"
    write_text(ORBIT_ANALYSIS, str(analysis_orbit / "Orbit_Harmonic_Analysis.md"))
    write_text(ORBIT_VOICE_LEADING, str(analysis_orbit / "Orbit_Voice_Leading_Guide.md"))
    write_text(ORBIT_FORM_MAP_HTML, str(analysis_orbit / "Orbit_Form_Map.html"))
    
    # Source folder
    source_orbit = base_orbit / "Source"
    orbit_master = generate_orbit_master()
    write_xml(orbit_master, str(source_orbit / "Orbit_Master.musicxml"))
    
    # =========================================================================
    # CRYSTAL SILENCE
    # =========================================================================
    print("\n=== CRYSTAL SILENCE ===")
    
    # Analysis folder
    analysis_crystal = base_crystal / "Analysis"
    write_text(CRYSTAL_ANALYSIS, str(analysis_crystal / "Crystal_Silence_Harmonic_Analysis.md"))
    write_text(CRYSTAL_VOICE_LEADING, str(analysis_crystal / "Crystal_Silence_Voice_Leading_Guide.md"))
    write_text(CRYSTAL_FORM_MAP_HTML, str(analysis_crystal / "Crystal_Silence_Form_Map.html"))
    
    # Source folder
    source_crystal = base_crystal / "Source"
    crystal_master = generate_crystal_master()
    write_xml(crystal_master, str(source_crystal / "Crystal_Silence_Master.musicxml"))
    
    print("\n" + "=" * 60)
    print("ANALYSIS & SOURCE FILES COMPLETE!")
    print("=" * 60)
    print("\nGenerated:")
    print("  ORBIT:")
    print("    - Analysis/Orbit_Harmonic_Analysis.md")
    print("    - Analysis/Orbit_Voice_Leading_Guide.md")
    print("    - Analysis/Orbit_Form_Map.html")
    print("    - Source/Orbit_Master.musicxml")
    print("  CRYSTAL SILENCE:")
    print("    - Analysis/Crystal_Silence_Harmonic_Analysis.md")
    print("    - Analysis/Crystal_Silence_Voice_Leading_Guide.md")
    print("    - Analysis/Crystal_Silence_Form_Map.html")
    print("    - Source/Crystal_Silence_Master.musicxml")

if __name__ == "__main__":
    main()

