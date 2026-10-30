"""Aggregate results/ into results/summary.md and figures/*.png."""
import json
import re
from collections import Counter
from pathlib import Path

import jiwer
import matplotlib
import numpy as np
import pandas as pd

from sgbench.metrics import bleu, bootstrap, number_counts, wer_counts
from sgbench.numbers_de import numbers, tokens

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RES, FIG = Path("results"), Path("figures")
SHORT = {
    "openai__whisper-small": "whisper-small",
    "openai__whisper-large-v3-turbo": "large-v3-turbo",
    "openai__whisper-large-v3": "large-v3",
    "gcoli__whisper-large-v3-turbo-swiss-german-mit": "turbo-SG (MIT)",
    "Flix-AI__flix-swissgerman-full": "large-v3-SG (Flix)",
}
COND = {"wide": "wideband 16 kHz", "phone": "G.711 phone", "phone_loss3": "G.711 + 3% loss"}


_FR = re.compile(r"\b(le|la|les|des|nous|est|et|pour|une|que|qui|dans|pas|vous|je)\b")
_DE = re.compile(r"\b(der|die|das|und|ist|nicht|wir|sie|ich|mit|von|auch)\b")


def french_share(text):
    fr, de = len(_FR.findall(text.lower())), len(_DE.findall(text.lower()))
    return fr / max(fr + de, 1)


def load(ds):
    """Bern's parliament is bilingual: SPC_R segments with French references are dropped
    from the Swiss German scores (counted separately)."""
    runs = {}
    for p in sorted((RES / ds).glob("*.jsonl")):
        model, cond = p.stem.rsplit("__", 1)
        df = pd.read_json(p, lines=True)
        if ds == "spcr":
            df = df[df.ref.apply(french_share) <= 0.1].reset_index(drop=True)
        runs[(SHORT.get(model, model), cond)] = df
    # paired bootstraps index all runs with the same positions
    ids = [tuple(df.id) for df in runs.values()]
    assert all(i == ids[0] for i in ids), f"{ds}: runs are not aligned on the same utterances"
    return runs


_NUMWORD = re.compile(r"tausend|hundert|zig|zehn|sieb|seb|sib")


SKIPPED = "lost in a skipped passage (≥ 5 words)"


def number_error_types(df):
    """Total over segments of per_segment_number_errors."""
    return sum(per_segment_number_errors(df), Counter())


def per_segment_number_errors(df):
    """Align ref/hyp after normalisation and label every reference number that is not
    reproduced exactly. One Counter per segment."""
    rows = []
    for r in df.itertuples():
        out = Counter()
        rows.append(out)
        R, H = tokens(r.ref), tokens(r.hyp) or ["<empty>"]
        for a in jiwer.process_words(" ".join(R), " ".join(H)).alignments[0]:
            span = [t for t in R[a.ref_start_idx:a.ref_end_idx] if t.isdigit()]
            hyp = H[a.hyp_start_idx:a.hyp_end_idx] if a.type != "delete" else []
            for t in span:
                out["total"] += 1
                if a.type == "equal":
                    continue
                v = int(t)
                hd = [int(h) for h in hyp if h.isdigit()]
                if a.type == "delete" and a.ref_end_idx - a.ref_start_idx >= 5:
                    out[SKIPPED] += 1
                elif a.type == "delete":
                    out["dropped locally"] += 1
                elif any(_NUMWORD.search(h) for h in hyp if not h.isdigit()):
                    out["malformed number words (e.g. 'dreitausendsebhundert')"] += 1
                elif 1900 <= v <= 2100 and v % 100 in hd:
                    out["year shortened (2025 -> 25)"] += 1
                elif 1900 <= v <= 2100 and any(1900 <= h <= 2100 for h in hd):
                    out["wrong year (2021 -> 2020)"] += 1
                elif v >= 1000 and len(hd) >= 2:
                    out["split into digit groups (14800 -> 14 ...)"] += 1
                elif hd:
                    out["other wrong value"] += 1
                else:
                    out["replaced by non-number words"] += 1
    return rows


def number_specific_rate(rows):
    """Number error rate ignoring numbers lost in skipped passages (a long-form decoding
    problem, not a number problem). Returns (errors, total) arrays per segment."""
    err = np.array([sum(v for k, v in c.items() if k not in ("total", SKIPPED)) for c in rows])
    tot = np.array([c["total"] - c[SKIPPED] for c in rows])
    return err, tot


def fmt(p, lo, hi, pct=True):
    k = 100 if pct else 1
    return f"{p * k:.1f} [{lo * k:.1f}, {hi * k:.1f}]"


def score(df, clusters):
    e, n = wer_counts(df.ref, df.hyp)
    m, nr, nh = number_counts(df.ref, df.hyp)
    N = len(df)
    return {
        "e": e, "n": n, "m": m, "nr": nr, "nh": nh,
        "wer": bootstrap(lambda i: e[i].sum() / n[i].sum(), N, clusters),
        "num_recall": bootstrap(lambda i: m[i].sum() / max(nr[i].sum(), 1), N, clusters),
        "num_prec": m.sum() / max(nh.sum(), 1),
        "bleu": bleu(df.ref, df.hyp),
    }


def number_misses(df, k=12):
    rows = []
    for r in df.itertuples():
        missed = Counter(numbers(r.ref)) - Counter(numbers(r.hyp))
        if missed and len(r.ref) < 200:
            rows.append((r.group, r.ref, r.hyp, sorted(missed.elements())))
    return rows[:k]


def main():
    FIG.mkdir(exist_ok=True)
    md = ["# Results\n"]
    lat = {SHORT.get(p.stem, p.stem): json.loads(p.read_text())
           for p in (RES / "latency").glob("*.json")}

    for ds in ["asgdts", "spcr"]:
        runs = load(ds)
        if not runs:
            continue
        any_df = next(iter(runs.values()))
        clusters = any_df.speaker.values if ds == "asgdts" else None
        scores = {k: score(df, clusters) for k, df in runs.items()}
        models = [m for m in SHORT.values() if any(k[0] == m for k in scores)]

        md += [f"\n## {ds}  (n = {len(any_df)})\n",
               "| model | condition | WER % ↓ [95% CI] | BLEU ↑ | number recall % ↑ [95% CI] | number precision % ↑ |",
               "|---|---|---|---|---|---|"]
        for (mdl, cond), s in sorted(scores.items(), key=lambda kv: (models.index(kv[0][0]), kv[0][1] != "wide")):
            md.append(f"| {mdl} | {COND[cond]} | {fmt(*s['wer'])} | {s['bleu']:.1f} | "
                      f"{fmt(*s['num_recall'])} | {s['num_prec'] * 100:.1f} |")

        # paired, speaker-clustered CI for the phone penalty
        md += ["\n**Phone-line penalty (phone - wideband, paired bootstrap):**\n",
               "| model | Δ WER pts [95% CI] | Δ number recall pts [95% CI] |", "|---|---|---|"]
        for mdl in models:
            if (mdl, "wide") in scores and (mdl, "phone") in scores:
                a, b = scores[(mdl, "wide")], scores[(mdl, "phone")]
                dw = bootstrap(lambda i: b["e"][i].sum() / b["n"][i].sum() - a["e"][i].sum() / a["n"][i].sum(),
                               len(any_df), clusters)
                dn = bootstrap(lambda i: b["m"][i].sum() / max(b["nr"][i].sum(), 1)
                               - a["m"][i].sum() / max(a["nr"][i].sum(), 1), len(any_df), clusters)
                md.append(f"| {mdl} | {fmt(*dw)} | {fmt(*dn)} |")

        # figure: WER per model and condition
        fig, ax = plt.subplots(figsize=(8, 4))
        conds = [c for c in COND if any(k[1] == c for k in scores)]
        w = 0.8 / len(conds)
        for j, c in enumerate(conds):
            xs, ys, err = [], [], []
            for i, mdl in enumerate(models):
                if (mdl, c) in scores:
                    p, lo, hi = scores[(mdl, c)]["wer"]
                    xs.append(i + j * w), ys.append(p * 100), err.append([(p - lo) * 100, (hi - p) * 100])
            ax.bar(xs, ys, w, yerr=np.array(err).T, capsize=3, label=COND[c])
        ax.set_xticks(np.arange(len(models)) + w * (len(conds) - 1) / 2, models, rotation=15)
        ax.set_ylabel("WER % (lower is better)")
        title = {"asgdts": "All Swiss German Dialects test set", "spcr": "SPC_R (Bern parliament)"}[ds]
        ax.set_title(f"{title}: WER with 95% bootstrap CI")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG / f"{ds}_wer.png", dpi=150)
        plt.close(fig)

        if ds == "asgdts":
            # per-dialect WER on the phone line
            groups = any_df.group.values
            cantons = [g for g, c in pd.Series(groups).value_counts().items() if c >= 100]
            md += ["\n**WER % by dialect region, G.711 phone line** (cantons with ≥ 100 clips):\n",
                   "| model | " + " | ".join(cantons) + " |", "|---|" + "---|" * len(cantons)]
            heat = []
            for mdl in models:
                if (mdl, "phone") not in scores:
                    continue
                s = scores[(mdl, "phone")]
                row = [s["e"][groups == g].sum() / s["n"][groups == g].sum() * 100 for g in cantons]
                heat.append(row)
                md.append(f"| {mdl} | " + " | ".join(f"{v:.1f}" for v in row) + " |")
            # SG vs ZH with speaker-clustered CI, best SG model
            best = min((m for m in models if (m, "phone") in scores),
                       key=lambda m: scores[(m, "phone")]["wer"][0])
            s = scores[(best, "phone")]
            for g in ["SG", "ZH", "BE", "VS"]:
                if g in cantons:
                    sel = np.flatnonzero(groups == g)
                    ci = bootstrap(lambda i: s["e"][sel][i].sum() / s["n"][sel][i].sum(),
                                   len(sel), any_df.speaker.values[sel])
                    md.append(f"\n{best}, phone, {g}: WER {fmt(*ci)}")

        if ds == "spcr":
            n_all = sum(1 for _ in open(next((RES / ds).glob("*.jsonl")), encoding="utf-8"))
            md.append(f"\n({n_all - len(any_df)} of {n_all} segments with French references excluded.)")
            types = {m: number_error_types(runs[(m, "phone")]) for m in models if (m, "phone") in runs}
            cats = sorted({c for t in types.values() for c in t if c != "total"},
                          key=lambda c: -sum(t[c] for t in types.values()))
            md += ["\n**What goes wrong with numbers on the phone line** "
                   "(% of reference numbers, token alignment):\n",
                   "| error type | " + " | ".join(types) + " |", "|---|" + "---|" * len(types)]
            for c in cats:
                md.append(f"| {c} | " + " | ".join(f"{100 * t[c] / t['total']:.1f}" for t in types.values()) + " |")
            md.append("| **all number errors** | " + " | ".join(
                f"**{100 * sum(v for k, v in t.items() if k != 'total') / t['total']:.1f}**"
                for t in types.values()) + " |")

            # number-specific error rate with CI, and each model vs. its base model
            per = {m: number_specific_rate(per_segment_number_errors(runs[(m, "phone")])) for m in types}
            N = len(any_df)
            md += ["\n**Number-specific error rate on the phone line** (excluding skipped passages; "
                   "paired bootstrap vs. the base model):\n",
                   "| model | error % ↓ [95% CI] | vs. base | Δ pts [95% CI] |", "|---|---|---|---|"]
            base_of = {"turbo-SG (MIT)": "large-v3-turbo", "large-v3-SG (Flix)": "large-v3"}
            for m, (e, t) in per.items():
                ci = bootstrap(lambda i: e[i].sum() / t[i].sum(), N)
                b = base_of.get(m)
                if b in per:
                    eb, tb = per[b]
                    d = bootstrap(lambda i: e[i].sum() / t[i].sum() - eb[i].sum() / tb[i].sum(), N)
                    md.append(f"| {m} | {fmt(*ci)} | {b} | {fmt(*d)} |")
                else:
                    md.append(f"| {m} | {fmt(*ci)} | | |")

        miss = number_misses(runs[(models[-1], "phone")]) if (models[-1], "phone") in runs else []
        if miss:
            md += [f"\n**Number errors, {models[-1]} on the phone line (sample):**\n",
                   "| dialect | reference | hypothesis | missed |", "|---|---|---|---|"]
            md += [f"| {g} | {r} | {h} | {m} |" for g, r, h, m in miss]

    if lat:
        md += ["\n## Latency (batch size 1, G.711 clips, " + next(iter(lat.values()))["gpu"] + ")\n",
               "| model | mean clip s | p50 ms ↓ | p90 ms ↓ | p99 ms ↓ | RTF ↓ |", "|---|---|---|---|---|---|"]
        for mdl in SHORT.values():
            if mdl in lat:
                r = lat[mdl]
                md.append(f"| {mdl} | {r['mean_clip_s']:.1f} | {r['p50_ms']:.0f} | {r['p90_ms']:.0f} | "
                          f"{r['p99_ms']:.0f} | {r['rtf']:.3f} |")
        # quality vs latency trade-off
        runs = load("asgdts")
        if runs:
            any_df = next(iter(runs.values()))
            fig, ax = plt.subplots(figsize=(6, 4))
            for mdl in lat:
                if (mdl, "phone") in runs:
                    e, n = wer_counts(runs[(mdl, "phone")].ref, runs[(mdl, "phone")].hyp)
                    ax.scatter(lat[mdl]["p50_ms"], e.sum() / n.sum() * 100, s=60)
                    ax.annotate(mdl, (lat[mdl]["p50_ms"], e.sum() / n.sum() * 100),
                                textcoords="offset points", xytext=(6, 4), fontsize=8)
            ax.set_xlabel("p50 latency per utterance (ms), batch 1")
            ax.set_ylabel("WER % on G.711 phone audio")
            ax.set_title("Quality vs latency (lower-left is better)")
            fig.tight_layout()
            fig.savefig(FIG / "tradeoff.png", dpi=150)
            plt.close(fig)

    (RES / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
