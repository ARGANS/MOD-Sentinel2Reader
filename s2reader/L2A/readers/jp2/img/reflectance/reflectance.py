from s2reader.L2A.readers.jp2.img.img import IMGReader

import xarray as xr

class ReflectanceReader(IMGReader):
    
    _PATTERNS = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B10', 'B11', 'B12']
    
    def read(self, tag):
        
        image_path = self._get_img_path(tag)
        
        band_data = self.read_jp2(tag, image_path)
        
        offset = self.product.meta.get_band_offset(tag)
        quant  = self.product.meta.get_band_quantification('BOA')
        
        band_data = band_data + offset
        band_data = band_data / quant
        
        self.product.update(da=band_data)
        
        
        
        
        
        
        