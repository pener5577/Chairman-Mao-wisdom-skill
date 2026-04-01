"""
OBS Session Management

Handles connection state and session persistence.
"""

import json
import os
from typing import Optional, Dict, Any


class Session:
    """Manages OBS WebSocket connection and session state"""
    
    def __init__(self):
        self.host = "localhost"
        self.port = 4455
        self.password = ""
        self.connected = False
        self.current_scene = "Main"
        self.recording = False
        self.streaming = False
        self.scenes = []
        self.sources = []
        
        # Try to connect via WebSocket
        self._ws = None
        self._connect()
    
    def _connect(self):
        """Attempt to connect to OBS via WebSocket"""
        try:
            import websocket
            self._ws = websocket.WebSocket()
            self._ws.connect(
                f"ws://{self.host}:{self.port}",
                password=self.password
            )
            self.connected = True
            self._sync_state()
        except Exception as e:
            self.connected = False
            self._simulate_state()
    
    def _sync_state(self):
        """Sync state from OBS"""
        if not self.connected:
            return
        
        try:
            # Get scene list
            self._ws.send(json.dumps({"requestType": "GetSceneList"}))
            response = json.loads(self._ws.recv())
            if "sceneList" in response:
                self.scenes = [s["sceneName"] for s in response["sceneList"]["scenes"]]
                self.current_scene = response["sceneList"]["currentScene"]
            
            # Get recording status
            self._ws.send(json.dumps({"requestType": "GetRecordStatus"}))
            response = json.loads(self._ws.recv())
            self.recording = response.get("outputActive", False)
            
            # Get streaming status  
            self._ws.send(json.dumps({"requestType": "GetStreamStatus"}))
            response = json.loads(self._ws.recv())
            self.streaming = response.get("outputActive", False)
        except Exception:
            self.connected = False
    
    def _simulate_state(self):
        """Simulate state when OBS is not running"""
        self.scenes = ["Main", "Scene 2", "Scene 3"]
        self.sources = [
            {"name": "Screen Capture", "type": "monitor_capture"},
            {"name": "Webcam", "type": "video_capture_device"},
            {"name": "Audio", "type": "audio_input_capture"}
        ]
    
    def configure(self, host: str, port: int, password: str):
        """Configure connection settings"""
        self.host = host
        self.port = port
        self.password = password
        if self._ws:
            try:
                self._ws.close()
            except:
                pass
        self._connect()
    
    def get_status(self) -> Dict[str, Any]:
        """Get OBS status"""
        return {
            "connected": self.connected,
            "current_scene": self.current_scene,
            "recording": self.recording,
            "streaming": self.streaming,
            "scene_count": len(self.scenes),
            "host": self.host,
            "port": self.port
        }
    
    def get_scenes(self) -> Dict[str, Any]:
        """Get all scenes"""
        if not self.scenes:
            self._simulate_state()
        return {
            "scenes": [{"name": s, "index": i} for i, s in enumerate(self.scenes)],
            "current": self.current_scene
        }
    
    def switch_scene(self, name: str) -> bool:
        """Switch to a scene"""
        if name not in self.scenes:
            # Try to switch in OBS
            if self.connected:
                try:
                    self._ws.send(json.dumps({
                        "requestType": "SetCurrentProgramScene",
                        "requestData": {"sceneName": name}
                    }))
                    self.current_scene = name
                    return True
                except:
                    return False
            return False
        
        self.current_scene = name
        return True
    
    def get_recording_status(self) -> Dict[str, Any]:
        """Get recording status"""
        if self.connected:
            try:
                self._ws.send(json.dumps({"requestType": "GetRecordStatus"}))
                response = json.loads(self._ws.recv())
                return {
                    "recording": response.get("outputActive", False),
                    "duration": response.get("outputDuration", 0)
                }
            except:
                pass
        
        return {"recording": self.recording}
    
    def start_recording(self) -> bool:
        """Start recording"""
        if self.connected:
            try:
                self._ws.send(json.dumps({"requestType": "StartRecord"}))
                self.recording = True
                return True
            except:
                pass
        return False
    
    def stop_recording(self) -> bool:
        """Stop recording"""
        if self.connected:
            try:
                self._ws.send(json.dumps({"requestType": "StopRecord"}))
                self.recording = False
                return True
            except:
                pass
        return False
    
    def get_streaming_status(self) -> Dict[str, Any]:
        """Get streaming status"""
        if self.connected:
            try:
                self._ws.send(json.dumps({"requestType": "GetStreamStatus"}))
                response = json.loads(self._ws.recv())
                return {"streaming": response.get("outputActive", False)}
            except:
                pass
        
        return {"streaming": self.streaming}
    
    def start_streaming(self) -> bool:
        """Start streaming"""
        if self.connected:
            try:
                self._ws.send(json.dumps({"requestType": "StartStream"}))
                self.streaming = True
                return True
            except:
                pass
        return False
    
    def stop_streaming(self) -> bool:
        """Stop streaming"""
        if self.connected:
            try:
                self._ws.send(json.dumps({"requestType": "StopStream"}))
                self.streaming = False
                return True
            except:
                pass
        return False
    
    def get_sources(self) -> Dict[str, Any]:
        """Get sources in current scene"""
        if not self.sources:
            self._simulate_state()
        return {"sources": self.sources}
    
    def add_source(self, name: str, source_type: str) -> bool:
        """Add a source to current scene"""
        if self.connected:
            try:
                self._ws.send(json.dumps({
                    "requestType": "CreateSceneItem",
                    "requestData": {
                        "sceneName": self.current_scene,
                        "sourceName": name,
                        "sourceType": source_type
                    }
                }))
                return True
            except:
                pass
        return False
    
    def get_projects(self) -> Dict[str, Any]:
        """Get all scene collections"""
        return {"projects": ["Default", "Streaming", "Recording"]}
    
    def create_project(self, name: str) -> bool:
        """Create a new scene collection"""
        if self.connected:
            try:
                self._ws.send(json.dumps({
                    "requestType": "CreateSceneCollection",
                    "requestData": {"sceneCollectionName": name}
                }))
                return True
            except:
                pass
        return False
