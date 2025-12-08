"""
Error Handler for CEO Module
==============================

Provides comprehensive error detection, diagnostics, and fallback logic.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum


class CEOErrorType(Enum):
    """Types of errors the CEO can encounter."""
    INVALID_SCALE = "invalid_scale"
    INVALID_KEY = "invalid_key"
    MISSING_MELODY = "missing_melody"
    IMPOSSIBLE_VOICING = "impossible_voicing"
    INVALID_TRIAD_PAIR = "invalid_triad_pair"
    ENGINE_NOT_AVAILABLE = "engine_not_available"
    ENGINE_EXECUTION_FAILED = "engine_execution_failed"
    EXPORT_FAILED = "export_failed"
    MUSICXML_INVALID = "musicxml_invalid"
    REGISTER_OUT_OF_RANGE = "register_out_of_range"
    STRING_SET_IMPOSSIBLE = "string_set_impossible"
    PARAMETER_VALIDATION_FAILED = "parameter_validation_failed"
    UNKNOWN = "unknown"


@dataclass
class CEOError:
    """
    A structured error from the CEO.
    
    Attributes:
        error_type: Type of error
        message: Human-readable message
        details: Additional details
        recoverable: Whether fallback is possible
        fallback_suggestion: Suggested fallback action
        original_exception: Original exception if any
    """
    error_type: CEOErrorType
    message: str
    details: Optional[Dict] = None
    recoverable: bool = True
    fallback_suggestion: Optional[str] = None
    original_exception: Optional[Exception] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "details": self.details,
            "recoverable": self.recoverable,
            "fallback_suggestion": self.fallback_suggestion,
        }


@dataclass
class DiagnosticResult:
    """
    Result of a diagnostic check.
    
    Attributes:
        passed: Whether the check passed
        check_name: Name of the check
        message: Result message
        severity: 'info', 'warning', 'error'
    """
    passed: bool
    check_name: str
    message: str
    severity: str = "info"


class CEOErrorHandler:
    """
    Handles errors, provides diagnostics, and manages fallbacks.
    """
    
    # Valid values for validation
    VALID_KEYS = [
        "C", "C#", "Db", "D", "D#", "Eb", "E", "F",
        "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"
    ]
    
    VALID_SCALES = [
        "major", "minor", "dorian", "phrygian", "lydian", "mixolydian",
        "aeolian", "locrian", "melodic_minor", "harmonic_minor",
        "whole_tone", "diminished", "altered", "lydian_dominant",
        "pentatonic_major", "pentatonic_minor", "blues"
    ]
    
    VALID_STRING_SETS = ["6-4", "5-3", "4-2", "auto"]
    
    GUITAR_REGISTER = (40, 84)  # E2 to C6
    
    def __init__(self):
        """Initialize the error handler."""
        self.errors: List[CEOError] = []
        self.warnings: List[str] = []
    
    def clear(self):
        """Clear all errors and warnings."""
        self.errors = []
        self.warnings = []
    
    def add_error(self, error: CEOError):
        """Add an error to the list."""
        self.errors.append(error)
    
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_fatal_errors(self) -> bool:
        """Check if there are non-recoverable errors."""
        return any(not e.recoverable for e in self.errors)
    
    def get_all_errors(self) -> List[CEOError]:
        """Get all errors."""
        return self.errors
    
    def get_error_summary(self) -> Dict:
        """Get a summary of all errors and warnings."""
        return {
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "has_fatal_errors": self.has_fatal_errors(),
            "errors": [e.to_dict() for e in self.errors],
            "warnings": self.warnings
        }
    
    # =========================================================================
    # Validation Methods
    # =========================================================================
    
    def validate_key(self, key: str) -> Tuple[bool, Optional[CEOError]]:
        """Validate a key name."""
        if key in self.VALID_KEYS:
            return True, None
        
        # Try to find similar key
        similar = self._find_similar(key, self.VALID_KEYS)
        
        error = CEOError(
            error_type=CEOErrorType.INVALID_KEY,
            message=f"Invalid key: '{key}'",
            details={"provided": key, "valid_keys": self.VALID_KEYS},
            recoverable=True,
            fallback_suggestion=f"Using 'C' as fallback. Did you mean '{similar}'?" if similar else "Using 'C' as fallback."
        )
        return False, error
    
    def validate_scale(self, scale: str) -> Tuple[bool, Optional[CEOError]]:
        """Validate a scale name."""
        scale_lower = scale.lower()
        if scale_lower in self.VALID_SCALES:
            return True, None
        
        similar = self._find_similar(scale_lower, self.VALID_SCALES)
        
        error = CEOError(
            error_type=CEOErrorType.INVALID_SCALE,
            message=f"Invalid scale: '{scale}'",
            details={"provided": scale, "valid_scales": self.VALID_SCALES},
            recoverable=True,
            fallback_suggestion=f"Using 'major' as fallback. Did you mean '{similar}'?" if similar else "Using 'major' as fallback."
        )
        return False, error
    
    def validate_string_set(self, string_set: str) -> Tuple[bool, Optional[CEOError]]:
        """Validate a string set."""
        if string_set in self.VALID_STRING_SETS:
            return True, None
        
        error = CEOError(
            error_type=CEOErrorType.STRING_SET_IMPOSSIBLE,
            message=f"Invalid string set: '{string_set}'",
            details={"provided": string_set, "valid": self.VALID_STRING_SETS},
            recoverable=True,
            fallback_suggestion="Using 'auto' as fallback."
        )
        return False, error
    
    def validate_register(
        self,
        pitches: List[int],
        register: Tuple[int, int] = None
    ) -> Tuple[bool, Optional[CEOError]]:
        """Validate that pitches are within register."""
        register = register or self.GUITAR_REGISTER
        
        out_of_range = [p for p in pitches if p < register[0] or p > register[1]]
        
        if not out_of_range:
            return True, None
        
        error = CEOError(
            error_type=CEOErrorType.REGISTER_OUT_OF_RANGE,
            message=f"{len(out_of_range)} pitch(es) out of register",
            details={
                "out_of_range": out_of_range,
                "register_low": register[0],
                "register_high": register[1]
            },
            recoverable=True,
            fallback_suggestion="Pitches will be transposed to fit register."
        )
        return False, error
    
    def validate_melody_input(self, melody: Any) -> Tuple[bool, Optional[CEOError]]:
        """Validate melody input for chord-melody engine."""
        if melody is None:
            error = CEOError(
                error_type=CEOErrorType.MISSING_MELODY,
                message="Melody input is required for chord-melody generation",
                recoverable=False,
                fallback_suggestion="Please provide a melody as MIDI, MusicXML, or pitch list."
            )
            return False, error
        
        return True, None
    
    def validate_voicing_feasibility(
        self,
        pitches: List[int],
        string_set: str = "auto"
    ) -> Tuple[bool, Optional[CEOError]]:
        """Check if a voicing is playable on guitar."""
        # Simplified check - full implementation would use fretboard analysis
        if len(pitches) > 6:
            error = CEOError(
                error_type=CEOErrorType.IMPOSSIBLE_VOICING,
                message="Too many notes for guitar voicing",
                details={"note_count": len(pitches), "max": 6},
                recoverable=True,
                fallback_suggestion="Reducing to 4-note voicing."
            )
            return False, error
        
        # Check range
        if pitches:
            range_span = max(pitches) - min(pitches)
            if range_span > 36:  # More than 3 octaves
                error = CEOError(
                    error_type=CEOErrorType.IMPOSSIBLE_VOICING,
                    message="Voicing range too wide for guitar",
                    details={"range_span": range_span, "max": 36},
                    recoverable=True,
                    fallback_suggestion="Voicing will be compressed."
                )
                return False, error
        
        return True, None
    
    # =========================================================================
    # Diagnostic Methods
    # =========================================================================
    
    def run_diagnostics(self, request: Any) -> List[DiagnosticResult]:
        """
        Run comprehensive diagnostics on a request.
        
        Args:
            request: CEORequest to diagnose
        
        Returns:
            List of DiagnosticResult objects
        """
        results = []
        
        # Check key
        valid, error = self.validate_key(request.key)
        results.append(DiagnosticResult(
            passed=valid,
            check_name="Key Validation",
            message=f"Key '{request.key}' is {'valid' if valid else 'invalid'}",
            severity="info" if valid else "error"
        ))
        if error:
            self.add_error(error)
        
        # Check scale
        valid, error = self.validate_scale(request.scale)
        results.append(DiagnosticResult(
            passed=valid,
            check_name="Scale Validation",
            message=f"Scale '{request.scale}' is {'valid' if valid else 'invalid'}",
            severity="info" if valid else "error"
        ))
        if error:
            self.add_error(error)
        
        # Check string set
        valid, error = self.validate_string_set(request.string_set)
        results.append(DiagnosticResult(
            passed=valid,
            check_name="String Set Validation",
            message=f"String set '{request.string_set}' is {'valid' if valid else 'invalid'}",
            severity="info" if valid else "warning"
        ))
        if error:
            self.add_error(error)
        
        # Check melody for chord-melody
        if hasattr(request, 'engine') and request.engine.value == "chord_melody":
            valid, error = self.validate_melody_input(request.melody)
            results.append(DiagnosticResult(
                passed=valid,
                check_name="Melody Input",
                message="Melody input " + ("provided" if valid else "missing"),
                severity="info" if valid else "error"
            ))
            if error:
                self.add_error(error)
        
        # Check bar count
        bar_valid = 1 <= request.bars <= 64
        results.append(DiagnosticResult(
            passed=bar_valid,
            check_name="Bar Count",
            message=f"Bar count {request.bars} is {'valid' if bar_valid else 'out of range'}",
            severity="info" if bar_valid else "warning"
        ))
        
        return results
    
    # =========================================================================
    # Fallback Methods
    # =========================================================================
    
    def apply_fallbacks(self, request: Any) -> Any:
        """
        Apply fallback values for invalid parameters.
        
        Args:
            request: CEORequest to fix
        
        Returns:
            Fixed request
        """
        # Key fallback
        if request.key not in self.VALID_KEYS:
            self.add_warning(f"Invalid key '{request.key}' replaced with 'C'")
            request.key = "C"
        
        # Scale fallback
        if request.scale.lower() not in self.VALID_SCALES:
            self.add_warning(f"Invalid scale '{request.scale}' replaced with 'major'")
            request.scale = "major"
        
        # String set fallback
        if request.string_set not in self.VALID_STRING_SETS:
            self.add_warning(f"Invalid string set '{request.string_set}' replaced with 'auto'")
            request.string_set = "auto"
        
        # Bar count fallback
        if request.bars < 1:
            request.bars = 1
        elif request.bars > 64:
            request.bars = 64
        
        return request
    
    def get_fallback_for_error(self, error: CEOError) -> Dict[str, Any]:
        """
        Get specific fallback action for an error.
        
        Args:
            error: The error to handle
        
        Returns:
            Dictionary with fallback parameters
        """
        fallbacks = {
            CEOErrorType.INVALID_KEY: {"key": "C"},
            CEOErrorType.INVALID_SCALE: {"scale": "major"},
            CEOErrorType.STRING_SET_IMPOSSIBLE: {"string_set": "auto"},
            CEOErrorType.REGISTER_OUT_OF_RANGE: {"transpose": True},
            CEOErrorType.IMPOSSIBLE_VOICING: {"reduce_voices": True},
        }
        
        return fallbacks.get(error.error_type, {})
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _find_similar(self, value: str, valid_list: List[str]) -> Optional[str]:
        """Find the most similar valid value."""
        value_lower = value.lower()
        
        # Check for prefix match
        for valid in valid_list:
            if valid.startswith(value_lower) or value_lower.startswith(valid):
                return valid
        
        # Check for substring match
        for valid in valid_list:
            if value_lower in valid or valid in value_lower:
                return valid
        
        return None
    
    def handle_exception(self, exception: Exception, context: str = "") -> CEOError:
        """
        Convert an exception to a CEOError.
        
        Args:
            exception: The exception to handle
            context: Context about where the error occurred
        
        Returns:
            CEOError object
        """
        error = CEOError(
            error_type=CEOErrorType.UNKNOWN,
            message=f"Unexpected error in {context}: {str(exception)}",
            details={"exception_type": type(exception).__name__},
            recoverable=False,
            original_exception=exception
        )
        self.add_error(error)
        return error
    
    def format_error_report(self) -> str:
        """Generate a formatted error report."""
        lines = ["=" * 50, "CEO ERROR REPORT", "=" * 50]
        
        if not self.errors and not self.warnings:
            lines.append("No errors or warnings.")
            return "\n".join(lines)
        
        if self.errors:
            lines.append(f"\nERRORS ({len(self.errors)}):")
            lines.append("-" * 30)
            for i, error in enumerate(self.errors, 1):
                lines.append(f"{i}. [{error.error_type.value}] {error.message}")
                if error.fallback_suggestion:
                    lines.append(f"   → {error.fallback_suggestion}")
        
        if self.warnings:
            lines.append(f"\nWARNINGS ({len(self.warnings)}):")
            lines.append("-" * 30)
            for warning in self.warnings:
                lines.append(f"• {warning}")
        
        lines.append("")
        lines.append("=" * 50)
        return "\n".join(lines)

