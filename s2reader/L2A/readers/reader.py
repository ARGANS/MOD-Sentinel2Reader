from abc import ABC, abstractmethod
import re

   
class BaseReader(ABC):
    
    """Abstract base class for file readers."""
    
    _PATTERNS = []  # Regex pattern for file matching

    def __init__(self, product):
        """ Initialize with the L2AProduct class."""
        self.product = product  # Reference to Sentinel2L2AProduct
    
    def compatible(self, tag):
        """ Check if a given tag is a compatible pattern for reading."""
        for pattern in self._PATTERNS:
            if tag == pattern or re.fullmatch(pattern, tag):
                return True
    
    def read(self, tag):
        """ Override in subclasses to read data."""
        raise NotImplementedError("Subclasses must implement read() method.")