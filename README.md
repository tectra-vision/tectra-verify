# tectra-verify

Open-source Python library for verifying content provenance using the [Tectra](https://tectra.vision) registry.

**No API key required.** Verify any image or video against the Tectra blockchain registry using SHA-256 hashing, perceptual hashing, DWT-DCT watermark extraction, and Merkle proof verification.

A [C2PA Contributor Member](https://c2pa.org) open-source implementation.

---

## Install

```bash
pip install tectra-verify
```

## Quick start

```python
from tectra_verify import verify

result = verify("photo.jpg")

if result.authentic:
    print(f"✓ Authentic — signed by {result.signer.org_name}")
    print(f"  Origin: {result.origin.label}")
    print(f"  Blockchain: {result.blockchain_tx}")
else:
    print(f"✗ Unverified (confidence: {result.confidence:.0%})")

# Inspect individual checks
for name, check in result.checks.items():
    icon = "✓" if check.passed else "○"
    print(f"  {icon} {name}: {check.details}")
```

Output:
```
✓ Authentic — signed by OpenAI
  Origin: AI Generated Image
  Blockchain: 0xfeffb501...

  ✓ hash_exact: Exact SHA-256 match found
  ✓ blockchain: Merkle proof verified — batch anchored on-chain
```

## CLI

```bash
# Verify a single file
tectra-verify photo.jpg

# Verify multiple files
tectra-verify frame1.jpg frame2.jpg video.mp4

# JSON output
tectra-verify --json photo.jpg
```

## Verification tiers

| Tier | Method | Upload? | Works for |
|------|--------|---------|-----------|
| 1 | SHA-256 hash | No | Exact original file |
| 2 | Upload + watermark + pHash | Yes (images only) | Modified copies, screenshots |

Videos are always verified via hash only — **no video data ever leaves your machine**.

## Low-level API

```python
from tectra_verify import (
    compute_sha256,
    compute_perceptual_hash,
    phash_similarity,
    extract_watermark,
    verify_merkle_proof,
)

# Compute hashes
sha256 = compute_sha256(open("photo.jpg", "rb").read())
phash = compute_perceptual_hash(open("photo.jpg", "rb").read())

# Compare perceptual hashes (1.0 = identical)
sim = phash_similarity("a1b2c3d4e5f60708", "a1b2c3d4e5f60709")

# Extract invisible watermark (DWT-DCT)
payload = extract_watermark(open("signed.png", "rb").read())
payload_hex = payload.hex()[:32]  # meaningful 16-byte payload

# Verify a Merkle proof locally (no network)
valid = verify_merkle_proof(
    leaf_hash=sha256,
    proof=[{"hash": "abc...", "direction": "right"}, ...],
    expected_root="def...",
)
```

## How it works

Tectra uses a four-layer provenance system:

1. **SHA-256** — exact fingerprint of the file bytes
2. **Perceptual hash (pHash)** — visual fingerprint that survives re-encoding, compression, and moderate cropping
3. **DWT-DCT watermark** — invisible payload embedded in the image's frequency domain, survives JPEG compression
4. **Blockchain anchor** — Merkle batch of SHA-256 hashes registered on Polygon, verified locally without any trusted third party

Unlike [C2PA](https://c2pa.org) (which embeds credentials *inside* the file), Tectra's blockchain record survives metadata stripping — common when images are uploaded to social platforms. The pHash matching also detects modified copies that would fail an exact hash check.

## Requirements

- Python 3.9+
- PIL / Pillow
- imagehash
- invisible-watermark
- requests
- numpy

## License

MIT — see [LICENSE](LICENSE).

## Links

- [Tectra](https://tectra.vision)
- [Documentation](https://tectra.vision/docs)
- [PyPI](https://pypi.org/project/tectra-verify/)
- [C2PA](https://c2pa.org) — Tectra is a Contributor Member
