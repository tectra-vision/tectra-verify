"""SHA-256 and perceptual hashing utilities."""
from __future__ import annotations
import hashlib
import io
from PIL import Image
import imagehash


def compute_sha256(data: bytes) -> str:
    """Return the lowercase hex SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def compute_perceptual_hash(image_bytes: bytes) -> str:
    """Compute a 64-bit DCT-based perceptual hash.

    Returns a 16-character lowercase hex string. Two images with a Hamming
    distance of ≤ 10 bits are considered visually identical by Tectra's
    matching algorithm.

    Works on any PIL-supported image format (PNG, JPEG, WebP, etc.).
    """
    img = Image.open(io.BytesIO(image_bytes))
    ph = imagehash.phash(img, hash_size=8)
    return str(ph)


def hamming_distance(hash_a: str, hash_b: str) -> int:
    """Bit-level Hamming distance between two 16-char hex pHash strings.

    Returns an integer in [0, 64]. Lower = more similar.
    """
    if len(hash_a) != len(hash_b):
        raise ValueError(f"Hash length mismatch: {len(hash_a)} vs {len(hash_b)}")
    return bin(int(hash_a, 16) ^ int(hash_b, 16)).count("1")


def phash_similarity(hash_a: str, hash_b: str) -> float:
    """Return a similarity score in [0.0, 1.0].

    1.0 = identical, 0.0 = completely different.
    """
    dist = hamming_distance(hash_a, hash_b)
    return 1.0 - (dist / 64.0)


PHASH_MATCH_THRESHOLD = 10
