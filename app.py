import gradio as gr
import requests
import json
import time
from pypdf import PdfReader
import os
import uuid
import scene_planner
import scene_validator
import render_normalizer
import renderer
import video_composer
import help_content
import manual_scene_ui

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3.2:latest"

def predict(message, history):
    start_time = time.time()
    
    # Handle multimodal dictionary
    if isinstance(message, dict):
        user_text = message.get("text", "")
        files = message.get("files", [])
    else:
        user_text = message
        files = []
        
    extracted_text = ""
    for file_info in files:
        file_path = file_info if isinstance(file_info, str) else file_info.get("path")
        if file_path and file_path.lower().endswith(".pdf"):
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    extracted_text += page.extract_text() + "\n"
            except Exception as e:
                print(f"Failed to read PDF {file_path}: {e}")
                
    if extracted_text.strip():
        user_text = f"DOCUMENT CONTEXT:\n{extracted_text}\n\nUSER PROMPT:\n{user_text}"
        
    # print(f"Incoming message text length: {len(user_text)}")
    
    messages = []
    for item in history:
        if isinstance(item, dict):
            raw_content = item.get("content", "")
            if isinstance(raw_content, str):
                messages.append({"role": item.get("role", "user"), "content": raw_content})
            elif isinstance(raw_content, tuple):
                messages.append({"role": item.get("role", "user"), "content": f"[Attached File: {raw_content[0]}]"})
            else:
                messages.append({"role": item.get("role", "user"), "content": str(raw_content)})
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            if isinstance(item[0], str): messages.append({"role": "user", "content": item[0]})
            if item[1] and isinstance(item[1], str): messages.append({"role": "assistant", "content": item[1]})
        
    messages.append({"role": "user", "content": user_text})
    # print("Payload to Ollama:", messages)
    
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True
    }
    
    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True) as response:
            print("Response Headers:", response.headers)
            if response.status_code != 200:
                error_body = response.text
                print("Error status code:", response.status_code, error_body)
                yield f"Error: Received status code {response.status_code} from Ollama. Details: {error_body}"
                return
            
            partial_message = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    # print("RAW LINE:", decoded_line)
                    try:
                        data = json.loads(decoded_line)
                        if "message" in data and "content" in data["message"]:
                            partial_message += data["message"]["content"]
                            yield partial_message
                        
                        if data.get("done"):
                            total_time = time.time() - start_time
                            partial_message += f"\n\n*(⏱️ Response time: {total_time:.1f}s)*"
                            yield partial_message
                            
                    except json.JSONDecodeError:
                        print("JSON decode error on:", decoded_line)
    except requests.exceptions.RequestException as e:
        print("RequestException:", str(e))
        yield f"Error communicating with local model: {e}"

# Premium CSS for high contrast and glassmorphism
css = """
.gradio-container { background: #0b0f19 !important; }
.chatbot .message.user {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    border-radius: 18px 18px 2px 18px !important;
    border: none !important;
}
.chatbot .message.bot {
    background: #1f2937 !important;
    color: #f3f4f6 !important;
    border-radius: 18px 18px 18px 2px !important;
    border: 1px solid #374151 !important;
}
.chatbot .message {
    font-size: 1.05rem !important;
    line-height: 1.6 !important;
    padding: 12px 16px !important;
}
.chatbot .message-row { margin-bottom: 1rem !important; }
/* Smooth streaming feel */
.chatbot .message p { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
"""

theme = gr.themes.Soft(
    primary_hue="purple",
    secondary_hue="indigo",
)

with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.Tab("Chat"):
            gr.ChatInterface(
                fn=predict,
                multimodal=True,
                title="Llama 3.2 Local Intelligence",
                description="Secure, local chat interface powered by Gradio and Ollama (Llama 3.2 3B).",
                examples=["What can you do?", "Write a python script to read a file."],
            )
            

        with gr.Tab("Text → Images"):
            gr.Markdown("### Text → Images Generation")
            img_prompt = gr.Textbox(label="Prompt", placeholder="Enter your visual idea...")
            img_mode = gr.Radio(["Mode A: Simple prompt → single image", "Mode B: Prompt → Gemma 4 generates storyline → sequential multiple images"], label="Mode", value="Mode A: Simple prompt → single image")
            img_engine = gr.Radio(["Local (Quantized SD 1.5 - runs on 2GB GPU)", "Cloud/AI (Fal.ai Flux, Replicate, Together.ai)"], label="Local vs Cloud Selection", value="Local (Quantized SD 1.5 - runs on 2GB GPU)")
            img_btn = gr.Button("Generate Image(s) 🎨", variant="primary")
            img_gallery = gr.Gallery(label="Generated Images")
            
            def mock_generate_image(prompt, mode, engine):
                # Placeholder logic to prove UI works
                return None
            img_btn.click(mock_generate_image, inputs=[img_prompt, img_mode, img_engine], outputs=img_gallery)
            
        manual_scene_ui.create_manual_tab_contents()
        
        with gr.Tab("Lip-Sync Animation"):
            gr.Markdown("### Lip-Sync Animation Generator")
            with gr.Row():
                with gr.Column():
                    lip_image = gr.Image(label="Upload Character Face", type="filepath")
                    lip_audio = gr.Audio(label="Upload Voice Audio (Mic or File)", type="filepath")
                with gr.Column():
                    lip_tool = gr.Radio(["Wav2Lip", "SadTalker"], label="Animation Processing Tool", value="Wav2Lip")
                    lip_engine = gr.Radio(["Local Execution", "Cloud/AI External API"], label="Local vs Cloud Selection", value="Local Execution")
                    lip_btn = gr.Button("Generate Lip-Sync 🗣️", variant="primary")
                    lip_video = gr.Video(label="Lip-Sync Animation Output")
            
            def mock_generate_lipsync(img, aud, tool, engine):
                # Placeholder logic
                return None
            lip_btn.click(mock_generate_lipsync, inputs=[lip_image, lip_audio, lip_tool, lip_engine], outputs=[lip_video])

        with gr.Tab("Simple Text → Simple Video"):
            gr.Markdown("### Simple Concept Animation")
            simple_vid_prompt = gr.Textbox(label="Action Prompt", placeholder="e.g. A basic stick figure waving hello")
            simple_vid_engine = gr.Radio(["Local Concept Drawing (MoviePy / Manim)", "Cloud/AI Advanced Pipeline"], label="Local vs Cloud Selection", value="Local Concept Drawing (MoviePy / Manim)")
            simple_vid_btn = gr.Button("Generate Simple Video 🎞️", variant="primary")
            simple_vid_output = gr.Video(label="Concept Animation Video")
            
            def mock_simple_video(prompt, engine):
                # Placeholder logic
                return None
            simple_vid_btn.click(mock_simple_video, inputs=[simple_vid_prompt, simple_vid_engine], outputs=[simple_vid_output])

        with gr.Tab("MD"):
            gr.Markdown("### MD Module\n*(Feature incoming - Placeholder)*")
            
        with gr.Tab("Repos"):
            gr.Markdown("### Repositories Module\n*(Feature incoming - Placeholder)*")
            
        with gr.Tab("CLIs"):
            gr.Markdown("""### Integrated CLIs
            - GitHub CLI
            - Google Workspace CLI
            - MEM CLI
            - Open Code CLI
            """)
            
        with gr.Tab("MCP"):
            gr.Markdown("### MCP Module\n*(Feature incoming - Placeholder)*")
            
        with gr.Tab("About"):
            gr.Markdown("""
            ## About Llama 3.2 Local Intelligence
            This application serves as a completely offline, fast, and secure interface bridging you to local logic.
            
            ### Current Capabilities
            - **Conversational Intelligence**: Engage directly with the locally hosted `llama3.2` model off-grid.
            - **Document Analysis**: Upload PDF documents into the chat window to extract their contextual data and perform instantaneous analysis.
            
            ### Upcoming / Wishlist Features
            - **Integration of Open Code CLI**
            - **Integration of Memory CLI**: To store context and data for longer periods of time.
            - **Integration of Obsidian**: To automatically keep notes and organize generations.
            - **Audio to Text Translation**: Transcription module where users speak directly into the microphone.
            - **Image Analysis (Computer Vision)**: Users upload an image and the AI contextually analyzes and speaks about it.
            - **Data Visualization**: CSV ingestion leading point-to-point data filtration workflows and visual analytics.
            - **Daily News Digest**: Connects dynamically to APIs to provide custom daily news tailored to the user.
            - **Personal Finance Tracker**
            - **Job Application Helper**
            - **Task Application Helper**: Autonomous scraper that looks on websites for tasks you can do.
            - **Text/Image to Video Generation**
            - **Goals Planner**: AI-assisted weekly goal tracking, follow-ups, and step-by-step action breakdowns.
            - **Custom AI Workflows**: Dynamic orchestration layer for multi-step tasks (e.g., data cleaning -> processing -> visuals). Could likely be structured utilizing `.md` files to schema logic blocks.
            - **Native Voice Interface**: Direct speech-to-system interactions replacing the need for chat typing.
            - **Dynamic Living Artifacts**: A dedicated, auto-refreshing UI frame separate from the main chat. If the AI designs a system model, JSON snippet, or line graph, it cleanly renders inside the UI in real-time without a page refresh.
            - *Targeted PDF Analysis (RAG)*
            """)

if __name__ == "__main__":
    demo.launch(theme=theme, css=css, server_name="0.0.0.0", server_port=7860)
