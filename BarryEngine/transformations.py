"""
Transformation Functions
========================

Functions to improve phrases based on Barry's analysis:
- improve_line_movement: Enhance stepwise motion and voice-leading
- add_bebop_enclosures: Add bebop enclosures to chord tones
- strengthen_cadence: Improve cadential resolution
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass

from .gml import GMLNote, GMLPhrase, GMLProgression, note_from_midi


@dataclass
class TransformationResult:
    """
    Result of a transformation operation.
    
    Attributes:
        phrase: Transformed GMLPhrase
        changes_made: List of descriptions of changes
        score_improvement: Improvement in score (if applicable)
    """
    phrase: GMLPhrase
    changes_made: List[str]
    score_improvement: Optional[float] = None


def improve_line_movement(phrase: GMLPhrase, harmony: Optional[GMLProgression] = None) -> TransformationResult:
    """
    Improve stepwise motion and voice-leading in a phrase.
    
    Args:
        phrase: GMLPhrase to improve
        harmony: Optional GMLProgression for harmonic context
    
    Returns:
        TransformationResult with improved phrase
    """
    if not phrase.notes:
        return TransformationResult(
            phrase=phrase,
            changes_made=["No notes to transform"]
        )
    
    new_notes = []
    changes = []
    
    for i, note in enumerate(phrase.notes):
        if note.is_rest:
            new_notes.append(note)
            continue
        
        # Check for large leaps
        if i > 0 and not phrase.notes[i-1].is_rest:
            prev_note = phrase.notes[i-1]
            interval = abs(prev_note.interval_to(note))
            
            # If large leap (> 7 semitones), try to add passing tones
            if interval > 7:
                # Add a passing tone between prev and current
                mid_pitch = (prev_note.midi_pitch + note.midi_pitch) // 2
                passing_note = note_from_midi(
                    mid_pitch,
                    duration=min(0.25, note.duration / 2),
                    onset=note.onset - min(0.25, note.duration / 2)
                )
                passing_note.harmonic_context = note.harmonic_context
                new_notes.append(passing_note)
                changes.append(f"Added passing tone between notes {i-1} and {i}")
        
        new_notes.append(note)
    
    improved_phrase = GMLPhrase(
        notes=new_notes,
        bar_start=phrase.bar_start,
        bar_end=phrase.bar_end,
        role=phrase.role,
        harmonic_progression=phrase.harmonic_progression,
        key=phrase.key,
        time_signature=phrase.time_signature
    )
    
    return TransformationResult(
        phrase=improved_phrase,
        changes_made=changes
    )


def add_bebop_enclosures(phrase: GMLPhrase, harmony: Optional[GMLProgression] = None) -> TransformationResult:
    """
    Add bebop enclosures to chord tones in a phrase.
    
    Enclosures: approach from above and below (e.g., target-1, target+1, target).
    
    Args:
        phrase: GMLPhrase to improve
        harmony: Optional GMLProgression for harmonic context
    
    Returns:
        TransformationResult with improved phrase
    """
    if not phrase.notes:
        return TransformationResult(
            phrase=phrase,
            changes_made=["No notes to transform"]
        )
    
    new_notes = []
    changes = []
    i = 0
    
    while i < len(phrase.notes):
        note = phrase.notes[i]
        
        if note.is_rest:
            new_notes.append(note)
            i += 1
            continue
        
        # Check if this note is a chord tone (simplified: assume it is if we have context)
        chord = note.harmonic_context or phrase.get_chord_at_beat(note.onset)
        
        if chord and i < len(phrase.notes) - 1:
            # Check if next note is not already part of an enclosure
            next_note = phrase.notes[i + 1]
            
            # Add enclosure: approach from above, then below, then target
            if not next_note.is_rest:
                # Create enclosure notes
                target_pitch = note.midi_pitch
                above_pitch = target_pitch + 1
                below_pitch = target_pitch - 1
                
                # Adjust durations
                enclosure_duration = min(0.125, note.duration / 3)
                
                above_note = note_from_midi(
                    above_pitch,
                    duration=enclosure_duration,
                    onset=note.onset - 2 * enclosure_duration
                )
                above_note.harmonic_context = note.harmonic_context
                
                below_note = note_from_midi(
                    below_pitch,
                    duration=enclosure_duration,
                    onset=note.onset - enclosure_duration
                )
                below_note.harmonic_context = note.harmonic_context
                
                # Original note (target)
                target_note = GMLNote(
                    pitch_class=note.pitch_class,
                    octave=note.octave,
                    duration=note.duration - 2 * enclosure_duration,
                    onset=note.onset,
                    harmonic_context=note.harmonic_context
                )
                
                new_notes.extend([above_note, below_note, target_note])
                changes.append(f"Added enclosure around note {i}")
                i += 1
            else:
                new_notes.append(note)
                i += 1
        else:
            new_notes.append(note)
            i += 1
    
    improved_phrase = GMLPhrase(
        notes=new_notes,
        bar_start=phrase.bar_start,
        bar_end=phrase.bar_end,
        role=phrase.role,
        harmonic_progression=phrase.harmonic_progression,
        key=phrase.key,
        time_signature=phrase.time_signature
    )
    
    return TransformationResult(
        phrase=improved_phrase,
        changes_made=changes
    )


def strengthen_cadence(phrase: GMLPhrase, cadence_context: Optional[str] = None) -> TransformationResult:
    """
    Strengthen cadential resolution in a phrase.
    
    Ensures phrase ends with clear resolution (e.g., 7th -> 3rd, 4th -> 3rd).
    
    Args:
        phrase: GMLPhrase to improve (should be a cadential phrase)
        cadence_context: Optional cadence type (e.g., "V-I", "ii-V-I")
    
    Returns:
        TransformationResult with improved phrase
    """
    if not phrase.notes:
        return TransformationResult(
            phrase=phrase,
            changes_made=["No notes to transform"]
        )
    
    # Get last few notes
    last_notes = [n for n in phrase.notes if not n.is_rest][-2:]
    
    if len(last_notes) < 2:
        return TransformationResult(
            phrase=phrase,
            changes_made=["Not enough notes for cadence strengthening"]
        )
    
    new_notes = phrase.notes.copy()
    changes = []
    
    # Ensure last note is on a strong beat (downbeat)
    last_note = new_notes[-1]
    beats_per_bar = phrase.time_signature[0]
    beat_in_bar = (last_note.onset % beats_per_bar) + 1
    
    # If not on downbeat, adjust
    if beat_in_bar != 1:
        # Move to downbeat of next bar
        bar_num = int(last_note.onset // beats_per_bar) + 1
        new_onset = bar_num * beats_per_bar
        new_notes[-1] = GMLNote(
            pitch_class=last_note.pitch_class,
            octave=last_note.octave,
            duration=last_note.duration,
            onset=new_onset,
            harmonic_context=last_note.harmonic_context
        )
        changes.append("Moved final note to downbeat for stronger cadence")
    
    # Ensure resolution motion (7th -> 3rd, 4th -> 3rd, etc.)
    if len(last_notes) >= 2:
        penultimate = last_notes[-2]
        final = last_notes[-1]
        
        # Check if we have a resolution interval
        interval = abs(penultimate.interval_to(final))
        
        # Good resolution intervals: 4th (5 semitones), 5th (7 semitones), stepwise
        if interval not in [1, 2, 5, 7]:
            # Try to adjust final note for better resolution
            # Simplified: move to stepwise resolution
            if penultimate.midi_pitch > final.midi_pitch:
                new_final_pitch = penultimate.midi_pitch - 2  # Step down
            else:
                new_final_pitch = penultimate.midi_pitch + 2  # Step up
            
            new_notes[-1] = GMLNote(
                pitch_class=new_final_pitch % 12,
                octave=(new_final_pitch // 12) - 1,
                duration=final.duration,
                onset=final.onset,
                harmonic_context=final.harmonic_context
            )
            changes.append("Adjusted final note for stronger resolution")
    
    improved_phrase = GMLPhrase(
        notes=new_notes,
        bar_start=phrase.bar_start,
        bar_end=phrase.bar_end,
        role=phrase.role,
        harmonic_progression=phrase.harmonic_progression,
        key=phrase.key,
        time_signature=phrase.time_signature
    )
    
    return TransformationResult(
        phrase=improved_phrase,
        changes_made=changes
    )

