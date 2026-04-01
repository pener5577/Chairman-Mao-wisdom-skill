"""OBS Studio CLI - Making OBS Agent-Native"""

__version__ = "1.0.0"

from .core.session import Session
from .core import scenes, sources, recording, streaming, project

__all__ = [
    'Session',
    'scenes',
    'sources',
    'recording',
    'streaming',
    'project'
]
