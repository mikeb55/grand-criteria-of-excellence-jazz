"""
Request Parser for CEO Module
==============================

Parses user requests from:
1. Natural-language task requests (free text)
2. Structured JSON requests
3. Direct engine calls

Extracts parameters and detects required engine(s).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
from enum import Enum
import re
import json


class EngineType(Enum):
    """Available engine types."""
    OPEN_TRIAD = "open_triad"
    ETUDE_GENERATOR = "etude_generator"
    TRIAD_PAIR_SOLO = "triad_pair_solo"
    CHORD_MELODY = "chord_melody"
    MULTI = "multi"  # Multiple engines


class TaskType(Enum):
    """Types of tasks the CEO can handle."""
    GENERATE_SOLO = "generate_solo"
    GENERATE_ETUDE = "generate_etude"
    HARMONISE_MELODY = "harmonise_melody"
    GENERATE_INVERSIONS = "generate_inversions"
    GENERATE_VOICINGS = "generate_voicings"
    COMBINE_OUTPUTS = "combine_outputs"
    ANALYZE = "analyze"


@dataclass
class CEORequest:
    """
    A parsed and validated CEO request.
    
    Attributes:
        engine: Target engine(s)
        task: Task type
        key: Musical key
        scale: Scale type
        progression: Optional chord progression
        melody: Optional melody input
        bars: Number of bars
        mode: Operating mode
        style: Style/harmonisation approach
        string_set: Guitar string set
        difficulty: Difficulty level
        rhythmic_style: Rhythmic feel
        texture: Voicing texture
        contour: Melodic contour
        output_formats: Requested output formats
        additional_params: Any additional parameters
        raw_request: Original request text/data
        engines_sequence: For multi-engine, order of execution
    """
    engine: EngineType = EngineType.OPEN_TRIAD
    task: TaskType = TaskType.GENERATE_VOICINGS
    key: str = "C"
    scale: str = "major"
    progression: Optional[List[str]] = None
    melody: Optional[Any] = None
    bars: int = 4
    mode: str = "modal"
    style: str = "diatonic"
    string_set: str = "auto"
    difficulty: str = "intermediate"
    rhythmic_style: str = "swing"
    texture: str = "medium"
    contour: str = "wave"
    output_formats: List[str] = field(default_factory=lambda: ["json", "musicxml"])
    additional_params: Dict[str, Any] = field(default_factory=dict)
    raw_request: str = ""
    engines_sequence: List[EngineType] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "engine": self.engine.value,
            "task": self.task.value,
            "key": self.key,
            "scale": self.scale,
            "progression": self.progression,
            "melody": str(self.melody) if self.melody else None,
            "bars": self.bars,
            "mode": self.mode,
            "style": self.style,
            "string_set": self.string_set,
            "difficulty": self.difficulty,
            "rhythmic_style": self.rhythmic_style,
            "texture": self.texture,
            "contour": self.contour,
            "output_formats": self.output_formats,
            "additional_params": self.additional_params,
        }


class RequestParser:
    """
    Parses user requests into structured CEORequest objects.
    """
    
    # Engine detection keywords
    ENGINE_KEYWORDS = {
        EngineType.ETUDE_GENERATOR: [
            "etude", "study", "exercise", "practice", "drill",
            "technique", "pattern drill", "scale exercise"
        ],
        EngineType.TRIAD_PAIR_SOLO: [
            "solo", "improvisation", "triad pair", "triad-pair",
            "intervallic", "improvise", "jazz line", "modern jazz"
        ],
        EngineType.CHORD_MELODY: [
            "chord melody", "chord-melody", "harmonise", "harmonize",
            "arrange", "melody with chords", "accompany", "voicings for melody"
        ],
        EngineType.OPEN_TRIAD: [
            "open triad", "inversions", "inversion cycle", "mapping",
            "convert", "transform", "drop2", "drop3", "voice leading"
        ]
    }
    
    # Scale name aliases
    SCALE_ALIASES = {
        "maj": "major", "min": "minor", "dor": "dorian",
        "phryg": "phrygian", "lyd": "lydian", "mixo": "mixolydian",
        "aeo": "aeolian", "loc": "locrian", "mel min": "melodic_minor",
        "harm min": "harmonic_minor", "melodic minor": "melodic_minor",
        "harmonic minor": "harmonic_minor", "whole tone": "whole_tone",
        "wholetone": "whole_tone", "dim": "diminished", "alt": "altered",
        "lyd dom": "lydian_dominant", "lydian dominant": "lydian_dominant"
    }
    
    # Key detection pattern
    KEY_PATTERN = re.compile(
        r'\b([A-G][#b]?)\s*(major|minor|dorian|phrygian|lydian|'
        r'mixolydian|aeolian|locrian|melodic[_\s]?minor|harmonic[_\s]?minor|'
        r'whole[_\s]?tone|diminished|altered|lydian[_\s]?dominant|'
        r'maj|min|dor|phryg|lyd|mixo|aeo|loc)\b',
        re.IGNORECASE
    )
    
    # Bar count pattern
    BAR_PATTERN = re.compile(r'(\d+)[\s-]?bar', re.IGNORECASE)
    
    # Mode detection
    MODE_KEYWORDS = {
        "functional": ["functional", "ii-v-i", "ii v i", "251", "tonal"],
        "modal": ["modal", "static", "vamp", "one chord"],
        "intervallic": ["intervallic", "wide", "leaps", "angular"],
        "chord_melody": ["chord-melody", "chord melody", "harmonised"],
    }
    
    # String set pattern
    STRING_SET_PATTERN = re.compile(r'string[s]?\s*(?:set)?\s*[:\s]?\s*(\d-\d)', re.IGNORECASE)
    
    def __init__(self):
        """Initialize the request parser."""
        self.last_error = None
    
    def parse(self, request: Union[str, Dict]) -> CEORequest:
        """
        Parse a request into a CEORequest object.
        
        Args:
            request: Natural language string, JSON string, or dictionary
        
        Returns:
            CEORequest object
        """
        if isinstance(request, dict):
            return self._parse_dict(request)
        elif isinstance(request, str):
            # Try JSON first
            try:
                data = json.loads(request)
                if isinstance(data, dict):
                    return self._parse_dict(data)
            except json.JSONDecodeError:
                pass
            
            # Natural language parsing
            return self._parse_natural_language(request)
        else:
            raise ValueError(f"Unsupported request type: {type(request)}")
    
    def _parse_dict(self, data: Dict) -> CEORequest:
        """Parse a dictionary request."""
        # Direct engine specification
        engine = data.get("engine", "open_triad")
        if isinstance(engine, str):
            try:
                engine = EngineType(engine)
            except ValueError:
                engine = EngineType.OPEN_TRIAD
        
        # Task type
        task = data.get("task", "generate_voicings")
        if isinstance(task, str):
            try:
                task = TaskType(task)
            except ValueError:
                task = TaskType.GENERATE_VOICINGS
        
        return CEORequest(
            engine=engine,
            task=task,
            key=data.get("key", "C"),
            scale=self._normalize_scale(data.get("scale", "major")),
            progression=data.get("progression"),
            melody=data.get("melody"),
            bars=data.get("bars", 4),
            mode=data.get("mode", "modal"),
            style=data.get("style", "diatonic"),
            string_set=data.get("string_set", "auto"),
            difficulty=data.get("difficulty", "intermediate"),
            rhythmic_style=data.get("rhythmic_style", "swing"),
            texture=data.get("texture", "medium"),
            contour=data.get("contour", "wave"),
            output_formats=data.get("output_formats", ["json", "musicxml"]),
            additional_params=data.get("additional_params", {}),
            raw_request=json.dumps(data),
            engines_sequence=data.get("engines_sequence", [])
        )
    
    def _parse_natural_language(self, text: str) -> CEORequest:
        """Parse a natural language request."""
        text_lower = text.lower()
        
        # Detect engine(s)
        engines = self._detect_engines(text_lower)
        
        # Detect task
        task = self._detect_task(text_lower, engines)
        
        # Extract key and scale
        key, scale = self._extract_key_scale(text)
        
        # Extract bar count
        bars = self._extract_bars(text)
        
        # Extract mode
        mode = self._extract_mode(text_lower)
        
        # Extract string set
        string_set = self._extract_string_set(text)
        
        # Detect multi-engine workflow
        engines_sequence = []
        if len(engines) > 1:
            engines_sequence = engines
            primary_engine = EngineType.MULTI
        elif len(engines) == 1:
            primary_engine = engines[0]
        else:
            primary_engine = EngineType.OPEN_TRIAD
        
        # Detect difficulty
        difficulty = "intermediate"
        if any(word in text_lower for word in ["beginner", "easy", "simple"]):
            difficulty = "beginner"
        elif any(word in text_lower for word in ["advanced", "hard", "complex"]):
            difficulty = "advanced"
        
        # Detect rhythm style
        rhythmic_style = "swing"
        if "straight" in text_lower:
            rhythmic_style = "straight"
        elif "triplet" in text_lower:
            rhythmic_style = "triplet"
        elif "syncopat" in text_lower:
            rhythmic_style = "syncopated"
        
        # Detect style/harmonisation
        style = "diatonic"
        if any(word in text_lower for word in ["reharm", "reharmoni"]):
            style = "reharm"
        elif "ust" in text_lower or "upper structure" in text_lower:
            style = "ust"
        elif "functional" in text_lower:
            style = "functional"
        elif "modal" in text_lower:
            style = "modal"
        
        # Detect output formats
        output_formats = ["json", "musicxml"]
        if "pdf" in text_lower:
            output_formats.append("pdf")
        if "tab" in text_lower:
            output_formats.append("tab")
        
        return CEORequest(
            engine=primary_engine,
            task=task,
            key=key,
            scale=scale,
            bars=bars,
            mode=mode,
            style=style,
            string_set=string_set,
            difficulty=difficulty,
            rhythmic_style=rhythmic_style,
            output_formats=output_formats,
            raw_request=text,
            engines_sequence=engines_sequence
        )
    
    def _detect_engines(self, text: str) -> List[EngineType]:
        """Detect which engine(s) are needed from text."""
        engines = []
        
        for engine_type, keywords in self.ENGINE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    if engine_type not in engines:
                        engines.append(engine_type)
                    break
        
        return engines
    
    def _detect_task(
        self, 
        text: str, 
        engines: List[EngineType]
    ) -> TaskType:
        """Detect the task type from text and detected engines."""
        if EngineType.CHORD_MELODY in engines:
            return TaskType.HARMONISE_MELODY
        elif EngineType.ETUDE_GENERATOR in engines:
            return TaskType.GENERATE_ETUDE
        elif EngineType.TRIAD_PAIR_SOLO in engines:
            return TaskType.GENERATE_SOLO
        elif "inversion" in text:
            return TaskType.GENERATE_INVERSIONS
        elif "combine" in text or "followed by" in text:
            return TaskType.COMBINE_OUTPUTS
        elif "analyze" in text or "analyse" in text:
            return TaskType.ANALYZE
        else:
            return TaskType.GENERATE_VOICINGS
    
    def _extract_key_scale(self, text: str) -> tuple:
        """Extract key and scale from text."""
        match = self.KEY_PATTERN.search(text)
        
        if match:
            key = match.group(1).upper()
            if len(key) > 1:
                key = key[0].upper() + key[1].lower()
            scale = self._normalize_scale(match.group(2))
            return key, scale
        
        # Check for just a key letter
        key_only = re.search(r'\b([A-G][#b]?)\b', text)
        if key_only:
            return key_only.group(1).upper(), "major"
        
        return "C", "major"
    
    def _normalize_scale(self, scale: str) -> str:
        """Normalize scale name to standard format."""
        scale_lower = scale.lower().strip()
        return self.SCALE_ALIASES.get(scale_lower, scale_lower)
    
    def _extract_bars(self, text: str) -> int:
        """Extract bar count from text."""
        match = self.BAR_PATTERN.search(text)
        if match:
            bars = int(match.group(1))
            return max(1, min(64, bars))
        return 4
    
    def _extract_mode(self, text: str) -> str:
        """Extract operating mode from text."""
        for mode, keywords in self.MODE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return mode
        return "modal"
    
    def _extract_string_set(self, text: str) -> str:
        """Extract string set from text."""
        match = self.STRING_SET_PATTERN.search(text)
        if match:
            string_set = match.group(1)
            if string_set in ["6-4", "5-3", "4-2"]:
                return string_set
        return "auto"
    
    def validate_request(self, request: CEORequest) -> tuple:
        """
        Validate a parsed request.
        
        Args:
            request: The CEORequest to validate
        
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Validate key
        valid_keys = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", 
                      "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
        if request.key not in valid_keys:
            issues.append(f"Invalid key: {request.key}")
        
        # Validate scale
        valid_scales = [
            "major", "minor", "dorian", "phrygian", "lydian", "mixolydian",
            "aeolian", "locrian", "melodic_minor", "harmonic_minor",
            "whole_tone", "diminished", "altered", "lydian_dominant"
        ]
        if request.scale not in valid_scales:
            issues.append(f"Invalid scale: {request.scale}")
        
        # Validate string set
        if request.string_set not in ["6-4", "5-3", "4-2", "auto"]:
            issues.append(f"Invalid string set: {request.string_set}")
        
        # Chord-melody requires melody
        if request.engine == EngineType.CHORD_MELODY and request.melody is None:
            issues.append("Chord-melody engine requires melody input")
        
        # Bar count sanity
        if request.bars < 1 or request.bars > 64:
            issues.append(f"Bar count must be 1-64, got {request.bars}")
        
        return len(issues) == 0, issues

