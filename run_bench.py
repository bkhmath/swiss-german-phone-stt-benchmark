"""Transcribe a test set with one Whisper checkpoint under one channel condition.

    python run_bench.py --model openai/whisper-large-v3-turbo --dataset asgdts --condition phone

Writes results/<dataset>/<model>__<condition>.jsonl (one line per utterance) and a
.meta.json with throughput numbers.
"""
import argparse
import json
import time
from pathlib import Path

import torch
from transformers import pipeline

from sgbench.data import LOADERS, SR
from sgbench.telephone import phone_line

CONDITIONS = {
    "wide": lambda x, i: x,
    "phone": lambda x, i: phone_line(x),
    "phone_loss3": lambda x, i: phone_line(x, packet_loss=0.03, seed=i),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dataset", choices=LOADERS, required=True)
    ap.add_argument("--condition", choices=CONDITIONS, default="wide")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--max-seconds", type=float)
    ap.add_argument("--batch-size", type=int, default=16)
    args = ap.parse_args()

    out_dir = Path("results") / args.dataset
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{args.model.replace('/', '__')}__{args.condition}"
    out_path = out_dir / f"{stem}.jsonl"

    kw = {"max_seconds": args.max_seconds} if args.dataset == "spcr" else {}
    items, total = [], [0]

    def stream():
        # audio is decoded and degraded on the fly, so only a few batches sit in RAM
        for i, it in enumerate(LOADERS[args.dataset](limit=args.limit, **kw)):
            a = CONDITIONS[args.condition](it.pop("audio"), i)
            items.append(it)
            total[0] += len(a) / SR
            yield {"raw": a, "sampling_rate": SR}

    asr = pipeline(
        "automatic-speech-recognition", model=args.model,
        dtype=torch.float16, device="cuda:0",
        model_kwargs={"attn_implementation": "sdpa"},
    )
    gen = {"language": "de", "task": "transcribe", "num_beams": 1}
    asr([next(iter(LOADERS[args.dataset](**kw)))["audio"]], generate_kwargs=gen)  # warm-up

    torch.cuda.synchronize()
    t0 = time.perf_counter()
    hyps = [o["text"].strip() for o in asr(
        stream(), batch_size=args.batch_size, chunk_length_s=30, generate_kwargs=gen)]
    torch.cuda.synchronize()
    wall = time.perf_counter() - t0
    total_audio_s = total[0]

    with out_path.open("w", encoding="utf-8") as f:
        for it, h in zip(items, hyps):
            f.write(json.dumps({**it, "hyp": h}, ensure_ascii=False) + "\n")
    meta = {"model": args.model, "dataset": args.dataset, "condition": args.condition,
            "n": len(items), "audio_hours": total_audio_s / 3600, "wall_s": wall,
            "batch_rtf": wall / total_audio_s, "gpu": torch.cuda.get_device_name(0)}
    (out_dir / f"{stem}.meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
