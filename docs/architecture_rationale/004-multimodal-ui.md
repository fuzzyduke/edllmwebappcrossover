# Architecture Rationale: 004 - Multimodal UI Structural Shell

## Purpose
This document logs the addition of four completely new, standalone multimodal generation UI tabs within the core Gradio `app.py` script. The purpose is to prepare the interface for heavy-duty content architectures (stable diffusion, video generation, lip-syncing) without disrupting the core Gemma 4 text capabilities.

## What Was Implemented

The Gradio frontend has been significantly upgraded with four new capabilities replacing the previous placeholders:

1. **Text → Images Tab**
   - Built a prompt input with dual radio buttons for **Modes** ("Single Prompt" vs. "Gemma Storyboard Generation") and **Execution Contexts** (Local vs. Cloud API).
   - Hooked up to a standalone gallery display.

2. **Text → Video Tab (Scene-by-Scene)**
   - Constructed a complex two-step workflow constraint: A button targets *local* Gemma 4 explicitly to generate an editable layout script before allowing the structural generation.
   - Outputs feed gracefully into a final `gr.Video` loop block. 

3. **Lip-Sync Animation Tab**
   - Added `gr.Image` and `gr.Audio` twin upload components.
   - Introduced dynamic radio checks allowing switching between theoretical Wav2Lip and SadTalker engines running either local or out-of-band via Cloud APIs.

4. **Simple Text → Simple Video Tab**
   - Created a basic concept prompt aimed at extremely stripped down local renderers like MoviePy or Matplotlib to bypass the VRAM footprint of tools.

## What Needs To Be Addressed (Future Work)

**The entire computational engine backing these UI panels has been mocked via Python "dummy" functions.** 
We deliberately avoided downloading the multi-gigabyte models required for these pipelines. In the upcoming phase, the following robust heavy installations will be demanded:

1. **Local Image Orchestration**: Downscale and implement `diffusers` PyTorch configurations for the 2GB Quantized SD 1.5 logic bounds.
2. **Local Video Concepts**: Install system-level ImageMagick/FFmpeg drivers alongside Python `moviepy/manim` wrappers to begin programmatic stick-figure generation.
3. **Local Lip-Syncing**: Import the Wav2Lip inference architectures, clone their repository paths locally, and orchestrate the audio/video processing chunk hooks.
4. **Cloud Hook Integrations**: Add configurable `.env` integrations and exact API requests connecting Fal.ai, Replicate, Together.ai, Magic Hour, etc., mapped conditionally to the "Cloud/AI" UI toggle variables.
