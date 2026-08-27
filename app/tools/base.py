from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseRouteTool(ABC):
    """
    Base interface for tools used by the route optimization agent.

    Concrete tools should implement:
        - name
        - description
        - execute()
    """

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the tool and return a structured result.
        """
        raise NotImplementedError