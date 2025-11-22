import json
import os

# --- DATA DEFINITIONS ---

# 1. V3_RC_Presets_Full.json
rc_presets = {
    "version": "3.0",
    "description": "Bebop-Language Project V3.0 Presets",
    "engines": {
        "Engine_A_Bebop": {
            "description": "Parker / Stitt / Barry Harris / Bailey / Martino / Django / Hawkins / Wes",
            "features": {
                "target_gravity": ["3rd", "5th", "7th", "9th"],
                "scales": ["Bebop Major", "Bebop Dominant", "6th-Diminished"],
                "ornamentation": ["Approach Tones", "Enclosures (SB/Django)"],
                "rhythm": "Swing Cells + Anticipations",
                "behavior": "Up-Scale, Down-Chord (Barry Harris)"
            },
            "phrases": [
                {"name": "Parker Enclosure", "type": "melodic", "length": "2 beats"},
                {"name": "Martino Minor Convert", "type": "harmonic", "rule": "Minor for Dom7"},
                {"name": "Hawkins Arpeggio", "type": "arpeggio", "direction": "vertical"},
                {"name": "Wes Octaves", "type": "voicing", "interval": 12}
            ]
        },
        "Engine_B_Avant": {
            "description": "Shorter / Coltrane / Avant Engine",
            "features": {
                "intervals": ["2nds", "4ths", "5ths"],
                "harmony": ["Pentatonic", "Hexatonic", "Triad Superimposition"],
                "scales": ["Altered", "Whole Tone", "Acoustic", "Diminished"],
                "rhythm": ["3+3+2", "5+3", "Over-the-barline"]
            },
            "phrases": [
                {"name": "Sheets of Sound", "pattern": "1-2-3-5"},
                {"name": "Side Slipping", "rule": "Shift +/- 1 semitone"},
                {"name": "Harmolodic", "mode": "Free"}
            ]
        },
        "Engine_C_Orchestral": {
            "description": "Maria Schneider Orchestral Jazz Engine",
            "features": {
                "modal_color": ["Lydian", "Lydian b7"],
                "texture": ["Planed Clusters", "Pastel Triad Pairs"],
                "orchestration": ["String Arcs", "Woodwind Dovetailing"]
            },
            "phrases": [
                {"name": "Polyrhythm 3:2", "ratio": "3:2"},
                {"name": "Polyrhythm 5:4", "ratio": "5:4"},
                {"name": "Color Voice Leading", "method": "semitone_shift"}
            ]
        },
        "Engine_D_GuitarModernism": {
            "description": "Metheny / Scofield / Rosenwinkel / Abercrombie / Coryell / Martino",
            "features": {
                "melody": "Wide Intervals + Pentatonics",
                "rhythm": "Chromatic Displacement",
                "texture": "Multi-octave lines"
            },
            "phrases": [
                {"name": "Metheny Pentatonic", "type": "melodic"},
                {"name": "Scofield Outside", "type": "chromatic_displacement"},
                {"name": "Rosenwinkel Triads", "type": "superimposition"},
                {"name": "ECM Ostinato", "length": "5 notes"}
            ]
        }
    }
}

# 2. rc_liveset.json
rc_liveset = {
    "name": "Bebop V3 Live Set",
    "tracks": [
        {"id": 1, "name": "Lead", "engine": "Engine_A_Bebop", "midi_channel": 1},
        {"id": 2, "name": "Counterpoint", "engine": "Engine_B_Avant", "midi_channel": 2},
        {"id": 3, "name": "Orchestra", "engine": "Engine_C_Orchestral", "midi_channel": 3},
        {"id": 4, "name": "Guitar", "engine": "Engine_D_GuitarModernism", "midi_channel": 4}
    ],
    "global_transformations": ["F2_Polychord", "F3_Polyrhythm"]
}

# 3. rc_transformations.json
rc_transformations = {
    "F2_Polychord_Generator": {
        "structures": [
            {"name": "Martino Minor", "formula": "Minor + Diminished"},
            {"name": "Lydian Stack", "formula": "Major + Major"},
            {"name": "Dorian Hex", "formula": "Major + Minor"},
            {"name": "Altered Hex", "formula": "Major + Augmented"}
        ]
    },
    "F3_Polyrhythm_Engine": {
        "ratios": ["3:2", "5:4", "2:3:4"],
        "pitch_pool": "Shared Triad Pair",
        "cluster_type": "Symmetrical (Dim/Aug)"
    }
}

# 4. the_score_playbackmap.json (Playback Map)
# Mapping instruments to Sonuscore The Score keyswitches/channels (hypothetical mapping)
the_score_map = {
    "map_name": "Bebop V3 Ensemble",
    "instruments": [
        {"name": "Flute", "channel": 1, "ks_sustain": "C0", "ks_staccato": "C#0"},
        {"name": "Clarinet in Bb", "channel": 2, "ks_sustain": "C0", "ks_staccato": "C#0"},
        {"name": "Flugelhorn", "channel": 3, "ks_sustain": "C0", "ks_staccato": "C#0"},
        {"name": "Violin I", "channel": 4, "ks_sustain": "C0", "ks_staccato": "C#0"},
        {"name": "Violin II", "channel": 5, "ks_sustain": "C0", "ks_staccato": "C#0"},
        {"name": "Viola", "channel": 6, "ks_sustain": "C0", "ks_staccato": "C#0"},
        {"name": "Cello", "channel": 7, "ks_sustain": "C0", "ks_staccato": "C#0"},
        {"name": "Electric Guitar", "channel": 8, "ks_sustain": "C0", "ks_staccato": "C#0"},
        {"name": "Piano", "channel": 9, "ks_sustain": "C0", "ks_staccato": "C#0"},
        {"name": "Double Bass", "channel": 10, "ks_sustain": "C0", "ks_pizz": "C#0"},
        {"name": "Light Percussion", "channel": 11, "map": "General MIDI"}
    ]
}

# 5. the_score_playbackmap.txt
the_score_txt = """
# The Score Playback Map for Bebop V3

1. Flute        - CH1
2. Clarinet     - CH2
3. Flugelhorn   - CH3
4. Violin I     - CH4
5. Violin II    - CH5
6. Viola        - CH6
7. Cello        - CH7
8. Elec Guitar  - CH8
9. Piano        - CH9
10. Bass        - CH10
11. Percussion  - CH11

# KeySwitches
Sustain: C0
Staccato: C#0
Pizzicato (Strings): D0
"""

# 6. README.md
readme_content = """# Bebop-Language Project V3.0 Rebuild

This folder contains the generated assets for the Bebop-Language Project V3.0 integration with Rapid Composer, The Score, and Sibelius.

## Files

1. **V3_RC_Presets_Full.json**: Definitions for Engines A, B, C, D.
2. **rc_liveset.json**: Live Set configuration for Rapid Composer.
3. **rc_transformations.json**: Transformation rules (Polychords, Polyrhythms).
4. **the_score_playbackmap.json**: Playback configuration for Sonuscore.
5. **small_jazz_orchestra_template.musicxml**: Empty template for the 11-piece ensemble.

## Usage

1. **Rapid Composer**: Import `V3_RC_Presets_Full.json` into your Custom Phrases/Browsers. Load `rc_liveset.json`.
2. **The Score**: Load the ensemble presets matching `the_score_playbackmap.json`.
3. **Sibelius**: Import `small_jazz_orchestra_template.musicxml` as your house style/template.

## Engines

*   **Engine A**: Bebop (Parker, Stitt, etc.)
*   **Engine B**: Avant (Shorter, Coltrane)
*   **Engine C**: Orchestral (Maria Schneider)
*   **Engine D**: Guitar Modernism (Metheny, Scofield)
"""

def write_file(filename, content):
    with open(filename, 'w') as f:
        if filename.endswith('.json'):
            json.dump(content, f, indent=2)
        else:
            f.write(content)
    print(f"Created {filename}")

def main():
    write_file("V3_RC_Presets_Full.json", rc_presets)
    write_file("rc_liveset.json", rc_liveset)
    write_file("rc_transformations.json", rc_transformations)
    write_file("the_score_playbackmap.json", the_score_map)
    write_file("the_score_playbackmap.txt", the_score_txt)
    write_file("README.md", readme_content)

if __name__ == "__main__":
    main()

