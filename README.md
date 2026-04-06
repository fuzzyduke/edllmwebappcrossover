# edllmwebappcrossover

Discover apps/pages created with LLM/SLM that interact with a page to sync value.

## About

This repository is a collection of experimental web applications and pages where LLM/SLM agents interact with browser pages to synchronize values in real-time across different contexts (tabs, windows, devices).

## Goals

- Explore real-time state synchronization between LLM-driven interfaces
- Build demo apps showcasing cross-page value sync
- Document patterns for LLM-to-page interaction
- Create Gradio-based tooling powered by local LLMs

## Stack

- **Gradio** — UI framework for LLM-powered tools
- **Ollama** — Local LLM inference (gemma4:e4b)
- Vite + React + TypeScript (future web apps)
- BroadcastChannel API for cross-tab sync
- WebSocket for cross-device sync

## Devlog

### 2026-04-06
- Repository created
- Local Ollama setup: pulled `gemma4:e4b`, removed `gemma4:26b`
- VPS OpenClaw upgraded from `2026.3.24` → `2026.4.5`
- Next: Build Gradio-based tooling with local LLM integration

---

*Created and maintained with AI assistance.*

