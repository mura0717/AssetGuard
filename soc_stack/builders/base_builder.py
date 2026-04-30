"""
Base Payload Builder Interface
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

from soc_stack.states.base_state import StateResult


@dataclass
class BuildResult:
    """Result of payload building."""
    payload: Dict[str, Any]
    asset_id: str
    action: str
    snipe_id: Optional[int] = None  # For cross-reference
    metadata: Dict = field(default_factory=dict)


class BasePayloadBuilder(ABC):
    """Abstract base for integration payload builders."""
    
    @abstractmethod
    def build(self, asset_data: Dict, state_result: StateResult) -> BuildResult:
        """
        Build payload for target integration.
        
        Args:
            asset_data: Canonical asset data
            state_result: Result from state manager
            
        Returns:
            BuildResult with payload and metadata
        """
        pass