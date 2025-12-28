"""
Bebop Language Analysis
========================

Analyzes phrases for idiomatic bebop characteristics:
- 8th-note-based lines
- Approach tones and enclosures resolving to chord tones
- Downbeat chord tone targeting
- Chromaticism that can be explained (enclosures, approach tones, scales)
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass

from .gml import GMLNote, GMLPhrase, GMLProgression


@dataclass
class BebopScore:
    """
    Bebop language analysis score for a phrase.
    
    Attributes:
        eighth_note_ratio: Ratio of 8th-note durations (0.0-1.0)
        chord_tone_targeting: Quality of chord tone targeting on downbeats (0.0-1.0)
        approach_tone_usage: Quality of approach tone usage (0.0-1.0)
        enclosure_usage: Quality of enclosure patterns (0.0-1.0)
        chromatic_explanation: How well chromaticism is explained (0.0-1.0)
        overall: Overall bebop score (0.0-1.0, higher = better)
        issues: List of issue descriptions
    """
    eighth_note_ratio: float = 0.0
    chord_tone_targeting: float = 0.0
    approach_tone_usage: float = 0.0
    enclosure_usage: float = 0.0
    chromatic_explanation: float = 0.0
    overall: float = 0.0
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


# Common bebop durations (in beats)
EIGHTH_NOTE = 0.5
QUARTER_NOTE = 1.0
HALF_NOTE = 2.0


def analyze_eighth_note_usage(notes: List[GMLNote]) -> Tuple[float, List[str]]:
    """
    Analyze ratio of 8th-note durations.
    
    Bebop lines favor 8th-note motion.
    """
    if not notes:
        return (0.0, ["No notes to analyze"])
    
    eighth_count = 0
    total_notes = 0
    
    for note in notes:
        if note.is_rest:
            continue
        
        total_notes += 1
        # Check if duration is close to 8th note (0.5 beats)
        if abs(note.duration - EIGHTH_NOTE) < 0.1:
            eighth_count += 1
    
    ratio = eighth_count / total_notes if total_notes > 0 else 0.0
    
    issues = []
    if ratio < 0.3:
        issues.append("Low 8th-note usage (bebop lines favor 8th-note motion)")
    
    return (ratio, issues)


def analyze_chord_tone_targeting(phrase: GMLPhrase) -> Tuple[float, List[str]]:
    """
    Analyze chord tone targeting on structurally strong beats (downbeats).
    
    Bebop lines should target chord tones on downbeats.
    """
    if not phrase.notes:
        return (0.0, ["No notes to analyze"])
    
    beats_per_bar = phrase.time_signature[0]
    downbeat_hits = 0
    total_downbeats = 0
    issues = []
    
    for note in phrase.notes:
        if note.is_rest:
            continue
        
        # Check if note is on a downbeat (beat 1, 3 in 4/4, or beat 1 in other meters)
        beat_in_bar = (note.onset % beats_per_bar) + 1
        
        # Downbeat: beat 1, or beat 3 in 4/4
        is_downbeat = (beat_in_bar == 1) or (beats_per_bar == 4 and beat_in_bar == 3)
        
        if is_downbeat:
            total_downbeats += 1
            
            # Check if note has harmonic context
            chord = note.harmonic_context or phrase.get_chord_at_beat(note.onset)
            
            if chord:
                # Simplified: assume it's a chord tone if we have context
                # Full implementation would parse chord and check membership
                downbeat_hits += 1
            else:
                issues.append(f"Downbeat at {note.onset} lacks harmonic context")
    
    score = downbeat_hits / total_downbeats if total_downbeats > 0 else 0.5
    
    if score < 0.4:
        issues.append("Weak chord tone targeting on downbeats")
    
    return (score, issues)


def detect_enclosure(note1: GMLNote, note2: GMLNote, target: GMLNote) -> bool:
    """
    Detect if note1 and note2 form an enclosure around target.
    
    Enclosure: approach from above and below (e.g., target-1, target+1, target).
    """
    if note1.is_rest or note2.is_rest or target.is_rest:
        return False
    
    # Check if note1 and note2 are one semitone above and below target
    interval1 = abs(note1.interval_to(target))
    interval2 = abs(note2.interval_to(target))
    
    # Enclosure: one note is +1, other is -1 from target
    return (interval1 == 1 and interval2 == 1) and (
        (note1.midi_pitch > target.midi_pitch and note2.midi_pitch < target.midi_pitch) or
        (note1.midi_pitch < target.midi_pitch and note2.midi_pitch > target.midi_pitch)
    )


def analyze_enclosures(notes: List[GMLNote]) -> Tuple[float, List[str]]:
    """
    Analyze usage of enclosure patterns.
    
    Enclosures: chromatic or diatonic approach from above and below.
    """
    if len(notes) < 3:
        return (0.0, ["Not enough notes for enclosure analysis"])
    
    enclosure_count = 0
    total_opportunities = 0
    
    # Look for 3-note patterns: approach, approach, target
    for i in range(len(notes) - 2):
        if notes[i].is_rest or notes[i+1].is_rest or notes[i+2].is_rest:
            continue
        
        total_opportunities += 1
        
        if detect_enclosure(notes[i], notes[i+1], notes[i+2]):
            enclosure_count += 1
    
    ratio = enclosure_count / total_opportunities if total_opportunities > 0 else 0.0
    
    issues = []
    if ratio < 0.1:
        issues.append("Few enclosure patterns detected")
    
    return (ratio, issues)


def analyze_approach_tones(notes: List[GMLNote]) -> Tuple[float, List[str]]:
    """
    Analyze usage of approach tones (chromatic or diatonic).
    
    Approach tones: notes that lead stepwise into chord tones.
    """
    if len(notes) < 2:
        return (0.0, ["Not enough notes for approach tone analysis"])
    
    approach_count = 0
    total_motions = 0
    
    for i in range(len(notes) - 1):
        if notes[i].is_rest or notes[i+1].is_rest:
            continue
        
        total_motions += 1
        interval = abs(notes[i].interval_to(notes[i+1]))
        
        # Stepwise motion (approach tone)
        if interval <= 2:
            approach_count += 1
    
    ratio = approach_count / total_motions if total_motions > 0 else 0.0
    
    issues = []
    if ratio < 0.3:
        issues.append("Low approach tone usage")
    
    return (ratio, issues)


def analyze_chromatic_explanation(notes: List[GMLNote], phrase: GMLPhrase) -> Tuple[float, List[str]]:
    """
    Analyze how well chromaticism is explained.
    
    Good chromaticism: enclosures, approach tones, scale-based (diminished, altered).
    Bad chromaticism: arbitrary "outside" notes.
    """
    if not notes:
        return (0.0, ["No notes to analyze"])
    
    # Simplified: check if chromatic notes are part of stepwise patterns
    # Full implementation would analyze scale membership and pattern context
    
    chromatic_notes = 0
    explained_chromatic = 0
    
    for i, note in enumerate(notes):
        if note.is_rest:
            continue
        
        # Check if note is chromatic (not in key)
        # Simplified: assume all notes are potentially valid
        # Full implementation would check key membership
        
        # Check if it's part of a stepwise pattern (explained)
        if i > 0 and i < len(notes) - 1:
            prev_note = notes[i-1]
            next_note = notes[i+1]
            
            if not prev_note.is_rest and not next_note.is_rest:
                # Stepwise motion suggests explanation
                if (abs(prev_note.interval_to(note)) <= 2 and 
                    abs(note.interval_to(next_note)) <= 2):
                    explained_chromatic += 1
        
        chromatic_notes += 1  # Simplified
    
    score = explained_chromatic / chromatic_notes if chromatic_notes > 0 else 0.5
    
    issues = []
    if score < 0.5:
        issues.append("Some chromaticism may be unmotivated")
    
    return (score, issues)


def score_phrase_bebop_idiom(phrase: GMLPhrase, harmony: Optional[GMLProgression] = None) -> BebopScore:
    """
    Score a phrase for bebop language idiomaticity.
    
    Args:
        phrase: GMLPhrase to analyze
        harmony: Optional GMLProgression for harmonic context
    
    Returns:
        BebopScore with detailed analysis
    """
    notes = [n for n in phrase.notes if not n.is_rest]
    
    if not notes:
        return BebopScore(
            overall=0.5,
            issues=["No notes to analyze"]
        )
    
    # Analyze components
    eighth_ratio, eighth_issues = analyze_eighth_note_usage(notes)
    chord_tone_score, chord_issues = analyze_chord_tone_targeting(phrase)
    approach_score, approach_issues = analyze_approach_tones(notes)
    enclosure_score, enclosure_issues = analyze_enclosures(notes)
    chromatic_score, chromatic_issues = analyze_chromatic_explanation(notes, phrase)
    
    # Combine issues
    all_issues = eighth_issues + chord_issues + approach_issues + enclosure_issues + chromatic_issues
    
    # Calculate overall score (weighted average)
    weights = {
        'eighth': 0.2,
        'chord_tone': 0.3,
        'approach': 0.2,
        'enclosure': 0.15,
        'chromatic': 0.15,
    }
    
    overall = (
        weights['eighth'] * eighth_ratio +
        weights['chord_tone'] * chord_tone_score +
        weights['approach'] * approach_score +
        weights['enclosure'] * enclosure_score +
        weights['chromatic'] * chromatic_score
    )
    
    # Clamp to [0, 1]
    overall = max(0.0, min(1.0, overall))
    
    return BebopScore(
        eighth_note_ratio=eighth_ratio,
        chord_tone_targeting=chord_tone_score,
        approach_tone_usage=approach_score,
        enclosure_usage=enclosure_score,
        chromatic_explanation=chromatic_score,
        overall=overall,
        issues=all_issues
    )

