"""
scene_cache.py — Computes unique hash for a scene state to avoid redundant LLM plans or re-renders.
Stores caches locally in memory or disk paths.
"""
import hashlib
import os

CACHE_DIR = "project_cache"
JSON_CACHE_DIR = os.path.join(CACHE_DIR, "json_plans")
RENDER_CACHE_DIR = os.path.join(CACHE_DIR, "render_clips")

# Ensure dirs exist
os.makedirs(JSON_CACHE_DIR, exist_ok=True)
os.makedirs(RENDER_CACHE_DIR, exist_ok=True)

def compute_scene_hash(scene_dict, global_style="stick_figure"):
    """
    Computes a deterministic hash for a scene brief and its explicit style/bg properties.
    """
    # Create a string representation that encapsulates all factors that influence generation
    factors = [
        scene_dict.get("brief", "").strip().lower(),
        str(scene_dict.get("duration", 4)),
        scene_dict.get("style_override", "").strip().lower() or global_style,
        scene_dict.get("background_override", "").strip().lower(),
        scene_dict.get("caption_override", "").strip()
    ]
    
    raw_str = "||".join(factors)
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()

def get_cached_paths(scene_hash):
    """
    Returns (json_path, mp4_path, json_exists, mp4_exists)
    """
    j_path = os.path.join(JSON_CACHE_DIR, f"{scene_hash}.json")
    v_path = os.path.join(RENDER_CACHE_DIR, f"{scene_hash}.mp4")
    
    return j_path, v_path, os.path.exists(j_path), os.path.exists(v_path)
