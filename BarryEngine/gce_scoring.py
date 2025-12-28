"""
Grand Criteria of Excellence (GCE) Scoring
===========================================

Evaluates phrases and sections against the Grand Criteria of Excellence:
- Tension-release arcs
- Motivic development
- Form and architecture
- Idiomaticity and authenticity
- Playability (abstract)
"""

from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass

from .gml import GMLPhrase, GMLSection, GMLForm, PhraseRole


@dataclass
class GCEScore:
    """
    Grand Criteria of Excellence score.
    
    Attributes:
        tension_release: Quality of tension-release arcs (0.0-1.0)
        motivic_development: Quality of motivic development (0.0-1.0)
        form_alignment: Alignment with form structure (0.0-1.0)
        idiomaticity: Idiomatic jazz language usage (0.0-1.0)
        playability: Abstract playability score (0.0-1.0)
        overall: Overall GCE score (0.0-1.0, higher = better)
        issues: List of issue descriptions
    """
    tension_release: float = 0.0
    motivic_development: float = 0.0
    form_alignment: float = 0.0
    idiomaticity: float = 0.0
    playability: float = 0.0
    overall: float = 0.0
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


def analyze_tension_release(phrases: List[GMLPhrase]) -> Tuple[float, List[str]]:
    """
    Analyze tension-release arcs.
    
    Phrases should build and release tension in recognizable waves.
    """
    if len(phrases) < 2:
        return (0.5, ["Not enough phrases for tension-release analysis"])
    
    # Simplified: check for pitch range variation
    # Full implementation would analyze harmonic tension, rhythmic density, etc.
    
    pitch_ranges = []
    for phrase in phrases:
        if phrase.notes:
            pitch_range = phrase.get_pitch_range()
            pitch_ranges.append(pitch_range[1] - pitch_range[0])  # Range span
    
    if not pitch_ranges:
        return (0.5, ["No pitch data for tension analysis"])
    
    # Check for variation (indicates tension-release)
    if len(set(pitch_ranges)) > 1:
        score = 0.7  # Good variation
    else:
        score = 0.3  # Flat, no variation
        return (score, ["Flat tension (no variation in pitch range)"])
    
    return (score, [])


def extract_motif(notes: List, length: int = 3) -> Optional[Tuple]:
    """Extract a short motif (sequence of intervals)."""
    if len(notes) < length:
        return None
    
    intervals = []
    for i in range(length - 1):
        if i < len(notes) - 1:
            interval = notes[i].interval_to(notes[i+1])
            intervals.append(interval)
    
    return tuple(intervals)


def analyze_motivic_development(phrases: List[GMLPhrase]) -> Tuple[float, List[str]]:
    """
    Analyze motivic development.
    
    Detects reuse and variation of ideas (sequence, inversion, displacement).
    """
    if len(phrases) < 2:
        return (0.5, ["Not enough phrases for motivic analysis"])
    
    # Extract motifs from each phrase
    motifs = []
    for phrase in phrases:
        notes = [n for n in phrase.notes if not n.is_rest]
        if len(notes) >= 3:
            motif = extract_motif(notes, length=3)
            if motif:
                motifs.append(motif)
    
    if len(motifs) < 2:
        return (0.3, ["Insufficient motifs for development analysis"])
    
    # Check for repeated or varied motifs
    unique_motifs = set(motifs)
    repetition_ratio = 1.0 - (len(unique_motifs) / len(motifs))
    
    # Some repetition is good (development), but not too much (boring)
    if 0.2 <= repetition_ratio <= 0.6:
        score = 0.7
    elif repetition_ratio < 0.2:
        score = 0.4
        return (score, ["Little motivic repetition (may lack development)"])
    else:
        score = 0.5
        return (score, ["Too much exact repetition (may lack variation)"])
    
    return (score, [])


def analyze_form_alignment(section: GMLSection, form: Optional[GMLForm] = None) -> Tuple[float, List[str]]:
    """
    Analyze alignment with form structure.
    
    Ensures sections relate motivically and harmonically but provide contrast.
    """
    if not section.phrases:
        return (0.5, ["No phrases in section"])
    
    form_to_check = form or section.form
    
    # Check phrase roles
    roles = [p.role for p in section.phrases]
    
    # Good form: has opening, continuation, and cadential phrases
    has_opening = PhraseRole.OPENING in roles
    has_continuation = PhraseRole.CONTINUATION in roles
    has_cadential = PhraseRole.CADENTIAL in roles
    
    score = 0.5
    issues = []
    
    if has_opening and has_continuation and has_cadential:
        score = 0.8
    elif has_opening and has_cadential:
        score = 0.6
    else:
        issues.append("Section lacks clear phrase roles (opening/continuation/cadential)")
    
    # Check for contrast (different pitch ranges, rhythms)
    if len(section.phrases) >= 2:
        pitch_ranges = [p.get_pitch_range() for p in section.phrases if p.notes]
        if pitch_ranges:
            ranges = [r[1] - r[0] for r in pitch_ranges]
            if len(set(ranges)) > 1:
                score += 0.1  # Bonus for contrast
            else:
                issues.append("Phrases lack contrast")
    
    return (min(1.0, score), issues)


def analyze_idiomaticity(phrases: List[GMLPhrase]) -> Tuple[float, List[str]]:
    """
    Analyze idiomatic jazz language usage.
    
    Rewards lines and voicings that resemble real jazz practice.
    """
    if not phrases:
        return (0.5, ["No phrases to analyze"])
    
    # Simplified: check for common jazz patterns
    # Full implementation would check for:
    # - Standard cadential patterns
    # - Typical tensions
    # - Idiomatic comping patterns
    
    score = 0.6  # Default moderate score
    issues = []
    
    # Check for cadential phrases
    cadential_count = sum(1 for p in phrases if p.role == PhraseRole.CADENTIAL)
    if cadential_count == 0:
        issues.append("No cadential phrases detected")
        score -= 0.1
    
    # Check phrase lengths (typical: 2, 4, 8 bars)
    for phrase in phrases:
        bar_count = phrase.bar_count
        if bar_count not in [1, 2, 4, 8]:
            issues.append(f"Unusual phrase length: {bar_count} bars")
            score -= 0.05
    
    return (max(0.0, min(1.0, score)), issues)


def analyze_playability(phrases: List[GMLPhrase]) -> Tuple[float, List[str]]:
    """
    Analyze abstract playability.
    
    Models range and density constraints (avoids constant extremes).
    """
    if not phrases:
        return (0.5, ["No phrases to analyze"])
    
    all_notes = []
    for phrase in phrases:
        all_notes.extend([n for n in phrase.notes if not n.is_rest])
    
    if not all_notes:
        return (0.5, ["No notes to analyze"])
    
    # Check pitch range
    pitch_range = (min(n.midi_pitch for n in all_notes),
                   max(n.midi_pitch for n in all_notes))
    range_span = pitch_range[1] - pitch_range[0]
    
    score = 0.7
    issues = []
    
    # Very wide range (> 2 octaves) may be difficult
    if range_span > 24:
        score -= 0.2
        issues.append(f"Very wide pitch range: {range_span} semitones")
    
    # Check for constant extreme registers
    high_notes = sum(1 for n in all_notes if n.midi_pitch > 80)
    low_notes = sum(1 for n in all_notes if n.midi_pitch < 50)
    total_notes = len(all_notes)
    
    if high_notes / total_notes > 0.7:
        score -= 0.15
        issues.append("Too many notes in extreme high register")
    
    if low_notes / total_notes > 0.7:
        score -= 0.15
        issues.append("Too many notes in extreme low register")
    
    # Check density (notes per beat)
    total_duration = sum(n.duration for n in all_notes)
    if total_duration > 0:
        density = len(all_notes) / total_duration
        if density > 4.0:  # Very dense
            score -= 0.1
            issues.append("Very high note density")
    
    return (max(0.0, min(1.0, score)), issues)


def score_section_form_alignment(section: GMLSection, form: Optional[GMLForm] = None) -> GCEScore:
    """
    Score a section for Grand Criteria of Excellence.
    
    Args:
        section: GMLSection to analyze
        form: Optional form type (uses section.form if not provided)
    
    Returns:
        GCEScore with detailed analysis
    """
    if not section.phrases:
        return GCEScore(
            overall=0.5,
            issues=["No phrases in section"]
        )
    
    # Analyze components
    tension_score, tension_issues = analyze_tension_release(section.phrases)
    motivic_score, motivic_issues = analyze_motivic_development(section.phrases)
    form_score, form_issues = analyze_form_alignment(section, form)
    idiomatic_score, idiomatic_issues = analyze_idiomaticity(section.phrases)
    playability_score, playability_issues = analyze_playability(section.phrases)
    
    # Combine issues
    all_issues = tension_issues + motivic_issues + form_issues + idiomatic_issues + playability_issues
    
    # Calculate overall score (weighted average)
    weights = {
        'tension': 0.25,
        'motivic': 0.25,
        'form': 0.2,
        'idiomatic': 0.15,
        'playability': 0.15,
    }
    
    overall = (
        weights['tension'] * tension_score +
        weights['motivic'] * motivic_score +
        weights['form'] * form_score +
        weights['idiomatic'] * idiomatic_score +
        weights['playability'] * playability_score
    )
    
    # Clamp to [0, 1]
    overall = max(0.0, min(1.0, overall))
    
    return GCEScore(
        tension_release=tension_score,
        motivic_development=motivic_score,
        form_alignment=form_score,
        idiomaticity=idiomatic_score,
        playability=playability_score,
        overall=overall,
        issues=all_issues
    )

