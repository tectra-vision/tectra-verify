"""Pure-Python Merkle tree proof verification.

No external dependencies. The same algorithm used by the Tectra blockchain
anchoring pipeline -- verify locally without any network call.
"""
from __future__ import annotations
import hashlib


def _hash_pair(a: str, b: str) -> str:
    """Hash two hex strings sorted lexicographically to form a parent node."""
    combined = min(a, b) + max(a, b)
    return hashlib.sha256(bytes.fromhex(combined)).hexdigest()


def verify_merkle_proof(
    leaf_hash: str,
    proof: list[dict],
    expected_root: str,
) -> bool:
    """Verify a Merkle inclusion proof.

    Given a content hash (``leaf_hash``), a Merkle proof path (``proof``),
    and the expected Merkle root (``expected_root``), returns ``True`` if the
    proof is valid — i.e., the leaf is genuinely included in the batch that
    was anchored on-chain with that root.

    This is a pure local computation (no network calls).

    Args:
        leaf_hash:     64-char hex SHA-256 of the content.
        proof:         List of ``{"hash": str, "direction": "left"|"right"}``
                       dicts as returned by the Tectra API.
        expected_root: The Merkle root stored on the Polygon blockchain.

    Returns:
        ``True`` if the proof validates against ``expected_root``.

    Example::

        import requests
        from tectra_verify import verify_merkle_proof

        cert = requests.get(
            "https://tectra.vision/api/v1/content-records/RECORD_ID/certificate"
        ).json()

        valid = verify_merkle_proof(
            leaf_hash=cert["sha256_hash"],
            proof=cert["merkle_proof"],
            expected_root=cert["merkle_root"],
        )
        print("Proof valid:", valid)
    """
    current = leaf_hash
    for step in proof:
        sibling = step["hash"]
        if step["direction"] == "left":
            current = _hash_pair(sibling, current)
        else:
            current = _hash_pair(current, sibling)
    return current == expected_root
