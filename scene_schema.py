"""
scene_schema.py — Central source of truth for all allowed values in the Text-to-Video pipeline.
Every module imports from here. No magic strings elsewhere.
"""

WIDTH = 1280
HEIGHT = 720
FPS = 12

# ── Allowed Enums ──

ALLOWED_STYLES = ["stick_figure", "geometric_characters", "storyboard_cards", "flat_cartoon"]

ALLOWED_BACKGROUNDS = [
    "bedroom", "charging_room", "living_room", "kitchen", "classroom",
    "playground", "basketball_court", "cleaning_room", "outdoor_generic", "indoor_generic"
]

ALLOWED_MOTIONS = [
    "idle", "sleeping", "eyes_open", "stretch", "stand",
    "walk_left", "walk_right", "bend_down", "arm_raise", "pick_up",
    "place_object", "plug_in", "glow", "bounce", "look_down", "stand_proud"
]

ALLOWED_OBJECTS = [
    "charging_mat", "charging_station", "gauge_bar",
    "table", "chair", "bed", "box", "square_item", "circle_item", "triangle_item",
    "ball", "plant", "book", "desk", "sun", "tree"
]

ALLOWED_TRANSITIONS = ["cut", "fade", "fade_out"]

ALLOWED_SHAPES = ["circle_face", "square_face", "rectangle_face"]

# ── Defaults ──

DEFAULT_SCENE_DURATION = 4     # seconds
MIN_SCENE_DURATION = 3
MAX_SCENE_DURATION = 5
DEFAULT_TOTAL_DURATION = 12
DEFAULT_STYLE = "stick_figure"
DEFAULT_BACKGROUND = "indoor_generic"
DEFAULT_TRANSITION = "cut"
DEFAULT_SHAPE = "circle_face"
DEFAULT_MOTION = "idle"

# ── Color Palette ──

COLOR_MAP = {
    "red": "#ef4444", "blue": "#3b82f6", "green": "#22c55e", "yellow": "#f59e0b",
    "orange": "#f97316", "purple": "#8b5cf6", "indigo": "#6366f1", "pink": "#ec4899",
    "gray": "#94a3b8", "bright": "#3b82f6", "warm": "#f97316",
    "neutral": "#64748b", "white": "#e2e8f0", "black": "#1e293b",
    "teal": "#14b8a6", "cyan": "#06b6d4",
}

def resolve_color(hint):
    """Resolve a color hint to a hex value."""
    if not hint:
        return "#6366f1"
    hint_lower = hint.strip().lower()
    if hint_lower.startswith("#") and len(hint_lower) in (4, 7):
        return hint_lower
    return COLOR_MAP.get(hint_lower, "#6366f1")
