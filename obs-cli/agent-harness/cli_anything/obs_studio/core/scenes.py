"""Core module for scene management"""

from .session import Session

def list_scenes(session: Session):
    """List all scenes"""
    return session.get_scenes()

def switch_scene(session: Session, name: str):
    """Switch to a scene"""
    return session.switch_scene(name)

def add_scene(session: Session, name: str):
    """Add a new scene"""
    # This would call OBS WebSocket
    return True
