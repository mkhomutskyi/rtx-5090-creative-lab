# H3 companion validation —30 October2026

The local candidate branch is codex/h3-medium-companion. Nothing was pushed or published in this validation pass.

Passed:
- Python compilation of download_h3_models.py, run_h3.py, assemble_h3.py and serve_h3.py.
- Standalone H3 Compose configuration validation.
- Six-file existing model size verification against docs/h3/models.json. The underlying weights had already passed published SHA256 checks during original installation. The new downloader was not used to repeat44GB of downloads.
- A separate service on localhost8196 used the existing immutable runtime image and read-only verified weights. Original H3 and image services remained stopped.
- The documented run_h3.py command uploaded the included cafe image, submitted a fresh draft workflow, waited and downloaded a nonempty MP4. Elapsed112.553s. Output832x512,124frames,24fps,5.1667s;32kHz stereo audio. FFmpeg decoded the full file without error. Run receipt retained outside source control under outputs/.
- Preview and quality profile dry runs parsed successfully. These new helper profiles were not rerendered; their underlying graphs came from previously qualified runs.
- assemble_h3.py joined the five already-generated public example clips with0.5s crossfades and the licensed Precious Memories excerpt. Output23.8333s video; audio duration matched within0.1s. Full-file decode passed.
- /system_stats responded after generation. The temporary service was then stopped.

Not claimed:
- A clean Windows/driver install or a new Docker image rebuild in this pass.
- A repeated model download or new independent SHA256 scan of all44GB.
- A universal fastest configuration, subjective music review or perfect visual consistency.
- Public GitHub availability of this candidate, hosted final video or a published Medium article.

The build recipe pins the existing qualified ComfyUI source and Python packages. Before calling the setup a tested public clone, publish/review the candidate and validate that clone. No personal media, private correspondence or original robot reference photograph is included.
