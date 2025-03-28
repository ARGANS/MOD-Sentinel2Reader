from s2reader.L2A.readers.reader import BaseReader
import rioxarray as rio

class JP2Reader(BaseReader):
    
    def read_jp2(self, tag, path):
        
        # Read in the band data
        band_data = rio.open_rasterio(path)

        # Resample to the target resolution
        band_data = band_data.rio.reproject(
            band_data.rio.crs,  # Keep the same CRS
            resolution=self.product.target_resolution,
        )
        
        # Add the band name as a coordinate
        band_data = band_data.assign_coords(band=[tag])

        return band_data