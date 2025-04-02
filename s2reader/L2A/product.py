from s2reader.L2A.metadata import Metadata
from s2reader.L2A.readers  import ReflectanceReader, ClassificationReader, AtmosphericReader

from pathlib import Path
import re
import xarray as xr
import pandas as pd

class L2AProduct:
    """ Sentinel-2 Level 2A Product Reader
    
    Interface for reading Sentinel-2 Level 2A products (.SAFE format)
    """
    
    _READERS = [ReflectanceReader,
                ClassificationReader,
                AtmosphericReader]
    
    def __init__(self, safe_path: str = None, target_resolution: int = None) -> None:
        """
        Initializes an L2AProduct instance.

        Args:
            safe_path (str): Path to the .SAFE directory containing Sentinel-2 data.
            target_resolution (int, optional): Desired resolution (default is 10 meters).
        """
        # Parse args
        self.safe_path = Path(safe_path).resolve()
        self.target_resolution = 10 if target_resolution is None else target_resolution

        # Ensure is .SAFE
        if self.safe_path.suffixes != ['.SAFE']:
            raise Exception(f'{self.safe_path} is not a .SAFE directory')

        # Load metadata
        self.meta = Metadata(self.safe_path)

        # Initialize empty DataArray and GeoDataFrame
        self.da    = None
        self._mask = None
        self.gdf   = None

        # Ensure multiple readers do not have similar tags
        self._check_duplicate_tags()

    def read(self, *tags):
        """ Reads specified data tags using the appropriate readers.

        Args:
            *tags (str): List of data tags to read.
        """

        for tag in tags:
            
            for reader in self._READERS:
                
                if tag not in reader._PATTERNS:
                    continue
                    
                if self._exists(tag):
                    continue
                    
                data = reader(self).read(tag)

                if isinstance(data, xr.DataArray):
                    self.update(da=data)
                    
                elif isinstance(data, pd.DataFrame):
                    self.update(vec=data)
                    
                else:
                    raise Exception(f'Reader {reader.__module__} returned data type {type(data)}, expceted xarray.DataArray or pandas.DataFrame')

        self._apply_mask()

    def add_mask(self, tag, values, invert=False):
        
        # Make sure the band has been read
        existed = self._exists(tag)
        self.read(tag)

        # Select the relevant DataArray
        arr = self.da.sel(band=tag).drop('band')

        # Ensure _mask exists and is initialized to False
        if not hasattr(self, "_mask") or self._mask is None:
            self._mask = xr.zeros_like(arr, dtype=bool)

        # Create a boolean mask for the given values
        mask = xr.zeros_like(arr, dtype=bool)
        for value in values:
            mask = mask | (arr == value)

        # Apply inversion if needed
        if invert:
            mask = ~mask

        # Update the master mask
        self._mask |= mask

        # Fill value not applicable, remove it 
        del self._mask.attrs['_FillValue']
        
        # If previously explicitly read, keep. Otherwise, remove from the DataArray
        if not existed:
            self.remove(tag)


    def remove(self, *tags):
        """
        Remove specified bands from the DataArray.

        Args:
            *tags (str): List of band names to remove.
        """
        if self.da is None or 'band' not in self.da.dims:
            raise ValueError("No bands available to remove.")

        # Filter out the bands that need to be removed
        remaining_bands = self.da.band.isin(tags)
        if remaining_bands.sum() == len(self.da.band):
            # If all bands are removed, set self.da to None
            self.da = None
        else:
            # Keep only the bands that are not in the tags
            self.da = self.da.sel(band=~remaining_bands)


    def is_compatible(self, tag: str, patterns: list) -> bool:
        """ Checks if a given tag matches any string or regex pattern in the provided list.

        Args:
            tag (str): The tag to check.
            patterns (list): List of valid tag patterns (string or regex).

        Returns:
            bool: True if the tag matches a pattern, otherwise False.
        """
        for pattern in patterns:
            if tag == pattern or re.fullmatch(pattern, tag):
                return True
        return False
    
    def _exists(self, tag: str) -> bool:
        """ Checks if a given tag exists in the DataArray.

        Args:
            tag (str): The tag to check.

        Returns:
            bool: True if the tag exists, otherwise False.
        """
        
        if self.da is None:
            return False
        
        if tag in self.da.band.values:
            return True
        else:
            return False
    
    def update(self, vec=None, da=None):
        """ Adds bands to the DataArray or vector data to the GeoDataFrame.

        Args:
            vec (_type_, optional): Vector data (e.g., footprints, masks). Defaults to None.
            da (xarray.DataArray, optional): DataArray containing raster data. Defaults to None.

        Raises:
            Exception: If no data is provided.
        """
        if (vec is None) and (da is None):
            raise Exception('No data to add')
        
        if (vec is not None) and (da is not None):
            raise Exception('Can only add one type of data at a time')
        
        # Add the band data to the DataArray
        if self.da is None:
            self.da = da
        else:
            # If data already exists and we want to add a new band
            self.da = xr.concat([self.da, da], dim='band')
            
        # Add the band data to the DataArray
        if self.gdf is None:
            self.gdf = vec
        else:
            # If data already exists and we want to add a new band
            self.gdf = pd.concat([self.gdf, vec])
            
    def _apply_mask(self):
        
        if hasattr(self, "_mask") and self._mask is not None:
            self.da = self.da.where(~self._mask)
         
    def _check_duplicate_tags(self):
        """Checks for duplicate tags across different readers and raises an error if found.
        """
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