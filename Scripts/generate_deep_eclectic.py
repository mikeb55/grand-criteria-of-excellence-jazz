import xml.etree.ElementTree as ET
import random

# Source Setup
OUTPUT_FILE = "Works/Wonderland_Deep_Eclectic.musicxml"

# 11 Parts + Drums
PARTS = [
    {"id": "P1", "name": "Alto Sax 1 (Lead)", "midi": 66},
    {"id": "P2", "name": "Alto Sax 2", "midi": 66},
    {"id": "P3", "name": "Tenor Sax 1", "midi": 67},
    {"id": "P4", "name": "Tenor Sax 2", "midi": 67},
    {"id": "P5", "name": "Bari Sax", "midi": 68},
    {"id": "P6", "name": "Trumpet 1", "midi": 57},
    {"id": "P7", "name": "Trombone 1", "midi": 58},
    {"id": "P8", "name": "Guitar", "midi": 27},
    {"id": "P9", "name": "Piano", "midi": 1},
    {"id": "P10", "name": "Bass", "midi": 33},
    {"id": "P11", "name": "Drums", "midi": 119} # Kit
]

# COMPOSER LOGIC FUNCTIONS

def create_note(step, octave, duration, type_str, accidental=None, dot=False, tie=None, articulation=None):
    n = ET.Element("note")
    p = ET.SubElement(n, "pitch")
    ET.SubElement(p, "step").text = step
    ET.SubElement(p, "octave").text = str(octave)
    if accidental:
        ET.SubElement(p, "alter").text = "1" if accidental == "sharp" else "-1"
        ET.SubElement(n, "accidental").text = accidental
    
    ET.SubElement(n, "duration").text = str(duration)
    ET.SubElement(n, "type").text = type_str
    if dot: ET.SubElement(n, "dot")
    
    if tie:
        ET.SubElement(n, "tie", type=tie)
        notations = ET.SubElement(n, "notations")
        ET.SubElement(notations, "tied", type=tie)

    if articulation:
        notations = n.find("notations")
        if notations is None: notations = ET.SubElement(n, "notations")
        arts = notations.find("articulations")
        if arts is None: arts = ET.SubElement(notations, "articulations")
        ET.SubElement(arts, articulation)
        
    return n

def create_rest(duration, type_str):
    n = ET.Element("note")
    ET.SubElement(n, "rest")
    ET.SubElement(n, "duration").text = str(duration)
    ET.SubElement(n, "type").text = type_str
    return n

# --- GENERATION LOGIC PER COMPOSER ---

def gen_gil_evans(part_idx, m):
    # Lush, parallel planing. Long tones.
    # Chord: m1 Cmaj9 -> m2 Dbmaj9 (Planing)
    # Voicing: 5-part spread
    
    notes = []
    if part_idx == 0: # Lead Alto
        # Melody: E (m1) -> F (m2)
        step = "E" if m % 2 != 0 else "F"
        notes.append(create_note(step, 5, 8, "whole"))
    elif part_idx in [1, 2, 3, 4]: # Saxes / Horns
        # Harmony tones
        offsets = {1: ("B", 4), 2: ("G", 4), 3: ("D", 5), 4: ("C", 4)}
        step, oct = offsets.get(part_idx, ("C", 4))
        if m % 2 == 0: # Shift up semitone
            # Simple logic shift for demo
            notes.append(create_note(step, oct, 8, "whole", accidental="sharp")) # approx shift
        else:
            notes.append(create_note(step, oct, 8, "whole"))
    elif part_idx == 10: # Drums (Brushes)
         # Brush Stir
         notes.append(create_rest(8, "whole"))
    else:
         notes.append(create_rest(8, "whole"))
    return notes

def gen_charlie_parker(part_idx, m):
    # BEBOP: Fast 16th note runs, chromaticism
    notes = []
    if part_idx == 0: # Lead Alto Solo
        # Lick: C D D# E G A Bb B (Enclosure to C)
        # 16th notes (duration 0.5 in div 2? No, div=2 means quarter=2. So 16th = 0.5. Need div=4)
        # Let's use 8th note triplet runs for Parker speed feel in 4/4 at div=2
        # Actually, simple run:
        if m % 2 != 0:
            # Run Up
            scale = [("C",5), ("D",5), ("D",5,"sharp"), ("E",5), ("G",5), ("A",5), ("B",5,"flat"), ("B",5,"natural")]
            for s in scale:
                step = s[0]
                oct = s[1]
                acc = s[2] if len(s)>2 else None
                notes.append(create_note(step, oct, 1, "eighth", accidental=acc))
        else:
            # Arpeggio Down
            arp = [("C",6), ("G",5), ("E",5), ("C",5)]
            for x in arp:
                notes.append(create_note(x[0], x[1], 2, "quarter"))
    elif part_idx == 9: # Bass (Walking)
        # Walk 4 quarter notes
        bass_line = ["C", "E", "G", "A"]
        for b in bass_line:
            notes.append(create_note(b, 3, 2, "quarter"))
    elif part_idx == 10: # Drums (Swing)
        # Ride pattern
        for _ in range(4):
             n = ET.Element("note")
             p = ET.SubElement(n, "unpitched")
             ET.SubElement(p, "display-step").text = "G"
             ET.SubElement(p, "display-octave").text = "5"
             ET.SubElement(n, "duration").text = "2"
             ET.SubElement(n, "type").text = "quarter"
             notes.append(n)
    else: # Comping Piano/Guitar
        if m % 2 == 0:
            notes.append(create_rest(2, "quarter"))
            # Stab
            notes.append(create_note("E", 4, 2, "quarter", articulation="staccato"))
            notes.append(create_rest(4, "half"))
        else:
            notes.append(create_rest(8, "whole"))
            
    return notes

def gen_monk(part_idx, m):
    # ANGULAR: Whole tone, clusters, silence
    notes = []
    if part_idx == 8: # Piano (Monk)
        if m % 2 != 0:
            # Cluster: E + F
            n = create_note("E", 4, 2, "quarter", articulation="accent")
            # Add chord tone F manually (xml chord) - simplified to melody here
            notes.append(n)
            r = create_rest(6, "half")
            ET.SubElement(r, "dot")
            notes.append(r)
    elif part_idx == 0: # Sax (Melody)
        # Whole tone run: C D E F# G# Bb
        if m % 2 == 0:
            notes.append(create_note("C", 5, 2, "quarter"))
            notes.append(create_note("D", 5, 2, "quarter"))
            notes.append(create_note("F", 5, 2, "quarter", accidental="sharp"))
            notes.append(create_note("G", 5, 2, "quarter", accidental="sharp"))
        else:
            notes.append(create_rest(8, "whole"))
    elif part_idx == 10: # Drums (Disjointed)
        # Kicks on random beats
        notes.append(create_rest(2, "quarter"))
        n = ET.Element("note")
        p = ET.SubElement(n, "unpitched")
        ET.SubElement(p, "display-step").text = "F" # Snare
        ET.SubElement(p, "display-octave").text = "4"
        ET.SubElement(n, "duration").text = "2"
        ET.SubElement(n, "type").text = "quarter"
        notes.append(n)
        notes.append(create_rest(4, "half"))
    else:
        notes.append(create_rest(8, "whole"))
    return notes

def gen_scofield(part_idx, m):
    # FUSION: 7/4, angular, funk
    notes = []
    if part_idx == 7: # Guitar (Sco)
        # Angular Lick
        notes.append(create_note("E", 4, 1, "eighth")) # 0.5
        notes.append(create_note("F", 4, 1, "eighth")) # 0.5
        notes.append(create_note("Bb", 4, 1, "eighth", accidental="flat"))
        notes.append(create_note("A", 4, 1, "eighth"))
        notes.append(create_note("Db", 5, 2, "quarter", accidental="flat")) # Out
        notes.append(create_note("C", 5, 2, "quarter")) # In
        notes.append(create_rest(6, "half")) # Rest of 7/4?
        # 1+1+1+1+2+2 = 8. Need 14 for 7/4. 14-8=6.
    elif part_idx == 9: # Bass (Ostinato)
        # 7/4 Riff
        notes.append(create_note("C", 3, 2, "quarter"))
        notes.append(create_note("Bb", 2, 2, "quarter", accidental="flat"))
        notes.append(create_note("A", 2, 2, "quarter"))
        notes.append(create_note("F", 2, 2, "quarter"))
        notes.append(create_note("G", 2, 2, "quarter"))
        notes.append(create_note("Bb", 2, 2, "quarter", accidental="flat"))
        notes.append(create_note("C", 3, 2, "quarter"))
    elif part_idx == 10: # Drums (Funk)
         notes.append(create_rest(14, "whole")) # Placeholder for complex funk
    else:
         notes.append(create_rest(14, "whole"))
    return notes

def main():
    root = ET.Element("score-partwise", version="3.1")
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = "Wonderland: Deep Eclectic Suite"
    
    part_list = ET.SubElement(root, "part-list")
    for p in PARTS:
        sp = ET.SubElement(part_list, "score-part", id=p["id"])
        ET.SubElement(sp, "part-name").text = p["name"]
        si = ET.SubElement(sp, "score-instrument", id=f"{p['id']}-I1")
        ET.SubElement(si, "instrument-name").text = p["name"]
        mi = ET.SubElement(sp, "midi-instrument", id=f"{p['id']}-I1")
        ET.SubElement(mi, "midi-program").text = str(p["midi"])

    # Generate Measures 1-54
    for i, p in enumerate(PARTS):
        part = ET.SubElement(root, "part", id=p["id"])
        
        for m in range(1, 55):
            measure = ET.SubElement(part, "measure", number=str(m))
            
            # Time Sig Changes & Rehearsal Marks
            if m == 1:
                attr = ET.SubElement(measure, "attributes")
                divs = ET.SubElement(attr, "divisions")
                divs.text = "2" # Quarter = 2, Eighth = 1
                key = ET.SubElement(attr, "key")
                ET.SubElement(key, "fifths").text = "0"
                time = ET.SubElement(attr, "time")
                ET.SubElement(time, "beats").text = "4"
                ET.SubElement(time, "beat-type").text = "4"
                if i == 9: # Bass
                    clef = ET.SubElement(attr, "clef")
                    ET.SubElement(clef, "sign").text = "F"
                    ET.SubElement(clef, "line").text = "4"
                # Add Rehearsal Mark for Start
                if i == 0: # Lead Part Only
                     d = ET.SubElement(measure, "direction", placement="above")
                     dt = ET.SubElement(d, "direction-type")
                     ET.SubElement(dt, "rehearsal").text = "A - Gil Evans"

            if m == 10:
                 if i == 0:
                     d = ET.SubElement(measure, "direction", placement="above")
                     dt = ET.SubElement(d, "direction-type")
                     ET.SubElement(dt, "rehearsal").text = "B - Charlie Parker"

            if m == 19:
                 if i == 0:
                     d = ET.SubElement(measure, "direction", placement="above")
                     dt = ET.SubElement(d, "direction-type")
                     ET.SubElement(dt, "rehearsal").text = "C - Monk"

            if m == 28: # Scofield Section (7/4)
                attr = ET.SubElement(measure, "attributes")
                time = ET.SubElement(attr, "time")
                ET.SubElement(time, "beats").text = "7"
                ET.SubElement(time, "beat-type").text = "4"
                if i == 0:
                     d = ET.SubElement(measure, "direction", placement="above")
                     dt = ET.SubElement(d, "direction-type")
                     ET.SubElement(dt, "rehearsal").text = "D - Scofield"

            if m == 37: # ECM (Back to 4/4)
                attr = ET.SubElement(measure, "attributes")
                time = ET.SubElement(attr, "time")
                ET.SubElement(time, "beats").text = "4"
                ET.SubElement(time, "beat-type").text = "4"
                if i == 0:
                     d = ET.SubElement(measure, "direction", placement="above")
                     dt = ET.SubElement(d, "direction-type")
                     ET.SubElement(dt, "rehearsal").text = "E - ECM"
            
            # CONTENT GENERATION
            notes = []
            if 1 <= m <= 9:
                notes = gen_gil_evans(i, m)
            elif 10 <= m <= 18:
                notes = gen_charlie_parker(i, m)
            elif 19 <= m <= 27:
                notes = gen_monk(i, m)
            elif 28 <= m <= 36:
                notes = gen_scofield(i, m)
            # ... others ...
            else:
                 notes = [create_rest(8, "whole")] # Filler

            for n in notes:
                measure.append(n)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(OUTPUT_FILE, encoding="UTF-8", xml_declaration=True)
    print("Done.")

if __name__ == "__main__":
    main()

