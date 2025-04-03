from s2reader.L2A.readers.jp2.img.img import IMGReader
import xarray as xr

class AtmosphericReader(IMGReader):
    """
    Reader for atmospheric bands in Sentinel-2 products.

    This class extends the IMGReader to read atmospheric bands (e.g., Water Vapour - WVP, Aerosol Optical Thickness - AOT),
    apply quantification values, and return the processed data as an xarray DataArray.
    """

    _PATTERNS = ['WVP', 'AOT']

    def read(self, tag: str) -> xr.DataArray:
        """
        Read and process atmospheric bands for a given band tag.

        This method locates the JP2 file for the specified band tag, reads the data,
        applies the quantification value, and returns the processed data.

        Args:
            tag (str): The band tag (e.g., 'WVP' or 'AOT') to read and process.

        Returns:
            xr.DataArray: The processed atmospheric data as an xarray DataArray.
        """
        # Locate the image path for the given band tag
        image_path = self._get_img_path(tag)
        if image_path is None:
            raise FileNotFoundError(f"Image file for band tag '{tag}' not found.")

        # Read the JP2 file
        band_data = self.read_jp2(tag, image_path)

        # Retrieve the quantification value from metadata
        quant = self.product.meta.get_band_quantification(tag)

        # Apply the quantification value
        band_data = band_data / quant

        # Return the processed atmospheric data
        return band_data






