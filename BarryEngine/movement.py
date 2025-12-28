"""
Movement-Based Harmony and Voice-Leading Analysis
==================================================

Analyzes phrases for:
- Stepwise motion and small-interval voice-leading
- Guide tone resolution (3rds, 7ths, tensions)
- Standard progression patterns (ii-V-I, turnarounds, etc.)
- Penalties for large, unmotivated leaps
"""

from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

from .gml import GMLNote, GMLPhrase, GMLProgression, HarmonicFunction


@dataclass
class MovementScore:
    """
    Movement analysis score for a phrase.
    
    Attributes:
        stepwise_ratio: Ratio of stepwise motions (0.0-1.0)
        guide_tone_score: Quality of guide tone resolution (0.0-1.0)
        voice_leading_score: Smoothness of voice-leading (0.0-1.0)
        progression_score: Recognition of standard patterns (0.0-1.0)
        leap_penalty: Penalty for large unmotivated leaps (0.0-1.0, higher = worse)
        overall: Overall movement score (0.0-1.0, higher = better)
        issues: List of issue descriptions
    """
    stepwise_ratio: float = 0.0
    guide_tone_score: float = 0.0
    voice_leading_score: float = 0.0
    progression_score: float = 0.0
    leap_penalty: float = 0.0
    overall: float = 0.0
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


# Guide tones: 3rd, 7th, and key tensions (9, 11, 13)
GUIDE_TONES = {
    '3rd': 4,  # Major 3rd
    '3rd_minor': 3,  # Minor 3rd
    '7th': 10,  # Minor 7th
    '7th_major': 11,  # Major 7th
    '9th': 2,  # 9th (octave + 2)
    '11th': 5,  # 11th (octave + 5)
    '13th': 9,  # 13th (octave + 9)
}

# Standard progression patterns
STANDARD_PROGRESSIONS = {
    'ii-V-I': [2, 5, 1],
    'ii-V': [2, 5],
    'V-I': [5, 1],
    'I-vi-ii-V': [1, 6, 2, 5],
    'vi-ii-V-I': [6, 2, 5, 1],
    'I-IV-V-I': [1, 4, 5, 1],
    'I-vi-IV-V': [1, 6, 4, 5],
}


def analyze_stepwise_motion(notes: List[GMLNote]) -> Tuple[float, List[str]]:
    """
    Analyze stepwise motion in a sequence of notes.
    
    Returns:
        Tuple of (stepwise_ratio, issues)
    """
    if len(notes) < 2:
        return (1.0, [])
    
    stepwise_count = 0
    total_motions = 0
    issues = []
    
    for i in range(len(notes) - 1):
        if notes[i].is_rest or notes[i+1].is_rest:
            continue
        
        total_motions += 1
        interval = abs(notes[i].interval_to(notes[i+1]))
        
        if interval <= 2:  # Stepwise (m2 or M2)
            stepwise_count += 1
        elif interval > 7:  # Large leap
            issues.append(f"Large leap of {interval} semitones at note {i+1}")
    
    ratio = stepwise_count / total_motions if total_motions > 0 else 1.0
    return (ratio, issues)


def analyze_guide_tones(phrase: GMLPhrase, progression: Optional[GMLProgression] = None) -> Tuple[float, List[str]]:
    """
    Analyze guide tone resolution in a phrase.
    
    Guide tones (3rd, 7th) should resolve smoothly through progressions.
    """
    if not phrase.notes or not phrase.harmonic_progression:
        return (0.5, ["No harmonic context provided"])
    
    # For now, simplified: check if notes align with chord tones
    # In a full implementation, we'd analyze voice-leading between chords
    chord_tone_hits = 0
    total_notes = 0
    issues = []
    
    for note in phrase.notes:
        if note.is_rest:
            continue
        
        total_notes += 1
        chord = note.harmonic_context or phrase.get_chord_at_beat(note.onset)
        
        if chord:
            # Simplified: check if note is a chord tone
            # Full implementation would parse chord and check membership
            chord_tone_hits += 1  # Placeholder
    
    score = chord_tone_hits / total_notes if total_notes > 0 else 0.5
    
    if score < 0.3:
        issues.append("Low guide tone/chord tone alignment")
    
    return (score, issues)


def analyze_voice_leading(notes: List[GMLNote]) -> Tuple[float, List[str]]:
    """
    Analyze voice-leading smoothness.
    
    Prefers:
    - Stepwise motion
    - Common tones
    - Contrary/oblique motion over parallel
    """
    if len(notes) < 2:
        return (1.0, [])
    
    smooth_motions = 0
    total_motions = 0
    issues = []
    
    for i in range(len(notes) - 1):
        if notes[i].is_rest or notes[i+1].is_rest:
            continue
        
        total_motions += 1
        interval = abs(notes[i].interval_to(notes[i+1]))
        
        # Smooth: stepwise (1-2 semitones) or small leaps (3-4)
        if interval <= 4:
            smooth_motions += 1
        elif interval > 7:
            issues.append(f"Large voice-leading leap of {interval} semitones")
    
    score = smooth_motions / total_motions if total_motions > 0 else 1.0
    return (score, issues)


def analyze_progression_pattern(progression: GMLProgression) -> Tuple[float, List[str]]:
    """
    Recognize standard progression patterns.
    
    Returns score based on how well progression matches standard jazz patterns.
    """
    if not progression.chords or len(progression.chords) < 2:
        return (0.5, ["Progression too short"])
    
    # Simplified: check for ii-V-I patterns
    # Full implementation would parse chord roots and analyze function
    
    # For now, just check if we have multiple chords (indicates progression)
    score = min(1.0, len(progression.chords) / 4.0)  # Normalize to 4-chord progression
    
    issues = []
    if len(progression.chords) < 2:
        issues.append("Progression too short for meaningful analysis")
    
    return (score, issues)


def calculate_leap_penalty(notes: List[GMLNote]) -> Tuple[float, List[str]]:
    """
    Calculate penalty for large, unmotivated leaps.
    
    Returns:
        Tuple of (penalty_score, issues) where penalty_score is 0.0-1.0 (higher = worse)
    """
    if len(notes) < 2:
        return (0.0, [])
    
    large_leaps = 0
    total_motions = 0
    issues = []
    
    for i in range(len(notes) - 1):
        if notes[i].is_rest or notes[i+1].is_rest:
            continue
        
        total_motions += 1
        interval = abs(notes[i].interval_to(notes[i+1]))
        
        # Large leap: > 7 semitones (perfect 5th)
        if interval > 7:
            large_leaps += 1
            # Check if it's "motivated" (resolves stepwise)
            if i + 2 < len(notes) and not notes[i+2].is_rest:
                resolution_interval = abs(notes[i+1].interval_to(notes[i+2]))
                if resolution_interval > 2:
                    issues.append(f"Unmotivated large leap of {interval} semitones at note {i+1}")
    
    # Penalty: ratio of large leaps
    penalty = large_leaps / total_motions if total_motions > 0 else 0.0
    return (penalty, issues)


def score_phrase_movement(phrase: GMLPhrase, progression: Optional[GMLProgression] = None) -> MovementScore:
    """
    Score a phrase for movement-based harmony and voice-leading.
    
    Args:
        phrase: GMLPhrase to analyze
        progression: Optional GMLProgression for harmonic context
    
    Returns:
        MovementScore with detailed analysis
    """
    notes = [n for n in phrase.notes if not n.is_rest]
    
    if not notes:
        return MovementScore(
            overall=0.5,
            issues=["No notes to analyze"]
        )
    
    # Analyze components
    stepwise_ratio, stepwise_issues = analyze_stepwise_motion(notes)
    guide_tone_score, guide_issues = analyze_guide_tones(phrase, progression)
    voice_leading_score, vl_issues = analyze_voice_leading(notes)
    leap_penalty, leap_issues = calculate_leap_penalty(notes)
    
    # Progression analysis
    if progression:
        progression_score, prog_issues = analyze_progression_pattern(progression)
    else:
        progression_score = 0.5
        prog_issues = ["No progression provided"]
    
    # Combine issues
    all_issues = stepwise_issues + guide_issues + vl_issues + leap_issues + prog_issues
    
    # Calculate overall score
    # Weighted average, with leap_penalty subtracted
    weights = {
        'stepwise': 0.3,
        'guide_tone': 0.25,
        'voice_leading': 0.25,
        'progression': 0.2,
    }
    
    overall = (
        weights['stepwise'] * stepwise_ratio +
        weights['guide_tone'] * guide_tone_score +
        weights['voice_leading'] * voice_leading_score +
        weights['progression'] * progression_score -
        0.2 * leap_penalty  # Subtract penalty
    )
    
    # Clamp to [0, 1]
    overall = max(0.0, min(1.0, overall))
    
    return MovementScore(
        stepwise_ratio=stepwise_ratio,
        guide_tone_score=guide_tone_score,
        voice_leading_score=voice_leading_score,
        progression_score=progression_score,
        leap_penalty=leap_penalty,
        overall=overall,
        issues=all_issues
    )

