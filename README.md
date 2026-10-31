# RTX 5090 Creative Lab

Turn a gaming PC into a small local creative studio. Start with an original Moon repair-shop scene, generate its illustration with ComfyUI, and add optional Kokoro narration. Use native LM Studio to help write and refine the prompt.

This companion project supplies our Docker build recipe, Windows commands, original examples and small API helpers. It uses third-party applications and models. No hosted generation API or API key is required for the supplied inference paths.

## Start here

- [MiniMax H3: local video on an RTX 5090](docs/h3/README.md): model downloader, Docker profile, five robot images, animation commands and a music-video edit. See its [validation limits](docs/h3/VALIDATION.md).

- [Windows and Docker setup](docs/WINDOWS-DOCKER.md): install prerequisites, prepare folders, build, check CUDA, generate, narrate and stop.
- [Kokoro and Voxtral speech](docs/SPEECH-WINDOWS.md): generate three clips with each voice, transcribe them locally and open a listening page.
- [Speech research](docs/SPEECH-RESEARCH.md): current Voxtral 3 coverage and the older downloadable baselines used here.
- [Models](docs/MODELS.md): exact filenames, publisher download links and placement.
- [Improve the prompt and picture](docs/PROMPT-WORKFLOW.md): a reusable LM Studio brief and a small comparison loop.
- [Validation](docs/VALIDATION.md): dated tests, versions, model hashes and limits.
- [Dependencies and licenses](docs/DEPENDENCIES.md): what is ours and what comes from upstream.

For desktop apps, native LM Studio and Comfy Desktop are another route. This repository covers the Docker image workflow and optional local speech profiles. LM Studio stays native on Windows. The host-side Python helpers use only the standard library.

After cloning and following the prerequisites and [model guide](docs/MODELS.md), run from this folder in PowerShell:

```powershell
.\scripts\Initialize-Lab.ps1
python scripts/check_models.py --models models
docker compose config --quiet
docker compose build comfyui
docker compose run --rm --no-deps comfyui python -c "import torch; assert torch.cuda.is_available(); x=torch.ones(4, device='cuda'); print(torch.cuda.get_device_name(0), (x+x).cpu().tolist())"
docker compose up -d comfyui
```

Wait for `docker compose ps` to show healthy, then:

```powershell
python scripts/generate_robot_study.py --url http://127.0.0.1:8195 --prompts examples/scene-prompts.json --record-dir outputs/receipts
docker compose stop comfyui
```

The full guide covers optional reference images, narration, blocked PowerShell scripts, port conflicts and recovery. The web services bind to this computer's loopback address. Unload your LLM before image work to free GPU memory. Use a new job name and receipt directory for a fresh comparison; the Base helper skips existing receipts.

Whisper has a [separate native-Windows installation guide](docs/WHISPER-WINDOWS.md). That optional guide has not been qualified as part of this Docker release.

## What stays local

Model weights, recordings, input photos, credentials, state and generated outputs are ignored by Git. This repository contains code, configuration, documentation, workflow JSON and original text examples. It includes no model weights, manufacturer photos or generated celebrity pictures.

Our code and documentation use the [MIT license](LICENSE), with an Apache-licensed adapted pipeline listed in [third-party notices](THIRD_PARTY_NOTICES.md). Upstream applications, containers and model weights retain their own terms. The build downloads several GB; model weights require additional storage. The validation record describes one RTX 5090 workstation, not a promise for every Windows installation.

A huge thank-you to my friend Shai for gifting me the RTX 5090 and making these experiments possible.
