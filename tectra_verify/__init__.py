"""
tectra_verify — open-source content provenance verification.

No API key required. Verify any image or video against the Tectra registry
using SHA-256 hashing, perceptual hashing, DWT-DCT watermark extraction,
and Merkle proof verification.

Quick start::

    from tectra_verify import verify

    result = verify("photo.jpg")
    print(result.authentic, result.confidence)
    print(result.signer)
"""

from .verifier import verify, verify_bytes
from .hashing import compute_sha256, compute_perceptual_hash, phash_similarity
from .watermark import extract_watermark
from .merkle import verify_merkle_proof
from .models import VerifyResult, VerificationCheck, SignerInfo, OriginInfo

__all__ = [
    "verify",
    "verify_bytes",
    "compute_sha256",
    "compute_perceptual_hash",
    "phash_similarity",
    "extract_watermark",
    "verify_merkle_proof",
    "VerifyResult",
    "VerificationCheck",
    "SignerInfo",
    "OriginInfo",
]

__version__ = "0.1.0"
