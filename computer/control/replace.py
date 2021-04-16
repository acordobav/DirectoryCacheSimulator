from enum import Enum


class ReplaceAction(Enum):
    invalid_replace = 0
    share_replaced = 1
    modified_replaced = 2