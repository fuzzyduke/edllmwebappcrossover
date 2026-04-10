"""
render_normalizer.py — Converts validated story JSON into strict render-scene JSON.
Maps scenes to templates, assigns coordinates, and converts intended_motion into timed beats.
"""
import copy
from scene_schema import WIDTH, HEIGHT, resolve_color
from scene_templates import TEMPLATES, match_template


def normalize_scene(story_scene):
    """
    Transform a single validated story scene into a render-ready scene dict.
    Returns (render_scene, template_name, warnings).
    """
    warnings = []

    # 1. Match to a template
    template_name = match_template(story_scene)
    template = copy.deepcopy(TEMPLATES[template_name])

    render = {
        "scene_number": story_scene["scene_number"],
        "duration": story_scene["duration"],
        "background": story_scene.get("background", template["background"]),
        "caption": story_scene.get("caption", ""),
        "transition": story_scene.get("transition", "cut"),
    }

    # 2. Place characters
    chars = story_scene.get("characters", [])
    render_chars = []
    for i, ch in enumerate(chars):
        if i == 0:
            pos = copy.deepcopy(template["character_start"])
        else:
            # Additional characters offset to the right
            pos = {
                "x": template["character_start"]["x"] + (i * 250),
                "y": template["character_start"]["y"],
            }
        render_chars.append({
            "id": ch.get("id", f"char_{i}"),
            "shape": ch.get("shape", "circle_face"),
            "color_hint": ch.get("color_hint", "blue"),
            "position": pos,
        })
    render["characters"] = render_chars

    # 3. Place objects — merge template defaults with story key_objects
    render_objects = []
    used_types = set()

    # Template default objects first
    for obj in template.get("default_objects", []):
        render_objects.append({
            "id": obj["type"],
            "type": obj["type"],
            "position": copy.deepcopy(obj["position"]),
        })
        used_types.add(obj["type"])

    # Then add story key_objects that aren't already placed
    story_objs = story_scene.get("key_objects", [])
    next_x = 600
    for obj_type in story_objs:
        if obj_type not in used_types:
            render_objects.append({
                "id": obj_type,
                "type": obj_type,
                "position": {"x": next_x, "y": int(HEIGHT * 0.62)},
            })
            used_types.add(obj_type)
            next_x += 180

    render["objects"] = render_objects

    # 4. Build beats from intended_motion
    intended = story_scene.get("intended_motion", [])
    template_beats = template.get("default_beats", [])

    if intended and len(intended) > 0:
        # Distribute intended motions evenly across the duration
        beats = []
        n = len(intended)
        for j, motion in enumerate(intended):
            time_pct = j / max(n, 1)
            beat = {"time_pct": round(time_pct, 2), "pose": motion}

            # If this is a walk and there's a target from template, use it
            if motion in ("walk_left", "walk_right"):
                # Look for a matching template beat with target_x
                for tb in template_beats:
                    if tb.get("pose") == motion and "target_x" in tb:
                        beat["target_x"] = tb["target_x"]
                        break
                else:
                    # Default walk targets
                    if motion == "walk_right":
                        beat["target_x"] = min(
                            render_chars[0]["position"]["x"] + 300, WIDTH - 100
                        ) if render_chars else 600
                    else:
                        beat["target_x"] = max(
                            render_chars[0]["position"]["x"] - 300, 100
                        ) if render_chars else 200

            beats.append(beat)
        render["beats"] = beats
    else:
        # Fall back to template beats
        render["beats"] = template_beats
        warnings.append(f"Scene {render['scene_number']}: using template beats (no intended_motion).")

    return render, template_name, warnings


def normalize_plan(validated_plan):
    """
    Convert an entire validated story plan into a list of render-scene dicts.
    Returns (render_scenes, template_names, all_warnings).
    """
    render_scenes = []
    template_names = []
    all_warnings = []

    for scene in validated_plan.get("scenes", []):
        render_scene, tname, warns = normalize_scene(scene)
        render_scenes.append(render_scene)
        template_names.append(tname)
        all_warnings.extend(warns)

    return render_scenes, template_names, all_warnings


if __name__ == "__main__":
    import json
    test_scene = {
        "scene_number": 1,
        "duration": 4,
        "background": "bedroom",
        "characters": [{"id": "robot", "shape": "rectangle_face", "color_hint": "gray"}],
        "action_summary": "robot wakes up from charging mat",
        "key_objects": ["charging_mat"],
        "intended_motion": ["sleeping", "eyes_open", "stretch", "stand"],
        "caption": "Beep boop... Awake!",
        "transition": "cut"
    }
    render, tname, warns = normalize_scene(test_scene)
    print(f"Template: {tname}")
    print(json.dumps(render, indent=2))
    print("Warnings:", warns)
