# What is ours and what is upstream

| Component | Responsibility | Included here |
| --- | --- | --- |
| Build and deployment glue | Our Dockerfile, Compose setup and folder preparation | Source/configuration |
| Example orchestration | Our small API clients, prompts and workflow graphs | Source and original text |
| ComfyUI | Third-party open-source image engine | Fetched from its public repository at a pinned commit during build |
| PyTorch and CUDA runtime packages | Upstream GPU execution libraries | Installed from the official PyTorch CUDA wheel index during build |
| Z-Image / FLUX weights | Third-party image models | No weights; publisher links and filenames only |
| LM Studio | Third-party desktop app for local LLMs | Not redistributed or placed in a Windows container |
| Qwen / Gemma / other LLMs | Third-party language models | Not redistributed; install in LM Studio separately |
| Kokoro | Third-party speech model | Optional service uses the upstream Kokoro-FastAPI image |
| Kokoro-FastAPI | Third-party community API wrapper | An optional upstream image pinned by digest |
| Voxtral TTS / STT | Third-party speech models | Pinned download helper; no weights |
| vLLM-Omni | Third-party speech runtime | Upstream image pinned by digest; adapted pipeline retains Apache 2.0 |
| Docker Desktop / WSL 2 | Windows container host | Not redistributed |

Our setup code, original prompts and documentation are licensed under [MIT](../LICENSE). The adapted Voxtral pipeline retains Apache 2.0; see [third-party notices](../THIRD_PARTY_NOTICES.md). ComfyUI is fetched separately and retains its upstream GPL license. Model weights, PyTorch, LM Studio, Docker Desktop and the Kokoro image retain their own terms; our license does not relicense any of them. See [ComfyUI](https://github.com/Comfy-Org/ComfyUI), [PyTorch](https://pytorch.org/), [Kokoro](https://github.com/hexgrad/kokoro), [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI), and [LM Studio](https://lmstudio.ai/).

Docker builds and model downloads need internet access. The selected local inference paths do not require a hosted generation API or API key. A cloud node or connected LM Studio tool would change that boundary; none is configured by this candidate. No NVIDIA or robot-manufacturer endorsement is implied.

## MiniMax H3 companion

See [the H3 licensing notes](h3/LICENSING.md). H3 weights are not bundled or licensed under this repository's code licence. Readers must obtain applicable rights themselves. The generated Paris example separately credits Microduck's design reference and the music creator. Full music recordings and original reference photography are not redistributed.
