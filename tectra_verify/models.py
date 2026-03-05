"""Data models for verification results."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class OriginInfo:
    """Origin/category of the signed content."""
    category: str  # camera | ai | creative | medical | document | iot | other
    code: str
    label: str


@dataclass
class SignerInfo:
    """Information about the entity that signed the content."""
    org_name: str
    org_type: str
    public_key: str
    key_name: str
    origin: OriginInfo | None = None
    device_id: str | None = None


@dataclass
class VerificationCheck:
    """Result of an individual verification check."""
    passed: bool
    details: str


@dataclass
class VerifyResult:
    """Full verification result for a piece of content.

    Attributes:
        authentic:      True if confidence >= 40% (at least 2 of 4 checks pass).
        confidence:     Score from 0.0 to 1.0. 1.0 = all checks passed.
        checks:         Dict of individual check results keyed by check name.
        signer:         Information about who signed the content (if found).
        origin:         Origin category of the content (if found).
        timestamp:      When the content was originally signed.
        blockchain_tx:  Polygon transaction hash (if anchored).
        video_summary:  Present for video content.
    """
    authentic: bool
    confidence: float
    checks: dict[str, VerificationCheck] = field(default_factory=dict)
    signer: SignerInfo | None = None
    origin: OriginInfo | None = None
    timestamp: datetime | None = None
    blockchain_tx: str | None = None
    video_summary: dict | None = None

    def __str__(self) -> str:
        status = "✓ AUTHENTIC" if self.authentic else "✗ UNVERIFIED"
        pct = round(self.confidence * 100)
        lines = [f"{status}  (confidence: {pct}%)"]
        if self.signer:
            lines.append(f"Signed by: {self.signer.org_name} ({self.signer.org_type})")
        if self.origin:
            lines.append(f"Origin: {self.origin.label}")
        if self.timestamp:
            lines.append(f"Signed at: {self.timestamp.isoformat()}")
        if self.blockchain_tx:
            lines.append(f"Blockchain: {self.blockchain_tx[:16]}...")
        for name, check in self.checks.items():
            icon = "✓" if check.passed else "○"
            lines.append(f"  {icon} {name.replace('_', ' ')}: {check.details}")
        return "\n".join(lines)
