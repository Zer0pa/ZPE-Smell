from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

import numpy as np

from .stream import Mode, PREAMBLE_A, PREAMBLE_B, WORD_MASK


RECEPTOR_COUNT = 8
RESIDUAL_SCALE = 0.12
DATA_BASE = 0xB000
DATA_PANEL = 0xC000
DATA_RESIDUAL = 0xD000
DATA_ADAPT = 0xE000
CHECKSUM_WORD = 0xF000
FAMILY_ID = 1
SCHEMA_ID = 2
BASIS_ID = 2
RESPONSE_BITS = 6
ADAPTATION_BITS = 5
RESIDUAL_BITS = 7


@dataclass(frozen=True)
class OdorantSpec:
    name: str
    latent: tuple[float, float, float]
    receptor_pref: tuple[float, ...]
    efficacy: tuple[float, ...]
    quality: tuple[float, float, float, float, float]
    pleasant_bias: float
    category: str


@dataclass(frozen=True)
class Component:
    odorant: str
    concentration: float


@dataclass(frozen=True)
class SmellSniff:
    components: tuple[Component, ...]
    nuisance_marker: bool = False


@dataclass(frozen=True)
class SmellEpisode:
    label: str
    sniffs: tuple[SmellSniff, ...]
    history_tag: str


@dataclass(frozen=True)
class GroundTruthState:
    base_point: tuple[float, float, float]
    receptor_vector: tuple[float, ...]
    adaptation_vector: tuple[float, ...]
    residual_vector: tuple[float, ...]


@dataclass(frozen=True)
class EncodedState:
    base_point: tuple[float, float, float]
    fiber_indices: tuple[int, ...]
    fiber_weights: tuple[float, ...]
    adaptation_values: tuple[float, ...]
    residual_values: tuple[float, ...]
    adaptation_signature: tuple[float, ...]
    checksum: int


@dataclass(frozen=True)
class DecodedEpisode:
    sniffs: tuple[EncodedState, ...]
    metadata: dict[str, int]


@dataclass(frozen=True)
class SmellModel:
    odorants: dict[str, OdorantSpec]
    receptor_affinity: np.ndarray
    receptor_efficacy: np.ndarray
    projector: np.ndarray
    residual_pairs: dict[tuple[str, str], np.ndarray]


def _ball_clip(vector: np.ndarray, max_norm: float = 0.97) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm <= max_norm or norm == 0.0:
        return vector
    return vector * (max_norm / norm)


def _quantize_signed_unit(value: float, bits: int) -> int:
    levels = (1 << bits) - 1
    clipped = max(-1.0, min(1.0, float(value)))
    scaled = int(round(((clipped + 1.0) * 0.5) * levels))
    return max(0, min(levels, scaled))


def _dequantize_signed_unit(value: int, bits: int) -> float:
    levels = (1 << bits) - 1
    clipped = max(0, min(levels, int(value)))
    return (float(clipped) / float(levels)) * 2.0 - 1.0


def _quantize_unit(value: float, bits: int) -> int:
    levels = (1 << bits) - 1
    clipped = max(0.0, min(1.0, float(value)))
    scaled = int(round(clipped * levels))
    return max(0, min(levels, scaled))


def _dequantize_unit(value: int, bits: int) -> float:
    levels = (1 << bits) - 1
    clipped = max(0, min(levels, int(value)))
    return float(clipped) / float(levels)


def _ext_word(version: int, payload: int) -> int:
    word = (Mode.EXTENSION.value << 18) | ((int(version) & 0x3) << 16) | (int(payload) & 0xFFFF)
    if word < 0 or word > WORD_MASK:
        raise ValueError(f"out-of-range smell word: {word}")
    return word


def _make_odorants() -> dict[str, OdorantSpec]:
    specs = [
        OdorantSpec(
            name="citrus",
            latent=(0.56, 0.18, 0.02),
            receptor_pref=(0.92, 0.88, 0.16, 0.06, 0.02, 0.05, 0.04, 0.12),
            efficacy=(0.90, 0.82, 0.22, 0.08, 0.03, 0.04, 0.02, 0.10),
            quality=(0.35, 0.92, 0.06, 0.08, 0.03),
            pleasant_bias=0.80,
            category="FRUITY",
        ),
        OdorantSpec(
            name="banana",
            latent=(0.46, 0.26, 0.06),
            receptor_pref=(0.86, 0.78, 0.10, 0.05, 0.02, 0.03, 0.06, 0.08),
            efficacy=(0.88, 0.80, 0.14, 0.05, 0.01, 0.02, 0.05, 0.06),
            quality=(0.28, 0.88, 0.04, 0.04, 0.02),
            pleasant_bias=0.78,
            category="FRUITY",
        ),
        OdorantSpec(
            name="rose",
            latent=(0.44, 0.08, 0.22),
            receptor_pref=(0.90, 0.40, 0.26, 0.10, 0.04, 0.03, 0.08, 0.10),
            efficacy=(0.84, 0.35, 0.24, 0.06, 0.02, 0.01, 0.10, 0.08),
            quality=(0.92, 0.32, 0.12, 0.05, 0.01),
            pleasant_bias=0.88,
            category="FLORAL",
        ),
        OdorantSpec(
            name="mint",
            latent=(0.22, 0.52, 0.18),
            receptor_pref=(0.32, 0.58, 0.86, 0.08, 0.02, 0.08, 0.02, 0.12),
            efficacy=(0.24, 0.52, 0.90, 0.06, 0.01, 0.10, 0.01, 0.14),
            quality=(0.20, 0.40, 0.74, 0.06, 0.02),
            pleasant_bias=0.58,
            category="MINTY_CAMPHOR",
        ),
        OdorantSpec(
            name="cedar",
            latent=(-0.20, 0.04, 0.42),
            receptor_pref=(0.06, 0.10, 0.14, 0.90, 0.06, 0.04, 0.16, 0.28),
            efficacy=(0.04, 0.08, 0.10, 0.86, 0.04, 0.03, 0.12, 0.32),
            quality=(0.04, 0.06, 0.18, 0.86, 0.04),
            pleasant_bias=0.32,
            category="WOODY_EARTHY",
        ),
        OdorantSpec(
            name="coffee",
            latent=(-0.08, -0.10, 0.38),
            receptor_pref=(0.12, 0.10, 0.24, 0.76, 0.10, 0.12, 0.14, 0.44),
            efficacy=(0.10, 0.08, 0.20, 0.72, 0.08, 0.10, 0.12, 0.46),
            quality=(0.04, 0.05, 0.18, 0.72, 0.10),
            pleasant_bias=0.18,
            category="WOODY_EARTHY",
        ),
        OdorantSpec(
            name="musk",
            latent=(0.08, -0.12, 0.46),
            receptor_pref=(0.08, 0.04, 0.14, 0.42, 0.12, 0.06, 0.88, 0.18),
            efficacy=(0.06, 0.04, 0.10, 0.36, 0.10, 0.05, 0.92, 0.16),
            quality=(0.10, 0.04, 0.10, 0.30, 0.08),
            pleasant_bias=0.10,
            category="MUSKY_ANIMAL",
        ),
        OdorantSpec(
            name="solvent",
            latent=(-0.44, 0.30, -0.16),
            receptor_pref=(0.02, 0.06, 0.10, 0.04, 0.22, 0.92, 0.04, 0.16),
            efficacy=(0.01, 0.04, 0.08, 0.03, 0.24, 0.88, 0.02, 0.14),
            quality=(0.02, 0.04, 0.10, 0.08, 0.86),
            pleasant_bias=-0.72,
            category="CHEMICAL_SOLVENT",
        ),
        OdorantSpec(
            name="sulfur",
            latent=(-0.54, -0.30, -0.08),
            receptor_pref=(0.02, 0.02, 0.08, 0.06, 0.94, 0.24, 0.10, 0.22),
            efficacy=(0.01, 0.01, 0.06, 0.04, 0.96, 0.18, 0.08, 0.20),
            quality=(0.01, 0.02, 0.06, 0.08, 0.94),
            pleasant_bias=-0.92,
            category="PUTRID_DECAY",
        ),
        OdorantSpec(
            name="smoke",
            latent=(-0.28, -0.16, 0.28),
            receptor_pref=(0.04, 0.04, 0.16, 0.46, 0.26, 0.18, 0.08, 0.84),
            efficacy=(0.02, 0.02, 0.12, 0.42, 0.22, 0.12, 0.06, 0.90),
            quality=(0.02, 0.02, 0.10, 0.38, 0.30),
            pleasant_bias=-0.28,
            category="SPICY_HERBAL",
        ),
        OdorantSpec(
            name="lavender",
            latent=(0.34, 0.16, 0.30),
            receptor_pref=(0.84, 0.40, 0.26, 0.10, 0.02, 0.02, 0.06, 0.08),
            efficacy=(0.80, 0.36, 0.22, 0.08, 0.01, 0.02, 0.04, 0.06),
            quality=(0.84, 0.24, 0.22, 0.06, 0.02),
            pleasant_bias=0.72,
            category="FLORAL",
        ),
        OdorantSpec(
            name="green_leaf",
            latent=(0.12, 0.36, 0.26),
            receptor_pref=(0.24, 0.42, 0.54, 0.16, 0.04, 0.04, 0.04, 0.12),
            efficacy=(0.18, 0.36, 0.58, 0.12, 0.02, 0.02, 0.03, 0.10),
            quality=(0.14, 0.30, 0.62, 0.12, 0.04),
            pleasant_bias=0.44,
            category="SPICY_HERBAL",
        ),
    ]
    return {spec.name: spec for spec in specs}


def _receptor_matrix(odorants: Sequence[OdorantSpec], field: str) -> np.ndarray:
    rows = [getattr(spec, field) for spec in odorants]
    return np.asarray(rows, dtype=np.float64)


def _fit_projector(odorants: Sequence[OdorantSpec]) -> np.ndarray:
    responses = np.stack([np.asarray(spec.receptor_pref, dtype=np.float64) for spec in odorants], axis=0)
    latents = np.stack([np.asarray(spec.latent, dtype=np.float64) for spec in odorants], axis=0)
    return np.linalg.pinv(responses) @ latents


def build_default_model() -> SmellModel:
    odorants = _make_odorants()
    ordered = list(odorants.values())
    residual_pairs = {
        ("banana", "rose"): np.array([0.08, 0.02, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]),
        ("citrus", "solvent"): np.array([0.00, 0.00, 0.00, 0.00, -0.03, -0.08, 0.00, 0.00]),
        ("cedar", "smoke"): np.array([0.00, 0.00, 0.00, 0.08, 0.02, 0.00, 0.00, 0.06]),
        ("musk", "sulfur"): np.array([0.00, 0.00, 0.00, 0.00, -0.10, 0.00, -0.04, 0.00]),
        ("green_leaf", "mint"): np.array([0.00, 0.03, 0.06, 0.00, 0.00, 0.00, 0.00, 0.00]),
    }
    return SmellModel(
        odorants=odorants,
        receptor_affinity=_receptor_matrix(ordered, "receptor_pref"),
        receptor_efficacy=_receptor_matrix(ordered, "efficacy"),
        projector=_fit_projector(ordered),
        residual_pairs=residual_pairs,
    )


def _pair_key(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))


def _component_arrays(sniff: SmellSniff, model: SmellModel) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    concentrations = []
    affinities = []
    efficacies = []
    for component in sniff.components:
        spec = model.odorants[component.odorant]
        concentrations.append(float(component.concentration))
        affinities.append(np.asarray(spec.receptor_pref, dtype=np.float64))
        efficacies.append(np.asarray(spec.efficacy, dtype=np.float64))
    return (
        np.asarray(concentrations, dtype=np.float64),
        np.stack(affinities, axis=0),
        np.stack(efficacies, axis=0),
    )


def _ground_truth_base(sniff: SmellSniff, model: SmellModel) -> np.ndarray:
    weighted = np.zeros(3, dtype=np.float64)
    total = sum(component.concentration for component in sniff.components)
    if total <= 0:
        return weighted

    for component in sniff.components:
        spec = model.odorants[component.odorant]
        weighted += (component.concentration / total) * np.asarray(spec.latent, dtype=np.float64)

    interaction_shift = np.zeros(3, dtype=np.float64)
    for left, right in combinations(sniff.components, 2):
        key = _pair_key(left.odorant, right.odorant)
        if key == ("banana", "rose"):
            interaction_shift += np.array([0.04, 0.02, 0.00])
        elif key == ("cedar", "smoke"):
            interaction_shift += np.array([-0.02, -0.01, 0.05])
        elif key == ("citrus", "solvent"):
            interaction_shift += np.array([-0.05, 0.00, -0.03])
        elif key == ("musk", "sulfur"):
            interaction_shift += np.array([-0.03, -0.02, -0.02])
    return _ball_clip(weighted + interaction_shift)


def _competitive_binding(sniff: SmellSniff, prev_adaptation: np.ndarray, model: SmellModel) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    concentrations, affinities, efficacies = _component_arrays(sniff, model)
    numerator = np.sum((efficacies * concentrations[:, None]) / np.maximum(affinities, 1e-3), axis=0)
    denominator = 1.0 + np.sum(concentrations[:, None] / np.maximum(affinities, 1e-3), axis=0)
    binding = numerator / denominator

    residual = np.zeros(RECEPTOR_COUNT, dtype=np.float64)
    total_concentration = float(np.sum(concentrations))
    for left, right in combinations(sniff.components, 2):
        key = _pair_key(left.odorant, right.odorant)
        if key not in model.residual_pairs:
            continue
        strength = (left.concentration * right.concentration) / max(total_concentration, 1e-6)
        residual += strength * model.residual_pairs[key]
    residual = np.clip(residual, -RESIDUAL_SCALE, RESIDUAL_SCALE)

    next_adaptation = 0.58 * prev_adaptation + 0.42 * binding
    effective = np.maximum(0.0, binding - 0.55 * prev_adaptation) + residual
    effective = np.maximum(effective, 1e-6)
    return effective, next_adaptation, residual


def ground_truth_episode_states(episode: SmellEpisode, model: SmellModel) -> tuple[GroundTruthState, ...]:
    states = []
    adaptation = np.zeros(RECEPTOR_COUNT, dtype=np.float64)
    for sniff in episode.sniffs:
        effective, adaptation, residual = _competitive_binding(sniff, adaptation, model)
        normalized = effective / np.sum(effective)
        base = _ground_truth_base(sniff, model)
        states.append(
            GroundTruthState(
                base_point=tuple(float(v) for v in base),
                receptor_vector=tuple(float(v) for v in normalized),
                adaptation_vector=tuple(float(v) for v in adaptation),
                residual_vector=tuple(float(v) for v in residual),
            )
        )
    return tuple(states)


def _panel_state_from_sniff(
    sniff: SmellSniff,
    receptor_vector: Sequence[float],
    adaptation: Sequence[float],
    residual: Sequence[float],
    model: SmellModel,
) -> EncodedState:
    base = tuple(float(value) for value in _ground_truth_base(sniff, model))
    return EncodedState(
        base_point=base,
        fiber_indices=tuple(range(RECEPTOR_COUNT)),
        fiber_weights=tuple(float(value) for value in receptor_vector),
        adaptation_values=tuple(float(value) for value in adaptation),
        residual_values=tuple(float(value) for value in residual),
        adaptation_signature=tuple(float(value) for value in adaptation),
        checksum=0,
    )


def _checksum_for_payloads(payloads: Sequence[int]) -> int:
    total = 0
    for payload in payloads:
        total += int(payload) & 0x3FF
        total += (int(payload) >> 10) & 0x3F
    return int(total % 64)


def encode_episode_words(episode: SmellEpisode, model: SmellModel) -> tuple[list[int], tuple[EncodedState, ...]]:
    adaptation = np.zeros(RECEPTOR_COUNT, dtype=np.float64)
    states: list[EncodedState] = []
    words: list[int] = []

    for sniff in episode.sniffs:
        effective, adaptation, residual = _competitive_binding(sniff, adaptation, model)
        normalized = effective / np.sum(effective)
        states.append(_panel_state_from_sniff(sniff, normalized, adaptation, residual, model))

    words_per_sniff = 3 + RECEPTOR_COUNT + RECEPTOR_COUNT + RECEPTOR_COUNT + 1
    total_words = 2 + len(states) * words_per_sniff
    words.append(_ext_word(1, PREAMBLE_A | ((FAMILY_ID & 0xF) << 4) | (len(states) & 0xF)))
    words.append(_ext_word(2, PREAMBLE_B | (total_words & 0xFF)))

    for state in states:
        sniff_payloads: list[int] = []

        for axis, value in enumerate(state.base_point):
            payload = DATA_BASE | ((axis & 0x3) << 10) | (_quantize_signed_unit(value, 10) & 0x3FF)
            sniff_payloads.append(payload)
            words.append(_ext_word(3, payload))

        for receptor_idx, weight in enumerate(state.fiber_weights):
            payload = DATA_PANEL | ((receptor_idx & 0xF) << RESPONSE_BITS) | (_quantize_unit(weight, RESPONSE_BITS) & ((1 << RESPONSE_BITS) - 1))
            sniff_payloads.append(payload)
            words.append(_ext_word(3, payload))

        for receptor_idx, value in enumerate(state.adaptation_signature):
            payload = DATA_ADAPT | ((receptor_idx & 0xF) << ADAPTATION_BITS) | (_quantize_unit(value, ADAPTATION_BITS) & ((1 << ADAPTATION_BITS) - 1))
            sniff_payloads.append(payload)
            words.append(_ext_word(3, payload))

        for receptor_idx, value in enumerate(state.residual_values):
            payload = DATA_RESIDUAL | ((receptor_idx & 0xF) << RESIDUAL_BITS) | (
                _quantize_signed_unit(value / max(RESIDUAL_SCALE, 1e-8), RESIDUAL_BITS) & ((1 << RESIDUAL_BITS) - 1)
            )
            sniff_payloads.append(payload)
            words.append(_ext_word(3, payload))

        checksum = _checksum_for_payloads(sniff_payloads)
        words.append(_ext_word(3, CHECKSUM_WORD | (checksum & 0x3F)))

    return words, tuple(states)


def decode_episode_words(words: Sequence[int]) -> DecodedEpisode:
    if len(words) < 2:
        raise ValueError("smell bundle requires at least two preamble words")

    first = int(words[0])
    second = int(words[1])
    mode0 = (first >> 18) & 0x3
    mode1 = (second >> 18) & 0x3
    version0 = (first >> 16) & 0x3
    version1 = (second >> 16) & 0x3
    payload0 = first & 0xFFFF
    payload1 = second & 0xFFFF

    if mode0 != Mode.EXTENSION.value or version0 != 1 or (payload0 & 0xFF00) != PREAMBLE_A:
        raise ValueError("missing smell bundle preamble A")
    if mode1 != Mode.EXTENSION.value or version1 != 2 or (payload1 & 0xFF00) != PREAMBLE_B:
        raise ValueError("missing smell bundle preamble B")

    sniff_count = payload0 & 0xF
    total_words = payload1 & 0xFF
    if total_words != len(words):
        raise ValueError("smell bundle length mismatch")

    cursor = 2
    states: list[EncodedState] = []

    for _ in range(sniff_count):
        coords: list[float] = []
        sniff_payloads: list[int] = []

        for axis in range(3):
            payload = int(words[cursor]) & 0xFFFF
            if (payload & 0xF000) != DATA_BASE:
                raise ValueError("missing base coordinate word")
            encoded_axis = (payload >> 10) & 0x3
            if encoded_axis != axis:
                raise ValueError("base coordinate axis mismatch")
            sniff_payloads.append(payload)
            coords.append(_dequantize_signed_unit(payload & 0x3FF, 10))
            cursor += 1

        indices: list[int] = []
        weights: list[float] = []
        for receptor_idx in range(RECEPTOR_COUNT):
            payload = int(words[cursor]) & 0xFFFF
            if (payload & 0xF000) != DATA_PANEL:
                raise ValueError("missing receptor panel word")
            sniff_payloads.append(payload)
            encoded_idx = (payload >> RESPONSE_BITS) & 0xF
            if encoded_idx != receptor_idx:
                raise ValueError("receptor panel index mismatch")
            indices.append(encoded_idx)
            weights.append(_dequantize_unit(payload & ((1 << RESPONSE_BITS) - 1), RESPONSE_BITS))
            cursor += 1

        adaptations: list[float] = []
        for receptor_idx in range(RECEPTOR_COUNT):
            payload = int(words[cursor]) & 0xFFFF
            if (payload & 0xF000) != DATA_ADAPT:
                raise ValueError("missing adaptation word")
            sniff_payloads.append(payload)
            encoded_idx = (payload >> ADAPTATION_BITS) & 0xF
            if encoded_idx != receptor_idx:
                raise ValueError("adaptation index mismatch")
            adaptations.append(_dequantize_unit(payload & ((1 << ADAPTATION_BITS) - 1), ADAPTATION_BITS))
            cursor += 1

        residuals: list[float] = []
        for receptor_idx in range(RECEPTOR_COUNT):
            payload = int(words[cursor]) & 0xFFFF
            if (payload & 0xF000) != DATA_RESIDUAL:
                raise ValueError("missing residual word")
            sniff_payloads.append(payload)
            encoded_idx = (payload >> RESIDUAL_BITS) & 0xF
            if encoded_idx != receptor_idx:
                raise ValueError("residual index mismatch")
            residual_unit = _dequantize_signed_unit(payload & ((1 << RESIDUAL_BITS) - 1), RESIDUAL_BITS)
            residuals.append(residual_unit * RESIDUAL_SCALE)
            cursor += 1

        checksum_payload = int(words[cursor]) & 0xFFFF
        if (checksum_payload & 0xF000) != CHECKSUM_WORD:
            raise ValueError("missing checksum word")
        checksum = checksum_payload & 0x3F
        expected = _checksum_for_payloads(sniff_payloads)
        if checksum != expected:
            raise ValueError("smell bundle checksum mismatch")
        cursor += 1

        states.append(
            EncodedState(
                base_point=tuple(coords),
                fiber_indices=tuple(indices),
                fiber_weights=tuple(weights),
                adaptation_values=tuple(adaptations),
                residual_values=tuple(residuals),
                adaptation_signature=tuple(adaptations),
                checksum=checksum,
            )
        )

    metadata = {
        "family_id": FAMILY_ID,
        "schema_id": SCHEMA_ID,
        "basis_id": BASIS_ID,
        "sniff_count": sniff_count,
        "total_words": total_words,
    }
    return DecodedEpisode(sniffs=tuple(states), metadata=metadata)


def generate_episode_corpus(model: SmellModel) -> list[SmellEpisode]:
    del model

    episodes: list[SmellEpisode] = []
    singles = ["citrus", "rose", "mint", "cedar", "solvent", "sulfur", "coffee", "musk"]
    for name in singles:
        episodes.append(
            SmellEpisode(
                label=f"single::{name}",
                sniffs=(SmellSniff((Component(name, 1.0),)),),
                history_tag="clean",
            )
        )

    binary_specs = [
        ("banana", "rose", 0.55, 0.45),
        ("citrus", "solvent", 0.62, 0.38),
        ("cedar", "smoke", 0.50, 0.50),
        ("musk", "sulfur", 0.52, 0.48),
        ("green_leaf", "mint", 0.60, 0.40),
        ("coffee", "cedar", 0.58, 0.42),
        ("citrus", "mint", 0.50, 0.50),
        ("rose", "lavender", 0.48, 0.52),
    ]
    for left, right, a, b in binary_specs:
        episodes.append(
            SmellEpisode(
                label=f"binary::{left}+{right}",
                sniffs=(SmellSniff((Component(left, a), Component(right, b))),),
                history_tag="clean",
            )
        )

    ternaries = [
        ("citrus", "rose", "green_leaf"),
        ("cedar", "coffee", "smoke"),
        ("banana", "lavender", "mint"),
        ("solvent", "sulfur", "smoke"),
        ("citrus", "mint", "solvent"),
        ("musk", "coffee", "cedar"),
    ]
    for first, second, third in ternaries:
        episodes.append(
            SmellEpisode(
                label=f"ternary::{first}+{second}+{third}",
                sniffs=(
                    SmellSniff(
                        (
                            Component(first, 0.40),
                            Component(second, 0.35),
                            Component(third, 0.25),
                        )
                    ),
                ),
                history_tag="clean",
            )
        )

    history_targets = [
        ("adapt::citrus+solvent::clean", (SmellSniff((Component("citrus", 0.64), Component("solvent", 0.36))),), "clean"),
        (
            "adapt::citrus+solvent::precursor",
            (SmellSniff((Component("solvent", 0.90),)), SmellSniff((Component("citrus", 0.64), Component("solvent", 0.36)))),
            "solvent_precursor",
        ),
        ("adapt::musk+sulfur::clean", (SmellSniff((Component("musk", 0.55), Component("sulfur", 0.45))),), "clean"),
        (
            "adapt::musk+sulfur::precursor",
            (SmellSniff((Component("musk", 0.88),)), SmellSniff((Component("musk", 0.55), Component("sulfur", 0.45)))),
            "musk_precursor",
        ),
        ("adapt::banana+rose::clean", (SmellSniff((Component("banana", 0.52), Component("rose", 0.48))),), "clean"),
        (
            "adapt::banana+rose::precursor",
            (SmellSniff((Component("rose", 0.86),)), SmellSniff((Component("banana", 0.52), Component("rose", 0.48)))),
            "rose_precursor",
        ),
    ]
    for label, sniffs, tag in history_targets:
        episodes.append(SmellEpisode(label=label, sniffs=sniffs, history_tag=tag))

    nuisance_targets = [
        ("nuisance::cedar+smoke", (SmellSniff((Component("cedar", 0.52), Component("smoke", 0.48)), nuisance_marker=True),)),
        ("nuisance::citrus+mint", (SmellSniff((Component("citrus", 0.58), Component("mint", 0.42)), nuisance_marker=True),)),
        ("nuisance::musk+sulfur", (SmellSniff((Component("musk", 0.55), Component("sulfur", 0.45)), nuisance_marker=True),)),
        ("nuisance::rose+lavender", (SmellSniff((Component("rose", 0.48), Component("lavender", 0.52)), nuisance_marker=True),)),
        (
            "nuisance::citrus+rose+green_leaf",
            (
                SmellSniff(
                    (
                        Component("citrus", 0.40),
                        Component("rose", 0.35),
                        Component("green_leaf", 0.25),
                    ),
                    nuisance_marker=True,
                ),
            ),
        ),
        (
            "nuisance::cedar+coffee+smoke",
            (
                SmellSniff(
                    (
                        Component("cedar", 0.40),
                        Component("coffee", 0.35),
                        Component("smoke", 0.25),
                    ),
                    nuisance_marker=True,
                ),
            ),
        ),
        (
            "nuisance::musk+coffee+cedar",
            (
                SmellSniff(
                    (
                        Component("musk", 0.40),
                        Component("coffee", 0.35),
                        Component("cedar", 0.25),
                    ),
                    nuisance_marker=True,
                ),
            ),
        ),
    ]
    for label, sniffs in nuisance_targets:
        episodes.append(SmellEpisode(label=label, sniffs=sniffs, history_tag="nuisance"))

    return episodes
