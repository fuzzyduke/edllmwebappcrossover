"""
ui_help_content.py — Extended Markdown help content for the Text-to-Video tab modes.
"""

MODE_HELP = """
## Text-to-Video Workflow Modes

This feature converts your written ideas into simple concept animations.

### A. Auto Split Mode
*   **What it does:** Type one large creative prompt. The system uses local AI to automatically slice the prompt into N scenes.
*   **Best for:** Quick generation, casual brainstorming, simple uninterrupted flows.

### B. Manual Scene Builder Mode (Recommended)
*   **What it does:** Affords you complete directorial control. You explicitly author and configure each scene card in the project.
*   **Best for:** Highly structured shorts, iterating on a single failed scene without re-rendering the entire video, working with imported scripts.

**Features of Manual Mode:**
*   Add, duplicate, reorder, or delete scenes.
*   Write a one-line brief or a full paragraph for each scene.
*   Optional Overrides: You can force a specific background or style per-scene.
*   **Per-Scene Rerendering**: Render one scene and see if you like it before rendering the rest of the movie!
"""

IMPORT_HELP_MODAL = """
## How to Import a Scene Script

You can rapidly populate the scene builder by uploading a `.txt` or `.json` file, or by pasting a bulk brief directly.

### 1. TXT Format
The parser reads paragraphs as independent scenes. You can separate scenes with a blank line, or use explicit headers.

**Example 1 (Paragraphs):**
```
A boy wakes up and looks out the window.

He gets dressed and rushes to school.

He arrives in class and smiles at his friend.
```

**Example 2 (Headers):**
```
Scene 1
A boy wakes up and looks out the window.

Scene 2
He gets dressed and rushes to school.
```

### 2. JSON Format
You can supply a highly rigid script by uploading a `.json` array or project object.
```json
{
  "title": "Simple Story",
  "style": "stick_figure",
  "scenes": [
    {
      "scene_number": 1,
      "brief": "A boy wakes up and looks out the window.",
      "duration": 4
    },
    {
      "scene_number": 2,
      "brief": "He gets dressed and rushes to school.",
      "duration": 4
    }
  ]
}
```

*Note: You can still manually edit and customize imported scenes before rendering.*
"""
