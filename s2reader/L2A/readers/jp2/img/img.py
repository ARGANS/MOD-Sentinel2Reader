from s2reader.L2A.readers.jp2.jp2 import JP2Reader

import re
import pandas as pd
from pathlib import Path
from typing import Optional


class IMGReader(JP2Reader):
    """
    Reader for JP2 files in IMG_DATA (i.e. ref bands, water vapour) files in Sentinel-2 products.

    This class extends the JP2Reader to locate and read image files
    based on metadata and target resolution.
    """

    def _get_img_path(self, tag: str) -> Optional[Path]:
        """
        Finds the best image file path for a given band tag and target resolution.

        Args:
            tag (str): The band tag (e.g., 'B08') to locate the corresponding image file.

        Returns:
            Optional[Path]: Path to the best available image file, or None if no match is found.
        """
        # Extract image file paths from metadata
        image_files = self.product.meta.product.findall('.//Granule/IMAGE_FILE')
        if not image_files:
            raise ValueError("No image files found in metadata.")

        image_list = []

        for image_file in image_files:
            image_path = self.product.safe_path / image_file.text
            match = re.search(r'_([A-Z0-9]{2,3})_(\d{2})m', image_path.stem)
            if not match:
                continue

            name, resolution = match.groups()
            if name == tag:
                image_list.append((name, int(resolution), image_path.with_suffix('.jp2')))

        if not image_list:
            return None

        # Convert to DataFrame
        image_df = pd.DataFrame(image_list, columns=['name', 'resolution', 'path'])

        # Find the best path based on the minimum resolution difference
        best_path = image_df.loc[image_df['resolution'].idxmin()]['path']

        return best_path