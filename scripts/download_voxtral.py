"""Download two dated Voxtral baselines; never downloads a moving model revision."""
import argparse
from pathlib import Path
import json
from huggingface_hub import snapshot_download

MODELS = [
    ("mistralai/Voxtral-4B-TTS-2603", "b81be46c3777f88621676791b512bb01dc1cb970", "voxtral-tts",
     ["consolidated.safetensors", "params.json", "tekken.json", "voice_embedding/*", "README.md"]),
    ("mistralai/Voxtral-Mini-4B-Realtime-2602", "2769294da9567371363522aac9bbcfdd19447add", "voxtral-stt",
     ["model.safetensors", "config.json", "generation_config.json", "processor_config.json", "tekken.json", "README.md"]),
]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--models", type=Path, required=True)
    a = p.parse_args()
    a.models.mkdir(parents=True, exist_ok=True)
    for repo, revision, folder, patterns in MODELS:
        print("Downloading", repo, revision, flush=True)
        snapshot_download(repo_id=repo, revision=revision, local_dir=a.models / folder, allow_patterns=patterns)
    record = [{"repo": r, "revision": v, "folder": f, "patterns": p} for r, v, f, p in MODELS]
    (a.models / "voxtral-download-record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
