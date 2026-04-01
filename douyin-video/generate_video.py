#!/usr/bin/env python3
"""
生成简单的测试视频 - 抖音竖屏 9:16
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
DURATION_SEC = 10
TOTAL_FRAMES = FPS * DURATION_SEC

# 输出文件
output_path = f"{output_dir}/test_video.mp4"

# 创建视频写入器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, FPS, (WIDTH, HEIGHT))

print(f"生成视频中... {FPS}fps x {DURATION_SEC}秒 = {TOTAL_FRAMES} 帧")

for frame_num in range(TOTAL_FRAMES):
    # 创建空白画布 - 深色背景
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    
    # 动态背景渐变
    progress = frame_num / TOTAL_FRAMES
    bg_color = (
        int(20 + 30 * progress),
        int(20 + 20 * progress),
        int(40 + 40 * progress)
    )
    frame[:, :] = bg_color
    
    # 中心文字
    text = "🎉 测试视频"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2.5
    thickness = 5
    
    # 计算文字大小并居中
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    x = (WIDTH - text_w) // 2
    y = (HEIGHT - text_h) // 2
    
    # 绘制文字
    cv2.putText(frame, text, (x, y), font, font_scale, (255, 255, 255), thickness)
    
    # 底部副标题
    subtext = "OpenClaw + 抖音发布测试"
    (sub_w, sub_h), _ = cv2.getTextSize(subtext, font, 1.2, 3)
    sub_x = (WIDTH - sub_w) // 2
    sub_y = HEIGHT - 200
    cv2.putText(frame, subtext, (sub_x, sub_y), font, 1.2, (200, 200, 200), 3)
    
    # 添加动态元素 - 移动的圆点
    circle_y = int(HEIGHT * 0.3 + 100 * np.sin(progress * 2 * np.pi))
    circle_x = WIDTH // 2
    cv2.circle(frame, (circle_x, circle_y), 30, (255, 200, 0), -1)
    
    # 帧计数器（左上角）
    fps_text = f"帧: {frame_num+1}/{TOTAL_FRAMES}"
    cv2.putText(frame, fps_text, (50, 80), font, 0.8, (150, 150, 150), 2)
    
    # 进度条（底部）
    bar_height = 20
    bar_width = int(WIDTH * progress)
    cv2.rectangle(frame, (0, HEIGHT - bar_height), (bar_width, HEIGHT), (100, 200, 255), -1)
    
    # 写入帧
    out.write(frame)
    
    # 每 30 帧打印一次进度
    if (frame_num + 1) % 30 == 0:
        print(f"  进度: {frame_num + 1}/{TOTAL_FRAMES}")

# 释放资源
out.release()

# 获取文件大小
file_size = os.path.getsize(output_path)
print(f"\n✅ 视频生成完成！")
print(f"📁 文件: {output_path}")
print(f"📊 大小: {file_size / 1024 / 1024:.2f} MB")
print(f"🕐 时长: {DURATION_SEC} 秒")
print(f"📐 分辨率: {WIDTH}x{HEIGHT}")
