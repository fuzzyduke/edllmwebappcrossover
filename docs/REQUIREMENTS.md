# Project Requirements

This document tracks all formal requirements for the `edllmwebappcrossover` project.

## Phase 1 Requirements
1. **Core Functionality**: Create a simple chat webpage to interface with the local `gemma4:26b` model.
2. **Tech Stack**: Use `Gradio` to power the UI application.
3. **Backend Communication**: Communicate with the local Ollama backend instance.
4. **Documentation**: Maintain a track record of architectural decisions and system design rationales in dedicated documents.

## Phase 2 Requirements
1. **Multimodal File Uploads**: Expand the UI to process document attachments alongside standard text.
2. **PDF Parsing**: Locally extract text from uploaded PDF files and inject it directly into the prompt context for language model analysis.

## Phase 3 / Future Wishlist
*(Recorded for the next development sprint / AI Handover)*
1. **Dynamic Living Artifacts**: Render code, graphs, and snippets in an auto-refreshing side-frame.
2. **Native Voice Interface**: Support direct audio input to prompt generation.
3. **Multi-Step Orchestration**: Data pipelines processing tasks natively (ETL).
4. **Third-Party Integrations**: Open Code CLI, Memory CLI, GitHub CLI, Google Workspace CLI, Obsidian.
5. **Tool Modules**: Finance trackers, Job scrapers, Task scrapers, News Daily Digests.
6. **New Modalities**: Image-to-Video generation, and Computer Vision image analysis.
