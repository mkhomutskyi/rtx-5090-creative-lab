# Models and file placement

Run `scripts/Initialize-Lab.ps1` first. Download only what your chosen workflow needs. Large weights stay in the ignored `models` folder. The Compose model mount is read-only while the service runs. Do not copy another application's configuration or overwrite its model files.

## First image with Z-Image Base

Use the model links in the [official Comfy Z-Image workflow](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_z_image.json) and the [Comfy-Org Base model page](https://huggingface.co/Comfy-Org/z_image). Place:

| Relative file | Role |
| --- | --- |
| `models/diffusion_models/z_image_bf16.safetensors` | [Base diffusion model](https://huggingface.co/Comfy-Org/z_image/resolve/main/split_files/diffusion_models/z_image_bf16.safetensors) |
| `models/text_encoders/qwen_3_4b.safetensors` | [Text encoder](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| `models/vae/ae.safetensors` | [VAE](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |

This is Base, not Turbo. The helper uses 30 steps, CFG 4, shift 3, res_multistep/simple, 1280 by 768, batch 1. These are the settings used in the dated article experiment; they are not a guarantee of image quality on a new installation.

```powershell
python scripts/check_models.py --workflow zimage
```

Presence alone does not establish model identity, license acceptance, runtime compatibility or a successful generation. Compare your SHA-256 hashes with the dated qualification record.

## Optional image-reference workflow

The [official FLUX Klein KV image-edit template](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_flux2_klein_9b_kv_image_edit.json) identifies the exact publisher files. The supplied helper expects:

- `models/diffusion_models/flux-2-klein-9b-kv-fp8.safetensors`: [publisher file](https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-kv-fp8/resolve/main/flux-2-klein-9b-kv-fp8.safetensors)
- `models/text_encoders/qwen_3_8b_fp8mixed.safetensors`: [publisher file](https://huggingface.co/Comfy-Org/flux2-klein-9B/resolve/main/split_files/text_encoders/qwen_3_8b_fp8mixed.safetensors)
- `models/vae/flux2-vae.safetensors`: [publisher file](https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors)

Review the exact checkpoint's terms and complete any publisher account/license step yourself. No gated download or acceptance is automated. Upload your own robot reference through the local ComfyUI interface as `robot-reference.png`, then run the optional reference example. Original third-party robot photos are not distributed here.

Model weights are reader-managed downloads. The release qualification reused existing files read-only; it did not test downloading them onto a new machine.

Download links were checked against the official Comfy templates on 24 October 2026. Review each model card before downloading. The text encoder and VAE are shared with Turbo, but the diffusion file above is Base. Start with about 20 GB of Base weights, plus container layers and room for outputs; the optional reference files add more.

To compare a local file with the release's SHA-256 record:

```powershell
Get-FileHash models/diffusion_models/z_image_bf16.safetensors -Algorithm SHA256
```

## Optional Voxtral speech weights

Follow [SPEECH-WINDOWS.md](SPEECH-WINDOWS.md) for the pinned download helper, exact model revisions and separate TTS/STT profiles. The TTS checkpoint uses CC BY-NC 4.0, while the selected STT checkpoint uses Apache 2.0. They are dated baselines, not Voxtral 3. The hash record is [model-sha256.txt](model-sha256.txt).
