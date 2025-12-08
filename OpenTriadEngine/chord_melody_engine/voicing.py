"""
Voicing Generation Module for Chord-Melody Engine
===================================================

Generates playable guitar voicings:
1. Map melody to top voice
2. Assign open-triad inversion below
3. Check string-set feasibility
4. Adjust register if needed
5. Optionally expand to 4-note voicing
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum

try:
    from .inputs import ChordMelodyConfig, VoicingDensity, Difficulty
    from .melody import MelodyNote
    from .harmonisation import TriadOption, HarmonisedMoment
except ImportError:
    from inputs import ChordMelodyConfig, VoicingDensity, Difficulty
    from melody import MelodyNote
    from harmonisation import TriadOption, HarmonisedMoment


@dataclass
class GuitarNote:
    """
    A note on the guitar with string/fret information.
    
    Attributes:
        pitch: MIDI pitch
        pitch_name: Note name
        string: String number (1=high E, 6=low E)
        fret: Fret number
        finger: Suggested fingering (1-4)
        voice: Voice type (melody, root, third, fifth, extension)
    """
    pitch: int
    pitch_name: str
    string: int
    fret: int
    finger: Optional[int] = None
    voice: str = "harmony"


@dataclass
class ChordMelodyVoicing:
    """
    A complete chord-melody voicing.
    
    Attributes:
        melody_note: The melody note
        guitar_notes: All notes in the voicing
        triad: The underlying triad
        position: Fretboard position (average fret)
        stretch: Maximum fret stretch required
        playability_score: 0.0 (hard) to 1.0 (easy)
        analysis: Voicing analysis
    """
    melody_note: MelodyNote
    guitar_notes: List[GuitarNote]
    triad: Optional[TriadOption] = None
    position: int = 5
    stretch: int = 4
    playability_score: float = 0.8
    analysis: str = ""
    
    def get_tab_string(self) -> str:
        """Get TAB representation for this voicing."""
        # Initialize string positions
        strings = {i: "X" for i in range(1, 7)}
        
        for note in self.guitar_notes:
            strings[note.string] = str(note.fret)
        
        return "".join(strings[i].rjust(3) for i in range(6, 0, -1))
    
    def get_pitches(self) -> List[int]:
        """Get all MIDI pitches."""
        return [n.pitch for n in self.guitar_notes]


class VoicingGenerator:
    """
    Generates playable guitar voicings for chord-melody.
    """
    
    # Standard guitar tuning (MIDI pitches)
    GUITAR_TUNING = [40, 45, 50, 55, 59, 64]  # E2, A2, D3, G3, B3, E4
    
    # String names
    STRING_NAMES = {1: "e", 2: "B", 3: "G", 4: "D", 5: "A", 6: "E"}
    
    # MIDI to note name
    MIDI_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    def __init__(self, config: ChordMelodyConfig):
        """
        Initialize the voicing generator.
        
        Args:
            config: Chord-melody configuration
        """
        self.config = config
        self.string_set = config.string_set
        self.voicing_density = config.voicing_density
        self.difficulty = config.difficulty
        
        # Max stretch by difficulty
        self.max_stretch = {
            Difficulty.BEGINNER: 3,
            Difficulty.INTERMEDIATE: 4,
            Difficulty.ADVANCED: 5
        }.get(config.difficulty, 4)
    
    def _midi_to_note_name(self, midi: int) -> str:
        """Convert MIDI to note name with octave."""
        octave = (midi // 12) - 1
        note = self.MIDI_TO_NOTE[midi % 12]
        return f"{note}{octave}"
    
    def _get_string_set_range(self) -> Tuple[int, int]:
        """
        Get the string range for the current string set.
        
        Returns:
            Tuple of (lowest_string, highest_string) (1=high E, 6=low E)
        """
        if self.string_set == "6-4":
            return (4, 6)  # Strings 6, 5, 4
        elif self.string_set == "5-3":
            return (3, 5)  # Strings 5, 4, 3
        elif self.string_set == "4-2":
            return (2, 4)  # Strings 4, 3, 2
        else:  # auto
            return (1, 6)  # All strings
    
    def _find_fret_for_pitch(
        self,
        pitch: int,
        string: int
    ) -> Optional[int]:
        """
        Find the fret position for a pitch on a given string.
        
        Args:
            pitch: MIDI pitch
            string: String number (1-6)
        
        Returns:
            Fret number or None if not playable
        """
        open_pitch = self.GUITAR_TUNING[string - 1]
        fret = pitch - open_pitch
        
        if 0 <= fret <= 22:
            return fret
        return None
    
    def _find_best_string(
        self,
        pitch: int,
        excluded_strings: List[int],
        target_position: int = 5
    ) -> Optional[Tuple[int, int]]:
        """
        Find the best string for a pitch.
        
        Args:
            pitch: MIDI pitch
            excluded_strings: Strings already in use
            target_position: Target fret position
        
        Returns:
            Tuple of (string, fret) or None
        """
        best = None
        best_distance = float('inf')
        
        low_string, high_string = self._get_string_set_range()
        
        for string in range(1, 7):
            if string in excluded_strings:
                continue
            
            # Check if within string set (for auto, allow all)
            if self.string_set != "auto":
                if string < high_string or string > low_string:
                    continue
            
            fret = self._find_fret_for_pitch(pitch, string)
            if fret is not None:
                distance = abs(fret - target_position)
                if distance < best_distance:
                    best = (string, fret)
                    best_distance = distance
        
        return best
    
    def _calculate_playability(
        self,
        guitar_notes: List[GuitarNote]
    ) -> float:
        """
        Calculate playability score for a voicing.
        
        Args:
            guitar_notes: Notes in the voicing
        
        Returns:
            Score from 0.0 (hard) to 1.0 (easy)
        """
        if not guitar_notes:
            return 1.0
        
        frets = [n.fret for n in guitar_notes if n.fret > 0]
        
        if not frets:
            return 1.0  # All open strings
        
        # Stretch penalty
        stretch = max(frets) - min(frets)
        stretch_penalty = max(0, (stretch - 3) * 0.15)
        
        # Position penalty (high positions are harder)
        avg_fret = sum(frets) / len(frets)
        position_penalty = max(0, (avg_fret - 7) * 0.02)
        
        # Barre chord bonus (consistent fretting hand position)
        fret_counts = {}
        for f in frets:
            fret_counts[f] = fret_counts.get(f, 0) + 1
        has_barre = any(count >= 2 for count in fret_counts.values())
        barre_bonus = 0.05 if has_barre else 0
        
        score = 1.0 - stretch_penalty - position_penalty + barre_bonus
        return max(0.1, min(1.0, score))
    
    def _assign_fingerings(
        self,
        guitar_notes: List[GuitarNote]
    ) -> List[GuitarNote]:
        """
        Assign suggested fingerings to notes.
        
        Args:
            guitar_notes: Notes to finger
        
        Returns:
            Notes with fingering suggestions
        """
        if not guitar_notes:
            return guitar_notes
        
        # Sort by fret position
        fretted = [(i, n) for i, n in enumerate(guitar_notes) if n.fret > 0]
        fretted.sort(key=lambda x: (x[1].fret, x[1].string))
        
        # Assign fingers
        fingers = [1, 2, 3, 4]
        finger_idx = 0
        
        for i, (orig_idx, note) in enumerate(fretted):
            if finger_idx < len(fingers):
                guitar_notes[orig_idx].finger = fingers[finger_idx]
                finger_idx += 1
        
        return guitar_notes
    
    def generate_voicing(
        self,
        moment: HarmonisedMoment
    ) -> ChordMelodyVoicing:
        """
        Generate a playable voicing for a harmonised moment.
        
        Args:
            moment: The harmonised moment
        
        Returns:
            ChordMelodyVoicing with guitar positions
        """
        melody_note = moment.melody_note
        triad = moment.triad
        
        if melody_note.is_rest or triad is None:
            return ChordMelodyVoicing(
                melody_note=melody_note,
                guitar_notes=[],
                triad=triad,
                analysis="Rest or no harmony"
            )
        
        guitar_notes = []
        used_strings = []
        
        # Start with melody on top
        melody_pos = self._find_best_string(
            melody_note.pitch,
            used_strings,
            target_position=7
        )
        
        if melody_pos:
            string, fret = melody_pos
            guitar_notes.append(GuitarNote(
                pitch=melody_note.pitch,
                pitch_name=melody_note.pitch_name,
                string=string,
                fret=fret,
                voice="melody"
            ))
            used_strings.append(string)
            target_position = fret
        else:
            # Can't place melody - fallback
            return ChordMelodyVoicing(
                melody_note=melody_note,
                guitar_notes=[],
                triad=triad,
                playability_score=0.0,
                analysis="Melody not playable"
            )
        
        # Add harmony notes (excluding melody pitch class)
        melody_pc = melody_note.pitch % 12
        harmony_pitches = [p for p in triad.pitches if p % 12 != melody_pc]
        
        # Sort harmony from high to low
        harmony_pitches.sort(reverse=True)
        
        for pitch in harmony_pitches:
            # Find playable position
            pos = self._find_best_string(pitch, used_strings, target_position)
            
            if pos:
                string, fret = pos
                
                # Check stretch
                all_frets = [n.fret for n in guitar_notes if n.fret > 0]
                all_frets.append(fret)
                
                if fret > 0:
                    stretch = max(all_frets) - min(all_frets)
                    if stretch > self.max_stretch:
                        continue  # Skip this note - too stretchy
                
                # Determine voice type
                voice_type = "harmony"
                triad_intervals = [p % 12 for p in triad.pitches]
                pitch_pc = pitch % 12
                root_pc = triad.pitches[0] % 12
                
                if pitch_pc == root_pc:
                    voice_type = "root"
                elif pitch_pc == triad_intervals[1] if len(triad_intervals) > 1 else -1:
                    voice_type = "third"
                else:
                    voice_type = "fifth"
                
                guitar_notes.append(GuitarNote(
                    pitch=pitch,
                    pitch_name=self._midi_to_note_name(pitch),
                    string=string,
                    fret=fret,
                    voice=voice_type
                ))
                used_strings.append(string)
        
        # Ensure we have at least 2 notes for 3-note voicings
        if len(guitar_notes) < 2 and self.voicing_density != VoicingDensity.TWO_NOTE:
            # Try to add bass note
            bass_pitch = min(triad.pitches)
            bass_pos = self._find_best_string(bass_pitch, used_strings, target_position)
            
            if bass_pos:
                string, fret = bass_pos
                guitar_notes.append(GuitarNote(
                    pitch=bass_pitch,
                    pitch_name=self._midi_to_note_name(bass_pitch),
                    string=string,
                    fret=fret,
                    voice="bass"
                ))
        
        # Assign fingerings
        guitar_notes = self._assign_fingerings(guitar_notes)
        
        # Calculate metrics
        frets = [n.fret for n in guitar_notes]
        position = int(sum(frets) / len(frets)) if frets else 5
        stretch = max(frets) - min(f for f in frets if f > 0) if any(f > 0 for f in frets) else 0
        playability = self._calculate_playability(guitar_notes)
        
        return ChordMelodyVoicing(
            melody_note=melody_note,
            guitar_notes=sorted(guitar_notes, key=lambda n: n.string, reverse=True),
            triad=triad,
            position=position,
            stretch=stretch,
            playability_score=playability,
            analysis=f"{triad.root}{triad.quality} inv{triad.inversion}, pos{position}"
        )
    
    def generate_all_voicings(
        self,
        harmonised_moments: List[HarmonisedMoment]
    ) -> List[ChordMelodyVoicing]:
        """
        Generate voicings for all harmonised moments.
        
        Args:
            harmonised_moments: List of harmonised moments
        
        Returns:
            List of ChordMelodyVoicing objects
        """
        return [self.generate_voicing(m) for m in harmonised_moments]
    
    def get_alternative_voicings(
        self,
        moment: HarmonisedMoment,
        count: int = 3
    ) -> List[ChordMelodyVoicing]:
        """
        Generate alternative voicings for a moment.
        
        Args:
            moment: The harmonised moment
            count: Number of alternatives to generate
        
        Returns:
            List of alternative ChordMelodyVoicing objects
        """
        alternatives = []
        
        for option in moment.all_options[:count]:
            alt_moment = HarmonisedMoment(
                melody_note=moment.melody_note,
                triad=option,
                analysis=f"Alt: {option.root}{option.quality}"
            )
            voicing = self.generate_voicing(alt_moment)
            if voicing.playability_score > 0:
                alternatives.append(voicing)
        
        return alternatives

