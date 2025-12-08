"""
Voice-Leading Smart Module (VL-SM) for Open Triad Engine
=========================================================

Implements 4 adaptive voice-leading modes:
1. Functional Mode - traditional voice leading with common-tone retention
2. Modal/Modern Jazz Mode - intervallic freedom with stability mapping
3. Counterpoint Mode - independent melodic lines with contrary motion
4. Orchestration Mode - register/instrument-aware voice assignment

Includes specialized algorithms:
- APVL (Axis-Preserving Voice Leading)
- TRAM (Tension/Release Alternating Motion)
- SISM (Sum-Interval Stability Mapping)
- Directional Inversion Cycling
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
from abc import ABC, abstractmethod

from .core import Note, Triad, Inversion, VoicingType, VoiceMotion
from .transformations import InversionEngine
from .inputs import RegisterLimits, INSTRUMENT_REGISTERS


class VLMode(Enum):
    """Voice-leading modes."""
    FUNCTIONAL = "functional"
    MODAL = "modal"
    COUNTERPOINT = "counterpoint"
    ORCHESTRATION = "orchestration"


@dataclass
class VoiceLeadingResult:
    """
    Result of a voice-leading operation.
    
    Attributes:
        source: Original triad
        target: Voice-led triad
        motions: List of voice motions
        narrative: Human-readable explanation
        score: Quality score (lower is better for smooth VL)
        mode: VL mode used
    """
    source: Triad
    target: Triad
    motions: List[VoiceMotion]
    narrative: str
    score: float
    mode: VLMode
    
    def to_dict(self) -> Dict:
        return {
            'source': self.source.to_dict(),
            'target': self.target.to_dict(),
            'motions': [
                {
                    'voice': m.voice_name,
                    'from': str(m.from_note),
                    'to': str(m.to_note),
                    'interval': m.interval,
                    'type': m.motion_type
                }
                for m in self.motions
            ],
            'narrative': self.narrative,
            'score': self.score,
            'mode': self.mode.value
        }


class APVL:
    """
    Axis-Preserving Voice Leading.
    
    Maintains an "axis" note that remains common between chords,
    creating smooth connections around a pivot point.
    """
    
    @staticmethod
    def find_common_tones(triad1: Triad, triad2: Triad) -> List[Tuple[Note, Note]]:
        """Find common tones between two triads."""
        common = []
        for v1 in triad1.voices:
            for v2 in triad2.voices:
                if v1.pitch_class == v2.pitch_class:
                    common.append((v1, v2))
        return common
    
    @staticmethod
    def apply(source: Triad, target_root: Note, target_type) -> Triad:
        """
        Apply APVL to voice-lead from source to a target chord.
        
        Tries to maintain at least one common tone as the axis.
        """
        # Create target triad
        from .core import TriadType
        target = Triad(root=target_root, triad_type=target_type)
        
        # Find which inversion gives best axis preservation
        best_inversion = None
        best_common = 0
        
        for inv in [Inversion.ROOT, Inversion.FIRST, Inversion.SECOND]:
            test_target = InversionEngine.get_inversion(target, inv)
            common = APVL.find_common_tones(source, test_target)
            if len(common) > best_common:
                best_common = len(common)
                best_inversion = inv
        
        if best_inversion:
            return InversionEngine.get_inversion(target, best_inversion)
        return target


class TRAM:
    """
    Tension/Release Alternating Motion.
    
    Alternates between tense (wide intervals, dissonance) and
    release (stepwise, consonance) voice leading for musical interest.
    """
    
    def __init__(self, tension_threshold: int = 5):
        """
        Initialize TRAM.
        
        Args:
            tension_threshold: Interval size above which is considered "tense"
        """
        self.tension_threshold = tension_threshold
        self.last_was_tense = False
    
    def get_next_tension_state(self) -> bool:
        """Get whether next voice leading should be tense."""
        should_be_tense = not self.last_was_tense
        self.last_was_tense = should_be_tense
        return should_be_tense
    
    def apply(self, source: Triad, target: Triad, prefer_tense: bool) -> Triad:
        """
        Apply TRAM to choose an inversion for the target.
        
        If prefer_tense, choose inversion with wider intervals.
        If not, choose inversion with smallest motion.
        """
        best_inv = None
        best_score = float('inf') if not prefer_tense else 0
        
        for inv in [Inversion.ROOT, Inversion.FIRST, Inversion.SECOND]:
            test_target = InversionEngine.get_inversion(target, inv)
            motion_sum = self._calculate_motion_sum(source, test_target)
            
            if prefer_tense:
                if motion_sum > best_score:
                    best_score = motion_sum
                    best_inv = inv
            else:
                if motion_sum < best_score:
                    best_score = motion_sum
                    best_inv = inv
        
        if best_inv:
            return InversionEngine.get_inversion(target, best_inv)
        return target
    
    def _calculate_motion_sum(self, source: Triad, target: Triad) -> int:
        """Calculate sum of voice motions."""
        sorted_source = sorted(source.voices, key=lambda n: n.midi_number)
        sorted_target = sorted(target.voices, key=lambda n: n.midi_number)
        
        total = 0
        for s, t in zip(sorted_source, sorted_target):
            total += abs(s.midi_number - t.midi_number)
        return total


class SISM:
    """
    Sum-Interval Stability Mapping.
    
    Measures the "stability" of a voicing based on the intervals
    between voices. Used in modal/modern jazz contexts where
    certain interval stacks are preferred.
    """
    
    # Interval stability ratings (0 = most stable, 10 = least stable)
    STABILITY_MAP = {
        0: 0,   # Unison
        1: 8,   # m2
        2: 6,   # M2
        3: 3,   # m3
        4: 2,   # M3
        5: 4,   # P4
        6: 9,   # TT
        7: 1,   # P5
        8: 3,   # m6
        9: 2,   # M6
        10: 5,  # m7
        11: 7,  # M7
    }
    
    @classmethod
    def calculate_stability(cls, triad: Triad) -> float:
        """
        Calculate stability score for a triad voicing.
        
        Lower score = more stable (traditional consonance).
        Higher score = more tension (modern jazz color).
        """
        intervals = triad.intervals
        total = sum(cls.STABILITY_MAP.get(iv % 12, 5) for iv in intervals)
        return total / len(intervals) if intervals else 0
    
    @classmethod
    def rank_by_stability(cls, triads: List[Triad]) -> List[Tuple[Triad, float]]:
        """Rank triads by stability score."""
        scored = [(t, cls.calculate_stability(t)) for t in triads]
        return sorted(scored, key=lambda x: x[1])


class VoiceLeadingSmartModule:
    """
    The main voice-leading module supporting all 4 modes.
    
    Provides adaptive voice-leading based on context and style.
    """
    
    def __init__(
        self,
        mode: VLMode = VLMode.FUNCTIONAL,
        allow_parallel_fifths: bool = False,
        allow_parallel_octaves: bool = False,
        prefer_contrary_motion: bool = True,
        max_voice_leap: int = 12,
        register_limits: Optional[RegisterLimits] = None,
        instruments: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the VL-SM.
        
        Args:
            mode: Voice-leading mode
            allow_parallel_fifths: Whether to allow parallel fifths
            allow_parallel_octaves: Whether to allow parallel octaves
            prefer_contrary_motion: Whether to prefer contrary motion
            max_voice_leap: Maximum leap for any voice in semitones
            register_limits: Pitch range limits
            instruments: Instrument assignments for orchestration mode
        """
        self.mode = mode
        self.allow_parallel_fifths = allow_parallel_fifths
        self.allow_parallel_octaves = allow_parallel_octaves
        self.prefer_contrary_motion = prefer_contrary_motion
        self.max_voice_leap = max_voice_leap
        self.register_limits = register_limits or RegisterLimits()
        self.instruments = instruments or {
            "top": "violin",
            "middle": "viola",
            "bottom": "cello"
        }
        
        # Initialize specialized algorithms
        self.tram = TRAM()
    
    def voice_lead(
        self, 
        source: Triad, 
        target: Triad,
        mode_override: Optional[VLMode] = None
    ) -> VoiceLeadingResult:
        """
        Voice-lead from source to target triad.
        
        Args:
            source: Starting triad
            target: Ending triad (may be modified for optimal VL)
            mode_override: Override the default mode
            
        Returns:
            VoiceLeadingResult with optimal voicing and analysis
        """
        mode = mode_override or self.mode
        
        if mode == VLMode.FUNCTIONAL:
            return self._functional_voice_lead(source, target)
        elif mode == VLMode.MODAL:
            return self._modal_voice_lead(source, target)
        elif mode == VLMode.COUNTERPOINT:
            return self._counterpoint_voice_lead(source, target)
        elif mode == VLMode.ORCHESTRATION:
            return self._orchestration_voice_lead(source, target)
        
        return self._functional_voice_lead(source, target)
    
    def voice_lead_progression(
        self,
        triads: List[Triad],
        mode_override: Optional[VLMode] = None
    ) -> List[VoiceLeadingResult]:
        """
        Voice-lead an entire progression.
        
        Args:
            triads: List of triads to voice-lead
            mode_override: Override the default mode
            
        Returns:
            List of VoiceLeadingResults
        """
        if len(triads) < 2:
            return []
        
        results = []
        current = triads[0]
        
        for next_triad in triads[1:]:
            result = self.voice_lead(current, next_triad, mode_override)
            results.append(result)
            current = result.target
        
        return results
    
    def _functional_voice_lead(self, source: Triad, target: Triad) -> VoiceLeadingResult:
        """
        Functional mode voice leading.
        
        Features:
        - Common-tone retention (APVL)
        - Tension/release alternation (TRAM)
        - Optional parallel fifth/octave avoidance
        - Inversion switching to minimize outer-voice leaps
        """
        # Try to find common tones
        common_tones = APVL.find_common_tones(source, target)
        
        # Evaluate all inversions
        candidates = []
        for inv in [Inversion.ROOT, Inversion.FIRST, Inversion.SECOND]:
            voiced = InversionEngine.get_inversion(target, inv)
            score = self._score_functional(source, voiced, common_tones)
            
            # Check for parallel motion issues
            if not self.allow_parallel_fifths:
                if self._has_parallel_fifths(source, voiced):
                    score += 100  # Heavy penalty
            if not self.allow_parallel_octaves:
                if self._has_parallel_octaves(source, voiced):
                    score += 100
            
            candidates.append((voiced, score, inv))
        
        # Sort by score (lower is better)
        candidates.sort(key=lambda x: x[1])
        best_target, best_score, _ = candidates[0]
        
        # Calculate motions
        motions = self._calculate_motions(source, best_target)
        
        # Build narrative
        narrative = self._build_narrative(source, best_target, motions, common_tones)
        
        return VoiceLeadingResult(
            source=source,
            target=best_target,
            motions=motions,
            narrative=narrative,
            score=best_score,
            mode=VLMode.FUNCTIONAL
        )
    
    def _modal_voice_lead(self, source: Triad, target: Triad) -> VoiceLeadingResult:
        """
        Modal/Modern Jazz mode voice leading.
        
        Features:
        - Intervallic freedom
        - SISM (Sum-Interval Stability Mapping)
        - Directional Inversion Cycling
        """
        # Get all inversions with stability scores
        inversions = InversionEngine.all_inversions(target)
        scored = [(inv, SISM.calculate_stability(triad)) 
                  for inv, triad in inversions.items()]
        
        # In modal context, we might prefer MORE tension (higher score)
        # for color, balanced against voice-leading smoothness
        candidates = []
        for inv_name, stability in scored:
            voiced = inversions[inv_name]
            motion_score = self._calculate_motion_score(source, voiced)
            
            # Modal mode: balance motion with desired stability
            # Lower motion is still good, but we value color
            combined_score = motion_score - (stability * 0.5)  # Slight preference for color
            candidates.append((voiced, combined_score, inv_name))
        
        candidates.sort(key=lambda x: x[1])
        best_target, best_score, inv_name = candidates[0]
        
        motions = self._calculate_motions(source, best_target)
        
        narrative = f"Modal voice leading to {target.symbol} ({inv_name}). "
        narrative += f"Stability score: {SISM.calculate_stability(best_target):.1f}. "
        if any(m.motion_type == 'leap' for m in motions):
            narrative += "Wide intervals preserved for color."
        
        return VoiceLeadingResult(
            source=source,
            target=best_target,
            motions=motions,
            narrative=narrative,
            score=best_score,
            mode=VLMode.MODAL
        )
    
    def _counterpoint_voice_lead(self, source: Triad, target: Triad) -> VoiceLeadingResult:
        """
        Counterpoint mode voice leading.
        
        Features:
        - Treat each voice as independent melodic line
        - Prefer contrary or oblique motion
        - Prevent voice crossing
        - Optional anti-parallel rules
        """
        # Find inversion that maximizes contrary motion
        candidates = []
        
        for inv in [Inversion.ROOT, Inversion.FIRST, Inversion.SECOND]:
            voiced = InversionEngine.get_inversion(target, inv)
            
            # Check for voice crossing
            if self._has_voice_crossing(source, voiced):
                continue  # Skip this inversion
            
            score = self._score_counterpoint(source, voiced)
            candidates.append((voiced, score, inv))
        
        if not candidates:
            # Fallback: accept voice crossing if no alternatives
            for inv in [Inversion.ROOT, Inversion.FIRST, Inversion.SECOND]:
                voiced = InversionEngine.get_inversion(target, inv)
                score = self._score_counterpoint(source, voiced) + 50  # Penalty
                candidates.append((voiced, score, inv))
        
        candidates.sort(key=lambda x: x[1])
        best_target, best_score, _ = candidates[0]
        
        motions = self._calculate_motions(source, best_target)
        
        # Analyze motion types
        motion_types = self._analyze_motion_types(motions)
        narrative = f"Counterpoint voice leading: {motion_types}. "
        if not self._has_voice_crossing(source, best_target):
            narrative += "No voice crossing. "
        
        return VoiceLeadingResult(
            source=source,
            target=best_target,
            motions=motions,
            narrative=narrative,
            score=best_score,
            mode=VLMode.COUNTERPOINT
        )
    
    def _orchestration_voice_lead(self, source: Triad, target: Triad) -> VoiceLeadingResult:
        """
        Orchestration mode voice leading.
        
        Features:
        - Assign voices to instrument registers
        - Enforce range limits
        - Choose inversions for timbral clarity and spacing
        """
        # Get instrument ranges
        top_reg = INSTRUMENT_REGISTERS.get(self.instruments['top'])
        mid_reg = INSTRUMENT_REGISTERS.get(self.instruments['middle'])
        bot_reg = INSTRUMENT_REGISTERS.get(self.instruments['bottom'])
        
        candidates = []
        for inv in [Inversion.ROOT, Inversion.FIRST, Inversion.SECOND]:
            voiced = InversionEngine.get_inversion(target, inv)
            sorted_voices = sorted(voiced.voices, key=lambda n: n.midi_number)
            
            # Check register compliance
            register_score = 0
            if bot_reg and not (bot_reg.low <= sorted_voices[0].midi_number <= bot_reg.high):
                register_score += 20
            if mid_reg and len(sorted_voices) > 1:
                if not (mid_reg.low <= sorted_voices[1].midi_number <= mid_reg.high):
                    register_score += 20
            if top_reg and len(sorted_voices) > 2:
                if not (top_reg.low <= sorted_voices[2].midi_number <= top_reg.high):
                    register_score += 20
            
            # Prefer good spacing for clarity
            spacing_score = self._score_orchestral_spacing(voiced)
            
            total_score = register_score + spacing_score
            candidates.append((voiced, total_score, inv))
        
        candidates.sort(key=lambda x: x[1])
        best_target, best_score, _ = candidates[0]
        
        motions = self._calculate_motions(source, best_target)
        
        sorted_target = sorted(best_target.voices, key=lambda n: n.midi_number)
        narrative = f"Orchestration: "
        narrative += f"{self.instruments['bottom']}={sorted_target[0]}, "
        narrative += f"{self.instruments['middle']}={sorted_target[1]}, "
        narrative += f"{self.instruments['top']}={sorted_target[2]}. "
        
        return VoiceLeadingResult(
            source=source,
            target=best_target,
            motions=motions,
            narrative=narrative,
            score=best_score,
            mode=VLMode.ORCHESTRATION
        )
    
    def _score_functional(
        self, 
        source: Triad, 
        target: Triad,
        common_tones: List[Tuple[Note, Note]]
    ) -> float:
        """Score a voice-leading option for functional mode."""
        score = 0.0
        
        # Reward common tones
        score -= len(common_tones) * 5
        
        # Calculate voice motion
        sorted_source = sorted(source.voices, key=lambda n: n.midi_number)
        sorted_target = sorted(target.voices, key=lambda n: n.midi_number)
        
        for s, t in zip(sorted_source, sorted_target):
            motion = abs(s.midi_number - t.midi_number)
            
            # Steps are best
            if motion <= 2:
                score += motion * 0.5
            # Thirds are okay
            elif motion <= 4:
                score += motion * 1.0
            # Larger intervals cost more
            else:
                score += motion * 2.0
            
            # Penalize exceeding max leap
            if motion > self.max_voice_leap:
                score += 50
        
        # Bonus for contrary motion in outer voices
        if self.prefer_contrary_motion:
            outer_source = [sorted_source[0], sorted_source[-1]]
            outer_target = [sorted_target[0], sorted_target[-1]]
            
            motion1 = outer_target[0].midi_number - outer_source[0].midi_number
            motion2 = outer_target[1].midi_number - outer_source[1].midi_number
            
            if (motion1 > 0 and motion2 < 0) or (motion1 < 0 and motion2 > 0):
                score -= 3  # Bonus for contrary
        
        return score
    
    def _score_counterpoint(self, source: Triad, target: Triad) -> float:
        """Score a voice-leading option for counterpoint mode."""
        score = 0.0
        
        sorted_source = sorted(source.voices, key=lambda n: n.midi_number)
        sorted_target = sorted(target.voices, key=lambda n: n.midi_number)
        
        motions = []
        for s, t in zip(sorted_source, sorted_target):
            motion = t.midi_number - s.midi_number
            motions.append(motion)
        
        # Count contrary motion pairs
        contrary_count = 0
        oblique_count = 0
        parallel_count = 0
        
        for i in range(len(motions)):
            for j in range(i + 1, len(motions)):
                if (motions[i] > 0 and motions[j] < 0) or (motions[i] < 0 and motions[j] > 0):
                    contrary_count += 1
                elif motions[i] == 0 or motions[j] == 0:
                    oblique_count += 1
                else:
                    parallel_count += 1
        
        # Counterpoint prefers contrary > oblique > parallel
        score += parallel_count * 5
        score += oblique_count * 2
        score -= contrary_count * 3
        
        # Penalize large leaps
        for m in motions:
            if abs(m) > 7:
                score += abs(m) - 7
        
        return score
    
    def _score_orchestral_spacing(self, triad: Triad) -> float:
        """Score orchestral spacing clarity."""
        intervals = triad.intervals
        
        # Prefer wider spacing at bottom (acoustic clarity)
        if len(intervals) >= 2:
            if intervals[0] < intervals[1]:
                return 0  # Good: wider at bottom
            else:
                return 5  # Not ideal
        return 0
    
    def _calculate_motion_score(self, source: Triad, target: Triad) -> float:
        """Calculate total motion score."""
        sorted_source = sorted(source.voices, key=lambda n: n.midi_number)
        sorted_target = sorted(target.voices, key=lambda n: n.midi_number)
        
        return sum(abs(s.midi_number - t.midi_number) 
                   for s, t in zip(sorted_source, sorted_target))
    
    def _calculate_motions(self, source: Triad, target: Triad) -> List[VoiceMotion]:
        """Calculate voice motions between triads."""
        sorted_source = sorted(source.voices, key=lambda n: n.midi_number)
        sorted_target = sorted(target.voices, key=lambda n: n.midi_number)
        
        voice_names = ['bass', 'middle', 'top']
        motions = []
        
        for i, (s, t) in enumerate(zip(sorted_source, sorted_target)):
            motion = VoiceMotion(
                voice_name=voice_names[i] if i < len(voice_names) else f'voice{i}',
                from_note=s,
                to_note=t,
                interval=t.midi_number - s.midi_number
            )
            motions.append(motion)
        
        return motions
    
    def _has_parallel_fifths(self, source: Triad, target: Triad) -> bool:
        """Check for parallel fifths."""
        sorted_source = sorted(source.voices, key=lambda n: n.midi_number)
        sorted_target = sorted(target.voices, key=lambda n: n.midi_number)
        
        for i in range(len(sorted_source)):
            for j in range(i + 1, len(sorted_source)):
                source_interval = (sorted_source[j].midi_number - sorted_source[i].midi_number) % 12
                target_interval = (sorted_target[j].midi_number - sorted_target[i].midi_number) % 12
                
                # Both are perfect fifths and voices moved in same direction
                if source_interval == 7 and target_interval == 7:
                    source_motion = sorted_target[i].midi_number - sorted_source[i].midi_number
                    target_motion = sorted_target[j].midi_number - sorted_source[j].midi_number
                    if source_motion != 0 and (source_motion > 0) == (target_motion > 0):
                        return True
        return False
    
    def _has_parallel_octaves(self, source: Triad, target: Triad) -> bool:
        """Check for parallel octaves."""
        sorted_source = sorted(source.voices, key=lambda n: n.midi_number)
        sorted_target = sorted(target.voices, key=lambda n: n.midi_number)
        
        for i in range(len(sorted_source)):
            for j in range(i + 1, len(sorted_source)):
                source_interval = (sorted_source[j].midi_number - sorted_source[i].midi_number) % 12
                target_interval = (sorted_target[j].midi_number - sorted_target[i].midi_number) % 12
                
                if source_interval == 0 and target_interval == 0:
                    source_motion = sorted_target[i].midi_number - sorted_source[i].midi_number
                    target_motion = sorted_target[j].midi_number - sorted_source[j].midi_number
                    if source_motion != 0 and (source_motion > 0) == (target_motion > 0):
                        return True
        return False
    
    def _has_voice_crossing(self, source: Triad, target: Triad) -> bool:
        """Check for voice crossing."""
        sorted_source = sorted(source.voices, key=lambda n: n.midi_number)
        sorted_target = sorted(target.voices, key=lambda n: n.midi_number)
        
        # Check if any voice ends up in wrong order
        for i in range(len(sorted_target) - 1):
            if sorted_target[i].midi_number >= sorted_target[i + 1].midi_number:
                return True
        return False
    
    def _analyze_motion_types(self, motions: List[VoiceMotion]) -> str:
        """Analyze and describe the types of motion between voices."""
        if len(motions) < 2:
            return "single voice"
        
        directions = [m.interval for m in motions]
        
        # Check for contrary
        contrary = False
        oblique = False
        parallel = True
        
        for i in range(len(directions)):
            for j in range(i + 1, len(directions)):
                if directions[i] == 0 or directions[j] == 0:
                    oblique = True
                    parallel = False
                elif (directions[i] > 0) != (directions[j] > 0):
                    contrary = True
                    parallel = False
        
        if contrary:
            return "contrary motion"
        elif oblique:
            return "oblique motion"
        elif parallel:
            return "parallel motion"
        return "mixed motion"
    
    def _build_narrative(
        self, 
        source: Triad, 
        target: Triad,
        motions: List[VoiceMotion],
        common_tones: List[Tuple[Note, Note]]
    ) -> str:
        """Build a human-readable narrative of the voice leading."""
        parts = []
        
        # Common tones
        if common_tones:
            tones = ', '.join(str(ct[0]) for ct in common_tones)
            parts.append(f"Common tone(s) retained: {tones}")
        
        # Motion description
        for motion in motions:
            if motion.motion_type == 'common_tone':
                parts.append(f"{motion.voice_name.capitalize()} stays on {motion.from_note}")
            elif motion.motion_type == 'step':
                direction = "up" if motion.interval > 0 else "down"
                parts.append(f"{motion.voice_name.capitalize()} steps {direction}: {motion.from_note} → {motion.to_note}")
            else:
                direction = "up" if motion.interval > 0 else "down"
                parts.append(f"{motion.voice_name.capitalize()} moves {direction} by {abs(motion.interval)} semitones")
        
        # Overall motion type
        motion_type = self._analyze_motion_types(motions)
        parts.append(f"Overall: {motion_type}")
        
        return ". ".join(parts) + "."


def voice_lead(
    source: Triad, 
    target: Triad,
    mode: str = 'functional',
    **kwargs
) -> VoiceLeadingResult:
    """
    Convenience function for voice leading two triads.
    
    Args:
        source: Starting triad
        target: Target triad
        mode: 'functional', 'modal', 'counterpoint', or 'orchestration'
        **kwargs: Additional options passed to VoiceLeadingSmartModule
        
    Returns:
        VoiceLeadingResult
    """
    mode_map = {
        'functional': VLMode.FUNCTIONAL,
        'modal': VLMode.MODAL,
        'counterpoint': VLMode.COUNTERPOINT,
        'orchestration': VLMode.ORCHESTRATION,
    }
    
    vl_mode = mode_map.get(mode.lower(), VLMode.FUNCTIONAL)
    module = VoiceLeadingSmartModule(mode=vl_mode, **kwargs)
    return module.voice_lead(source, target)

