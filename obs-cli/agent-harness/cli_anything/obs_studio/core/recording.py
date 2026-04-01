"""Core module for recording control"""

from .session import Session

def start_recording(session: Session):
    """Start recording"""
    return session.start_recording()

def stop_recording(session: Session):
    """Stop recording"""
    return session.stop_recording()

def get_recording_status(session: Session):
    """Get recording status"""
    return session.get_recording_status()
