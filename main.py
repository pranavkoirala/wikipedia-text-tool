import shutil
import os
import random
from playwright.sync_api import sync_playwright
from PIL import Image
from moviepy import ImageClip, concatenate_videoclips
import time

# ---------------- User Input ----------------
output_dir_screenshots = "screenshots"
output_dir_clip = "clips"
word_to_find = input("Enter the target word: ").strip()
wikipedia_url = input("Enter the full Wikipedia URL: ").strip()
duration_sec = float(input("Enter the total video duration in seconds: "))

# Clear old screenshots
if output_dir_screenshots and os.path.exists(output_dir_screenshots):
    shutil.rmtree(output_dir_screenshots)

if output_dir_clip and os.path.exists(output_dir_clip):
    shutil.rmtree(output_dir_clip)

os.makedirs(output_dir_clip, exist_ok=True)
os.makedirs(output_dir_screenshots, exist_ok=True)

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1440
MAX_INSTANCES = 12
ZOOM_WIDTH = 400
ZOOM_HEIGHT = 300
FPS = 6  # 6 images per second

# ---------------- Take Screenshots ----------------
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(wikipedia_url)
    page.wait_for_load_state("networkidle")
    time.sleep(3)

    # Get text node positions
    elements = page.evaluate(
        f"""
        () => {{
            const nodes = [];
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            const regex = new RegExp("\\\\b{word_to_find}\\\\b", "gi");
            while(walker.nextNode()) {{
                const node = walker.currentNode;
                const matches = [...node.nodeValue.matchAll(regex)];
                for (const match of matches) {{
                    const idx = match.index;
                    if(idx !== null && node.parentElement.offsetWidth > 0 && node.parentElement.offsetHeight > 0) {{
                        const range = document.createRange();
                        range.setStart(node, idx);
                        range.setEnd(node, idx + match[0].length);
                        const rect = range.getBoundingClientRect();
                        nodes.push({{
                            x: rect.x + window.scrollX,
                            y: rect.y + window.scrollY,
                            width: rect.width,
                            height: rect.height
                        }});
                    }}
                }}
            }}
            return nodes;
        }}
        """
    )


    # Remove duplicates
    seen = set()
    unique_elements = []
    for el in elements:
        key = (round(el['x']), round(el['y']))
        if key not in seen:
            seen.add(key)
            unique_elements.append(el)

    print(f"Found {len(unique_elements)} exact instances of '{word_to_find}'")

    for i, box in enumerate(unique_elements[:MAX_INSTANCES]):
        center_x = box['x'] + box['width'] / 2
        center_y = box['y'] + box['height'] / 2

        # Scroll to roughly center the word on the screen
        page.evaluate(f"window.scrollTo({{ top: {center_y - SCREEN_HEIGHT//2}, behavior: 'auto' }});")
        page.wait_for_timeout(200)  # small pause to render

        # Take full-page screenshot
        full_path = os.path.join(output_dir_screenshots, f"{word_to_find}_{i}_full.png")
        page.screenshot(path=full_path, full_page=True)

        img = Image.open(full_path)
        left = max(int(center_x - ZOOM_WIDTH/2), 0)
        upper = max(int(center_y - ZOOM_HEIGHT/2), 0)
        right = min(left + ZOOM_WIDTH, img.width)
        lower = min(upper + ZOOM_HEIGHT, img.height)
        cropped = img.crop((left, upper, right, lower))

        # Resize to final dimensions while preserving aspect ratio
        cropped_ratio = cropped.width / cropped.height
        target_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
        if cropped_ratio > target_ratio:
            new_width = SCREEN_WIDTH
            new_height = int(SCREEN_WIDTH / cropped_ratio)
        else:
            new_height = SCREEN_HEIGHT
            new_width = int(SCREEN_HEIGHT * cropped_ratio)
        cropped = cropped.resize((new_width, new_height), Image.LANCZOS)

        final_img = Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT), (255, 255, 255))
        final_img.paste(cropped, ((SCREEN_WIDTH - new_width)//2, (SCREEN_HEIGHT - new_height)//2))

        final_path = os.path.join(output_dir_screenshots, f"{word_to_find}_{i}.png")
        final_img.save(final_path)
        os.remove(full_path)
        print(f"Saved screenshot: {final_path}")

    browser.close()

# ---------------- Create Video ----------------
image_files = [os.path.join(output_dir_screenshots, f) for f in os.listdir(output_dir_screenshots)
               if f.startswith(word_to_find) and f.endswith(".png")]

if not image_files:
    raise ValueError("No images found for the video.")

num_frames_needed = int(duration_sec * FPS)

# Randomly select images with replacement to fill the video
selected_images = [random.choice(image_files) for _ in range(num_frames_needed)]

# Create ImageClips
clips = [ImageClip(img).with_duration(1/FPS) for img in selected_images]

# Concatenate and write video
video = concatenate_videoclips(clips, method="compose")
video_output_path = os.path.join(output_dir_clip, f"{word_to_find}.mp4")

video.write_videofile(video_output_path, fps=FPS)

print(f"Video saved to {video_output_path}")
