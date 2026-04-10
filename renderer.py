"""
renderer.py — Beat-driven frame renderer using Pillow.
Consumes render-scene JSON (with beats[], objects[], character positions).
Draws backgrounds, objects, characters with pose states, and captions.
"""
from PIL import Image, ImageDraw, ImageFont
import math
from scene_schema import WIDTH, HEIGHT, FPS, resolve_color


# ══════════════════════════════════════════════════════════
#  POSE SYSTEM
# ══════════════════════════════════════════════════════════

def _draw_character(draw, x, y, shape="circle_face", color="#6366f1", pose="idle", anim_t=0):
    """Draw a stick figure at (x,y) with the given pose and animation time."""
    size = 1.0
    head_r = 28 * size
    torso_h = 70 * size
    arm_l = 45 * size
    leg_l = 55 * size

    # Pose-specific adjustments
    y_offset = 0
    arm_angle_l = -45
    arm_angle_r = 45
    leg_angle_l = -25
    leg_angle_r = 25
    eye_open = True
    body_glow = False
    body_shrink = 1.0

    if pose == "sleeping":
        y_offset = 30  # lower, lying down
        arm_angle_l = -80
        arm_angle_r = 80
        leg_angle_l = -10
        leg_angle_r = 10
        eye_open = False
    elif pose == "eyes_open":
        y_offset = 20
        arm_angle_l = -70
        arm_angle_r = 70
    elif pose == "stretch":
        arm_angle_l = -160
        arm_angle_r = 160
        y_offset = -10
    elif pose == "stand":
        pass  # default upright
    elif pose == "idle":
        # subtle breathing
        y_offset = math.sin(anim_t * 2) * 3
    elif pose in ("walk_left", "walk_right"):
        leg_angle_l = -25 + math.sin(anim_t * 4) * 30
        leg_angle_r = 25 - math.sin(anim_t * 4) * 30
        arm_angle_l = -45 - math.sin(anim_t * 4) * 25
        arm_angle_r = 45 + math.sin(anim_t * 4) * 25
        y_offset = -abs(math.sin(anim_t * 4) * 8)
    elif pose == "bend_down":
        y_offset = 40
        arm_angle_l = -90
        arm_angle_r = 90
        body_shrink = 0.7
    elif pose == "arm_raise":
        arm_angle_l = -170
        arm_angle_r = 170
    elif pose == "pick_up":
        y_offset = 25
        arm_angle_l = -100
        arm_angle_r = 100
        body_shrink = 0.8
    elif pose == "place_object":
        arm_angle_l = -60
        arm_angle_r = 60
        y_offset = 10
    elif pose == "plug_in":
        arm_angle_l = -45
        arm_angle_r = 20  # reaching forward
    elif pose == "glow":
        body_glow = True
        arm_angle_l = -50
        arm_angle_r = 50
    elif pose == "bounce":
        y_offset = -abs(math.sin(anim_t * 3) * 25)
        leg_angle_l = -25 + math.sin(anim_t * 3) * 15
        leg_angle_r = 25 - math.sin(anim_t * 3) * 15
    elif pose == "look_down":
        y_offset = 8
    elif pose == "stand_proud":
        arm_angle_l = -140
        arm_angle_r = 140
        y_offset = -5

    # Apply body shrink
    torso_h *= body_shrink
    arm_l *= body_shrink
    leg_l *= body_shrink

    # Glow effect
    if body_glow:
        glow_r = int(head_r * 3.5)
        for gr in range(glow_r, 0, -8):
            alpha = max(20, 60 - gr)
            draw.ellipse(
                [x - gr, y + y_offset - torso_h - head_r - gr,
                 x + gr, y + y_offset - torso_h - head_r + gr],
                fill=None, outline=color, width=2
            )

    # Head
    hx = x
    hy = y + y_offset - torso_h - head_r
    outline_col = "#ffffff"

    if shape == "circle_face":
        draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r],
                     fill=color, outline=outline_col, width=2)
    elif shape == "square_face":
        draw.rectangle([hx - head_r, hy - head_r, hx + head_r, hy + head_r],
                       fill=color, outline=outline_col, width=2)
    elif shape == "rectangle_face":
        draw.rectangle([hx - head_r * 0.8, hy - head_r * 1.2,
                        hx + head_r * 0.8, hy + head_r * 1.2],
                       fill=color, outline=outline_col, width=2)

    # Eyes
    if eye_open:
        draw.ellipse([hx - 10, hy - 5, hx - 4, hy + 1], fill="white")
        draw.ellipse([hx + 4, hy - 5, hx + 10, hy + 1], fill="white")
        draw.ellipse([hx - 8, hy - 3, hx - 6, hy - 1], fill="black")
        draw.ellipse([hx + 6, hy - 3, hx + 8, hy - 1], fill="black")
    else:
        draw.line([hx - 10, hy - 2, hx - 4, hy - 2], fill="black", width=2)
        draw.line([hx + 4, hy - 2, hx + 10, hy - 2], fill="black", width=2)

    # Smile (tiny)
    draw.arc([hx - 6, hy + 2, hx + 6, hy + 10], start=0, end=180, fill="black", width=2)

    # Torso
    tx, ty = x, y + y_offset - torso_h
    bx, by = x, y + y_offset
    draw.line([tx, ty, bx, by], fill="#e2e8f0", width=4)

    # Arms
    lax = tx + math.sin(math.radians(arm_angle_l)) * arm_l
    lay = ty + math.cos(math.radians(arm_angle_l)) * arm_l
    draw.line([tx, ty, lax, lay], fill="#e2e8f0", width=3)

    rax = tx + math.sin(math.radians(arm_angle_r)) * arm_l
    ray = ty + math.cos(math.radians(arm_angle_r)) * arm_l
    draw.line([tx, ty, rax, ray], fill="#e2e8f0", width=3)

    # Legs
    llx = bx + math.sin(math.radians(leg_angle_l)) * leg_l
    lly = by + math.cos(math.radians(leg_angle_l)) * leg_l
    draw.line([bx, by, llx, lly], fill="#e2e8f0", width=3)

    rlx = bx + math.sin(math.radians(leg_angle_r)) * leg_l
    rly = by + math.cos(math.radians(leg_angle_r)) * leg_l
    draw.line([bx, by, rlx, rly], fill="#e2e8f0", width=3)


# ══════════════════════════════════════════════════════════
#  OBJECT DRAWING
# ══════════════════════════════════════════════════════════

def _draw_object(draw, obj_type, x, y, anim_t=0, state=None):
    """Draw a simple primitive object at (x, y)."""
    if obj_type == "table":
        draw.rectangle([x - 60, y - 5, x + 60, y + 5], fill="#8B4513", outline="#5C2D0A")
        draw.rectangle([x - 55, y + 5, x - 48, y + 45], fill="#8B4513")
        draw.rectangle([x + 48, y + 5, x + 55, y + 45], fill="#8B4513")
    elif obj_type == "chair":
        draw.rectangle([x - 15, y - 30, x + 15, y], fill="#A0522D", outline="#5C2D0A")
        draw.rectangle([x - 12, y, x - 8, y + 30], fill="#A0522D")
        draw.rectangle([x + 8, y, x + 12, y + 30], fill="#A0522D")
    elif obj_type == "bed":
        draw.rectangle([x - 70, y - 10, x + 70, y + 20], fill="#4a5568", outline="#2d3748")
        draw.rectangle([x - 70, y - 30, x - 50, y - 10], fill="#718096")  # pillow
        draw.rectangle([x - 70, y - 10, x + 70, y], fill="#667eea")  # blanket
    elif obj_type == "charging_station":
        draw.rectangle([x - 20, y - 50, x + 20, y], fill="#4a5568", outline="#718096", width=2)
        draw.polygon([(x - 8, y - 40), (x + 2, y - 25), (x - 2, y - 25), (x + 8, y - 10)],
                     fill="#f59e0b")  # lightning bolt
    elif obj_type == "charging_mat":
        draw.rectangle([x - 50, y - 5, x + 50, y + 5], fill="#374151", outline="#6366f1", width=2)
        draw.ellipse([x - 8, y - 4, x + 8, y + 4], fill="#6366f1")
    elif obj_type == "gauge_bar":
        # Background bar
        bar_w, bar_h = 120, 25
        draw.rectangle([x - bar_w//2, y - bar_h//2, x + bar_w//2, y + bar_h//2],
                       fill="#1f2937", outline="#4b5563", width=2)
        # Fill based on animation time
        fill_pct = min(1.0, anim_t * 0.5) if state != "full" else 1.0
        fill_w = int((bar_w - 6) * fill_pct)
        if fill_w > 0:
            color = "#22c55e" if fill_pct > 0.6 else "#f59e0b" if fill_pct > 0.3 else "#ef4444"
            draw.rectangle([x - bar_w//2 + 3, y - bar_h//2 + 3,
                            x - bar_w//2 + 3 + fill_w, y + bar_h//2 - 3],
                           fill=color)
        # Label
        draw.text((x, y - bar_h//2 - 12), "ENERGY", fill="#9ca3af", anchor="mm")
    elif obj_type == "ball":
        draw.ellipse([x - 15, y - 15, x + 15, y + 15], fill="#f97316", outline="#ea580c", width=2)
        draw.arc([x - 10, y - 8, x + 10, y + 8], start=0, end=180, fill="#ea580c", width=1)
    elif obj_type == "box":
        draw.rectangle([x - 30, y - 25, x + 30, y + 25], fill="#78716c", outline="#57534e", width=2)
        draw.line([x - 30, y - 10, x + 30, y - 10], fill="#57534e", width=1)
    elif obj_type == "square_item":
        draw.rectangle([x - 10, y - 10, x + 10, y + 10], fill="#ef4444", outline="#dc2626")
    elif obj_type == "circle_item":
        draw.ellipse([x - 10, y - 10, x + 10, y + 10], fill="#3b82f6", outline="#2563eb")
    elif obj_type == "triangle_item":
        draw.polygon([(x, y - 12), (x - 10, y + 10), (x + 10, y + 10)],
                     fill="#22c55e", outline="#16a34a")
    elif obj_type == "plant":
        # Pot
        draw.polygon([(x - 15, y), (x + 15, y), (x + 10, y + 25), (x - 10, y + 25)],
                     fill="#92400e")
        # Stem
        draw.rectangle([x - 2, y - 30, x + 2, y], fill="#16a34a")
        # Leaves
        draw.ellipse([x - 18, y - 40, x, y - 20], fill="#22c55e")
        draw.ellipse([x, y - 45, x + 18, y - 25], fill="#16a34a")
    elif obj_type == "book":
        draw.rectangle([x - 18, y - 5, x + 18, y + 5], fill="#6366f1", outline="#4f46e5")
        draw.line([x, y - 5, x, y + 5], fill="#4f46e5", width=1)
    elif obj_type == "desk":
        draw.rectangle([x - 70, y - 5, x + 70, y + 5], fill="#92400e", outline="#78350f")
        draw.rectangle([x - 60, y + 5, x - 52, y + 50], fill="#92400e")
        draw.rectangle([x + 52, y + 5, x + 60, y + 50], fill="#92400e")
    elif obj_type == "sun":
        draw.ellipse([x - 25, y - 25, x + 25, y + 25], fill="#fbbf24", outline="#f59e0b")
        for angle in range(0, 360, 45):
            rx = x + math.cos(math.radians(angle)) * 35
            ry = y + math.sin(math.radians(angle)) * 35
            draw.line([x + math.cos(math.radians(angle)) * 27,
                       y + math.sin(math.radians(angle)) * 27,
                       rx, ry], fill="#fbbf24", width=2)
    elif obj_type == "tree":
        draw.rectangle([x - 10, y, x + 10, y + 50], fill="#744210")
        draw.ellipse([x - 35, y - 40, x + 35, y + 10], fill="#276749")


# ══════════════════════════════════════════════════════════
#  BACKGROUNDS
# ══════════════════════════════════════════════════════════

_BG_CONFIGS = {
    "bedroom": {
        "sky": "#1e293b", "floor": "#334155",
        "extras": lambda d: [
            d.rectangle([20, 200, 60, int(HEIGHT*0.7)], fill="#475569"),  # wall lamp
            d.rectangle([60, 240, 80, 260], fill="#fbbf24"),  # lamp light
        ]
    },
    "charging_room": {
        "sky": "#0f172a", "floor": "#1e293b",
        "extras": lambda d: [
            d.rectangle([WIDTH-80, 150, WIDTH-40, int(HEIGHT*0.7)], fill="#374151"),  # panel
            d.ellipse([WIDTH-70, 170, WIDTH-50, 190], fill="#22c55e"),  # indicator
        ]
    },
    "living_room": {
        "sky": "#1e293b", "floor": "#78716c",
        "extras": lambda d: [
            d.rectangle([80, 250, 200, int(HEIGHT*0.7)], fill="#4a5568"),  # couch
        ]
    },
    "kitchen": {
        "sky": "#292524", "floor": "#44403c",
        "extras": lambda d: [
            d.rectangle([WIDTH-120, 180, WIDTH-20, int(HEIGHT*0.7)], fill="#57534e"),  # counter
            d.rectangle([WIDTH-100, 100, WIDTH-40, 180], fill="#78716c"),  # cabinet
        ]
    },
    "classroom": {
        "sky": "#fef3c7", "floor": "#92400e",
        "extras": lambda d: [
            d.rectangle([80, 120, WIDTH-80, 180], fill="#1e3a5f"),  # blackboard
            d.text((WIDTH//2, 150), "ABC", fill="#fbbf24", anchor="mm"),
        ]
    },
    "playground": {
        "sky": "#bae6fd", "floor": "#65a30d",
        "extras": lambda d: [
            d.rectangle([WIDTH-100, 300, WIDTH-90, int(HEIGHT*0.7)], fill="#a16207"),  # pole
            d.rectangle([WIDTH-130, 300, WIDTH-60, 320], fill="#dc2626"),  # bar
            _draw_object(d, "sun", 100, 80),
        ]
    },
    "basketball_court": {
        "sky": "#7dd3fc", "floor": "#c2410c",
        "extras": lambda d: [
            d.rectangle([WIDTH-80, 200, WIDTH-70, int(HEIGHT*0.7)], fill="#78716c"),  # post
            d.rectangle([WIDTH-120, 200, WIDTH-40, 230], fill="#ffffff", outline="#ef4444"),  # backboard
            d.ellipse([WIDTH-95, 230, WIDTH-65, 250], fill=None, outline="#ef4444", width=2),  # rim
        ]
    },
    "cleaning_room": {
        "sky": "#f1f5f9", "floor": "#cbd5e1",
        "extras": lambda d: []
    },
    "outdoor_generic": {
        "sky": "#bae6fd", "floor": "#65a30d",
        "extras": lambda d: [
            _draw_object(d, "sun", 100, 70),
            _draw_object(d, "tree", WIDTH - 120, int(HEIGHT * 0.7) - 50),
        ]
    },
    "indoor_generic": {
        "sky": "#1e293b", "floor": "#334155",
        "extras": lambda d: []
    },
}


def _draw_bg(draw, bg_name):
    """Draw the full background for a scene."""
    cfg = _BG_CONFIGS.get(bg_name, _BG_CONFIGS["indoor_generic"])
    floor_y = int(HEIGHT * 0.7)

    # Sky / wall
    draw.rectangle([0, 0, WIDTH, floor_y], fill=cfg["sky"])
    # Floor
    draw.rectangle([0, floor_y, WIDTH, HEIGHT], fill=cfg["floor"])
    # Floor line
    draw.line([0, floor_y, WIDTH, floor_y], fill="#64748b", width=2)

    # Background-specific extras
    try:
        cfg["extras"](draw)
    except Exception:
        pass  # graceful degradation


# ══════════════════════════════════════════════════════════
#  BEAT INTERPOLATION & FRAME RENDERING
# ══════════════════════════════════════════════════════════

def _get_current_beat(beats, progress):
    """Given a list of beats and a progress (0.0-1.0), return the current beat."""
    current = beats[0] if beats else {"pose": "idle"}
    for beat in beats:
        if beat["time_pct"] <= progress:
            current = beat
        else:
            break
    return current


def _interpolate_x(char_x, beat, prev_beat, progress, beat_start_pct, beat_end_pct):
    """Smoothly interpolate X position for walk beats."""
    if "target_x" not in beat:
        return char_x
    if beat_end_pct <= beat_start_pct:
        return beat["target_x"]
    local_pct = (progress - beat_start_pct) / (beat_end_pct - beat_start_pct)
    local_pct = max(0, min(1, local_pct))
    start_x = prev_beat.get("target_x", char_x) if prev_beat and "target_x" in prev_beat else char_x
    return start_x + (beat["target_x"] - start_x) * local_pct


def render_scene(render_data):
    """
    Render a single render-scene dict into a list of PIL Image frames.
    Uses beat-driven animation.
    """
    frames = []
    duration = render_data.get("duration", 4)
    num_frames = int(duration * FPS)
    bg_name = render_data.get("background", "indoor_generic")
    caption = render_data.get("caption", "")
    characters = render_data.get("characters", [])
    objects = render_data.get("objects", [])
    beats = render_data.get("beats", [{"time_pct": 0, "pose": "idle"}])

    # Track character X positions (mutable)
    char_positions = {}
    for ch in characters:
        pos = ch.get("position", {"x": 400, "y": int(HEIGHT * 0.65)})
        char_positions[ch["id"]] = {"x": pos["x"], "y": pos["y"]}

    for f_idx in range(num_frames):
        progress = f_idx / max(num_frames - 1, 1)
        anim_t = f_idx / FPS

        img = Image.new("RGB", (WIDTH, HEIGHT), "#0f172a")
        draw = ImageDraw.Draw(img)

        # Background
        _draw_bg(draw, bg_name)

        # Objects
        for obj in objects:
            ox = obj["position"]["x"]
            oy = obj["position"]["y"]
            _draw_object(draw, obj["type"], ox, oy, anim_t=anim_t)

        # Determine current beat
        current_beat = _get_current_beat(beats, progress)

        # Find previous beat for interpolation
        prev_beat = None
        current_beat_start = 0
        next_beat_start = 1.0
        for bi, b in enumerate(beats):
            if b["time_pct"] <= progress:
                current_beat = b
                current_beat_start = b["time_pct"]
                prev_beat = beats[bi - 1] if bi > 0 else None
                next_beat_start = beats[bi + 1]["time_pct"] if bi + 1 < len(beats) else 1.0

        pose = current_beat.get("pose", "idle")

        # Characters
        for ch in characters:
            cid = ch["id"]
            cx = char_positions[cid]["x"]
            cy = char_positions[cid]["y"]

            # Interpolate walk
            if "target_x" in current_beat:
                cx = _interpolate_x(
                    char_positions[cid]["x"], current_beat, prev_beat,
                    progress, current_beat_start, next_beat_start
                )
                # Update tracked position for next frame
                char_positions[cid]["x"] = cx

            color = resolve_color(ch.get("color_hint", "blue"))
            _draw_character(draw, int(cx), int(cy), shape=ch.get("shape", "circle_face"),
                           color=color, pose=pose, anim_t=anim_t)

        # Caption bar
        cap_h = 60
        draw.rectangle([0, HEIGHT - cap_h, WIDTH, HEIGHT], fill="#000000")
        draw.text((WIDTH // 2, HEIGHT - cap_h // 2), caption, fill="#e2e8f0", anchor="mm")

        # Scene number label
        sn = render_data.get("scene_number", "")
        draw.text((20, 15), f"Scene {sn}", fill="#94a3b8", anchor="lt")

        frames.append(img)

    return frames


if __name__ == "__main__":
    import json
    test = {
        "scene_number": 1,
        "duration": 3,
        "background": "bedroom",
        "characters": [{"id": "robot", "shape": "rectangle_face", "color_hint": "gray",
                        "position": {"x": 300, "y": 468}}],
        "objects": [{"id": "bed", "type": "bed", "position": {"x": 300, "y": 417}}],
        "beats": [
            {"time_pct": 0.0, "pose": "sleeping"},
            {"time_pct": 0.3, "pose": "eyes_open"},
            {"time_pct": 0.6, "pose": "stretch"},
            {"time_pct": 0.85, "pose": "stand"},
        ],
        "caption": "Beep boop... Awake!",
        "transition": "cut"
    }
    frames = render_scene(test)
    frames[0].save("test_frame_0.png")
    frames[len(frames)//2].save("test_frame_mid.png")
    frames[-1].save("test_frame_end.png")
    print(f"Rendered {len(frames)} frames.")
