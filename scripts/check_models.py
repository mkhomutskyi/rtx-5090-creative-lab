"""Check model-file presence only; this does not prove inference compatibility."""
import argparse
from pathlib import Path
import sys

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--models', type=Path, default=Path('models'))
p.add_argument('--workflow', choices=['zimage','flux-reference'], default='zimage')
a = p.parse_args()
required = {
    'zimage': ['diffusion_models/z_image_bf16.safetensors','text_encoders/qwen_3_4b.safetensors','vae/ae.safetensors'],
    'flux-reference': ['diffusion_models/flux-2-klein-9b-kv-fp8.safetensors','text_encoders/qwen_3_8b_fp8mixed.safetensors','vae/flux2-vae.safetensors'],
}[a.workflow]
missing = []
for name in required:
    file = a.models / name
    if file.is_file() and file.stat().st_size > 0:
        print('FOUND', name)
    else:
        print('MISSING', name)
        missing.append(name)
sys.exit(1 if missing else 0)
