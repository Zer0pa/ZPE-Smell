from __future__ import annotations

import json
from pathlib import Path

from zpe_smell import build_default_model, decode_episode_words, encode_episode_words, evaluate_public_surface, generate_episode_corpus
from zpe_smell.evaluation import AUTHORITY_SOURCE_COMMIT
from zpe_smell.stream import IMAGE_FAMILY_VALUE, iter_stream


ROOT = Path(__file__).resolve().parents[1]
PROOF_ARTIFACT = ROOT / "proofs" / "artifacts" / "public_smell_surrogate_scope.json"
REFERENCE_RESULT = ROOT / "validation" / "results" / "reference_public_eval.json"


def _nuisance_episode():
    model = build_default_model()
    episodes = {episode.label: episode for episode in generate_episode_corpus(model)}
    return episodes["nuisance::citrus+rose+green_leaf"]


def test_roundtrip_keeps_full_receptor_panel() -> None:
    model = build_default_model()
    words, _states = encode_episode_words(_nuisance_episode(), model)
    decoded = decode_episode_words(words)
    assert decoded.metadata["sniff_count"] == 1
    assert decoded.metadata["basis_id"] == 2
    assert len(decoded.sniffs[0].fiber_indices) == 8


def test_image_prefix_does_not_break_smell_routing() -> None:
    model = build_default_model()
    words, _states = encode_episode_words(_nuisance_episode(), model)
    routed = iter_stream([((2 << 18) | IMAGE_FAMILY_VALUE), *words])
    modalities = [modality for modality, _word in routed]
    assert modalities.count("image") == 1
    assert modalities.count("smell") == len(words)


def test_public_eval_matches_bounded_scope() -> None:
    result = evaluate_public_surface(source_commit=AUTHORITY_SOURCE_COMMIT)
    assert result["scope"]["surface"] == "surrogate receptor-response panel"
    assert result["scope"]["not_admitted_to_certified_subset"] is True
    assert result["verdict"]["status"] == "bounded_adopter_on_surrogate_scope"
    assert result["gates"]["all_pass"] is True


def test_public_eval_beats_public_comparators() -> None:
    result = evaluate_public_surface(source_commit=AUTHORITY_SOURCE_COMMIT)
    metrics = result["metrics"]
    receptor = result["comparators"]["receptor_only"]
    base = result["comparators"]["base_geometry_only"]
    assert metrics["spearman_distance_correlation"] > receptor["spearman_distance_correlation"]
    assert metrics["spearman_distance_correlation"] > base["spearman_distance_correlation"]
    assert metrics["nn_recall_at1"] > receptor["nn_recall_at1"]
    assert metrics["nn_recall_at1"] > base["nn_recall_at1"]


def test_committed_artifacts_match_live_eval() -> None:
    live = evaluate_public_surface(source_commit=AUTHORITY_SOURCE_COMMIT)
    proof = json.loads(PROOF_ARTIFACT.read_text(encoding="utf-8"))
    reference = json.loads(REFERENCE_RESULT.read_text(encoding="utf-8"))
    assert live == proof == reference
