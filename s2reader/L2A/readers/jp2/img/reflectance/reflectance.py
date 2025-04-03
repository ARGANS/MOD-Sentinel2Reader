from s2reader.L2A.readers.jp2.img.img import IMGReader

import xarray as xr

class ReflectanceReader(IMGReader):
    """
    Reader for Reflectance bands in Sentinel-2 products.

    This class extends the IMGReader to read reflectance bands, apply offsets and quantification
    values, and return the processed data as an xarray DataArray.
    """

    _PATTERNS = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B10', 'B11', 'B12']

    def read(self, tag: str) -> xr.DataArray:
        """
        Read and process reflectance data for a given band tag.

        This method locates the JP2 file for the specified band tag, reads the data,
        applies the band offset and quantification value, and returns the processed data.

        Args:
            tag (str): The band tag (e.g., 'B08') to read and process.

        Returns:
            xr.DataArray: The processed reflectance data as an xarray DataArray.
        """
        # Locate the image path for the given band tag
        image_path = self._get_img_path(tag)
        if image_path is None:
            raise FileNotFoundError(f"Image file for band tag '{tag}' not found.")

        # Read the JP2 file
        band_data = self.read_jp2(tag, image_path)

        # Retrieve the band offset and quantification value from metadata
        offset = self.product.meta.get_band_offset(tag)
        quant = self.product.meta.get_band_quantification('BOA')

        # Apply offset and quantification to the band data
        band_data = band_data + offset
        band_data = band_data / quant

        # Return the processed reflectance data
        return band_data






