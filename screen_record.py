#!/usr/bin/env python3
"""
屏幕录制控制器
功能：使用ffmpeg录制服务器屏幕
"""

import subprocess
import sys
import os
import signal
import time
from datetime import datetime

class ScreenRecorder:
    def __init__(self, output_dir="/root/Videos"):
        self.output_dir = output_dir
        self.recording = False
        self.process = None
        os.makedirs(output_dir, exist_ok=True)
    
    def get_display(self):
        """获取当前显示编号"""
        return os.environ.get("DISPLAY", ":99")
    
    def start_recording(self, width=1280, height=800, fps=30):
        """开始录制"""
        if self.recording:
            print("⚠️ 已经在录制中")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_dir, f"recording_{timestamp}.mp4")
        
        # ffmpeg命令录制屏幕
        display = self.get_display()
        cmd = [
            'ffmpeg',
            '-f', 'x11grab',
            '-framerate', str(fps),
            '-video_size', f'{width}x{height}',
            '-i', display,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-y',  # 覆盖输出文件
            output_file
        ]
        
        print(f"🎬 开始录制: {output_file}")
        print(f"📐 分辨率: {width}x{height}")
        print(f"🎯 FPS: {fps}")
        
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.recording = True
            self.output_file = output_file
            print("✅ 录制已开始 (Ctrl+C 停止)")
            return True
        except Exception as e:
            print(f"❌ 录制失败: {e}")
            return False
    
    def stop_recording(self):
        """停止录制"""
        if not self.recording or not self.process:
            print("⚠️ 没有正在录制的进程")
            return None
        
        print("🛑 正在停止录制...")
        self.process.send_signal(signal.SIGINT)
        
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
        
        self.recording = False
        output = self.output_file
        print(f"✅ 录制已保存: {output}")
        return output
    
    def status(self):
        """查看状态"""
        if self.recording:
            elapsed = time.time() - getattr(self, 'start_time', time.time())
            print(f"📹 录制中...")
            print(f"⏱️ 已录制: {int(elapsed)}秒")
            print(f"📁 文件: {getattr(self, 'output_file', 'unknown')}")
        else:
            print("📹 未录制")
        
        # 显示已录制的文件
        files = sorted([f for f in os.listdir(self.output_dir) if f.endswith('.mp4')])
        if files:
            print(f"\n📂 已录制的文件 ({len(files)}个):")
            for f in files[-5:]:  # 显示最近5个
                path = os.path.join(self.output_dir, f)
                size = os.path.getsize(path) / 1024 / 1024  # MB
                print(f"  - {f} ({size:.1f} MB)")


def main():
    print("=" * 50)
    print("🎬 屏幕录制控制器")
    print("=" * 50)
    
    recorder = ScreenRecorder()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            recorder.start_recording()
            recorder.start_time = time.time()
            try:
                while recorder.recording and recorder.process.poll() is None:
                    time.sleep(1)
            except KeyboardInterrupt:
                recorder.stop_recording()
        
        elif command == "stop":
            recorder.stop_recording()
        
        elif command == "status":
            recorder.status()
        
        elif command == "list":
            recorder.output_dir = "/root/Videos"
            recorder.status()
        
        else:
            print_help()
    else:
        print_help()


def print_help():
    print("""
用法:
  python3 screen_record.py start    - 开始录制
  python3 screen_record.py stop       - 停止录制
  python3 screen_record.py status    - 查看状态
  python3 screen_record.py list      - 列出已录制文件

快捷键:
  Ctrl+C  - 停止录制并保存
""")


if __name__ == "__main__":
    main()
