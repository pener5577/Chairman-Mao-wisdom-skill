#!/usr/bin/env python3
"""
OBS远程控制脚本
功能：控制OBS录制、直播、场景切换等
"""

import obsws_python as obs
import sys
import time

class OBSController:
    def __init__(self, host="localhost", port=4444, password=""):
        """初始化OBS连接"""
        try:
            self.cl = obs.ReqClient(host=host, port=port, password=password)
            print(f"✅ 已连接到OBS (WebSocket {host}:{port})")
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            self.cl = None
    
    def get_status(self):
        """获取OBS状态"""
        if not self.cl:
            return None
        try:
            # 获取录制状态
            resp = self.cl.get_record_status()
            print(f"📊 录制状态: {'录制中' if resp.output_active else '未录制'}")
            print(f"📁 录制文件: {resp.output_path}")
            
            # 获取流状态
            stream = self.cl.get_stream_status()
            print(f"📡 直播状态: {'直播中' if stream.output_active else '未直播'}")
            
            # 获取场景列表
            scenes = self.cl.get_scene_list()
            print(f"🎬 可用场景: {[s.scene_name for s in scenes.scenes]}")
            
            # 当前场景
            current = self.cl.get_current_program_scene()
            print(f"🎯 当前场景: {current.current_program_scene_name}")
            
            return True
        except Exception as e:
            print(f"❌ 获取状态失败: {e}")
            return False
    
    def start_recording(self):
        """开始录制"""
        if not self.cl:
            return False
        try:
            self.cl.start_record()
            print("✅ 录制已开始")
            return True
        except Exception as e:
            print(f"❌ 录制失败: {e}")
            return False
    
    def stop_recording(self):
        """停止录制"""
        if not self.cl:
            return False
        try:
            self.cl.stop_record()
            print("✅ 录制已停止")
            return True
        except Exception as e:
            print(f"❌ 停止录制失败: {e}")
            return False
    
    def toggle_recording(self):
        """切换录制状态"""
        if not self.cl:
            return False
        try:
            resp = self.cl.get_record_status()
            if resp.output_active:
                return self.stop_recording()
            else:
                return self.start_recording()
        except Exception as e:
            print(f"❌ 切换录制失败: {e}")
            return False
    
    def switch_scene(self, scene_name):
        """切换场景"""
        if not self.cl:
            return False
        try:
            self.cl.set_current_program_scene(scene_name)
            print(f"✅ 已切换到场景: {scene_name}")
            return True
        except Exception as e:
            print(f"❌ 切换场景失败: {e}")
            return False
    
    def start_streaming(self):
        """开始直播"""
        if not self.cl:
            return False
        try:
            self.cl.start_stream()
            print("✅ 直播已开始")
            return True
        except Exception as e:
            print(f"❌ 直播失败: {e}")
            return False
    
    def stop_streaming(self):
        """停止直播"""
        if not self.cl:
            return False
        try:
            self.cl.stop_stream()
            print("✅ 直播已停止")
            return True
        except Exception as e:
            print(f"❌ 停止直播失败: {e}")
            return False


def main():
    print("=" * 50)
    print("🎬 OBS 远程控制器")
    print("=" * 50)
    
    # 创建控制器（默认无密码）
    controller = OBSController()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            controller.get_status()
        
        elif command == "start":
            controller.start_recording()
        
        elif command == "stop":
            controller.stop_recording()
        
        elif command == "toggle":
            controller.toggle_recording()
        
        elif command == "scene" and len(sys.argv) > 2:
            controller.switch_scene(sys.argv[2])
        
        elif command == "stream-start":
            controller.start_streaming()
        
        elif command == "stream-stop":
            controller.stop_streaming()
        
        else:
            print("用法:")
            print("  python3 obs_control.py status        - 查看状态")
            print("  python3 obs_control.py start         - 开始录制")
            print("  python3 obs_control.py stop          - 停止录制")
            print("  python3 obs_control.py toggle        - 切换录制")
            print("  python3 obs_control.py scene <名称> - 切换场景")
            print("  python3 obs_control.py stream-start - 开始直播")
            print("  python3 obs_control.py stream-stop  - 停止直播")
    else:
        controller.get_status()


if __name__ == "__main__":
    main()
