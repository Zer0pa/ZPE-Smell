from __future__ import annotations

from enum import IntEnum
from typing import Iterable


WORD_MASK = (1 << 20) - 1
SMELL_TYPE_BIT = 0x0200
IMAGE_FAMILY_VALUE = 0x0400
PREAMBLE_A = SMELL_TYPE_BIT | 0x9000
PREAMBLE_B = SMELL_TYPE_BIT | 0xA000


class Mode(IntEnum):
    EXTENSION = 2


def iter_stream(words: Iterable[int]) -> list[tuple[str, int]]:
    routed: list[tuple[str, int]] = []
    remaining_smell_words = 0
    awaiting_length_word = False

    for raw_word in words:
        word = int(raw_word)
        payload = word & 0xFFFF
        mode = (word >> 18) & 0x3

        if remaining_smell_words > 0:
            routed.append(("smell", word))
            remaining_smell_words -= 1
            continue

        if awaiting_length_word:
            if mode == Mode.EXTENSION.value and (payload & 0xFF00) == PREAMBLE_B:
                total_words = payload & 0xFF
                remaining_smell_words = max(total_words - 2, 0)
                routed.append(("smell", word))
            else:
                routed.append(("unknown", word))
            awaiting_length_word = False
            continue

        if mode == Mode.EXTENSION.value and payload == IMAGE_FAMILY_VALUE:
            routed.append(("image", word))
            continue

        if mode == Mode.EXTENSION.value and (payload & 0xFF00) == PREAMBLE_A:
            routed.append(("smell", word))
            awaiting_length_word = True
            continue

        routed.append(("unknown", word))

    return routed


def stream_summary(words: Iterable[int]) -> dict[str, dict[str, int]]:
    counts = {"smell": 0, "image": 0, "unknown": 0}
    for modality, _word in iter_stream(words):
        counts[modality] += 1
    return {"counts": counts}
