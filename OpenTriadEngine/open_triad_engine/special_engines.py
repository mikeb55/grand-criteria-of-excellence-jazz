"""
Special Use-Case Engines for Open Triad Engine
===============================================

Implements specialized engines for specific musical contexts:
1. Chord-Melody Engine - melody on top with open triad support
2. ii-V-I Open Triad Engine - functional progressions with APVL/TRAM
3. Open Triad Triad-Pair Engine - triad pairs in open spacing
4. Counterpoint Companion - three independent melodic lines
5. Orchestration Mapper - voice-to-instrument assignment
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

from .core import Note, Triad, TriadType, Inversion, VoicingType, create_triad
from .transformations import InversionEngine, ClosedToOpenConverter, ScaleMapper
from .voice_leading import (
    VoiceLeadingSmartModule, VLMode, VoiceLeadingResult,
    APVL, TRAM, SISM
)
from .inputs import RegisterLimits, INSTRUMENT_REGISTERS


@dataclass
class ChordMelodyVoicing:
    """
    A chord-melody voicing with melody on top.
    
    Attributes:
        melody_note: The melody note (must be on top)
        triad: The supporting open triad
        full_voicing: All notes from bottom to top
    """
    melody_note: Note
    triad: Triad
    full_voicing: List[Note]
    
    @property
    def bass_note(self) -> Note:
        return min(self.full_voicing, key=lambda n: n.midi_number)
    
    @property
    def top_note(self) -> Note:
        return max(self.full_voicing, key=lambda n: n.midi_number)
    
    def to_dict(self) -> Dict:
        return {
            'melody': str(self.melody_note),
            'chord': self.triad.symbol,
            'voicing': [str(n) for n in self.full_voicing]
        }


class ChordMelodyEngine:
    """
    Engine for creating chord-melody arrangements.
    
    Rules:
    - Melody must be the top voice
    - Open triad supports underneath
    - Allows diatonic harmonization or reharm/UST logic
    - Uses VL-SM for transitions
    """
    
    def __init__(
        self,
        scale_name: str = 'ionian',
        root: str = 'C',
        allow_reharm: bool = True
    ):
        self.scale_mapper = ScaleMapper(root)
        self.scale_name = scale_name
        self.allow_reharm = allow_reharm
        self.vl_module = VoiceLeadingSmartModule(mode=VLMode.FUNCTIONAL)
    
    def harmonize_note(
        self,
        melody_note: Note,
        chord_symbol: Optional[str] = None
    ) -> ChordMelodyVoicing:
        """
        Harmonize a single melody note with an open triad.
        
        Args:
            melody_note: The melody note to harmonize
            chord_symbol: Optional specific chord to use
            
        Returns:
            ChordMelodyVoicing with melody on top
        """
        if chord_symbol:
            triad = Triad.from_symbol(chord_symbol, melody_note.octave - 1)
        else:
            triad = self._find_diatonic_harmony(melody_note)
        
        # Find inversion that puts melody on top
        voiced = self._voice_with_melody_on_top(triad, melody_note)
        
        full_voicing = sorted(voiced.voices, key=lambda n: n.midi_number)
        
        return ChordMelodyVoicing(
            melody_note=melody_note,
            triad=voiced,
            full_voicing=full_voicing
        )
    
    def harmonize_melody(
        self,
        melody: List[Note],
        chord_symbols: Optional[List[str]] = None
    ) -> List[ChordMelodyVoicing]:
        """
        Harmonize an entire melody line.
        
        Args:
            melody: List of melody notes
            chord_symbols: Optional list of chord symbols (one per note or fewer)
            
        Returns:
            List of ChordMelodyVoicing objects
        """
        voicings = []
        
        for i, note in enumerate(melody):
            chord = None
            if chord_symbols and i < len(chord_symbols):
                chord = chord_symbols[i]
            
            voicing = self.harmonize_note(note, chord)
            voicings.append(voicing)
        
        return voicings
    
    def _find_diatonic_harmony(self, melody_note: Note) -> Triad:
        """Find a diatonic chord that contains the melody note."""
        scale_notes = self.scale_mapper.get_scale_notes(self.scale_name)
        diatonic_triads = self.scale_mapper.get_diatonic_triads(
            self.scale_name, melody_note.octave - 1
        )
        
        # Find chords containing the melody note
        melody_pc = melody_note.pitch_class
        candidates = []
        
        for triad in diatonic_triads:
            triad_pcs = set(v.pitch_class for v in triad.voices)
            if melody_pc in triad_pcs:
                candidates.append(triad)
        
        if candidates:
            # Prefer I, IV, V chords
            return candidates[0]
        
        # Fallback: use chord built on melody note
        return Triad(root=melody_note.transpose(-12), triad_type=TriadType.MAJOR)
    
    def _voice_with_melody_on_top(self, triad: Triad, melody: Note) -> Triad:
        """Voice the triad so melody ends up on top."""
        melody_pc = melody.pitch_class
        
        # Try each inversion
        for inv in [Inversion.ROOT, Inversion.FIRST, Inversion.SECOND]:
            voiced = InversionEngine.get_inversion(triad, inv)
            top = max(voiced.voices, key=lambda n: n.midi_number)
            
            if top.pitch_class == melody_pc:
                # Adjust octave to match melody
                octave_diff = melody.octave - top.octave
                if octave_diff != 0:
                    voiced.voices = [v.transpose(octave_diff * 12) for v in voiced.voices]
                return voiced
        
        # If melody note isn't in chord, use upper structure
        # Add melody and adjust other voices below
        new_voices = [
            melody.transpose(-19),  # 10th below
            melody.transpose(-12),  # Octave below
            melody
        ]
        
        result = triad.copy()
        result.voices = new_voices
        return result


@dataclass
class TwoFiveOneResult:
    """
    Result of a ii-V-I voice-leading.
    
    Attributes:
        ii: The ii chord
        V: The V chord
        I: The I chord
        vl_ii_to_V: Voice leading from ii to V
        vl_V_to_I: Voice leading from V to I
    """
    ii: Triad
    V: Triad
    I: Triad
    vl_ii_to_V: VoiceLeadingResult
    vl_V_to_I: VoiceLeadingResult
    
    def to_dict(self) -> Dict:
        return {
            'ii': self.ii.to_dict(),
            'V': self.V.to_dict(),
            'I': self.I.to_dict(),
            'voice_leading': {
                'ii_to_V': self.vl_ii_to_V.to_dict(),
                'V_to_I': self.vl_V_to_I.to_dict()
            }
        }


class TwoFiveOneEngine:
    """
    Engine for ii-V-I progressions with optimal voice leading.
    
    Uses APVL (Axis-Preserving Voice Leading) and TRAM
    (Tension/Release Alternating Motion) for smooth functional
    voice leading with inversion optimization.
    """
    
    def __init__(self, use_tram: bool = True):
        self.use_tram = use_tram
        self.tram = TRAM()
        self.vl_module = VoiceLeadingSmartModule(
            mode=VLMode.FUNCTIONAL,
            prefer_contrary_motion=True
        )
    
    def generate(
        self,
        key: str = 'C',
        octave: int = 4,
        minor: bool = False
    ) -> TwoFiveOneResult:
        """
        Generate a ii-V-I progression in open triads.
        
        Args:
            key: Key center (e.g., 'C', 'Bb', 'F#')
            octave: Base octave
            minor: If True, generate ii-V-i (minor tonic)
            
        Returns:
            TwoFiveOneResult with optimal voice leading
        """
        from .core import CHROMATIC_NOTES
        
        root_pc = CHROMATIC_NOTES.index(key) if key in CHROMATIC_NOTES else 0
        
        # Build the chords
        # ii is minor, a whole step above the root
        ii_root = CHROMATIC_NOTES[(root_pc + 2) % 12]
        ii = Triad(
            root=Note(ii_root, octave),
            triad_type=TriadType.MINOR
        )
        
        # V is major (or dominant), a fifth above the root
        v_root = CHROMATIC_NOTES[(root_pc + 7) % 12]
        V = Triad(
            root=Note(v_root, octave),
            triad_type=TriadType.MAJOR
        )
        
        # I is major or minor
        I = Triad(
            root=Note(key, octave),
            triad_type=TriadType.MINOR if minor else TriadType.MAJOR
        )
        
        # Convert to open voicings
        ii_open = InversionEngine.open_root(ii)
        
        # Voice lead ii to V
        vl_ii_V = self.vl_module.voice_lead(ii_open, V)
        V_voiced = vl_ii_V.target
        
        # Voice lead V to I
        vl_V_I = self.vl_module.voice_lead(V_voiced, I)
        I_voiced = vl_V_I.target
        
        return TwoFiveOneResult(
            ii=ii_open,
            V=V_voiced,
            I=I_voiced,
            vl_ii_to_V=vl_ii_V,
            vl_V_to_I=vl_V_I
        )
    
    def generate_all_keys(self, minor: bool = False) -> Dict[str, TwoFiveOneResult]:
        """Generate ii-V-I in all 12 keys."""
        from .core import CHROMATIC_NOTES
        
        results = {}
        for key in CHROMATIC_NOTES:
            results[key] = self.generate(key, minor=minor)
        return results


@dataclass
class TriadPair:
    """
    A pair of triads used in triad-pair improvisation.
    
    Attributes:
        triad1: First triad
        triad2: Second triad  
        relationship: Relationship between triads (diatonic, UST, etc.)
    """
    triad1: Triad
    triad2: Triad
    relationship: str
    
    @property
    def combined_pitch_classes(self) -> set:
        """Get all unique pitch classes from both triads."""
        pcs = set()
        for v in self.triad1.voices + self.triad2.voices:
            pcs.add(v.pitch_class)
        return pcs
    
    def to_dict(self) -> Dict:
        return {
            'triad1': self.triad1.to_dict(),
            'triad2': self.triad2.to_dict(),
            'relationship': self.relationship,
            'combined_pitches': list(self.combined_pitch_classes)
        }


class OpenTriadPairEngine:
    """
    Engine for triad-pair improvisation using open triads.
    
    Supports:
    - Diatonic triad pairs
    - Klemons pairs (triads a whole step apart)
    - UST (Upper Structure Triad) pairs
    - All pairs in open-triad spacing for intervallic lines
    """
    
    # Common triad pair relationships
    PAIR_TYPES = {
        'diatonic_adjacent': (0, 2),     # Adjacent diatonic (e.g., C-Dm)
        'diatonic_thirds': (0, 4),       # Third apart (e.g., C-Em)
        'klemons': (0, 2),               # Whole step (major triads)
        'ust_tritone': (0, 6),           # Tritone apart
        'ust_minor_third': (0, 3),       # Minor third apart
    }
    
    def __init__(self):
        self.inversion_engine = InversionEngine()
    
    def create_diatonic_pair(
        self,
        scale_name: str,
        root: str,
        degree1: int,
        degree2: int
    ) -> TriadPair:
        """
        Create a diatonic triad pair from a scale.
        
        Args:
            scale_name: Scale to use
            root: Root of the scale
            degree1: First scale degree (1-7)
            degree2: Second scale degree (1-7)
            
        Returns:
            TriadPair in open voicing
        """
        mapper = ScaleMapper(root)
        triads = mapper.get_diatonic_triads(scale_name)
        
        idx1 = (degree1 - 1) % len(triads)
        idx2 = (degree2 - 1) % len(triads)
        
        triad1 = InversionEngine.open_root(triads[idx1])
        triad2 = InversionEngine.open_root(triads[idx2])
        
        return TriadPair(
            triad1=triad1,
            triad2=triad2,
            relationship=f"diatonic_{degree1}_{degree2}"
        )
    
    def create_klemons_pair(
        self,
        root: str,
        octave: int = 4
    ) -> TriadPair:
        """
        Create a Klemons-style triad pair (major triads a whole step apart).
        
        Args:
            root: Root of first triad
            octave: Base octave
            
        Returns:
            TriadPair with two major triads a whole step apart
        """
        triad1 = Triad(root=Note(root, octave), triad_type=TriadType.MAJOR)
        triad2 = triad1.transpose(2)  # Whole step up
        
        open1 = InversionEngine.open_root(triad1)
        open2 = InversionEngine.open_root(triad2)
        
        return TriadPair(
            triad1=open1,
            triad2=open2,
            relationship="klemons"
        )
    
    def create_ust_pair(
        self,
        chord_root: str,
        ust_root: str,
        octave: int = 4
    ) -> TriadPair:
        """
        Create an Upper Structure Triad pair.
        
        Args:
            chord_root: Root of the base chord
            ust_root: Root of the upper structure
            octave: Base octave
            
        Returns:
            TriadPair for UST improvisation
        """
        base = Triad(root=Note(chord_root, octave), triad_type=TriadType.MAJOR)
        ust = Triad(root=Note(ust_root, octave), triad_type=TriadType.MAJOR)
        
        open_base = InversionEngine.open_root(base)
        open_ust = InversionEngine.open_root(ust)
        
        # Calculate interval relationship
        from .core import CHROMATIC_NOTES
        base_pc = CHROMATIC_NOTES.index(chord_root) if chord_root in CHROMATIC_NOTES else 0
        ust_pc = CHROMATIC_NOTES.index(ust_root) if ust_root in CHROMATIC_NOTES else 0
        interval = (ust_pc - base_pc) % 12
        
        return TriadPair(
            triad1=open_base,
            triad2=open_ust,
            relationship=f"ust_{interval}_semitones"
        )
    
    def generate_melodic_line(
        self,
        pair: TriadPair,
        length: int = 8,
        pattern: str = 'alternating'
    ) -> List[Note]:
        """
        Generate a melodic line using the triad pair.
        
        Args:
            pair: The triad pair to use
            length: Number of notes to generate
            pattern: 'alternating', 'sequential', or 'random'
            
        Returns:
            List of notes forming a melodic line
        """
        notes = []
        all_notes1 = sorted(pair.triad1.voices, key=lambda n: n.midi_number)
        all_notes2 = sorted(pair.triad2.voices, key=lambda n: n.midi_number)
        
        if pattern == 'alternating':
            for i in range(length):
                if i % 2 == 0:
                    notes.append(all_notes1[i % len(all_notes1)])
                else:
                    notes.append(all_notes2[i % len(all_notes2)])
        
        elif pattern == 'sequential':
            for i in range(length):
                if i < length // 2:
                    notes.append(all_notes1[i % len(all_notes1)])
                else:
                    notes.append(all_notes2[(i - length//2) % len(all_notes2)])
        
        else:  # Default sequential
            combined = all_notes1 + all_notes2
            for i in range(length):
                notes.append(combined[i % len(combined)])
        
        return notes


@dataclass
class CounterpointLine:
    """
    A single contrapuntal line.
    
    Attributes:
        voice_name: 'soprano', 'alto', or 'bass'
        notes: List of notes in the line
    """
    voice_name: str
    notes: List[Note]
    
    def to_dict(self) -> Dict:
        return {
            'voice': self.voice_name,
            'notes': [str(n) for n in self.notes]
        }


@dataclass
class CounterpointResult:
    """
    Result of counterpoint generation.
    
    Attributes:
        soprano: Top voice line
        alto: Middle voice line
        bass: Bottom voice line
        triads: Source triads
    """
    soprano: CounterpointLine
    alto: CounterpointLine
    bass: CounterpointLine
    triads: List[Triad]
    
    def to_dict(self) -> Dict:
        return {
            'soprano': self.soprano.to_dict(),
            'alto': self.alto.to_dict(),
            'bass': self.bass.to_dict(),
            'triads': [t.to_dict() for t in self.triads]
        }


class CounterpointCompanion:
    """
    Engine for creating three-voice counterpoint from triads.
    
    Each triad voice becomes an independent melodic line with
    proper counterpoint rules (contrary motion, no crossing, etc.).
    """
    
    def __init__(self, prefer_contrary: bool = True):
        self.prefer_contrary = prefer_contrary
        self.vl_module = VoiceLeadingSmartModule(
            mode=VLMode.COUNTERPOINT,
            prefer_contrary_motion=prefer_contrary
        )
    
    def generate_counterpoint(
        self,
        triads: List[Triad]
    ) -> CounterpointResult:
        """
        Generate three-voice counterpoint from a triad progression.
        
        Args:
            triads: List of triads to convert to counterpoint
            
        Returns:
            CounterpointResult with three independent lines
        """
        if not triads:
            return CounterpointResult(
                soprano=CounterpointLine('soprano', []),
                alto=CounterpointLine('alto', []),
                bass=CounterpointLine('bass', []),
                triads=[]
            )
        
        # Voice lead the progression
        voiced_triads = [InversionEngine.open_root(triads[0])]
        
        for i in range(1, len(triads)):
            result = self.vl_module.voice_lead(
                voiced_triads[-1],
                triads[i]
            )
            voiced_triads.append(result.target)
        
        # Extract lines
        soprano_notes = []
        alto_notes = []
        bass_notes = []
        
        for triad in voiced_triads:
            sorted_voices = sorted(triad.voices, key=lambda n: n.midi_number)
            bass_notes.append(sorted_voices[0])
            alto_notes.append(sorted_voices[1])
            soprano_notes.append(sorted_voices[2])
        
        return CounterpointResult(
            soprano=CounterpointLine('soprano', soprano_notes),
            alto=CounterpointLine('alto', alto_notes),
            bass=CounterpointLine('bass', bass_notes),
            triads=voiced_triads
        )
    
    def analyze_motion(
        self,
        result: CounterpointResult
    ) -> Dict[str, Dict]:
        """Analyze the motion types in the counterpoint."""
        analysis = {}
        
        for voice in ['soprano', 'alto', 'bass']:
            line = getattr(result, voice)
            if len(line.notes) < 2:
                analysis[voice] = {'motion': 'static'}
                continue
            
            motions = []
            for i in range(len(line.notes) - 1):
                interval = line.notes[i + 1].midi_number - line.notes[i].midi_number
                if interval == 0:
                    motions.append('static')
                elif abs(interval) <= 2:
                    motions.append('step')
                elif abs(interval) <= 4:
                    motions.append('skip')
                else:
                    motions.append('leap')
            
            analysis[voice] = {
                'motions': motions,
                'steps': motions.count('step'),
                'skips': motions.count('skip'),
                'leaps': motions.count('leap')
            }
        
        return analysis


@dataclass
class OrchestrationVoicing:
    """
    An orchestrated voicing with instrument assignments.
    
    Attributes:
        triad: The voiced triad
        assignments: Mapping of voice position to instrument
        register_info: Register information for each voice
    """
    triad: Triad
    assignments: Dict[str, str]
    register_info: Dict[str, Dict]
    
    def to_dict(self) -> Dict:
        return {
            'triad': self.triad.to_dict(),
            'assignments': self.assignments,
            'registers': self.register_info
        }


class OrchestrationMapper:
    """
    Maps open triad voices to instruments based on register and timbre.
    
    Default assignments:
    - Top voice: violin/flute
    - Middle voice: viola/clarinet
    - Bottom voice: cello/bass/guitar
    """
    
    DEFAULT_ASSIGNMENTS = {
        'top': ['violin', 'flute', 'oboe'],
        'middle': ['viola', 'clarinet', 'horn'],
        'bottom': ['cello', 'bass', 'bassoon', 'guitar']
    }
    
    def __init__(
        self,
        top_instruments: Optional[List[str]] = None,
        middle_instruments: Optional[List[str]] = None,
        bottom_instruments: Optional[List[str]] = None
    ):
        self.top = top_instruments or self.DEFAULT_ASSIGNMENTS['top']
        self.middle = middle_instruments or self.DEFAULT_ASSIGNMENTS['middle']
        self.bottom = bottom_instruments or self.DEFAULT_ASSIGNMENTS['bottom']
    
    def assign_instruments(
        self,
        triad: Triad,
        preferred: Optional[Dict[str, str]] = None
    ) -> OrchestrationVoicing:
        """
        Assign instruments to triad voices.
        
        Args:
            triad: The triad to orchestrate
            preferred: Optional preferred instrument assignments
            
        Returns:
            OrchestrationVoicing with assignments
        """
        sorted_voices = sorted(triad.voices, key=lambda n: n.midi_number)
        
        assignments = {}
        register_info = {}
        
        # Assign each voice
        for i, voice in enumerate(sorted_voices):
            if i == 0:
                pos = 'bottom'
                pool = self.bottom
            elif i == 1:
                pos = 'middle'
                pool = self.middle
            else:
                pos = 'top'
                pool = self.top
            
            # Check preferred
            if preferred and pos in preferred:
                instrument = preferred[pos]
            else:
                # Find best instrument for this register
                instrument = self._find_best_instrument(voice, pool)
            
            assignments[pos] = instrument
            
            # Get register info
            reg = INSTRUMENT_REGISTERS.get(instrument)
            if reg:
                register_info[pos] = {
                    'instrument': instrument,
                    'note': str(voice),
                    'in_range': reg.low <= voice.midi_number <= reg.high,
                    'in_preferred': reg.preferred_low <= voice.midi_number <= reg.preferred_high
                }
            else:
                register_info[pos] = {
                    'instrument': instrument,
                    'note': str(voice),
                    'in_range': True,
                    'in_preferred': True
                }
        
        return OrchestrationVoicing(
            triad=triad,
            assignments=assignments,
            register_info=register_info
        )
    
    def _find_best_instrument(self, note: Note, pool: List[str]) -> str:
        """Find the best instrument for a note from a pool."""
        midi = note.midi_number
        
        best = pool[0]
        best_score = float('inf')
        
        for instrument in pool:
            reg = INSTRUMENT_REGISTERS.get(instrument)
            if not reg:
                continue
            
            # Check if in range
            if not (reg.low <= midi <= reg.high):
                continue
            
            # Score based on position in preferred range
            if reg.preferred_low <= midi <= reg.preferred_high:
                # Distance from center of preferred range
                center = (reg.preferred_low + reg.preferred_high) / 2
                score = abs(midi - center)
            else:
                score = 100  # In range but not preferred
            
            if score < best_score:
                best_score = score
                best = instrument
        
        return best
    
    def orchestrate_progression(
        self,
        triads: List[Triad],
        preferred: Optional[Dict[str, str]] = None
    ) -> List[OrchestrationVoicing]:
        """Orchestrate an entire progression."""
        return [self.assign_instruments(t, preferred) for t in triads]
    
    def check_register_violations(
        self,
        voicing: OrchestrationVoicing
    ) -> List[str]:
        """Check for any register violations."""
        violations = []
        
        for pos, info in voicing.register_info.items():
            if not info['in_range']:
                violations.append(
                    f"{pos} ({info['instrument']}): {info['note']} out of range"
                )
            elif not info['in_preferred']:
                violations.append(
                    f"{pos} ({info['instrument']}): {info['note']} outside preferred range"
                )
        
        return violations

