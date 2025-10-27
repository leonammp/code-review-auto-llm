"""
Ports - Interfaces/abstrações para serviços externos
"""

from src.core.ports.diff_port import DiffPort, FileChange
from src.core.ports.llm_port import LLMPort
from src.core.ports.vcs_port import VCSPort

__all__ = [
    "VCSPort",
    "LLMPort",
    "DiffPort",
    "FileChange",
]
