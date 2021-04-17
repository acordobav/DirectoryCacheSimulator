from enum import Enum


class DirectoryState(Enum):
    exclusive = "DM"
    shared = "DS"
    uncached = "DI"
