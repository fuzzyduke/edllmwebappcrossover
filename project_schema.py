"""
project_schema.py — Data models/schemas for the Manual Scene Builder project.
Provides helper functions to create empty or default states safely.
"""

def create_empty_project():
    return {
        "title": "Untitled Project",
        "global_style": "stick_figure",
        "scene_input_mode": "manual",
        "scenes": []
    }

def create_empty_scene(scene_id, number):
    return {
        "id": scene_id,
        "scene_number": number,
        "brief": "",
        "duration": 4, # default duration
        "caption_override": "",
        "background_override": "",
        "style_override": "",
        "status": "draft" # draft, planned, rendered, failed
    }
