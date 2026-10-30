"""Simulate a narrowband phone line (what a voice agent actually hears on PSTN/SIP).

Chain: 16 kHz wideband -> 300-3400 Hz telephone band -> 8 kHz -> G.711 mu-law (8 bit)
-> optional packet loss -> back to 16 kHz for the ASR model.
"""
import warnings

import numpy as np
from scipy.signal import butter, resample_poly, sosfilt

with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    try:
        import audioop  # exact ITU-T G.711 tables; removed in Python 3.13
    except ImportError:  # pragma: no cover
        audioop = None

SR = 16_000
PHONE_SR = 8_000
_SOS = butter(4, [300, 3400], btype="bandpass", fs=SR, output="sos")


def _mulaw_roundtrip(x: np.ndarray) -> np.ndarray:
    pcm = (np.clip(x, -1.0, 1.0) * 32767).astype("<i2").tobytes()
    if audioop is not None:
        pcm = audioop.ulaw2lin(audioop.lin2ulaw(pcm, 2), 2)
        return np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32767
    # continuous mu-law approximation (mu = 255, 8 bit)
    mu = 255.0
    y = np.sign(x) * np.log1p(mu * np.abs(x)) / np.log1p(mu)
    y = np.round((y + 1) / 2 * 255) / 255 * 2 - 1
    return (np.sign(y) * np.expm1(np.abs(y) * np.log1p(mu)) / mu).astype(np.float32)


def phone_line(x: np.ndarray, packet_loss: float = 0.0, seed: int = 0) -> np.ndarray:
    """Degrade a 16 kHz float waveform as a G.711 call would. Returns 16 kHz float32."""
    x = x.astype(np.float32)
    peak = np.abs(x).max()
    if peak > 0:
        x = x / peak * 0.5  # typical call level, avoids clipping in the codec
    x = sosfilt(_SOS, x)
    x = resample_poly(x, 1, 2)  # 16k -> 8k
    x = _mulaw_roundtrip(x)
    if packet_loss > 0:
        # drop 20 ms RTP frames, no concealment (worst case)
        rng = np.random.default_rng(seed)
        frame = PHONE_SR // 50
        n = len(x) // frame
        lost = rng.random(n) < packet_loss
        x = x.copy()
        for i in np.flatnonzero(lost):
            x[i * frame:(i + 1) * frame] = 0
    return resample_poly(x, 2, 1).astype(np.float32)
