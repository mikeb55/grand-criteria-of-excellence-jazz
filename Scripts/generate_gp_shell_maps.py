"""
Level 2 Shell Voicing Maps - Guitar Pro 8 Generator
====================================================
TAB is authoritative. Notation follows TAB.
Frets 5-9 ONLY. Strings 5-3 or 4-2 ONLY.
"""

import guitarpro
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(r"C:\Users\mike\Documents\Cursor AI Projects\GCE-Jazz\Trio Tunes\Alternative_LeadSheets")

# Guitar tuning (standard)
TUNING = [64, 59, 55, 50, 45, 40]  # E4, B3, G3, D3, A2, E2


def create_shell_voicing_track(song_title: str, composer: str, time_sig: tuple, key: int, voicings: list) -> guitarpro.models.Song:
    """Create a Guitar Pro song with shell voicings."""
    
    song = guitarpro.models.Song()
    song.title = song_title
    song.artist = composer
    song.tempo = guitarpro.models.Tempo(value=60)
    
    # Create guitar track
    track = guitarpro.models.Track()
    track.name = "Guitar"
    track.channel.instrument = 25  # Acoustic Guitar (steel)
    track.isPercussionTrack = False
    track.strings = [guitarpro.models.GuitarString(i+1, TUNING[i]) for i in range(6)]
    
    # Group voicings by bar
    bars = {}
    for v in voicings:
        bar_num = v['bar']
        if bar_num not in bars:
            bars[bar_num] = []
        bars[bar_num].append(v)
    
    # Create measures
    for bar_num in range(1, 17):
        measure_header = guitarpro.models.MeasureHeader()
        measure_header.number = bar_num
        measure_header.start = 960 * (bar_num - 1) * time_sig[0]
        measure_header.tempo = guitarpro.models.Tempo(value=60)
        measure_header.timeSignature = guitarpro.models.TimeSignature(
            numerator=time_sig[0],
            denominator=guitarpro.models.Duration(value=time_sig[1])
        )
        if bar_num == 1:
            measure_header.keySignature = guitarpro.models.KeySignature(key=key, isMinor=False)
        
        # Add section markers
        if bar_num == 1:
            measure_header.marker = guitarpro.models.Marker(title="A", color=guitarpro.models.Color(0, 0, 0))
        elif bar_num == 9:
            measure_header.marker = guitarpro.models.Marker(title="B", color=guitarpro.models.Color(0, 0, 0))
        elif bar_num == 13:
            measure_header.marker = guitarpro.models.Marker(title="A'", color=guitarpro.models.Color(0, 0, 0))
        
        song.measureHeaders.append(measure_header)
        
        # Create measure for track
        measure = guitarpro.models.Measure(track, measure_header)
        
        # Add voice
        voice = guitarpro.models.Voice(measure)
        
        # Get voicings for this bar
        bar_voicings = bars.get(bar_num, [])
        
        if bar_voicings:
            for v in bar_voicings:
                beat = guitarpro.models.Beat(voice)
                beat.start = 960
                
                # Set duration based on voicing
                if v.get('duration') == '2':
                    beat.duration = guitarpro.models.Duration(value=2)  # Half note
                else:
                    beat.duration = guitarpro.models.Duration(value=1)  # Whole note
                
                # Add chord text
                beat.text = guitarpro.models.BeatText(value=v['chord'])
                
                # Add notes with explicit string/fret (TAB-first!)
                for string, fret in zip(v['strings'], v['frets']):
                    note = guitarpro.models.Note(beat)
                    note.string = string
                    note.fret = fret
                    note.value = TUNING[string - 1] + fret
                    note.velocity = 95
                    beat.notes.append(note)
                
                voice.beats.append(beat)
        else:
            # Empty bar - add rest
            beat = guitarpro.models.Beat(voice)
            beat.duration = guitarpro.models.Duration(value=1)
            voice.beats.append(beat)
        
        measure.voices.append(voice)
        # Add empty voices for remaining slots
        for _ in range(1, 4):
            empty_voice = guitarpro.models.Voice(measure)
            measure.voices.append(empty_voice)
        
        track.measures.append(measure)
    
    song.tracks.append(track)
    return song


# =============================================================================
# VOICING DATA (TAB-FIRST: string, fret, all frets 5-9)
# =============================================================================

THE_MIRROR_VOICINGS = [
    {'bar': 1, 'chord': 'Abmaj7', 'strings': (4, 3, 2), 'frets': (6, 5, 8)},
    {'bar': 2, 'chord': 'Fm7', 'strings': (5, 4, 3), 'frets': (8, 6, 8)},
    {'bar': 3, 'chord': 'Dbmaj7', 'strings': (3, 2, 1), 'frets': (5, 6, 9)},
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
    {'bar': 15, 'chord': 'Dbmaj7', 'strings': (3, 2, 1), 'frets': (5, 6, 9), 'duration': '2'},
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
    {'bar': 10, 'chord': 'Gmaj7', 'strings': (5, 4, 3), 'frets': (5, 9, 7)},  # Adjusted: G on str5/fret5, B on str4/fret9, F# on str3/fret7
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
    {'bar': 12, 'chord': 'Gmaj7', 'strings': (5, 4, 3), 'frets': (5, 9, 7)},  # Adjusted: G on str5/fret5, B on str4/fret9, F# on str3/fret7
    {'bar': 13, 'chord': 'Fmaj7', 'strings': (5, 4, 3), 'frets': (8, 7, 9)},
    {'bar': 14, 'chord': 'Ebm9', 'strings': (5, 4, 3), 'frets': (6, 6, 6)},  # Adjusted to stay in 5-9
    {'bar': 15, 'chord': 'Dbmaj7', 'strings': (4, 3, 2), 'frets': (5, 6, 9)},
    {'bar': 16, 'chord': 'Fmaj7', 'strings': (5, 4, 3), 'frets': (8, 7, 9)},
]


def validate_frets(voicings: list, song_name: str) -> bool:
    """Validate all frets are 5-9."""
    valid = True
    for v in voicings:
        for fret in v['frets']:
            if fret < 5 or fret > 9:
                print(f"ERROR: {song_name} bar {v['bar']} has fret {fret} (must be 5-9)")
                valid = False
    return valid


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    songs = [
        ("The Mirror 5X - Shell Voicing Map", "Mike Bryant", (4, 4), -4, THE_MIRROR_VOICINGS, "The_Mirror_Level2_ShellVoicingMap"),
        ("Crystal Silence - Shell Voicing Map", "Mike Bryant", (4, 4), 3, CRYSTAL_SILENCE_VOICINGS, "Crystal_Silence_Level2_ShellVoicingMap"),
        ("Orbit - Shell Voicing Map", "Mike Bryant", (3, 4), -1, ORBIT_VOICINGS, "Orbit_Level2_ShellVoicingMap"),
    ]
    
    print("Validating fret ranges (5-9 only)...")
    all_valid = True
    for title, _, _, _, voicings, _ in songs:
        if not validate_frets(voicings, title):
            all_valid = False
    
    if not all_valid:
        print("\nFRET VALIDATION FAILED. Fix voicings before proceeding.")
        return
    
    print("All frets validated: 5-9 only.\n")
    
    for title, composer, time_sig, key, voicings, filename in songs:
        print(f"Creating: {filename}.gp")
        song = create_shell_voicing_track(title, composer, time_sig, key, voicings)
        output_path = OUTPUT_DIR / f"{filename}.gp"
        guitarpro.write(song, str(output_path))
        print(f"  Saved: {output_path}")
    
    print("\n" + "="*60)
    print("Guitar Pro files created successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Open each .gp file in Guitar Pro 8")
    print("2. File > Export > Image (PNG)")
    print("3. Save to the same folder with exact filenames")
    print("\nOr run this command to open Guitar Pro 8:")
    print('  & "C:\\Program Files\\Arobas Music\\Guitar Pro 8\\GuitarPro.exe"')


if __name__ == "__main__":
    main()

