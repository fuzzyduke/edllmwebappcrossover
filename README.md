# ED-LLM Web App Crossover

## Overview
This repository contains a modular Python application built on **Gradio** that acts as a secure, offline, multi-modal orchestrator powered primarily by the local `gemma4:26b` model via Ollama. 

## Core Capabilities
The interface is structured into discrete tabs handling various AI generation pipelines:
1. **Chat UI & Multimodal PDF Engine**: Intercepts PDF documents natively, extracting textual context and injecting it into the prompt pipeline for analysis.
2. **Text → Images**: Dual-mode engine designed to generate single concept images or sequential storyboards orchestrated by Gemma 4. (Placeholder hooks for Quantized SD 1.5).
3. **Text → Video**: Deep multi-step workflow defined in our [Pipeline Architecture Document](docs/TEXT_TO_VIDEO_PIPELINE.md). Gemma 4 acts as a Scene Planner, passing constrained JSON through a Normalizer before arriving at our local beat-driven rendering engine.
4. **Lip-Sync Architectures**: UI handling dual-intake (Image + Audio) targeted for Wav2Lip or SadTalker integrations.
5. **Living Artifacts / Workflow Automation**: (Future Scope) Dynamically routing logic chains through CLI commands, Obsidian, and Memory loops.

## System Requirements
- **Python 3.10+**
- **Ollama** installed locally with `gemma4:26b` running on port `11434`.
- Run frontend: `python app.py`

*(Note: Heavy visual models like Diffusers/FFmpeg are deliberately decoupled locally right now to preserve GPU flexibility until targeted.)*
