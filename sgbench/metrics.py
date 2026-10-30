"""Corpus metrics with bootstrap confidence intervals (resampling utterances)."""
from collections import Counter

import jiwer
import numpy as np
import sacrebleu

from .numbers_de import numbers, tokens


def norm(text: str) -> str:
    return " ".join(tokens(text))


def wer_counts(refs, hyps):
    """Per-utterance (edit errors, reference words) so corpus WER can be bootstrapped."""
    errs, lens = [], []
    for r, h in zip(refs, hyps):
        r, h = norm(r), norm(h)
        n = len(r.split())
        if n == 0:
            errs.append(len(h.split()))
            lens.append(0)
            continue
        o = jiwer.process_words(r, h if h else "<empty>")
        errs.append(o.substitutions + o.deletions + o.insertions)
        lens.append(n)
    return np.array(errs), np.array(lens)


def number_counts(refs, hyps):
    """Per-utterance (matched, numbers in ref, numbers in hyp) as multisets."""
    m, nr, nh = [], [], []
    for r, h in zip(refs, hyps):
        cr, ch = Counter(numbers(r)), Counter(numbers(h))
        m.append(sum((cr & ch).values()))
        nr.append(sum(cr.values()))
        nh.append(sum(ch.values()))
    return np.array(m), np.array(nr), np.array(nh)


def bleu(refs, hyps) -> float:
    return sacrebleu.corpus_bleu([norm(h) for h in hyps], [[norm(r) for r in refs]]).score


def resampler(n_items: int, clusters=None, seed: int = 0):
    """Yields bootstrap index sets. With `clusters` (e.g. speaker ids), whole clusters are
    resampled: utterances of one speaker are correlated, so i.i.d. resampling of
    utterances would give intervals that are too narrow."""
    rng = np.random.default_rng(seed)
    if clusters is None:
        while True:
            yield rng.integers(0, n_items, n_items)
    clusters = np.asarray(clusters)
    members = [np.flatnonzero(clusters == c) for c in np.unique(clusters)]
    while True:
        pick = rng.integers(0, len(members), len(members))
        yield np.concatenate([members[k] for k in pick])


def bootstrap(stat, n_items: int, clusters=None, n_boot: int = 1000, seed: int = 0):
    """stat(idx) -> float. Returns (point estimate, 2.5%, 97.5%)."""
    point = stat(np.arange(n_items))
    gen = resampler(n_items, clusters, seed)
    samples = [stat(next(gen)) for _ in range(n_boot)]
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return point, lo, hi
