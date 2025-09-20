# 📚 Wikipedia Word Video Generator

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Playwright](https://img.shields.io/badge/Playwright-Browser_Automation-orange)
![MoviePy](https://img.shields.io/badge/MoviePy-Video_Editing-purple)

Generate short video clips of a specific word appearing on any Wikipedia page.  
This project uses **Python**, **Playwright**, **Pillow**, and **MoviePy** to create visually appealing word-focused videos.  

---

## 🚀 Features

- Find **exact instances** of a word on a Wikipedia page.
- Capture **centered screenshots** of the word.
- Automatically crop, resize, and prepare images for video.
- Generate a **short looping video** with customizable duration.
- Fully automated workflow in Python.

---

## 🛠️ Installation

1. Clone the repository:

```bash
git clone https://github.com/pranavkoirala/wikipedia-text-tool.git
cd wikipedia-text-tool
```

2. Install dependencies:

```bash
pip install playwright pillow moviepy
python -m playwright install
```

## ⚡ Usage

Run the script:
```bash
python main.py
```

You will be prompted to enter:

1. Target word – the word you want to highlight.
2. Wikipedia URL – full URL of the page to scrape.
3. Video duration – total length in seconds.

The script will:

- Save cropped screenshots to screenshots/.
- Save the final video in clips/ as <word>.mp4.

## 🎨 Customization

- Screen size: SCREEN_WIDTH and SCREEN_HEIGHT in the script.

- Zoom crop size: ZOOM_WIDTH and ZOOM_HEIGHT.

- FPS: Frames per second for the video.

## 📂 Output Structure
```bash
project-folder/
├─ clips/               # Final video output
├─ screenshots/         # Cropped word images
├─ main.py              # Main Python script
```
