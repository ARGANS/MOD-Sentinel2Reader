from s2reader.L2A.readers.reader import BaseReader

import rioxarray as rio
import xarray as xr
from pathlib import Path

class JP2Reader(BaseReader):
    """
    Reader for JP2 files.

    This class provides functionality to read JP2 files, resample them to the target resolution,
    and return the data as an xarray DataArray.
    """

    def read_jp2(self, tag: str, path: Path) -> xr.DataArray:
        """
        Read a JP2 file and resample it to the target resolution.

        Args:
            tag (str): The band tag (e.g., 'B08') to associate with the data.
            path (Path): Path to the JP2 file to be read.

        Returns:
            xr.DataArray: The resampled band data with the band tag as a coordinate.
        """
        if not path.exists():
            raise FileNotFoundError(f"JP2 file not found: {path}")

        # Read in the band data
        try:
            band_data = rio.open_rasterio(path)
        except Exception as e:
            raise ValueError(f"Failed to read JP2 file at {path}: {e}")

        # Resample to the target resolution
        band_data = band_data.rio.reproject(
            band_data.rio.crs,  # Keep the same CRS
            resolution=self.product.target_resolution,
        )

        # Add the band name as a coordinate
        band_data = band_data.assign_coords(band=[tag])

        return band_data