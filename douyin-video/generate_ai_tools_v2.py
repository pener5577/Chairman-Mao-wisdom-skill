#!/usr/bin/env python3
"""
生成 AI 工具合集视频 V2 - 无 Emoji + 纯色背景 + 清晰文字
"""
import cv2
import numpy as np
import os

output_dir = "/root/.openclaw/workspace/douyin-video"
os.makedirs(output_dir, exist_ok=True)

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION_SEC = 18
TOTAL_FRAMES = FPS * DURATION_SEC

output_path = f"{output_dir}/ai_tools_v2.mp4"

COLORS = {
    'bg': (20, 25, 40),
    'white': (255, 255, 255),
    'blue': (50, 150, 255),
    'green': (50, 255, 150),
    'purple': (180, 100, 255),
    'orange': (255, 150, 50),
    'pink': (255, 100, 180),
    'yellow': (255, 230, 100),
    'gray': (120, 120, 120),
}

TOOLS = [
    {"num": "1", "name": "ChatGPT", "color": COLORS['green'], "desc": "写文案 做方案 查资料"},
    {"num": "2", "name": "Midjourney", "color": COLORS['purple'], "desc": "AI生成爆款图片"},
    {"num": "3", "name": "Notion AI", "color": COLORS['blue'], "desc": "笔记整理 周报写作"},
    {"num": "4", "name": "ElevenLabs", "color": COLORS['orange'], "desc": "AI智能配音"},
    {"num": "5", "name": "Perplexity", "color": COLORS['pink'], "desc": "精准搜索 无广告"},
]

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, FPS, (WIDTH, HEIGHT))

font = cv2.FONT_HERSHEY_SIMPLEX

def draw_centered_text(frame, text, y, font_scale, color, thickness=3):
    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
    x = (WIDTH - text_w) // 2
    # 阴影效果
    cv2.putText(frame, text, (x + 2, y + 2), font, font_scale, (0, 0, 0), thickness)
    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)
    return text_h

print(f"生成视频中... {TOTAL_FRAMES} 帧")

for frame_num in range(TOTAL_FRAMES):
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    progress = frame_num / TOTAL_FRAMES
    
    # ========== 镜头 1: 开场 (0-3秒) ==========
    if progress < 0.167:
        t = progress / 0.167
        # 渐变背景
        bg_color = tuple(int(c * t) for c in COLORS['bg'])
        frame[:, :] = bg_color
        
        # 主标题
        draw_centered_text(frame, "5 个 AI 工具", HEIGHT//2 - 60, 2.2, COLORS['white'], 5)
        draw_centered_text(frame, "效率翻 10 倍", HEIGHT//2 + 40, 1.8, COLORS['yellow'], 4)
        
        if t > 0.6:
            draw_centered_text(frame, "打工人必备", HEIGHT - 200, 1.2, COLORS['gray'], 2)
    
    # ========== 镜头 2: ChatGPT (3-7秒) ==========
    elif progress < 0.389:
        t = (progress - 0.167) / 0.222
        frame[:, :] = COLORS['bg']
        
        center_y = HEIGHT // 2 - 80
        
        # 圆形背景
        cv2.circle(frame, (WIDTH//2, center_y), 100, COLORS['green'], -1)
        cv2.circle(frame, (WIDTH//2, center_y), 100, COLORS['white'], 4)
        
        # 数字
        draw_centered_text(frame, "1", center_y, 2.5, COLORS['white'], 5)
        
        # 工具名称
        draw_centered_text(frame, "ChatGPT", center_y + 180, 2.0, COLORS['green'], 4)
        draw_centered_text(frame, "写文案 / 做方案 / 查资料", center_y + 250, 1.0, COLORS['gray'], 2)
    
    # ========== 镜头 3: Midjourney (7-11秒) ==========
    elif progress < 0.611:
        t = (progress - 0.389) / 0.222
        frame[:, :] = COLORS['bg']
        
        center_y = HEIGHT // 2 - 80
        
        # 渐变圆
        for r in range(100, 0, -10):
            alpha = r / 100
            color = tuple(int(c * alpha + 20 * (1-alpha)) for c in COLORS['purple'])
            cv2.circle(frame, (WIDTH//2, center_y), r, color, -1)
        cv2.circle(frame, (WIDTH//2, center_y), 100, COLORS['white'], 4)
        
        draw_centered_text(frame, "2", center_y, 2.5, COLORS['white'], 5)
        draw_centered_text(frame, "Midjourney", center_y + 180, 2.0, COLORS['purple'], 4)
        draw_centered_text(frame, "AI生成爆款图片", center_y + 250, 1.0, COLORS['gray'], 2)
    
    # ========== 镜头 4: 工具 3-5 (11-15秒) ==========
    elif progress < 0.833:
        t = (progress - 0.611) / 0.222
        frame[:, :] = COLORS['bg']
        
        # 三个工具并排
        spacing = WIDTH // 4
        for i, tool in enumerate(TOOLS[2:]):
            x = spacing * (i + 1)
            y = HEIGHT // 2 - 50
            
            cv2.circle(frame, (x, y), 50, tool['color'], -1)
            cv2.circle(frame, (x, y), 50, COLORS['white'], 3)
            draw_centered_text(frame, tool['num'], y, 1.8, COLORS['white'], 3)
            
            draw_centered_text(frame, tool['name'], y + 100, 1.0, tool['color'], 2)
            draw_centered_text(frame, tool['desc'], y + 140, 0.7, COLORS['gray'], 1)
    
    # ========== 镜头 5: 结尾 (15-18秒) ==========
    else:
        t = (progress - 0.833) / 0.167
        
        # 渐变背景 绿->深色
        for i in range(HEIGHT):
            ratio = i / HEIGHT
            color = (
                int(COLORS['green'][0] * ratio + COLORS['bg'][0] * (1-ratio)),
                int(COLORS['green'][1] * ratio + COLORS['bg'][1] * (1-ratio)),
                int(COLORS['green'][2] * ratio + COLORS['bg'][2] * (1-ratio))
            )
            cv2.line(frame, (0, i), (WIDTH, i), color)
        
        # 勾号圆圈
        cv2.circle(frame, (WIDTH//2, HEIGHT//2 - 80), 80, COLORS['white'], -1)
        # 对勾
        pts = np.array([(WIDTH//2 - 30, HEIGHT//2 - 80), (WIDTH//2 - 5, HEIGHT//2 - 50), (WIDTH//2 + 40, HEIGHT//2 - 120)], np.int32)
        cv2.polylines(frame, [pts], False, COLORS['green'], 10)
        
        draw_centered_text(frame, "学会这 5 个工具", HEIGHT//2 + 60, 1.5, COLORS['white'], 3)
        draw_centered_text(frame, "准时下班不是梦", HEIGHT//2 + 130, 1.5, COLORS['yellow'], 3)
        
        if t > 0.5:
            draw_centered_text(frame, "点赞支持", HEIGHT - 150, 1.0, COLORS['gray'], 2)
    
    out.write(frame)

out.release()

file_size = os.path.getsize(output_path)
print(f"视频生成完成: {output_path}")
print(f"大小: {file_size / 1024 / 1024:.2f} MB")
