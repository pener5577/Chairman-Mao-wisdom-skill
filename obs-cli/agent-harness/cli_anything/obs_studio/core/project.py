"""Core module for project/scene management"""

from .session import Session

def list_projects(session: Session):
    """List all scene collections"""
    return session.get_projects()

def create_project(session: Session, name: str):
    """Create a new scene collection"""
    return session.create_project(name)
