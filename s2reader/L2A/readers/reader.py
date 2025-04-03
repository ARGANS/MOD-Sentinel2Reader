from abc import ABC, abstractmethod
import re
from typing import List, Any

class BaseReader(ABC):
    """Abstract base class for file readers.

    This class provides a template for implementing file readers that are compatible
    with specific tags or patterns. Subclasses must define `_PATTERNS` and implement
    the `read` method.
    """

    _PATTERNS: List[str] = []  # List of regex patterns for file matching

    def __init__(self, product: object) -> None:
        """
        Initialize the BaseReader with a reference to the L2AProduct instance.

        Args:
            product (object): An instance of the L2AProduct class.
        """
        self.product = product  # Reference to the L2AProduct instance

    def compatible(self, tag: str) -> bool:
        """
        Check if a given tag matches any of the patterns defined in `_PATTERNS`.

        Args:
            tag (str): The tag to check for compatibility.

        Returns:
            bool: True if the tag matches a pattern, otherwise False.
        """
        for pattern in self._PATTERNS:
            if tag == pattern or re.fullmatch(pattern, tag):
                return True
        return False

    @abstractmethod
    def read(self, tag: str) -> Any:
        """
        Read data associated with the given tag.

        This method must be implemented by subclasses to define how data is read.

        Args:
            tag (str): The tag to read data for.

        Returns:
            Any: The data read by the subclass implementation.
        """
        raise NotImplementedError("Subclasses must implement the read() method.")