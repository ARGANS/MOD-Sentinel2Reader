from s2reader.L2A.readers.jp2.jp2 import JP2Reader

import re
import pandas as pd

class IMGReader(JP2Reader):
    
    
    def _get_img_path(self, tag):

        """Finds the best image file path for a given target resolution.

        Args:
            meta: Metadata object containing product information.
            safe_path (Path): Base path of the SAFE directory.
            target_resolution (int): Target resolution (e.g., 10, 20, 60 meters).

        Returns:
            Path: Path to the best available image file.
        """
        # Extract image file paths from metadata
        image_files = self.product.meta.product.findall('.//Granule/IMAGE_FILE')
        image_list = []
        
        for image_file in image_files:
            image_path = self.product.safe_path / image_file.text
            name, resolution = re.search(r'_([A-Z0-9]{2,3})_(\d{2})m', image_path.stem).groups()
            
            if name == tag:
                image_list.append((name, int(resolution), image_path.with_suffix('.jp2')))
        
        # Convert to DataFrame
        image_df = pd.DataFrame(image_list, columns=['name', 'resolution', 'path'])
        best_path = image_df.loc[image_df['resolution'].idxmin()]['path']

        return best_path