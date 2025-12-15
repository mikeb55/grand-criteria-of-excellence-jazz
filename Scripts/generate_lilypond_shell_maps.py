"""
Level 2 Shell Voicing Maps - LilyPond Generator (TAB-FIRST)
============================================================
TAB is authoritative. Pitches derived from string+fret.
Frets 5-9 ONLY.
"""

from pathlib import Path

# Output directory
OUTPUT_DIR = Path(r"C:\Users\mike\Documents\Cursor AI Projects\GCE-Jazz\Trio Tunes\Alternative_LeadSheets")

# Guitar tuning (MIDI pitch for open strings)
TUNING = {1: 64, 2: 59, 3: 55, 4: 50, 5: 45, 6: 40}  # E4, B3, G3, D3, A2, E2

# MIDI to LilyPond note name (with octave)
def midi_to_lilypond(midi: int) -> str:
    """Convert MIDI pitch to LilyPond note name."""
    NOTE_NAMES = ['c', 'cis', 'd', 'dis', 'e', 'f', 'fis', 'g', 'gis', 'a', 'ais', 'b']
    # Use flats for some notes
    FLAT_NOTES = {1: 'des', 3: 'ees', 6: 'ges', 8: 'aes', 10: 'bes'}
    
    octave = (midi // 12) - 1  # MIDI 60 = C4 = octave 4
    pc = midi % 12
    
    # Prefer flats for jazz
    if pc in FLAT_NOTES:
        note = FLAT_NOTES[pc]
    else:
        note = NOTE_NAMES[pc]
    
    # LilyPond octave: c' = C4, c'' = C5, c = C3, c, = C2
    lily_octave = octave - 3  # c' is octave 4, so offset by 3
    
    if lily_octave > 0:
        note += "'" * lily_octave
    elif lily_octave < 0:
        note += "," * abs(lily_octave)
    
    return note


def string_fret_to_midi(string: int, fret: int) -> int:
    """Convert string/fret to MIDI pitch."""
    return TUNING[string] + fret


def generate_lilypond(title: str, composer: str, key_sig: str, time_sig: str, voicings: list, output_name: str):
    """Generate LilyPond file with correct TAB-first pitches."""
    
    # Group voicings by bar
    bars = {}
    for v in voicings:
        bar_num = v['bar']
        if bar_num not in bars:
            bars[bar_num] = []
        bars[bar_num].append(v)
    
    # Build notation and TAB content
    notation_bars = []
    tab_bars = []
    chord_bars = []
    
    for bar_num in range(1, 17):
        bar_voicings = bars.get(bar_num, [])
        
        notation_notes = []
        tab_notes = []
        chord_names = []
        
        for v in bar_voicings:
            # Calculate correct pitches from string+fret (TAB-first!)
            notes = []
            tab_chord = []
            
            for string, fret in zip(v['strings'], v['frets']):
                midi = string_fret_to_midi(string, fret)
                lily_note = midi_to_lilypond(midi)
                notes.append((midi, lily_note, string))
                tab_chord.append((midi, lily_note, string))
            
            # Sort by pitch (low to high)
            notes.sort(key=lambda x: x[0])
            tab_chord.sort(key=lambda x: x[0])
            
            # Build notation chord
            dur = v.get('duration', '1')
            note_strs = [n[1] for n in notes]
            notation_notes.append(f"<{' '.join(note_strs)}>{dur}")
            
            # Build TAB chord with string numbers
            tab_strs = [f"{n[1]}\\{n[2]}" for n in tab_chord]
            tab_notes.append(f"<{' '.join(tab_strs)}>{dur}")
            
            # Chord name for chordmode
            chord_names.append(chord_to_lilypond(v['chord'], dur))
        
        if notation_notes:
            notation_bars.append("  " + " ".join(notation_notes))
            tab_bars.append("  " + " ".join(tab_notes))
            chord_bars.append("  " + " ".join(chord_names))
        else:
            notation_bars.append("  r1")
            tab_bars.append("  r1")
            chord_bars.append("  r1")
    
    # Section markers
    def add_marker(content: list, bar: int, marker: str):
        content[bar - 1] = f'  \\mark \\markup {{ \\box "{marker}" }}\n' + content[bar - 1]
    
    add_marker(notation_bars, 1, "A")
    add_marker(notation_bars, 9, "B")
    add_marker(notation_bars, 13, "A'")
    
    # Add break after bar 8
    notation_bars[7] += "\n  \\break"
    tab_bars[7] += "\n  \\break"
    
    lily_content = f'''\\version "2.24.0"

\\header {{
  title = "{title}"
  composer = "{composer}"
  tagline = ##f
}}

\\paper {{
  #(set-paper-size "a4")
  top-margin = 15\\mm
  bottom-margin = 15\\mm
  left-margin = 15\\mm
  right-margin = 15\\mm
  indent = 0
}}

chordNames = \\chordmode {{
{chr(10).join(chord_bars)}
}}

notation = {{
  \\clef "treble_8"
  \\key {key_sig}
  \\time {time_sig}
  
{chr(10).join(notation_bars)}
  \\bar "|."
}}

tabNotation = {{
{chr(10).join(tab_bars)}
  \\bar "|."
}}

\\score {{
  <<
    \\new ChordNames {{ \\chordNames }}
    \\new Staff {{ \\notation }}
    \\new TabStaff {{
      \\set TabStaff.stringTunings = \\stringTuning <e, a, d g b e'>
      \\tabNotation
    }}
  >>
  \\layout {{ }}
}}
'''
    
    output_path = OUTPUT_DIR / f"{output_name}.ly"
    output_path.write_text(lily_content, encoding='utf-8')
    print(f"Generated: {output_path}")
    return output_path


def chord_to_lilypond(chord_name: str, duration: str = "1") -> str:
    """Convert chord name to LilyPond chordmode."""
    chord = chord_name.replace("#11", "").replace("#5", "").replace("/A", "")
    
    if len(chord) > 1 and chord[1] in 'b#':
        root = chord[0:2]
        quality = chord[2:]
    else:
        root = chord[0]
        quality = chord[1:]
    
    lily_root = root[0].lower()
    if len(root) > 1:
        if root[1] == 'b':
            lily_root += "es"
        elif root[1] == '#':
            lily_root += "is"
    
    if 'maj7' in quality or 'maj9' in quality:
        lily_quality = ":maj7"
    elif 'm7' in quality or 'm9' in quality or 'm11' in quality:
        lily_quality = ":m7"
    elif quality == 'm':
        lily_quality = ":m"
    elif 'sus4' in quality:
        lily_quality = ":sus4"
    elif '7' in quality:
        lily_quality = ":7"
    else:
        lily_quality = ":maj7"
    
    return f"{lily_root}{duration}{lily_quality}"


# =============================================================================
# VOICING DATA (TAB-FIRST: string, fret, all frets 5-9)
# =============================================================================

THE_MIRROR_VOICINGS = [
    {'bar': 1, 'chord': 'Abmaj7', 'strings': (4, 3, 2), 'frets': (6, 5, 8)},
    {'bar': 2, 'chord': 'Fm7', 'strings': (5, 4, 3), 'frets': (8, 6, 8)},
    {'bar': 3, 'chord': 'Dbmaj7', 'strings': (4, 3, 2), 'frets': (5, 6, 9)},
    {'bar': 4, 'chord': 'Ebsus4', 'strings': (5, 4, 3), 'frets': (6, 6, 6), 'duration': '2'},
    {'bar': 4, 'chord': 'Eb7', 'strings': (5, 4, 3), 'frets': (6, 5, 6), 'duration': '2'},
    {'bar': 5, 'chord': 'Abmaj7', 'strings': (4, 3, 2), 'frets': (6, 5, 8)},
    {'bar': 6, 'chord': 'Bbm7', 'strings': (4, 3, 2), 'frets': (8, 6, 9)},
    {'bar': 7, 'chord': 'Gbmaj7', 'strings': (5, 4, 3), 'frets': (8, 8, 6)},
    {'bar': 8, 'chord': 'Cm7', 'strings': (5, 4, 3), 'frets': (6, 8, 5), 'duration': '2'},
    {'bar': 8, 'chord': 'Fm7', 'strings': (5, 4, 3), 'frets': (8, 6, 8), 'duration': '2'},
    {'bar': 9, 'chord': 'Bmaj7', 'strings': (5, 4, 3), 'frets': (6, 8, 8)},
    {'bar': 10, 'chord': 'Emaj7', 'strings': (5, 4, 3), 'frets': (7, 6, 8)},
    {'bar': 11, 'chord': 'Bbm7', 'strings': (4, 3, 2), 'frets': (8, 6, 9)},
    {'bar': 12, 'chord': 'Eb7', 'strings': (5, 4, 3), 'frets': (6, 5, 6)},
    {'bar': 13, 'chord': 'Abmaj7', 'strings': (4, 3, 2), 'frets': (6, 5, 8)},
    {'bar': 14, 'chord': 'Fm7', 'strings': (5, 4, 3), 'frets': (8, 6, 8)},
    {'bar': 15, 'chord': 'Dbmaj7', 'strings': (4, 3, 2), 'frets': (5, 6, 9), 'duration': '2'},
    {'bar': 15, 'chord': 'Dbm', 'strings': (5, 4, 3), 'frets': (7, 6, 6), 'duration': '2'},
    {'bar': 16, 'chord': 'Abmaj7', 'strings': (4, 3, 2), 'frets': (6, 5, 8)},
]

CRYSTAL_SILENCE_VOICINGS = [
    {'bar': 1, 'chord': 'Amaj9', 'strings': (5, 4, 3), 'frets': (5, 6, 6)},
    {'bar': 2, 'chord': 'F#m11', 'strings': (4, 3, 2), 'frets': (9, 7, 9)},
    {'bar': 3, 'chord': 'Dmaj9', 'strings': (4, 3, 2), 'frets': (5, 7, 6)},
    {'bar': 4, 'chord': 'E/A', 'strings': (5, 4, 3), 'frets': (7, 6, 7)},
    {'bar': 5, 'chord': 'Amaj9', 'strings': (5, 4, 3), 'frets': (5, 6, 6)},
    {'bar': 6, 'chord': 'C#m7', 'strings': (4, 3, 2), 'frets': (9, 9, 7)},
    {'bar': 7, 'chord': 'Bm9', 'strings': (4, 3, 2), 'frets': (7, 7, 5)},
    {'bar': 8, 'chord': 'Esus4', 'strings': (5, 4, 3), 'frets': (7, 7, 7), 'duration': '2'},
    {'bar': 8, 'chord': 'E7', 'strings': (5, 4, 3), 'frets': (7, 6, 7), 'duration': '2'},
    {'bar': 9, 'chord': 'Fmaj7', 'strings': (5, 4, 3), 'frets': (8, 7, 9)},
    {'bar': 10, 'chord': 'Gmaj7', 'strings': (5, 4, 3), 'frets': (5, 9, 7)},
    {'bar': 11, 'chord': 'Amaj9', 'strings': (5, 4, 3), 'frets': (5, 6, 6)},
    {'bar': 12, 'chord': 'Dmaj7', 'strings': (4, 3, 2), 'frets': (5, 7, 6)},
    {'bar': 13, 'chord': 'Bm11', 'strings': (4, 3, 2), 'frets': (7, 7, 5)},
    {'bar': 14, 'chord': 'E7sus4', 'strings': (5, 4, 3), 'frets': (7, 7, 7)},
    {'bar': 15, 'chord': 'Amaj9', 'strings': (5, 4, 3), 'frets': (5, 6, 6)},
    {'bar': 16, 'chord': 'Amaj9', 'strings': (5, 4, 3), 'frets': (5, 6, 6)},
]

ORBIT_VOICINGS = [
    {'bar': 1, 'chord': 'Fmaj7', 'strings': (5, 4, 3), 'frets': (8, 7, 9)},
    {'bar': 2, 'chord': 'Ebmaj7', 'strings': (5, 4, 3), 'frets': (6, 5, 7)},
    {'bar': 3, 'chord': 'Dbmaj7', 'strings': (4, 3, 2), 'frets': (5, 6, 9)},
    {'bar': 4, 'chord': 'Bmaj7', 'strings': (5, 4, 3), 'frets': (6, 8, 8)},
    {'bar': 5, 'chord': 'Bbm9', 'strings': (4, 3, 2), 'frets': (8, 6, 9)},
    {'bar': 6, 'chord': 'Abmaj7', 'strings': (4, 3, 2), 'frets': (6, 5, 8)},
    {'bar': 7, 'chord': 'Gbmaj7', 'strings': (5, 4, 3), 'frets': (8, 8, 6)},
    {'bar': 8, 'chord': 'Emaj7', 'strings': (5, 4, 3), 'frets': (7, 6, 8)},
    {'bar': 9, 'chord': 'Fmaj7', 'strings': (5, 4, 3), 'frets': (8, 7, 9)},
    {'bar': 10, 'chord': 'Dbmaj7', 'strings': (4, 3, 2), 'frets': (5, 6, 9)},
    {'bar': 11, 'chord': 'Amaj7', 'strings': (5, 4, 3), 'frets': (5, 6, 6)},
    {'bar': 12, 'chord': 'Gmaj7', 'strings': (5, 4, 3), 'frets': (5, 9, 7)},
    {'bar': 13, 'chord': 'Fmaj7', 'strings': (5, 4, 3), 'frets': (8, 7, 9)},
    {'bar': 14, 'chord': 'Ebm9', 'strings': (5, 4, 3), 'frets': (6, 6, 6)},
    {'bar': 15, 'chord': 'Dbmaj7', 'strings': (4, 3, 2), 'frets': (5, 6, 9)},
    {'bar': 16, 'chord': 'Fmaj7', 'strings': (5, 4, 3), 'frets': (8, 7, 9)},
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Validate all frets are 5-9
    print("Validating fret ranges (5-9 only)...")
    all_valid = True
    for name, voicings in [("The Mirror", THE_MIRROR_VOICINGS), 
                            ("Crystal Silence", CRYSTAL_SILENCE_VOICINGS),
                            ("Orbit", ORBIT_VOICINGS)]:
        for v in voicings:
            for fret in v['frets']:
                if fret < 5 or fret > 9:
                    print(f"ERROR: {name} bar {v['bar']} has fret {fret}")
                    all_valid = False
    
    if not all_valid:
        print("VALIDATION FAILED")
        return
    
    print("All frets validated: 5-9 only.\n")
    
    # Generate LilyPond files
    files = []
    files.append(generate_lilypond(
        "The Mirror 5X - Shell Voicing Map", "Mike Bryant",
        "aes \\major", "4/4", THE_MIRROR_VOICINGS, "The_Mirror_Level2_ShellVoicingMap"
    ))
    files.append(generate_lilypond(
        "Crystal Silence - Shell Voicing Map", "Mike Bryant", 
        "a \\major", "4/4", CRYSTAL_SILENCE_VOICINGS, "Crystal_Silence_Level2_ShellVoicingMap"
    ))
    files.append(generate_lilypond(
        "Orbit - Shell Voicing Map", "Mike Bryant",
        "f \\major", "3/4", ORBIT_VOICINGS, "Orbit_Level2_ShellVoicingMap"
    ))
    
    print("\nLilyPond files generated. Run these commands to create PNGs:")
    for f in files:
        print(f'  lilypond --png -dresolution=300 "{f}"')


if __name__ == "__main__":
    main()
