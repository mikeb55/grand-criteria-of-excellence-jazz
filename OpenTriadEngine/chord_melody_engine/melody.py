"""
Melody Module for Chord-Melody Engine
======================================

Handles melody input parsing from various formats:
- MIDI data
- MusicXML
- List of pitches
- Lead sheet notation
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union, Tuple
from enum import Enum
import xml.etree.ElementTree as ET
from pathlib import Path


@dataclass
class MelodyNote:
    """
    Represents a single melody note.
    
    Attributes:
        pitch: MIDI pitch number (60 = C4)
        pitch_name: Note name with octave (e.g., "C4", "F#5")
        duration: Duration in beats
        onset: Start time in beats from beginning
        bar: Bar number (1-indexed)
        beat: Beat position within bar
        chord_context: Optional chord symbol for this beat
        is_rest: Whether this is a rest
        articulation: Optional articulation marking
    """
    pitch: int
    pitch_name: str
    duration: float
    onset: float
    bar: int = 1
    beat: float = 1.0
    chord_context: Optional[str] = None
    is_rest: bool = False
    articulation: Optional[str] = None
    
    @property
    def pitch_class(self) -> int:
        """Get pitch class (0-11)."""
        return self.pitch % 12
    
    @property
    def octave(self) -> int:
        """Get octave number."""
        return (self.pitch // 12) - 1


@dataclass
class Melody:
    """
    Represents a complete melody.
    
    Attributes:
        notes: List of MelodyNote objects
        key: Key signature
        time_signature: Tuple of (beats_per_bar, beat_value)
        tempo: Tempo in BPM
        title: Optional title
    """
    notes: List[MelodyNote]
    key: str = "C"
    time_signature: Tuple[int, int] = (4, 4)
    tempo: int = 120
    title: str = "Untitled"
    
    def get_pitches(self) -> List[int]:
        """Get list of MIDI pitches (excluding rests)."""
        return [n.pitch for n in self.notes if not n.is_rest]
    
    def get_pitch_range(self) -> Tuple[int, int]:
        """Get lowest and highest pitches."""
        pitches = self.get_pitches()
        return (min(pitches), max(pitches)) if pitches else (60, 60)
    
    def total_duration(self) -> float:
        """Get total duration in beats."""
        if not self.notes:
            return 0.0
        last_note = self.notes[-1]
        return last_note.onset + last_note.duration
    
    def bar_count(self) -> int:
        """Get number of bars."""
        if not self.notes:
            return 0
        return max(n.bar for n in self.notes)
    
    def get_notes_in_bar(self, bar: int) -> List[MelodyNote]:
        """Get all notes in a specific bar."""
        return [n for n in self.notes if n.bar == bar]


class MelodyParser:
    """
    Parses melody from various input formats.
    """
    
    # MIDI note to name mapping
    MIDI_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    NOTE_TO_MIDI = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
        "E": 4, "Fb": 4, "E#": 5, "F": 5, "F#": 6, "Gb": 6,
        "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10,
        "B": 11, "Cb": 11, "B#": 0
    }
    
    def __init__(self, time_signature: Tuple[int, int] = (4, 4)):
        """
        Initialize the parser.
        
        Args:
            time_signature: Default time signature (beats, beat_value)
        """
        self.time_signature = time_signature
        self.beats_per_bar = time_signature[0]
    
    def _midi_to_note_name(self, midi: int) -> str:
        """Convert MIDI pitch to note name with octave."""
        octave = (midi // 12) - 1
        note = self.MIDI_TO_NOTE[midi % 12]
        return f"{note}{octave}"
    
    def _note_name_to_midi(self, note_name: str) -> int:
        """Convert note name to MIDI pitch."""
        # Parse note name (e.g., "C4", "F#5", "Bb3")
        if len(note_name) >= 2:
            if note_name[1] in ['#', 'b']:
                note = note_name[:2]
                octave = int(note_name[2:])
            else:
                note = note_name[0]
                octave = int(note_name[1:])
            
            pitch_class = self.NOTE_TO_MIDI.get(note, 0)
            return pitch_class + (octave + 1) * 12
        return 60  # Default to C4
    
    def parse_pitch_list(
        self,
        pitches: List[Union[int, str]],
        durations: Optional[List[float]] = None,
        key: str = "C"
    ) -> Melody:
        """
        Parse melody from a list of pitches.
        
        Args:
            pitches: List of MIDI pitches (int) or note names (str)
            durations: Optional list of durations in beats
            key: Key signature
        
        Returns:
            Melody object
        """
        notes = []
        current_onset = 0.0
        current_bar = 1
        current_beat = 1.0
        
        # Default duration is quarter note
        if durations is None:
            durations = [1.0] * len(pitches)
        
        for i, pitch in enumerate(pitches):
            # Convert to MIDI if string
            if isinstance(pitch, str):
                midi_pitch = self._note_name_to_midi(pitch)
                pitch_name = pitch
            else:
                midi_pitch = pitch
                pitch_name = self._midi_to_note_name(pitch)
            
            duration = durations[i] if i < len(durations) else 1.0
            
            note = MelodyNote(
                pitch=midi_pitch,
                pitch_name=pitch_name,
                duration=duration,
                onset=current_onset,
                bar=current_bar,
                beat=current_beat
            )
            notes.append(note)
            
            # Update position
            current_onset += duration
            current_beat += duration
            
            # Handle bar transitions
            while current_beat > self.beats_per_bar:
                current_beat -= self.beats_per_bar
                current_bar += 1
        
        return Melody(notes=notes, key=key, time_signature=self.time_signature)
    
    def parse_musicxml(self, filepath: str) -> Melody:
        """
        Parse melody from a MusicXML file.
        
        Args:
            filepath: Path to MusicXML file
        
        Returns:
            Melody object
        """
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        notes = []
        current_onset = 0.0
        current_bar = 1
        divisions = 1  # Divisions per quarter note
        
        # Find divisions
        for div_elem in root.iter('divisions'):
            divisions = int(div_elem.text)
            break
        
        # Extract key
        key = "C"
        for key_elem in root.iter('key'):
            fifths = key_elem.find('fifths')
            if fifths is not None:
                key = self._fifths_to_key(int(fifths.text))
            break
        
        # Extract time signature
        time_sig = (4, 4)
        for time_elem in root.iter('time'):
            beats = time_elem.find('beats')
            beat_type = time_elem.find('beat-type')
            if beats is not None and beat_type is not None:
                time_sig = (int(beats.text), int(beat_type.text))
            break
        
        self.time_signature = time_sig
        self.beats_per_bar = time_sig[0]
        
        # Extract notes
        for measure in root.iter('measure'):
            measure_num = int(measure.get('number', current_bar))
            current_bar = measure_num
            measure_onset = 0.0
            
            for elem in measure:
                if elem.tag == 'note':
                    # Check for rest
                    is_rest = elem.find('rest') is not None
                    
                    # Get duration
                    duration_elem = elem.find('duration')
                    duration = float(duration_elem.text) / divisions if duration_elem is not None else 1.0
                    
                    if is_rest:
                        # Create rest note
                        note = MelodyNote(
                            pitch=0,
                            pitch_name="rest",
                            duration=duration,
                            onset=current_onset,
                            bar=current_bar,
                            beat=1.0 + measure_onset,
                            is_rest=True
                        )
                    else:
                        # Get pitch
                        pitch_elem = elem.find('pitch')
                        if pitch_elem is not None:
                            step = pitch_elem.find('step').text
                            octave = int(pitch_elem.find('octave').text)
                            alter = pitch_elem.find('alter')
                            
                            if alter is not None:
                                alter_val = int(alter.text)
                                if alter_val == 1:
                                    step += "#"
                                elif alter_val == -1:
                                    step += "b"
                            
                            pitch_name = f"{step}{octave}"
                            midi_pitch = self._note_name_to_midi(pitch_name)
                            
                            note = MelodyNote(
                                pitch=midi_pitch,
                                pitch_name=pitch_name,
                                duration=duration,
                                onset=current_onset,
                                bar=current_bar,
                                beat=1.0 + measure_onset
                            )
                            notes.append(note)
                    
                    # Check for chord (simultaneous notes)
                    if elem.find('chord') is None:
                        current_onset += duration
                        measure_onset += duration
        
        # Extract title
        title = "Untitled"
        for work_title in root.iter('work-title'):
            title = work_title.text or "Untitled"
            break
        
        return Melody(
            notes=notes,
            key=key,
            time_signature=time_sig,
            title=title
        )
    
    def _fifths_to_key(self, fifths: int) -> str:
        """Convert circle of fifths position to key name."""
        keys = ["C", "G", "D", "A", "E", "B", "F#", "C#"]
        flat_keys = ["C", "F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb"]
        
        if fifths >= 0:
            return keys[min(fifths, 7)]
        else:
            return flat_keys[min(-fifths, 7)]
    
    def parse_simple_notation(
        self,
        notation: str,
        key: str = "C"
    ) -> Melody:
        """
        Parse melody from simple text notation.
        
        Format: "C4 D4 E4 F4 | G4 A4 B4 C5"
        
        Args:
            notation: Text notation string
            key: Key signature
        
        Returns:
            Melody object
        """
        notes = []
        current_onset = 0.0
        current_bar = 1
        current_beat = 1.0
        
        # Split by bars and notes
        bars = notation.split("|")
        
        for bar_idx, bar in enumerate(bars, 1):
            bar_notes = bar.strip().split()
            
            for note_str in bar_notes:
                if not note_str:
                    continue
                
                # Parse duration suffix (e.g., "C4:2" for half note)
                if ":" in note_str:
                    note_part, dur_part = note_str.split(":")
                    duration = float(dur_part)
                else:
                    note_part = note_str
                    duration = 1.0  # Quarter note default
                
                # Handle rests
                if note_part.lower() in ['r', 'rest']:
                    note = MelodyNote(
                        pitch=0,
                        pitch_name="rest",
                        duration=duration,
                        onset=current_onset,
                        bar=bar_idx,
                        beat=current_beat,
                        is_rest=True
                    )
                else:
                    midi_pitch = self._note_name_to_midi(note_part)
                    note = MelodyNote(
                        pitch=midi_pitch,
                        pitch_name=note_part,
                        duration=duration,
                        onset=current_onset,
                        bar=bar_idx,
                        beat=current_beat
                    )
                
                notes.append(note)
                current_onset += duration
                current_beat += duration
                
                if current_beat > self.beats_per_bar:
                    current_beat = 1.0
            
            current_bar = bar_idx + 1
            current_beat = 1.0
        
        return Melody(notes=notes, key=key, time_signature=self.time_signature)
    
    def create_from_progression(
        self,
        progression: List[str],
        melody_degrees: List[int],
        key: str = "C"
    ) -> Melody:
        """
        Create a melody from chord progression and scale degrees.
        
        Args:
            progression: List of chord symbols
            melody_degrees: Scale degrees for each chord (1-7)
            key: Key signature
        
        Returns:
            Melody object
        """
        # Scale degrees to semitones (major scale)
        degree_to_semitone = {
            1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11
        }
        
        # Get root pitch
        root_midi = self.NOTE_TO_MIDI.get(key, 0) + 60  # C4 = 60
        
        notes = []
        current_onset = 0.0
        
        for i, (chord, degree) in enumerate(zip(progression, melody_degrees)):
            # Map degree to semitone offset
            semitone = degree_to_semitone.get(degree, 0)
            midi_pitch = root_midi + semitone
            
            note = MelodyNote(
                pitch=midi_pitch,
                pitch_name=self._midi_to_note_name(midi_pitch),
                duration=self.beats_per_bar,  # One chord per bar
                onset=current_onset,
                bar=i + 1,
                beat=1.0,
                chord_context=chord
            )
            notes.append(note)
            current_onset += self.beats_per_bar
        
        return Melody(notes=notes, key=key, time_signature=self.time_signature)

