# Validation: 24 October 2026

This release was tested on one Windows 11 workstation with an NVIDIA GeForce RTX 5090 (32 GB class), NVIDIA driver 621.01, Docker Engine 29.9.2, Compose 5.6.1 and WSL 2 kernel 6.18.54.1. The Linux environment reported about 37.2 GiB of system RAM. Lower-memory Windows systems and other GPUs were not qualified.

## Image build and inference: passed

The portable Dockerfile was built from public sources, without using the private image used for earlier article experiments. The final recipe pins its Python base digest and ComfyUI commit, constrains the resolved Python dependency set and includes the C compiler required by Triton. `pip check` passed. A real CUDA tensor calculation returned the RTX 5090 device and four `2.0` values. The final service also completed both real image workflows on CUDA.

| Check | Actual result |
| --- | --- |
| ComfyUI readiness | Healthy; `/system_stats` responds |
| Original Z-Image Base scene | Successful history receipt and inspected 1280 x 768 PNG; 45.15 seconds including model loading |
| FLUX reference example | Successful history receipt and inspected 1280 x 768 PNG; 10.02 seconds including model loading |
| Image inspection | Base scene shows one yellow robot with a telescope at a lunar shop; reference result shows one bipedal mechanical robot |
| Model identity | SHA-256 recorded for all six image-model files |

The reference input was an earlier generated robot illustration. It is not included in this source-only repository, so readers supply their own input. The Base image is an illustration, not a guarantee of engineering or astronomical accuracy. Both outputs are single examples; these times are not general performance promises.

The test reused existing image weights read-only through a private test override. Input, output and state folders were isolated. It did not repeat Windows/driver installation on a clean PC or download fresh image weights. Readers use their own `models` folder as shown in the public Compose file.

See [image results](image-results-20261024.json), [model hashes](model-sha256.txt), [Dockerfile](../docker/Dockerfile) and [resolved packages](../docker/resolved-packages.txt). The recorded custom image ID is a local build identity; readers build the image themselves. The recipe is not a bit-for-bit OS/package archive: apt repositories and the pip bootstrap can still change.

## Kokoro and Voxtral speech: passed functional tests

The optional upstream Kokoro image and vLLM-Omni image are digest-pinned. The public download helper retrieved or verified the exact two Voxtral baseline revisions. Tests used only original scripts and preset voices. Both TTS engines produced three complete, non-silent, mono 24 kHz PCM WAVs. Header/frame counts and file hashes were checked. The helper now normalizes upstream streaming WAV headers before saving them.

Voxtral STT loaded its entire BF16 model onto CUDA and transcribed all six clips. Its peak allocated GPU memory was about 8.51 GiB. This was file transcription, not a test of live microphone latency or diarization.

| TTS / script | Audio duration | TTS request wall time | Raw round-trip WER |
| --- | ---: | ---: | ---: |
| Kokoro / scene | 21.660 s | 1.653 s | 0% |
| Kokoro / technical | 14.622 s | 0.310 s | 31.4% |
| Kokoro / playful | 8.288 s | 0.277 s | 0% |
| Voxtral TTS / scene | 18.779 s | 56.494 s | 0% |
| Voxtral TTS / technical | 15.832 s | 3.290 s | 31.4% |
| Voxtral TTS / playful | 7.495 s | 1.678 s | 0% |

**Read the transcripts before interpreting that 31.4%.** Both technical outputs wrote `Comfy UI` for `ComfyUI`, `4271` for the four spoken digits, and `$12.50` for the spelled-out price. The simple metric does not rewrite those forms. It is not evidence that a third of the audio was unintelligible. Scene and playful text matched after case/punctuation normalization. No preferred-sounding voice was selected by an automated score; human listening is still needed.

TTS timings exclude server/model startup and include the host helper request. The first Voxtral request includes first-use work; the later two are warm. STT model loading took 52.888 seconds. Its first generation took 24.927 seconds; later file inferences took 2.738 to 6.744 seconds. Different text lengths, preset voices, runtimes and cache states prevent treating this as a controlled speed ranking. No streaming-latency or broad speech-quality claim is made.

See the full [speech result record](speech-results-20261024.json), [research](SPEECH-RESEARCH.md), and [Windows speech example](SPEECH-WINDOWS.md). The tested TTS 2603 and STT 2602 are dated local baselines. Voxtral 3 was researched, not run.

## Source and release checks

Python helpers compiled. The Windows folder initializer ran successfully and passed PowerShell syntax parsing. Compose configuration passed with all optional profiles. The saved Base workflow matches the sample and helper. WER arithmetic was checked with exact-match, substitution, deletion, insertion and punctuation/case examples. The listening-page generator ran against actual transcripts and existing audio files.

Public files were reviewed for weights, media, credentials and private application/workstation paths. Runtime folders are ignored by Git. The public material consists of source, configuration, original text and small dated result records. Our code uses MIT; the adapted upstream Voxtral pipeline retains Apache 2.0 with its license and attribution included.

All test services were stopped after completion. No unrelated application's containers, model files or settings were changed. The separate native Whisper guide remains unqualified; it is not advertised as a tested part of this Docker release.
