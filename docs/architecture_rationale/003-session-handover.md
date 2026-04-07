# Architecture Rationale: 003 - Session Learnings & AI Handover Context

## Purpose
This document serves as a critical handover file for any future AI agent or developer continuing development on the `edllmwebappcrossover` repository. It contains extremely important technical decisions, operational insights, and implementation workflows discovered during the initial build out.

## 1. Technical Stack & Architectural Shift
* **Decision**: Transitioned from a React+Vite frontend down to a pure Python stack utilizing **Gradio**.
* **Rationale**: Gradio's `ChatInterface` instantly provided a production-ready chatbot layout with native streaming and multimodal (file upload) components natively. Trying to implement Python-based ML capabilities or backend proxying on top of a React stack proved too over-engineered for the current MVP scope.
* **Implementation Workflow**: All development now focuses entirely on `app.py` and tracking dependencies via `requirements.txt`. There is no node/npm build step.

## 2. Gradio 6.x Schema & Silent Failures
* **Decision**: Custom schema unification in `predict(message, history)`.
* **Rationale/Learning**: Gradio version 5.x and 6.x fundamentally changed the data schema of the `history` and `message` parameters, especially when `multimodal=True` was activated. Instead of returning tuples, Gradio returns a list of dictionaries with `"role"` and `"content"` keys. 
* **Crucial Note**: If the backend unpacking fails, Gradio handles the exception internally. The frontend UI simply shows an empty message bubble or hangs, creating a "silent failure".
* **Implementation Workflow**: The backend `app.py` script now has strict, backwards-compatible parsing that dynamically checks `if isinstance(item, dict):` versus tuples to safeguard the Ollama `messages` payload formatting. **Future AIs must log directly via `print()` inside the payload builder to diagnose missing chat responses!**

## 3. Streaming and Hardware TTFT (Time-To-First-Token)
* **Decision**: Local model `gemma4:26b` streams outputs via `requests.iter_lines()`.
* **Rationale**: Because the stakeholder utilizes local 17GB models offloaded to local CPU/GPU compute, **Time-to-First-Token evaluation takes upwards of 3 to 4 minutes without errors.**
* **Crucial Note**: If the Gradio UI displays `queue: 1/1 | 180s`, *it is not stuck*. It is waiting on `requests.post(stream=True)` to yield the first response byte from Ollama. The next AI must **never** assume the prompt pipeline is broken if the inference takes multiple minutes.

## 4. Multimodal PDF Parsing vs Context Limits
* **Decision**: Utilize pure-Python `pypdf` for local extraction, injecting text directly into the chat prompt string.
* **Rationale**: Required zero system-binary installations.
* **Crucial Note / Risk**: There is currently no Vector Database or Retrieval-Augmented Generation (RAG) chunking pipeline. The entire PDF content is dumped into the system prompt. Because local models have hard ceiling token context boundaries and processing scales exponentially, uploading textbooks will OOM (Out Of Memory) crash the local model.
* **Implementation Workflow**: For future phases, if the system requires heavy multi-document handling, the next AI should implement LangChain/LlamaIndex chunking and vector storage (e.g., ChromaDB or FAISS) to gracefully scale the context.

## 5. Performance Timing
* **Decision**: Measured end-to-end response evaluation timing.
* **Rationale**: Due to the severe lag of large models, `app.py` natively stops the clock when `{"done": true}` is captured from the stream and renders `*(⏱️ Response time: \_\_s)*` into the UI block so the user explicitly sees the benchmark footprint.

## 6. Modular Tab UI
* **Decision**: Refactored the layout into a discrete Tabbed system using `gr.Tabs`.
* **Rationale**: As the feature wishlist grew, cramming capabilities into a single chat window became restrictive. The UI is now broken out into 'Chat', 'MD', 'Repos', 'CLIs', 'MCP', and 'About' pages. The new tabs act as placeholders for the next AI agent to populate independently.

## 7. Upcoming / Wishlist Features (Future Scope)
* **Living Artifacts / Action Interfaces**: The system must eventually break free of standard text loops. Code, line graphs, and JSON logic should render natively in a separate pane without reloading the page.
* **Non-Text Communication**: Integrating Voice Input/Transcription directly to the system.
* **Tool Orchestration Layer**: Establishing `.md` driven workflow schemas that chain data cleaning, analytics, and tool CLI commands autonomously.
* **Integrated Logic Hooks**: Connecting Open Code CLI, Obsidian, MEM (Memory) CLI, etc. directly into the framework.
* **Extended Modalities**: Image analysis, CV integrations, Image-to-Video architectures.
