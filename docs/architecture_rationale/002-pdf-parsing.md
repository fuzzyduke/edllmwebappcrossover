# Architecture Rationale: 002 - PDF Parsing

## Context
The user requested the ability to upload a PDF document and have the system parse it to generate prompt context based on the extracted text.

## Decision
We activated the `multimodal=True` capability of Gradio's `ChatInterface` and integrated `pypdf` into the backend logic.

## Rationale
1. **Gradio Multimodal Support**: By setting `multimodal=True`, Gradio natively generates an upload dialog box UI with zero custom frontend code. It handles file staging securely and passes out an absolute path to the uploaded file.
2. **PyPDF Choice**: `pypdf` is a deeply established, lightweight, pure python library capable of cleanly pulling strings from PDF text buffers without relying on unsecure local binaries or bloated dependencies (unlike PyMuPDF or Tesseract).

## Constraints
Gemma4:26b is a thick local model with a context window ceiling. Injecting an un-chunked PDF stream into the system prompt risks out-of-memory errors for massive 200+ page books. Since we don't have RAG (Retrieval Augmented Generation) configured yet via a vector database, this feature is explicitly scoped for reasonably small documents. 
