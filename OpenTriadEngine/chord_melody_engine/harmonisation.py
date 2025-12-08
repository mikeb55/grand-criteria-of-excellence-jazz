"""
Harmonisation Engine for Chord-Melody Engine
==============================================

Implements multiple harmonisation modes:
- Diatonic: Scale-degree triads with modal interchange
- Reharm: Chromatic approaches, secondary dominants, tritone subs
- UST: Upper Structure Triads for tensions
- Functional: APVL + TRAM for ii-V-I motion
- Modal: Static color, reduced functional pull
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum

try:
    from .inputs import ChordMelodyConfig, HarmonisationStyle
    from .melody import MelodyNote, Melody
except ImportError:
    from inputs import ChordMelodyConfig, HarmonisationStyle
    from melody import MelodyNote, Melody


@dataclass
class TriadOption:
    """
    Represents a possible triad harmonisation for a melody note.
    
    Attributes:
        root: Root note name
        quality: Triad quality (major, minor, dim, aug)
        pitches: MIDI pitches (root, third, fifth)
        inversion: Inversion number (0, 1, 2)
        relationship: How this triad relates to the melody note
        tension_level: 0.0 (consonant) to 1.0 (dissonant)
        function: Harmonic function (tonic, subdominant, dominant)
    """
    root: str
    quality: str
    pitches: List[int]
    inversion: int = 0
    relationship: str = "contains_melody"
    tension_level: float = 0.3
    function: Optional[str] = None
    
    def __repr__(self):
        return f"{self.root}{self.quality}(inv{self.inversion})"
    
    def get_top_pitch(self) -> int:
        """Get the highest pitch in this voicing."""
        return max(self.pitches)


@dataclass
class HarmonisedMoment:
    """
    A single harmonised moment (melody note + harmony).
    
    Attributes:
        melody_note: The original melody note
        triad: The chosen triad harmonisation
        all_options: All available triad options considered
        voice_leading_info: Info about voice-leading from previous moment
        analysis: Harmonic analysis explanation
    """
    melody_note: MelodyNote
    triad: Optional[TriadOption]
    all_options: List[TriadOption] = field(default_factory=list)
    voice_leading_info: Optional[Dict] = None
    analysis: str = ""


class HarmonisationEngine:
    """
    Main harmonisation engine with multiple modes.
    """
    
    # Note to MIDI mapping
    NOTE_TO_MIDI = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
        "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
        "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
    }
    
    MIDI_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    # Scale patterns (intervals from root)
    SCALE_PATTERNS = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "aeolian": [0, 2, 3, 5, 7, 8, 10],
        "locrian": [0, 1, 3, 5, 6, 8, 10],
        "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
        "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    }
    
    # Triad qualities for scale degrees (major scale)
    MAJOR_SCALE_TRIADS = [
        ("major", "tonic"), ("minor", "supertonic"), ("minor", "mediant"),
        ("major", "subdominant"), ("major", "dominant"), ("minor", "submediant"),
        ("dim", "leading")
    ]
    
    # Triad intervals from root
    TRIAD_INTERVALS = {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "dim": [0, 3, 6],
        "aug": [0, 4, 8],
        "sus2": [0, 2, 7],
        "sus4": [0, 5, 7],
    }
    
    # UST triads for dominant chords
    UST_DOMINANT = {
        "7alt": [("Eb", "major"), ("E", "major"), ("F#", "major"), ("Ab", "major")],
        "7#11": [("D", "major"), ("F#", "dim")],
        "7b9": [("Ab", "major"), ("B", "dim")],
        "13": [("E", "minor"), ("A", "minor")],
    }
    
    def __init__(self, config: ChordMelodyConfig):
        """
        Initialize the harmonisation engine.
        
        Args:
            config: Chord-melody configuration
        """
        self.config = config
        self.key = config.key
        self.scale = config.scale
        self.style = config.harmonisation_style
        self.key_midi = self.NOTE_TO_MIDI.get(config.key, 0)
    
    def _get_scale_notes(self) -> List[int]:
        """Get the scale notes as pitch classes."""
        pattern = self.SCALE_PATTERNS.get(self.scale, self.SCALE_PATTERNS["major"])
        return [(self.key_midi + interval) % 12 for interval in pattern]
    
    def _get_note_at_interval(self, root: str, semitones: int) -> str:
        """Get note name at interval from root."""
        root_midi = self.NOTE_TO_MIDI.get(root, 0)
        target = (root_midi + semitones) % 12
        return self.MIDI_TO_NOTE[target]
    
    def _build_triad(
        self,
        root: str,
        quality: str,
        base_octave: int = 4
    ) -> List[int]:
        """Build triad pitches from root and quality."""
        root_midi = self.NOTE_TO_MIDI.get(root, 0) + (base_octave + 1) * 12
        intervals = self.TRIAD_INTERVALS.get(quality, self.TRIAD_INTERVALS["major"])
        return [root_midi + interval for interval in intervals]
    
    def _apply_inversion(
        self,
        pitches: List[int],
        inversion: int
    ) -> List[int]:
        """Apply inversion to a triad."""
        if inversion == 0:
            return pitches
        elif inversion == 1:
            return [pitches[1], pitches[2], pitches[0] + 12]
        elif inversion == 2:
            return [pitches[2], pitches[0] + 12, pitches[1] + 12]
        return pitches
    
    def _melody_in_triad(self, melody_pitch: int, triad_pitches: List[int]) -> bool:
        """Check if melody pitch class is contained in triad."""
        melody_pc = melody_pitch % 12
        triad_pcs = [p % 12 for p in triad_pitches]
        return melody_pc in triad_pcs
    
    def _find_inversion_with_melody_on_top(
        self,
        triad_pitches: List[int],
        melody_pitch: int
    ) -> Tuple[List[int], int]:
        """
        Find the inversion that places melody on top.
        
        Returns:
            Tuple of (adjusted_pitches, inversion_number)
        """
        melody_pc = melody_pitch % 12
        
        for inv in range(3):
            inverted = self._apply_inversion(triad_pitches, inv)
            
            # Adjust octave so top note matches melody pitch class
            top_pc = inverted[-1] % 12
            if top_pc == melody_pc:
                # Calculate octave adjustment
                target_octave = melody_pitch // 12
                current_octave = inverted[-1] // 12
                octave_shift = (target_octave - current_octave) * 12
                
                adjusted = [p + octave_shift for p in inverted]
                
                # Verify melody is on top
                if adjusted[-1] == melody_pitch:
                    return adjusted, inv
        
        # Fallback: force melody on top
        return self._force_melody_on_top(triad_pitches, melody_pitch)
    
    def _force_melody_on_top(
        self,
        triad_pitches: List[int],
        melody_pitch: int
    ) -> Tuple[List[int], int]:
        """Force arrangement with melody on top."""
        melody_pc = melody_pitch % 12
        
        # Find which voice matches melody pitch class
        for i, p in enumerate(triad_pitches):
            if p % 12 == melody_pc:
                # Rearrange so this voice is on top
                new_pitches = [melody_pitch]
                for j, other_p in enumerate(triad_pitches):
                    if j != i:
                        # Place other notes below melody
                        adjusted = other_p
                        while adjusted >= melody_pitch:
                            adjusted -= 12
                        new_pitches.insert(0, adjusted)
                return sorted(new_pitches), i
        
        # If melody not in triad, just place triad below
        adjusted = []
        for p in triad_pitches:
            while p >= melody_pitch:
                p -= 12
            adjusted.append(p)
        return sorted(adjusted) + [melody_pitch], 0
    
    def get_diatonic_options(
        self,
        melody_note: MelodyNote
    ) -> List[TriadOption]:
        """
        Get diatonic triad options for a melody note.
        
        Args:
            melody_note: The melody note to harmonise
        
        Returns:
            List of possible TriadOption harmonisations
        """
        options = []
        melody_pc = melody_note.pitch % 12
        scale_notes = self._get_scale_notes()
        
        # Get scale-degree triads
        for degree, (quality, function) in enumerate(self.MAJOR_SCALE_TRIADS):
            root_pc = scale_notes[degree]
            root_name = self.MIDI_TO_NOTE[root_pc]
            
            # Build triad
            base_pitches = self._build_triad(root_name, quality)
            
            # Check if melody is in this triad
            if self._melody_in_triad(melody_note.pitch, base_pitches):
                # Find best inversion for melody on top
                adjusted_pitches, inv = self._find_inversion_with_melody_on_top(
                    base_pitches, melody_note.pitch
                )
                
                # Calculate tension based on function
                tension = 0.2 if function == "tonic" else 0.5 if function == "dominant" else 0.3
                
                options.append(TriadOption(
                    root=root_name,
                    quality=quality,
                    pitches=adjusted_pitches,
                    inversion=inv,
                    relationship="diatonic",
                    tension_level=tension,
                    function=function
                ))
        
        # Modal interchange options
        if self.config.allow_modal_interchange:
            options.extend(self._get_modal_interchange_options(melody_note))
        
        return options
    
    def _get_modal_interchange_options(
        self,
        melody_note: MelodyNote
    ) -> List[TriadOption]:
        """Get modal interchange (borrowed chord) options."""
        options = []
        melody_pc = melody_note.pitch % 12
        
        # Common borrowed chords
        borrowed = [
            ("bVI", "major", 8),   # From parallel minor
            ("bVII", "major", 10), # From mixolydian
            ("iv", "minor", 5),    # From minor
            ("bIII", "major", 3),  # From minor
        ]
        
        for name, quality, interval in borrowed:
            root_pc = (self.key_midi + interval) % 12
            root_name = self.MIDI_TO_NOTE[root_pc]
            base_pitches = self._build_triad(root_name, quality)
            
            if self._melody_in_triad(melody_note.pitch, base_pitches):
                adjusted, inv = self._find_inversion_with_melody_on_top(
                    base_pitches, melody_note.pitch
                )
                
                options.append(TriadOption(
                    root=root_name,
                    quality=quality,
                    pitches=adjusted,
                    inversion=inv,
                    relationship=f"modal_interchange_{name}",
                    tension_level=0.6,
                    function="borrowed"
                ))
        
        return options
    
    def get_reharm_options(
        self,
        melody_note: MelodyNote
    ) -> List[TriadOption]:
        """
        Get reharmonisation options including chromatic approaches,
        secondary dominants, and tritone substitutions.
        """
        options = self.get_diatonic_options(melody_note)  # Start with diatonic
        melody_pc = melody_note.pitch % 12
        
        # Chromatic approach triads (half-step above/below)
        for offset in [-1, 1]:
            approach_root_pc = (melody_pc + offset) % 12
            approach_root = self.MIDI_TO_NOTE[approach_root_pc]
            
            for quality in ["major", "minor", "dim"]:
                base_pitches = self._build_triad(approach_root, quality)
                
                if self._melody_in_triad(melody_note.pitch, base_pitches):
                    adjusted, inv = self._find_inversion_with_melody_on_top(
                        base_pitches, melody_note.pitch
                    )
                    
                    options.append(TriadOption(
                        root=approach_root,
                        quality=quality,
                        pitches=adjusted,
                        inversion=inv,
                        relationship="chromatic_approach",
                        tension_level=0.7,
                        function="passing"
                    ))
        
        # Tritone substitution triads
        tritone_root_pc = (self.key_midi + 6) % 12  # bV
        tritone_root = self.MIDI_TO_NOTE[tritone_root_pc]
        base_pitches = self._build_triad(tritone_root, "major")
        
        if self._melody_in_triad(melody_note.pitch, base_pitches):
            adjusted, inv = self._find_inversion_with_melody_on_top(
                base_pitches, melody_note.pitch
            )
            
            options.append(TriadOption(
                root=tritone_root,
                quality="major",
                pitches=adjusted,
                inversion=inv,
                relationship="tritone_sub",
                tension_level=0.8,
                function="dominant_sub"
            ))
        
        return options
    
    def get_ust_options(
        self,
        melody_note: MelodyNote,
        chord_context: Optional[str] = None
    ) -> List[TriadOption]:
        """
        Get Upper Structure Triad options.
        
        Treats melody as part of an upper structure voicing,
        finding triads that support chord tensions.
        """
        options = []
        melody_pc = melody_note.pitch % 12
        
        # Determine chord type from context or default to dominant
        chord_type = "7alt"
        if chord_context:
            if "alt" in chord_context.lower():
                chord_type = "7alt"
            elif "#11" in chord_context:
                chord_type = "7#11"
            elif "b9" in chord_context:
                chord_type = "7b9"
            elif "13" in chord_context:
                chord_type = "13"
        
        ust_triads = self.UST_DOMINANT.get(chord_type, self.UST_DOMINANT["7alt"])
        
        for root, quality in ust_triads:
            # Transpose to current key
            original_root_pc = self.NOTE_TO_MIDI.get(root, 0)
            transposed_root_pc = (original_root_pc + self.key_midi) % 12
            transposed_root = self.MIDI_TO_NOTE[transposed_root_pc]
            
            base_pitches = self._build_triad(transposed_root, quality)
            
            if self._melody_in_triad(melody_note.pitch, base_pitches):
                adjusted, inv = self._find_inversion_with_melody_on_top(
                    base_pitches, melody_note.pitch
                )
                
                options.append(TriadOption(
                    root=transposed_root,
                    quality=quality,
                    pitches=adjusted,
                    inversion=inv,
                    relationship=f"ust_{chord_type}",
                    tension_level=0.85,
                    function="tension"
                ))
        
        return options
    
    def get_functional_options(
        self,
        melody_note: MelodyNote,
        previous_harmony: Optional[TriadOption] = None
    ) -> List[TriadOption]:
        """
        Get functional harmony options optimised for ii-V-I motion.
        Uses APVL and TRAM concepts for voice-leading.
        """
        options = self.get_diatonic_options(melody_note)
        
        # Prioritise by function for smooth resolution
        if previous_harmony:
            prev_function = previous_harmony.function
            
            # Functional progression preferences
            if prev_function == "supertonic":
                # ii should go to V
                options = sorted(options, 
                    key=lambda x: 0 if x.function == "dominant" else 1)
            elif prev_function == "dominant":
                # V should go to I
                options = sorted(options,
                    key=lambda x: 0 if x.function == "tonic" else 1)
        
        return options
    
    def get_modal_options(
        self,
        melody_note: MelodyNote
    ) -> List[TriadOption]:
        """
        Get modal harmonisation options with reduced functional pull.
        Emphasises static color and SISM spacing.
        """
        options = self.get_diatonic_options(melody_note)
        
        # Prefer non-dominant triads for modal stability
        modal_options = []
        for opt in options:
            if opt.function in ["tonic", "subdominant", "mediant", "submediant"]:
                opt.tension_level *= 0.8  # Reduce perceived tension
                modal_options.append(opt)
            elif opt.function == "dominant":
                opt.tension_level = 0.7  # Higher tension for dominant in modal
                modal_options.append(opt)
            else:
                modal_options.append(opt)
        
        # Add sus chords for modal color
        for root_offset in [0, 5, 7]:  # I, IV, V roots
            root_pc = (self.key_midi + root_offset) % 12
            root_name = self.MIDI_TO_NOTE[root_pc]
            
            for sus_type in ["sus2", "sus4"]:
                base_pitches = self._build_triad(root_name, sus_type)
                
                if self._melody_in_triad(melody_note.pitch, base_pitches):
                    adjusted, inv = self._find_inversion_with_melody_on_top(
                        base_pitches, melody_note.pitch
                    )
                    
                    modal_options.append(TriadOption(
                        root=root_name,
                        quality=sus_type,
                        pitches=adjusted,
                        inversion=inv,
                        relationship="modal_sus",
                        tension_level=0.25,
                        function="modal_color"
                    ))
        
        return modal_options
    
    def harmonise_melody(
        self,
        melody: Melody
    ) -> List[HarmonisedMoment]:
        """
        Harmonise an entire melody.
        
        Args:
            melody: The melody to harmonise
        
        Returns:
            List of HarmonisedMoment objects
        """
        harmonised = []
        previous_harmony = None
        
        for note in melody.notes:
            if note.is_rest:
                # Create a rest moment
                moment = HarmonisedMoment(
                    melody_note=note,
                    triad=None,
                    analysis="Rest"
                )
            else:
                # Get options based on style
                if self.style == HarmonisationStyle.DIATONIC:
                    options = self.get_diatonic_options(note)
                elif self.style == HarmonisationStyle.REHARM:
                    options = self.get_reharm_options(note)
                elif self.style == HarmonisationStyle.UST:
                    options = self.get_ust_options(note, note.chord_context)
                elif self.style == HarmonisationStyle.FUNCTIONAL:
                    options = self.get_functional_options(note, previous_harmony)
                elif self.style == HarmonisationStyle.MODAL:
                    options = self.get_modal_options(note)
                else:
                    options = self.get_diatonic_options(note)
                
                # Choose best option
                if options:
                    # Sort by tension level (prefer lower tension by default)
                    options.sort(key=lambda x: x.tension_level)
                    chosen = options[0]
                    
                    moment = HarmonisedMoment(
                        melody_note=note,
                        triad=chosen,
                        all_options=options,
                        analysis=f"{chosen.root}{chosen.quality} ({chosen.relationship})"
                    )
                    previous_harmony = chosen
                else:
                    # No harmony found
                    moment = HarmonisedMoment(
                        melody_note=note,
                        triad=None,
                        analysis="No suitable harmony"
                    )
            
            harmonised.append(moment)
        
        return harmonised
    
    def get_all_options_for_note(
        self,
        melody_note: MelodyNote
    ) -> Dict[str, List[TriadOption]]:
        """
        Get all harmonisation options from all modes for a single note.
        
        Args:
            melody_note: The melody note
        
        Returns:
            Dictionary mapping style name to list of options
        """
        return {
            "diatonic": self.get_diatonic_options(melody_note),
            "reharm": self.get_reharm_options(melody_note),
            "ust": self.get_ust_options(melody_note),
            "functional": self.get_functional_options(melody_note),
            "modal": self.get_modal_options(melody_note),
        }

