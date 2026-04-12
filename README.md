# ED-LLM Web App Crossover

## Overview
This repository contains a modular Python application built on **Gradio** that acts as a secure, offline, multi-modal orchestrator. It is primarily powered by the local, memory-efficient **`llama3.2:latest` (3B)** model via Ollama to maximize parallel processing and eliminate OOM errors on constrained setups.

## Core Capabilities
The interface is structured into discrete tabs handling various AI generation pipelines:
1. **Chat UI & Multimodal PDF Engine**: Intercepts PDF documents natively, extracting textual context and injecting it into the prompt pipeline for analysis.
2. **Text → Images**: Dual-mode engine designed to generate single concept images or sequential storyboards.
3. **Text → Video (Scene Builder Mode)**: A scalable short-movie workbench supporting hundreds of scenes natively. It features:
   - **Bulk Script Ingestion**: Drop `.txt` or `.json` block scripts to auto-populate the project.
   - **Scene Planning**: Localized `llama3.2` story-planning isolated to the active scene, neutralizing monolithic prompt errors.
   - **Smart Caching Engine**: Project clips are mathematically fingerprinted and saved locally, so massive multi-scene renders skip redundant generations.
   - **Movie Composer**: Uses MoviePy to stitch thousands of cached `mp4` storyboard frames into a deterministic final output.
4. **Lip-Sync Architectures**: UI handling dual-intake (Image + Audio) targeted for Wav2Lip or SadTalker integrations.

## System Requirements
- **Python 3.10+**
- **Ollama** installed locally with `llama3.2:latest` running on port `11434`.
- Run frontend: `python app.py`

*(Note: Heavy visual models like Diffusers/FFmpeg are deliberately decoupled locally right now to preserve GPU flexibility until targeted.)*
