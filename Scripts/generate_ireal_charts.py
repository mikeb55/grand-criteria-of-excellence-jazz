"""
GCE Jazz Guitar Collection - iReal Pro Chart Generator
Generates iReal Pro format charts from the tune analysis Markdown files.
Output: HTML file with clickable import links for all 18 tunes.
"""

import re
import urllib.parse
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
MD_DIR = BASE_DIR / "Trio Tunes" / "MD"
OUTPUT_HTML = BASE_DIR / "GCE_iReal_Pro_Charts.html"

# Tune configurations (manually mapped from the analysis files)
TUNES = [
    {
        "file": "Tune_1_Blue_Cycle.md",
        "title": "Blue Cycle",
        "composer": "GCE Jazz",
        "style": "Blues",
        "key": "Bb",
        "tempo": 120,
        "time": "4/4",
        "chords": [
            "Bb7", "Eb7", "Bb7", "Fm7 Bb7",
            "Eb7", "Edim7", "Bb7", "G7",
            "Cm7", "F7", "Bb7 G7", "Cm7 F7"
        ]
    },
    {
        "file": "Tune_2_Orbit.md",
        "title": "Orbit",
        "composer": "GCE Jazz",
        "style": "Ballad",
        "key": "F",
        "tempo": 160,
        "time": "3/4",
        "chords": [
            "F^7#11", "Db^7", "Bbm7", "A^7",
            "F^7#11", "Eb^7#5", "Dm9", "E7alt",
            "Ab^7", "Gb13", "E^7", "Cm7 F7sus",
            "Bb^7", "Am7b5", "Gm11", " ",
            "F^7#11", "Db^7", "Bbm7", "A^7",
            "F^7#11", "Eb^7#5", "Dm9", "E7alt",
            "Db/F", "B^7#11", "Bb7sus", "Am9",
            "Ab^7#5", "Gm7", "F^9", " "
        ]
    },
    {
        "file": "Tune_3_Rust_and_Chrome.md",
        "title": "Rust And Chrome",
        "composer": "GCE Jazz",
        "style": "Funk",
        "key": "E",
        "tempo": 95,
        "time": "4/4",
        "chords": [
            "E9", "E9", "A13", "A13",
            "E9", "G9", "F#m7", "B7#9",
            "E9", "E9", "A13", "A13",
            "E9", "G9", "F#m7", "B7#9",
            "C#m7", "F#7#9", "Bm7", "E7#9",
            "A^7", "G#m7b5", "C#7alt", "B7sus B7",
            "E9", "E9", "A13", "A13",
            "E9", "G9", "F#m7", "B7#9"
        ]
    },
    {
        "file": "Tune_4_Sao_Paulo_Rain.md",
        "title": "Sao Paulo Rain",
        "composer": "GCE Jazz",
        "style": "Bossa Nova",
        "key": "D",
        "tempo": 130,
        "time": "4/4",
        "chords": [
            "D^9", "D^9", "Em9", "A13",
            "D^9", "F#m7", "Bm9", "E9",
            "D^9", "D^9", "Em9", "A13",
            "D^9", "F#m7", "Bm9", "E9",
            "Gm9", "Gm9", "Gb7#11", "F^7#11",
            "Em11", "Eb9#11", "D^9", "A7sus A7",
            "D^9", "D^9", "Em9", "A13",
            "D^9", "F#m7", "Bm9", "E9"
        ]
    },
    {
        "file": "Tune_5_The_Mirror.md",
        "title": "The Mirror",
        "composer": "GCE Jazz",
        "style": "Ballad",
        "key": "Ab",
        "tempo": 60,
        "time": "4/4",
        "chords": [
            "Ab^9", " ", "Fm9", "Db9#11",
            "Cm7", "Bbm11", "Ab^9/G", "Eb7sus",
            "Db^7#11", "Cm7b5", "Fm^7", "Bb7alt",
            "Eb^9", "Am7b5", "Ab^9", " ",
            "Ab^9", " ", "Fm9", "Db9#11",
            "Cm7", "Bbm11", "Ab^9/G", "Eb7sus",
            "Gb9", "F^7#5", "Bbm9", "Eb13",
            "Ab^9", "Db^7", "Ab^9/Eb", " "
        ]
    },
    {
        "file": "Tune_6_Bright_Size_Life_2.md",
        "title": "Bright Size Life 2",
        "composer": "GCE Jazz",
        "style": "Even 8ths",
        "key": "D",
        "tempo": 145,
        "time": "4/4",
        "chords": [
            "D/A", "E/A", "F#m/A", "G/A",
            "D/A", "Bm/A", "G^7/A", "A",
            "D/A", "E/A", "F#m/A", "G/A",
            "D/A", "Bm/A", "G^7/A", "A",
            "Bm7", "E9", "Asus A", "D^7",
            "Gm9", "C9", "F#m7", "E7sus E7",
            "D/A", "E/A", "F#m/A", "G/A",
            "D/A", "Bm/A", "G^7/A", "D"
        ]
    },
    {
        "file": "Tune_7_Monks_Dream.md",
        "title": "Monks Dream",
        "composer": "GCE Jazz",
        "style": "Medium Swing",
        "key": "C",
        "tempo": 110,
        "time": "4/4",
        "chords": [
            "C^7#11", " ", "D7#11", " ",
            "Ebo7", "Dm7", "G7#5", "C^7",
            "C^7#11", " ", "D7#11", " ",
            "Ebo7", "Dm7", "G7#5", "C^7",
            "Ab7#11", " ", "Gb7#11", "F^7#5",
            "Fm6", "Em7b5", "Eb7", "Dm7 G7",
            "C^7#11", " ", "D7#11", " ",
            "Ebo7", "Dm7", "G7#5", "C^7"
        ]
    },
    {
        "file": "Tune_8_Nefertitis_Shadow.md",
        "title": "Nefertitis Shadow",
        "composer": "GCE Jazz",
        "style": "Up Tempo Swing",
        "key": "Eb",
        "tempo": 180,
        "time": "4/4",
        "chords": [
            "Eb^7#11", "Db^7", "Cm9", "Ab^7#5",
            "Gm7b5", "Gb^7", "Fm11", "Eo7",
            "Eb^9", "D7alt", "Db^7#11", "Cm^7",
            "Bm9", "Bb^7#5", "Am7b5", "Ab^7",
            "Gm9", "Gb7#9", "Fm9", "E^7",
            "Eb^7", "D^7#11", "Db^9", "Eb^7"
        ]
    },
    {
        "file": "Tune_9_Greezy.md",
        "title": "Greezy",
        "composer": "GCE Jazz",
        "style": "Blues",
        "key": "G",
        "tempo": 100,
        "time": "4/4",
        "chords": [
            "G7", "G7", "G7", "G#o7",
            "C9", "C#o7", "G7", "E7#9",
            "Am7", "D7#9", "G7 E7", "Am7 D7"
        ]
    },
    {
        "file": "Tune_10_Hexagon.md",
        "title": "Hexagon",
        "composer": "GCE Jazz",
        "style": "Even 8ths",
        "key": "B",
        "tempo": 135,
        "time": "5/4",
        "chords": [
            "B^7", "C#m9", "D#m7", "E^7#11",
            "B^7/F#", "G#m9", "F#13sus", "F#7",
            "B^7", "C#m9", "D#m7", "E^7#11",
            "B^7/F#", "G#m9", "F#13sus", "F#7",
            "G^7#11", "F#m7b5", "E^7", "Eb7alt",
            "D#m9", "D^7#11", "C#m11", "F#7sus F#7",
            "B^7", "C#m9", "D#m7", "E^7#11",
            "B^7/F#", "G#m9", "F#13sus", "B^9"
        ]
    },
    {
        "file": "Tune_11_Crystal_Silence.md",
        "title": "Crystal Silence",
        "composer": "GCE Jazz",
        "style": "Ballad",
        "key": "A",
        "tempo": 80,
        "time": "4/4",
        "chords": [
            "A^9", "A^9", "F#m11", "D^7#11",
            "C#m9", "Bm9", "A^9/E", "E9sus",
            "F^7#11", "Em9", "D^9", "Db^7",
            "C#m7", "C^7#11", "Bm11", "E7sus",
            "A^9", "A^9", "F#m11", "D^7#11",
            "C#m9", "Bm9", "A^9/E", "E9sus",
            "Gb^7", "F#m9", "E^7", "Eb7#11",
            "D^9", "C#m7", "A^9", " "
        ]
    },
    {
        "file": "Tune_12_Angular_Motion.md",
        "title": "Angular Motion",
        "composer": "GCE Jazz",
        "style": "Up Tempo Swing",
        "key": "Gb",
        "tempo": 200,
        "time": "4/4",
        "chords": [
            "Gb^7", "Fm7 Bb7", "Eb^7", "Ebm7 Ab7",
            "Db^7", "Cm7b5 F7", "Bbm7", "Eb7 Ab7",
            "Gb^7", "Fm7 Bb7", "Eb^7", "Ebm7 Ab7",
            "Db^7", "Cm7b5 F7", "Bbm7", "Eb7 Ab7",
            "Dbm7", "Gb7", "Cb^7", "Bbm7",
            "Abm7", "Db7", "Gb^7", "Cm7b5 F7alt",
            "Gb^7", "Fm7 Bb7", "Eb^7", "Ebm7 Ab7",
            "Db^7", "Cm7b5 F7", "Bbm7", "Gb^7"
        ]
    },
    {
        "file": "Tune_13_The_Void.md",
        "title": "The Void",
        "composer": "GCE Jazz",
        "style": "Free",
        "key": "C",
        "tempo": 0,
        "time": "4/4",
        "chords": [
            " ", " ", " ", " ",
            " ", " ", " ", " ",
            " ", " ", " ", " ",
            " ", " ", " ", " "
        ]
    },
    {
        "file": "Tune_14_Solar_Flare.md",
        "title": "Solar Flare",
        "composer": "GCE Jazz",
        "style": "Even 8ths",
        "key": "C#",
        "tempo": 150,
        "time": "7/8",
        "chords": [
            "C#^7", "D#m9", "E#m7", "F#^7#11",
            "G#m7", "A#m7", "B#o7", " ",
            "C#^7", "D#m9", "E#m7", "F#^7#11",
            "G#m7", "A#m7", "B#o7", " ",
            "A^7#11", "G#m7b5", "F#m9", "F7#9",
            "E^7", "Eb7alt", "D#m11", " ",
            "C#^7", "D#m9", "E#m7", "F#^7#11",
            "G#m7", "A#m7", "B#o7", "C#^9"
        ]
    },
    {
        "file": "Tune_15_Final_Departure.md",
        "title": "Final Departure",
        "composer": "GCE Jazz",
        "style": "Ballad",
        "key": "Db",
        "tempo": 70,
        "time": "4/4",
        "chords": [
            "Db^9", "Bbm9", "Ebm9", "Ab13",
            "Db^9", "Gb^7#11", "Fm7", "Bb7sus Bb7",
            "Db^9", "Bbm9", "Ebm9", "Ab13",
            "Db^9", "Gb^7#11", "Fm7", "Bb7sus Bb7",
            "Bm9", "E^7#11", "Eb^9", "Ab^7",
            "Gm7b5", "C7alt", "Fm9", "Bb7sus",
            "Db^9", "Bbm9", "Ebm9", "Ab13",
            "Db^9", "Gb^7#11", "Fm7", "Db^9"
        ]
    },
    {
        "file": "Tune_16_Bop_Burner.md",
        "title": "Bop Burner",
        "composer": "GCE Jazz",
        "style": "Up Tempo Swing",
        "key": "F",
        "tempo": 240,
        "time": "4/4",
        "chords": [
            "F^7", "Em7b5 A7", "Dm7", "G7",
            "Gm7", "C7", "F^7", "Gm7 C7",
            "F^7", "Em7b5 A7", "Dm7", "G7",
            "Gm7", "C7", "F^7", "Gm7 C7",
            "Cm7", "F7", "Bb^7", "Bbm7 Eb7",
            "Am7", "D7", "Gm7", "C7",
            "F^7", "Em7b5 A7", "Dm7", "G7",
            "Gm7", "C7", "F^7", "Gm7 C7"
        ]
    },
    {
        "file": "Tune_17_Blue_Minor.md",
        "title": "Blue Minor",
        "composer": "GCE Jazz",
        "style": "Medium Swing",
        "key": "C-",
        "tempo": 180,
        "time": "4/4",
        "chords": [
            "Cm^7", "Cm6", "Fm9", "Fm6",
            "Dm7b5", "G7alt", "Cm^7", "Dm7b5 G7",
            "Cm^7", "Cm6", "Fm9", "Fm6",
            "Dm7b5", "G7alt", "Cm^7", "Dm7b5 G7",
            "Eb^7", "Ab^7", "Dm7b5", "Db7#11",
            "Cm9", "Bb7#9", "Ab^7", "G7alt",
            "Cm^7", "Cm6", "Fm9", "Fm6",
            "Dm7b5", "G7alt", "Cm^7", "Dm7b5 G7"
        ]
    },
    {
        "file": "Tune_18_Epistrophy_2.md",
        "title": "Epistrophy 2",
        "composer": "GCE Jazz",
        "style": "Medium Swing",
        "key": "Db",
        "tempo": 120,
        "time": "4/4",
        "chords": [
            "Db7#9", "D7#9", "Db7#9", "D7#9",
            "Eb7#9", "E7#9", "Eb7#9", " ",
            "Db7#9", "D7#9", "Db7#9", "D7#9",
            "Eb7#9", "E7#9", "Eb7#9", " ",
            "Gb^7#11", "Fm7", "Ebm9", "Ab7sus",
            "Db^7", "Dm7b5", "Gb^7", "Ab7",
            "Db7#9", "D7#9", "Db7#9", "D7#9",
            "Eb7#9", "E7#9", "Eb7#9", "Db^7"
        ]
    },
]


def encode_ireal_chord(chord):
    """Convert a chord symbol to iReal Pro format."""
    if not chord or chord.strip() == "":
        return " "
    
    # Clean up the chord
    chord = chord.strip()
    
    # Map chord qualities to iReal Pro format
    replacements = [
        ("^7#11", "^7#11"),
        ("^7#5", "^7#5"),
        ("^9", "^9"),
        ("^7", "^7"),
        ("^", "^7"),
        ("m7b5", "h7"),
        ("m^7", "-^7"),
        ("m9", "-9"),
        ("m11", "-11"),
        ("m7", "-7"),
        ("m6", "-6"),
        ("m", "-"),
        ("7#9", "7#9"),
        ("7#11", "7#11"),
        ("7alt", "7alt"),
        ("7sus", "7sus"),
        ("7b9", "7b9"),
        ("9#11", "9#11"),
        ("13sus", "13sus"),
        ("13", "13"),
        ("9sus", "9sus"),
        ("9", "9"),
        ("o7", "o7"),
        ("o", "o"),
        ("sus", "sus"),
    ]
    
    result = chord
    for old, new in replacements:
        if old in result:
            result = result.replace(old, new)
            break
    
    return result


def generate_ireal_url(tune):
    """Generate an iReal Pro URL for a single tune."""
    title = tune["title"]
    composer = tune["composer"]
    style = tune["style"]
    key = tune["key"]
    
    # Build chord string
    chord_str = ""
    bars_per_line = 4
    
    for i, chord in enumerate(tune["chords"]):
        # Handle two chords in one bar
        if " " in chord and chord.strip() != "":
            parts = chord.split()
            if len(parts) == 2:
                c1 = encode_ireal_chord(parts[0])
                c2 = encode_ireal_chord(parts[1])
                chord_str += f"{c1} {c2}|"
            else:
                chord_str += f"{encode_ireal_chord(chord)}|"
        else:
            chord_str += f"{encode_ireal_chord(chord)}|"
        
        # Add line break every 4 bars
        if (i + 1) % bars_per_line == 0:
            chord_str += "\n"
    
    # Build the iReal Pro URL
    # Format: irealb://[title]=[composer]=[style]=[key]=n=[chords]
    
    # Encode the chord data for URL
    # iReal uses specific encoding
    encoded_chords = chord_str.replace("\n", "")
    
    # Build URL components
    url_data = f"{title}={composer}={style}={key}=n={encoded_chords}"
    
    # URL encode
    encoded_url = urllib.parse.quote(url_data, safe="")
    
    return f"irealb://{encoded_url}"


def generate_html_output(tunes):
    """Generate HTML file with all iReal Pro links."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCE Jazz Guitar - iReal Pro Charts</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 40px;
            font-size: 1.1rem;
        }
        .instructions {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #00d4ff;
        }
        .instructions h3 { color: #00d4ff; margin-bottom: 10px; }
        .instructions ol { padding-left: 20px; }
        .instructions li { margin: 8px 0; color: #aaa; }
        .tune-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }
        .tune-card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .tune-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 30px rgba(0,212,255,0.2);
        }
        .tune-num {
            display: inline-block;
            background: linear-gradient(135deg, #00d4ff, #7b2cbf);
            color: #fff;
            font-weight: bold;
            width: 32px;
            height: 32px;
            line-height: 32px;
            text-align: center;
            border-radius: 50%;
            margin-bottom: 10px;
        }
        .tune-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .tune-meta {
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 15px;
        }
        .tune-meta span {
            display: inline-block;
            margin-right: 15px;
        }
        .import-btn {
            display: inline-block;
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: #fff;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            transition: opacity 0.2s;
        }
        .import-btn:hover { opacity: 0.9; }
        .import-all {
            display: block;
            width: 100%;
            text-align: center;
            background: linear-gradient(135deg, #7b2cbf, #5a189a);
            color: #fff;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: bold;
            margin-top: 30px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎸 GCE JAZZ GUITAR</h1>
        <p class="subtitle">iReal Pro Chart Collection — 18 Tunes</p>
        
        <div class="instructions">
            <h3>📱 How to Import into iReal Pro</h3>
            <ol>
                <li>Make sure iReal Pro is installed on your device</li>
                <li>Click any "Import to iReal Pro" button below</li>
                <li>iReal Pro will open automatically with the chart</li>
                <li>Save the chart to your library</li>
            </ol>
        </div>
        
        <div class="tune-grid">
"""
    
    for i, tune in enumerate(tunes, 1):
        url = generate_ireal_url(tune)
        html += f"""
            <div class="tune-card">
                <div class="tune-num">{i}</div>
                <div class="tune-title">{tune['title']}</div>
                <div class="tune-meta">
                    <span>🎵 {tune['style']}</span>
                    <span>🔑 {tune['key']}</span>
                    <span>⏱️ {tune['time']}</span>
                </div>
                <a href="{url}" class="import-btn">Import to iReal Pro</a>
            </div>
"""
    
    # Generate playlist URL (all tunes combined)
    all_tunes_data = []
    for tune in tunes:
        url = generate_ireal_url(tune)
        all_tunes_data.append(url.replace("irealb://", ""))
    
    playlist_url = "irealb://" + "===".join(all_tunes_data)
    
    html += f"""
        </div>
        
        <a href="{playlist_url}" class="import-all">
            📥 Import ALL 18 Tunes as Playlist
        </a>
        
        <p class="footer">
            GCE Jazz Guitar Collection • Grand Criteria of Excellence<br>
            Generated for iReal Pro
        </p>
    </div>
</body>
</html>
"""
    
    return html


def main():
    print("GCE Jazz - iReal Pro Chart Generator")
    print("=" * 40)
    
    # Generate HTML
    print(f"  Processing {len(TUNES)} tunes...")
    html_content = generate_html_output(TUNES)
    
    # Write output
    print(f"  Writing HTML file...")
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n  File: {OUTPUT_HTML}")
    print(f"  Size: {OUTPUT_HTML.stat().st_size / 1024:.1f} KB")
    print()


if __name__ == "__main__":
    main()
    print("Job done Mike!")

