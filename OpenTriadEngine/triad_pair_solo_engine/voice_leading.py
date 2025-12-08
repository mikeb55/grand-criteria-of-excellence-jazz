"""
Voice-Leading Integration for Triad Pair Solo Engine
======================================================

Integrates with the VL-SM (Voice-Leading Smart Module) from Open Triad Engine.
Focuses on:
- Intervallic Mode: Large leaps, SISM, directional inversion cycling
- Functional Mode: APVL, TRAM for grounding
- Modal Mode: Open, floating lines with SISM-based spacing
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from enum import Enum
import sys
import os

# Add parent directory for Open Triad Engine imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from .triad_pairs import TriadPair
    from .patterns import PatternNote, MelodicCell
    from .inputs import SoloMode
except ImportError:
    from triad_pairs import TriadPair
    from patterns import PatternNote, MelodicCell
    from inputs import SoloMode


@dataclass
class VoiceLeadingResult:
    """
    Result of voice-leading analysis between two chords/triads.
    
    Attributes:
        from_voicing: Starting voicing (list of MIDI pitches)
        to_voicing: Ending voicing (list of MIDI pitches)
        motion_intervals: Interval moved per voice (in semitones, positive=up)
        motion_types: Type of motion per voice (step, leap, common_tone)
        leap_sizes: Absolute size of each motion
        narrative: Human-readable explanation
        tension_level: 0.0 (smooth) to 1.0 (maximum tension)
    """
    from_voicing: List[int]
    to_voicing: List[int]
    motion_intervals: List[int]
    motion_types: List[str]
    leap_sizes: List[int]
    narrative: str
    tension_level: float = 0.5


class SoloVoiceLeadingEngine:
    """
    Voice-leading engine specialized for intervallic solo lines.
    Integrates with Open Triad Engine's VL-SM concepts.
    """
    
    # SISM (Sum-Interval Stability Mapping) thresholds
    SISM_STABLE = 12      # Sums <= 12 semitones = stable
    SISM_MODERATE = 18    # Sums 13-18 = moderate tension
    SISM_TENSE = 24       # Sums > 18 = high tension
    
    def __init__(self, mode: SoloMode = SoloMode.INTERVALLIC):
        """
        Initialize the voice-leading engine.
        
        Args:
            mode: Solo mode (affects voice-leading behavior)
        """
        self.mode = mode
    
    def analyze_transition(
        self,
        from_triad: Tuple[str, str],
        to_triad: Tuple[str, str],
        from_inversion: int = 0,
        to_inversion: int = 0,
        base_octave: int = 4
    ) -> VoiceLeadingResult:
        """
        Analyze voice-leading between two triads.
        
        Args:
            from_triad: Starting triad (root, quality)
            to_triad: Target triad (root, quality)
            from_inversion: Inversion of starting triad (0, 1, 2)
            to_inversion: Inversion of target triad
            base_octave: Base octave for pitch calculation
        
        Returns:
            VoiceLeadingResult with analysis
        """
        from_voicing = self._get_voicing(from_triad, from_inversion, base_octave)
        to_voicing = self._get_voicing(to_triad, to_inversion, base_octave)
        
        # Calculate motion for each voice
        motion_intervals = []
        motion_types = []
        leap_sizes = []
        
        for i in range(min(len(from_voicing), len(to_voicing))):
            interval = to_voicing[i] - from_voicing[i]
            motion_intervals.append(interval)
            leap_sizes.append(abs(interval))
            
            if interval == 0:
                motion_types.append("common_tone")
            elif abs(interval) <= 2:
                motion_types.append("step")
            elif abs(interval) <= 4:
                motion_types.append("small_leap")
            else:
                motion_types.append("leap")
        
        # Calculate tension based on mode
        tension_level = self._calculate_tension(motion_intervals, leap_sizes)
        
        # Generate narrative
        narrative = self._generate_narrative(motion_types, motion_intervals)
        
        return VoiceLeadingResult(
            from_voicing=from_voicing,
            to_voicing=to_voicing,
            motion_intervals=motion_intervals,
            motion_types=motion_types,
            leap_sizes=leap_sizes,
            narrative=narrative,
            tension_level=tension_level
        )
    
    def _get_voicing(
        self,
        triad: Tuple[str, str],
        inversion: int,
        octave: int
    ) -> List[int]:
        """Get MIDI pitches for a triad voicing."""
        note_to_midi = {
            "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
            "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
            "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
        }
        
        triad_intervals = {
            "major": [0, 4, 7],
            "minor": [0, 3, 7],
            "dim": [0, 3, 6],
            "aug": [0, 4, 8],
        }
        
        root = triad[0]
        quality = triad[1]
        
        root_midi = note_to_midi.get(root, 0) + (octave + 1) * 12
        intervals = triad_intervals.get(quality, triad_intervals["major"])
        
        pitches = [root_midi + interval for interval in intervals]
        
        # Apply inversion
        if inversion == 1:
            pitches = [pitches[1], pitches[2], pitches[0] + 12]
        elif inversion == 2:
            pitches = [pitches[2], pitches[0] + 12, pitches[1] + 12]
        
        return pitches
    
    def _calculate_tension(
        self,
        motion_intervals: List[int],
        leap_sizes: List[int]
    ) -> float:
        """Calculate tension level based on voice-leading motion."""
        total_motion = sum(leap_sizes)
        
        if self.mode == SoloMode.INTERVALLIC:
            # In intervallic mode, large motion = interesting, not tense
            if total_motion > self.SISM_TENSE:
                return 0.8  # High interest
            elif total_motion > self.SISM_MODERATE:
                return 0.6
            else:
                return 0.4  # Lower interest for small motion
        
        elif self.mode == SoloMode.FUNCTIONAL:
            # In functional mode, smooth = good, leaps = tension
            if total_motion <= self.SISM_STABLE:
                return 0.2  # Smooth
            elif total_motion <= self.SISM_MODERATE:
                return 0.5
            else:
                return 0.8  # High tension
        
        else:  # Modal or Hybrid
            # Balanced approach
            return min(total_motion / self.SISM_TENSE, 1.0)
    
    def _generate_narrative(
        self,
        motion_types: List[str],
        motion_intervals: List[int]
    ) -> str:
        """Generate a human-readable narrative of the voice-leading."""
        parts = []
        
        common_tones = motion_types.count("common_tone")
        steps = motion_types.count("step")
        leaps = motion_types.count("leap") + motion_types.count("small_leap")
        
        if common_tones > 0:
            parts.append(f"{common_tones} common tone(s) retained")
        
        if steps > 0:
            parts.append(f"{steps} voice(s) moving stepwise")
        
        if leaps > 0:
            # Describe the direction of leaps
            up_leaps = sum(1 for m in motion_intervals if m > 4)
            down_leaps = sum(1 for m in motion_intervals if m < -4)
            if up_leaps and down_leaps:
                parts.append(f"contrary motion with {leaps} leap(s)")
            elif up_leaps:
                parts.append(f"{leaps} ascending leap(s)")
            elif down_leaps:
                parts.append(f"{leaps} descending leap(s)")
            else:
                parts.append(f"{leaps} leap(s)")
        
        # Overall characterization
        if self.mode == SoloMode.INTERVALLIC:
            parts.append("intervallic expansion")
        elif self.mode == SoloMode.FUNCTIONAL:
            if common_tones > 0:
                parts.append("functional voice-leading maintained")
        elif self.mode == SoloMode.MODAL:
            parts.append("modal floating quality")
        
        return "; ".join(parts) if parts else "neutral motion"
    
    def optimize_inversion(
        self,
        from_triad: Tuple[str, str],
        to_triad: Tuple[str, str],
        direction: str = "ascending"
    ) -> Tuple[int, int]:
        """
        Find optimal inversions for a triad pair transition.
        
        Args:
            from_triad: Starting triad
            to_triad: Target triad
            direction: "ascending" or "descending"
        
        Returns:
            Tuple of (from_inversion, to_inversion)
        """
        if self.mode == SoloMode.INTERVALLIC:
            # For intervallic mode, choose inversions that maximize leaps
            return self._optimize_for_leaps(from_triad, to_triad, direction)
        elif self.mode == SoloMode.FUNCTIONAL:
            # For functional mode, minimize voice motion
            return self._optimize_for_smoothness(from_triad, to_triad)
        else:
            # Modal: directional inversion cycling
            return self._directional_cycling(direction)
    
    def _optimize_for_leaps(
        self,
        from_triad: Tuple[str, str],
        to_triad: Tuple[str, str],
        direction: str
    ) -> Tuple[int, int]:
        """Optimize inversions for maximum intervallic interest."""
        best_pair = (0, 0)
        max_motion = 0
        
        for from_inv in range(3):
            for to_inv in range(3):
                result = self.analyze_transition(from_triad, to_triad, from_inv, to_inv)
                total_motion = sum(result.leap_sizes)
                
                # Check direction
                avg_motion = sum(result.motion_intervals) / len(result.motion_intervals)
                if direction == "ascending" and avg_motion <= 0:
                    continue
                if direction == "descending" and avg_motion >= 0:
                    continue
                
                if total_motion > max_motion:
                    max_motion = total_motion
                    best_pair = (from_inv, to_inv)
        
        return best_pair
    
    def _optimize_for_smoothness(
        self,
        from_triad: Tuple[str, str],
        to_triad: Tuple[str, str]
    ) -> Tuple[int, int]:
        """Optimize inversions for smoothest voice-leading (APVL)."""
        best_pair = (0, 0)
        min_motion = float('inf')
        
        for from_inv in range(3):
            for to_inv in range(3):
                result = self.analyze_transition(from_triad, to_triad, from_inv, to_inv)
                total_motion = sum(result.leap_sizes)
                
                if total_motion < min_motion:
                    min_motion = total_motion
                    best_pair = (from_inv, to_inv)
        
        return best_pair
    
    def _directional_cycling(self, direction: str) -> Tuple[int, int]:
        """
        Directional inversion cycling for modal mode.
        Ascending: 1st → 2nd → root
        Descending: root → 2nd → 1st
        """
        if direction == "ascending":
            return (1, 2)  # First inversion to second
        else:
            return (0, 2)  # Root to second (descending)
    
    def apply_sism_spacing(
        self,
        cell: MelodicCell,
        target_tension: float = 0.6
    ) -> MelodicCell:
        """
        Apply SISM (Sum-Interval Stability Mapping) to adjust spacing.
        
        High tension = wider spacing, low tension = narrower spacing.
        
        Args:
            cell: Input melodic cell
            target_tension: Desired tension level (0.0-1.0)
        
        Returns:
            MelodicCell with adjusted spacing
        """
        if not cell.notes or len(cell.notes) < 2:
            return cell
        
        # Calculate octave displacement based on tension
        if target_tension > 0.7:
            octave_shift = 12  # Wide spacing
        elif target_tension > 0.4:
            octave_shift = 0   # Normal
        else:
            octave_shift = -12  # Compressed
        
        adjusted_notes = []
        for i, note in enumerate(cell.notes):
            # Apply displacement to alternating notes for intervallic effect
            if i % 2 == 1 and target_tension > 0.5:
                new_pitch = note.pitch + octave_shift
            else:
                new_pitch = note.pitch
            
            adjusted_notes.append(PatternNote(
                pitch=new_pitch,
                pitch_name=self._midi_to_note_name(new_pitch),
                duration=note.duration,
                triad_source=note.triad_source,
                voice=note.voice,
                string=note.string,
                fret=note.fret,
                articulation=note.articulation
            ))
        
        return MelodicCell(
            notes=adjusted_notes,
            pattern_type=cell.pattern_type,
            triad_pair=cell.triad_pair,
            contour=cell.contour
        )
    
    def _midi_to_note_name(self, midi: int) -> str:
        """Convert MIDI pitch to note name."""
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (midi // 12) - 1
        note = note_names[midi % 12]
        return f"{note}{octave}"
    
    def apply_chromatic_approach(
        self,
        notes: List[PatternNote],
        probability: float = 0.3
    ) -> List[PatternNote]:
        """
        Add chromatic approach tones to target notes.
        
        Args:
            notes: Input notes
            probability: Probability of adding approach tone
        
        Returns:
            Notes with chromatic approaches added
        """
        import random
        
        enhanced_notes = []
        
        for i, note in enumerate(notes):
            # Randomly add chromatic approach to some notes
            if i > 0 and random.random() < probability:
                # Approach from half step below or above
                approach_direction = random.choice([-1, 1])
                approach_pitch = note.pitch + approach_direction
                
                # Shorten the approach note and the main note
                approach_duration = note.duration * 0.25
                main_duration = note.duration * 0.75
                
                enhanced_notes.append(PatternNote(
                    pitch=approach_pitch,
                    pitch_name=self._midi_to_note_name(approach_pitch),
                    duration=approach_duration,
                    triad_source="approach",
                    voice=0,
                    articulation="ghost"
                ))
                
                enhanced_notes.append(PatternNote(
                    pitch=note.pitch,
                    pitch_name=note.pitch_name,
                    duration=main_duration,
                    triad_source=note.triad_source,
                    voice=note.voice,
                    string=note.string,
                    fret=note.fret,
                    articulation=note.articulation
                ))
            else:
                enhanced_notes.append(note)
        
        return enhanced_notes
    
    def generate_tram_sequence(
        self,
        triad_pairs: List[TriadPair]
    ) -> List[Dict]:
        """
        Generate TRAM (Tension/Release Alternating Motion) analysis.
        
        Args:
            triad_pairs: List of triad pairs to analyze
        
        Returns:
            List of dicts with tension/release characterization
        """
        results = []
        
        for i, pair in enumerate(triad_pairs):
            # Analyze tension within the pair
            result = self.analyze_transition(pair.triad_a, pair.triad_b)
            
            phase = "tension" if i % 2 == 0 else "release"
            
            results.append({
                "pair_index": i,
                "triad_a": f"{pair.triad_a[0]}{pair.triad_a[1]}",
                "triad_b": f"{pair.triad_b[0]}{pair.triad_b[1]}",
                "phase": phase,
                "tension_level": result.tension_level,
                "narrative": result.narrative,
                "recommended_inversion": self.optimize_inversion(
                    pair.triad_a, pair.triad_b, 
                    "ascending" if phase == "tension" else "descending"
                )
            })
        
        return results

