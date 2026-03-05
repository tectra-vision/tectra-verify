"""Main verification entry point — calls the Tectra public API."""
from __future__ import annotations
import io
from datetime import datetime, timezone
from pathlib import Path

import requests

from .hashing import compute_sha256, compute_perceptual_hash, hamming_distance, PHASH_MATCH_THRESHOLD
from .watermark import extract_watermark_hex
from .merkle import verify_merkle_proof
from .models import VerifyResult, VerificationCheck, SignerInfo, OriginInfo

TECTRA_API = "https://tectra.vision"
_VERIFY_ENDPOINT = f"{TECTRA_API}/api/v1/verify"
_VERIFY_HASH_ENDPOINT = f"{TECTRA_API}/api/v1/verify/by-hash"


def verify(
    path: str | Path,
    *,
    api_url: str = TECTRA_API,
    timeout: int = 30,
) -> VerifyResult:
    """Verify a file's provenance against the Tectra registry.

    Uses a two-tier approach:

    1. **SHA-256 hash check** (no upload) — instant for exact matches.
    2. **Full content upload** — for images that may have been modified
       (re-encoded, cropped, screenshotted). Runs watermark extraction
       and perceptual hash matching server-side.

    Videos are always verified via hash only — the file never leaves
    your machine.

    Args:
        path:    Path to the image or video file.
        api_url: Tectra API base URL (default: https://tectra.vision).
        timeout: HTTP request timeout in seconds.

    Returns:
        :class:`VerifyResult` with ``authentic``, ``confidence``, and
        individual check details.

    Example::

        from tectra_verify import verify

        result = verify("photo.jpg")
        if result.authentic:
            print(f"Authentic! Signed by {result.signer.org_name}")
        else:
            print("Not verified")

    Raises:
        FileNotFoundError: If *path* does not exist.
        requests.HTTPError: If the API returns an error response.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    data = file_path.read_bytes()
    return verify_bytes(data, filename=file_path.name, api_url=api_url, timeout=timeout)


def verify_bytes(
    data: bytes,
    *,
    filename: str = "file",
    content_type: str | None = None,
    api_url: str = TECTRA_API,
    timeout: int = 30,
) -> VerifyResult:
    """Verify raw bytes against the Tectra registry.

    Same two-tier logic as :func:`verify` but accepts bytes directly.
    Useful when the file is already in memory (e.g., from a web request).

    Args:
        data:         Raw file bytes.
        filename:     Original filename (used for content-type detection).
        content_type: MIME type override. If omitted, inferred from filename.
        api_url:      Tectra API base URL.
        timeout:      HTTP request timeout in seconds.

    Returns:
        :class:`VerifyResult`.
    """
    ct = content_type or _guess_content_type(filename)
    is_video = ct.startswith("video/")

    # Tier 1: hash-only (no upload)
    sha256 = compute_sha256(data)
    hash_result = _verify_by_hash(sha256, ct, api_url=api_url, timeout=timeout)

    if hash_result.authentic or is_video:
        return hash_result

    # Tier 2: full upload (image only — watermark + pHash)
    return _verify_upload(data, filename, ct, api_url=api_url, timeout=timeout)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _verify_by_hash(
    sha256: str,
    content_type: str,
    *,
    api_url: str,
    timeout: int,
) -> VerifyResult:
    endpoint = f"{api_url}/api/v1/verify/by-hash"
    resp = requests.post(
        endpoint,
        json={"sha256_hash": sha256, "content_type": content_type},
        timeout=timeout,
    )
    resp.raise_for_status()
    return _parse_result(resp.json())


def _verify_upload(
    data: bytes,
    filename: str,
    content_type: str,
    *,
    api_url: str,
    timeout: int,
) -> VerifyResult:
    endpoint = f"{api_url}/api/v1/verify"
    resp = requests.post(
        endpoint,
        files={"file": (filename, io.BytesIO(data), content_type)},
        timeout=timeout,
    )
    resp.raise_for_status()
    return _parse_result(resp.json())


def _parse_result(data: dict) -> VerifyResult:
    checks: dict[str, VerificationCheck] = {}
    for name, check in (data.get("checks") or {}).items():
        checks[name] = VerificationCheck(
            passed=check["passed"],
            details=check["details"],
        )

    signer = None
    if data.get("signer"):
        s = data["signer"]
        origin = None
        if s.get("origin"):
            o = s["origin"]
            origin = OriginInfo(category=o["category"], code=o["code"], label=o["label"])
        signer = SignerInfo(
            org_name=s["org_name"],
            org_type=s["org_type"],
            public_key=s.get("public_key", ""),
            key_name=s.get("key_name", ""),
            origin=origin,
            device_id=s.get("device_id"),
        )

    origin = None
    if data.get("origin"):
        o = data["origin"]
        origin = OriginInfo(category=o["category"], code=o["code"], label=o["label"])

    timestamp = None
    if data.get("timestamp"):
        try:
            timestamp = datetime.fromisoformat(data["timestamp"])
        except (ValueError, TypeError):
            pass

    return VerifyResult(
        authentic=data.get("authentic", False),
        confidence=data.get("confidence", 0.0),
        checks=checks,
        signer=signer,
        origin=origin,
        timestamp=timestamp,
        blockchain_tx=data.get("blockchain_tx"),
        video_summary=data.get("video_summary"),
    )


def _guess_content_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mov": "video/quicktime",
    }.get(ext, "application/octet-stream")
