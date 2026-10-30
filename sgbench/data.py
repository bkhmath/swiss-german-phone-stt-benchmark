"""Loaders for the two public Swiss German test sets used here.

asgdts: FHNW/i4ds All Swiss German Dialects Test Set (MIT). 5750 short read clips,
        178 speakers, canton-of-origin label per speaker.
spcr:   i4ds/spc_r test split (CC BY 4.0). 679 long-form segments of spontaneous
        debate in the Grosser Rat Bern; dense in amounts, votes, dates, article numbers.
Both pair Swiss German audio with a Standard German reference.
"""
import io
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
from scipy.signal import resample_poly

DATA = Path(__file__).resolve().parent.parent / "data"
SR = 16_000


def _to_16k(x, sr):
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != SR:
        g = np.gcd(sr, SR)
        x = resample_poly(x, SR // g, sr // g)
    return x.astype(np.float32)


def load_asgdts(limit=None, seed=0):
    root = DATA / "asgdts"
    df = pd.read_csv(root / "Clickworker_Test_Set" / "all.tsv", sep="\t", quoting=3)
    if limit:
        df = df.sample(n=limit, random_state=seed)
    for row in df.itertuples():
        x, sr = sf.read(root / "clips" / row.path, dtype="float32")
        yield {"id": row.path, "ref": row.sentence, "group": row.accent,
               "speaker": str(row.client_id), "audio": _to_16k(x, sr)}


def load_spcr(limit=None, max_seconds=None, seed=0):
    df = pd.read_parquet(DATA / "spc_r_test.parquet", columns=["audio", "text"])
    df = df.reset_index().rename(columns={"index": "id"})
    if limit:
        df = df.sample(n=limit, random_state=seed)
    for row in df.itertuples():
        buf = io.BytesIO(row.audio["bytes"])
        if max_seconds and sf.info(buf).duration > max_seconds:
            continue  # skip before decoding: the longest segments are ~50 min
        buf.seek(0)
        x, sr = sf.read(buf, dtype="float32")
        x = _to_16k(x, sr)
        yield {"id": f"spcr_{row.id}", "ref": row.text, "group": "BE-parliament",
               "speaker": "", "audio": x}


LOADERS = {"asgdts": load_asgdts, "spcr": load_spcr}
