"""Save speech from a local API without installing Python dependencies."""
import argparse
import io
import json
from pathlib import Path
import sys
import wave
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--url", default="http://127.0.0.1:8895/v1/audio/speech")
    parser.add_argument("--model", default="kokoro")
    parser.add_argument("--voice", default="af_heart")
    parser.add_argument("--speed", type=float, default=0.95)
    args = parser.parse_args()
    parsed = urlparse(args.url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        parser.error("Use an HTTP loopback URL for this local-only example.")
    if not 0.25 <= args.speed <= 4:
        parser.error("Speed must be between 0.25 and 4.")
    if args.output.exists():
        parser.error("Output already exists. Choose a new filename.")
    text = args.input.read_text(encoding="utf-8-sig").strip()
    if not text:
        parser.error("Input is empty.")
    request = Request(args.url, data=json.dumps({"model": args.model, "input": text,
        "voice": args.voice, "speed": args.speed, "response_format": "wav"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=300) as response:
        data = response.read()
    if len(data) <= 44 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError("Service did not return a nonempty RIFF/WAVE file.")
    # The upstream streaming WAV may use placeholder lengths. Rebuild its
    # header from the actual PCM bytes before saving a normal seekable file.
    with wave.open(io.BytesIO(data), "rb") as source:
        params = source.getparams()
        frames = source.readframes(source.getnframes())
    frame_bytes = params.nchannels * params.sampwidth
    if not frames or len(frames) % frame_bytes:
        raise ValueError("Service returned empty or incomplete PCM audio.")
    normalized = io.BytesIO()
    with wave.open(normalized, "wb") as target:
        target.setparams(params)
        target.setnframes(len(frames) // frame_bytes)
        target.writeframes(frames)
    data = normalized.getvalue()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as output:
        output.write(data)
    print(f"Saved {args.output} ({len(data)} bytes). Listen before using it.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, URLError, ValueError, wave.Error, EOFError) as exc:
        print(f"Narration failed: {exc}", file=sys.stderr)
        sys.exit(1)
