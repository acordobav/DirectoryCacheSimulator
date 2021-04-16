from enum import Enum


class CacheAlert(Enum):
    rdHit = 1
    rdMiss = 2
    wrHit = 3
    wrMiss = 4

