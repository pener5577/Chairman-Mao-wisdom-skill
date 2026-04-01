#!/usr/bin/env python3
"""
生成 AI 工具视频 V3 - 修复中文显示 + 改善音频
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

output_path = f"{output_dir}/ai_tools_v3.mp4"

COLORS = {
    'bg': (25, 25, 45),
    'white': (255, 255, 255),
    'blue': (80, 160, 255),
    'green': (80, 255, 180),
    'purple': (200, 120, 255),
    'orange': (255, 180, 80),
    'pink': (255, 120, 200),
    'yellow': (255, 240, 120),
    'gray': (140, 140, 160),
}

TOOLS = [
    {"num": "1", "name": "ChatGPT", "desc": "写文案 做方案 查资料"},
    {"num": "2", "name": "Midjourney", "desc": "AI生成图片"},
    {"num": "3", "name": "Notion AI", "desc": "笔记整理 周报写作"},
    {"num": "4", "name": "ElevenLabs", "desc": "AI智能配音"},
    {"num": "5", "name": "Perplexity", "desc": "精准搜索"},
]

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, FPS, (WIDTH, HEIGHT))

# 使用默认字体
font = cv2.FONT_HERSHEY_SIMPLEX

def draw_centered_text(frame, text, y, font_scale, color, thickness=3):
    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
    x = (WIDTH - text_w) // 2
    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)

def draw_with_shadow(frame, text, y, font_scale, color, thickness=3):
    # 阴影
    cv2.putText(frame, text, (102, y+2), font, font_scale, (0, 0, 0), thickness)
    # 主体
    cv2.putText(frame, text, (100, y), font, font_scale, color, thickness)

print(f"生成视频中... {TOTAL_FRAMES} 帧")

for frame_num in range(TOTAL_FRAMES):
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    frame[:, :] = COLORS['bg']
    progress = frame_num / TOTAL_FRAMES
    
    # 镜头 1: 开场 (0-3秒)
    if progress < 0.2:
        draw_with_shadow(frame, "5 个 AI 工具", HEIGHT//2 - 40, 2.0, COLORS['white'], 5)
        draw_with_shadow(frame, "效率翻 10 倍", HEIGHT//2 + 40, 1.5, COLORS['yellow'], 3)
    
    # 镜头 2: ChatGPT (3-6秒)
    elif progress < 0.4:
        t = (progress - 0.2) / 0.2
        cv2.circle(frame, (WIDTH//2, HEIGHT//2 - 80), 90, COLORS['green'], -1)
        draw_centered_text(frame, "1", HEIGHT//2 - 80 + 20, 2.5, COLORS['white'], 5)
        draw_with_shadow(frame, "ChatGPT", HEIGHT//2 + 80, 1.8, COLORS['green'], 4)
        draw_centered_text(frame, "写文案 / 做方案 / 查资料", HEIGHT//2 + 140, 0.9, COLORS['gray'], 2)
    
    # 镜头 3: Midjourney (6-9秒)
    elif progress < 0.6:
        cv2.circle(frame, (WIDTH//2, HEIGHT//2 - 80), 90, COLORS['purple'], -1)
        draw_centered_text(frame, "2", HEIGHT//2 - 80 + 20, 2.5, COLORS['white'], 5)
        draw_with_shadow(frame, "Midjourney", HEIGHT//2 + 80, 1.8, COLORS['purple'], 4)
        draw_centered_text(frame, "AI生成爆款图片", HEIGHT//2 + 140, 0.9, COLORS['gray'], 2)
    
    # 镜头 4: 工具 3-5 (9-12秒)
    elif progress < 0.8:
        spacing = WIDTH // 4
        for i, tool in enumerate(TOOLS[2:]):
            x = spacing * (i + 1)
            y_pos = HEIGHT // 2 - 50
            cv2.circle(frame, (x, y_pos), 45, COLORS['blue' if i==0 else ('orange' if i==1 else 'pink')], -1)
            draw_centered_text(frame, tool['num'], y_pos, 1.5, COLORS['white'], 3)
            draw_centered_text(frame, tool['name'], y_pos + 90, 0.9, COLORS['white'], 2)
            draw_centered_text(frame, tool['desc'], y_pos + 130, 0.6, COLORS['gray'], 1)
    
    # 镜头 5: 结尾 (12-15秒)
    else:
        for i in range(HEIGHT):
            ratio = i / HEIGHT
            color = tuple(int(80 * ratio + 25 * (1-ratio)) for _ in range(3))
            cv2.line(frame, (0, i), (WIDTH, i), color)
        
        cv2.circle(frame, (WIDTH//2, HEIGHT//2 - 60), 70, COLORS['white'], -1)
        # 对勾
        pts = np.array([(WIDTH//2 - 25, HEIGHT//2 - 60), (WIDTH//2 - 5, HEIGHT//2 - 35), (WIDTH//2 + 35, HEIGHT//2 - 85)], np.int32)
        cv2.polylines(frame, [pts], False, COLORS['green'], 8)
        
        draw_with_shadow(frame, "学会这 5 个工具", HEIGHT//2 + 60, 1.3, COLORS['white'], 3)
        draw_with_shadow(frame, "准时下班不是梦", HEIGHT//2 + 120, 1.3, COLORS['yellow'], 3)
    
    out.write(frame)

out.release()

file_size = os.path.getsize(output_path)
print(f"视频生成完成: {output_path}")
print(f"大小: {file_size / 1024 / 1024:.2f} MB")
