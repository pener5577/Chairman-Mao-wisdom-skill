#!/usr/bin/env python3
"""
生成 AI 工具合集视频 - 抖音竖屏 9:16
"""
import cv2
import numpy as np
import os

# 输出目录
output_dir = "/root/.openclaw/workspace/douyin-video"
os.makedirs(output_dir, exist_ok=True)

# 抖音竖屏分辨率
WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION_SEC = 18
TOTAL_FRAMES = FPS * DURATION_SEC

output_path = f"{output_dir}/ai_tools_video.mp4"

# 颜色配置
COLORS = {
    'bg': (20, 25, 40),
    'white': (255, 255, 255),
    'blue': (50, 150, 255),
    'green': (50, 255, 150),
    'purple': (180, 100, 255),
    'orange': (255, 150, 50),
    'pink': (255, 100, 180),
    'yellow': (255, 230, 100),
    'gray': (150, 150, 150),
    'dark': (30, 35, 50),
}

# AI 工具列表
TOOLS = [
    {"name": "ChatGPT", "emoji": "🤖", "color": COLORS['green'], "desc": "写文案、做方案"},
    {"name": "Midjourney", "emoji": "🎨", "color": COLORS['purple'], "desc": "AI 生成图片"},
    {"name": "Notion AI", "emoji": "📝", "color": COLORS['blue'], "desc": "笔记整理"},
    {"name": "ElevenLabs", "emoji": "🎙️", "color": COLORS['orange'], "desc": "AI 配音"},
    {"name": "Perplexity", "emoji": "🔍", "color": COLORS['pink'], "desc": "精准搜索"},
]

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, FPS, (WIDTH, HEIGHT))

font = cv2.FONT_HERSHEY_SIMPLEX

def draw_text_centered(frame, text, y, font_scale, color, thickness=3, shadow=True):
    """居中绘制文字"""
    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
    x = (WIDTH - text_w) // 2
    
    if shadow:
        cv2.putText(frame, text, (x + 3, y + 3), font, font_scale, (0, 0, 0), thickness)
    
    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)
    return text_h

def draw_circle_button(frame, x, y, radius, color, emoji_text):
    """绘制圆形按钮"""
    cv2.circle(frame, (x, y), radius, color, -1)
    cv2.circle(frame, (x, y), radius, COLORS['white'], 3)
    # 简化的 emoji 显示（用文字代替）
    (text_w, text_h), _ = cv2.getTextSize(emoji_text, font, 1.5, 3)
    cv2.putText(frame, emoji_text, (x - text_w//2, y + text_h//2), font, 1.5, COLORS['white'], 3)

print(f"🎬 生成视频中... {FPS}fps x {DURATION_SEC}秒 = {TOTAL_FRAMES} 帧")

for frame_num in range(TOTAL_FRAMES):
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    progress = frame_num / TOTAL_FRAMES
    
    # ========== 镜头 1: 开场 (0-3秒) ==========
    if progress < 0.167:
        t = progress / 0.167  # 0-1
        frame[:, :] = [int(c * t) for c in COLORS['bg']]
        
        # 标题
        if t > 0.3:
            alpha = min(1, (t - 0.3) / 0.3)
            draw_text_centered(frame, "🤖 5 个 AI 工具", HEIGHT//2 - 80, 2.0, COLORS['white'], 5)
            draw_text_centered(frame, "效率翻 10 倍", HEIGHT//2 + 50, 1.5, COLORS['yellow'], 3)
            
            # 底部提示
            if t > 0.7:
                draw_text_centered(frame, "打工人必备", HEIGHT - 200, 1.2, COLORS['gray'], 2)
    
    # ========== 镜头 2: ChatGPT (3-7秒) ==========
    elif progress < 0.389:
        t = (progress - 0.167) / 0.222  # 0-1
        
        # 背景渐变
        gradient = int(t * 50)
        frame[:, :] = (COLORS['bg'][0] + gradient, COLORS['bg'][1], COLORS['bg'][2] + gradient)
        
        # 工具 1
        center_x, center_y = WIDTH // 2, HEIGHT // 2 - 100
        radius = 80
        cv2.circle(frame, (center_x, center_y), radius, COLORS['green'], -1)
        cv2.circle(frame, (center_x, center_y), radius, COLORS['white'], 4)
        
        # Emoji
        (text_w, text_h), _ = cv2.getTextSize("1", font, 2.5, 5)
        cv2.putText(frame, "1", (center_x - text_w//2, center_y + text_h//2), font, 2.5, COLORS['white'], 5)
        
        # 名称
        draw_text_centered(frame, "ChatGPT 🤖", center_y + 150, 1.8, COLORS['green'], 4)
        draw_text_centered(frame, "写文案、做方案、查资料", center_y + 220, 1.0, COLORS['gray'], 2)
        
        # 底部进度条
        bar_y = HEIGHT - 100
        bar_width = int(WIDTH * (t * 0.8 + 0.1))
        cv2.rectangle(frame, (100, bar_y), (100 + bar_width, bar_y + 10), COLORS['green'], -1)
    
    # ========== 镜头 3: Midjourney (7-11秒) ==========
    elif progress < 0.611:
        t = (progress - 0.389) / 0.222
        
        frame[:, :] = (COLORS['bg'][0] + 30, COLORS['bg'][1], COLORS['bg'][2] + 60)
        
        # 工具 2
        center_x, center_y = WIDTH // 2, HEIGHT // 2 - 100
        
        # 渐变圆
        for r in range(radius, 0, -5):
            alpha = r / radius
            color = tuple(int(c * alpha) for c in COLORS['purple'])
            cv2.circle(frame, (center_x, center_y), r, color, -1)
        
        cv2.circle(frame, (center_x, center_y), radius, COLORS['white'], 4)
        (text_w, text_h), _ = cv2.getTextSize("2", font, 2.5, 5)
        cv2.putText(frame, "2", (center_x - text_w//2, center_y + text_h//2), font, 2.5, COLORS['white'], 5)
        
        draw_text_centered(frame, "Midjourney 🎨", center_y + 150, 1.8, COLORS['purple'], 4)
        draw_text_centered(frame, "AI 生成爆款图片", center_y + 220, 1.0, COLORS['gray'], 2)
        
        # 动态光效
        import math
        wave = int(30 * math.sin(t * 10))
        cv2.circle(frame, (center_x, center_y), radius + wave, COLORS['purple'], 2)
    
    # ========== 镜头 4: 工具 3-5 (11-15秒) ==========
    elif progress < 0.833:
        t = (progress - 0.611) / 0.222
        
        frame[:, :] = COLORS['bg']
        
        # 三个工具并排
        spacing = WIDTH // 4
        for i, tool in enumerate(TOOLS[2:]):  # Notion, ElevenLabs, Perplexity
            x = spacing * (i + 1)
            y = HEIGHT // 2
            
            # 圆形
            cv2.circle(frame, (x, y), 60, tool['color'], -1)
            cv2.circle(frame, (x, y), 60, COLORS['white'], 3)
            
            # 数字
            (text_w, text_h), _ = cv2.getTextSize(str(i+3), font, 1.8, 3)
            cv2.putText(frame, str(i+3), (x - text_w//2, y + text_h//2), font, 1.8, COLORS['white'], 3)
            
            # 名称
            draw_text_centered(frame, f"{tool['name']}", y + 120, 1.2, tool['color'], 3)
            draw_text_centered(frame, tool['desc'], y + 160, 0.8, COLORS['gray'], 1)
    
    # ========== 镜头 5: 结尾 (15-18秒) ==========
    else:
        t = (progress - 0.833) / 0.167
        
        # 渐变背景
        for i in range(HEIGHT):
            ratio = i / HEIGHT
            color = (
                int(COLORS['green'][0] * ratio + COLORS['bg'][0] * (1-ratio)),
                int(COLORS['green'][1] * ratio + COLORS['bg'][1] * (1-ratio)),
                int(COLORS['green'][2] * ratio + COLORS['bg'][2] * (1-ratio))
            )
            cv2.line(frame, (0, i), (WIDTH, i), color)
        
        # 勾号
        check_x, check_y = WIDTH // 2, HEIGHT // 2 - 100
        cv2.circle(frame, (check_x, check_y), 80, COLORS['white'], -1)
        # 对勾
        pts = np.array([(check_x - 30, check_y), (check_x - 5, check_y + 25), (check_x + 40, check_y - 20)], np.int32)
        cv2.polylines(frame, [pts], False, COLORS['green'], 8)
        
        # 文字
        draw_text_centered(frame, "学会这 5 个工具", HEIGHT//2 + 50, 1.5, COLORS['white'], 3)
        draw_text_centered(frame, "准时下班不是梦 ⏰", HEIGHT//2 + 120, 1.5, COLORS['yellow'], 3)
        
        # 关注提示
        if t > 0.5:
            draw_text_centered(frame, "点个赞再走 👍", HEIGHT - 150, 1.2, COLORS['gray'], 2)
    
    out.write(frame)
    
    if (frame_num + 1) % 90 == 0:
        print(f"  进度: {frame_num + 1}/{TOTAL_FRAMES}")

out.release()

file_size = os.path.getsize(output_path)
print(f"\n✅ 视频生成完成！")
print(f"📁 文件: {output_path}")
print(f"📊 大小: {file_size / 1024 / 1024:.2f} MB")
print(f"🕐 时长: {DURATION_SEC} 秒")
