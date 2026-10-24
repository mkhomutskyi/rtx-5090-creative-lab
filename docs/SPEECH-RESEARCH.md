# Speech research: Kokoro and Voxtral

Checked 24 October 2026 against the linked primary sources.

| Tool | Job | Route selected for this lab |
| --- | --- | --- |
| Kokoro-82M | Text to speech | Existing upstream Kokoro-FastAPI GPU image; preset `af_heart` |
| Voxtral 4B TTS 2603 | Text to speech | March 2026 open-weight baseline; preset `casual_male`; vLLM-Omni in a Linux container |
| Voxtral Mini 4B Realtime 2602 | Speech to text | February 2026 open-weight baseline; Transformers file transcription on CUDA |
| Voxtral 3 | Newer TTS and STT family | Current research coverage; no inference result claimed |

Kokoro is a speech synthesizer, not a transcriber. Voxtral is a family: its TTS and STT models are different checkpoints. Loading one does not provide both jobs.

## Why these exact versions

Mistral announced Voxtral 3 on [20 October 2026](https://docs.mistral.ai/resources/changelogs). Its [announcement](https://mistral.ai/news/voxtral-3/) describes API and self-deployment options. The current [TTS 3](https://docs.mistral.ai/models/voxtral-mini-tts-3-0) and [Mini Transcribe 3](https://docs.mistral.ai/models/voxtral-mini-transcribe-3-0) cards classify them as Premier public previews. At the check date, Mistral's [public Voxtral weight collection](https://huggingface.co/collections/mistralai/voxtral) did not list downloadable Voxtral 3 checkpoints. An enterprise self-deployment offer is not proof of a public one-command consumer download. We did not call the hosted API or claim to run Voxtral 3 on this GPU.

The public [TTS 2603 card](https://huggingface.co/mistralai/Voxtral-4B-TTS-2603) recommends vLLM-Omni and lists a 16 GB minimum GPU. Its weights and reference voices use CC BY-NC 4.0; review the exact terms before using it in a commercial project. The [Realtime 2602 card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602) uses Apache 2.0 and documents Transformers support. The lab selects these as explicit older local baselines, not the latest Voxtral release. No weights or voices are redistributed in this repository.

A newer Arabic-specialized checkpoint is present in the collection, but its [own model card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-Arabic) recommends the original model for other languages. It is not used as a substitute for the English test.

## Test design

Three original English scripts cover a scene, technical names and numbers, and a playful line about a robot nap. Generate each with both TTS engines, then transcribe the resulting six files with the same Voxtral STT checkpoint. Save the exact source, transcript, timings and simple word-error calculation. Run one GPU service at a time.

This is a functional example on synthetic speech. It is not a microphone, noisy-room, accent, diarization or streaming-latency benchmark. The round trip combines synthesizer pronunciation and transcriber behavior; a word mismatch cannot by itself identify which model caused it. Case and punctuation are removed for WER; number and acronym spellings are not rewritten. Human listening remains necessary before choosing a preferred voice.

## Runtime sources

- [Kokoro](https://github.com/hexgrad/kokoro) and [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI).
- [Official vLLM-Omni GPU installation](https://docs.vllm.ai/projects/vllm-omni/en/latest/getting_started/installation/gpu/) and [speech API](https://docs.vllm.ai/projects/vllm-omni/en/stable/serving/speech_api/).
- [Transformers Voxtral Realtime](https://huggingface.co/docs/transformers/main/en/model_doc/voxtral_realtime).

Use the dated [validation record](VALIDATION.md) for actual outcomes and the [speech guide](SPEECH-WINDOWS.md) for the tested commands.
