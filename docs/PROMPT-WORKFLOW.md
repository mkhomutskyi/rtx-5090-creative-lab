# Better prompts, then better pictures

The local comparison on 24 October 2026 completed 45 text responses across 21 screened configurations and four finalists. Qwen3.8 27B Q4_K_M was the most useful recent prompt-writing default in that small sample; the installed Gemma 4 26B baseline was a fast alternative. These are dated observations from one workstation and one reviewer, not a general model ranking. No new LLM downloads were needed.

Good wording did not guarantee a faithful robot. Four matched Z-Image renders used the first Qwen and Gemma cover/nap prompts with the same image settings and task seeds. Both writers produced images with changed robot construction. Gemma staged those scenes a little better; that is too small a sample to declare an image-quality winner.

## Try this in native LM Studio

Load an appropriate model, then give it a visible contract before asking for a polished paragraph:

> Write one image-generation prompt. Return only the prompt. Put physical construction and spatial relationships first. Preserve the exact subject count, positions, style, colors and exclusions. Do not invent props or technical specifications.
>
> Scene: two compact bipedal robots, one on either side of a stationary desktop PC. Each robot has a camera head, exposed mechanical neck, compact hip, two jointed legs and broad feet. No arms, antennae or wheels. Flat editorial ink illustration on an edge-to-edge white background. Blue, black and yellow. Clear empty space above the subjects for a title that will be added later. Separate picture and waveform icons. No text, letters, logos or watermarks.

Check its answer against each requirement. Save the answer, unload the LLM to free GPU memory, and place the prompt into a new copy of `examples/scene-prompts.json`. Use a new job name and receipt folder.

After looking at the actual image, ask for a focused revision:

> Keep [the parts that worked]. The image got [visible detail] wrong. Change [specific construction or relationship]. Do not add new subjects or disguise the defect with decoration. Return only the revised prompt.

## Compare one change at a time

1. Save the starting prompt, seed, settings and image.
2. Change only the positive prompt for the first comparison. Keep the seed and image settings fixed.
3. Inspect counts, anatomy, action, composition, colors and accidental lettering.
4. If shape still drifts, try the separately documented reference workflow. Use an image you have permission to use.
5. Treat model changes, reference conditioning and finishing edits as separate experiments. Keep earlier versions.
6. Add the actual heading in a layout editor and check the cover at thumbnail size.

In the article's refinement example, a concrete text revision helped, but adding a reference in a separate FLUX comparison preserved the robot mechanism more closely. A later edit adjusted the colors and layout. Changing the model and adding a reference together cannot establish which change caused an improvement. Longer prompts, extra steps and higher resolution were not independently proven to improve quality here.

The public starter uses an original Moon repair-shop scene. It includes no manufacturer photos or generated celebrity pictures. The scripts accept your own prompts and local references.
