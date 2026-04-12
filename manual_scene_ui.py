import gradio as gr
import json
import uuid
import os
import scene_planner
import scene_validator
import render_normalizer
import renderer
import video_composer
import project_schema
import scene_importer
import scene_cache
import ui_help_content
from scene_schema import ALLOWED_STYLES, ALLOWED_BACKGROUNDS

def create_manual_tab_contents():
    with gr.Tab("Manual Scene Builder Mode"):
        gr.Markdown(ui_help_content.MODE_HELP)
        project_state = gr.State(project_schema.create_empty_project())
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Project Manager")
                
                with gr.Accordion("Import Scripts 📁", open=False):
                    gr.Markdown(ui_help_content.IMPORT_HELP_MODAL)
                    import_file = gr.File(label="Upload .txt or .json")
                    
                    gr.Markdown("#### Auto Split / Bulk Import Box")
                    import_paste = gr.Textbox(
                        label="Paste your full story or scene list here", 
                        placeholder="e.g. A kid wakes up.\n\nHe drinks milk.\n\nHe runs outside.",
                        lines=6
                    )
                    btn_import = gr.Button("Import from Text/File")
                
                gr.Markdown("#### Scene List")
                scene_dropdown = gr.Dropdown(label="Select Scene to Edit", choices=[], value=None)
                btn_add_scene = gr.Button("+ Add New Scene")
                
                gr.Markdown("#### Global Actions")
                btn_render_all = gr.Button("🎬 Render All & Stitch Movie", variant="primary")
                status_all = gr.Textbox(label="Project Status", interactive=False)
                final_vid_out = gr.Video(label="Final Movie")
            
            with gr.Column(scale=2):
                gr.Markdown("### Selected Scene Inspector 🔍")
                scene_lbl = gr.Markdown("**No scene selected**")
                
                brief_input = gr.Textbox(label="Scene Brief (Action)", lines=4)
                
                with gr.Row():
                    dur_input = gr.Slider(3, 5, step=1, label="Duration (s)", value=4)
                    bg_override = gr.Dropdown([""] + ALLOWED_BACKGROUNDS, label="Background Override")
                    style_override = gr.Dropdown([""] + ALLOWED_STYLES, label="Style Override")
                
                cap_override = gr.Textbox(label="Caption Override (Optional)")
                
                with gr.Row():
                    btn_save = gr.Button("💾 Save Scene Editing")
                    btn_dup = gr.Button("Duplicate")
                    btn_del = gr.Button("Delete", variant="stop")
                
                with gr.Row():
                    btn_up = gr.Button("⬆️ Move Up")
                    btn_down = gr.Button("⬇️ Move Down")
                
                gr.Markdown("#### Single Scene Rendering")
                btn_render_single = gr.Button("🎨 Render This Scene", variant="secondary")
                single_status = gr.Textbox(label="Scene Status", interactive=False)
                single_preview = gr.Video(label="Scene Preview")
                debug_log = gr.Textbox(label="Debugger / Error Logs", lines=5, interactive=False)

        # --- Helper Functions for State Management ---
        
        def update_dropdown(proj):
            if not proj or not proj["scenes"]:
                return gr.update(choices=[], value=None)
            choices = [f"Scene {s['scene_number']}: {s['brief'][:40]}..." for s in proj["scenes"]]
            # keep current selection if possible, else 0
            val = choices[0] if choices else None
            return gr.update(choices=choices, value=val)

        def sync_inspector(choice, proj):
            if not choice or not proj or not proj["scenes"]:
                return "**No scene selected**", "", 4, "", "", "", None
            try:
                s_num = int(choice.split(":")[0].replace("Scene ", ""))
            except:
                return "**Error parsing scene selection**", "", 4, "", "", "", None
                
            scene = next((s for s in proj["scenes"] if s["scene_number"] == s_num), None)
            if not scene:
                return "**No scene selected**", "", 4, "", "", "", None
                
            shash = scene_cache.compute_scene_hash(scene, proj["global_style"])
            _, vpath, _, vexists = scene_cache.get_cached_paths(shash)
            
            lbl = f"**Editing Scene {s_num}** | Status: `{scene['status']}`"
            
            return lbl, scene["brief"], scene.get("duration", 4), scene.get("background_override", ""), scene.get("style_override", ""), scene.get("caption_override", ""), vpath if vexists else None

        def do_import(file_obj, paste_txt):
            if file_obj:
                if file_obj.name.endswith(".json"):
                    proj = scene_importer.parse_json_briefs(file_obj.name)
                else:
                    with open(file_obj.name, 'r', encoding='utf-8') as f:
                        proj = scene_importer.parse_txt_briefs(f.read())
            elif paste_txt:
                proj = scene_importer.parse_txt_briefs(paste_txt)
            else:
                proj = project_schema.create_empty_project()
                
            if not proj:
                proj = project_schema.create_empty_project()
            return proj, "Imported successfully.", update_dropdown(proj)

        def add_scene(proj):
            if not proj: proj = project_schema.create_empty_project()
            new_num = len(proj["scenes"]) + 1
            new_s = project_schema.create_empty_scene(f"scene_{str(uuid.uuid4())[:8]}", new_num)
            new_s["brief"] = "New empty scene action..."
            proj["scenes"].append(new_s)
            
            dd = update_dropdown(proj)
            dd['value'] = dd['choices'][-1] # Select the new scene
            return proj, dd

        def get_selected_idx(choice, proj):
            if not choice or not proj or not proj["scenes"]: return -1
            try:
                s_num = int(choice.split(":")[0].replace("Scene ", ""))
            except:
                return -1
            for i, s in enumerate(proj["scenes"]):
                if s["scene_number"] == s_num:
                    return i
            return -1

        def save_scene(choice, proj, brief, dur, bg, style, cap):
            idx = get_selected_idx(choice, proj)
            if idx == -1: return proj, update_dropdown(proj)
            
            proj["scenes"][idx]["brief"] = brief
            proj["scenes"][idx]["duration"] = dur
            proj["scenes"][idx]["background_override"] = bg
            proj["scenes"][idx]["style_override"] = style
            proj["scenes"][idx]["caption_override"] = cap
            proj["scenes"][idx]["status"] = "draft"
            
            dd = update_dropdown(proj)
            dd['value'] = dd['choices'][idx]
            return proj, dd

        def del_scene(choice, proj):
            idx = get_selected_idx(choice, proj)
            if idx != -1:
                proj["scenes"].pop(idx)
                for i, s in enumerate(proj["scenes"]):
                    s["scene_number"] = i + 1
            dd = update_dropdown(proj)
            return proj, dd
            
        def dup_scene(choice, proj):
            idx = get_selected_idx(choice, proj)
            if idx != -1:
                orig = proj["scenes"][idx]
                new_s = project_schema.create_empty_scene(f"scene_{str(uuid.uuid4())[:8]}", orig["scene_number"]+1)
                new_s["brief"] = orig["brief"] + " (Copy)"
                new_s["duration"] = orig["duration"]
                new_s["background_override"] = orig["background_override"]
                new_s["style_override"] = orig["style_override"]
                new_s["caption_override"] = orig["caption_override"]
                proj["scenes"].insert(idx+1, new_s)
                for i, s in enumerate(proj["scenes"]):
                    s["scene_number"] = i + 1
            dd = update_dropdown(proj)
            if idx != -1: dd['value'] = dd['choices'][idx+1]
            return proj, dd

        def move_up(choice, proj):
            idx = get_selected_idx(choice, proj)
            if idx > 0:
                proj["scenes"][idx], proj["scenes"][idx-1] = proj["scenes"][idx-1], proj["scenes"][idx]
                for i, s in enumerate(proj["scenes"]): s["scene_number"] = i + 1
            dd = update_dropdown(proj)
            if idx > 0: dd['value'] = dd['choices'][idx-1]
            return proj, dd
            
        def move_down(choice, proj):
            idx = get_selected_idx(choice, proj)
            if idx != -1 and idx < len(proj["scenes"]) - 1:
                proj["scenes"][idx], proj["scenes"][idx+1] = proj["scenes"][idx+1], proj["scenes"][idx]
                for i, s in enumerate(proj["scenes"]): s["scene_number"] = i + 1
            dd = update_dropdown(proj)
            if idx != -1 and idx < len(proj["scenes"]) - 1: dd['value'] = dd['choices'][idx+1]
            return proj, dd

        def process_single_scene(scene_dict, global_style):
            shash = scene_cache.compute_scene_hash(scene_dict, global_style)
            j_path, v_path, j_exists, v_exists = scene_cache.get_cached_paths(shash)
            
            if v_exists:
                scene_dict["status"] = "rendered"
                yield f"✅ Scene loaded from cache ({shash})", v_path, True, f"CACHE HIT: Hash {shash} found."
                return
                
            # Need to plan and render
            yield f"🧠 Planning scene...", None, False, f"Starting Planning for scene {scene_dict['scene_number']}..."
            plan = scene_planner.plan_single_scene(scene_dict["brief"], scene_dict["scene_number"], scene_dict["duration"])
            
            if not plan:
                scene_dict["status"] = "failed"
                yield "❌ Failed to generate scene plan.", None, False, "LLM TIMEOUT/PARSE ERROR: Prompt returned no valid JSON."
                return
                
            # Apply overrides
            if scene_dict.get("background_override"):
                plan["background"] = scene_dict["background_override"]
            if scene_dict.get("caption_override"):
                plan["caption"] = scene_dict["caption_override"]
                
            yield f"🔍 Normalizing scene...", None, False, f"LLM Plan succeeded. Running Normalization...\n{json.dumps(plan)}"
            
            # wrap in array for normalizer
            valid_plan, warnings = scene_validator.validate_plan({"scenes": [plan]})
            render_scenes, ts, ws = render_normalizer.normalize_plan(valid_plan)
            
            w_str = f"Validation/Norm Warnings: {warnings + ws}" if (warnings + ws) else "No warnings during normalization."
            
            if not render_scenes:
                scene_dict["status"] = "failed"
                yield "❌ Normalization failed.", None, False, f"NORMALIZER EXCEPTION: {w_str}\nInput was: {json.dumps(valid_plan)}"
                return
                
            r_scene = render_scenes[0]
            
            yield f"🎨 Rendering frames...", None, False, f"Sending Render JSON to MoviePy engine...\n{w_str}"
            try:
                frames = renderer.render_scene(r_scene)
                video_composer.compose_scene_clip(frames, v_path)
                with open(j_path, 'w') as f:
                    json.dump(r_scene, f)
                scene_dict["status"] = "rendered"
                yield f"✅ Scene rendered and cached.", v_path, True, f"SUCCESS: Scene {scene_dict['scene_number']} cached as {shash}."
            except Exception as e:
                scene_dict["status"] = "failed"
                yield f"❌ Render failed: {e}", None, False, f"RENDERER EXCEPTION:\n{str(e)}"

        def render_single(choice, proj):
            idx = get_selected_idx(choice, proj)
            if idx == -1:
                insp_tuple = sync_inspector(choice, proj)
                lbl = insp_tuple[0] if insp_tuple else "**No scene selected**"
                yield proj, "❌ No scene selected", None, lbl, "Cannot render: No scene index active."
                return
                
            scene = proj["scenes"][idx]
            
            for status_msg, vid_path, is_done, dbg_log in process_single_scene(scene, proj["global_style"]):
                if is_done:
                    # Final update
                    insp = sync_inspector(choice, proj)
                    yield proj, status_msg, vid_path, insp[0], dbg_log
                else:
                    yield proj, status_msg, None, gr.update(), dbg_log
                    
        def render_all(proj):
            if not proj or not proj["scenes"]:
                yield proj, "❌ No scenes in project.", None
                return
                
            clip_paths = []
            for i, scene in enumerate(proj["scenes"]):
                yield proj, f"Working on Scene {i+1} / {len(proj['scenes'])}...", None
                
                final_vpath = None
                for status_msg, vid_path, is_done, _ in process_single_scene(scene, proj["global_style"]):
                    if is_done and vid_path:
                        final_vpath = vid_path
                        
                if scene["status"] != "rendered" or not final_vpath:
                    yield proj, f"❌ Failed on Scene {i+1}. Stopping.", None
                    return
                clip_paths.append(final_vpath)
                
            yield proj, f"🎞️ Stitching {len(clip_paths)} clips...", None
            out_file = f"project_cache/final_stitched_{str(uuid.uuid4())[:8]}.mp4"
            try:
                video_composer.compose_video(clip_paths, out_file)
                yield proj, "✅ Movie completely rendered and stitched!", out_file
            except Exception as e:
                yield proj, f"❌ Stitching failed: {e}", None

        # --- Event Wiring ---
        btn_import.click(do_import, inputs=[import_file, import_paste], outputs=[project_state, status_all, scene_dropdown])
        btn_add_scene.click(add_scene, inputs=[project_state], outputs=[project_state, scene_dropdown])
        
        scene_dropdown.change(sync_inspector, inputs=[scene_dropdown, project_state], outputs=[scene_lbl, brief_input, dur_input, bg_override, style_override, cap_override, single_preview])
        
        btn_save.click(save_scene, inputs=[scene_dropdown, project_state, brief_input, dur_input, bg_override, style_override, cap_override], outputs=[project_state, scene_dropdown]).then(
            sync_inspector, inputs=[scene_dropdown, project_state], outputs=[scene_lbl, brief_input, dur_input, bg_override, style_override, cap_override, single_preview]
        )
        
        btn_del.click(del_scene, inputs=[scene_dropdown, project_state], outputs=[project_state, scene_dropdown])
        btn_dup.click(dup_scene, inputs=[scene_dropdown, project_state], outputs=[project_state, scene_dropdown])
        btn_up.click(move_up, inputs=[scene_dropdown, project_state], outputs=[project_state, scene_dropdown])
        btn_down.click(move_down, inputs=[scene_dropdown, project_state], outputs=[project_state, scene_dropdown])
        
        # Single render yields multiple updates
        render_btn_evt = btn_render_single.click(
            render_single, 
            inputs=[scene_dropdown, project_state], 
            outputs=[project_state, single_status, single_preview, scene_lbl, debug_log]
        )
        
        btn_render_all.click(render_all, inputs=[project_state], outputs=[project_state, status_all, final_vid_out])
        
