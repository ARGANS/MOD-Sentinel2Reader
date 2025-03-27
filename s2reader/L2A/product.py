from s2reader.L2A.metadata import Metadata
from s2reader.L2A.band     import BandReader

from pathlib import Path

class L2AProduct(BandReader):
    
    """ Sentinel-2 Level 2A Product Reader 
    """
    
    def __init__(self, safe_path:str=None, target_resolution:int=None) -> None:

        # Parse args
        self.safe_path = Path(safe_path).resolve()
        self.target_resolution = 10 if target_resolution is None else target_resolution

        # Ensure is .SAFE
        if self.safe_path.suffixes != ['.SAFE']:
            raise Exception(f'{self.safe_path} is not a .SAFE directory')

        # Load in the metadata
        self.meta  = Metadata(self.safe_path)

        # Empty DataArray
        self.da = None


    def read(self, *args):
        
        for arg in args:
            if   arg in self.ALL_BAND:
                res = self.read_band(arg)
            elif arg in self.GEO_BAND:
                res = self.read_geometry(arg)
            else:
                raise Exception(f'{arg} not recognised')
