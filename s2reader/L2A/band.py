import re
import pandas as pd
import rioxarray as rio
import xarray as xr

class BandReader:
    
    REF_BAND = ['B01','B02','B03','B04','B05','B06','B07','B8A','B09','B10','B11','B12']
    MET_BAND = ['AOT','WVP']
    UTL_BAND = ['SCL']
    ALL_BAND = REF_BAND + MET_BAND + UTL_BAND

    def read_band(self, band_name:str) -> None:
        
        """ Read a band image file, resample, and add to the DataArray.

        Args:
            band_name (str): Band name to read (e.g. B02)
        """
        
        if band_name not in self.ALL_BAND:
            raise Exception(f'{band_name} not recognised')
        
        # Get band meta info
        available_df = self._find_bands()
        
        # Get rows for the given band (e.g. B01)
        band_df = available_df[available_df['name'] == band_name]

        # Grab the best image file for the band (i.e. 10/20/60m native files)
        band_file = self._get_best(band_df)

        # Read in the band data
        band_data = rio.open_rasterio(str(band_file['path']))

        # Resample to the target resolution
        band_data = band_data.rio.reproject(
            band_data.rio.crs,  # Keep the same CRS
            resolution=self.target_resolution,
        )
        
        # Add the band name as a coordinate
        band_data = band_data.assign_coords(band=[band_name])

        if band_name in self.REF_BAND:
            offset = self.meta.get_band_offset(band_name)
            quant  = self.meta.get_band_quantification('BOA')

        elif band_name in self.MET_BAND:
            offset = 0.0
            quant  = self.meta.get_band_quantification(band_name)
            
        elif band_name in self.UTL_BAND:
            offset = 0.0
            quant  = 1.0

        else:
            raise Exception('Band not recognised')

        band_data = (band_data + offset) / quant

        if self.da is None:
            self.da = band_data
        else:
            # If data already exists and we want to add a new band
            self.da = xr.concat([self.da, band_data], dim='band')


    def _find_bands(self) -> pd.DataFrame:
        
        """ Find all the image files and associated information

        Returns:
            pd.Dataframe: Dataframe of image files with additional information
        """
        
        # Get all the Image files in the metadata
        image_files = self.meta.product.findall('.//Granule/IMAGE_FILE')
        image_list  = []
        for image_file in image_files:
            # Relative -> Absolue Path
            image_path = self.safe_path / image_file.text 
            # Get the band name and native resolution
            name, resolution = re.search(r'_([A-Z0-9]{2,3})_(\d{2})m', image_path.stem).groups()
            # Append file as tuple, to transform to dataframe
            image_list.append((name, int(resolution), 'img', image_path.with_suffix('.jp2')))
        # Convert to DataFrame
        image_df = pd.DataFrame(image_list, columns=['name','resolution','type','path'])
        return image_df


    def _get_best(self, band_df:pd.DataFrame) -> pd.Series:
        
        """ Finds the "best" image file for the given band, considering the target and native resolutions

        Args:
            band_df (pd.DataFrame): Image files for the given band (e.g. B02 at 10m, 20m, 60m)

        Returns:
            pd.Series: Image file row with the "best" resolution
        """
        
        # Preferentially take the band file that has the same native resolution to the target resolution
        # If not, take the band file with the finest resolution
        if self.target_resolution in band_df['resolution']:
            band_file = band_df[band_df['resolution'] == self.target_resolution].iloc[0]
        else:
            band_file = band_df.loc[band_df['resolution'].idxmin()]

        return pd.Series(band_file)