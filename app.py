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

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "gemma4:e4b"

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
                title="Gemma4 Local Intelligence",
                description="Secure, local chat interface powered by Gradio and Ollama.",
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
            
        with gr.Tab("Text → Video"):
            with gr.Row():
                with gr.Column(scale=3):
                    gr.Markdown("### 🎞️ Text → Video Generator")
                    vid_prompt = gr.Textbox(
                        label="Describe your story", 
                        placeholder="e.g. A kid wakes up sleepy, drinks milk, then runs outside full of energy...",
                        lines=3
                    )
                    with gr.Row():
                        vid_style = gr.Dropdown(
                            ["stick_figure", "geometric", "storyboard"], 
                            label="Visual Style", 
                            value="stick_figure"
                        )
                        vid_scene_count = gr.Slider(1, 5, step=1, label="Target Scene Count", value=3)
                    
                    gr.Markdown("#### Sample Prompts (Click to use)")
                    examples = [
                        "A girl plants a seed, waters it, then smiles when a flower blooms.",
                        "A boy studies late, drinks water, then confidently takes a test.",
                        "A robot wakes up, charges its battery, then helps clean the room.",
                        "A child eats breakfast, gains energy, then plays basketball."
                    ]
                    for ex in examples:
                        gr.Button(ex, variant="secondary", size="sm").click(lambda x=ex: x, None, vid_prompt)

                    vid_generate_btn = gr.Button("🚀 Generate Concept Video", variant="primary")
                
                with gr.Column(scale=2):
                    with gr.Accordion("How it Works 💡", open=False):
                        gr.Markdown(help_content.HELP_TEXT)
                    
                    vid_status = gr.Textbox(label="Creation Status", interactive=False, value="Ready")
                    vid_status = gr.Textbox(label="Creation Status", interactive=False, value="Ready")
                    
                    gr.Markdown("#### Scene Previews")
                    with gr.Row():
                        vid_previews = []
                        for i in range(5):
                            # We create 5 hidden previews; they will update via outputs
                            vp = gr.Video(label=f"Scene {i+1}", height=200, min_width=150)
                            vid_previews.append(vp)
                    
                    vid_output_final = gr.Video(label="Final Stitched Concept Video")
                    
                    with gr.Accordion("Debug: Story Plan (JSON) 📝", open=False):
                        vid_plan_json = gr.JSON()
                        
                    with gr.Accordion("Debug: Render Plan (JSON) 🛠️", open=False):
                        vid_render_json = gr.JSON()
                    
                    def generate_video_flow(prompt, style, scene_count):
                        preview_clips = [None] * 5
                        
                        def build_yield(status_text, final_vid, story_j, render_j):
                            """Helper to return the exact number of outputs expected by Gradio."""
                            return [status_text, final_vid, story_j, render_j] + preview_clips

                        yield build_yield("🧠 Phase 1/5: Sending request to Gemma...", None, None, None)
                        try:
                            # Step 1: Planning
                            yield build_yield("⏳ Phase 1/5: Gemma is thinking (typically 1-3 minutes)...", None, None, None)
                            raw_plan = scene_planner.plan_scenes(f"Style: {style}, Scene Count: {scene_count}. Prompt: {prompt}")
                            
                            if not raw_plan:
                                yield build_yield("❌ Error: Failed to generate scene plan. (Timeout or Malformed JSON)", None, None, None)
                                return
                                
                            # Step 2: Validation
                            yield build_yield("🔍 Phase 2/5: Validating and repairing plan...", None, raw_plan, None)
                            valid_plan, warnings = scene_validator.validate_plan(raw_plan)
                            
                            # Step 3: Normalization
                            yield build_yield("⚙️ Phase 3/5: Normalizing to render instructions...", None, valid_plan, None)
                            render_scenes, template_names, norm_warnings = render_normalizer.normalize_plan(valid_plan)
                            
                            all_warnings = warnings + norm_warnings
                            if all_warnings:
                                print(f"Normalization Warnings: {all_warnings}")
                                
                            yield build_yield(f"✅ Phase 3/5: Plans ready. Moving to render...", None, valid_plan, render_scenes)
                            
                            # Step 4: Rendering & Save scene clips
                            gen_id = str(uuid.uuid4())[:8]
                            clip_paths = []
                            for i, r_scene in enumerate(render_scenes):
                                if i >= 5: break  # Cap max scenes in UI
                                progress = f"🎨 Phase 4/5: Rendering Scene {i+1}/{len(render_scenes)} ({template_names[i]})..."
                                yield build_yield(progress, None, valid_plan, render_scenes)
                                
                                try:
                                    scene_frames = renderer.render_scene(r_scene)
                                    scene_path = f"scene_{gen_id}_{i}.mp4"
                                    video_composer.compose_scene_clip(scene_frames, scene_path)
                                    
                                    clip_paths.append(scene_path)
                                    preview_clips[i] = scene_path
                                    
                                    # Yield to update the preview player piece by piece
                                    yield build_yield(f"✅ Scene {i+1} complete.", None, valid_plan, render_scenes)
                                except Exception as re_err:
                                    yield build_yield(f"⚠️ Scene {i+1} render failed: {re_err}", None, valid_plan, render_scenes)
                                
                            if not clip_paths:
                                yield build_yield("❌ Error: All scene renders failed.", None, valid_plan, render_scenes)
                                return

                            # Step 5: Stitching
                            yield build_yield("🎞️ Phase 5/5: Stitching final video...", None, valid_plan, render_scenes)
                            output_filename = f"video_{gen_id}_final.mp4"
                            final_path = video_composer.compose_video(clip_paths, output_filename)
                            
                            yield build_yield("✅ Success! Video generated.", final_path, valid_plan, render_scenes)
                        except Exception as e:
                            yield build_yield(f"❌ Unexpected Error: {str(e)}", None, None, None)

                    outputs_list = [vid_status, vid_output_final, vid_plan_json, vid_render_json] + vid_previews
                    vid_generate_btn.click(
                        generate_video_flow, 
                        inputs=[vid_prompt, vid_style, vid_scene_count], 
                        outputs=outputs_list
                    )
            
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
    demo.launch(theme=theme, css=css, server_name="0.0.0.0", server_port=7860)
