"""Core module for source management"""

from .session import Session

def list_sources(session: Session):
    """List sources in current scene"""
    return session.get_sources()

def add_source(session: Session, name: str, source_type: str):
    """Add a source to current scene"""
    return session.add_source(name, source_type)

def remove_source(session: Session, name: str):
    """Remove a source from current scene"""
    return True
