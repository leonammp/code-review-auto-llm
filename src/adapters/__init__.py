"""
Adapters - Implementações concretas das Ports
"""

from src.adapters.azure_devops_adapter import AzureDevOpsAdapter
from src.adapters.diff_adapter import DiffAdapter
from src.adapters.litellm_adapter import LiteLLMAdapter

__all__ = [
    "AzureDevOpsAdapter",
    "LiteLLMAdapter",
    "DiffAdapter",
]
