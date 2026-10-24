# Whisper transcription on Windows

Goal: transcribe a short recording into text and subtitles with local GPU execution. This is a documented candidate installation; run the checks below before treating it as working on your machine.

## Prerequisites

Install Python 3.11 with its launcher from [Python](https://www.python.org/downloads/windows/). Install FFmpeg using a method linked by the [official Whisper README](https://github.com/openai/whisper#setup). If you already use Chocolatey, its documented command is `choco install ffmpeg`; if you already use Scoop, it is `scoop install ffmpeg`. Otherwise follow [FFmpeg's Windows download links](https://ffmpeg.org/download.html#build-windows) and add the extracted `bin` directory to your user PATH. Reopen PowerShell.

```powershell
py -3.11 --version
ffmpeg -version
```

Success: both commands print versions. Do not substitute a different Python just because `python` resolves to it.

## Create a separate environment

Run from the companion repository root:

```powershell
py -3.11 -m venv .venv-whisper
.\.venv-whisper\Scripts\python.exe -m pip install --upgrade pip
.\.venv-whisper\Scripts\python.exe -m pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cu128
.\.venv-whisper\Scripts\python.exe -m pip install openai-whisper
.\.venv-whisper\Scripts\python.exe -m pip check
```

The torch command selects an official [Windows CUDA 12.8 build](https://pytorch.org/get-started/previous-versions/) rather than claiming this is the newest release. Whisper is not pinned in this draft. After clean validation, record and lock the complete dependency set. Keep these packages separate from LM Studio and ComfyUI's environments.

## Prove the GPU can perform an operation

```powershell
.\.venv-whisper\Scripts\python.exe -c "import torch; assert torch.cuda.is_available(), 'CUDA unavailable'; x=torch.ones(4, device='cuda'); print(torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0), (x+x).cpu().tolist())"
```

Success: the device name is your RTX 5090 and the result contains four `2.0` values. GPU detection without this calculation is a weaker check. If you get `no kernel image`, the installed runtime/build is incompatible; do not quietly fall back to CPU and label it GPU success.

## Transcribe

Record yourself saying the original scene idea in Windows Sound Recorder. Export or save it as `inputs\idea.m4a`. Create the `inputs` folder if needed. Keep recordings private.

```powershell
.\.venv-whisper\Scripts\whisper.exe inputs\idea.m4a --model small.en --device cuda --language en --task transcribe --output_format all --output_dir outputs\transcript
```

The first run downloads weights. `small.en` is a conservative English starter. Use a multilingual model for other languages. Whisper's upstream model table describes larger choices and approximate memory needs; a larger model does not automatically improve your specific recording.

Success: readable TXT and subtitle files that match the recording. Listen while reviewing names and timing. The command explicitly requests CUDA. Close the process after completion to release its GPU allocation.
