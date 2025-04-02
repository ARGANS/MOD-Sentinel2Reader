from s2reader.L2A.readers.jp2.img.img import IMGReader

class ClassificationReader(IMGReader):
    
    _PATTERNS = ['SCL']
    
    def read(self, tag):
        
        image_path = self._get_img_path(tag)
        
        band_data = self.read_jp2(tag, image_path)

        return band_data
        
        
        
        
        
        
        