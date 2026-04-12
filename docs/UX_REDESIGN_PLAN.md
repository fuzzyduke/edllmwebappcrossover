# UX Redesign & 5-Step Workflow Plan (Manual Scene Builder)

## Problem Diagnosis
Based on UX analysis of the Manual Scene Builder, the following issues were identified:
1. **Hidden Input Flow**: The primary multi-scene import functions (Bulk Paste & File Upload) are located inside a collapsed `gr.Accordion`. This breaks the expected entry-point visibility.
2. **Auto-Select Desync Bug**: Programmatically updating the `gr.Dropdown` after importing or adding a scene does not trigger its `.change()` event in Gradio automatically. This leaves the Inspector pane blank ("No scene selected") giving the illusion that the import failed.
3. **Lack of Global Visibility**: For multi-scene projects (e.g., 10+ scenes), a simple Dropdown is insufficient for reviewing the scope of the generated project.
4. **Silent Error Output**: Importing lacks a definitive success message, leaving the user guessing the state of the system.

## Proposed 5-Step Restructure

To resolve this, the layout of `manual_scene_ui.py` should be rebuilt into a sequential, top-to-bottom and left-to-right 5-step workflow.

### Step 1: Import or Paste Script (Top Container)
*   **Action**: Delete the `gr.Accordion`. Elevate the import UI to a dedicated top-level `gr.Row` titled "Step 1: Import or Paste Script".
*   **Action**: Add an explicit `import_status_box` (e.g., `"✅ Imported 10 scenes. Parsed from TXT successfully. Scene 1 auto-selected"`).

### Step 2: Review Parsed Scenes (New Dataframe)
*   **Action**: Add a read-only `gr.Dataframe` directly beneath Step 1.
*   **Purpose**: Allows users to see all imported scenes at a glance. The dataframe lists `[Scene #, Brief, Status, Duration]` and rebuilds dynamically whenever an import or edit occurs.

### Step 3: Edit Selected Scene (Left Pane)
*   **Action**: Move the Dropdown and the entire **Scene Inspector** into a dedicated left-hand pane.
*   **Fix**: Chain `.then(sync_inspector, ...)` onto the `btn_import.click` and `btn_add.click` events to physically force the Inspector UI to populate with Scene 1's data immediately, fixing the blank screen bug.

### Step 4: Render Controls (Right Pane - Top)
*   **Action**: Group the `🎨 Render This Scene` and `🎬 Render All & Stitch Movie` buttons together.
*   **Support**: Include the dedicated `debugger_log` multiline textbox right beneath the buttons to explicitly catch specific scene errors without silent failures.

### Step 5: Final Movie (Right Pane - Bottom)
*   **Action**: The `gr.Video(label="Final Movie")` component acts as the visual terminus of the 5-step flow.
