# Architecture Rationale: 001 - Tech Stack Shift to Gradio

## Context
The repository was initially set up as a Vite + React web application. The initial request was for "a simple page with a chat to gemma4 model". 

## Decision
We pivoted the tech stack entirely from React/Vite to Python utilizing the `Gradio` library.

## Rationale
1. **Developer Velocity**: Gradio's `ChatInterface` provides an instant, production-ready LLM interaction UI out-of-the-box. It significantly reduces the amount of frontend code (HTML/CSS/JS) needed to be written and maintained.
2. **Ecosystem**: Python is the lingua-franca of AI. Transitioning to a Python stack natively allows seamless integration of future machine learning libraries, vector databases, and complex orchestration scripts without relying on an external Node bridge or API.
3. **Requirement Compliance**: The project stakeholder explicitly defined Gradio as a requirement.

## Constraints & Tradeoffs
- Switching to Python means we lose out-of-the-box support for deep frontend CSS customization that React provides, however, Gradio supports custom themes and CSS injection which should suffice for rapid MVP needs.
