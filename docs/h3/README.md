# H3 on Windows: the tested RTX5090 configuration

This guide uses Docker Desktop with its WSL2 backend and NVIDIA GPU access. The measured computer had an RTX5090 with32GB VRAM and64GB system RAM. A new Windows installation and different GPU/driver stacks were not tested. The optional native ComfyUI Portable route is linked below, but is not the source of these measurements.

## Before downloading

Read the [H3 licence](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE). Obtain any authorization required for your country and intended use through the [official request form](https://platform.minimax.io/h3-license). This repository grants no model rights. Do not submit application details here. Model weights, credentials and personal files are not included.

Install Git, Python3.11+ and Docker Desktop with WSL2/GPU support. From PowerShell, confirm `nvidia-smi` works and Docker Desktop runs Linux containers. Use a separate folder and leave other working AI installations unchanged. Allow disk space for44GB of H3 files, the Docker image, build cache and outputs;70GB free is not a guarantee of sufficient space.

## Get the companion

```powershell
git clone https://github.com/mkhomutskyi/rtx-5090-creative-lab.git
cd rtx-5090-creative-lab
```

The H3 companion includes the model manifest, native workflows, generated example images and helper scripts. See [VALIDATION.md](VALIDATION.md) for the tested scope and remaining limits.

## Models and runtime

```powershell
python scripts/download_h3_models.py --accept-license
docker compose -f compose.h3.yaml config --quiet
docker compose -f compose.h3.yaml build
docker compose -f compose.h3.yaml up -d
```

The downloader obtains six public Comfy-Org files and checks every new download's SHA256. It resumes .part files and preserves existing files on mismatch. `--accept-license` records your acknowledgement; it does not obtain permission. For an existing model folder:

```powershell
python scripts/download_h3_models.py --models-dir models --verify-only --hash-check
```

The manifest is [models.json](models.json). The build pins the same ComfyUI source and Python packages used by the existing companion runtime. H3 starts at http://127.0.0.1:8193. Another local service using that port must be stopped or use a different H3_PORT. Only one large GPU model should be active while running these profiles.

H3 selected profile: INT8 ConvRot pruned FL2VA; Qwen3-VL32B NVFP4 AWQ encoder; INT8 videoVAE; FP32 audioVAE. ComfyKitchen attention, dynamicVRAM, memory mapping, disabled pinned memory, disabled asynchronous offload and disabled Comfy compiler. Container34GiB RAM/42GiB RAM+swap,12CPU. The900-second idle supervisor releases models when the queue is empty; the UI remains open. Closing the browser does not stop the container.

## Generate one clip

```powershell
python scripts/run_h3.py --image examples/h3-paris/images/01-cafe.png --prompt-file examples/h3-paris/prompts/01-cafe.txt --profile draft --width 832 --height 512 --seed 42 --output outputs/01-cafe.mp4
```

The helper uploads only the supplied image to the local service, submits one workflow, waits and downloads the MP4. It refuses an initially busy queue and existing output filename. A `.run.json` beside the MP4 records the exact graph,seed,history and elapsed time. Do not expose this unauthenticated ComfyUI service publicly.

Profiles: draft=eight-step Turbo; preview=matching768p four-step Turbo; quality=twenty steps without Turbo. Quality is a comparison profile, not a universal visual ranking. UI/API graphs are in workflows/h3/. Use multiples of32 for width/height. The measured clips contain124frames at24fps, about5.17s. Larger dimensions or longer duration require separate memory and quality tests.

## Generate the five examples

```powershell
$scenes = '01-cafe','02-bakery','03-seine','04-flowers','05-eiffel'
foreach ($scene in $scenes) {
  python scripts/run_h3.py --image "examples/h3-paris/images/$scene.png" --prompt-file "examples/h3-paris/prompts/$scene.txt" --width 832 --height 512 --seed 42 --output "outputs/$scene.mp4"
  if ($LASTEXITCODE -ne 0) { throw "Generation failed: $scene" }
}
```

The included stills were generated locally with FLUX.2 Klein9B KV FP8,4steps,CFG1 and native reference conditioning. Exact still prompts are included. The reference photograph and FLUX weights are not redistributed. These H3 commands can use the included images without installing an image model. They do not reproduce the still-generation stage automatically.

## Add one continuous soundtrack

Download your chosen track from its creator. Put it in inputs/. For this example the track is [Precious Memories by Shane Ivers](https://www.silvermansound.com/free-music/precious-memories), CC BY4.0, with an excerpt starting00:22. Include the credit in your video description or credits; see examples/h3-paris/CREDITS.txt. Music is not bundled.

FFmpeg is included inside the container, so no separate Windows FFmpeg installation is needed:

```powershell
docker compose -f compose.h3.yaml exec h3 python /lab/scripts/assemble_h3.py --clips /opt/ComfyUI/output/01-cafe.mp4 /opt/ComfyUI/output/02-bakery.mp4 /opt/ComfyUI/output/03-seine.mp4 /opt/ComfyUI/output/04-flowers.mp4 /opt/ComfyUI/output/05-eiffel.mp4 --music /opt/ComfyUI/input/precious-memories.mp3 --music-start 22 --output /opt/ComfyUI/output/microducks-paris.mp4
```

This replaces the per-clip generated sound with one full-length music excerpt. It checks that the audio lasts through the film and decode-checks the result. Five clips with0.5s transitions yield about23.8s. Inspect motion as well: a successful render does not prove that all limbs, objects or lettering are correct.

## Finish

```powershell
docker compose -f compose.h3.yaml stop
```

This releases the service while retaining models and files. Restart with up-d. Automatic boot startup is disabled.

## Evidence and limits

Original runtime:13 successful baseline jobs.480p8step104s cold,54–56s fresh prompt,18s cached-conditioning variation.768p4step88s,38s with cached conditioning. Five new832x512 Paris jobs:113s first,56–60s afterward. All timings are from one5090/64GB Windows system; prompt/cache conditions differ. Peak sampled baseline whole-card VRAM31.2GiB.

FastH3 FP4/fused warm480p26s, cold process to first output~214s; retained only as separate experiment. No Spectrum measurement. The local companion helper is separately validated as recorded in VALIDATION.md; do not substitute those numbers for the original bench runs.

Official references: [H3 guide](https://docs.comfy.org/tutorials/video/minimax/minimax-h3), [model files](https://huggingface.co/Comfy-Org/MiniMax-H3), [Windows Portable](https://docs.comfy.org/installation/comfyui_portable_windows). No claim that this is the fastest possible configuration on every machine.
