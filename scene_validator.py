"""
scene_validator.py — Validates and repairs Gemma's story JSON against scene_schema.py.
Coerces unknown values to nearest allowed values, fills missing fields with defaults.
"""
import difflib
from scene_schema import (
    ALLOWED_STYLES, ALLOWED_BACKGROUNDS, ALLOWED_MOTIONS,
    ALLOWED_OBJECTS, ALLOWED_TRANSITIONS, ALLOWED_SHAPES,
    DEFAULT_SCENE_DURATION, MIN_SCENE_DURATION, MAX_SCENE_DURATION,
    DEFAULT_STYLE, DEFAULT_BACKGROUND, DEFAULT_TRANSITION, DEFAULT_SHAPE, DEFAULT_MOTION
)


def _closest_match(value, allowed, default):
    """Find the closest allowed value using fuzzy matching, or return default."""
    if not value or not isinstance(value, str):
        return default
    value_lower = value.strip().lower().replace(" ", "_").replace("-", "_")
    if value_lower in allowed:
        return value_lower
    # Fuzzy match
    matches = difflib.get_close_matches(value_lower, allowed, n=1, cutoff=0.4)
    return matches[0] if matches else default


def _clamp(val, lo, hi):
    try:
        return max(lo, min(hi, int(val)))
    except (TypeError, ValueError):
        return lo


def validate_plan(plan):
    """
    Validate and repair a story plan dict.
    Returns (validated_plan, warnings_list).
    """
    warnings = []

    if not isinstance(plan, dict):
        return None, ["Plan is not a dict."]

    # Top-level fields
    plan.setdefault("title", "Untitled Animation")
    plan.setdefault("summary", "")
    plan.setdefault("total_duration", 12)

    # Style
    raw_style = plan.get("style", "")
    plan["style"] = _closest_match(raw_style, ALLOWED_STYLES, DEFAULT_STYLE)
    if plan["style"] != raw_style:
        warnings.append(f"Style '{raw_style}' → '{plan['style']}'")

    # Scenes
    scenes = plan.get("scenes", [])
    if not isinstance(scenes, list) or len(scenes) == 0:
        warnings.append("No scenes found. Creating a fallback single scene.")
        scenes = [{
            "scene_number": 1,
            "duration": DEFAULT_SCENE_DURATION,
            "background": DEFAULT_BACKGROUND,
            "characters": [{"id": "character", "shape": DEFAULT_SHAPE, "color_hint": "blue"}],
            "action_summary": plan.get("summary", "A simple scene"),
            "key_objects": [],
            "intended_motion": ["idle"],
            "caption": plan.get("summary", ""),
            "transition": DEFAULT_TRANSITION
        }]

    validated_scenes = []
    for i, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            warnings.append(f"Scene {i+1} is not a dict, skipping.")
            continue

        vs = {}
        vs["scene_number"] = i + 1
        vs["duration"] = _clamp(scene.get("duration", DEFAULT_SCENE_DURATION),
                                MIN_SCENE_DURATION, MAX_SCENE_DURATION)

        # Background
        raw_bg = scene.get("background", "")
        vs["background"] = _closest_match(raw_bg, ALLOWED_BACKGROUNDS, DEFAULT_BACKGROUND)
        if vs["background"] != raw_bg and raw_bg:
            warnings.append(f"Scene {i+1} background '{raw_bg}' → '{vs['background']}'")

        # Characters
        raw_chars = scene.get("characters", [])
        if not isinstance(raw_chars, list) or len(raw_chars) == 0:
            raw_chars = [{"id": "character", "shape": DEFAULT_SHAPE, "color_hint": "blue"}]
            warnings.append(f"Scene {i+1}: no characters, using default.")

        validated_chars = []
        for ch in raw_chars:
            if not isinstance(ch, dict):
                continue
            vc = {
                "id": ch.get("id", "character"),
                "shape": _closest_match(ch.get("shape", ""), ALLOWED_SHAPES, DEFAULT_SHAPE),
                "color_hint": ch.get("color_hint", "blue")
            }
            validated_chars.append(vc)
        vs["characters"] = validated_chars if validated_chars else [
            {"id": "character", "shape": DEFAULT_SHAPE, "color_hint": "blue"}
        ]

        # Action summary
        vs["action_summary"] = scene.get("action_summary", scene.get("action", ""))

        # Key objects — coerce each to allowed
        raw_objs = scene.get("key_objects", [])
        if not isinstance(raw_objs, list):
            raw_objs = []
        vs["key_objects"] = [
            _closest_match(o, ALLOWED_OBJECTS, None) for o in raw_objs
        ]
        vs["key_objects"] = [o for o in vs["key_objects"] if o is not None]

        # Intended motion — coerce each to allowed
        raw_motions = scene.get("intended_motion", [])
        if not isinstance(raw_motions, list):
            # Try to read old-style single "motion" field
            old_motion = scene.get("motion", DEFAULT_MOTION)
            raw_motions = [old_motion]
        if len(raw_motions) == 0:
            raw_motions = [DEFAULT_MOTION]
        vs["intended_motion"] = []
        for m in raw_motions:
            matched = _closest_match(m, ALLOWED_MOTIONS, None)
            if matched:
                vs["intended_motion"].append(matched)
        if not vs["intended_motion"]:
            vs["intended_motion"] = [DEFAULT_MOTION]

        # Caption
        vs["caption"] = scene.get("caption", "")

        # Transition
        raw_trans = scene.get("transition", "")
        vs["transition"] = _closest_match(raw_trans, ALLOWED_TRANSITIONS, DEFAULT_TRANSITION)

        validated_scenes.append(vs)

    plan["scenes"] = validated_scenes
    plan["total_duration"] = sum(s["duration"] for s in validated_scenes)

    return plan, warnings


if __name__ == "__main__":
    import json
    test_plan = {
        "title": "Test",
        "style": "stickfigure",  # typo — should be coerced
        "scenes": [
            {
                "duration": 10,  # too long — should be clamped
                "background": "park",  # not in allowed — should be coerced
                "characters": [{"id": "kid", "shape": "round_head"}],  # bad shape
                "motion": "walking",  # old format
                "caption": "Hello"
            }
        ]
    }
    validated, warns = validate_plan(test_plan)
    print("Validated:", json.dumps(validated, indent=2))
    print("Warnings:", warns)
