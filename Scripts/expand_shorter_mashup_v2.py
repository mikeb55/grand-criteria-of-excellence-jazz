import xml.etree.ElementTree as ET
import math
import random
import copy

# --- CONFIGURATION ---
SOURCE_FILE = "Works/V1 0-Shorter-Mash-up.musicxml"
OUTPUT_XML = "Works/V7_Wonderland_Orchestral_Shorter_Expanded.musicxml"
OUTPUT_MIDI = "Works/V7_Wonderland_Orchestral_Shorter_Expanded.mid"

# Wayne Shorter / Maria Schneider Palette
ZONES = {
    "A": {"range": (1, 16), "root": "C", "scale": "Mixolydian", "pedal": True, "mood": "Cryptic"},
    "B": {"range": (17, 24), "root": "B", "scale": "Super Locrian", "pedal": False, "mood": "Tension"},
    "C": {"range": (25, 48), "root": "F", "scale": "Lydian", "pedal": False, "mood": "Flight"}
}

INSTRUMENTS = {
    "P1": {"name": "Flute", "midi": 73, "clef": "G", "role": "Melody_High"},
    "P2": {"name": "Clarinet", "midi": 71, "clef": "G", "role": "Melody_Mid"},
    "P3": {"name": "Flugelhorn", "midi": 56, "clef": "G", "role": "Melody_Lead"},
    "P4": {"name": "Violin I", "midi": 40, "clef": "G", "role": "Counterpoint_High"},
    "P5": {"name": "Violin II", "midi": 40, "clef": "G", "role": "Counterpoint_Mid"},
    "P6": {"name": "Viola", "midi": 41, "clef": "C", "role": "Pad_Inner"},
    "P7": {"name": "Cello", "midi": 42, "clef": "F", "role": "Bass_Counter"},
    "P8": {"name": "Guitar", "midi": 27, "clef": "G", "role": "Color_Ambient"},
    "P9": {"name": "Piano", "midi": 0, "clef": "G", "role": "Comping_Quartal"},
    "P10": {"name": "Bass", "midi": 32, "clef": "F", "role": "Bass_Anchor"},
    "P11": {"name": "Percussion", "midi": 118, "clef": "percussion", "role": "Color_Rhythm"}
}

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def midi_to_pitch(midi_val):
    step = NOTE_NAMES[midi_val % 12].replace("#", "")
    octave = (midi_val // 12) - 1
    alter = 1 if "#" in NOTE_NAMES[midi_val % 12] else 0
    return step, octave, alter

class Motif:
    def __init__(self, intervals, durations):
        self.intervals = intervals # Relative steps
        self.durations = durations # In divisions
    
    def transpose(self, semitones):
        # Not strictly applicable to relative intervals unless we store absolute, 
        # but here we just use this to modify the starting pitch later.
        pass 

class Generator:
    def __init__(self):
        self.divisions = 256
        self.source_motif = [] # List of (midi, duration)

    def parse_source(self):
        try:
            tree = ET.parse(SOURCE_FILE)
            root = tree.getroot()
            
            # Extract from P1 (Alto Sax) - Assuming it has the main theme
            # We want to find the "Shape" to develop
            part = root.find(".//part[@id='P1']")
            if not part: part = root.find("part")
            
            notes = []
            for m in part.findall("measure")[:8]: # First 8 bars for motif
                for n in m.findall("note"):
                    if n.find("rest") is None:
                        step = n.find("pitch/step").text
                        octave = int(n.find("pitch/octave").text)
                        alter = int(n.find("pitch/alter").text) if n.find("pitch/alter") is not None else 0
                        dur = int(n.find("duration").text)
                        midi = (NOTE_NAMES.index(step) + (octave+1)*12) + alter
                        notes.append((midi, dur))
            
            # Simplify to core motif (remove short passing tones?)
            # For now, take the first 4 significant notes
            if notes:
                self.source_motif = notes # Keep all for now
                print(f"Extracted motif: {len(notes)} notes")
                
        except Exception as e:
            print(f"Error parsing source: {e}")
            # Fallback motif (Shorter-esque)
            # C - Eb - F - B (m3, M2, tritone)
            self.source_motif = [(72, 256), (75, 256), (77, 512), (83, 1024)] 

    def get_scale_notes(self, root_name, scale_type):
        root_val = NOTE_NAMES.index(root_name)
        if scale_type == "Mixolydian":
            intervals = [0, 2, 4, 5, 7, 9, 10] # C D E F G A Bb
        elif scale_type == "Super Locrian": # Altered
            intervals = [0, 1, 3, 4, 6, 8, 10] # B C D Eb F G A
        elif scale_type == "Lydian":
            intervals = [0, 2, 4, 6, 7, 9, 11] # F G A B C D E
        
        return [(root_val + i) % 12 for i in intervals]

    def generate_xml(self):
        root = ET.Element("score-partwise", version="3.1")
        work = ET.SubElement(root, "work")
        ET.SubElement(work, "work-title").text = "Wonderland: Shorter Orchestral Expansion V7"
        
        part_list = ET.SubElement(root, "part-list")
        for pid, info in INSTRUMENTS.items():
            sp = ET.SubElement(part_list, "score-part", id=pid)
            ET.SubElement(sp, "part-name").text = info["name"]

        parts_data = {pid: [] for pid in INSTRUMENTS}
        
        # GENERATION LOOP
        for bar in range(1, 49):
            # Identify Zone
            zone_name = "A"
            if 17 <= bar <= 24: zone_name = "B"
            if 25 <= bar <= 48: zone_name = "C"
            zone = ZONES[zone_name]
            
            scale_notes = self.get_scale_notes(zone["root"], zone["scale"])
            
            # Create Measures
            for pid, info in INSTRUMENTS.items():
                m = ET.Element("measure", number=str(bar))
                
                # Attributes (Bar 1)
                if bar == 1:
                    attr = ET.SubElement(m, "attributes")
                    divs = ET.SubElement(attr, "divisions")
                    divs.text = str(self.divisions)
                    k = ET.SubElement(attr, "key")
                    ET.SubElement(k, "fifths").text = "0"
                    t = ET.SubElement(attr, "time")
                    ET.SubElement(t, "beats").text = "4"
                    ET.SubElement(t, "beat-type").text = "4"
                    c = ET.SubElement(attr, "clef")
                    sign = "G"
                    line = "2"
                    if info["clef"] == "F": sign = "F"; line = "4"
                    if info["clef"] == "C": sign = "C"; line = "3"
                    if info["clef"] == "percussion": sign = "percussion"; line = "2"
                    ET.SubElement(c, "sign").text = sign
                    ET.SubElement(c, "line").text = line

                # Rehearsal Marks
                if bar == 1 or bar == 17 or bar == 25:
                    direct = ET.SubElement(m, "direction", placement="above")
                    dt = ET.SubElement(direct, "direction-type")
                    reh = ET.SubElement(dt, "rehearsal")
                    reh.text = zone_name
                    
                notes_to_write = [] # (midi, dur, type, tie_start, tie_stop)
                
                # --- LOGIC ---
                
                # 1. MELODY (Winds) - Developed
                if pid in ["P1", "P3"]: # Flute, Flugel
                    if bar <= 16: # Zone A: Sparse Shorter Motif
                        if bar % 4 == 1: # Every 4 bars
                            # Play motif transposed
                            base_pitch = 72 + (12 if pid == "P1" else 0)
                            notes_to_write.append((base_pitch, self.divisions, "quarter", False, False)) # C
                            notes_to_write.append((base_pitch+3, self.divisions, "quarter", False, False)) # Eb
                            notes_to_write.append((base_pitch+5, self.divisions*2, "half", False, False)) # F (Sus)
                        else:
                            notes_to_write.append((-1, self.divisions*4, "whole", False, False))
                    elif 17 <= bar <= 24: # Zone B: Tension
                        # Chromatic angular lines
                        base = 71 if pid == "P3" else 83
                        notes_to_write.append((base, self.divisions, "quarter", False, False))
                        notes_to_write.append((base-1, self.divisions, "quarter", False, False))
                        notes_to_write.append((base+3, self.divisions, "quarter", False, False))
                        notes_to_write.append((base+6, self.divisions, "quarter", False, False)) # Tritone
                    else: # Zone C: Lydian Melody (Schneider)
                        # Long soaring notes
                        target = 78 if pid == "P3" else 90 # F# (#11)
                        notes_to_write.append((target, self.divisions*4, "whole", False, False))
                
                # 2. COUNTERPOINT (Strings)
                elif pid in ["P4", "P5"]: # Violins
                    if zone_name == "A":
                        # Sustained harmonics/pads but with movement
                        # V1 moves, V2 holds
                        root_midi = 72 if pid == "P4" else 67 # C5 / G4
                        if bar % 2 == 0: # Move
                            notes_to_write.append((root_midi, self.divisions*2, "half", False, False))
                            notes_to_write.append((root_midi-2, self.divisions*2, "half", False, False)) # Bb (7th)
                        else:
                            notes_to_write.append((root_midi, self.divisions*4, "whole", True, True)) # Tie potentially
                    elif zone_name == "B":
                         # Tremolo clusters
                         base = 71 # B
                         notes_to_write.append((base + (3 if pid=="P4" else 10), self.divisions*4, "whole", False, False))
                    else:
                         # Arpeggiated background
                         arp = [0, 4, 7, 11] # Fmaj7
                         idx = (bar * 4) % 4
                         note = 65 + arp[idx] + (12 if pid=="P4" else 0)
                         notes_to_write.append((note, self.divisions*4, "whole", False, False))

                # 3. PIANO (Quartal)
                elif pid == "P9":
                    if zone_name == "A":
                        # McCoy Tyner 4ths: F - Bb - Eb
                        # Sparse: only on bar 1 and 3 of 4-bar phrase
                        if bar % 4 in [1, 3]:
                            # Chord
                            chord = [53, 58, 63] # F2 Bb2 Eb3
                            # We can't write chords easily in this simple list structure without 'backup'
                            # Simplify: Arpeggiate or just write top note for now?
                            # Better: Write as chord in XML loop below
                            notes_to_write.append(("chord", [53, 58, 63], self.divisions*2))
                            notes_to_write.append((-1, self.divisions*2, "half", False, False))
                        else:
                             notes_to_write.append((-1, self.divisions*4, "whole", False, False))
                    elif zone_name == "B":
                        # Altered comping
                        notes_to_write.append((-1, self.divisions, "quarter", False, False)) # Rest 1
                        notes_to_write.append(("chord", [47, 53, 57, 62], self.divisions)) # B7alt stab
                        notes_to_write.append((-1, self.divisions*2, "half", False, False))
                    else:
                        # Upper register sparkles
                        if bar % 2 == 0:
                            notes_to_write.append((-1, self.divisions*3, "dotted-half", False, False))
                            notes_to_write.append(("chord", [84, 89, 94], self.divisions)) # High quartal
                        else:
                            notes_to_write.append((-1, self.divisions*4, "whole", False, False))

                # 4. BASS
                elif pid == "P10":
                    if zone_name == "A":
                        # Pedal C
                        notes_to_write.append((36, self.divisions*4, "whole", False, False))
                    elif zone_name == "B":
                        # Walking/Tension B
                        notes_to_write.append((35, self.divisions*3, "dotted-half", False, False))
                        notes_to_write.append((41, self.divisions, "quarter", False, False)) # F (tritone)
                    else:
                        # F Pedal with rhythmic skips
                        notes_to_write.append((29, self.divisions*3, "dotted-half", False, False)) # Low F
                        notes_to_write.append((41, self.divisions, "quarter", False, False)) # F octave

                # Defaults/Rests
                elif not notes_to_write:
                     notes_to_write.append((-1, self.divisions*4, "whole", False, False))

                # WRITE TO XML
                for item in notes_to_write:
                    if item[0] == "chord":
                        pitches, dur = item[1], item[2]
                        for i, p_midi in enumerate(pitches):
                            n = ET.SubElement(m, "note")
                            if i > 0: ET.SubElement(n, "chord")
                            
                            step, octave, alter = midi_to_pitch(p_midi)
                            p_node = ET.SubElement(n, "pitch")
                            ET.SubElement(p_node, "step").text = step
                            ET.SubElement(p_node, "octave").text = str(octave)
                            if alter: 
                                ET.SubElement(p_node, "alter").text = "1"
                                acc = ET.SubElement(n, "accidental")
                                acc.text = "sharp"
                            
                            ET.SubElement(n, "duration").text = str(dur)
                            ET.SubElement(n, "type").text = "quarter" # Simplified
                    
                    elif item[0] == -1: # Rest
                        n = ET.SubElement(m, "note")
                        ET.SubElement(n, "rest")
                        ET.SubElement(n, "duration").text = str(item[1])
                        t = "whole" if item[1] >= self.divisions*4 else "quarter"
                        ET.SubElement(n, "type").text = t
                    
                    else: # Single Note
                        midi, dur, ntype, tie_s, tie_e = item
                        n = ET.SubElement(m, "note")
                        step, octave, alter = midi_to_pitch(midi)
                        p_node = ET.SubElement(n, "pitch")
                        ET.SubElement(p_node, "step").text = step
                        ET.SubElement(p_node, "octave").text = str(octave)
                        if alter: 
                            ET.SubElement(p_node, "alter").text = "1"
                            acc = ET.SubElement(n, "accidental")
                            acc.text = "sharp"
                        ET.SubElement(n, "duration").text = str(dur)
                        ET.SubElement(n, "type").text = ntype
                        
                        if tie_s: 
                            t = ET.SubElement(n, "tie", type="start")
                            n.append(ET.Element("notations", {}))
                            ET.SubElement(n.find("notations"), "tied", type="start")
                        if tie_e:
                            t = ET.SubElement(n, "tie", type="stop")
                            if n.find("notations") is None: n.append(ET.Element("notations", {}))
                            ET.SubElement(n.find("notations"), "tied", type="stop")

                parts_data[pid].append(m)

        # Assemble Parts
        for pid in INSTRUMENTS:
            p_node = ET.SubElement(root, "part", id=pid)
            for m in parts_data[pid]:
                p_node.append(m)
        
        # Write XML
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(OUTPUT_XML, encoding="UTF-8", xml_declaration=True)
        print(f"Generated {OUTPUT_XML}")

        # WRITE MIDI
        from midi_writer import MIDIWriterWrapper
        mw = MIDIWriterWrapper()
        
        for pid in INSTRUMENTS:
            track_idx = mw.add_track(INSTRUMENTS[pid]["name"])
            channel = 9 if pid == "P11" else (list(INSTRUMENTS.keys()).index(pid) % 16)
            
            # Set Program Change
            prog_num = INSTRUMENTS[pid]["midi"]
            if pid != "P11": 
                mw.add_program_change(track_idx, channel, prog_num)

            curr_time = 0
            for m in parts_data[pid]:
                notes_in_measure = m.findall("note")
                for i, n in enumerate(notes_in_measure):
                    is_rest = n.find("rest") is not None
                    dur_text = n.find("duration").text
                    dur = int(dur_text) / self.divisions if dur_text else 0
                    
                    if not is_rest:
                        # Pitch
                        p = n.find("pitch")
                        if p is not None:
                            step = p.find("step").text
                            octave = int(p.find("octave").text)
                            alter = int(p.find("alter").text) if p.find("alter") is not None else 0
                            midi_pitch = (NOTE_NAMES.index(step) + (octave+1)*12) + alter
                            
                            # Handle Chord (same start time)
                            is_chord = n.find("chord") is not None
                            
                            start = curr_time
                            if is_chord:
                                start = curr_time - dur 
                            
                            mw.add_note(track_idx, channel, midi_pitch, start, dur, 80)
                            
                            if not is_chord:
                                curr_time += dur
                        else:
                            # Unpitched or Error
                             curr_time += dur
                    else:
                        curr_time += dur
                        
        mw.write(OUTPUT_MIDI)
        print(f"Generated {OUTPUT_MIDI}")

        
if __name__ == "__main__":
    gen = Generator()
    gen.parse_source()
    gen.generate_xml()

