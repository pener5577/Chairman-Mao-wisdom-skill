from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os

# 创建目录
output_dir = "/root/.openclaw/workspace/douyin-images"
os.makedirs(output_dir, exist_ok=True)

# 竖屏 9:16 比例 - 1080x1920
WIDTH, HEIGHT = 1080, 1920

# 自定义字体（使用系统字体）
try:
    # 尝试加载中文字体
    font_large = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 120)
    font_medium = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 80)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 60)
except:
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

def create_warning_image(text_lines, bg_color, text_color, accent_color, accent_symbol):
    """创建警示图"""
    img = Image.new('RGB', (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 绘制背景渐变效果
    for i in range(HEIGHT):
        alpha = int(255 * (i / HEIGHT))
        color = (
            int(accent_color[0] * alpha / 255 + bg_color[0] * (1 - alpha / 255)),
            int(accent_color[1] * alpha / 255 + bg_color[1] * (1 - alpha / 255)),
            int(accent_color[2] * alpha / 255 + bg_color[2] * (1 - alpha / 255))
        )
        draw.line([(0, i), (WIDTH, i)], fill=color)
    
    # 绘制大标题
    title = "⚠️ 手机正在裸奔"
    bbox = draw.textbbox((0, 0), title, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (WIDTH - text_width) // 2
    y = (HEIGHT - text_height) // 2 - 200
    draw.text((x, y), title, font=font_large, fill=text_color)
    
    # 绘制副标题
    subtitle = "3 个开关必须关"
    bbox = draw.textbbox((0, 0), subtitle, font=font_medium)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (WIDTH - text_width) // 2
    y = (HEIGHT - text_height) // 2 + 50
    draw.text((x, y), subtitle, font=font_medium, fill=text_color)
    
    # 绘制警告符号
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    # 三角形
    triangle_points = [
        (center_x, center_y - 100),
        (center_x - 80, center_y + 100),
        (center_x + 80, center_y + 100)
    ]
    draw.polygon(triangle_points, fill=accent_color)
    # 感叹号
    draw.rectangle([center_x - 30, center_y, center_x + 30, center_y + 120], fill=(255, 255, 255))
    draw.rectangle([center_x - 10, center_y + 130, center_x + 10, center_y + 150], fill=(255, 255, 255))
    
    # 添加底部提示
    footer = "看完赶紧去设置里关掉"
    bbox = draw.textbbox((0, 0), footer, font=font_small)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    y = HEIGHT - 150
    draw.text((x, y), footer, font=font_small, fill=text_color)
    
    return img

def create_phone_ui_image(screen_title, highlight_text, description, bg_color, highlight_color, accent_color):
    """创建手机设置界面图"""
    img = Image.new('RGB', (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 模拟手机边框
    draw.rectangle([50, 50, WIDTH - 50, HEIGHT - 50], outline=(50, 50, 50), width=5)
    draw.rectangle([55, 55, WIDTH - 55, HEIGHT - 55], fill=(30, 30, 40))
    
    # 状态栏
    draw.rectangle([55, 55, WIDTH - 55, 105], fill=(20, 20, 30))
    time_text = "06:29"
    bbox = draw.textbbox((0, 0), time_text, font=font_medium)
    text_width = bbox[2] - bbox[0]
    x = WIDTH - 55 - text_width - 20
    y = 65
    draw.text((x, y), time_text, font=font_medium, fill=(255, 255, 255))
    
    # 标题
    bbox = draw.textbbox((0, 0), screen_title, font=font_medium)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (WIDTH - text_width) // 2
    y = 150
    draw.text((x, y), screen_title, font=font_medium, fill=(255, 255, 255))
    
    # 内容项 - 高亮显示
    for i, item in enumerate(highlight_text):
        y = 250 + i * 180
        # 背景框
        draw.rectangle([150, y - 60, WIDTH - 150, y + 100], fill=highlight_color)
        # 边框
        draw.rectangle([150, y - 60, WIDTH - 150, y + 100], outline=accent_color, width=4)
        # 文字
        bbox = draw.textbbox((0, 0), item, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (WIDTH - text_width) // 2
        draw.text((x, y - 80), item, font=font_large, fill=(255, 255, 255))
    
    # 说明文字
    bbox = draw.textbbox((0, 0), description, font=font_medium)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    y = HEIGHT - 200
    draw.text((x, y), description, font=font_medium, fill=(200, 200, 200))
    
    return img

def create_security_complete_image(title, description, bg_color, accent_color):
    """创建安全完成图"""
    img = Image.new('RGB', (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 渐变背景
    for i in range(HEIGHT):
        alpha = int(255 * (i / HEIGHT))
        color = (
            int(accent_color[0] * alpha / 255 + bg_color[0] * (1 - alpha / 255)),
            int(accent_color[1] * alpha / 255 + bg_color[1] * (1 - alpha / 255)),
            int(accent_color[2] * alpha / 255 + bg_color[2] * (1 - alpha / 255))
        )
        draw.line([(0, i), (WIDTH, i)], fill=color)
    
    # 盾牌图标
    shield_points = [
        (WIDTH // 2, 400),
        (WIDTH // 2 - 150, 600),
        (WIDTH // 2 - 150, 900),
        (WIDTH // 2 - 100, 1000),
        (WIDTH // 2 + 100, 1000),
        (WIDTH // 2 + 150, 900),
        (WIDTH // 2 + 150, 600)
    ]
    draw.polygon(shield_points, fill=accent_color)
    draw.polygon(shield_points, outline=(255, 255, 255), width=8)
    
    # 勾号
    check_points = [
        (WIDTH // 2 - 40, 750),
        (WIDTH // 2 - 80, 800),
        (WIDTH // 2 + 60, 950)
    ]
    draw.polygon(check_points, fill=(255, 255, 255))
    
    # 标题
    bbox = draw.textbbox((0, 0), title, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (WIDTH - text_width) // 2
    y = 950
    draw.text((x, y), title, font=font_large, fill=(255, 255, 255))
    
    # 说明
    bbox = draw.textbbox((0, 0), description, font=font_medium)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    y = HEIGHT - 180
    draw.text((x, y), description, font=font_medium, fill=(255, 255, 255))
    
    return img

# 生成图片
print("正在生成图片...")

# 图 1：封面警示图
img1 = create_warning_image(
    ["⚠️ 手机正在裸奔", "3 个开关必须关"],
    bg_color=(20, 20, 20),
    text_color=(255, 255, 255),
    accent_color=(255, 200, 0),
    accent_symbol="⚠️"
)
img1.save(f"{output_dir}/douyin_01_cover_warning.png")
print(f"✓ 已生成：douyin_01_cover_warning.png")

# 图 2：位置权限界面
img2 = create_phone_ui_image(
    screen_title="位置服务",
    highlight_text=["总是允许", "仅本次"],
    description="应用后台定位，比你想象的更疯狂",
    bg_color=(30, 30, 40),
    highlight_color=(50, 50, 80),
    accent_color=(0, 200, 255)
)
img2.save(f"{output_dir}/douyin_02_location.png")
print(f"✓ 已生成：douyin_02_location.png")

# 图 3：蓝牙警告界面
img3 = create_phone_ui_image(
    screen_title="蓝牙设置",
    highlight_text=["自动连接", "手动连接"],
    description="公共场所设备可能正在入侵",
    bg_color=(30, 30, 40),
    highlight_color=(80, 30, 30),
    accent_color=(255, 80, 80)
)
img3.save(f"{output_dir}/douyin_03_bluetooth.png")
print(f"✓ 已生成：douyin_03_bluetooth.png")

# 图 4：照片元数据界面
img4 = create_phone_ui_image(
    screen_title="照片元数据",
    highlight_text=["包含地址信息", "包含时间信息"],
    description="每张照片都在泄露隐私",
    bg_color=(30, 30, 40),
    highlight_color=(60, 40, 80),
    accent_color=(200, 100, 255)
)
img4.save(f"{output_dir}/douyin_04_photo_metadata.png")
print(f"✓ 已生成：douyin_04_photo_metadata.png")

# 图 5：安全完成图
img5 = create_security_complete_image(
    title="已保护你的隐私",
    description="赶紧去设置里关掉这 3 个开关",
    bg_color=(20, 40, 20),
    accent_color=(50, 200, 100)
)
img5.save(f"{output_dir}/douyin_05_security_complete.png")
print(f"✓ 已生成：douyin_05_security_complete.png")

print("\n✅ 所有图片生成完成！")
print(f"图片保存在：{output_dir}/")
print("文件名：")
for i in range(1, 6):
    print(f"  - douyin_{i:02d}_*.png")
