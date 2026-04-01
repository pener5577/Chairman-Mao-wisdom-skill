"""Core module for streaming control"""

from .session import Session

def start_streaming(session: Session):
    """Start streaming"""
    return session.start_streaming()

def stop_streaming(session: Session):
    """Stop streaming"""
    return session.stop_streaming()

def get_streaming_status(session: Session):
    """Get streaming status"""
    return session.get_streaming_status()
