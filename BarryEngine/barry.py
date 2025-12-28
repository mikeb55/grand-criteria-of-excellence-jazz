"""
Barry Engine - Main API
========================

The main entry point for Barry's analysis and transformation functions.
All functions are stateless and deterministic.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from .gml import GMLPhrase, GMLProgression, GMLSection, GMLForm
from .movement import score_phrase_movement, MovementScore
from .bebop import score_phrase_bebop_idiom, BebopScore
from .gce_scoring import score_section_form_alignment, GCEScore
from .transformations import (
    improve_line_movement,
    add_bebop_enclosures,
    strengthen_cadence,
    TransformationResult
)


@dataclass
class AnalysisResult:
    """
    Complete analysis result for a phrase or section.
    
    Attributes:
        movement: Movement-based harmony score
        bebop: Bebop language score
        gce: Grand Criteria of Excellence score (for sections)
        overall: Overall score (weighted combination)
        tags: Brief explanation tags (e.g., "weak cadence at bar 8")
    """
    movement: Optional[MovementScore] = None
    bebop: Optional[BebopScore] = None
    gce: Optional[GCEScore] = None
    overall: float = 0.0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class BarryEngine:
    """
    Main Barry Engine class.
    
    Provides stateless, deterministic analysis and transformation functions.
    """
    
    def __init__(self):
        """Initialize Barry engine."""
        pass
    
    def analyze_phrase(
        self,
        phrase: GMLPhrase,
        progression: Optional[GMLProgression] = None
    ) -> AnalysisResult:
        """
        Analyze a phrase for movement, bebop idiom, and overall quality.
        
        Args:
            phrase: GMLPhrase to analyze
            progression: Optional GMLProgression for harmonic context
        
        Returns:
            AnalysisResult with detailed scores and tags
        """
        # Analyze movement
        movement_score = score_phrase_movement(phrase, progression)
        
        # Analyze bebop
        bebop_score = score_phrase_bebop_idiom(phrase, progression)
        
        # Calculate overall (weighted average)
        overall = (
            0.5 * movement_score.overall +
            0.5 * bebop_score.overall
        )
        
        # Collect tags from issues
        tags = []
        tags.extend([f"Movement: {issue}" for issue in movement_score.issues[:3]])
        tags.extend([f"Bebop: {issue}" for issue in bebop_score.issues[:3]])
        
        return AnalysisResult(
            movement=movement_score,
            bebop=bebop_score,
            overall=overall,
            tags=tags
        )
    
    def analyze_section(
        self,
        section: GMLSection,
        form: Optional[GMLForm] = None
    ) -> AnalysisResult:
        """
        Analyze a section for form alignment and GCE criteria.
        
        Args:
            section: GMLSection to analyze
            form: Optional form type (uses section.form if not provided)
        
        Returns:
            AnalysisResult with detailed scores and tags
        """
        # Analyze GCE
        gce_score = score_section_form_alignment(section, form)
        
        # Also analyze individual phrases for movement/bebop
        movement_scores = []
        bebop_scores = []
        
        for phrase in section.phrases:
            phrase_result = self.analyze_phrase(phrase)
            if phrase_result.movement:
                movement_scores.append(phrase_result.movement.overall)
            if phrase_result.bebop:
                bebop_scores.append(phrase_result.bebop.overall)
        
        avg_movement = sum(movement_scores) / len(movement_scores) if movement_scores else 0.5
        avg_bebop = sum(bebop_scores) / len(bebop_scores) if bebop_scores else 0.5
        
        # Overall: weighted combination
        overall = (
            0.3 * avg_movement +
            0.3 * avg_bebop +
            0.4 * gce_score.overall
        )
        
        # Collect tags
        tags = []
        tags.extend([f"GCE: {issue}" for issue in gce_score.issues[:5]])
        
        return AnalysisResult(
            movement=None,  # Section-level, not phrase-level
            bebop=None,
            gce=gce_score,
            overall=overall,
            tags=tags
        )
    
    def improve_phrase(
        self,
        phrase: GMLPhrase,
        progression: Optional[GMLProgression] = None,
        focus: Optional[str] = None
    ) -> TransformationResult:
        """
        Improve a phrase using Barry's transformation functions.
        
        Args:
            phrase: GMLPhrase to improve
            progression: Optional GMLProgression for harmonic context
            focus: Optional focus area ("movement", "bebop", "cadence", or None for all)
        
        Returns:
            TransformationResult with improved phrase
        """
        if focus == "movement":
            return improve_line_movement(phrase, progression)
        elif focus == "bebop":
            return add_bebop_enclosures(phrase, progression)
        elif focus == "cadence":
            return strengthen_cadence(phrase)
        else:
            # Apply all transformations in sequence
            result1 = improve_line_movement(phrase, progression)
            result2 = add_bebop_enclosures(result1.phrase, progression)
            result3 = strengthen_cadence(result2.phrase)
            
            # Combine changes
            all_changes = result1.changes_made + result2.changes_made + result3.changes_made
            
            return TransformationResult(
                phrase=result3.phrase,
                changes_made=all_changes
            )


# Convenience functions are imported from their modules in __init__.py
# to avoid circular imports. They are re-exported for convenience.


def evaluate_phrase_bundle(
    phrases: List[GMLPhrase],
    context: Optional[Dict[str, Any]] = None
) -> List[AnalysisResult]:
    """
    Evaluate multiple phrase candidates and return analysis for each.
    
    Args:
        phrases: List of candidate GMLPhrase objects
        context: Optional context dict (e.g., {"progression": GMLProgression})
    
    Returns:
        List of AnalysisResult for each phrase
    """
    engine = BarryEngine()
    progression = context.get("progression") if context else None
    
    results = []
    for phrase in phrases:
        result = engine.analyze_phrase(phrase, progression)
        results.append(result)
    
    return results


def suggest_best_candidate_line(
    candidates: List[GMLPhrase],
    context: Optional[Dict[str, Any]] = None
) -> Tuple[GMLPhrase, AnalysisResult]:
    """
    Suggest the best candidate line from multiple options.
    
    Args:
        candidates: List of candidate GMLPhrase objects
        context: Optional context dict (e.g., {"progression": GMLProgression})
    
    Returns:
        Tuple of (best_phrase, analysis_result)
    """
    results = evaluate_phrase_bundle(candidates, context)
    
    # Find best by overall score
    best_idx = max(range(len(results)), key=lambda i: results[i].overall)
    
    return (candidates[best_idx], results[best_idx])

