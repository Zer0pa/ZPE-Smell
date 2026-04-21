from __future__ import annotations

from itertools import combinations
from typing import Sequence

import numpy as np
from scipy.stats import spearmanr

from .codec import (
    BASIS_ID,
    DecodedEpisode,
    EncodedState,
    GroundTruthState,
    SmellEpisode,
    SmellModel,
    build_default_model,
    decode_episode_words,
    encode_episode_words,
    generate_episode_corpus,
    ground_truth_episode_states,
)
from .stream import IMAGE_FAMILY_VALUE, iter_stream, stream_summary


AUTHORITY_SOURCE_COMMIT = "48507cbfcdc5"


def _poincare_distance(a: Sequence[float], b: Sequence[float]) -> float:
    ax = np.asarray(a, dtype=np.float64)
    bx = np.asarray(b, dtype=np.float64)
    na = float(np.sum(ax * ax))
    nb = float(np.sum(bx * bx))
    diff = float(np.sum((ax - bx) ** 2))
    denom = max((1.0 - na) * (1.0 - nb), 1e-8)
    arg = 1.0 + 2.0 * diff / denom
    return float(np.arccosh(max(arg, 1.0 + 1e-8)))


def _ground_truth_zero_state() -> GroundTruthState:
    zeros = (0.0,) * 8
    return GroundTruthState(
        base_point=(0.0, 0.0, 0.0),
        receptor_vector=zeros,
        adaptation_vector=zeros,
        residual_vector=zeros,
    )


def _decoded_zero_state() -> EncodedState:
    zeros = (0.0,) * 8
    return EncodedState(
        base_point=(0.0, 0.0, 0.0),
        fiber_indices=tuple(range(8)),
        fiber_weights=zeros,
        adaptation_values=zeros,
        residual_values=zeros,
        adaptation_signature=zeros,
        checksum=0,
    )


def _trajectory_distance(left: Sequence[object], right: Sequence[object], state_distance, zero_state: object) -> float:
    total = 0.0
    steps = max(len(left), len(right))
    for offset in range(1, steps + 1):
        left_state = left[-offset] if offset <= len(left) else zero_state
        right_state = right[-offset] if offset <= len(right) else zero_state
        total += float(state_distance(left_state, right_state))
    return total / max(steps, 1)


def _ground_truth_state_distance(left: GroundTruthState, right: GroundTruthState) -> float:
    base = _poincare_distance(left.base_point, right.base_point)
    receptor = float(np.sum(np.abs(np.asarray(left.receptor_vector) - np.asarray(right.receptor_vector))))
    adaptation = float(np.sum(np.abs(np.asarray(left.adaptation_vector) - np.asarray(right.adaptation_vector))))
    return base + 0.75 * receptor + 0.50 * adaptation


def _ground_truth_distance(left: Sequence[GroundTruthState], right: Sequence[GroundTruthState]) -> float:
    return _trajectory_distance(left, right, _ground_truth_state_distance, _ground_truth_zero_state())


def _decoded_state_distance(left: EncodedState, right: EncodedState) -> float:
    base = _poincare_distance(left.base_point, right.base_point)
    fiber = float(np.sum(np.abs(np.asarray(left.fiber_weights) - np.asarray(right.fiber_weights))))
    adaptation = float(np.sum(np.abs(np.asarray(left.adaptation_signature) - np.asarray(right.adaptation_signature))))
    return base + 0.75 * fiber + 0.50 * adaptation


def _decoded_distance(left: DecodedEpisode, right: DecodedEpisode) -> float:
    return _trajectory_distance(left.sniffs, right.sniffs, _decoded_state_distance, _decoded_zero_state())


def _receptor_only_distance(left: Sequence[GroundTruthState], right: Sequence[GroundTruthState]) -> float:
    def state_distance(left_state: GroundTruthState, right_state: GroundTruthState) -> float:
        return float(np.sum(np.abs(np.asarray(left_state.receptor_vector) - np.asarray(right_state.receptor_vector))))

    return _trajectory_distance(left, right, state_distance, _ground_truth_zero_state())


def _base_geometry_only_distance(left: Sequence[GroundTruthState], right: Sequence[GroundTruthState]) -> float:
    def state_distance(left_state: GroundTruthState, right_state: GroundTruthState) -> float:
        return _poincare_distance(left_state.base_point, right_state.base_point)

    return _trajectory_distance(left, right, state_distance, _ground_truth_zero_state())


def _nearest_neighbor_indices(matrix: np.ndarray) -> list[int]:
    out = []
    for row_idx in range(matrix.shape[0]):
        row = matrix[row_idx].copy()
        row[row_idx] = np.inf
        out.append(int(np.argmin(row)))
    return out


def _distance_matrix(items: Sequence[object], distance_fn) -> np.ndarray:
    count = len(items)
    matrix = np.zeros((count, count), dtype=np.float64)
    for left_idx in range(count):
        for right_idx in range(left_idx + 1, count):
            distance = float(distance_fn(items[left_idx], items[right_idx]))
            matrix[left_idx, right_idx] = distance
            matrix[right_idx, left_idx] = distance
    return matrix


def _matrix_spearman(reference: np.ndarray, candidate: np.ndarray) -> float:
    upper = np.triu_indices_from(reference, k=1)
    corr, _ = spearmanr(reference[upper], candidate[upper])
    if np.isnan(corr):
        return 0.0
    return float(corr)


def _nn_recall_at1(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref_nn = _nearest_neighbor_indices(reference)
    cand_nn = _nearest_neighbor_indices(candidate)
    matches = sum(int(left == right) for left, right in zip(ref_nn, cand_nn))
    return float(matches) / max(len(ref_nn), 1)


def _mixture_collision_rate(episodes: Sequence[SmellEpisode], reference: np.ndarray, candidate: np.ndarray) -> float:
    collisions = 0
    total = 0
    for left_idx, right_idx in combinations(range(len(episodes)), 2):
        left = episodes[left_idx]
        right = episodes[right_idx]
        if left.label.startswith("single::") or right.label.startswith("single::"):
            continue
        if reference[left_idx, right_idx] < 0.55:
            continue
        total += 1
        if candidate[left_idx, right_idx] < 0.52:
            collisions += 1
    return float(collisions) / max(total, 1)


def _fiber_collision_rate(
    episodes: Sequence[SmellEpisode],
    states: Sequence[Sequence[GroundTruthState]],
    decoded: Sequence[DecodedEpisode],
) -> float:
    collisions = 0
    total = 0
    for left_idx, right_idx in combinations(range(len(episodes)), 2):
        left_gt = states[left_idx][0]
        right_gt = states[right_idx][0]
        base_distance = _poincare_distance(left_gt.base_point, right_gt.base_point)
        fiber_distance = float(np.sum(np.abs(np.asarray(left_gt.receptor_vector) - np.asarray(right_gt.receptor_vector))))
        if base_distance > 0.35 or fiber_distance < 0.30:
            continue
        total += 1
        decoded_distance = _decoded_distance(decoded[left_idx], decoded[right_idx])
        if decoded_distance < 0.50:
            collisions += 1
    return float(collisions) / max(total, 1)


def _adaptation_alias_rate(episodes: Sequence[SmellEpisode], decoded: Sequence[DecodedEpisode]) -> float:
    groups: dict[str, list[int]] = {}
    for index, episode in enumerate(episodes):
        if not episode.label.startswith("adapt::"):
            continue
        root = "::".join(episode.label.split("::")[:2])
        groups.setdefault(root, []).append(index)

    alias_rates = []
    for indices in groups.values():
        if len(indices) < 2:
            continue
        distances = []
        for left_idx, right_idx in combinations(indices, 2):
            distances.append(_decoded_distance(decoded[left_idx], decoded[right_idx]))
        if distances:
            alias_rates.append(float(np.mean([1.0 if dist < 0.38 else 0.0 for dist in distances])))
    return float(np.mean(alias_rates)) if alias_rates else 1.0


def _transport_attack_success(episodes: Sequence[SmellEpisode], encoded_words: Sequence[Sequence[int]]) -> float:
    attack_success = 0
    total = 0
    nuisance_word = (2 << 18) | IMAGE_FAMILY_VALUE
    for episode, words in zip(episodes, encoded_words):
        stream = [nuisance_word, *words]
        summary = stream_summary(stream)
        smells = summary["counts"]["smell"]
        images = summary["counts"]["image"]
        if episode.history_tag == "nuisance":
            total += 1
            if images != 1 or smells != len(words):
                attack_success += 1
    return float(attack_success) / max(total, 1)


def _comparator_metrics(episodes: Sequence[SmellEpisode], reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    return {
        "spearman_distance_correlation": _matrix_spearman(reference, candidate),
        "nn_recall_at1": _nn_recall_at1(reference, candidate),
        "mixture_collision_rate": _mixture_collision_rate(episodes, reference, candidate),
    }


def evaluate_public_surface(model: SmellModel | None = None, source_commit: str = AUTHORITY_SOURCE_COMMIT) -> dict[str, object]:
    if model is None:
        model = build_default_model()

    episodes = generate_episode_corpus(model)
    ground_truth = [ground_truth_episode_states(episode, model) for episode in episodes]
    encoded_words = []
    decoded = []
    for episode in episodes:
        words, _states = encode_episode_words(episode, model)
        encoded_words.append(words)
        decoded.append(decode_episode_words(words))

    reference_matrix = _distance_matrix(ground_truth, _ground_truth_distance)
    decoded_matrix = _distance_matrix(decoded, _decoded_distance)
    receptor_matrix = _distance_matrix(ground_truth, _receptor_only_distance)
    base_geometry_matrix = _distance_matrix(ground_truth, _base_geometry_only_distance)

    spearman = _matrix_spearman(reference_matrix, decoded_matrix)
    nn_at1 = _nn_recall_at1(reference_matrix, decoded_matrix)
    mixture_collision = _mixture_collision_rate(episodes, reference_matrix, decoded_matrix)
    fiber_collision = _fiber_collision_rate(episodes, ground_truth, decoded)
    adaptation_alias = _adaptation_alias_rate(episodes, decoded)
    transport_attack_success = _transport_attack_success(episodes, encoded_words)

    gates = {
        "spearman_min_0p60": spearman >= 0.60,
        "nn_at1_min_0p40": nn_at1 >= 0.40,
        "mixture_collision_max_0p05": mixture_collision <= 0.05,
        "fiber_collision_max_0p05": fiber_collision <= 0.05,
        "adaptation_alias_max_0p20": adaptation_alias <= 0.20,
        "transport_attack_success_eq_0p0": transport_attack_success == 0.0,
    }
    all_gates_pass = all(gates.values())

    nuisance_streams = [
        [list(item) for item in iter_stream([((2 << 18) | IMAGE_FAMILY_VALUE), *words])]
        for episode, words in zip(episodes, encoded_words)
        if episode.history_tag == "nuisance"
    ]

    return {
        "product": "zpe-smell",
        "artifact_version": 1,
        "state_label": "research_in_progress",
        "source_commit": source_commit,
        "scope": {
            "surface": "surrogate receptor-response panel",
            "bounded_result": "bounded_adopter",
            "not_admitted_to_certified_subset": True,
            "episode_count": len(episodes),
            "single_count": sum(1 for episode in episodes if episode.label.startswith("single::")),
            "binary_count": sum(1 for episode in episodes if episode.label.startswith("binary::")),
            "ternary_count": sum(1 for episode in episodes if episode.label.startswith("ternary::")),
            "history_variant_count": sum(1 for episode in episodes if episode.label.startswith("adapt::")),
            "nuisance_case_count": sum(1 for episode in episodes if episode.history_tag == "nuisance"),
            "odorants": sorted(model.odorants),
        },
        "metrics": {
            "spearman_distance_correlation": spearman,
            "nn_recall_at1": nn_at1,
            "mixture_collision_rate": mixture_collision,
            "fiber_collision_rate": fiber_collision,
            "adaptation_alias_rate": adaptation_alias,
            "transport_attack_success_rate": transport_attack_success,
        },
        "comparators": {
            "receptor_only": _comparator_metrics(episodes, reference_matrix, receptor_matrix),
            "base_geometry_only": _comparator_metrics(episodes, reference_matrix, base_geometry_matrix),
        },
        "gates": {
            "basis_id": BASIS_ID,
            "pass_flags": gates,
            "all_pass": all_gates_pass,
        },
        "transport_surface": {
            "nuisance_prefix_case_count": len(nuisance_streams),
            "nuisance_prefix_routing_sample": nuisance_streams[0] if nuisance_streams else [],
        },
        "non_claims": [
            "No digital smell product claim is made.",
            "No claim extends beyond the surrogate receptor-response scope used in this repo.",
            "No claim is made about the full empirical receptor panel.",
            "No claim is made that this result is admitted to the broader certified subset.",
        ],
        "verdict": {
            "status": "bounded_adopter_on_surrogate_scope" if all_gates_pass else "does_not_clear_surrogate_scope",
            "confidence_pct": 100.0 if all_gates_pass else 0.0,
            "statement": (
                "The public smell codec clears the fixed surrogate receptor-response benchmark surface and remains research in progress."
                if all_gates_pass
                else "The public smell codec does not clear the fixed surrogate receptor-response benchmark surface."
            ),
        },
    }
