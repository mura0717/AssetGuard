"""
Base Dispatcher Interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Union, Any
from soc_stack.builders.base_builder import BuildResult

class BaseDispatcher(ABC):
    
    @abstractmethod
    def sync(self, build_results: List[BuildResult]) -> Dict[str, int]:
        """Sync built payloads to the destination system."""
        pass