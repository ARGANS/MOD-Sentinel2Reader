from s2reader.L2A.readers.jp2.img.img import IMGReader
import xarray as xr

class ClassificationReader(IMGReader):
    """
    Reader for classification bands in Sentinel-2 products.

    This class extends the IMGReader to read classification bands (e.g., Scene Classification Layer - SCL)
    and return the data as an xarray DataArray.
    """

    _PATTERNS = ['SCL']

    def read(self, tag: str) -> xr.DataArray:
        """
        Read and process scene classification band (SCL).

        This method finds the JP2 file for the specified band tag, reads the data,
        and returns it as an xarray DataArray.

        Args:
            tag (str): The band tag (e.g., 'SCL') to read and process.

        Returns:
            xr.DataArray: The classification data as an xarray DataArray.
        """
        # Locate the image path for the given band tag
        image_path = self._get_img_path(tag)
        if image_path is None:
            raise FileNotFoundError(f"Image file for band tag '{tag}' not found.")

        # Read the JP2 file
        band_data = self.read_jp2(tag, image_path)

        # Return the classification data
        return band_data






