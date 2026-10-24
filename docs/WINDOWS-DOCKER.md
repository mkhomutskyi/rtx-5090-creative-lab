# Deploy the creative lab with Docker on Windows

This route keeps LM Studio native on Windows and runs ComfyUI, plus optional Kokoro, in Linux containers through Docker Desktop. All commands below run in **PowerShell from this repository's root** unless stated otherwise. They create an independent lab; they do not require a pre-existing private Docker image.

**Status:** build, real GPU image generation and optional speech examples tested on 24 October 2026. See [validation](VALIDATION.md) for the exact scope and limits. Earlier article images came from a separate runtime.

## 1 Prepare Windows

Use Windows 11, a current NVIDIA Windows driver and Docker Desktop's WSL 2 backend. See [Docker's Windows installer](https://docs.docker.com/desktop/setup/install/windows-install/), [Windows GPU requirements](https://docs.docker.com/desktop/features/gpu/) and [Microsoft WSL setup](https://learn.microsoft.com/en-us/windows/wsl/install). Follow those installers for the actual machine; reboot when requested. Review the applicable Docker Desktop terms.

If WSL is not installed, Microsoft's initial command is `wsl --install` from an administrator PowerShell window. An existing WSL installation may need `wsl --update`. In Docker Desktop select the WSL 2 backend and Linux containers. Do not install a Linux NVIDIA display driver inside WSL as a substitute for the Windows driver.

Check:

```powershell
nvidia-smi
wsl --status
docker version
docker compose version
```

Success: Windows lists the RTX 5090, WSL is available, and Docker reports both client and server. These checks do not prove CUDA inference.

## 2 Prepare the lab folders and models

Place this project in its own folder. Install [Git for Windows](https://gitforwindows.org/) to clone it, or use GitHub's Download ZIP button. With Git installed:

```powershell
git clone https://github.com/mkhomutskyi/rtx-5090-creative-lab.git D:\rtx-5090-creative-lab-public
Set-Location D:\rtx-5090-creative-lab-public
```
```powershell
.\scripts\Initialize-Lab.ps1
```

If Windows blocks this local script, review it, then run `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Initialize-Lab.ps1`. This applies only to that process. The script creates local `models`, `inputs`, `outputs` and `state` folders. It installs nothing. Put the three Base files from [the model guide](MODELS.md) in their indicated subfolders, then check:

```powershell
python scripts/check_models.py --workflow zimage
```

Use a supported Python 3.11+ installation for the host helpers. They need no third-party Python packages. Allow substantial SSD space for container layers, Torch and model files. The first build downloads multiple GB; it is not a quick-start timing promise.

## 3 Validate and build

```powershell
docker compose config --quiet
docker compose build comfyui
```

Our Dockerfile fetches ComfyUI at commit `b0b743566f65daafc423b4fea8a2fbda94b3384a` from its public repository. It installs Torch 2.14.1 and Torchvision 0.29.1 from the official CUDA 13.0 wheel index. The recipe also pins the Python base digest and resolved Python dependency constraints. The new build completed the dated qualification. Build-time downloads do not include model weights. Custom nodes are disabled by default.

## 4 Prove a GPU calculation works in the built container

```powershell
docker compose run --rm --no-deps comfyui python -c "import torch; assert torch.cuda.is_available(), 'CUDA unavailable'; x=torch.ones(4, device='cuda'); print(torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0), (x+x).cpu().tolist())"
```

Success: the RTX 5090 name and four `2.0` values. A driver table or a passing build alone is insufficient. If CUDA fails, stop here and diagnose the driver/WSL/container path.

## 5 Start ComfyUI and create one image

Unload any LM Studio model first so the image job has room on the GPU. Port 8195 must be available; if you already use it, change the host port in Compose and use that port in the following commands.

```powershell
docker compose up -d comfyui
docker compose ps
docker compose logs --tail 50 comfyui
Invoke-RestMethod http://127.0.0.1:8195/system_stats
```

Wait for startup and the health check. Open [local ComfyUI](http://127.0.0.1:8195). The host port binds to loopback, not the network. Then run:

```powershell
python scripts/generate_robot_study.py --url http://127.0.0.1:8195 --prompts examples/scene-prompts.json --record-dir outputs/receipts
```

Success: a PNG under `outputs` and a matching successful history receipt under `outputs/receipts`. Inspect the picture. A 200 response from `system_stats` proves API readiness, not image correctness. The helper refuses a busy queue and records the submitted workflow and seed.

## 6 Optional reference-guided image

Install the additional files listed in [MODELS.md](MODELS.md), upload your own `robot-reference.png` through the local UI, and check the files:

```powershell
python scripts/check_models.py --workflow flux-reference
New-Item -ItemType Directory -Path outputs/reference-receipts -Force
python scripts/generate_robot_references.py --url http://127.0.0.1:8195 --prompts examples/reference-prompts.json --record-dir outputs/reference-receipts
```

This path changes the image model and conditioning; compare it separately from a prompt-only change. Inspect the actual result for anatomy and likeness. Image files supplied as references are local inputs, not automatically publishable source assets.

## 7 Optional narration with Kokoro

Release ComfyUI's GPU allocation before starting speech:

```powershell
docker compose stop comfyui
docker compose --profile voice up -d kokoro
docker compose --profile voice logs --tail 50 kokoro
```

The optional service uses the upstream RTX 50-series Kokoro-FastAPI image, pinned to the digest observed locally. It is still a third-party community wrapper. Wait for its [local API docs](http://127.0.0.1:8895/docs), then:

```powershell
python scripts/narrate.py --input examples/scene.txt --output outputs/scene.wav
```

Listen to the WAV. The release test verified functional narration and WAV structure. For three matched Kokoro/Voxtral clips, local speech-to-text and a listening page, follow [SPEECH-WINDOWS.md](SPEECH-WINDOWS.md). Stop it with:

```powershell
docker compose --profile voice stop kokoro
```

## 8 LM Studio and Whisper

LM Studio stays a Windows desktop app. Install it from its publisher, load an appropriate GGUF and unload it before image generation. No Windows GUI app is packed inside this Linux container. The article's prompt comparison used Qwen3.8 27B Q4_K_M and an installed Gemma baseline.

Whisper is an optional [separate native-Python workflow](WHISPER-WINDOWS.md). It is not included in this first Docker profile, and no all-in-one stack is claimed. This keeps the public starter focused on one reproducible image plus optional speech.

## Stop and recover

```powershell
docker compose stop comfyui
docker compose --profile voice stop kokoro
```

These commands stop only this project's services and retain the files. The dated validation links the resolved packages, exact model hashes and image identity. Keep new receipts when reproducing the examples.

If Windows sees the GPU but WSL reports no adapter, save work before a WSL/Docker restart: it closes Linux sessions and interrupts containers. Our workstation required that recovery once. Do not treat a restart as proof of success; repeat the GPU calculation afterward. No global reset or deletion command is included here.
