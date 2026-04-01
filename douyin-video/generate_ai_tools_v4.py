#!/usr/bin/env python3
"""
AI Tools Video V4 - English Only (避免中文显示问题)
"""
import cv2
import numpy as np
import os

output_dir = "/root/.openclaw/workspace/douyin-video"
os.makedirs(output_dir, exist_ok=True)

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION_SEC = 15
TOTAL_FRAMES = FPS * DURATION_SEC

output_path = f"{output_dir}/ai_tools_v4.mp4"

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (80, 255, 150)
PURPLE = (180, 100, 255)
BLUE = (80, 150, 255)
ORANGE = (255, 170, 80)
PINK = (255, 100, 180)
YELLOW = (255, 230, 100)
GRAY = (130, 130, 150)
BG = (20, 20, 35)

TOOLS = [
    ("1", "ChatGPT", "Write / Plan / Research", GREEN),
    ("2", "Midjourney", "AI Image Generation", PURPLE),
    ("3", "Notion AI", "Notes & Reports", BLUE),
    ("4", "ElevenLabs", "AI Voice", ORANGE),
    ("5", "Perplexity", "Smart Search", PINK),
]

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, FPS, (WIDTH, HEIGHT))
font = cv2.FONT_HERSHEY_SIMPLEX

def draw_text(frame, text, y, scale, color, thick=3):
    (tw, th), _ = cv2.getTextSize(text, font, scale, thick)
    x = (WIDTH - tw) // 2
    cv2.putText(frame, text, (x+2, y+2), font, scale, BLACK, thick)
    cv2.putText(frame, text, (x, y), font, scale, color, thick)

print(f"Generating video... {TOTAL_FRAMES} frames")

for f in range(TOTAL_FRAMES):
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    frame[:] = BG
    p = f / TOTAL_FRAMES
    
    # Scene 1: Opening (0-3s)
    if p < 0.2:
        draw_text(frame, "5 AI TOOLS", HEIGHT//2 - 50, 2.2, WHITE, 5)
        draw_text(frame, "10x EFFICIENCY", HEIGHT//2 + 30, 1.8, YELLOW, 4)
    
    # Scene 2: ChatGPT (3-6s)
    elif p < 0.4:
        cv2.circle(frame, (WIDTH//2, HEIGHT//2 - 80), 95, GREEN, -1)
        draw_text(frame, "1", HEIGHT//2 - 70, 2.8, WHITE, 6)
        draw_text(frame, "ChatGPT", HEIGHT//2 + 90, 2.0, GREEN, 4)
        draw_text(frame, "Write / Plan / Research", HEIGHT//2 + 150, 1.0, GRAY, 2)
    
    # Scene 3: Midjourney (6-9s)
    elif p < 0.6:
        cv2.circle(frame, (WIDTH//2, HEIGHT//2 - 80), 95, PURPLE, -1)
        draw_text(frame, "2", HEIGHT//2 - 70, 2.8, WHITE, 6)
        draw_text(frame, "Midjourney", HEIGHT//2 + 90, 2.0, PURPLE, 4)
        draw_text(frame, "AI Image Generation", HEIGHT//2 + 150, 1.0, GRAY, 2)
    
    # Scene 4: Tools 3-5 (9-12s)
    elif p < 0.8:
        sp = WIDTH // 4
        for i, (num, name, desc, color) in enumerate(TOOLS[2:]):
            x = sp * (i + 1)
            y = HEIGHT // 2 - 40
            cv2.circle(frame, (x, y), 50, color, -1)
            draw_text(frame, num, y, 1.8, WHITE, 4)
            draw_text(frame, name, y + 95, 1.0, WHITE, 2)
            draw_text(frame, desc, y + 135, 0.7, GRAY, 1)
    
    # Scene 5: Ending (12-15s)
    else:
        for i in range(HEIGHT):
            r = i / HEIGHT
            c = tuple(int(80*r + 20*(1-r)) for _ in range(3))
            cv2.line(frame, (0, i), (WIDTH, i), c)
        
        cv2.circle(frame, (WIDTH//2, HEIGHT//2 - 50), 75, WHITE, -1)
        pts = np.array([(WIDTH//2 - 25, HEIGHT//2 - 50), (WIDTH//2 - 5, HEIGHT//2 - 25), (WIDTH//2 + 35, HEIGHT//2 - 75)], np.int32)
        cv2.polylines(frame, [pts], False, GREEN, 10)
        
        draw_text(frame, "Learn These 5 Tools", HEIGHT//2 + 70, 1.4, WHITE, 3)
        draw_text(frame, "Leave Work On Time", HEIGHT//2 + 130, 1.4, YELLOW, 3)
    
    out.write(frame)

out.release()
size = os.path.getsize(output_path)
print(f"Video: {output_path} ({size/1024/1024:.2f}MB)")
