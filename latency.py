"""Per-utterance latency at batch size 1, as in a live call: the caller stops talking,
the full utterance is sent to the model, we wait for the text.

    python latency.py --model openai/whisper-large-v3-turbo --n 200
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

from sgbench.data import SR, load_asgdts
from sgbench.telephone import phone_line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=200)
    args = ap.parse_args()

    proc = AutoProcessor.from_pretrained(args.model)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        args.model, torch_dtype=torch.float16, attn_implementation="sdpa").to("cuda").eval()
    clips = [phone_line(it["audio"]) for it in load_asgdts(limit=args.n, seed=1)]

    def run(x):
        feats = proc(x, sampling_rate=SR, return_tensors="pt").input_features.to("cuda", torch.float16)
        with torch.inference_mode():
            model.generate(feats, language="de", task="transcribe", num_beams=1)
        torch.cuda.synchronize()

    for x in clips[:5]:
        run(x)  # warm-up
    lat = []
    for x in clips:
        t0 = time.perf_counter()
        run(x)
        lat.append(time.perf_counter() - t0)
    lat = np.array(lat) * 1000
    dur = np.array([len(x) / SR for x in clips])
    res = {"model": args.model, "n": len(clips), "mean_clip_s": float(dur.mean()),
           "p50_ms": float(np.percentile(lat, 50)), "p90_ms": float(np.percentile(lat, 90)),
           "p99_ms": float(np.percentile(lat, 99)), "rtf": float((lat / 1000).sum() / dur.sum()),
           "gpu": torch.cuda.get_device_name(0)}
    out = Path("results") / "latency"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.model.replace('/', '__')}.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res))


if __name__ == "__main__":
    main()
