from s2reader.L2A.readers.jp2.img.img import IMGReader

class AtmosphericReader(IMGReader):
    
    _PATTERNS = ['WVP','AOT']
    
    def read(self, tag):
        
        image_path = self._get_img_path(tag)
        
        band_data = self.read_jp2(tag, image_path)

        quant  = self.product.meta.get_band_quantification(tag)
        band_data = band_data / quant
        
        return band_data
        
        
        
        
        
        
        