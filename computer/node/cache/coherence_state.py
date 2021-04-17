from enum import Enum


class CoherenceState(Enum):
    modified = "M"
    shared = "S"
    invalid = "I"
