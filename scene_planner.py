"""
scene_planner.py — Sends user prompts to Gemma via Ollama and receives constrained story JSON.
Uses a heavily structured system prompt with allowed enums and a full example.
"""
import requests
import json
import re
from scene_schema import (
    ALLOWED_STYLES, ALLOWED_BACKGROUNDS, ALLOWED_MOTIONS,
    ALLOWED_OBJECTS, ALLOWED_TRANSITIONS, ALLOWED_SHAPES
)

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3.2:latest"

SYSTEM_PROMPT = f"""You are a Scene Planner for a simple animated storyboard generator.
Your job: convert a user's story prompt into a structured JSON scene plan.

RULES:
- Return ONLY valid JSON. No markdown fences. No explanation. No text outside the JSON object.
- Use ONLY the allowed values listed below. Do not invent new values.
- Keep scenes short: 3 to 5 seconds each.
- Keep total duration 10 to 15 seconds for 3 scenes.

ALLOWED VALUES:
- style: {json.dumps(ALLOWED_STYLES)}
- background: {json.dumps(ALLOWED_BACKGROUNDS)}
- intended_motion (array of poses in order): {json.dumps(ALLOWED_MOTIONS)}
- key_objects: {json.dumps(ALLOWED_OBJECTS)}
- transition: {json.dumps(ALLOWED_TRANSITIONS)}
- character shape: {json.dumps(ALLOWED_SHAPES)}

SCHEMA:
{{
  "title": "short title string",
  "summary": "one sentence summary",
  "style": "one of allowed styles",
  "total_duration": integer seconds,
  "scenes": [
    {{
      "scene_number": integer,
      "duration": integer 3-5,
      "background": "one of allowed backgrounds",
      "characters": [
        {{"id": "name", "shape": "one of allowed shapes", "color_hint": "color name"}}
      ],
      "action_summary": "short description of what happens",
      "key_objects": ["from allowed objects list"],
      "intended_motion": ["from allowed motions list, in order"],
      "caption": "text to display at bottom of scene",
      "transition": "one of allowed transitions"
    }}
  ]
}}

EXAMPLE OUTPUT:
{{
  "title": "Robot's Morning Routine",
  "summary": "A robot wakes up, recharges, and cleans a room.",
  "style": "stick_figure",
  "total_duration": 13,
  "scenes": [
    {{
      "scene_number": 1,
      "duration": 4,
      "background": "bedroom",
      "characters": [{{"id": "robot", "shape": "rectangle_face", "color_hint": "gray"}}],
      "action_summary": "robot wakes up from charging mat",
      "key_objects": ["charging_mat"],
      "intended_motion": ["sleeping", "eyes_open", "stretch", "stand"],
      "caption": "Beep boop... Awake!",
      "transition": "cut"
    }},
    {{
      "scene_number": 2,
      "duration": 5,
      "background": "charging_room",
      "characters": [{{"id": "robot", "shape": "rectangle_face", "color_hint": "gray"}}],
      "action_summary": "robot walks to charger and powers up",
      "key_objects": ["charging_station", "gauge_bar"],
      "intended_motion": ["walk_right", "plug_in", "glow"],
      "caption": "Recharging batteries...",
      "transition": "cut"
    }},
    {{
      "scene_number": 3,
      "duration": 4,
      "background": "cleaning_room",
      "characters": [{{"id": "robot", "shape": "rectangle_face", "color_hint": "gray"}}],
      "action_summary": "robot collects scattered items into a box",
      "key_objects": ["square_item", "circle_item", "triangle_item", "box"],
      "intended_motion": ["look_down", "bend_down", "pick_up", "place_object", "stand_proud"],
      "caption": "Time to clean up!",
      "transition": "fade"
    }}
  ]
}}

Now generate the JSON for the user's prompt. Remember: ONLY JSON, no other text."""


def plan_scenes(prompt):
    """Send the user prompt to Gemma and return parsed story JSON, or None on failure."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=600)
        if response.status_code == 200:
            result = response.json()
            content = result['message']['content'].strip()

            # Extract JSON object even if wrapped in markdown or extra text
            if "{" in content and "}" in content:
                content = content[content.find("{"):content.rfind("}") + 1]

            content = re.sub(r'```json\n?|\n?```', '', content).strip()

            try:
                return json.loads(content)
            except json.JSONDecodeError as je:
                print(f"JSON Parse Error: {je} | Raw: {content[:200]}...")
                return None
        else:
            print(f"Ollama error: {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        print("Scene planning timed out after 600s.")
        return None
    except Exception as e:
        print(f"Scene planning failed: {e}")
        return None

SINGLE_SCENE_PROMPT = f"""You are a Single Scene Planner for an animated storyboard generator.
Your job: output the structured JSON for exactly ONE scene.

RULES:
- Return ONLY valid JSON. No markdown fences. No explanation.
- Use ONLY the allowed values listed below.
- Keep the action concise.

ALLOWED VALUES:
- background: {json.dumps(ALLOWED_BACKGROUNDS)}
- intended_motion (array of poses in order): {json.dumps(ALLOWED_MOTIONS)}
- key_objects: {json.dumps(ALLOWED_OBJECTS)}
- transition: {json.dumps(ALLOWED_TRANSITIONS)}
- character shape: {json.dumps(ALLOWED_SHAPES)}

SCHEMA:
{{
  "scene_number": integer,
  "duration": integer,
  "background": "one of allowed backgrounds",
  "characters": [
    {{"id": "name", "shape": "one of allowed shapes", "color_hint": "color name"}}
  ],
  "action_summary": "short description of what happens",
  "key_objects": ["from allowed objects list"],
  "intended_motion": ["from allowed motions list, in order"],
  "caption": "text to display at bottom of scene",
  "transition": "one of allowed transitions"
}}

Generate the JSON for this scene brief. Remember: ONLY JSON, no other text."""

def plan_single_scene(scene_brief, scene_num=1, duration=4):
    """Specific planner that generates a single scene dictionary."""
    messages = [
        {"role": "system", "content": SINGLE_SCENE_PROMPT},
        {"role": "user", "content": f"Scene Number: {scene_num}, Duration: {duration}s. Brief:\n{scene_brief}"}
    ]
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        if response.status_code == 200:
            result = response.json()
            content = result['message']['content'].strip()
            
            # Extract JSON object
            if "{" in content and "}" in content:
                content = content[content.find("{"):content.rfind("}") + 1]
            content = re.sub(r'```json\n?|\n?```', '', content).strip()
            
            try:
                scene_dict = json.loads(content)
                # Ensure the correct scene number is enforced
                scene_dict["scene_number"] = scene_num
                # Ensure duration is enforced if missing
                if "duration" not in scene_dict:
                    scene_dict["duration"] = duration
                return scene_dict
            except json.JSONDecodeError as je:
                print(f"JSON Parse Error (Single Scene): {je}")
                return None
        return None
    except Exception as e:
        print(f"Single Scene planning failed: {e}")
        return None

if __name__ == "__main__":
    test_prompt = "A robot wakes up, charges its battery, then helps clean the room."
    plan = plan_scenes(test_prompt)
    if plan:
        print(json.dumps(plan, indent=2))
    else:
        print("Planning failed.")
