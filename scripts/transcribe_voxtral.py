"""Transcribe synthetic test clips locally with Voxtral and compare their source text."""
import argparse
import json
from pathlib import Path
import re
import time
import unicodedata


def words(text):
    return re.findall(r"\w+", unicodedata.normalize("NFKC", text).lower())


def word_errors(reference, hypothesis):
    ref, hyp = words(reference), words(hypothesis)
    if not ref:
        raise ValueError("Reference text must contain words.")
    dp = [[0] * (len(hyp) + 1) for _ in range(len(ref) + 1)]
    for i in range(len(ref) + 1):
        dp[i][0] = i
    for j in range(len(hyp) + 1):
        dp[0][j] = j
    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1,
                           dp[i-1][j-1] + (ref[i-1] != hyp[j-1]))
    i, j, sub, delete, insert = len(ref), len(hyp), 0, 0, 0
    while i or j:
        if i and j and ref[i-1] == hyp[j-1] and dp[i][j] == dp[i-1][j-1]:
            i, j = i-1, j-1
        elif i and j and dp[i][j] == dp[i-1][j-1] + 1:
            sub += 1
            i, j = i-1, j-1
        elif i and dp[i][j] == dp[i-1][j] + 1:
            delete += 1
            i -= 1
        else:
            insert += 1
            j -= 1
    return {"reference_words": len(ref), "substitutions": sub, "deletions": delete,
            "insertions": insert, "wer": (sub + delete + insert) / len(ref)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--cases", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        p.error("Output already exists. Choose a fresh results file.")
    cases = json.loads(a.cases.read_text(encoding="utf-8-sig"))["cases"]
    for case in cases:
        if not Path(case["audio"]).is_file() or not Path(case["reference"]).is_file():
            p.error("Missing audio or reference for " + case["name"])
    import torch
    from transformers import AutoProcessor, VoxtralRealtimeForConditionalGeneration
    from mistral_common.tokens.tokenizers.audio import Audio
    assert torch.cuda.is_available(), "CUDA unavailable; CPU fallback is not a GPU test."
    start = time.monotonic()
    processor = AutoProcessor.from_pretrained(a.model, local_files_only=True)
    model = VoxtralRealtimeForConditionalGeneration.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda", local_files_only=True,
        attn_implementation="sdpa").eval()
    assert model.device.type == "cuda"
    torch.cuda.synchronize()
    result = {"model": "mistralai/Voxtral-Mini-4B-Realtime-2602",
              "revision": "2769294da9567371363522aac9bbcfdd19447add",
              "device": torch.cuda.get_device_name(0), "dtype": str(model.dtype),
              "model_loading_seconds": round(time.monotonic() - start, 3),
              "mode": "file transcription; not a live microphone/streaming latency test",
              "normalization": "NFKC, lowercase, Unicode word tokens; no number or acronym rewriting",
              "cases": []}
    for index, case in enumerate(cases):
        audio = Audio.from_file(case["audio"], strict=False)
        audio.resample(processor.feature_extractor.sampling_rate)
        duration = len(audio.audio_array) / processor.feature_extractor.sampling_rate
        inputs = processor(audio.audio_array, return_tensors="pt").to(model.device, dtype=model.dtype)
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
        start = time.monotonic()
        with torch.inference_mode():
            output = model.generate(**inputs, do_sample=False, max_new_tokens=512)
        torch.cuda.synchronize()
        elapsed = time.monotonic() - start
        text = processor.batch_decode(output, skip_special_tokens=True)[0].strip()
        reference = Path(case["reference"]).read_text(encoding="utf-8-sig").strip()
        item = {"name": case["name"], "source_text": reference, "transcript": text,
                "audio_seconds": round(duration, 3), "inference_seconds": round(elapsed, 3),
                "real_time_factor": round(elapsed / duration, 3), "first_generation": index == 0,
                "peak_gpu_allocated_gib": round(torch.cuda.max_memory_allocated() / 2**30, 3),
                **word_errors(reference, text)}
        result["cases"].append(item)
        print(json.dumps(item, ensure_ascii=False), flush=True)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x", encoding="utf-8") as target:
        json.dump(result, target, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
