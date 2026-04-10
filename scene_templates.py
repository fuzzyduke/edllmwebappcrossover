"""
scene_templates.py — Reusable scene blueprints that define default layouts, object slots,
character positions, and beat timings for common scene types.
"""
from scene_schema import WIDTH, HEIGHT


def _char_pos(index, total):
    """Distribute characters evenly across the scene."""
    spacing = WIDTH // (total + 1)
    return {"x": spacing * (index + 1), "y": int(HEIGHT * 0.65)}


# ── Template Definitions ──

TEMPLATES = {
    "wake_up": {
        "background": "bedroom",
        "default_objects": [
            {"type": "bed", "position": {"x": 300, "y": int(HEIGHT * 0.58)}},
        ],
        "character_start": {"x": 300, "y": int(HEIGHT * 0.65)},
        "default_beats": [
            {"time_pct": 0.0,  "pose": "sleeping"},
            {"time_pct": 0.3,  "pose": "eyes_open"},
            {"time_pct": 0.6,  "pose": "stretch"},
            {"time_pct": 0.85, "pose": "stand"},
        ],
    },
    "walk_to_object": {
        "background": "indoor_generic",
        "default_objects": [],
        "character_start": {"x": 180, "y": int(HEIGHT * 0.65)},
        "default_beats": [
            {"time_pct": 0.0,  "pose": "stand"},
            {"time_pct": 0.1,  "pose": "walk_right", "target_x": 600},
            {"time_pct": 0.7,  "pose": "stand"},
            {"time_pct": 0.85, "pose": "idle"},
        ],
    },
    "charging": {
        "background": "charging_room",
        "default_objects": [
            {"type": "charging_station", "position": {"x": 500, "y": int(HEIGHT * 0.58)}},
            {"type": "gauge_bar",        "position": {"x": 700, "y": int(HEIGHT * 0.25)}},
        ],
        "character_start": {"x": 200, "y": int(HEIGHT * 0.65)},
        "default_beats": [
            {"time_pct": 0.0,  "pose": "walk_right", "target_x": 460},
            {"time_pct": 0.5,  "pose": "plug_in"},
            {"time_pct": 0.7,  "pose": "glow"},
            {"time_pct": 0.9,  "pose": "stand"},
        ],
    },
    "cleaning": {
        "background": "cleaning_room",
        "default_objects": [
            {"type": "square_item",   "position": {"x": 350, "y": int(HEIGHT * 0.68)}},
            {"type": "circle_item",   "position": {"x": 550, "y": int(HEIGHT * 0.68)}},
            {"type": "triangle_item", "position": {"x": 750, "y": int(HEIGHT * 0.68)}},
            {"type": "box",           "position": {"x": 900, "y": int(HEIGHT * 0.60)}},
        ],
        "character_start": {"x": 200, "y": int(HEIGHT * 0.65)},
        "default_beats": [
            {"time_pct": 0.0,  "pose": "look_down"},
            {"time_pct": 0.15, "pose": "walk_right", "target_x": 350},
            {"time_pct": 0.3,  "pose": "bend_down"},
            {"time_pct": 0.45, "pose": "pick_up"},
            {"time_pct": 0.55, "pose": "walk_right", "target_x": 900},
            {"time_pct": 0.7,  "pose": "place_object"},
            {"time_pct": 0.85, "pose": "stand_proud"},
        ],
    },
    "sports": {
        "background": "basketball_court",
        "default_objects": [
            {"type": "ball", "position": {"x": 500, "y": int(HEIGHT * 0.68)}},
        ],
        "character_start": {"x": 200, "y": int(HEIGHT * 0.65)},
        "default_beats": [
            {"time_pct": 0.0,  "pose": "stand"},
            {"time_pct": 0.1,  "pose": "walk_right", "target_x": 500},
            {"time_pct": 0.4,  "pose": "pick_up"},
            {"time_pct": 0.5,  "pose": "bounce"},
            {"time_pct": 0.8,  "pose": "arm_raise"},
            {"time_pct": 0.95, "pose": "stand_proud"},
        ],
    },
    "studying": {
        "background": "classroom",
        "default_objects": [
            {"type": "desk", "position": {"x": 400, "y": int(HEIGHT * 0.58)}},
            {"type": "book", "position": {"x": 420, "y": int(HEIGHT * 0.52)}},
        ],
        "character_start": {"x": 400, "y": int(HEIGHT * 0.65)},
        "default_beats": [
            {"time_pct": 0.0,  "pose": "idle"},
            {"time_pct": 0.3,  "pose": "look_down"},
            {"time_pct": 0.7,  "pose": "stand"},
            {"time_pct": 0.9,  "pose": "stand_proud"},
        ],
    },
    "planting": {
        "background": "outdoor_generic",
        "default_objects": [
            {"type": "plant", "position": {"x": 500, "y": int(HEIGHT * 0.65)}},
        ],
        "character_start": {"x": 300, "y": int(HEIGHT * 0.65)},
        "default_beats": [
            {"time_pct": 0.0,  "pose": "stand"},
            {"time_pct": 0.15, "pose": "walk_right", "target_x": 460},
            {"time_pct": 0.3,  "pose": "bend_down"},
            {"time_pct": 0.5,  "pose": "place_object"},
            {"time_pct": 0.7,  "pose": "stand"},
            {"time_pct": 0.9,  "pose": "stand_proud"},
        ],
    },
    "eating": {
        "background": "kitchen",
        "default_objects": [
            {"type": "table", "position": {"x": 500, "y": int(HEIGHT * 0.58)}},
            {"type": "chair", "position": {"x": 400, "y": int(HEIGHT * 0.62)}},
        ],
        "character_start": {"x": 400, "y": int(HEIGHT * 0.65)},
        "default_beats": [
            {"time_pct": 0.0,  "pose": "idle"},
            {"time_pct": 0.3,  "pose": "arm_raise"},
            {"time_pct": 0.6,  "pose": "idle"},
            {"time_pct": 0.9,  "pose": "stand"},
        ],
    },
    "generic": {
        "background": "indoor_generic",
        "default_objects": [],
        "character_start": {"x": int(WIDTH * 0.35), "y": int(HEIGHT * 0.65)},
        "default_beats": [
            {"time_pct": 0.0,  "pose": "idle"},
            {"time_pct": 0.5,  "pose": "stand"},
            {"time_pct": 0.9,  "pose": "idle"},
        ],
    },
}


# ── Template Matching ──

# Keywords in action_summary / key_objects that map to templates
_KEYWORD_MAP = {
    "wake_up": ["wake", "wakes", "sleeping", "sleep", "bed", "morning", "alarm"],
    "charging": ["charge", "charges", "charging", "recharge", "battery", "power", "plug"],
    "cleaning": ["clean", "cleans", "cleaning", "tidy", "sweep", "collect", "pick up", "organize"],
    "sports": ["basketball", "sport", "ball", "run", "race", "play", "exercise", "kick"],
    "studying": ["study", "studies", "read", "book", "test", "exam", "homework", "learn"],
    "planting": ["plant", "seed", "water", "flower", "garden", "grow", "bloom"],
    "eating": ["eat", "breakfast", "lunch", "dinner", "food", "drink", "milk", "juice", "meal"],
    "walk_to_object": ["walk", "go to", "approach", "move to"],
}


def match_template(scene):
    """Given a validated story scene dict, return the best-matching template name."""
    text = " ".join([
        scene.get("action_summary", ""),
        " ".join(scene.get("key_objects", [])),
        scene.get("background", ""),
        " ".join(scene.get("intended_motion", [])),
    ]).lower()

    best_name = "generic"
    best_score = 0

    for template_name, keywords in _KEYWORD_MAP.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_name = template_name

    return best_name
