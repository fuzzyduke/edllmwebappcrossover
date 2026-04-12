"""
scene_importer.py — Parses uploaded TXT and JSON files or bulk pasted text into standardized internal scene lists.
"""
import re
import json
import uuid
from project_schema import create_empty_project, create_empty_scene

def parse_txt_briefs(text):
    """
    Parses a string of text into separate scene briefs.
    Supports splitting by blank lines OR headings like 'Scene 1'.
    """
    if not text:
        return create_empty_project()
        
    lines = text.strip().split('\n')
    
    raw_scenes = []
    current_brief = []
    
    for line in lines:
        line_s = line.strip()
        if not line_s:
            if current_brief:
                raw_scenes.append("\n".join(current_brief).strip())
                current_brief = []
            continue
        
        # Detect headings like "Scene 1", "Scene 1:", "SCENE 01"
        if re.match(r'^Scene\s+\d+:?$', line_s, re.IGNORECASE):
            if current_brief:
                raw_scenes.append("\n".join(current_brief).strip())
                current_brief = []
            continue
            
        current_brief.append(line_s)
        
    if current_brief:
        raw_scenes.append("\n".join(current_brief).strip())
        
    proj = create_empty_project()
    if raw_scenes:
        proj["title"] = "Imported TXT Script"
        
    for i, brief in enumerate(raw_scenes):
        sc = create_empty_scene(f"scene_{str(uuid.uuid4())[:8]}", i+1)
        sc["brief"] = brief
        proj["scenes"].append(sc)
        
    return proj

def parse_json_briefs(filepath):
    """
    Reads a JSON file. Checks if it's already a Project structure or just a list of scenes.
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        proj = create_empty_project()
        
        if "scenes" in data and isinstance(data["scenes"], list):
            proj["title"] = data.get("title", "Imported JSON Project")
            proj["global_style"] = data.get("style", "stick_figure")
            scenes_list = data["scenes"]
        elif isinstance(data, list):
            proj["title"] = "Imported JSON Scene List"
            scenes_list = data
        else:
            raise ValueError("JSON does not match expected project or scene list format.")
            
        for i, raw_sc in enumerate(scenes_list):
            sc = create_empty_scene(f"scene_{str(uuid.uuid4())[:8]}", i+1)
            sc["brief"] = raw_sc.get("brief", raw_sc.get("action_summary", "Unknown scene action"))
            sc["duration"] = raw_sc.get("duration", 4)
            sc["caption_override"] = raw_sc.get("caption_override", "")
            sc["background_override"] = raw_sc.get("background_override", "")
            sc["style_override"] = raw_sc.get("style_override", "")
            proj["scenes"].append(sc)
            
        return proj
    except Exception as e:
        print(f"Failed to import JSON: {e}")
        return None
