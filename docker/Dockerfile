FROM python:3.12-slim-bookworm@sha256:6a0e06f5ba0b373d051aabd3fffb9b873f27f9a2a3a14bcbe37dee6f0e3bbc70
ARG COMFYUI_COMMIT=b0b743566f65daafc423b4fea8a2fbda94b3384a
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates libgl1 libglib2.0-0 libgomp1 ffmpeg && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --upgrade pip && python -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cu130
RUN git init /opt/ComfyUI && cd /opt/ComfyUI && git remote add origin https://github.com/Comfy-Org/ComfyUI.git && git fetch --depth 1 origin ${COMFYUI_COMMIT} && git checkout --detach FETCH_HEAD && test "$(git rev-parse HEAD)" = "${COMFYUI_COMMIT}"
COPY docker/constraints.txt /opt/constraints.txt
COPY docker/resolved-packages.txt /opt/resolved-packages.txt
RUN python -m pip install -r /opt/ComfyUI/requirements.txt -c /opt/constraints.txt -c /opt/resolved-packages.txt && python -m pip check && python -m pip freeze > /opt/build-requirements.txt
# Triton compiles a small CUDA host helper during the first image job.
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ComfyUI
EXPOSE 8188
CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188", "--disable-all-custom-nodes", "--preview-method", "none", "--cache-ram", "8", "12", "--mmap-torch-files", "--enable-dynamic-vram", "--fast-disk", "--disable-pinned-memory", "--disable-async-offload", "--use-pytorch-cross-attention"]
