import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
from s2reader.common.tools import read_xml

class Metadata:
    
    """ Sentinel-2 Level 2A Metadata Reader
    """
    
    def __init__(self, product_path:Path) -> None:
        
        # Load the product and tile metadata files, and generate the band table
        self.product   = self._read_product_metadata(product_path)
        self.tile      = self._read_tile_metadata(product_path)
        self.bands = self._create_band_table()


    def get_band_offset(self, band_tag: str) -> float:
        
        """ Get the offset value for a given band.

        Args:
            band_tag (str): Band tag e.g. B01

        Returns:
            float: Band offset value for DN to reflectance conversion
        """
        
        target = self._refer_band(band_tag, 'band_tag', 'band_id')
        for band_offset in self.product.findall('.//BOA_ADD_OFFSET'):
            if band_offset.attrib['band_id'] == target:
                return float(band_offset.text)


    def get_band_quantification(self, band_type:str) -> float:
        
        """ Get the quantification value for a given band.

        Args:
            band_type (str): Type of band to retrieve, i.e. reflectance, aerosol, etc.

        Returns:
            float: Band quantification value for DN to reflectance conversion
        """
        
        if band_type not in ['WVP','AOT','BOA']:
            raise Exception(f'No quantification value for type {band_type}')
        return float(self.product.find(f'.//{band_type}_QUANTIFICATION_VALUE').text)


    def _create_band_table(self) -> pd.DataFrame:
        
        """ Create a DataFrame of reflectance band specifications from metadata.

        Returns:
            pd.DataFrame: Band specifications for reflectance bands
        """
        
        data = []

        for band in self.product.findall(".//Spectral_Information"):
            # Extract band information
            band_id = band.attrib["bandId"]
            physical_band = band.attrib["physicalBand"]
            band_tag = self._phys_to_tag(physical_band)
            resolution = int(band.find("RESOLUTION").text)
            wavelengths = {
                "MIN": float(band.find("Wavelength/MIN").text),
                "MAX": float(band.find("Wavelength/MAX").text),
                "CENTRAL": float(band.find("Wavelength/CENTRAL").text)
            }
            spectral_values = list(map(float, band.find("Spectral_Response/VALUES").text.split()))
            
            # Collect dicts ready for DataFrame construction
            data.append({
                "band_id": band_id,
                "band_phys": physical_band,
                "band_tag": band_tag,
                "resolution": resolution,
                "min": wavelengths["MIN"],
                "max": wavelengths["MAX"],
                "ctr": wavelengths["CENTRAL"],
                "rsr": spectral_values
            })

        # Create DataFrame
        return pd.DataFrame(data)
        

    def _read_product_metadata(self, path:Path=None) -> ET.ElementTree:
        
        """ Read the MTD_MSIL2A.xml file from the product directory.

        Args:
            path (Path): Path object to the SAFE directory. Defaults to None.

        Returns:
            ET.ElementTree: Parsed XML data
        """
        
        product_meta_path = path / 'MTD_MSIL2A.xml'
        return read_xml(product_meta_path)


    def _read_tile_metadata(self, path: Path = None) -> ET.ElementTree:
        
        """Read the MTD_TL.xml file from the GRANULE directory.

        Args:
            path (Path): Path object to the SAFE directory. Defaults to None.

        Returns:
            ET.ElementTree: Parsed XML data

        Raises:
            Exception: If the number of MTD_TL.xml files found is not exactly one.
        """
        
        results = list(path.glob('GRANULE/*/MTD_TL.xml'))
        if len(results) != 1:
            raise Exception(f'Expected a single MTD_TL.xml file, found {len(results)}')
        return read_xml(results[0])


    def _tag_to_phys(self, band_tag: str) -> str:
        
        """ Convert band tag notation to physical band notation.

        Args:
            band_tag (str): Band tag notation (e.g., 'B08').

        Returns:
            str: Physical band notation (e.g., 'B8').
        
        """
        return 'B' + band_tag.replace('B', '').lstrip('0')


    def _phys_to_tag(self, band_phys: str) -> str:
       
        """ Convert physical band notation to band tag notation.

        Args:
            band_phys (str): Physical band notation (e.g., 'B8').

        Returns:
            str: Band tag notation (e.g., 'B08').
        """
        
        return 'B' + band_phys.replace('B', '').rjust(2, '0')


    def _phys_from_id(self, band_id: str) -> str:
        
        """Retrieve physical band notation from a given band ID.

        Args:
            band_id (str): The band identifier.

        Returns:
            str: Physical band notation (e.g., 'B8').
        """
        
        band = self.bands[self.bands['band_id'] == band_id]
        return band['band_phys']


    def _refer_band(self, band_ref: str, search_column: str, return_column: str) -> str:
        
        """Retrieve a band attribute based on a reference value.

        Args:
            band_ref (str): The reference band value.
            search_column (str): Column name to search in.
            return_column (str): Column name to return value from.

        Returns:
            str: The corresponding value from the return column, or None if no match is found.
        """
        
        band_info = self.bands[self.bands[search_column] == band_ref]
        if band_info.empty:
            return None
        return band_info[return_column].values[0]