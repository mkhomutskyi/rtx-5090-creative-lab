"""Build a local listening page from the Voxtral comparison JSON."""
import argparse
from pathlib import Path
import html
import json


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--results", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        p.error("Choose a new output page; existing pages are preserved.")
    data = json.loads(a.results.read_text(encoding="utf-8-sig"))
    rows = []
    for item in data["cases"]:
        name = item["name"]
        if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
            raise ValueError("Unsafe example filename")
        audio = a.output.parent / (name + ".wav")
        if not audio.is_file():
            raise FileNotFoundError(audio)
        rows.append(f'<section><h2>{html.escape(name)}</h2><audio controls preload="none" src="{name}.wav"></audio>'
                    f'<p><strong>Source</strong><br>{html.escape(item["source_text"])}</p>'
                    f'<p><strong>Voxtral transcript</strong><br>{html.escape(item["transcript"])}</p>'
                    f'<p class="metric">Raw word error rate: {item["wer"]:.1%} · audio: {item["audio_seconds"]:.2f}s · '
                    f'STT inference: {item["inference_seconds"]:.2f}s</p></section>')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>RTX 5090 speech listening test</title><style>
body{margin:0;background:#f4f7fb;color:#17283c;font:17px/1.55 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:40px 24px}h1{font-size:40px;line-height:1.15}h2{font-size:22px;color:#17548c}header{border-top:8px solid #f3c846;padding:18px 0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}section{background:white;padding:24px;border:1px solid #d6e0ec;border-radius:8px}audio{width:100%}.metric{font-size:14px;color:#465a70}@media(max-width:740px){.grid{grid-template-columns:1fr}h1{font-size:32px}}</style>
<main><header><h1>One script. Two voices. One transcriber.</h1><p>Listen to the original local test clips. Read the source and the Voxtral transcript. Decide what sounds clear, natural and worth improving.</p><p>This small synthetic round trip is not a human-speech benchmark. A transcription mismatch can come from either engine. Word-error rate is not a voice-quality score. The metric does not rewrite number formats or join compound names: four two seven one versus 4271, or ComfyUI versus Comfy UI, still count as differences.</p></header><div class="grid">'''
    # Keep corresponding Kokoro/Voxtral examples next to each other.
    order = sorted(range(len(rows)), key=lambda i: (data["cases"][i]["name"].split("-", 1)[-1], data["cases"][i]["name"]))
    page += "".join(rows[i] for i in order) + "</div></main></html>"
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(page, encoding="utf-8")
    print(a.output)


if __name__ == "__main__":
    main()
