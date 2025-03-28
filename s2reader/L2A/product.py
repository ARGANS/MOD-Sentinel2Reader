from s2reader.L2A.metadata import Metadata
from s2reader.L2A.readers  import ReflectanceReader, ClassificationReader, AtmosphericReader

from pathlib import Path
import re
import xarray as xr

class L2AProduct:
    
    """ Sentinel-2 Level 2A Product Reader 
    """
    
    _READERS = [ReflectanceReader,
                ClassificationReader,
                AtmosphericReader]
    
    def __init__(self, safe_path:str=None, target_resolution:int=None) -> None:

        # Parse args
        self.safe_path = Path(safe_path).resolve()
        self.target_resolution = 10 if target_resolution is None else target_resolution

        # Ensure is .SAFE
        if self.safe_path.suffixes != ['.SAFE']:
            raise Exception(f'{self.safe_path} is not a .SAFE directory')

        # Load in the metadata
        self.meta  = Metadata(self.safe_path)

        # Empty DataArray
        self.da = None
        
        # Empty GeoDataFrame (store footprint, etc.)
        self.vec = None
        
        self._check_duplicate_tags()


    def read(self, *tags):
        
        for tag in tags:
            
            for reader in self._READERS:
                
                if tag in reader._PATTERNS:
                    
                    reader(self).read(tag)

    def is_compatible(self, tag: str, patterns: list):
        """Check if the target string matches any string or regex pattern in the list."""
        for pattern in patterns:
            if tag == pattern or re.fullmatch(pattern, tag):
                return True
        return False
    
    
    def update(self, vec=None, da=None):
        
        if (vec is None) and (da is None):
            raise Exception('No data to add')
        
        # Add the band data to the DataArray
        if self.da is None:
            self.da = da
        else:
            # If data already exists and we want to add a new band
            self.da = xr.concat([self.da, da], dim='band')
            
            
    def _check_duplicate_tags(self):
        """Check for duplicate tags across readers and raise an error if found."""
        
        # Collect all tags from readers
        tag_to_readers = {}
        
        for reader in self._READERS:
            for tag in reader._PATTERNS:
                if tag in tag_to_readers:
                    tag_to_readers[tag].append(reader.__module__)
                else:
                    tag_to_readers[tag] = [reader.__module__]
        
        # Identify duplicates
        duplicates = {tag: readers for tag, readers in tag_to_readers.items() if len(readers) > 1}
        
        if duplicates:
            duplicate_messages = [f"Tag '{tag}' is used by {', '.join(readers)}" for tag, readers in duplicates.items()]
            raise ValueError("Duplicate tags found:\n" + "\n".join(duplicate_messages))