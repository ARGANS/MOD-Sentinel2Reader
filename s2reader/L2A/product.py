from s2reader.L2A.metadata import Metadata
from s2reader.L2A.readers import ReflectanceReader, ClassificationReader, AtmosphericReader

from typing import Optional, List, Dict, Union
from pathlib import Path
import re
import xarray as xr
import pandas as pd

class L2AProduct:
    """Sentinel-2 Level 2A Product Reader

    Interface for reading Sentinel-2 Level 2A products (.SAFE format).
    Provides methods to read, update, and manage raster and vector data.
    """

    _READERS: List[type] = [
        ReflectanceReader, 
        ClassificationReader, 
        AtmosphericReader
    ]

    def __init__(self, 
                 safe_path: str, 
                 target_resolution: Optional[int] = None, 
                 mask: Optional[Dict[str, List[float]]] = None) -> None:
        """
        Initializes an L2AProduct instance.

        Args:
            safe_path (Optional[str]): Path to the .SAFE directory containing Sentinel-2 data.
            target_resolution (Optional[int]): Desired resolution (default is 10 meters).
            mask (Dict[str, List[int]]): Dictionary of band names and their corresponding mask values.
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
        self.da: Optional[xr.DataArray] = None
        self.mask: Optional[xr.DataArray] = None
        self.gdf: Optional[pd.DataFrame] = None

        # Ensure multiple readers do not have similar tags
        self._unique_tags()

        # Generate mask
        if mask is not None:
            for band, values in mask.items():
                self._add_mask(band, values)

    def read(self, *tags: str) -> None:
        """
        Reads specified data tags using the appropriate readers.

        Args:
            *tags (str): List of data tags to read.

        Raises:
            Exception: If a reader returns an unsupported data type.
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
                    raise Exception(f'Reader {reader.__module__} returned data type {type(data)}, expected xarray.DataArray or pandas.DataFrame')

        self._apply_mask()

    def remove(self, *tags: str) -> None:
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

    def update(self, vec: Optional[pd.DataFrame] = None, da: Optional[xr.DataArray] = None) -> None:
        """
        Adds bands to the DataArray or vector data to the GeoDataFrame.

        Args:
            vec (Optional[pd.DataFrame]): Vector data (e.g., footprints, masks). Defaults to None.
            da (Optional[xr.DataArray]): DataArray containing raster data. Defaults to None.

        Raises:
            Exception: If no data is provided or both `vec` and `da` are provided.
        """
        if (vec is None) and (da is None):
            raise Exception('No data to add')

        if (vec is not None) and (da is not None):
            raise Exception('Can only add one type of data at a time')

        # Add the band data to the DataArray
        if da is not None:
            if self.da is None:
                self.da = da
            else:
                self.da = xr.concat([self.da, da], dim='band')

        # Add the vector data to the GeoDataFrame
        if vec is not None:
            if self.gdf is None:
                self.gdf = vec
            else:
                self.gdf = pd.concat([self.gdf, vec])

    def _add_mask(self, tag: str, values: List[float]) -> None:
        """
        Adds a mask for the specified tag and values.

        Args:
            tag (str): The band name to mask.
            values (List[float]): List of values to mask.
        """
        # Read and select the relevant DataArray
        self.read(tag)
        arr = self.da.sel(band=tag).drop('band')

        # Ensure _mask exists and is initialized to False
        if not hasattr(self, "_mask") or self._mask is None:
            self._mask = xr.zeros_like(arr, dtype=bool)

        # Create a boolean mask for the given values
        mask = xr.zeros_like(arr, dtype=bool)
        for value in values:
            mask = mask | (arr == value)

        # Update the master mask
        self._mask |= mask

    def _apply_mask(self) -> None:
        """
        Applies the mask to the DataArray, if it exists.
        """
        if hasattr(self, "_mask") and self._mask is not None:
            self.da = self.da.where(~self._mask)

    def _is_compatible(self, tag: str, patterns: List[Union[str, re.Pattern]]) -> bool:
        """
        Checks if a given tag matches any string or regex pattern in the provided list.

        Args:
            tag (str): The tag to check.
            patterns (List[Union[str, re.Pattern]]): List of valid tag patterns (string or regex).

        Returns:
            bool: True if the tag matches a pattern, otherwise False.
        """
        for pattern in patterns:
            if tag == pattern or re.fullmatch(pattern, tag):
                return True
        return False

    def _exists(self, tag: str) -> bool:
        """
        Checks if a given tag exists in the DataArray.

        Args:
            tag (str): The tag to check.

        Returns:
            bool: True if the tag exists, otherwise False.
        """
        return self.da is not None and tag in self.da.band.values

    def _unique_tags(self) -> None:
        """
        Checks for duplicate tags across different readers and raises an error if found.

        Raises:
            ValueError: If duplicate tags are found across readers.
        """
        tag_to_readers: Dict[str, List[str]] = {}

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