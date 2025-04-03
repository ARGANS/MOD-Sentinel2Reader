from s2reader.common.tools import read_xml

from typing import Dict, List, Union, Optional
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET

class Metadata:
    """Sentinel-2 Level 2A Metadata Reader.

    This class provides methods to read and parse metadata from Sentinel-2 Level 2A products.
    It extracts information about bands, wavelengths, and other metadata from XML files.
    """

    def __init__(self, product_path: Path) -> None:
        """
        Initialize the Metadata instance.

        Args:
            product_path (Path): Path to the .SAFE directory containing Sentinel-2 metadata.
        """
        # Load the product and tile metadata files, and generate the band table
        self.product = self._read_product_metadata(product_path)
        self.tile = self._read_tile_metadata(product_path)
        self.bands = self._create_band_table()

    def get_band_offset(self, band_tag: str) -> float:
        """
        Get the offset value for a given band.

        Args:
            band_tag (str): The band tag (e.g., 'B08').

        Returns:
            float: The offset value for the specified band.
        """
        target = self._refer_band(band_tag, 'band_tag', 'band_id')
        band_offset = self.product.find(f".//BOA_ADD_OFFSET[@band_id='{target}']")
        if band_offset is None:
            raise KeyError(f"No offset found for band {band_tag}")
        return float(band_offset.text)

    def get_band_quantification(self, band_type: str) -> float:
        """
        Get the quantification value for a given band type.

        Args:
            band_type (str): Type of band to retrieve (e.g., 'WVP', 'AOT', 'BOA').

        Returns:
            float: Band quantification value for DN to reflectance conversion.
        """
        if band_type not in ['WVP', 'AOT', 'BOA']:
            raise ValueError(f"No quantification value for type {band_type}")
        quantification_value = self.product.find(f".//{band_type}_QUANTIFICATION_VALUE")
        if quantification_value is None:
            raise KeyError(f"Quantification value not found for band type {band_type}")
        return float(quantification_value.text)

    def _extract_band_info(self, band: ET.Element) -> Dict[str, Union[str, int, float, List[float]]]:
        """
        Extract band information from an XML element.

        Args:
            band (ET.Element): XML element containing band information.

        Returns:
            Dict[str, Union[str, int, float, List[float]]]: A dictionary with band information.
        """
        band_id = band.attrib["bandId"]
        physical_band = band.attrib["physicalBand"]
        band_tag = self._phys_to_tag(physical_band)
        resolution = int(band.find("RESOLUTION").text)
        wavelengths = self._parse_wavelengths(band)
        spectral_values = list(map(float, band.find("Spectral_Response/VALUES").text.split()))

        return {
            "band_id": band_id,
            "band_phys": physical_band,
            "band_tag": band_tag,
            "resolution": resolution,
            **wavelengths,
            "rsr": spectral_values
        }

    def _parse_wavelengths(self, band: ET.Element) -> Dict[str, float]:
        """
        Parse wavelength information from an XML element.

        Args:
            band (ET.Element): XML element containing wavelength information.

        Returns:
            Dict[str, float]: A dictionary with min, max, and central wavelengths.
        """
        return {
            "min": float(band.find("Wavelength/MIN").text),
            "max": float(band.find("Wavelength/MAX").text),
            "ctr": float(band.find("Wavelength/CENTRAL").text)
        }

    def _create_band_table(self) -> pd.DataFrame:
        """
        Create a DataFrame of reflectance band specifications from metadata.

        Returns:
            pd.DataFrame: A DataFrame containing band information.
        """
        data = [self._extract_band_info(band) for band in self.product.findall(".//Spectral_Information")]
        return pd.DataFrame(data)

    def _read_product_metadata(self, path: Path) -> ET.ElementTree:
        """
        Read the MTD_MSIL2A.xml file from the product directory.

        Args:
            path (Path): Path to the .SAFE directory.

        Returns:
            ET.ElementTree: Parsed XML data.
        """
        product_meta_path = path / 'MTD_MSIL2A.xml'
        if not product_meta_path.exists():
            raise FileNotFoundError(f"Product metadata file not found: {product_meta_path}")
        return read_xml(product_meta_path)

    def _read_tile_metadata(self, path: Path) -> ET.ElementTree:
        """
        Read the MTD_TL.xml file from the GRANULE directory.

        Args:
            path (Path): Path to the .SAFE directory.

        Returns:
            ET.ElementTree: Parsed XML data.
        """
        results = list(path.glob('GRANULE/*/MTD_TL.xml'))
        if len(results) != 1:
            raise ValueError(f"Expected a single MTD_TL.xml file, found {len(results)}")
        return read_xml(results[0])

    def _tag_to_phys(self, band_tag: str) -> str:
        """
        Convert band tag notation to physical band notation.

        Args:
            band_tag (str): Band tag notation (e.g., 'B08').

        Returns:
            str: Physical band notation (e.g., 'B8').
        """
        return 'B' + band_tag.replace('B', '').lstrip('0')

    def _phys_to_tag(self, band_phys: str) -> str:
        """
        Convert physical band notation to band tag notation.

        Args:
            band_phys (str): Physical band notation (e.g., 'B8').

        Returns:
            str: Band tag notation (e.g., 'B08').
        """
        return 'B' + band_phys.replace('B', '').rjust(2, '0')

    def _phys_from_id(self, band_id: str) -> str:
        """
        Retrieve physical band notation from a given band ID.

        Args:
            band_id (str): The band identifier.

        Returns:
            str: Physical band notation (e.g., 'B8').
        """
        band = self.bands[self.bands['band_id'] == band_id]
        if band.empty:
            raise KeyError(f"No band found with ID {band_id}")
        return band['band_phys'].iloc[0]

    def _refer_band(self, band_ref: str, search_column: str, return_column: str) -> str:
        """
        Retrieve a band attribute based on a reference value.

        Args:
            band_ref (str): The reference band value.
            search_column (str): Column name to search in.
            return_column (str): Column name to return value from.

        Returns:
            str: The corresponding value from the return column.
        """
        band_info = self.bands[self.bands[search_column] == band_ref]
        if band_info.empty:
            raise KeyError(f"No match found for {band_ref} in column {search_column}")
        return band_info[return_column].iloc[0]