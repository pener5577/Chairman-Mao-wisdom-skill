"""
Tests for OBS CLI Core
"""

import pytest
from cli_anything.obs_studio.core.session import Session


def test_session_init():
    """Test session initialization"""
    session = Session()
    assert session is not None
    assert session.host == "localhost"
    assert session.port == 4455


def test_simulate_state():
    """Test state simulation when OBS not connected"""
    session = Session()
    assert session.connected == False
    assert len(session.scenes) > 0


def test_get_status():
    """Test getting status"""
    session = Session()
    status = session.get_status()
    assert "connected" in status
    assert "current_scene" in status


def test_switch_scene():
    """Test scene switching"""
    session = Session()
    session._simulate_state()
    
    result = session.switch_scene("Main")
    assert result == True
    assert session.current_scene == "Main"


def test_recording_status():
    """Test recording status"""
    session = Session()
    status = session.get_recording_status()
    assert "recording" in status


def test_streaming_status():
    """Test streaming status"""
    session = Session()
    status = session.get_streaming_status()
    assert "streaming" in status


def test_get_sources():
    """Test getting sources"""
    session = Session()
    session._simulate_state()
    sources = session.get_sources()
    assert "sources" in sources
    assert len(sources["sources"]) > 0
