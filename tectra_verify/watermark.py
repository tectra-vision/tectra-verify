"""DWT-DCT invisible watermark extraction."""
from __future__ import annotations
import io
import numpy as np
from PIL import Image
from imwatermark import WatermarkDecoder

WATERMARK_METHOD = "dwtDct"
WATERMARK_LENGTH_BYTES = 32


def extract_watermark(image_bytes: bytes) -> bytes:
    """Extract the 32-byte DWT-DCT invisible watermark payload from an image.

    Returns raw bytes. The first 16 bytes (32 hex chars) are the meaningful
    Tectra payload; the remaining bytes are zero-padding.

    Returns bytes of all zeros if no watermark is present, or if the image
    is too small / has insufficient frequency content for extraction.

    .. note::
        DWT-DCT watermarks survive JPEG compression, moderate re-encoding,
        and slight cropping. They do **not** survive screenshots or heavy
        pixel manipulation.

    Example::

        payload = extract_watermark(open("signed.png", "rb").read())
        payload_hex = payload.hex()[:32]  # meaningful 16 bytes
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_array = np.array(img)
    decoder = WatermarkDecoder("bytes", WATERMARK_LENGTH_BYTES * 8)
    raw = decoder.decode(img_array, WATERMARK_METHOD)
    return bytes(raw)


def extract_watermark_hex(image_bytes: bytes) -> str:
    """Extract watermark and return the meaningful 32-char hex payload.

    Returns a 32-character lowercase hex string.
    All zeros means no watermark was detected.
    """
    payload = extract_watermark(image_bytes)
    return payload.hex()[:32]
