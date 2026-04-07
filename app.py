import gradio as gr
import requests
import json
import time
from pypdf import PdfReader

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "gemma4:26b"

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
        
    print(f"Incoming message text length: {len(user_text)}")
    
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
    print("Payload to Ollama:", messages)
    
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
                    print("RAW LINE:", decoded_line)
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

# Optional dark theme tweaks for premium feel
theme = gr.themes.Soft(
    primary_hue="purple",
    secondary_hue="indigo",
).set(
    body_background_fill="*neutral_950",
    body_text_color="*neutral_50",
    border_color_primary="*neutral_800",
    background_fill_secondary="*neutral_900"
)

with gr.Blocks(theme=theme) as demo:
    with gr.Tabs():
        with gr.Tab("Chat"):
            gr.ChatInterface(
                fn=predict,
                multimodal=True,
                title="Gemma4 Local Intelligence",
                description="Secure, local chat interface powered by Gradio and Ollama.",
                examples=["What can you do?", "Write a python script to read a file."],
            )
            
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
            ## About Gemma4 Local Intelligence
            This application serves as a completely offline, fast, and secure interface bridging you to local logic.
            
            ### Current Capabilities
            - **Conversational Intelligence**: Engage directly with the locally hosted `gemma4:26b` model off-grid.
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
    demo.launch()
