"""
General Musical Language (GML) Data Structures
===============================================

GML provides instrument-agnostic representations of musical material:
- Notes with pitch class, octave, duration, onset
- Phrases as sequences of notes with harmonic context
- Progressions as sequences of chord functions
- Sections as collections of phrases with formal roles
- Forms as templates (AABA, ABAC, blues, etc.)

All structures are designed to be stateless and deterministic.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum


class PhraseRole(Enum):
    """Role of a phrase within a section or form."""
    OPENING = "opening"
    CONTINUATION = "continuation"
    CADENTIAL = "cadential"
    TRANSITION = "transition"
    CLOSING = "closing"
    UNKNOWN = "unknown"


class HarmonicFunction(Enum):
    """Harmonic function in a progression."""
    TONIC = "tonic"
    SUBDOMINANT = "subdominant"
    DOMINANT = "dominant"
    PRE_DOMINANT = "pre_dominant"
    SUBSTITUTE = "substitute"
    PASSING = "passing"
    PEDAL = "pedal"
    UNKNOWN = "unknown"


@dataclass
class GMLNote:
    """
    A single note in GML format.
    
    Attributes:
        pitch_class: Pitch class (0-11, where 0=C, 1=C#, etc.)
        octave: Octave number (middle C = 4)
        duration: Duration in beats
        onset: Start time in beats from phrase/section start
        is_rest: Whether this is a rest
        articulation: Optional articulation marking
        harmonic_context: Optional chord symbol at this moment
    """
    pitch_class: int
    octave: int = 4
    duration: float = 0.5
    onset: float = 0.0
    is_rest: bool = False
    articulation: Optional[str] = None
    harmonic_context: Optional[str] = None
    
    @property
    def midi_pitch(self) -> int:
        """Get MIDI pitch number (60 = C4)."""
        return (self.octave + 1) * 12 + self.pitch_class
    
    @property
    def pitch_name(self) -> str:
        """Get note name (e.g., 'C', 'F#')."""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return note_names[self.pitch_class]
    
    def interval_to(self, other: 'GMLNote') -> int:
        """Get interval in semitones to another note."""
        return other.midi_pitch - self.midi_pitch
    
    def is_stepwise_to(self, other: 'GMLNote') -> bool:
        """Check if motion to another note is stepwise (m2 or M2)."""
        interval = abs(self.interval_to(other))
        return interval in {1, 2}
    
    def __repr__(self) -> str:
        if self.is_rest:
            return f"Rest(dur={self.duration})"
        return f"{self.pitch_name}{self.octave}(dur={self.duration}, onset={self.onset})"


@dataclass
class GMLPhrase:
    """
    A musical phrase in GML format.
    
    Attributes:
        notes: List of GMLNote objects
        bar_start: Starting bar number (1-indexed)
        bar_end: Ending bar number (1-indexed)
        role: Phrase role within section
        harmonic_progression: Optional list of chord symbols
        key: Key signature (e.g., "C", "F#")
        time_signature: Tuple of (beats_per_bar, beat_value)
    """
    notes: List[GMLNote]
    bar_start: int = 1
    bar_end: int = 1
    role: PhraseRole = PhraseRole.UNKNOWN
    harmonic_progression: Optional[List[str]] = None
    key: str = "C"
    time_signature: Tuple[int, int] = (4, 4)
    
    def __post_init__(self):
        """Validate and set defaults."""
        if self.harmonic_progression is None:
            self.harmonic_progression = []
        if not self.notes:
            self.bar_end = self.bar_start
    
    @property
    def duration(self) -> float:
        """Get total duration in beats."""
        if not self.notes:
            return 0.0
        last_note = self.notes[-1]
        return last_note.onset + last_note.duration
    
    @property
    def bar_count(self) -> int:
        """Get number of bars."""
        return max(1, self.bar_end - self.bar_start + 1)
    
    def get_notes_in_bar(self, bar: int) -> List[GMLNote]:
        """Get all notes in a specific bar."""
        if bar < self.bar_start or bar > self.bar_end:
            return []
        return [n for n in self.notes if self.bar_start <= bar <= self.bar_end]
    
    def get_pitch_classes(self) -> List[int]:
        """Get list of pitch classes (excluding rests)."""
        return [n.pitch_class for n in self.notes if not n.is_rest]
    
    def get_pitch_range(self) -> Tuple[int, int]:
        """Get lowest and highest MIDI pitches."""
        pitches = [n.midi_pitch for n in self.notes if not n.is_rest]
        if not pitches:
            return (60, 60)  # Default to C4
        return (min(pitches), max(pitches))
    
    def get_chord_at_beat(self, beat: float) -> Optional[str]:
        """Get chord symbol at a specific beat (if harmonic_progression provided)."""
        if not self.harmonic_progression:
            return None
        
        beats_per_bar = self.time_signature[0]
        bar = int(beat // beats_per_bar)
        bar_in_phrase = bar - self.bar_start
        
        if 0 <= bar_in_phrase < len(self.harmonic_progression):
            return self.harmonic_progression[bar_in_phrase]
        return None


@dataclass
class GMLProgression:
    """
    A chord progression in GML format.
    
    Attributes:
        chords: List of chord symbols (e.g., ["Cm7", "F7", "BbMaj7"])
        functions: Optional list of harmonic functions
        key: Key signature
        bars_per_chord: Optional list of bar counts per chord
    """
    chords: List[str]
    functions: Optional[List[HarmonicFunction]] = None
    key: str = "C"
    bars_per_chord: Optional[List[int]] = None
    
    def __post_init__(self):
        """Validate and set defaults."""
        if self.bars_per_chord is None:
            self.bars_per_chord = [1] * len(self.chords)
        if self.functions is None:
            self.functions = [HarmonicFunction.UNKNOWN] * len(self.chords)
    
    @property
    def length(self) -> int:
        """Get number of chords."""
        return len(self.chords)
    
    @property
    def total_bars(self) -> int:
        """Get total number of bars."""
        return sum(self.bars_per_chord)
    
    def get_chord_at_bar(self, bar: int) -> Optional[str]:
        """Get chord symbol at a specific bar (1-indexed)."""
        current_bar = 1
        for i, (chord, bars) in enumerate(zip(self.chords, self.bars_per_chord)):
            if current_bar <= bar < current_bar + bars:
                return chord
            current_bar += bars
        return None


class GMLForm(Enum):
    """Musical form templates."""
    AABA = "aaba"
    ABAC = "abac"
    BLUES_12 = "blues_12"
    BLUES_16 = "blues_16"
    RONDO = "rondo"
    THROUGH_COMPOSED = "through_composed"
    CUSTOM = "custom"


@dataclass
class GMLSection:
    """
    A section of a composition in GML format.
    
    Attributes:
        phrases: List of GMLPhrase objects
        label: Section label (e.g., "A", "B", "Bridge")
        form: Form type
        key: Key signature
        time_signature: Tuple of (beats_per_bar, beat_value)
        metadata: Additional metadata
    """
    phrases: List[GMLPhrase]
    label: str = "A"
    form: GMLForm = GMLForm.CUSTOM
    key: str = "C"
    time_signature: Tuple[int, int] = (4, 4)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def bar_count(self) -> int:
        """Get total number of bars."""
        if not self.phrases:
            return 0
        return max(p.bar_end for p in self.phrases)
    
    @property
    def duration(self) -> float:
        """Get total duration in beats."""
        return sum(p.duration for p in self.phrases)
    
    def get_phrase_by_role(self, role: PhraseRole) -> List[GMLPhrase]:
        """Get all phrases with a specific role."""
        return [p for p in self.phrases if p.role == role]
    
    def get_cadential_phrases(self) -> List[GMLPhrase]:
        """Get all cadential phrases."""
        return self.get_phrase_by_role(PhraseRole.CADENTIAL)


# Helper functions for creating GML structures

def note_from_midi(midi_pitch: int, duration: float = 0.5, onset: float = 0.0) -> GMLNote:
    """Create a GMLNote from a MIDI pitch number."""
    octave = (midi_pitch // 12) - 1
    pitch_class = midi_pitch % 12
    return GMLNote(
        pitch_class=pitch_class,
        octave=octave,
        duration=duration,
        onset=onset
    )


def note_from_name(note_name: str, octave: int = 4, duration: float = 0.5, onset: float = 0.0) -> GMLNote:
    """Create a GMLNote from a note name (e.g., 'C', 'F#')."""
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    # Handle flats
    flat_map = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}
    note_name = flat_map.get(note_name, note_name)
    
    try:
        pitch_class = note_names.index(note_name)
    except ValueError:
        pitch_class = 0  # Default to C
    
    return GMLNote(
        pitch_class=pitch_class,
        octave=octave,
        duration=duration,
        onset=onset
    )


def phrase_from_pitches(
    pitches: List[int],
    durations: Optional[List[float]] = None,
    key: str = "C",
    bar_start: int = 1
) -> GMLPhrase:
    """Create a GMLPhrase from a list of MIDI pitches."""
    if durations is None:
        durations = [0.5] * len(pitches)
    
    notes = []
    current_onset = 0.0
    
    for i, pitch in enumerate(pitches):
        duration = durations[i] if i < len(durations) else 0.5
        note = note_from_midi(pitch, duration, current_onset)
        notes.append(note)
        current_onset += duration
    
    beats_per_bar = 4  # Default
    total_beats = current_onset
    bar_end = bar_start + int(total_beats // beats_per_bar)
    
    return GMLPhrase(
        notes=notes,
        bar_start=bar_start,
        bar_end=bar_end,
        key=key
    )

