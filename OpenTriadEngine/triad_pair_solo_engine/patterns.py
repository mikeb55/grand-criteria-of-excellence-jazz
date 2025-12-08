"""
Pattern Generation Module for Triad Pair Solo Engine
======================================================

Implements patterns specific to intervallic triad-pair soloing:
- Arpeggio patterns (up/down)
- Alternating triads (A → B → A → B)
- Rotation patterns (1-3-2, 3-1-2, etc.)
- Large interval skips (open-triad leaps)
- Directional waves
- Pivot-tone patterns
- Cross-string displacement
- Triad-pair sequencing over progression
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Callable
from enum import Enum
import random

try:
    from .triad_pairs import TriadPair
    from .inputs import ContourType, SoloDifficulty
except ImportError:
    from triad_pairs import TriadPair
    from inputs import ContourType, SoloDifficulty


class PatternType(Enum):
    """Types of melodic patterns."""
    UP_ARPEGGIO = "up_arpeggio"
    DOWN_ARPEGGIO = "down_arpeggio"
    ALTERNATING = "alternating"
    ROTATION_132 = "rotation_132"
    ROTATION_312 = "rotation_312"
    ROTATION_213 = "rotation_213"
    ROTATION_321 = "rotation_321"
    INTERVAL_SKIP = "interval_skip"
    WAVE = "wave"
    PIVOT_TONE = "pivot_tone"
    CROSS_STRING = "cross_string"
    SEQUENCE = "sequence"


@dataclass
class PatternNote:
    """
    Represents a single note in a pattern.
    
    Attributes:
        pitch: MIDI pitch number
        pitch_name: Note name (e.g., "C4", "F#5")
        duration: Duration in beats
        triad_source: Which triad this note came from (A or B)
        voice: Which voice in the triad (1=root, 2=third, 3=fifth)
        string: Guitar string (1-6, optional)
        fret: Guitar fret (optional)
        articulation: Optional articulation marking
    """
    pitch: int
    pitch_name: str
    duration: float = 0.5
    triad_source: str = "A"
    voice: int = 1
    string: Optional[int] = None
    fret: Optional[int] = None
    articulation: Optional[str] = None


@dataclass
class MelodicCell:
    """
    A short melodic cell (motif) derived from triad pair patterns.
    
    Attributes:
        notes: List of PatternNotes
        pattern_type: The pattern type used
        triad_pair: Source triad pair
        contour: Contour direction
    """
    notes: List[PatternNote]
    pattern_type: PatternType
    triad_pair: Optional[TriadPair] = None
    contour: str = "mixed"
    
    def get_pitches(self) -> List[int]:
        """Get list of MIDI pitches."""
        return [n.pitch for n in self.notes]
    
    def get_pitch_names(self) -> List[str]:
        """Get list of pitch names."""
        return [n.pitch_name for n in self.notes]
    
    def total_duration(self) -> float:
        """Get total duration in beats."""
        return sum(n.duration for n in self.notes)


class SoloPatternGenerator:
    """
    Generates melodic patterns for intervallic triad-pair soloing.
    """
    
    # MIDI note mapping
    NOTE_TO_MIDI = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
        "E": 4, "Fb": 4, "E#": 5, "F": 5, "F#": 6, "Gb": 6,
        "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10,
        "B": 11, "Cb": 11, "B#": 0
    }
    
    MIDI_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    # Triad intervals from root (in semitones)
    TRIAD_INTERVALS = {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "dim": [0, 3, 6],
        "aug": [0, 4, 8],
        "sus2": [0, 2, 7],
        "sus4": [0, 5, 7],
    }
    
    # Guitar string tuning (standard, in MIDI)
    GUITAR_TUNING = [40, 45, 50, 55, 59, 64]  # E2, A2, D3, G3, B3, E4
    
    def __init__(
        self, 
        base_octave: int = 4,
        seed: Optional[int] = None,
        difficulty: SoloDifficulty = SoloDifficulty.INTERMEDIATE
    ):
        """
        Initialize the pattern generator.
        
        Args:
            base_octave: Base octave for pattern generation
            seed: Random seed for reproducibility
            difficulty: Difficulty level affects pattern complexity
        """
        self.base_octave = base_octave
        self.difficulty = difficulty
        if seed is not None:
            random.seed(seed)
    
    def _note_to_midi(self, note: str, octave: int = None) -> int:
        """Convert note name to MIDI pitch."""
        if octave is None:
            octave = self.base_octave
        base = self.NOTE_TO_MIDI.get(note, 0)
        return base + (octave + 1) * 12
    
    def _midi_to_note_name(self, midi: int) -> str:
        """Convert MIDI pitch to note name with octave."""
        octave = (midi // 12) - 1
        note = self.MIDI_TO_NOTE[midi % 12]
        return f"{note}{octave}"
    
    def _get_triad_pitches(
        self, 
        root: str, 
        quality: str, 
        octave: int = None,
        inversion: int = 0
    ) -> List[int]:
        """
        Get MIDI pitches for a triad.
        
        Args:
            root: Root note
            quality: Triad quality
            octave: Base octave
            inversion: 0=root, 1=first, 2=second
        
        Returns:
            List of 3 MIDI pitches
        """
        if octave is None:
            octave = self.base_octave
        
        intervals = self.TRIAD_INTERVALS.get(quality, self.TRIAD_INTERVALS["major"])
        root_midi = self._note_to_midi(root, octave)
        
        pitches = [root_midi + interval for interval in intervals]
        
        # Apply inversion
        if inversion == 1:
            pitches = [pitches[1], pitches[2], pitches[0] + 12]
        elif inversion == 2:
            pitches = [pitches[2], pitches[0] + 12, pitches[1] + 12]
        
        return pitches
    
    def _get_guitar_position(self, midi_pitch: int, string_set: str = "auto") -> Tuple[int, int]:
        """
        Get guitar string and fret for a MIDI pitch.
        
        Args:
            midi_pitch: MIDI pitch number
            string_set: String set preference
        
        Returns:
            Tuple of (string, fret) - 1-indexed string
        """
        # Determine which strings to use
        if string_set == "6-4":
            strings = [0, 1, 2]  # E, A, D
        elif string_set == "5-3":
            strings = [1, 2, 3]  # A, D, G
        elif string_set == "4-2":
            strings = [2, 3, 4]  # D, G, B
        else:  # auto
            strings = list(range(6))
        
        # Find best string/fret combination
        best_string = None
        best_fret = None
        
        for string_idx in strings:
            open_pitch = self.GUITAR_TUNING[string_idx]
            fret = midi_pitch - open_pitch
            
            if 0 <= fret <= 15:  # Reasonable fret range
                if best_fret is None or abs(fret - 5) < abs(best_fret - 5):
                    best_string = 6 - string_idx  # Convert to 1-indexed (6=low E)
                    best_fret = fret
        
        return (best_string or 1, best_fret or 0)
    
    def generate_up_arpeggio(
        self, 
        triad_pair: TriadPair,
        duration: float = 0.5,
        string_set: str = "auto"
    ) -> MelodicCell:
        """Generate ascending arpeggio through both triads."""
        notes = []
        
        # Triad A ascending
        pitches_a = self._get_triad_pitches(triad_pair.triad_a[0], triad_pair.triad_a[1])
        for i, pitch in enumerate(pitches_a):
            string, fret = self._get_guitar_position(pitch, string_set)
            notes.append(PatternNote(
                pitch=pitch,
                pitch_name=self._midi_to_note_name(pitch),
                duration=duration,
                triad_source="A",
                voice=i + 1,
                string=string,
                fret=fret
            ))
        
        # Triad B ascending (higher octave for continuity)
        pitches_b = self._get_triad_pitches(
            triad_pair.triad_b[0], triad_pair.triad_b[1], 
            self.base_octave + 1
        )
        for i, pitch in enumerate(pitches_b):
            string, fret = self._get_guitar_position(pitch, string_set)
            notes.append(PatternNote(
                pitch=pitch,
                pitch_name=self._midi_to_note_name(pitch),
                duration=duration,
                triad_source="B",
                voice=i + 1,
                string=string,
                fret=fret
            ))
        
        return MelodicCell(
            notes=notes,
            pattern_type=PatternType.UP_ARPEGGIO,
            triad_pair=triad_pair,
            contour="ascending"
        )
    
    def generate_down_arpeggio(
        self, 
        triad_pair: TriadPair,
        duration: float = 0.5,
        string_set: str = "auto"
    ) -> MelodicCell:
        """Generate descending arpeggio through both triads."""
        notes = []
        
        # Triad B descending (higher octave)
        pitches_b = self._get_triad_pitches(
            triad_pair.triad_b[0], triad_pair.triad_b[1],
            self.base_octave + 1
        )
        for i, pitch in enumerate(reversed(pitches_b)):
            string, fret = self._get_guitar_position(pitch, string_set)
            notes.append(PatternNote(
                pitch=pitch,
                pitch_name=self._midi_to_note_name(pitch),
                duration=duration,
                triad_source="B",
                voice=3 - i,
                string=string,
                fret=fret
            ))
        
        # Triad A descending
        pitches_a = self._get_triad_pitches(triad_pair.triad_a[0], triad_pair.triad_a[1])
        for i, pitch in enumerate(reversed(pitches_a)):
            string, fret = self._get_guitar_position(pitch, string_set)
            notes.append(PatternNote(
                pitch=pitch,
                pitch_name=self._midi_to_note_name(pitch),
                duration=duration,
                triad_source="A",
                voice=3 - i,
                string=string,
                fret=fret
            ))
        
        return MelodicCell(
            notes=notes,
            pattern_type=PatternType.DOWN_ARPEGGIO,
            triad_pair=triad_pair,
            contour="descending"
        )
    
    def generate_alternating(
        self, 
        triad_pair: TriadPair,
        duration: float = 0.5,
        repetitions: int = 2,
        string_set: str = "auto"
    ) -> MelodicCell:
        """Generate alternating triad pattern (A → B → A → B)."""
        notes = []
        pitches_a = self._get_triad_pitches(triad_pair.triad_a[0], triad_pair.triad_a[1])
        pitches_b = self._get_triad_pitches(triad_pair.triad_b[0], triad_pair.triad_b[1])
        
        for rep in range(repetitions):
            # One note from each triad alternating
            for i in range(3):
                # From triad A
                pitch_a = pitches_a[i % 3]
                string, fret = self._get_guitar_position(pitch_a, string_set)
                notes.append(PatternNote(
                    pitch=pitch_a,
                    pitch_name=self._midi_to_note_name(pitch_a),
                    duration=duration,
                    triad_source="A",
                    voice=(i % 3) + 1,
                    string=string,
                    fret=fret
                ))
                
                # From triad B
                pitch_b = pitches_b[i % 3]
                string, fret = self._get_guitar_position(pitch_b, string_set)
                notes.append(PatternNote(
                    pitch=pitch_b,
                    pitch_name=self._midi_to_note_name(pitch_b),
                    duration=duration,
                    triad_source="B",
                    voice=(i % 3) + 1,
                    string=string,
                    fret=fret
                ))
        
        return MelodicCell(
            notes=notes,
            pattern_type=PatternType.ALTERNATING,
            triad_pair=triad_pair,
            contour="alternating"
        )
    
    def generate_rotation(
        self, 
        triad_pair: TriadPair,
        rotation_type: str = "132",
        duration: float = 0.5,
        string_set: str = "auto"
    ) -> MelodicCell:
        """
        Generate rotation pattern.
        
        Args:
            triad_pair: Source triad pair
            rotation_type: "132", "312", "213", or "321"
            duration: Note duration
            string_set: Guitar string set
        """
        rotation_map = {
            "132": [0, 2, 1],
            "312": [2, 0, 1],
            "213": [1, 0, 2],
            "321": [2, 1, 0],
        }
        order = rotation_map.get(rotation_type, [0, 2, 1])
        
        pattern_type_map = {
            "132": PatternType.ROTATION_132,
            "312": PatternType.ROTATION_312,
            "213": PatternType.ROTATION_213,
            "321": PatternType.ROTATION_321,
        }
        
        notes = []
        pitches_a = self._get_triad_pitches(triad_pair.triad_a[0], triad_pair.triad_a[1])
        pitches_b = self._get_triad_pitches(triad_pair.triad_b[0], triad_pair.triad_b[1])
        
        # Apply rotation to triad A
        for i in order:
            pitch = pitches_a[i]
            string, fret = self._get_guitar_position(pitch, string_set)
            notes.append(PatternNote(
                pitch=pitch,
                pitch_name=self._midi_to_note_name(pitch),
                duration=duration,
                triad_source="A",
                voice=i + 1,
                string=string,
                fret=fret
            ))
        
        # Apply rotation to triad B
        for i in order:
            pitch = pitches_b[i]
            string, fret = self._get_guitar_position(pitch, string_set)
            notes.append(PatternNote(
                pitch=pitch,
                pitch_name=self._midi_to_note_name(pitch),
                duration=duration,
                triad_source="B",
                voice=i + 1,
                string=string,
                fret=fret
            ))
        
        return MelodicCell(
            notes=notes,
            pattern_type=pattern_type_map.get(rotation_type, PatternType.ROTATION_132),
            triad_pair=triad_pair,
            contour="rotated"
        )
    
    def generate_interval_skip(
        self, 
        triad_pair: TriadPair,
        skip_size: int = 2,
        duration: float = 0.5,
        string_set: str = "auto"
    ) -> MelodicCell:
        """
        Generate large interval skips between triads.
        
        Args:
            triad_pair: Source triad pair
            skip_size: Number of voices to skip (1-2)
            duration: Note duration
            string_set: Guitar string set
        """
        notes = []
        pitches_a = self._get_triad_pitches(triad_pair.triad_a[0], triad_pair.triad_a[1])
        pitches_b = self._get_triad_pitches(
            triad_pair.triad_b[0], triad_pair.triad_b[1],
            self.base_octave + 1
        )
        
        # Create skip pattern
        combined = [(p, "A", i) for i, p in enumerate(pitches_a)]
        combined += [(p, "B", i) for i, p in enumerate(pitches_b)]
        
        # Sort by pitch
        combined.sort(key=lambda x: x[0])
        
        # Apply skip
        indices = list(range(0, len(combined), skip_size + 1))
        indices += list(range(len(combined) - 1, -1, -(skip_size + 1)))
        
        seen = set()
        for idx in indices:
            if idx < len(combined) and idx not in seen:
                seen.add(idx)
                pitch, source, voice = combined[idx]
                string, fret = self._get_guitar_position(pitch, string_set)
                notes.append(PatternNote(
                    pitch=pitch,
                    pitch_name=self._midi_to_note_name(pitch),
                    duration=duration,
                    triad_source=source,
                    voice=voice + 1,
                    string=string,
                    fret=fret
                ))
        
        return MelodicCell(
            notes=notes,
            pattern_type=PatternType.INTERVAL_SKIP,
            triad_pair=triad_pair,
            contour="skipwise"
        )
    
    def generate_wave(
        self, 
        triad_pair: TriadPair,
        wave_size: int = 2,
        duration: float = 0.5,
        string_set: str = "auto"
    ) -> MelodicCell:
        """
        Generate directional wave pattern.
        
        Args:
            triad_pair: Source triad pair
            wave_size: Number of notes per wave segment
            duration: Note duration
            string_set: Guitar string set
        """
        notes = []
        pitches_a = self._get_triad_pitches(triad_pair.triad_a[0], triad_pair.triad_a[1])
        pitches_b = self._get_triad_pitches(triad_pair.triad_b[0], triad_pair.triad_b[1])
        
        # Combine and create wave
        all_pitches = []
        for i, p in enumerate(pitches_a):
            all_pitches.append((p, "A", i))
        for i, p in enumerate(pitches_b):
            all_pitches.append((p, "B", i))
        
        # Sort by pitch for wave construction
        all_pitches.sort(key=lambda x: x[0])
        
        # Generate wave: up wave_size, down wave_size-1, repeat
        idx = 0
        direction = 1
        visited = []
        
        while len(visited) < len(all_pitches):
            if 0 <= idx < len(all_pitches) and idx not in [v[0] for v in visited]:
                visited.append((idx, all_pitches[idx]))
            
            idx += direction
            
            # Bounce at edges
            if idx >= len(all_pitches):
                direction = -1
                idx = len(all_pitches) - 2
            elif idx < 0:
                direction = 1
                idx = 1
            
            # Prevent infinite loop
            if len(visited) > len(all_pitches) * 2:
                break
        
        for _, (pitch, source, voice) in visited:
            string, fret = self._get_guitar_position(pitch, string_set)
            notes.append(PatternNote(
                pitch=pitch,
                pitch_name=self._midi_to_note_name(pitch),
                duration=duration,
                triad_source=source,
                voice=voice + 1,
                string=string,
                fret=fret
            ))
        
        return MelodicCell(
            notes=notes,
            pattern_type=PatternType.WAVE,
            triad_pair=triad_pair,
            contour="wave"
        )
    
    def generate_pivot_tone(
        self, 
        triad_pair: TriadPair,
        pivot_voice: int = 1,
        duration: float = 0.5,
        string_set: str = "auto"
    ) -> MelodicCell:
        """
        Generate pivot-tone pattern using a common or nearby tone.
        
        Args:
            triad_pair: Source triad pair
            pivot_voice: Which voice to use as pivot (1=root, 2=third, 3=fifth)
            duration: Note duration
            string_set: Guitar string set
        """
        notes = []
        pitches_a = self._get_triad_pitches(triad_pair.triad_a[0], triad_pair.triad_a[1])
        pitches_b = self._get_triad_pitches(triad_pair.triad_b[0], triad_pair.triad_b[1])
        
        pivot_idx = (pivot_voice - 1) % 3
        pivot_pitch = pitches_a[pivot_idx]
        
        # Pattern: pivot - other A notes - pivot - other B notes
        string, fret = self._get_guitar_position(pivot_pitch, string_set)
        notes.append(PatternNote(
            pitch=pivot_pitch,
            pitch_name=self._midi_to_note_name(pivot_pitch),
            duration=duration,
            triad_source="A",
            voice=pivot_idx + 1,
            string=string,
            fret=fret,
            articulation="accent"
        ))
        
        for i, pitch in enumerate(pitches_a):
            if i != pivot_idx:
                string, fret = self._get_guitar_position(pitch, string_set)
                notes.append(PatternNote(
                    pitch=pitch,
                    pitch_name=self._midi_to_note_name(pitch),
                    duration=duration,
                    triad_source="A",
                    voice=i + 1,
                    string=string,
                    fret=fret
                ))
        
        # Pivot again
        notes.append(PatternNote(
            pitch=pivot_pitch,
            pitch_name=self._midi_to_note_name(pivot_pitch),
            duration=duration,
            triad_source="A",
            voice=pivot_idx + 1,
            string=string,
            fret=fret,
            articulation="accent"
        ))
        
        for i, pitch in enumerate(pitches_b):
            string, fret = self._get_guitar_position(pitch, string_set)
            notes.append(PatternNote(
                pitch=pitch,
                pitch_name=self._midi_to_note_name(pitch),
                duration=duration,
                triad_source="B",
                voice=i + 1,
                string=string,
                fret=fret
            ))
        
        return MelodicCell(
            notes=notes,
            pattern_type=PatternType.PIVOT_TONE,
            triad_pair=triad_pair,
            contour="pivot"
        )
    
    def generate_sequence(
        self, 
        triad_pairs: List[TriadPair],
        pattern_type: PatternType = PatternType.UP_ARPEGGIO,
        duration: float = 0.5,
        string_set: str = "auto"
    ) -> List[MelodicCell]:
        """
        Generate a sequence of patterns over multiple triad pairs.
        
        Args:
            triad_pairs: List of triad pairs to sequence through
            pattern_type: Pattern type to use for each
            duration: Note duration
            string_set: Guitar string set
        
        Returns:
            List of MelodicCell objects
        """
        cells = []
        
        pattern_generators = {
            PatternType.UP_ARPEGGIO: self.generate_up_arpeggio,
            PatternType.DOWN_ARPEGGIO: self.generate_down_arpeggio,
            PatternType.ALTERNATING: self.generate_alternating,
            PatternType.ROTATION_132: lambda tp, d, s: self.generate_rotation(tp, "132", d, s),
            PatternType.ROTATION_312: lambda tp, d, s: self.generate_rotation(tp, "312", d, s),
            PatternType.WAVE: self.generate_wave,
            PatternType.PIVOT_TONE: self.generate_pivot_tone,
            PatternType.INTERVAL_SKIP: self.generate_interval_skip,
        }
        
        generator = pattern_generators.get(
            pattern_type, 
            self.generate_up_arpeggio
        )
        
        for tp in triad_pairs:
            cell = generator(tp, duration, string_set)
            cells.append(cell)
        
        return cells
    
    def generate_for_contour(
        self,
        triad_pair: TriadPair,
        contour: ContourType,
        duration: float = 0.5,
        string_set: str = "auto"
    ) -> MelodicCell:
        """
        Generate a pattern that matches the specified contour.
        
        Args:
            triad_pair: Source triad pair
            contour: Desired melodic contour
            duration: Note duration
            string_set: Guitar string set
        
        Returns:
            MelodicCell with appropriate contour
        """
        contour_to_pattern = {
            ContourType.ASCENDING: self.generate_up_arpeggio,
            ContourType.DESCENDING: self.generate_down_arpeggio,
            ContourType.WAVE: self.generate_wave,
            ContourType.ZIGZAG: self.generate_alternating,
            ContourType.RANDOM_SEEDED: self._generate_random_pattern,
        }
        
        generator = contour_to_pattern.get(contour, self.generate_wave)
        return generator(triad_pair, duration, string_set)
    
    def _generate_random_pattern(
        self,
        triad_pair: TriadPair,
        duration: float = 0.5,
        string_set: str = "auto"
    ) -> MelodicCell:
        """Generate a random pattern (seeded for reproducibility)."""
        pattern_choices = [
            self.generate_up_arpeggio,
            self.generate_down_arpeggio,
            self.generate_alternating,
            self.generate_wave,
            lambda tp, d, s: self.generate_rotation(tp, "132", d, s),
            lambda tp, d, s: self.generate_rotation(tp, "312", d, s),
        ]
        
        generator = random.choice(pattern_choices)
        return generator(triad_pair, duration, string_set)
    
    def stitch_cells_to_bar(
        self,
        cells: List[MelodicCell],
        bar_length: float = 4.0
    ) -> List[PatternNote]:
        """
        Stitch multiple melodic cells into bar-length phrases.
        
        Args:
            cells: List of MelodicCell objects
            bar_length: Target bar length in beats
        
        Returns:
            List of PatternNote objects forming a bar
        """
        bar_notes = []
        current_duration = 0.0
        
        for cell in cells:
            for note in cell.notes:
                if current_duration >= bar_length:
                    break
                
                # Adjust duration if it would exceed bar length
                remaining = bar_length - current_duration
                adjusted_note = PatternNote(
                    pitch=note.pitch,
                    pitch_name=note.pitch_name,
                    duration=min(note.duration, remaining),
                    triad_source=note.triad_source,
                    voice=note.voice,
                    string=note.string,
                    fret=note.fret,
                    articulation=note.articulation
                )
                bar_notes.append(adjusted_note)
                current_duration += adjusted_note.duration
            
            if current_duration >= bar_length:
                break
        
        return bar_notes

