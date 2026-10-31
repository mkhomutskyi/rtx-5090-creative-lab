# H3 Paris example

Five fictional AI-generated Microduck scenes: cafe, bakery, Seine, flowers and Eiffel Tower. The stills were generated locally with FLUX.2 Klein9B KV FP8,4steps,CFG1, using reference conditioning. They are not photographs of a real robot visit to Paris.

Animate them with the commands in [the H3 guide](../../docs/h3/README.md). Each scene has a matching motion prompt in prompts/. The exact still-generation prompts are in still-prompts.json. The original reference photo is not redistributed; obtain suitable reference material yourself to recreate the still stage. The included stills are sufficient for the H3 animation example.

Music and robot-design credits are in CREDITS.txt. The full music file is not bundled. Download the chosen track from its creator and follow its licence when sharing. MiniMax and FLUX model licences remain separate from the repository's source-code licence.

Recorded H3 animation times at832x512:112.7,56.3,60.4,58.3 and58.4seconds. Each source clip124frames at24fps. First-run loading and later warm runs differ. Five clips plus transitions produce23.8s. Prompt wording describes intended motion; inspect the actual output rather than assuming every instruction was followed.
