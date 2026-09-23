"""A couple of sanity tests for src/scorer.py. Run with: pytest

These stay meaningful across checkpoints: at checkpoint-0 they're expected to
fail (that's the point — the scorer isn't implemented yet), and they should
pass from checkpoint-1/2 onward.
"""
from src.scorer import keypoint_coverage, token_f1


def test_token_f1_identical_text_is_perfect():
    assert token_f1("the cat sat on the mat", "the cat sat on the mat") == 1.0


def test_token_f1_disjoint_text_is_zero():
    assert token_f1("completely unrelated words here", "totally different content indeed") == 0.0


def test_keypoint_coverage_all_present():
    kps = ["defines precision", "defines recall"]
    answer = "This answer defines precision and also defines recall clearly."
    assert keypoint_coverage(kps, answer) == 1.0


def test_keypoint_coverage_partial():
    kps = ["defines precision", "defines recall"]
    answer = "This answer only defines precision."
    assert 0.0 < keypoint_coverage(kps, answer) < 1.0
