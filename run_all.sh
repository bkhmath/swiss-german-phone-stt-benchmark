#!/usr/bin/env bash
# Full benchmark: 5 checkpoints x {wideband, phone} on both test sets, packet loss on two, latency.
# Runs whose results already exist are skipped, so the script can be resumed.
set -u
export PYTHONIOENCODING=utf-8 HF_HUB_DISABLE_SYMLINKS_WARNING=1 TRANSFORMERS_VERBOSITY=error
PY=.venv/Scripts/python
MODELS="openai/whisper-large-v3-turbo gcoli/whisper-large-v3-turbo-swiss-german-mit Flix-AI/flix-swissgerman-full openai/whisper-small openai/whisper-large-v3"

bench() {  # model dataset condition [extra args]
  local m=$1 ds=$2 c=$3; shift 3
  [ -f "results/$ds/${m//\//__}__$c.meta.json" ] && return
  $PY run_bench.py --model "$m" --dataset "$ds" --condition "$c" "$@" 2>/dev/null | tail -1
}

for m in $MODELS; do
  for c in wide phone; do
    bench "$m" asgdts $c
    bench "$m" spcr $c --max-seconds 120 --batch-size 8
  done
  [ -f "results/latency/${m//\//__}.json" ] || $PY latency.py --model "$m" --n 200 2>/dev/null | tail -1
done
for m in openai/whisper-large-v3-turbo gcoli/whisper-large-v3-turbo-swiss-german-mit; do
  bench "$m" asgdts phone_loss3
done
echo ALL_DONE
