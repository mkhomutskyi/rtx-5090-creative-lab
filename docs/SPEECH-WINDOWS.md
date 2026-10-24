# Local speech on Windows: Kokoro, Voxtral TTS and Voxtral STT

Use Docker Desktop's WSL 2 backend and the prerequisites in [WINDOWS-DOCKER.md](WINDOWS-DOCKER.md). Run the following commands from this repository in PowerShell. Read the [speech research and model terms](SPEECH-RESEARCH.md) first. The two Voxtral models below are explicitly older local baselines, not Voxtral 3.

Run one GPU workload at a time. Stop ComfyUI and unload LM Studio before starting speech. This guide uses three short original English scripts and preset voices. It does not clone a person's voice.

## 1 Prepare the optional Voxtral runtime and weights

The runtime is large, and the selected weights add about 17 GB. The following script downloads the pinned official revisions, preserves Hugging Face's resumable cache, and saves a model record. It does not download the duplicate consolidated STT weights.

```powershell
.\scripts\Initialize-Lab.ps1
$voxtralImage = 'vllm/vllm-omni@sha256:fc77cfaac7b1b43c30cbf32eaea214864434c6e0f303e6e9eb9f64104241a994'
docker pull $voxtralImage
docker run --rm -v "${PWD}/models:/models" -v "${PWD}/scripts:/scripts:ro" $voxtralImage python /scripts/download_voxtral.py --models /models
```

Weights go under `models/voxtral-tts` and `models/voxtral-stt`, both ignored by Git. No account token is required for these public revisions at the check date. If access requirements change, follow the publisher's process yourself. Never put credentials in a tracked file.

## 2 Make the three Kokoro clips

```powershell
docker compose stop comfyui
docker compose --profile voice up -d kokoro
```

Wait for [Kokoro's local docs](http://127.0.0.1:8895/docs), then:

```powershell
python scripts/narrate.py --input examples/scene.txt --output outputs/kokoro-scene.wav
python scripts/narrate.py --input examples/speech-technical.txt --output outputs/kokoro-technical.wav
python scripts/narrate.py --input examples/speech-playful.txt --output outputs/kokoro-playful.wav
docker compose --profile voice stop kokoro
```

The helper uses `af_heart` at speed 0.95 and saves a normal WAV header, including when the upstream response uses a streaming header. It refuses to replace an existing output.

## 3 Make the same three clips with Voxtral TTS

```powershell
docker compose --profile voxtral up -d voxtral-tts
docker compose --profile voxtral logs --tail 50 voxtral-tts
```

Wait for [the local model list](http://127.0.0.1:8896/v1/models). The profile uses an adapted upstream pipeline for one request at a time, with eager execution and a conservative GPU memory budget. See [third-party notices](../THIRD_PARTY_NOTICES.md).

```powershell
python scripts/narrate.py --url http://127.0.0.1:8896/v1/audio/speech --model voxtral-tts --voice casual_male --input examples/scene.txt --output outputs/voxtral-scene.wav
python scripts/narrate.py --url http://127.0.0.1:8896/v1/audio/speech --model voxtral-tts --voice casual_male --input examples/speech-technical.txt --output outputs/voxtral-technical.wav
python scripts/narrate.py --url http://127.0.0.1:8896/v1/audio/speech --model voxtral-tts --voice casual_male --input examples/speech-playful.txt --output outputs/voxtral-playful.wav
docker compose --profile voxtral stop voxtral-tts
```

These are different preset voices. The same nominal speed setting does not establish equal acoustic pace. Listen before choosing a voice; a lower error count is not proof of more expressive narration.

## 4 Transcribe all six files on the GPU

```powershell
docker compose --profile voxtral run --rm --no-deps voxtral-stt
```

Success: `outputs/voxtral-stt-results.json` contains each source, actual transcript, word-error count, duration and inference time. The helper requires CUDA and loads only the local pinned model files. It does not silently fall back to CPU. Existing result files are preserved; use a fresh `--output` when repeating a run.

This is file transcription with a model named Realtime. It does not test microphone capture, streaming delay, diarization or noisy audio.

## 5 Listen and compare

```powershell
python scripts/build_speech_review.py --results outputs/voxtral-stt-results.json --output outputs/speech-review.html
Start-Process outputs/speech-review.html
```

Keep this page next to its WAV files. Check names, numbers, pauses, missing words and sentence endings. The scripts and comparison JSON are reusable with your own short recordings, but the dated release results use synthetic speech only. A round-trip mismatch can originate in TTS pronunciation or STT interpretation. Review both before assigning blame.

The [validation record](VALIDATION.md) reports the actual tested outcomes. The newer Voxtral 3 family is documented separately; this profile does not call a hosted API.
