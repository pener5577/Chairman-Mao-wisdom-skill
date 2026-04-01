"""OBS Backend utilities - wraps OBS WebSocket protocol"""

import websocket
import json
from typing import Optional


def find_obs() -> Optional[str]:
    """Find OBS executable"""
    import shutil
    paths = ['obs', 'obs-cli', '/usr/bin/obs', '/Applications/OBS.app']
    for path in paths:
        if shutil.which(path):
            return path
    return None


class OBSBackend:
    """Backend for OBS WebSocket communication"""
    
    def __init__(self, host: str = "localhost", port: int = 4455, password: str = ""):
        self.host = host
        self.port = port
        self.password = password
        self.ws = None
    
    def connect(self) -> bool:
        """Connect to OBS"""
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(f"ws://{self.host}:{self.port}", password=self.password)
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from OBS"""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
    
    def send(self, request_type: str, data: dict = None) -> dict:
        """Send a request to OBS"""
        if not self.ws:
            raise RuntimeError("Not connected to OBS")
        
        request = {"requestType": request_type}
        if data:
            request["requestData"] = data
        
        self.ws.send(json.dumps(request))
        response = json.loads(self.ws.recv())
        return response
    
    def get_scene_list(self) -> dict:
        """Get list of scenes"""
        return self.send("GetSceneList")
    
    def set_current_scene(self, scene_name: str) -> bool:
        """Set current scene"""
        response = self.send("SetCurrentProgramScene", {"sceneName": scene_name})
        return response.get("requestStatus", {}).get("result", False)
    
    def start_recording(self) -> bool:
        """Start recording"""
        response = self.send("StartRecord")
        return response.get("requestStatus", {}).get("result", False)
    
    def stop_recording(self) -> bool:
        """Stop recording"""
        response = self.send("StopRecord")
        return response.get("requestStatus", {}).get("result", False)
    
    def start_streaming(self) -> bool:
        """Start streaming"""
        response = self.send("StartStream")
        return response.get("requestStatus", {}).get("result", False)
    
    def stop_streaming(self) -> bool:
        """Stop streaming"""
        response = self.send("StopStream")
        return response.get("requestStatus", {}).get("result", False)
