HELP_TEXT = """
# How Text to Video Works

### A. What this feature does
This tool turns your written idea into a short simple animation. It uses Gemma locally to understand your prompt and break it into scenes, then uses a lightweight animation engine to render a short concept video.

### B. The flow
1.  **Input**: You type a short story or scene sequence.
2.  **Story Planning**: Gemma turns it into a structured story plan.
3.  **Normalization**: The system normalizes that plan into renderable scenes with strict coordinates and templates.
4.  **Scene Rendering**: Each scene is rendered as a simple animated clip and previewed separately.
5.  **Final Stitching**: The clips are stitched into a final concept video.

### C. Best prompt style
Prompts work best when they describe a clear sequence:
*   Who is in the scene
*   What happens first
*   What changes next
*   What happens last

**Example**: "A robot wakes up, charges its battery, then helps clean the room."

### D. Visual style
This feature is built for **concept videos**, not cinematic realism.
Characters appear as:
*   Stick figures
*   Simple geometric people
*   Flat animated shapes
*   Storyboard-like scenes

### E. Limitations
*   Visuals are intentionally simplified (concept animation).
*   Character detail is minimal.
*   Animation uses basic to medium beat-driven motion.
*   No audio in this version.
*   Multiple scenes are stitched, but each uses a template-based layout.

### F. Sample breakdown
**Input**: "A robot wakes up, charges its battery, then helps clean the room."

**Story Plan**:
*   *Scene 1*: robot wakes up from bed (wake_up template)
*   *Scene 2*: runs to charging station to power up (charging template)
*   *Scene 3*: collects scattered items into a box (cleaning template)

**Output**: A set of individually rendered scene clips, followed by a final stitched animation using simple shapes, captions, and distinct scene assets.
"""
