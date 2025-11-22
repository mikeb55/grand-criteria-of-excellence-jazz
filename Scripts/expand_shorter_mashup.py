import xml.etree.ElementTree as ET
import math
import copy
import random

# --- CONFIG ---
SOURCE_FILE = "Works/V1 0-Shorter-Mash-up.musicxml"
OUTPUT_XML = "Works/V6_Wonderland_Orchestral_Shorter_Expanded.musicxml"
OUTPUT_MIDI = "Works/V6_Wonderland_Orchestral_Shorter_Expanded.mid"

# Target Instruments (MIDI Programs)
INSTRUMENTS = {
    "P1": {"name": "Flute", "midi": 73, "clef": "G", "transpose": 0},
    "P2": {"name": "Clarinet in Bb", "midi": 71, "clef": "G", "transpose": -2},
    "P3": {"name": "Flugelhorn", "midi": 56, "clef": "G", "transpose": -2},
    "P4": {"name": "Violin I", "midi": 40, "clef": "G", "transpose": 0},
    "P5": {"name": "Violin II", "midi": 40, "clef": "G", "transpose": 0},
    "P6": {"name": "Viola", "midi": 41, "clef": "C", "transpose": 0},
    "P7": {"name": "Cello", "midi": 42, "clef": "F", "transpose": 0},
    "P8": {"name": "Electric Guitar", "midi": 27, "clef": "G", "transpose": 0},
    "P9": {"name": "Piano", "midi": 0, "clef": "G", "transpose": 0},
    "P10": {"name": "Double Bass", "midi": 32, "clef": "F", "transpose": 0}, # Sounds 8va low usually handled by renderer, keeping 0 for pitch logic
    "P11": {"name": "Light Percussion", "midi": 118, "clef": "percussion", "transpose": 0}
}

# Scale/Chord Definitions
SCALES = {
    "C7sus": [0, 2, 5, 7, 10], # C D F G Bb
    "B7alt": [11, 0, 3, 4, 6, 8, 10], # B C D# E G A
    "Fmaj7#11": [5, 7, 9, 11, 0, 2, 4] # F G A B C D E
}

# Note Names
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def midi_to_note_name(midi_val):
    octave = (midi_val // 12) - 1
    note = NOTE_NAMES[midi_val % 12]
    return note, octave

# --- MIDI WRITER ---
class MIDIWriter:
    def __init__(self):
        self.tracks = []
        self.ticks_per_beat = 480

    def add_track(self, name):
        track = []
        self.tracks.append(track)
        return len(self.tracks) - 1

    def add_note(self, track_idx, channel, pitch, start_time, duration, velocity):
        # Simple list of events: (time, type, channel, data1, data2)
        # type: 0x90 (on), 0x80 (off)
        # Time is absolute here, will convert to delta
        on_time = int(start_time * self.ticks_per_beat)
        off_time = int((start_time + duration) * self.ticks_per_beat)
        self.tracks[track_idx].append((on_time, 0x90, channel, pitch, velocity))
        self.tracks[track_idx].append((off_time, 0x80, channel, pitch, 0))

    def write(self, filename):
        with open(filename, "wb") as f:
            # Header Chunk
            f.write(b'MThd')
            f.write(struct.pack('>L', 6))
            f.write(struct.pack('>HHH', 1, len(self.tracks), self.ticks_per_beat))
            
            # Track Chunks
            for track in self.tracks:
                track.sort(key=lambda x: x[0]) # Sort by time
                
                data = bytearray()
                last_time = 0
                
                for event in track:
                    time, type_, channel, d1, d2 = event
                    delta = time - last_time
                    last_time = time
                    
                    # Write variable length delta
                    data.extend(self.write_var_len(delta))
                    
                    # Status byte
                    data.append(type_ | (channel & 0x0F))
                    data.append(d1)
                    data.append(d2)
                    
                # End of track
                data.extend(self.write_var_len(0))
                data.append(0xFF)
                data.append(0x2F)
                data.append(0x00)
                
                f.write(b'MTrk')
                f.write(struct.pack('>L', len(data)))
                f.write(data)
                
    def write_var_len(self, value):
        if value == 0: return bytearray([0])
        
        bytes_list = []
        while value > 0:
            bytes_list.append(value & 0x7F)
            value >>= 7
        
        for i in range(1, len(bytes_list)):
            bytes_list[i] |= 0x80
            
        return bytearray(reversed(bytes_list))

import struct

# --- GENERATOR ---
class JazzExpansion:
    def __init__(self):
        self.source_notes = [] # List of {pitch, duration, start, type}
        self.divisions = 256
        
    def parse_source(self):
        print(f"Parsing {SOURCE_FILE}...")
        try:
            tree = ET.parse(SOURCE_FILE)
            root = tree.getroot()
        except Exception as e:
            print(f"Error reading {SOURCE_FILE}: {e}")
            return

        # Find Divisions
        for part in root.findall("part"):
            measure = part.find("measure")
            if measure is not None:
                attr = measure.find("attributes")
                if attr is not None:
                    div = attr.find("divisions")
                    if div is not None:
                        self.divisions = int(div.text)
                        break
        
        print(f"Divisions: {self.divisions}")

        # Extract Melody from P1 (Alto Sax) - Convert to Concert
        # P1 is Alto (transposes -9 semitones? Written C sounds Eb. So -9 check.)
        # Wait, Alto Sax in Eb: Written C4 -> Sounding Eb3. (Down Major 6th = -9 semitones)
        # But typically XML <transpose> says <chromatic>-9</chromatic>.
        
        part1 = root.find(".//part[@id='P1']")
        if part1 is None:
            print("Part P1 not found, trying first part")
            part1 = root.find("part")
            
        current_time = 0
        for measure in part1.findall("measure"):
            m_start = current_time
            curr_measure_time = 0
            
            for note in measure.findall("note"):
                dur_node = note.find("duration")
                if dur_node is None: continue
                
                duration = int(dur_node.text)
                is_rest = note.find("rest") is not None
                
                if not is_rest:
                    pitch_node = note.find("pitch")
                    if pitch_node is not None:
                        step = pitch_node.find("step").text
                        octave = int(pitch_node.find("octave").text)
                        alter = 0
                        if pitch_node.find("alter") is not None:
                            alter = int(pitch_node.find("alter").text)
                        
                        # Calculate MIDI
                        midi_base = (NOTE_NAMES.index(step) + (octave + 1) * 12) + alter
                        # Transpose to Concert (Alto Sax: Written C = Sounding Eb, so -9)
                        concert_midi = midi_base - 9 
                        
                        self.source_notes.append({
                            "pitch": concert_midi,
                            "duration": duration,
                            "start": m_start + curr_measure_time,
                            "measure": int(measure.get("number"))
                        })
                
                curr_measure_time += duration
            current_time += 4 * self.divisions # Assume 4/4 for calculation base
            
        print(f"Extracted {len(self.source_notes)} notes.")

    def generate(self):
        # Create New XML
        root = ET.Element("score-partwise", version="3.1")
        work = ET.SubElement(root, "work")
        ET.SubElement(work, "work-title").text = "Wonderland: Jazz Orchestral Expansion"
        
        # Part List
        part_list = ET.SubElement(root, "part-list")
        for pid, info in INSTRUMENTS.items():
            sp = ET.SubElement(part_list, "score-part", id=pid)
            ET.SubElement(sp, "part-name").text = info["name"]
            
        # Content Generation
        parts_content = {pid: [] for pid in INSTRUMENTS}
        
        # 48 Bars
        for bar in range(1, 49):
            # Determine Zone
            zone = "C7sus"
            if 17 <= bar <= 24: zone = "B7alt"
            if 25 <= bar <= 48: zone = "Fmaj7#11"
            
            # Base Chord Tones
            chord_tones = SCALES[zone]
            root_note = chord_tones[0]
            
            # For each part, generate measure
            for pid, info in INSTRUMENTS.items():
                m_node = ET.Element("measure", number=str(bar))
                
                # Attributes for Bar 1
                if bar == 1:
                    attr = ET.SubElement(m_node, "attributes")
                    divs = ET.SubElement(attr, "divisions")
                    divs.text = str(self.divisions)
                    key = ET.SubElement(attr, "key")
                    ET.SubElement(key, "fifths").text = "0" # Concert Key
                    time = ET.SubElement(attr, "time")
                    ET.SubElement(time, "beats").text = "4"
                    ET.SubElement(time, "beat-type").text = "4"
                    
                    clef = ET.SubElement(attr, "clef")
                    if info["clef"] == "F":
                        ET.SubElement(clef, "sign").text = "F"
                        ET.SubElement(clef, "line").text = "4"
                    elif info["clef"] == "C":
                        ET.SubElement(clef, "sign").text = "C"
                        ET.SubElement(clef, "line").text = "3"
                    elif info["clef"] == "percussion":
                        ET.SubElement(clef, "sign").text = "percussion"
                        ET.SubElement(clef, "line").text = "2"
                    else:
                        ET.SubElement(clef, "sign").text = "G"
                        ET.SubElement(clef, "line").text = "2"

                # --- LOGIC PER INSTRUMENT ---
                notes_to_add = [] # list of (midi, dur, type)
                
                # 1. MELODY (Flute, Clarinet, Flugel)
                if pid in ["P1", "P2", "P3"] and bar <= 32:
                    # Map source notes
                    # Find source notes for this bar (approx)
                    # Source bar mapping: 
                    #  1-16 -> Source 1-16
                    #  17-24 -> Source 17-24
                    #  25-32 -> Source 25-32
                    source_bar_idx = bar 
                    bar_notes = [n for n in self.source_notes if n["measure"] == source_bar_idx]
                    
                    if bar_notes:
                        # Distribute melody
                        if pid == "P1": # Flute takes top
                            for n in bar_notes:
                                target_pitch = n["pitch"] + 12 # 8va
                                # Transpose to key zone if needed? Source is likely compatible or we force it
                                # For now, keep source melody logic but fit to chord if wildly out?
                                # Assuming source melody fits the "Mash-up" intent.
                                notes_to_add.append((target_pitch, n["duration"], "quarter")) # Simplify rhythm
                        elif pid == "P3": # Flugel
                            if bar % 2 == 0: # Call and response
                                for n in bar_notes:
                                     notes_to_add.append((n["pitch"], n["duration"], "quarter"))
                    else:
                         notes_to_add.append((-1, self.divisions*4, "whole")) # Rest

                # 2. STRINGS (P4-P7) - Pads
                elif pid in ["P4", "P5", "P6", "P7"]:
                    # Generate pad note based on chord
                    # Distribute voicing: Root(Cello), 3rd/7th(Viola), Color(Vln2), Color(Vln1)
                    tone_idx = 0
                    octave_shift = 0
                    if pid == "P7": tone_idx = 0; octave_shift = 3 # Cello Root
                    if pid == "P6": tone_idx = 4; octave_shift = 4 # Viola 5th/7th
                    if pid == "P5": tone_idx = 2; octave_shift = 4 # Vln2 3rd
                    if pid == "P4": tone_idx = 3; octave_shift = 5 # Vln1 Color
                    
                    note_val = chord_tones[tone_idx % len(chord_tones)] + (octave_shift * 12) + 12
                    notes_to_add.append((note_val, self.divisions*4, "whole"))

                # 3. PIANO (P9) - Quartal Comping
                elif pid == "P9":
                    # Rhythmic comping
                    if bar % 2 == 1:
                        # Chord on 1 and 2+
                        voicing = [root_note+48, root_note+53, root_note+58] # Stacked 4ths
                        for v in voicing:
                             notes_to_add.append((v, self.divisions*2, "half"))
                        notes_to_add.append((-1, self.divisions*2, "half"))
                    else:
                        notes_to_add.append((-1, self.divisions*4, "whole"))
                
                # 4. BASS (P10)
                elif pid == "P10":
                    # Root notes with rhythm
                    chord_root = chord_tones[0] + 36 # Low
                    notes_to_add.append((chord_root, self.divisions*3, "dotted-half"))
                    notes_to_add.append((chord_root, self.divisions, "quarter"))

                # 5. DRUMS (P11)
                elif pid == "P11":
                    if bar > 4:
                        # Ride cymbal pattern
                        notes_to_add.append((51, self.divisions, "quarter")) # Ride
                        notes_to_add.append((51, self.divisions, "quarter"))
                        notes_to_add.append((51, self.divisions, "quarter"))
                        notes_to_add.append((51, self.divisions, "quarter"))
                    else:
                        notes_to_add.append((-1, self.divisions*4, "whole"))
                
                else:
                     notes_to_add.append((-1, self.divisions*4, "whole"))

                # Add notes to XML
                current_pos = 0
                for midi_p, dur, ntype in notes_to_add:
                    n_elem = ET.SubElement(m_node, "note")
                    if midi_p == -1:
                        ET.SubElement(n_elem, "rest")
                    else:
                        # Transpose for written pitch in XML if needed
                        # Logic: XML needs Written Pitch if Transpose is set? 
                        # Usually score-partwise with <transpose> in attributes handles playback, but notes are written.
                        # To simplify: We write CONCERT PITCH notes and set NO transpose in attributes for now, 
                        # OR we calculate written pitch. 
                        # Let's stick to Concert Pitch data and 0 transpose for simplicity of generation.
                        # (I set transpose to 0 in attributes above for most, but kept dict info)
                        
                        p_node = ET.SubElement(n_elem, "pitch")
                        step, oct_val = midi_to_note_name(midi_p)
                        ET.SubElement(p_node, "step").text = step.replace("#", "")
                        ET.SubElement(p_node, "octave").text = str(oct_val)
                        if "#" in step:
                            ET.SubElement(p_node, "alter").text = "1"
                            acc = ET.SubElement(n_elem, "accidental")
                            acc.text = "sharp"
                            
                    ET.SubElement(n_elem, "duration").text = str(int(dur))
                    # ET.SubElement(n_elem, "type").text = ntype # Optional, skip for now

                parts_content[pid].append(m_node)
        
        # Assemble
        for pid in INSTRUMENTS:
            p_node = ET.SubElement(root, "part", id=pid)
            for m in parts_content[pid]:
                p_node.append(m)
                
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(OUTPUT_XML, encoding="UTF-8", xml_declaration=True)
        print(f"Written {OUTPUT_XML}")

        # GENERATE MIDI
        mw = MIDIWriter()
        for pid, info in INSTRUMENTS.items():
            track = mw.add_track(info["name"])
            channel = 9 if pid == "P11" else (list(INSTRUMENTS.keys()).index(pid) % 16)
            
            # Parse generated XML back to events or just use logic?
            # Since I have the logic above, I should have stored the events.
            # Re-parsing the just-created XML parts_content is easier.
            
            curr_time = 0
            for m in parts_content[pid]:
                for n in m.findall("note"):
                    dur = int(n.find("duration").text) / self.divisions
                    is_rest = n.find("rest") is not None
                    if not is_rest:
                        p = n.find("pitch")
                        step = p.find("step").text
                        octave = int(p.find("octave").text)
                        alter = int(p.find("alter").text) if p.find("alter") is not None else 0
                        # Reconstruct MIDI
                        pitch = (NOTE_NAMES.index(step) + (octave + 1) * 12) + alter
                        mw.add_note(track, channel, pitch, curr_time, dur, 90)
                    curr_time += dur
                    
        mw.write(OUTPUT_MIDI)
        print(f"Written {OUTPUT_MIDI}")

if __name__ == "__main__":
    app = JazzExpansion()
    app.parse_source()
    app.generate()

