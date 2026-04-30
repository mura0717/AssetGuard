"""
Base State Manager Interface
Defines the contract for all integration state managers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class StateResult:
    """Result of a state check."""
    action: str              # 'create', 'update', 'skip'
    asset_id: str           # Unique identifier for this integration
    existing: Optional[Dict] # Existing record (for merging/reference)
    reason: Optional[str]    # Why this action was chosen (debugging)


class BaseStateManager(ABC):
    """
    Abstract base for integration state managers.
    
    Responsibilities:
    - Determine if asset exists in target system
    - Decide appropriate action (create/update/skip)
    - Provide existing data for merging
    """
    
    @abstractmethod
    def generate_id(self, asset_data: Dict) -> Optional[str]:
        """
        Generate unique identifier from asset data.
        Returns None if no suitable identifier found.
        """
        pass
    
    @abstractmethod
    def check(self, asset_data: Dict) -> StateResult:
        """
        Check asset state and determine action.
        Returns StateResult with action, existing data, etc.
        """
        pass
    
    @abstractmethod
    def record(self, asset_id: str, asset_data: Dict, action: str) -> None:
        """
        Record that an action was taken (for tracking/caching).
        """
        pass