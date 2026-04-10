from moviepy import ImageSequenceClip, concatenate_videoclips, VideoFileClip
import numpy as np
import os

def frames_to_clip(frames, fps=12):
    # Convert PIL images to numpy arrays for MoviePy
    np_frames = [np.array(f) for f in frames]
    return ImageSequenceClip(np_frames, fps=fps)

def compose_scene_clip(scene_frames, output_path, fps=12):
    """Save an individual scene's frames as an mp4 clip."""
    clip = frames_to_clip(scene_frames, fps=fps)
    clip.write_videofile(output_path, fps=fps, codec="libx264", logger=None)
    return output_path

def compose_video(clip_paths, output_path="output_video.mp4"):
    """
    Stitch together multiple individually saved scene mp4 paths into a final video.
    """
    clips = []
    for path in clip_paths:
        if os.path.exists(path):
            clips.append(VideoFileClip(path))
            
    if not clips:
        raise ValueError("No valid clip paths provided for concatenation.")
        
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(output_path, fps=12, codec="libx264", logger=None)
    
    # Close clips to prevent file lock issues
    for clip in clips:
        clip.close()
    
    return output_path

if __name__ == "__main__":
    # Test composer
    from PIL import Image
    frames = [Image.new("RGB", (1280, 720), (i, i, i)) for i in range(0, 255, 50)]
    clip1 = compose_scene_clip(frames, "test_clip1.mp4")
    clip2 = compose_scene_clip(frames, "test_clip2.mp4")
    final = compose_video([clip1, clip2], "test_final.mp4")
    print(f"Final video composed at: {final}")
