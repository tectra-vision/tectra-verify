"""Tests for tectra_verify."""
import hashlib
import pytest
from unittest.mock import patch, MagicMock
from tectra_verify.hashing import compute_sha256, compute_perceptual_hash, hamming_distance, phash_similarity
from tectra_verify.merkle import verify_merkle_proof
from tectra_verify.models import VerifyResult, VerificationCheck


# ── Hashing ──────────────────────────────────────────────────────────────────

def test_compute_sha256():
    assert compute_sha256(b"hello") == hashlib.sha256(b"hello").hexdigest()
    assert len(compute_sha256(b"x")) == 64


def test_hamming_distance_identical():
    assert hamming_distance("a1b2c3d4e5f60708", "a1b2c3d4e5f60708") == 0


def test_hamming_distance_opposite():
    assert hamming_distance("0000000000000000", "ffffffffffffffff") == 64


def test_phash_similarity_identical():
    assert phash_similarity("abcdef1234567890", "abcdef1234567890") == 1.0


def test_phash_similarity_opposite():
    assert phash_similarity("0000000000000000", "ffffffffffffffff") == 0.0


# ── Merkle proof ──────────────────────────────────────────────────────────────

def _h(a, b):
    combined = min(a, b) + max(a, b)
    return hashlib.sha256(bytes.fromhex(combined)).hexdigest()


def test_verify_merkle_proof_single_leaf():
    leaf = hashlib.sha256(b"content").hexdigest()
    assert verify_merkle_proof(leaf, [], leaf) is True


def test_verify_merkle_proof_two_leaves():
    leaf_a = hashlib.sha256(b"a").hexdigest()
    leaf_b = hashlib.sha256(b"b").hexdigest()
    root = _h(leaf_a, leaf_b)
    proof_a = [{"hash": leaf_b, "direction": "right"}]
    assert verify_merkle_proof(leaf_a, proof_a, root) is True


def test_verify_merkle_proof_invalid():
    leaf = hashlib.sha256(b"content").hexdigest()
    wrong_root = hashlib.sha256(b"wrong").hexdigest()
    assert verify_merkle_proof(leaf, [], wrong_root) is False


def test_verify_merkle_proof_tampered():
    leaf_a = hashlib.sha256(b"a").hexdigest()
    leaf_b = hashlib.sha256(b"b").hexdigest()
    leaf_c = hashlib.sha256(b"c").hexdigest()
    root = _h(leaf_a, leaf_b)
    # tampered: provide leaf_c as if it were leaf_a
    proof = [{"hash": leaf_b, "direction": "right"}]
    assert verify_merkle_proof(leaf_c, proof, root) is False


# ── VerifyResult model ────────────────────────────────────────────────────────

def test_verify_result_str_authentic():
    result = VerifyResult(
        authentic=True,
        confidence=1.0,
        checks={"hash_exact": VerificationCheck(passed=True, details="Match found")},
    )
    s = str(result)
    assert "AUTHENTIC" in s
    assert "100%" in s


def test_verify_result_str_unverified():
    result = VerifyResult(authentic=False, confidence=0.0)
    assert "UNVERIFIED" in str(result)
